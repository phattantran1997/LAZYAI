from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    username: str = Field(..., description="Username for the user")
    name: str = Field(..., description="Name of the user")
    email: str = Field(..., description="Email of the user")
    password: str = Field(..., description="Password for the user")
    role: str = Field(..., description="Role of the user")
