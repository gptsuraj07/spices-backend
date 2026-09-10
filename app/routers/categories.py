from fastapi import APIRouter
from typing import List
from app.database import db, category_helper

router = APIRouter(prefix="/api/categories", tags=["Categories"])

@router.get("", response_model=List[dict])
async def get_categories():
    categories = []
    async for c in db.categories.find().sort("displayOrder", 1):
        categories.append(category_helper(c))
    return categories
