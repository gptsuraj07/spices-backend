import os
import io
import uuid
import logging
from typing import Tuple, Optional
from PIL import Image
import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)

# Maximum image dimension (longest side in pixels)
MAX_IMAGE_DIMENSION = 1600
WEBP_QUALITY = 82

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "products")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_r2_client():
    account_id = os.getenv("R2_ACCOUNT_ID", "").strip()
    access_key = os.getenv("R2_ACCESS_KEY_ID", "").strip()
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY", "").strip()
    endpoint = os.getenv("R2_ENDPOINT", "").strip()

    if not access_key or not secret_key:
        return None

    endpoint_url = endpoint
    if account_id and "<ACCOUNT_ID>" in endpoint_url:
        endpoint_url = endpoint_url.replace("<ACCOUNT_ID>", account_id)

    if not endpoint_url and account_id:
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

    if not endpoint_url:
        return None

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="auto"
    )


def compress_and_resize_image(file_bytes: bytes) -> Tuple[bytes, str]:
    """
    Validates, resizes (max 1600px longest side), and compresses image bytes into WebP format.
    Raises ValueError if the input is not a valid image format.
    """
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
        img = Image.open(io.BytesIO(file_bytes))  # Reopen after verify
    except Exception as e:
        raise ValueError(f"Invalid or corrupted image file: {str(e)}")

    # Convert color modes if necessary
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")

    # Resize if any dimension exceeds MAX_IMAGE_DIMENSION
    width, height = img.size
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        if width >= height:
            new_width = MAX_IMAGE_DIMENSION
            new_height = int((MAX_IMAGE_DIMENSION / width) * height)
        else:
            new_height = MAX_IMAGE_DIMENSION
            new_width = int((MAX_IMAGE_DIMENSION / height) * width)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")

    output_buffer = io.BytesIO()
    img.save(output_buffer, format="WEBP", quality=WEBP_QUALITY, optimize=True)
    compressed_bytes = output_buffer.getvalue()

    return compressed_bytes, "image/webp"


def upload_product_image_to_r2(compressed_bytes: bytes, product_id: str) -> str:
    """
    Uploads compressed WebP image to Cloudflare R2 bucket.
    Fallback to local filesystem if R2 environment credentials are not provided.
    """
    bucket_name = os.getenv("R2_BUCKET_NAME", "aridhuproducts").strip() or "aridhuproducts"
    unique_key = f"products/product-{product_id}-{uuid.uuid4().hex[:8]}.webp"
    
    s3_client = get_r2_client()

    if s3_client:
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=unique_key,
                Body=compressed_bytes,
                ContentType="image/webp",
                CacheControl="public, max-age=31536000"
            )
            
            public_domain = os.getenv("R2_PUBLIC_DOMAIN", "").strip()
            if public_domain:
                if not public_domain.startswith("http"):
                    public_domain = f"https://{public_domain}"
                return f"{public_domain.rstrip('/')}/{unique_key}"
            
            account_id = os.getenv("R2_ACCOUNT_ID", "").strip()
            if account_id:
                return f"https://pub-{account_id}.r2.dev/{unique_key}"
            
            return f"https://{bucket_name}.r2.cloudflarestorage.com/{unique_key}"
        except Exception as e:
            logger.error(f"Failed to upload image to R2: {e}. Falling back to local storage.")

    # Fallback to local storage
    filename = os.path.basename(unique_key)
    target_path = os.path.join(UPLOAD_DIR, filename)
    with open(target_path, "wb") as f:
        f.write(compressed_bytes)

    port = os.getenv("PORT", "5000")
    return f"http://localhost:{port}/uploads/products/{filename}"


def delete_product_image_from_r2(image_url: Optional[str]) -> bool:
    """
    Removes the image object from Cloudflare R2 bucket or local filesystem.
    """
    if not image_url:
        return False

    bucket_name = os.getenv("R2_BUCKET_NAME", "aridhuproducts").strip() or "aridhuproducts"
    s3_client = get_r2_client()

    if "r2.dev" in image_url or "cloudflarestorage.com" in image_url or "r2." in image_url:
        if s3_client:
            try:
                # Extract key from URL
                parts = image_url.split("/")
                if "products" in parts:
                    idx = parts.index("products")
                    key = "/".join(parts[idx:])
                else:
                    key = parts[-1]

                s3_client.delete_object(Bucket=bucket_name, Key=key)
                logger.info(f"Deleted R2 object: {key}")
                return True
            except Exception as e:
                logger.error(f"Error deleting image from R2: {e}")

    # Local file fallback cleanup
    if "/uploads/" in image_url:
        filename = os.path.basename(image_url)
        local_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
                logger.info(f"Deleted local file: {local_path}")
                return True
            except Exception as e:
                logger.error(f"Error deleting local image file: {e}")

    return False
