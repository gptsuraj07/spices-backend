import os
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def main():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client.get_default_database("aridhu_db")
    
    # 1. Update all Podis / Tiffin Mixes to Medium Spicy
    res1 = await db.products.update_many(
        {"$or": [
            {"categoryId": "cat-tiffin"},
            {"name": {"$regex": "podi", "$options": "i"}}
        ]},
        {"$set": {"spiceLevel": "Medium Spicy"}}
    )
    
    # 2. Update Dal / Paruppu Podi specifically to Spicy
    res2 = await db.products.update_many(
        {"$or": [
            {"slug": "dal-paruppu-podi"},
            {"name": {"$regex": "dal|paruppu", "$options": "i"}}
        ]},
        {"$set": {"spiceLevel": "Spicy"}}
    )
    
    print(f"Podis updated to Medium Spicy matched: {res1.matched_count}, modified: {res1.modified_count}")
    print(f"Dal powder updated to Spicy matched: {res2.matched_count}, modified: {res2.modified_count}")

if __name__ == "__main__":
    asyncio.run(main())
