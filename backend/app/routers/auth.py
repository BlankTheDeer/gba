# ?? Authentication & Token Redeem Routes — BlankTB Portal
from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from app.core.security import verify_password, hash_password
from app.core.config import mongo_db
from app.services.session_manager import create_user_session, invalidate_session
from app.services.supervision import record_login_activity
from app.core.recaptcha import verify_recaptcha
from datetime import datetime
import secrets

router = APIRouter()

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), recaptcha: str = Form(None)):
    users = mongo_db.users
    user = await users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    if user["supervision"]["status"] == "locked":
        return JSONResponse({"error": "locked", "message": "Your account is locked. Please contact admin."}, status_code=403)

    # record IP/device
    client_ip = request.client.host
    client_device = request.headers.get("User-Agent", "unknown")
    await record_login_activity(user, client_ip, client_device)

    # create session
    jwt = await create_user_session(str(user["_id"]), client_ip, client_device)
    return {"status": "success", "token": jwt, "roles": user["roles"]}

@router.post("/logout")
async def logout(token: str = Form(...)):
    await invalidate_session(token)
    return {"status": "logged_out"}

@router.post("/redeem")
async def redeem_token(request: Request, token_code: str = Form(...), new_user: bool = Form(False)):
    tokens = mongo_db.tokens
    users = mongo_db.users
    receipts = mongo_db.receipts

    token_doc = await tokens.find_one({"token_code": token_code, "redeemed": False})
    if not token_doc:
        raise HTTPException(status_code=404, detail="Invalid or already used token")

    if new_user:
        username = f"user_{secrets.token_hex(3)}"
        password = secrets.token_hex(4)
        hashed = hash_password(password)
        new_user_doc = {
            "username": username,
            "email": f"{username}@blanktb.net",
            "hashed_password": hashed,
            "roles": ["user"],
            "access_expiration": datetime.utcnow(),
            "accepted_terms": False
        }
        result = await users.insert_one(new_user_doc)
        user_id = str(result.inserted_id)
        msg = f"Created new user {username}"
    else:
        # find user later from session context (handled in frontend)
        msg = "Existing user redeeming token"
        user_id = None

    # mark token & receipt
    await tokens.update_one({"_id": token_doc["_id"]}, {"$set": {"redeemed": True, "redeemed_at": datetime.utcnow(), "bound_user": user_id}})
    await receipts.update_one({"token_id": token_code}, {"$set": {"redeemed": True, "bound_user": user_id, "redeemed_at": datetime.utcnow()}})

    return {"status": "success", "message": msg, "token_days": token_doc["days"], "price": token_doc["price"]}

@router.post("/accept_policies")
async def accept_policies(user_id: str = Form(...)):
    await mongo_db.users.update_one({"_id": user_id}, {"$set": {"accepted_terms": True}})
    return {"status": "accepted"}
