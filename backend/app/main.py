#!/usr/bin/env python3
# 🦌 BlankTB Portal Backend Entry Point
# Powered by FastAPI, MongoDB, and Uvicorn
# (c) BlankTB — All Rights Reserved

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Core imports
from app.core.config import settings, init_mongo

# Routers
from app.routers import (
    auth, users, reps, admin, tokens, receipts, help, public, debug, status
)

# Services
from app.services.status_manager import auto_log_loop

# Load environment variables
load_dotenv()

# 🦌 FastAPI App Initialization
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for the BlankTB Portal (gba.blanktb.net)",
    version="1.0.0",
    contact={
        "name": "BlankTB Support",
        "url": f"{settings.DOMAIN}/help.html",
        "email": "support@blanktb.net"
    },
    license_info={
        "name": "BlankTB License",
        "url": f"{settings.DOMAIN}/license.html"
    }
)

# 🌐 CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.DOMAIN,
        "http://localhost",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Database & Background Task Setup
@app.on_event("startup")
async def startup_db():
    """Initialize MongoDB and start background status logger."""
    await init_mongo()
    asyncio.create_task(auto_log_loop())  # 🦌 automatic 10-minute monitoring loop


# 🧩 Routers Registration
app.include_router(public.router, prefix="/api/public", tags=["Public"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(reps.router, prefix="/api/reps", tags=["Reps"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(tokens.router, prefix="/api/tokens", tags=["Tokens"])
app.include_router(receipts.router, prefix="/api/receipts", tags=["Receipts"])
app.include_router(help.router, prefix="/api/help", tags=["Help"])
app.include_router(status.router, prefix="/api/status", tags=["Status"])
app.include_router(debug.router)  # Debug UI route — /api/debug/ui


# 🏠 Home Endpoint
@app.get("/")
async def home():
    """Simple health-check endpoint."""
    return {
        "status": "online",
        "message": "Welcome to the BlankTB Portal API 💜",
        "version": settings.APP_VERSION
    }
