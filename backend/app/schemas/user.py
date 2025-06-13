from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# ------------------------ Base ------------------------->

class UserBase(BaseModel):
    username: str = Field(..., description="Unique username for the user")
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    role: str = Field(..., description="Role of the user")  # 'user', 'admin', etc.

# ------------------------- Create ---------------------------->

class UserCreate(UserBase):
    password: str = Field(..., description="Password for the user")  # Required for creation

# ------------------------- Read ---------------------------->

class UserRead(UserBase):
    id: str  # MongoDB ObjectId converted to string for the response

    class Config:
        orm_mode = True  

# ------------------------- Update ---------------------------->

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="New username for the user")
    name: Optional[str] = Field(None, description="New name for the user")
    email: Optional[EmailStr] = Field(None, description="New email for the user")
    role: Optional[str] = Field(None, description="New role of the user")
    is_active: Optional[bool] = Field(None, description="New active status")
    
    class Config:
        orm_mode = True  
