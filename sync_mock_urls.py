import asyncio
import re
from app.database import db

async def sync():
    products = await db.products.find({}).to_list(100)
    img_map = {p.get("id"): p.get("imageUrl") for p in products if p.get("id") and p.get("imageUrl")}
    
    mock_file_path = "../frontend/src/app/core/data/products.mock.ts"
    with open(mock_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match product blocks
    for prod_id, img_url in img_map.items():
        # Match id: 'rasam-001' ... imageUrl: null OR imageUrl: '...'
        pattern = r"(id:\s*['\"]" + re.escape(prod_id) + r"['\"].*?imageUrl:\s*)(null|['\"].*?['\"])"
        replacement = r"\1'" + img_url + "'"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(mock_file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Updated products.mock.ts with real R2 WebP URLs!")

if __name__ == "__main__":
    asyncio.run(sync())
