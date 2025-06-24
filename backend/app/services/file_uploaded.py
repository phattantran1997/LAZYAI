from fastapi import UploadFile, HTTPException
from datetime import datetime

from app.models.file_uploaded import FileUploaded 
from app.schemas.file_uploaded import File

from dotenv import load_dotenv
import os   

load_dotenv()

# ---------------------- Folder Directory ------------------------>

upload_folder = os.getenv("upload_folder", "uploads")

# -------------------------- Convert UploadFile to right format ---------------------------->

def convert_upload_file(file_uploaded_in: UploadFile, username) -> File:
    file_name = file_uploaded_in.filename or "default_file_name"
    file_path = upload_folder + "/" + file_name
    return File(
        file_name=file_name,
        file_path=file_path,
        upload_date=datetime.now(),  # Use current date and time for upload_date
        size=file_uploaded_in.size or 0,  
        username=username or "default_username"  # Default username if not provided
    )

# ---------------------------- Create / Upload ------------------------>

async def create_file_uploaded(file_uploaded_in: UploadFile, username: str) -> FileUploaded:

        # Check in the database if the file's name has been existed
        existing_file = FileUploaded.objects(file_name=file_uploaded_in.filename).first()  # type: ignore
        if existing_file:
            raise HTTPException(status_code=400, detail="File with this name already exists")
        
        # Convert to file
        file_converted: File = convert_upload_file(file_uploaded_in, username)

        # Create and save the new file uploaded record in the database
        file = FileUploaded(
            file_name=file_converted.file_name,
            file_path=file_converted.file_path,
            upload_date=file_converted.upload_date,
            size=file_converted.size,
            username=file_converted.username
        )
        file.save()  

        # Save the content of file in database
        data = await file_uploaded_in.read()  # Read the file data
        file_path = str(file.file_path)[len('file://'):]
        with open(file_path, "wb") as f:
            f.write(data)  

        return file


# ---------------------------- Read ------------------------>

def get_file_uploaded_by_id(file_uploaded_id: str) -> FileUploaded:
    file_uploaded = FileUploaded.objects(id=file_uploaded_id).first()  # type: ignore
    if not file_uploaded:
        raise HTTPException(status_code=400, detail="File uploaded record not found")
    return file_uploaded        

# ---------------------------- Delete ------------------------>

def delete_file_uploaded(file_uploaded_id: str) -> bool:
    file_uploaded = FileUploaded.objects(id=file_uploaded_id).first()  # type: ignore
    if not file_uploaded:
        raise HTTPException(status_code=400, detail="File uploaded record not found")
    file_uploaded.delete()
    return True
