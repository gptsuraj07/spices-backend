from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.database import db, product_helper
import re

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("", response_model=List[dict])
async def get_products(
    categoryId: Optional[str] = None,
    categorySlug: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = "featured",
    featured: Optional[bool] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    status: str = "active"
):
    query = {"status": status}

    if categoryId or categorySlug:
        cat_conds = []
        if categoryId:
            cat_conds.append({"categoryId": categoryId})
            cat_conds.append({"categorySlug": categoryId.replace("cat-", "")})
        if categorySlug:
            cat_conds.append({"categorySlug": categorySlug})
            cat_conds.append({"categoryId": f"cat-{categorySlug}"})
        query["$or"] = cat_conds
    if featured is not None:
        query["featured"] = featured
    if minPrice is not None or maxPrice is not None:
        query["price"] = {}
        if minPrice is not None:
            query["price"]["$gte"] = minPrice
        if maxPrice is not None:
            query["price"]["$lte"] = maxPrice
    if search:
        regex = re.compile(re.escape(search), re.IGNORECASE)
        query["$or"] = [
            {"name": regex},
            {"shortDescription": regex},
            {"tags": {"$in": [regex]}}
        ]

    cursor = db.products.find(query)

    # Sorting
    if sort == "price_asc":
        cursor = cursor.sort("price", 1)
    elif sort == "price_desc":
        cursor = cursor.sort("price", -1)
    elif sort == "newest":
        cursor = cursor.sort("createdAt", -1)
    elif sort == "name_asc":
        cursor = cursor.sort("name", 1)
    else:
        cursor = cursor.sort("featured", -1)

    products = []
    async for p in cursor:
        products.append(product_helper(p))

    return products

@router.get("/featured", response_model=List[dict])
async def get_featured_products():
    products = []
    async for p in db.products.find({"featured": True, "status": "active"}):
        products.append(product_helper(p))
    return products

@router.get("/{slug}", response_model=dict)
async def get_product_by_slug(slug: str):
    product = await db.products.find_one({"slug": slug})
    if not product:
        # Also try to find by ID
        if ObjectId.is_valid(slug):
            product = await db.products.find_one({"_id": ObjectId(slug)})
        if not product:
            product = await db.products.find_one({"id": slug})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_helper(product)

from bson import ObjectId
from fastapi import Body

@router.post("", response_model=dict)
async def create_product(product_data: dict = Body(...)):
    if "slug" not in product_data or not product_data["slug"]:
        name = product_data.get("name", "product")
        product_data["slug"] = name.lower().replace(" ", "-")
        
    result = await db.products.insert_one(product_data)
    created = await db.products.find_one({"_id": result.inserted_id})
    return product_helper(created)

@router.put("/{id}", response_model=dict)
async def update_product(id: str, updates: dict = Body(...)):
    query = {"id": id}
    if ObjectId.is_valid(id):
        query = {"$or": [{"_id": ObjectId(id)}, {"id": id}, {"slug": id}]}
        
    result = await db.products.update_one(query, {"$set": updates})
    if result.matched_count == 0:
        # If not found, create or raise 404
        raise HTTPException(status_code=404, detail="Product not found")
        
    updated = await db.products.find_one(query)
    return product_helper(updated)

@router.delete("/{id}")
async def delete_product(id: str):
    query = {"id": id}
    if ObjectId.is_valid(id):
        query = {"$or": [{"_id": ObjectId(id)}, {"id": id}, {"slug": id}]}
    await db.products.delete_one(query)
    return {"message": "Product deleted successfully"}

