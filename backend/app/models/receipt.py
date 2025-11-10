# ?? Receipt model for BlankTB Portal
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
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

class Receipt(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    token_id: str
    token_type_name: str
    token_days: int
    price: float
    buyer_name: Optional[str]
    buyer_email: EmailStr
    issued_by: str  # rep/admin id
    redeemed: bool = False
    bound_user: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    redeemed_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
