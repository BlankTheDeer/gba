# ?? Admin Routes — manage users, tokens, receipts, reps, analytics, and logs
from fastapi import APIRouter, Form, HTTPException
from datetime import datetime
from app.core.config import mongo_db
import secrets

router = APIRouter()

# ---- USERS ----
@router.get("/users")
async def list_users():
    users = []
    cursor = mongo_db.users.find({})
    async for user in cursor:
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

@router.post("/user/lock")
async def lock_user(user_id: str = Form(...), reason: str = Form("Manual lock by admin")):
    await mongo_db.users.update_one(
        {"_id": user_id},
        {"$set": {"supervision.status": "locked", "supervision.reason": reason}}
    )
    await mongo_db.logs.insert_one({
        "actor_id": "admin",
        "action": "user_lock",
        "target": user_id,
        "details": {"reason": reason},
        "created_at": datetime.utcnow()
    })
    return {"status": "locked"}

@router.post("/user/unlock")
async def unlock_user(user_id: str = Form(...)):
    await mongo_db.users.update_one(
        {"_id": user_id},
        {"$set": {"supervision.status": "none", "supervision.reason": None, "supervision.flag_count": 0}}
    )
    return {"status": "unlocked"}

# ---- TOKEN MANAGEMENT ----
@router.post("/token/create")
async def create_token_type(name: str = Form(...), days: int = Form(...), price: float = Form(...), created_by: str = Form(...)):
    token_type = {
        "name": name,
        "days": days,
        "price": price,
        "active": True,
        "created_by": created_by,
        "created_at": datetime.utcnow()
    }
    result = await mongo_db.token_types.insert_one(token_type)
    return {"status": "created", "token_type_id": str(result.inserted_id)}

@router.get("/token/types")
async def get_token_types():
    types = []
    cursor = mongo_db.token_types.find({"active": True})
    async for t in cursor:
        t["_id"] = str(t["_id"])
        types.append(t)
    return types

@router.post("/token/deactivate")
async def deactivate_token_type(type_id: str = Form(...)):
    await mongo_db.token_types.update_one({"_id": type_id}, {"$set": {"active": False}})
    return {"status": "deactivated"}

# ---- REPS ----
@router.post("/rep/create")
async def create_rep(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    from app.core.security import hash_password
    hashed = hash_password(password)
    rep_doc = {
        "username": username,
        "email": email,
        "hashed_password": hashed,
        "roles": ["rep"],
        "access_expiration": None,
        "created_at": datetime.utcnow()
    }
    await mongo_db.users.insert_one(rep_doc)
    return {"status": "rep_created", "username": username}

@router.get("/reps")
async def list_reps():
    reps = []
    cursor = mongo_db.users.find({"roles": "rep"})
    async for rep in cursor:
        rep["_id"] = str(rep["_id"])
        reps.append(rep)
    return reps

# ---- RECEIPTS & ANALYTICS ----
@router.get("/receipts")
async def all_receipts():
    data = []
    cursor = mongo_db.receipts.find({})
    async for r in cursor:
        r["_id"] = str(r["_id"])
        data.append(r)
    return data

@router.get("/analytics/summary")
async def analytics_summary():
    user_count = await mongo_db.users.count_documents({})
    receipt_count = await mongo_db.receipts.count_documents({})
    token_types = await mongo_db.token_types.count_documents({"active": True})
    locked = await mongo_db.users.count_documents({"supervision.status": "locked"})
    return {
        "users": user_count,
        "receipts": receipt_count,
        "token_types": token_types,
        "locked_users": locked
    }

@router.get("/logs")
async def view_logs(limit: int = 100):
    logs = []
    cursor = mongo_db.logs.find({}).sort("created_at", -1).limit(limit)
    async for log in cursor:
        log["_id"] = str(log["_id"])
        logs.append(log)
    return logs
