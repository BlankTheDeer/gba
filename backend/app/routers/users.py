# ?? User Profile & Token Extension Routes
from fastapi import APIRouter, Form, HTTPException
from app.core.config import mongo_db
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    user = await mongo_db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return user

@router.post("/profile/update")
async def update_profile(user_id: str = Form(...), email: str = Form(...), theme: str = Form(...), sound: str = Form(...)):
    await mongo_db.users.update_one({"_id": user_id}, {"$set": {"email": email, "theme": theme, "sound_profile": sound}})
    return {"status": "updated"}

@router.post("/redeem_extend")
async def redeem_extend(user_id: str = Form(...), token_code: str = Form(...)):
    tokens = mongo_db.tokens
    user = await mongo_db.users.find_one({"_id": user_id})
    token_doc = await tokens.find_one({"token_code": token_code, "redeemed": False})
    if not token_doc:
        raise HTTPException(status_code=404, detail="Invalid or used token")

    now = datetime.utcnow()
    new_expiry = user["access_expiration"] or now
    new_expiry += timedelta(days=token_doc["days"])
    await mongo_db.users.update_one({"_id": user_id}, {"$set": {"access_expiration": new_expiry}})
    await tokens.update_one({"_id": token_doc["_id"]}, {"$set": {"redeemed": True, "redeemed_at": now, "bound_user": user_id}})
    return {"status": "extended", "expires_on": new_expiry}
