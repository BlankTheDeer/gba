# ?? Help & Support Routes for BlankTB Portal
from fastapi import APIRouter, Form, HTTPException
from app.core.config import mongo_db
from app.core.recaptcha import verify_recaptcha
from datetime import datetime

router = APIRouter()

@router.post("/contact")
async def contact_admin(
    name: str = Form(...),
    email: str = Form(...),
    category: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    recaptcha: str = Form(None)
):
    if not await verify_recaptcha(recaptcha):
        raise HTTPException(status_code=403, detail="reCAPTCHA failed")

    ticket = {
        "name": name,
        "email": email,
        "category": category,
        "subject": subject,
        "message": message,
        "status": "open",
        "created_at": datetime.utcnow()
    }
    result = await mongo_db.help_tickets.insert_one(ticket)
    return {"status": "received", "ticket_id": str(result.inserted_id)}

@router.get("/tickets/{email}")
async def list_user_tickets(email: str):
    tickets = mongo_db.help_tickets
    cursor = tickets.find({"email": email}).sort("created_at", -1)
    result = []
    async for t in cursor:
        t["_id"] = str(t["_id"])
        result.append(t)
    return result
