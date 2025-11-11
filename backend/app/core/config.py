#!/usr/bin/env python3
# 🦌 BlankTB Portal — Backend Configuration (Schema-Validated Edition)
# Loads environment variables via Pydantic, validates against .env.schema.json,
# initializes MongoDB, and sends Discord startup alerts 💌
# (c) Blank The Deer — BlankTB.net

import os
import json
import asyncio
import datetime
import aiohttp
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError
from motor.motor_asyncio import AsyncIOMotorClient


# ------------------------------------------------------
# 🌿 Settings Model (Pydantic)
# ------------------------------------------------------
class Settings(BaseSettings):
    # 🌐 App Info
    APP_NAME: str = Field("BlankTB Portal Backend")
    APP_VERSION: str = Field("1.0.0")
    DOMAIN: str = Field("https://gba.blanktb.net")
    ENVIRONMENT: str = Field("production")
    DEBUG: bool = False

    # 🗄️ MongoDB
    MONGO_URI: str = Field("mongodb://localhost:27017/blanktb_portal")
    MONGO_DB_NAME: str = Field("blanktb_portal")
    MONGO_COLLECTION_PREFIX: str = Field("btb_")
    MONGO_CONNECT_TIMEOUT_MS: int = 30000
    MONGO_SOCKET_TIMEOUT_MS: int = 30000

    # 🔐 Security / Auth
    SECRET_KEY: str = Field("changemeplease")
    JWT_EXPIRY_HOURS: int = 24
    PASSWORD_SALT_ROUNDS: int = 12
    ADMIN_API_KEY: str = Field("changeme_admin_token_here")

    # ✉️ Email / SMTP
    MAIL_ENABLED: bool = False
    MAIL_SERVER: str = ""
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM_NAME: str = Field("BlankTB Support 🦌")
    MAIL_FROM_EMAIL: str = Field("support@blanktb.net")
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # 🧠 Google ReCAPTCHA
    RECAPTCHA_ENABLED: bool = True
    RECAPTCHA_SITE_KEY: str = ""
    RECAPTCHA_SECRET_KEY: str = ""

    # 💾 Cache / Status
    STATUS_CACHE_FILE: str = "/home/container/status_cache.json"
    STATUS_ALERT_FILE: str = "/home/container/status_alerts.json"
    CACHE_TTL_MINUTES: int = 10
    RETENTION_DAYS: int = 30
    LOG_INTERVAL_MINUTES: int = 10
    ALERT_DELAY_MINUTES: int = 5

    # 🦋 Discord Webhooks
    DISCORD_ALERT_WEBHOOK: str = ""
    DISCORD_UPTIME_WEBHOOK: str = ""
    DISCORD_ADMIN_WEBHOOK: str = ""
    DISCORD_DEBUG_WEBHOOK: str = ""
    DISCORD_HEALTHCHECK_WEBHOOK: str = ""
    # ⚙️ Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_DIR: str = "/home/container/logs"
    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "https://gba.blanktb.net",
            "http://localhost:5173",
        ]
    )

    # 🦌 Feature Toggles
    DEVELOPER_MODE: bool = False
    ENABLE_PUBLIC_STATUS: bool = True
    ENABLE_EMAIL_SERVICE: bool = True
    ENABLE_RECAPTCHA: bool = True
    ENABLE_DISCORD_ALERTS: bool = True
    ENABLE_ANALYTICS: bool = True
    HEALTHCHECK_TIMEOUT: int = Field(default=10)
    HEALTHCHECK_FAIL_THRESHOLD: int = Field(default=3)
    BACKEND_BASE_URL: str = Field(default="https://backend.blanktb.net")
    HOME: str = Field(default="/home/blankthedeer")

    # 🌈 Branding
    BRAND_NAME: str = "BlankTB"
    BRAND_LOGO_URL: str = "https://cdn.blanktb.net/assets/logo_circular.svg"
    BRAND_PRIMARY_COLOR: str = "#A7E8B9"
    BRAND_ACCENT_COLOR: str = "#F6D5F7"
    BRAND_FAVICON_URL: str = "https://cdn.blanktb.net/assets/favicon.ico"

    # 📦 Paths & Misc
    DATA_DIR: str = "/home/container/app/data"
    TEMP_DIR: str = "/home/container/tmp"
    UPLOAD_DIR: str = "/home/container/uploads"
    BACKUP_DIR: str = "/home/container/backups"

    # 🕒 System Defaults
    FORCE_SSL_REDIRECT: bool = True
    TIMEZONE: str = "UTC"
    FASTAPI_WORKERS: int = 1

    class Config:
        env_file = ".env"
        case_sensitive = False


# ------------------------------------------------------
# 🌸 Schema Validation Helper
# ------------------------------------------------------
def validate_schema(schema_path: str = ".env.schema.json", env_path: str = ".env"):
    """Compare .env variables with .env.schema.json and warn on mismatches."""
    if not os.path.exists(schema_path):
        print("🌸 No .env.schema.json found — skipping schema validation.")
        return

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        required_vars = schema.get("required", [])
        properties = schema.get("properties", {})

        with open(env_path, "r", encoding="utf-8") as f:
            env_lines = [
                line.split("=", 1)[0].strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]

        missing = [v for v in required_vars if v not in env_lines]
        extras = [v for v in env_lines if v not in properties]

        if not missing and not extras:
            print("🦌 .env perfectly matches .env.schema.json — sparkle clean ✨")
        else:
            if missing:
                print("⚠️ Missing required variables:")
                for v in missing:
                    print(f"   🌸 {v}")
            if extras:
                print("💡 Extra variables in .env not found in schema:")
                for v in extras:
                    print(f"   🌿 {v}")

    except Exception as e:
        print(f"❌ Failed to validate schema: {e}")


