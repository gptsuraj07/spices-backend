import os
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def main():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client.get_default_database("aridhu_db")
    res1 = await db.categories.update_one(
        {"slug": "kozhambu"},
        {"$set": {"imageUrl": "/assets/aridhu-kuzhambu-hero.jpg"}}
    )
    res2 = await db.categories.update_one(
        {"slug": "rasam"},
        {"$set": {"imageUrl": "/assets/aridhu-rasam-hero.jpg"}}
    )
    print(f"Kozhambu Matched {res1.matched_count}, Modified {res1.modified_count}")
    print(f"Rasam Matched {res2.matched_count}, Modified {res2.modified_count}")

if __name__ == "__main__":
    asyncio.run(main())
