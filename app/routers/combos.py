from fastapi import APIRouter, HTTPException
from typing import List
from app.database import db, combo_helper

router = APIRouter(prefix="/api/combos", tags=["Combos"])

@router.get("", response_model=List[dict])
async def get_combos():
    combos = []
    async for c in db.combos.find():
        combos.append(combo_helper(c))
    return combos

@router.get("/{slug}", response_model=dict)
async def get_combo_by_slug(slug: str):
    combo = await db.combos.find_one({"slug": slug})
    if not combo:
        raise HTTPException(status_code=404, detail="Combo not found")
    return combo_helper(combo)
