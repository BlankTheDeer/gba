# í ½í²¼ Rep Routes â€” issue receipts & view their records
from fastapi import APIRouter, Form, HTTPException
from datetime import datetime
from app.core.config import mongo_db
from app.core.emailer import send_email
import secrets

router = APIRouter()

@router.get("/tokens")
async def available_tokens():
    tokens = []
    cursor = mongo_db.token_types.find({"active": True})
    async for t in cursor:
        tokens.append({
            "name": t["name"],
            "days": t["days"],
            "price": t["price"],
            "id": str(t["_id"])
        })
    return tokens


@router.post("/receipt/create")
async def create_receipt(
    buyer_name: str = Form(...),
    buyer_email: str = Form(...),
    token_type_id: str = Form(...),
    issued_by: str = Form(...)
):
    # Fetch token type
    token_type = await mongo_db.token_types.find_one({"_id": token_type_id})
    if not token_type:
        raise HTTPException(status_code=404, detail="Token type not found")

    # Generate token and receipt
    token_code = secrets.token_hex(6).upper()
    token_doc = {
        "token_code": token_code,
        "token_type_id": str(token_type["_id"]),
        "days": token_type["days"],
        "price": token_type["price"],
        "created_at": datetime.utcnow()
    }
    await mongo_db.tokens.insert_one(token_doc)

    receipt_doc = {
        "token_id": token_code,
        "token_type_name": token_type["name"],
        "token_days": token_type["days"],
        "price": token_type["price"],
        "buyer_name": buyer_name,
        "buyer_email": buyer_email,
        "issued_by": issued_by,
        "redeemed": False,
        "created_at": datetime.utcnow()
    }
    await mongo_db.receipts.insert_one(receipt_doc)

    # Send email with token
    html = f"""
    <h2>BlankTB Portal Access Token</h2>
    <p>Hi {buyer_name},</p>
    <p>Thank you for your purchase! Hereâ€™s your access token:</p>
    <div style='padding:10px;background:#f3f3f3;border-radius:8px;'><strong>{token_code}</strong></div>
    <p>This token grants you {token_type['days']} days of access to gba.blanktb.net.</p>
    <p>To redeem, visit <a href='https://gba.blanktb.net/redeem.html'>https://gba.blanktb.net/redeem.html</a>.</p>
    <p>” The BlankTB Team </p>"""
    await send_email(buyer_email, "Your BlankTB Portal Access Token", html)
    return {"status": "sent", "token": token_code}


@router.get("/receipts/{rep_id}")
async def rep_receipts(rep_id: str):
    cursor = mongo_db.receipts.find({"issued_by": rep_id}).sort("created_at", -1)
    results = []
    async for r in cursor:
        r["_id"] = str(r["_id"])
        results.append(r)
    return results
