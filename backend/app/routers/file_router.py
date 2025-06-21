from fastapi import APIRouter, HTTPException, status

from app.schemas.file_uploaded import File
from app.services.file_uploaded import *

# ----------------------- Router -------------------------------->

router = APIRouter(prefix="/files", tags=["files"])

# --------------------------- Create --------------------------------->

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_file_uploaded_endpoint(file_uploaded_in: File):
    try:
        file_uploaded = create_file_uploaded(file_uploaded_in) 
        return {"message": "File uploaded successfully", "file_id": str(file_uploaded.id)}  # type: ignore
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# --------------------------- Read --------------------------------->

@router.get("/{file_uploaded_id}", response_model=File)
async def get_file_uploaded_endpoint(file_uploaded_id: str):
    try:
        file_uploaded = get_file_uploaded_by_id(file_uploaded_id)
        return file_uploaded
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --------------------------- Delete --------------------------------->

@router.delete("/{file_uploaded_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_uploaded_endpoint(file_uploaded_id: str):
    try:
        delete_file_uploaded(file_uploaded_id)
        return {"message": "File uploaded record deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))