import asyncio
from app.database import db

async def check():
    products = await db.products.find({}).to_list(100)
    for p in products:
        print(p.get("id"), "|", p.get("name"), "-->", p.get("imageUrl"))

if __name__ == "__main__":
    asyncio.run(check())
