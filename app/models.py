from pydantic import BaseModel, Field
from typing import List, Optional

class ProductSchema(BaseModel):
    id: Optional[str] = None
    name: str
    slug: str
    subtitle: Optional[str] = None
    tamilName: Optional[str] = None
    price: float
    originalPrice: Optional[float] = None
    weight: int = 100
    unit: str = "g"
    categoryId: str
    categorySlug: str
    tags: List[str] = []
    featured: bool = False
    status: str = "active"
    imageUrl: Optional[str] = None
    shortDescription: Optional[str] = None
    description: Optional[str] = None
    usage: Optional[str] = None
    storage: Optional[str] = None
    inStock: bool = True

class CategorySchema(BaseModel):
    id: Optional[str] = None
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    displayOrder: int = 0

class ComboItemSchema(BaseModel):
    productId: str
    productSlug: Optional[str] = None
    name: str
    tamilName: Optional[str] = None
    weight: int = 100
    unit: str = "g"
    imageUrl: Optional[str] = None

class ComboSchema(BaseModel):
    id: Optional[str] = None
    name: str
    slug: str
    subtitle: Optional[str] = None
    tamilName: Optional[str] = None
    price: float
    originalPrice: Optional[float] = None
    totalWeight: int = 700
    itemCount: int = 7
    featured: bool = True
    imageUrl: Optional[str] = None
    description: Optional[str] = None
    items: List[ComboItemSchema] = []

class StatusHistoryItem(BaseModel):
    status: str
    timestamp: str
    note: Optional[str] = None

class OrderSchema(BaseModel):
    id: Optional[str] = None
    orderNumber: str
    customer: dict
    shippingAddress: dict
    items: List[dict]
    subtotal: float
    discount: float = 0
    shipping: float = 0
    total: float
    couponCode: Optional[str] = None
    status: str = "ORDER_PLACED"
    paymentStatus: str = "PENDING_VERIFICATION"
    paymentMethod: str = "UPI"
    utrNumber: Optional[str] = None
    shippingProvider: Optional[str] = None
    trackingNumber: Optional[str] = None
    verifiedAt: Optional[str] = None
    verifiedBy: Optional[str] = None
    statusHistory: List[StatusHistoryItem] = []
    notes: Optional[str] = None
    createdAt: str
    updatedAt: str

