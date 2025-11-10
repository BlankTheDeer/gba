# ?? Help ticket model for BlankTB Portal
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
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

class HelpTicket(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: Optional[str] = None
    name: str
    email: EmailStr
    category: str
    subject: str
    message: str
    status: str = "open"  # open, replied, closed
    context: Optional[Dict[str, str]] = None
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
