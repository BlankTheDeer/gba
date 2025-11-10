# ?? Session Manager — handles one-session-per-user logic
from datetime import datetime
from app.core.security import create_jwt_token, decode_jwt_token
from app.core.config import mongo_db

async def create_user_session(user_id: str, ip: str, device: str) -> str:
    """Create or refresh a user session, invalidating older ones."""
    sessions = mongo_db.sessions
    await sessions.delete_many({"user_id": user_id})  # Enforce single session
    token_data = {"user_id": user_id, "ip": ip, "device": device}
    jwt = create_jwt_token(token_data, expires_in=86400)
    await sessions.insert_one({
        "user_id": user_id,
        "ip": ip,
        "device": device,
        "token": jwt,
        "created_at": datetime.utcnow(),
        "active": True
    })
    return jwt

async def invalidate_session(jwt_token: str):
    """Mark a session as invalidated."""
    await mongo_db.sessions.update_one({"token": jwt_token}, {"$set": {"active": False}})

async def is_session_active(jwt_token: str) -> bool:
    """Check if a session token is still active."""
    decoded = decode_jwt_token(jwt_token)
    if not decoded:
        return False
    record = await mongo_db.sessions.find_one({"token": jwt_token, "active": True})
    return record is not None