# ------------------------------------------------------
# 🌿 Load and Validate Environment
# ------------------------------------------------------
try:
    settings = Settings()
    print("🦌 Loaded and validated environment variables successfully.")
    validate_schema()
except ValidationError as e:
    print("❌ Invalid environment configuration! Please fix your .env file.\n")
    print(e.json(indent=2))
    raise SystemExit(1)


# ------------------------------------------------------
# 🍃 MongoDB Initialization
# ------------------------------------------------------
mongo_client = None
mongo_db = None


async def init_mongo():
    """Initialize MongoDB connection and create indexes."""
    global mongo_client, mongo_db

    try:
        mongo_client = AsyncIOMotorClient(
            settings.MONGO_URI,
            connectTimeoutMS=settings.MONGO_CONNECT_TIMEOUT_MS,
            socketTimeoutMS=settings.MONGO_SOCKET_TIMEOUT_MS,
        )
        mongo_db = mongo_client.get_default_database()
        print(f"🦌 MongoDB connected to {mongo_db.name}")

        # ✅ Create indexes
        await mongo_db.users.create_index("username", unique=True)
        await mongo_db.users.create_index("email", unique=True)
        await mongo_db.tokens.create_index("token_code", unique=True)
        await mongo_db.receipts.create_index("token_id", unique=True)
        await mongo_db.help_tickets.create_index("email")
        await mongo_db.logs.create_index("created_at")

    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return

    # 🪄 Print local summary & send webhook
    await asyncio.sleep(0.5)
    print_startup_summary()
    await send_discord_startup_message()


# ------------------------------------------------------
# 🌷 Startup Summary
# ------------------------------------------------------
def print_startup_summary():
    """Pretty-print service configuration summary on startup."""
    print("\n🦌✨ BlankTB Portal Backend — Startup Summary ✨🦌")
    print("=" * 65)
    print(f"🌐 Environment:     {settings.ENVIRONMENT}")
    print(f"🧩 Version:         {settings.APP_VERSION}")
    print(f"🌍 Domain:          {settings.DOMAIN}")
    print(f"🗄️  MongoDB:         {settings.MONGO_DB_NAME}")
    print("-" * 65)
    print("🧠 Feature Flags:")
    print(f"   📬 Email Service:      {'✅ Enabled' if settings.MAIL_ENABLED else '❌ Disabled'}")
    print(f"   🔒 ReCAPTCHA:          {'✅ Enabled' if settings.RECAPTCHA_ENABLED else '❌ Disabled'}")
    print(f"   🦋 Discord Alerts:     {'✅ Enabled' if settings.ENABLE_DISCORD_ALERTS else '❌ Disabled'}")
    print(f"   📊 Analytics:          {'✅ Enabled' if settings.ENABLE_ANALYTICS else '❌ Disabled'}")
    print(f"   👩‍💻 Developer Mode:    {'🧪 Yes' if settings.DEVELOPER_MODE else '🚫 No'}")
    print("-" * 65)
    print("💾 Cache Settings:")
    print(f"   🕒 Retention Days:     {settings.RETENTION_DAYS}")
    print(f"   🔁 Log Interval:       {settings.LOG_INTERVAL_MINUTES} min")
    print(f"   🗂️ Cache File:         {settings.STATUS_CACHE_FILE}")
    print(f"   ⚙️  Alert File:         {settings.STATUS_ALERT_FILE}")
    print("-" * 65)
    print(f"🦌 Brand: {settings.BRAND_NAME} | Primary {settings.BRAND_PRIMARY_COLOR} • Accent {settings.BRAND_ACCENT_COLOR}")
    print("=" * 65)
    print("✨ Backend startup complete and ready to serve!\n")


# ------------------------------------------------------
# 💬 Discord Debug Webhook Announcement
# ------------------------------------------------------
async def send_discord_startup_message():
    """Sends a pretty startup notification to Discord debug webhook."""
    if not settings.DISCORD_DEBUG_WEBHOOK:
        print("🦋 Debug webhook not set, skipping Discord startup message.")
        return

    embed = {
        "title": "🦌 BlankTB Backend is Online!",
        "description": (
            f"**Environment:** {settings.ENVIRONMENT.capitalize()}\n"
            f"**MongoDB:** `{settings.MONGO_DB_NAME}`\n"
            f"**Version:** `{settings.APP_VERSION}`\n"
            f"**Domain:** {settings.DOMAIN}\n"
        ),
        "color": int(settings.BRAND_PRIMARY_COLOR.replace('#', '0x'), 16),
        "thumbnail": {"url": settings.BRAND_LOGO_URL},
        "footer": {"text": "BlankTB Portal • Backend Startup"},
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }

    payload = {"embeds": [embed]}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(settings.DISCORD_DEBUG_WEBHOOK, json=payload) as resp:
                if resp.status == 204:
                    print("🦋 Sent startup notification to Discord debug webhook.")
                else:
                    print(f"⚠️ Failed to send startup webhook (HTTP {resp.status}).")
    except Exception as e:
        print(f"❌ Discord startup webhook failed: {e}")
