import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://conceptraedu_db_user:FRk5gYmp4TVn6Xqm@cluster0.5q11fff.mongodb.net/aridhu_db?retryWrites=true&w=majority&appName=Cluster0"
)

combos_data = [
    {
        "name": "7 Rasam Collection",
        "slug": "7-rasam-collection",
        "subtitle": "The Complete Aridhu Rasam Experience",
        "price": 350,
        "originalPrice": 700,
        "totalWeight": 350,
        "itemCount": 7,
        "featured": True,
        "imageUrl": "/assets/aridhu-rasam-hero.jpg",
        "gallery": ["/assets/aridhu-rasam-hero.jpg"],
        "description": "Seven unique Rasam blends, each crafted from a distinct traditional recipe, brought together in one thoughtfully curated collection (50g packet each). This is the complete Aridhu Rasam experience — from the bold warmth of Milagu to the rare character of Kandathippili, from the comfort of Kalyana to the brightness of Ginger Lemon.",
        "shortDescription": "The complete Aridhu Rasam experience — all 7 varieties (50g each) in one collection.",
        "items": [
            {"productId": "rasam-001", "productSlug": "kalyana-rasam-powder", "name": "Kalyana Rasam Powder", "weight": 50},
            {"productId": "rasam-002", "productSlug": "ginger-lemon-rasam-powder", "name": "Ginger Lemon Rasam Powder", "weight": 50},
            {"productId": "rasam-003", "productSlug": "mor-rasam-powder", "name": "Mor Rasam Powder", "weight": 50},
            {"productId": "rasam-004", "productSlug": "kandathippili-rasam-powder", "name": "Kandathippili Rasam Powder", "weight": 50},
            {"productId": "rasam-005", "productSlug": "cinnamon-rasam-powder", "name": "Cinnamon Rasam Powder", "weight": 50},
            {"productId": "rasam-006", "productSlug": "kollu-rasam-powder", "name": "Kollu Rasam Powder", "weight": 50},
            {"productId": "rasam-007", "productSlug": "poricha-rasam-powder", "name": "Poricha Rasam Powder", "weight": 50},
        ],
        "comboProducts": [
            {"productId": "rasam-001", "quantity": 1, "displayOrder": 1},
            {"productId": "rasam-002", "quantity": 1, "displayOrder": 2},
            {"productId": "rasam-003", "quantity": 1, "displayOrder": 3},
            {"productId": "rasam-004", "quantity": 1, "displayOrder": 4},
            {"productId": "rasam-005", "quantity": 1, "displayOrder": 5},
            {"productId": "rasam-006", "quantity": 1, "displayOrder": 6},
            {"productId": "rasam-007", "quantity": 1, "displayOrder": 7},
        ],
    },
    {
        "name": "7 Kozhambu Collection",
        "slug": "7-kozhambu-collection",
        "subtitle": "Signature South Indian Gravy Collection",
        "price": 350,
        "originalPrice": 700,
        "totalWeight": 350,
        "itemCount": 7,
        "featured": True,
        "imageUrl": "/assets/aridhu-kuzhambu-hero.jpg",
        "gallery": ["/assets/aridhu-kuzhambu-hero.jpg"],
        "description": "Seven distinct Kozhambu blends exploring the rich landscape of South Indian gravy traditions (50g packet each). From Vatha Kuzhambu and Ennai Kathirikai to cooling Mor Kuzhambu, Talaga Kuzhambu, Vendaya Vendaikai, Kootu Kuzhambu, and unique Narthangai — this collection brings the full depth of Kozhambu cooking to your kitchen.",
        "shortDescription": "Seven traditional Kozhambu blends (50g each) — the complete South Indian gravy collection.",
        "items": [
            {"productId": "koz-001", "productSlug": "vatha-kuzhambu-powder", "name": "Vatha Kuzhambu Powder", "weight": 50},
            {"productId": "koz-002", "productSlug": "ennai-kathirikai-kuzhambu-powder", "name": "Ennai Kathirikai Kuzhambu Powder", "weight": 50},
            {"productId": "koz-003", "productSlug": "mor-kuzhambu-powder", "name": "Mor Kuzhambu Powder", "weight": 50},
            {"productId": "koz-004", "productSlug": "talaga-kuzhambu-powder", "name": "Talaga Kuzhambu Powder", "weight": 50},
            {"productId": "koz-005", "productSlug": "vendaya-vendaikai-kuzhambu-powder", "name": "Vendaya Vendaikai Kuzhambu Powder", "weight": 50},
            {"productId": "koz-006", "productSlug": "kootu-kuzhambu-powder", "name": "Kootu Kuzhambu Powder", "weight": 50},
            {"productId": "koz-007", "productSlug": "narthangai-kuzhambu-powder", "name": "Narthangai Kuzhambu Powder", "weight": 50},
        ],
        "comboProducts": [
            {"productId": "koz-001", "quantity": 1, "displayOrder": 1},
            {"productId": "koz-002", "quantity": 1, "displayOrder": 2},
            {"productId": "koz-003", "quantity": 1, "displayOrder": 3},
            {"productId": "koz-004", "quantity": 1, "displayOrder": 4},
            {"productId": "koz-005", "quantity": 1, "displayOrder": 5},
            {"productId": "koz-006", "quantity": 1, "displayOrder": 6},
            {"productId": "koz-007", "quantity": 1, "displayOrder": 7},
        ],
    },
]

async def update():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.get_default_database("aridhu_db")
    print("Connected to MongoDB Atlas...")

    for combo in combos_data:
        res = await db.combos.update_one(
            {"slug": combo["slug"]},
            {"$set": combo},
            upsert=True
        )
        print(f"Updated combo '{combo['name']}': matched={res.matched_count}, modified={res.modified_count}, upserted={res.upserted_id}")

if __name__ == "__main__":
    asyncio.run(update())
