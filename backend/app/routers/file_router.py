from fastapi import APIRouter, HTTPException, status
from app.schemas.file_uploaded import FileUploaded
from app.services.file_uploaded import *

# ----------------------- Router -------------------------------->

router = APIRouter(prefix="/files", tags=["files"])

# --------------------------- Create --------------------------------->

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=FileUploaded)
async def create_file_uploaded_endpoint(file_uploaded_in: FileUploaded):
    try:
        file_uploaded = create_file_uploaded(file_uploaded_in) # type: ignore
        return file_uploaded
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# --------------------------- Read --------------------------------->

@router.get("/{file_uploaded_id}", response_model=FileUploaded)
async def get_file_uploaded_endpoint(file_uploaded_id: str):
    try:
        file_uploaded = get_file_uploaded_by_id(file_uploaded_id)
        return file_uploaded
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.get("/", response_model=list[FileUploaded])
async def get_all_file_uploaded_endpoint(skip: int = 0, limit: int = 100):
    file_uploaded_records = get_all_file_uploaded(skip, limit)
    return file_uploaded_records

# --------------------------- Delete --------------------------------->

@router.delete("/{file_uploaded_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_uploaded_endpoint(file_uploaded_id: str):
    try:
        delete_file_uploaded(file_uploaded_id)
        return {"message": "File uploaded record deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))