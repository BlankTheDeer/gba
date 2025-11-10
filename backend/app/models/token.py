# ?? Token and TokenType models for BlankTB Portal
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

class TokenType(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    days: int
    price: float
    active: bool = True
    created_by: str
    created_at: datetime = datetime.utcnow()

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Token(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    token_code: str
    token_type_id: str
    days: int
    price: float
    receipt_id: Optional[str] = None
    redeemed: bool = False
    bound_user: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    redeemed_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
