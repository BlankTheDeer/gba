# ?? Token Information — for admin and system integrations
from fastapi import APIRouter
from app.core.config import mongo_db

router = APIRouter()

@router.get("/active")
async def active_tokens():
    result = []
    cursor = mongo_db.token_types.find({"active": True})
    async for t in cursor:
        t["_id"] = str(t["_id"])
        result.append(t)
    return result

@router.get("/all")
async def all_tokens():
    result = []
    cursor = mongo_db.tokens.find({}).sort("created_at", -1)
    async for t in cursor:
        t["_id"] = str(t["_id"])
        result.append(t)
    return result
