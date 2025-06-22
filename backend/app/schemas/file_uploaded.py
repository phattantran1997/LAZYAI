from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ------------------------------------------------------------->

'''
    File uploaded schema would have those attributes:
        - File name
        - File path
        - Upload date
        - Size
        - Username (reference to the user who uploaded the file)
'''

# ------------------------------------------------------------->


class File(BaseModel):
    # id: Optional[str] = Field(None, alias="_id")
    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=255)
    upload_date: datetime
    size: int = Field(..., ge=0)  # Size in bytes, must be non-negative
    username: str = Field(..., min_length=1, max_length=50)  # Reference to the user who uploaded the file

    class Config:
        from_attributes = True
