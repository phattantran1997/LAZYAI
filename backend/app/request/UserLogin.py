from pydantic import BaseModel, Field

class UserLogin(BaseModel):
    username: str = Field(..., description="Username for the user")
    password: str = Field(..., description="Password for the user")