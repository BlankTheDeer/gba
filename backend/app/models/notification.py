# ?? Notification model for BlankTB Portal
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
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

class Notification(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: str
    title: str
    message: str
    type: str = "info"  # info, warning, alert, success
    read: bool = False
    created_at: datetime = datetime.utcnow()

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
