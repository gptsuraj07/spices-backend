from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from bson import ObjectId
from app.database import db, product_helper
from app.services.r2_service import (
    compress_and_resize_image,
    upload_product_image_to_r2,
    delete_product_image_from_r2,
)

router = APIRouter(prefix="/api/admin/products", tags=["Admin Products"])


def build_product_query(id_str: str) -> dict:
    if ObjectId.is_valid(id_str):
        return {"$or": [{"_id": ObjectId(id_str)}, {"id": id_str}, {"slug": id_str}]}
    return {"$or": [{"id": id_str}, {"slug": id_str}]}


@router.post("/{id}/image", response_model=dict)
async def upload_product_image(id: str, file: UploadFile = File(...)):
    """
    Accepts multipart/form-data image file, compresses/resizes to WebP (max 1600px),
    uploads only the compressed WebP to R2, updates MongoDB product.imageUrl, and returns updated product.
    """
    # Verify product exists
    query = build_product_query(id)
    product = await db.products.find_one(query)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please select a valid image file (JPEG, PNG, WebP, etc.)."
        )

    try:
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # 1. Compress & resize image to WebP (max 1600px longest side)
        compressed_bytes, mime_type = compress_and_resize_image(raw_bytes)

        # 2. Delete existing R2 image if one was attached
        old_image_url = product.get("imageUrl")
        if old_image_url:
            delete_product_image_from_r2(old_image_url)

        # 3. Upload only compressed WebP to R2
        prod_id = str(product.get("id") or product["_id"])
        final_image_url = upload_product_image_to_r2(compressed_bytes, prod_id)

        # 4. Save to MongoDB
        await db.products.update_one(query, {"$set": {"imageUrl": final_image_url}})

        # 5. Return updated product
        updated_product = await db.products.find_one(query)
        return product_helper(updated_product)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Product image upload failed: {str(e)}"
        )


@router.delete("/{id}/image", response_model=dict)
async def remove_product_image(id: str):
    """
    Removes product image from R2, sets imageUrl = None in MongoDB, and returns updated product.
    """
    query = build_product_query(id)
    product = await db.products.find_one(query)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    old_image_url = product.get("imageUrl")
    if old_image_url:
        delete_product_image_from_r2(old_image_url)

    # Set imageUrl = None / null in MongoDB
    await db.products.update_one(query, {"$set": {"imageUrl": None}})

    updated_product = await db.products.find_one(query)
    return product_helper(updated_product)


@router.post("", response_model=dict)
async def create_product(data: dict = Body(...)):
    """
    Creates a new product document in MongoDB and returns the created product.
    """
    import uuid
    name = data.get("name", "New Product").strip()
    slug = data.get("slug") or name.lower().replace(" ", "-")
    slug = "".join(c if c.isalnum() or c == "-" else "" for c in slug)

    prod_id = data.get("id") or f"prod-{uuid.uuid4().hex[:8]}"

    new_doc = {
        "id": prod_id,
        "name": name,
        "slug": slug,
        "subtitle": data.get("subtitle", ""),
        "tamilName": data.get("tamilName", ""),
        "price": float(data.get("price", 0)),
        "originalPrice": float(data.get("originalPrice")) if data.get("originalPrice") is not None else None,
        "weight": int(data.get("weight", 100)),
        "unit": data.get("unit", "g"),
        "weightUnit": data.get("weightUnit", "g"),
        "sku": data.get("sku") or f"ARI-{slug[:6].upper()}-100",
        "stock": int(data.get("stock", 50)),
        "categoryId": data.get("categoryId", "cat-rasam"),
        "categorySlug": data.get("categorySlug") or data.get("categoryId", "cat-rasam").replace("cat-", ""),
        "tags": data.get("tags", []),
        "featured": bool(data.get("featured", False)),
        "status": data.get("status", "active"),
        "imageUrl": data.get("imageUrl"),
        "shortDescription": data.get("shortDescription", ""),
        "description": data.get("description", ""),
        "recipe": data.get("recipe"),
        "usage": data.get("usage", ""),
        "storage": data.get("storage", ""),
        "inStock": bool(data.get("inStock", True)),
    }

    result = await db.products.insert_one(new_doc)
    created = await db.products.find_one({"_id": result.inserted_id})
    return product_helper(created)


@router.put("/{id}", response_model=dict)
async def update_product(id: str, data: dict):
    """
    Updates full product details in MongoDB and returns updated product.
    """
    query = build_product_query(id)
    product = await db.products.find_one(query)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = {k: v for k, v in data.items() if k not in ["_id", "id"]}
    if update_data:
        await db.products.update_one(query, {"$set": update_data})

    updated_product = await db.products.find_one(query)
    return product_helper(updated_product)

