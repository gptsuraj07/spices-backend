import asyncio
from app.database import db

async def sync():
    products = await db.products.find({}).to_list(1000)
    print(f"Found {len(products)} products in database.")
    
    cat_map = {
        "cat-kozhambu": "kozhambu",
        "cat-rasam": "rasam",
        "cat-sambar": "sambar",
        "cat-tiffin": "tiffin-mixes",
        "cat-combos": "combos",
    }
    
    updated_count = 0
    for p in products:
        cat_id = p.get("categoryId") or "cat-kozhambu"
        cat_slug = cat_map.get(cat_id, cat_id.replace("cat-", ""))
        
        await db.products.update_one(
            {"_id": p["_id"]},
            {"$set": {"categoryId": cat_id, "categorySlug": cat_slug}}
        )
        updated_count += 1
        
    print(f"Successfully synced {updated_count} products with correct categoryId and categorySlug.")

if __name__ == "__main__":
    asyncio.run(sync())
