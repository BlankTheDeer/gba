# ?? Google reCAPTCHA verification
import httpx
from app.core.config import settings

async def verify_recaptcha(token: str) -> bool:
    if not settings.RECAPTCHA_SECRET:
        return True  # Skip if disabled
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": settings.RECAPTCHA_SECRET, "response": token}
        )
        data = resp.json()
        return data.get("success", False)
