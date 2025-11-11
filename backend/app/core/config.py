#!/usr/bin/env python3
# 🦌 BlankTB Portal — Backend Configuration
# Loads environment variables, initializes MongoDB, and defines core settings.
# Includes a startup summary & Discord boot announcement!
# (c) Blank The Deer — BlankTB.net

import os
import asyncio
import datetime
import aiohttp
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# 🌿 Load environment variables
load_dotenv()


# ------------------------------------------------------
# 🧩 Settings Class
# ------------------------------------------------------
class Settings:
    # 🌐 App Info
    APP_NAME: str = os.getenv("APP_NAME", "BlankTB Portal Backend")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DOMAIN: str = os.getenv("DOMAIN", "https://gba.blanktb.net")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 🗄️ MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/blanktb_portal")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "blanktb_portal")
    MONGO_COLLECTION_PREFIX: str = os.getenv("MONGO_COLLECTION_PREFIX", "btb_")
    MONGO_CONNECT_TIMEOUT_MS: int = int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", 30000))
    MONGO_SOCKET_TIMEOUT_MS: int = int(os.getenv("MONGO_SOCKET_TIMEOUT_MS", 30000))

    # 🔐 Security / Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changemeplease")
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", 24))
    PASSWORD_SALT_ROUNDS: int = int(os.getenv("PASSWORD_SALT_ROUNDS", 12))
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "changeme_admin_token_here")

    # ✉️ Email / SMTP
    MAIL_ENABLED: bool = os.getenv("MAIL_ENABLED", "false").lower() == "true"
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "BlankTB Support 🦌")
    MAIL_FROM_EMAIL: str = os.getenv("MAIL_FROM_EMAIL", "support@blanktb.net")
    MAIL_TLS: bool = os.getenv("MAIL_TLS", "true").lower() == "true"
    MAIL_SSL: bool = os.getenv("MAIL_SSL", "false").lower() == "true"

    # 🧠 Google ReCAPTCHA
    RECAPTCHA_ENABLED: bool = os.getenv("RECAPTCHA_ENABLED", "true").lower() == "true"
    RECAPTCHA_SITE_KEY: str = os.getenv("RECAPTCHA_SITE_KEY", "")
    RECAPTCHA_SECRET_KEY: str = os.getenv("RECAPTCHA_SECRET_KEY", "")

    # 💾 Cache / Status Management
    STATUS_CACHE_FILE: str = os.getenv("STATUS_CACHE_FILE", "/home/container/status_cache.json")
    STATUS_ALERT_FILE: str = os.getenv("STATUS_ALERT_FILE", "/home/container/status_alerts.json")
    CACHE_TTL_MINUTES: int = int(os.getenv("CACHE_TTL_MINUTES", 10))
    RETENTION_DAYS: int = int(os.getenv("RETENTION_DAYS", 30))
    LOG_INTERVAL_MINUTES: int = int(os.getenv("LOG_INTERVAL_MINUTES", 10))
    ALERT_DELAY_MINUTES: int = int(os.getenv("ALERT_DELAY_MINUTES", 5))

    # 🦋 Discord Webhooks
    DISCORD_ALERT_WEBHOOK: str = os.getenv("DISCORD_ALERT_WEBHOOK", "")
    DISCORD_UPTIME_WEBHOOK: str = os.getenv("DISCORD_UPTIME_WEBHOOK", "")
    DISCORD_ADMIN_WEBHOOK: str = os.getenv("DISCORD_ADMIN_WEBHOOK", "")
    DISCORD_DEBUG_WEBHOOK: str = os.getenv("DISCORD_DEBUG_WEBHOOK", "")

    # ⚙️ Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    _PORT_ENV = os.getenv("PORT", "8000")
    try:
        PORT: int = int(_PORT_ENV)
    except ValueError:
        print(f"⚠️ Invalid PORT value '{_PORT_ENV}', falling back to 8000.")
        PORT: int = 8000

    LOG_DIR: str = os.getenv("LOG_DIR", "/home/container/logs")
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "https://gba.blanktb.net,http://localhost:5173"
    ).split(",")

    # 🦌 Feature Toggles
    DEVELOPER_MODE: bool = os.getenv("DEVELOPER_MODE", "false").lower() == "true"
    ENABLE_PUBLIC_STATUS: bool = os.getenv("ENABLE_PUBLIC_STATUS", "true").lower() == "true"
    ENABLE_EMAIL_SERVICE: bool = os.getenv("ENABLE_EMAIL_SERVICE", "true").lower() == "true"
    ENABLE_RECAPTCHA: bool = os.getenv("ENABLE_RECAPTCHA", "true").lower() == "true"
    ENABLE_DISCORD_ALERTS: bool = os.getenv("ENABLE_DISCORD_ALERTS", "true").lower() == "true"
    ENABLE_ANALYTICS: bool = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"

    # 🌈 Branding
    BRAND_NAME: str = os.getenv("BRAND_NAME", "BlankTB")
    BRAND_LOGO_URL: str = os.getenv("BRAND_LOGO_URL", "https://cdn.blanktb.net/assets/logo_circular.svg")
    BRAND_PRIMARY_COLOR: str = os.getenv("BRAND_PRIMARY_COLOR", "#A7E8B9")
    BRAND_ACCENT_COLOR: str = os.getenv("BRAND_ACCENT_COLOR", "#F6D5F7")
    BRAND_FAVICON_URL: str = os.getenv("BRAND_FAVICON_URL", "https://cdn.blanktb.net/assets/favicon.ico")

    # 📦 Paths & Misc
    DATA_DIR: str = os.getenv("DATA_DIR", "/home/container/app/data")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/home/container/tmp")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/home/container/uploads")
    BACKUP_DIR: str = os.getenv("BACKUP_DIR", "/home/container/backups")

    # 🕒 System Defaults
    FORCE_SSL_REDIRECT: bool = os.getenv("FORCE_SSL_REDIRECT", "true").lower() == "true"
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")
    FASTAPI_WORKERS: int = int(os.getenv("FASTAPI_WORKERS", 1))


# Global instance
settings = Settings()

mongo_client = None
mongo_db = None


# ------------------------------------------------------
# 🍃 MongoDB Initialization
# ------------------------------------------------------
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
# 🌸 Startup Summary
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
        "color": 0xA7E8B9,
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
