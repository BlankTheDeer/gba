# ?? User model for BlankTB Portal
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    username: str
    email: EmailStr
    hashed_password: str
    roles: List[str] = ["user"]  # ["user"], ["rep"], ["admin"]
    avatar_url: Optional[str] = None
    theme: Optional[str] = "pastel_grove"
    sound_profile: Optional[str] = "forest"
    access_expiration: Optional[datetime] = None
    supervision: Dict[str, Optional[str]] = {
        "status": "none",  # none, supervised, locked
        "reason": None,
        "flag_count": 0
    }
    accepted_terms: bool = False
    created_at: datetime = datetime.utcnow()
    last_login: Optional[datetime] = None
    last_ip: Optional[str] = None
    last_device: Optional[str] = None
    storage_used: int = 0

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "username": "forestdeer",
                "email": "user@blanktb.net",
                "roles": ["user"],
                "access_expiration": "2025-12-31T00:00:00Z"
            }
        }
