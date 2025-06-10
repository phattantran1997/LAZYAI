from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId

# Custom ObjectId for Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator: Any) -> dict[str, Any]:
        return {"type": "string"}

# Base schema shared between creation and DB response
class UserBase(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(...)
    is_teacher: bool = Field(default=False)

# Schema for creating a new user
class UserCreate(UserBase):
    password: str

# Schema used internally (with MongoDB ObjectId and timestamps)
class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

# Schema for returning user info (e.g. API response, no password)
class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
