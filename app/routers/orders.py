from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.database import db, order_helper
import random

router = APIRouter(prefix="/api/orders", tags=["Orders"])

# ── Helpers ──────────────────────────────────────────────────

def generate_order_number() -> str:
    """Generate ARU-YYYYMMDD-XXXX human-readable order number."""
    now = datetime.utcnow()
    date_part = now.strftime("%Y%m%d")
    xxxx = random.randint(1000, 9999)
    return f"ARU-{date_part}-{xxxx}"

def build_query(id: str) -> dict:
    """Build a MongoDB query that matches by ObjectId, id, or orderNumber."""
    q = {"$or": [{"id": id}, {"orderNumber": id}]}
    if ObjectId.is_valid(id):
        q = {"$or": [{"_id": ObjectId(id)}, {"id": id}, {"orderNumber": id}]}
    return q

def append_status_history(order_data: dict, entry: dict) -> None:
    """Append a status history entry to the order's statusHistory array."""
    if "statusHistory" not in order_data:
        order_data["statusHistory"] = []
    order_data["statusHistory"].append(entry)

# ── Create Order ─────────────────────────────────────────────

@router.post("", response_model=dict)
async def create_order(order_data: dict = Body(...)):
    # Generate order number if not provided
    if not order_data.get("orderNumber"):
        order_data["orderNumber"] = generate_order_number()

    now_str = datetime.utcnow().isoformat()

    # Ensure new-style status fields
    if "status" not in order_data:
        order_data["status"] = "ORDER_PLACED"
    if "payment" not in order_data:
        order_data["payment"] = {
            "method": order_data.get("paymentMethod", "UPI"),
            "status": "PENDING_VERIFICATION",
        }
    if "fulfillment" not in order_data:
        order_data["fulfillment"] = {}

    # Initialize statusHistory if not provided
    if "statusHistory" not in order_data or not order_data["statusHistory"]:
        order_data["statusHistory"] = [
            {"status": "ORDER_PLACED", "timestamp": now_str, "note": "Order placed successfully"},
            {"status": "PAYMENT_VERIFICATION", "timestamp": now_str, "note": "Awaiting payment verification"},
        ]

    # Handle _historyEntry from frontend (append to history)
    if "_historyEntry" in order_data:
        order_data.pop("_historyEntry")

    order_data["createdAt"] = order_data.get("createdAt", now_str)
    order_data["updatedAt"] = now_str

    result = await db.orders.insert_one(order_data)
    created_order = await db.orders.find_one({"_id": result.inserted_id})
    return order_helper(created_order)

# ── Get All Orders ────────────────────────────────────────────

@router.get("", response_model=List[dict])
async def get_orders(
    status: Optional[str] = None,
    paymentStatus: Optional[str] = None,
    search: Optional[str] = None,
):
    query = {}
    if status:
        query["status"] = status
    if paymentStatus:
        # Support both new (PAID) and legacy (paid) payment status filters
        query["$or"] = [
            {"payment.status": paymentStatus},
            {"payment.status": paymentStatus.upper()},
            {"paymentStatus": paymentStatus.lower()},
        ]

    cursor = db.orders.find(query).sort("createdAt", -1)
    orders = []
    async for o in cursor:
        helper = order_helper(o)
        if search:
            q = search.lower()
            order_num  = str(helper.get("orderNumber", "")).lower()
            cust_name  = str(helper.get("customer", {}).get("name", "")).lower()
            cust_phone = str(helper.get("customer", {}).get("phone", "")).lower()
            if q in order_num or q in cust_name or q in cust_phone:
                orders.append(helper)
        else:
            orders.append(helper)
    return orders

# ── Get Order by ID or Order Number ──────────────────────────

@router.get("/{id}", response_model=dict)
async def get_order_by_id(id: str):
    order = None
    if ObjectId.is_valid(id):
        order = await db.orders.find_one({"_id": ObjectId(id)})
    if not order:
        order = await db.orders.find_one({"id": id})
    if not order:
        order = await db.orders.find_one({"orderNumber": id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_helper(order)

# ── Update Order (generic PATCH) ─────────────────────────────

@router.patch("/{id}", response_model=dict)
async def update_order(id: str, updates: dict = Body(...)):
    now_str = datetime.utcnow().isoformat()
    updates["updatedAt"] = now_str

    # Handle _historyEntry: append to statusHistory
    history_entry = updates.pop("_historyEntry", None)

    query = build_query(id)
    set_op = {"$set": updates}

    if history_entry:
        set_op["$push"] = {"statusHistory": history_entry}

    result = await db.orders.update_one(query, set_op)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found to update")

    updated = await db.orders.find_one(query)
    return order_helper(updated)

# ── Verify Payment ────────────────────────────────────────────

@router.post("/{id}/verify-payment", response_model=dict)
async def verify_payment(id: str, body: dict = Body(default={})):
    now_str = datetime.utcnow().isoformat()
    admin_name = body.get("adminName", "Admin")

    history_entry = {
        "status":    "PAYMENT_CONFIRMED",
        "timestamp": now_str,
        "note":      "Payment verified by admin",
        "adminNote": f"Verified by {admin_name}",
    }

    query = build_query(id)
    result = await db.orders.update_one(query, {
        "$set": {
            "status":           "PAYMENT_CONFIRMED",
            "paymentStatus":    "paid",
            "payment.status":   "PAID",
            "payment.verifiedAt": now_str,
            "payment.verifiedBy": admin_name,
            "updatedAt":        now_str,
        },
        "$push": {"statusHistory": history_entry},
    })
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    updated = await db.orders.find_one(query)
    return order_helper(updated)

# ── Reject Payment ────────────────────────────────────────────

@router.post("/{id}/reject-payment", response_model=dict)
async def reject_payment(id: str, body: dict = Body(default={})):
    now_str = datetime.utcnow().isoformat()
    reason = body.get("reason", "Payment could not be verified")

    history_entry = {
        "status":    "PAYMENT_FAILED",
        "timestamp": now_str,
        "note":      "Payment rejected by admin",
        "adminNote": reason,
    }

    query = build_query(id)
    result = await db.orders.update_one(query, {
        "$set": {
            "status":          "PAYMENT_FAILED",
            "paymentStatus":   "failed",
            "payment.status":  "FAILED",
            "updatedAt":       now_str,
        },
        "$push": {"statusHistory": history_entry},
    })
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    updated = await db.orders.find_one(query)
    return order_helper(updated)

# ── Update Shipping Details ───────────────────────────────────

@router.patch("/{id}/shipping", response_model=dict)
async def update_shipping(id: str, body: dict = Body(...)):
    now_str = datetime.utcnow().isoformat()
    provider        = body.get("provider", "")
    tracking_number = body.get("trackingNumber", "")

    history_entry = {
        "status":    "SHIPPED",
        "timestamp": now_str,
        "note":      f"Shipped via {provider}. Tracking: {tracking_number}",
    }

    query = build_query(id)
    result = await db.orders.update_one(query, {
        "$set": {
            "status":                    "SHIPPED",
            "fulfillment.provider":      provider,
            "fulfillment.trackingNumber": tracking_number,
            "fulfillment.shippedAt":     now_str,
            "updatedAt":                 now_str,
        },
        "$push": {"statusHistory": history_entry},
    })
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    updated = await db.orders.find_one(query)
    return order_helper(updated)

# ── Delete Order ──────────────────────────────────────────────

@router.delete("/{id}")
async def delete_order(id: str):
    query = build_query(id)
    await db.orders.delete_one(query)
    return {"message": "Order deleted successfully"}
