from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.schemas.file_uploaded import File

# ------------------------------------------------------------->

'''

    User schema would have those attributes:
        - Username
        - Name
        - Email
        - Password
        - Role
        
'''

# ------------------------- Register ---------------------------->

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field(default="user")

    class Config:
        from_attributes = True

# ------------------------- Log In ---------------------------->

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)  
    password: str = Field(..., min_length=8, max_length=100)  

    class Config:
        from_attributes = True

# ------------------------- Update ---------------------------->

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    email: Optional[EmailStr] = Field(None)
    role: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    
    class Config:
        from_attributes = True  

# -------------------------- Teacher ---------------------------->

class Teacher(UserRegister):
    file_uploaded: Optional[File] = None