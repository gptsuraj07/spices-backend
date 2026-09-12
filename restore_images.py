import os
import asyncio
import boto3
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def restore():
    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv('R2_ENDPOINT'),
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
        region_name='auto'
    )
    bucket = os.getenv('R2_BUCKET_NAME', 'aridhuproducts')
    res = s3.list_objects_v2(Bucket=bucket)
    keys = [obj['Key'] for obj in res.get('Contents', [])]
    domain = os.getenv('R2_PUBLIC_DOMAIN', '').rstrip('/')

    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = client.get_default_database("aridhu_db")

    updated_count = 0
    for key in keys:
        filename = os.path.basename(key)
        if filename.startswith("product-") and filename.endswith(".webp"):
            parts = filename[len("product-"):-len(".webp")].rsplit("-", 1)
            if len(parts) == 2:
                prod_id = parts[0]
                img_url = f"{domain}/{key}"
                res = await db.products.update_one(
                    {"$or": [{"id": prod_id}, {"slug": prod_id}]},
                    {"$set": {"imageUrl": img_url}}
                )
                if res.matched_count > 0:
                    updated_count += 1
                    print(f"Restored image for product [{prod_id}]: {img_url}")

    print(f"\nDone! Successfully restored {updated_count} product images from Cloudflare R2.")

if __name__ == "__main__":
    asyncio.run(restore())
