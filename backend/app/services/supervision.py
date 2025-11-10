# ?? Supervision logic — detects suspicious logins and locks accounts if needed
from datetime import datetime
from app.core.config import mongo_db

MAX_FLAGS = 3  # number of anomalies before supervision flag
MAX_LOCKS = 5  # number of flags before lock

async def record_login_activity(user, ip: str, device: str):
    """Record login, compare with previous, and detect anomalies."""
    if not user.last_ip:
        await mongo_db.users.update_one({"_id": user.id}, {"$set": {"last_ip": ip, "last_device": device}})
        return

    anomalies = 0
    if user.last_ip != ip:
        anomalies += 1
    if user.last_device != device:
        anomalies += 1

    if anomalies > 0:
        user.supervision["flag_count"] += anomalies
        status = "supervised" if user.supervision["flag_count"] >= MAX_FLAGS else "none"
        if user.supervision["flag_count"] >= MAX_LOCKS:
            status = "locked"
        await mongo_db.users.update_one(
            {"_id": user.id},
            {"$set": {
                "supervision.status": status,
                "supervision.flag_count": user.supervision["flag_count"],
                "supervision.reason": "Unusual login activity",
                "last_ip": ip,
                "last_device": device,
                "last_login": datetime.utcnow()
            }}
        )
        # Log event
        await mongo_db.logs.insert_one({
            "actor_id": str(user.id),
            "action": "supervision_update",
            "details": {"status": status, "ip": ip, "device": device},
            "created_at": datetime.utcnow(),
            "severity": "warning"
        })

async def auto_lock_inactive_accounts():
    """Lock accounts with supervision flag left unresolved for too long."""
    users = mongo_db.users
    flagged = users.find({"supervision.status": "supervised"})
    async for u in flagged:
        if u["supervision"]["flag_count"] > MAX_LOCKS:
            await users.update_one({"_id": u["_id"]}, {"$set": {"supervision.status": "locked"}})
