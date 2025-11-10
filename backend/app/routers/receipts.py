# ?? Receipts Management — user/admin visibility
from fastapi import APIRouter
from app.core.config import mongo_db

router = APIRouter()

@router.get("/user/{user_id}")
async def user_receipts(user_id: str):
    result = []
    cursor = mongo_db.receipts.find({"bound_user": user_id}).sort("created_at", -1)
    async for r in cursor:
        r["_id"] = str(r["_id"])
        result.append(r)
    return result

@router.get("/all")
async def all_receipts():
    result = []
    cursor = mongo_db.receipts.find({}).sort("created_at", -1)
    async for r in cursor:
        r["_id"] = str(r["_id"])
        result.append(r)
    return result
