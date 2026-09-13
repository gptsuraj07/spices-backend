import asyncio
import re
from app.database import db

async def clean_database():
    print("Starting MongoDB Atlas database cleanup...")
    
    # 1. Clean Products
    products = await db.products.find({}).to_list(1000)
    for p in products:
        updates = {}
        
        # Remove Tanjore from fields
        for field in ["name", "description", "shortDescription", "subtitle"]:
            val = p.get(field)
            if val and "tanjore" in val.lower():
                # Replace variations of Tanjore
                cleaned = re.sub(r'Tanjore banquet', 'festive banquet', val, flags=re.IGNORECASE)
                cleaned = re.sub(r'Tanjore marriage banquets', 'South Indian marriage banquets', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'Tanjore royal aroma', 'royal South Indian aroma', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'Tanjore style', 'South Indian style', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'Tanjore festival delicacy', 'South Indian festival delicacy', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'Tanjore special', 'Special', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'Tanjore feast', 'South Indian feast', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'Tanjore', 'South Indian', cleaned, flags=re.IGNORECASE)
                updates[field] = cleaned
        
        # Tags clean
        tags = p.get("tags")
        if tags and isinstance(tags, list):
            new_tags = [t for t in tags if t.lower() != "tanjore"]
            if new_tags != tags:
                updates["tags"] = new_tags
                
        # Spice Level / Heat set to Medium Spicy
        updates["spiceLevel"] = "Medium Spicy"
        
        if updates:
            await db.products.update_one({"_id": p["_id"]}, {"$set": updates})

    print(f"Updated {len(products)} product documents in MongoDB Atlas.")

    # 2. Clean Categories
    categories = await db.categories.find({}).to_list(100)
    for c in categories:
        updates = {}
        desc = c.get("description")
        if desc:
            if "7-Day authentic" in desc:
                desc = desc.replace("7-Day authentic", "authentic")
            if "Tanjore" in desc:
                desc = re.sub(r'Tanjore', 'South Indian', desc, flags=re.IGNORECASE)
            updates["description"] = desc
        
        if updates:
            await db.categories.update_one({"_id": c["_id"]}, {"$set": updates})

    print(f"Updated {len(categories)} category documents in MongoDB Atlas.")

    # 3. Clean Combos
    combos = await db.combos.find({}).to_list(100)
    for cb in combos:
        updates = {}
        desc = cb.get("description")
        if desc and "Tanjore" in desc:
            updates["description"] = re.sub(r'Tanjore', 'South Indian', desc, flags=re.IGNORECASE)
        if updates:
            await db.combos.update_one({"_id": cb["_id"]}, {"$set": updates})

    print(f"Updated {len(combos)} combo documents in MongoDB Atlas.")
    print("Database cleanup completed successfully!")

if __name__ == "__main__":
    asyncio.run(clean_database())
