from pydantic import BaseModel, Field

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


class FileUploaded(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=255)
    upload_date: str  # ISO format date string
    size: int = Field(..., ge=0)  # Size in bytes, must be non-negative
    username: str = Field(..., min_length=1, max_length=50)  # Reference to the user who uploaded the file
