# ?? BlankTB Portal Config + Index Initialization
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "BlankTB Portal")
    DOMAIN: str = os.getenv("DOMAIN", "https://gba.blanktb.net")
    MONGO_URI: str = os.getenv("MONGO_URI")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "changemeplease")
    RECAPTCHA_SECRET: str = os.getenv("RECAPTCHA_SECRET", "")
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_USER: str = os.getenv("MAIL_USER", "")
    MAIL_PASS: str = os.getenv("MAIL_PASS", "")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
settings = Settings()
mongo_client = None
mongo_db = None

async def init_mongo():
    """Initialize MongoDB connection and create indexes."""
    global mongo_client, mongo_db
    mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
    mongo_db = mongo_client.get_default_database()
    print(f"MongoDB connected to {mongo_db.name}")

    # Indexes
    await mongo_db.users.create_index("username", unique=True)
    await mongo_db.users.create_index("email", unique=True)
    await mongo_db.tokens.create_index("token_code", unique=True)
    await mongo_db.receipts.create_index("token_id", unique=True)
    await mongo_db.help_tickets.create_index("email")
    await mongo_db.logs.create_index("created_at")
