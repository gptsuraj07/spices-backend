import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://conceptraedu_db_user:FRk5gYmp4TVn6Xqm@cluster0.5q11fff.mongodb.net/aridhu_db?retryWrites=true&w=majority&appName=Cluster0"
)

client = AsyncIOMotorClient(MONGODB_URI)
db = client.get_default_database("aridhu_db")

# Helper functions to serialize MongoDB ObjectId / _id
def product_helper(product) -> dict:
    return {
        "id": str(product.get("_id", product.get("id"))),
        "name": product.get("name"),
        "slug": product.get("slug"),
        "subtitle": product.get("subtitle", ""),
        "tamilName": product.get("tamilName", ""),
        "price": product.get("price", 0),
        "originalPrice": product.get("originalPrice"),
        "weight": product.get("weight", 100),
        "unit": product.get("unit", "g"),
        "categoryId": product.get("categoryId", ""),
        "categorySlug": product.get("categorySlug", ""),
        "tags": product.get("tags", []),
        "featured": product.get("featured", False),
        "status": product.get("status", "active"),
        "imageUrl": product.get("imageUrl"),
        "shortDescription": product.get("shortDescription", ""),
        "description": product.get("description", ""),
        "usage": product.get("usage", ""),
        "storage": product.get("storage", ""),
        "inStock": product.get("inStock", True),
    }

def category_helper(category) -> dict:
    return {
        "id": str(category.get("_id", category.get("id"))),
        "name": category.get("name"),
        "slug": category.get("slug"),
        "description": category.get("description", ""),
        "icon": category.get("icon", ""),
        "displayOrder": category.get("displayOrder", 0),
    }

def combo_helper(combo) -> dict:
    return {
        "id": str(combo.get("_id", combo.get("id"))),
        "name": combo.get("name"),
        "slug": combo.get("slug"),
        "subtitle": combo.get("subtitle", ""),
        "tamilName": combo.get("tamilName", ""),
        "price": combo.get("price", 0),
        "originalPrice": combo.get("originalPrice"),
        "totalWeight": combo.get("totalWeight", 700),
        "itemCount": combo.get("itemCount", 7),
        "featured": combo.get("featured", True),
        "imageUrl": combo.get("imageUrl", ""),
        "description": combo.get("description", ""),
        "items": combo.get("items", []),
    }

def order_helper(order) -> dict:
    return {
        "id":              str(order.get("_id", order.get("id"))),
        "orderNumber":     order.get("orderNumber", ""),
        "customerId":      order.get("customerId"),
        "customer":        order.get("customer", {}),
        "shippingAddress": order.get("shippingAddress", {}),
        "items":           order.get("items", []),
        "subtotal":        order.get("subtotal", 0),
        "discount":        order.get("discount", 0),
        "shipping":        order.get("shipping", 0),
        "total":           order.get("total", 0),
        "couponCode":      order.get("couponCode"),
        "status":          order.get("status", "ORDER_PLACED"),
        # New structured fields
        "payment":         order.get("payment", {
            "method": order.get("paymentMethod", "UPI"),
            "status": "PENDING_VERIFICATION",
        }),
        "fulfillment":     order.get("fulfillment", {}),
        "statusHistory":   order.get("statusHistory", []),
        "adminNotes":      order.get("adminNotes"),
        # Legacy compat flat fields
        "paymentStatus":   order.get("paymentStatus", "pending"),
        "paymentMethod":   order.get("paymentMethod", "UPI"),
        "notes":           order.get("notes"),
        "createdAt":       order.get("createdAt"),
        "updatedAt":       order.get("updatedAt"),
    }
