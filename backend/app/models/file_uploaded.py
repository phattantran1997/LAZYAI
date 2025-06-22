from mongoengine import Document, StringField, DateTimeField, IntField

class FileUploaded(Document):
    # file_id = StringField(primary_key=True)  # Unique identifier for the file
    file_name = StringField(required=True)
    file_path = StringField(required=True)
    upload_date = DateTimeField(required=True)
    size = IntField(required=True)  # Size in bytes
    username = StringField(required=True)  # Reference to the user who uploaded the file

    meta = {'collection': 'file_uploaded'}


