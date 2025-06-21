from app.models.file_uploaded import FileUploaded 
from app.schemas.file_uploaded import File

# ---------------------------- Create ------------------------>

def create_file_uploaded(file_uploaded_in: File) -> FileUploaded:

    # Create and save the new file uploaded record in the database
    file_uploaded = FileUploaded(
        file_name=file_uploaded_in.file_name,
        file_path=file_uploaded_in.file_path,
        upload_date=file_uploaded_in.upload_date,
        size=file_uploaded_in.size,
        username=file_uploaded_in.username
    )
    file_uploaded.save()  # Save the file uploaded record in the database

    return file_uploaded

# ---------------------------- Read ------------------------>

def get_file_uploaded_by_id(file_uploaded_id: str) -> FileUploaded:
    file_uploaded = FileUploaded.objects(id=file_uploaded_id).first()  # type: ignore
    if not file_uploaded:
        raise ValueError("File uploaded record not found")
    return file_uploaded        

# ---------------------------- Delete ------------------------>

def delete_file_uploaded(file_uploaded_id: str) -> bool:
    file_uploaded = FileUploaded.objects(id=file_uploaded_id).first()  # type: ignore
    if not file_uploaded:
        raise ValueError("File uploaded record not found")
    file_uploaded.delete()
    return True
