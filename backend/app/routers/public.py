# ?? Public Routes — health checks, announcements, FAQ
from fastapi import APIRouter
from datetime import datetime
from app.core.config import mongo_db

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow()}

@router.get("/announcements")
async def announcements():
    result = []
    cursor = mongo_db.announcements.find({}).sort("date", -1)
    async for a in cursor:
        a["_id"] = str(a["_id"])
        result.append(a)
    return result

@router.get("/faq")
async def faq():
    return [
        {"q": "What is BlankTB Portal?", "a": "A private web portal for uploading and playing your own legally owned GBA ROMs."},
        {"q": "Do you provide games?", "a": "No. ROMs are user-uploaded only. BlankTB does not host or distribute any copyrighted content."},
        {"q": "How do tokens work?", "a": "Tokens provide time-limited access. Redeem them on the portal or request a new one from a rep."},
        {"q": "Is there a refund policy?", "a": "All payments are final and handled externally. The portal only records receipt and access data."},
    ]
