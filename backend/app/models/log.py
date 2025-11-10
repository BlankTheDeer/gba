# ?? System log model for BlankTB Portal
from datetime import datetime
from pydantic import BaseModel, Field
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

class Log(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    actor_id: Optional[str]
    action: str
    target: Optional[str]
    details: Optional[Dict[str, str]]
    created_at: datetime = datetime.utcnow()
    severity: str = "info"  # info, warning, error, critical

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
