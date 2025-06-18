from mongoengine import Document, StringField, EmailField, BooleanField

class User(Document):
    username = StringField(required=True, unique=True)
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(required=True)  # Teacher, User, Manager...
    is_active = BooleanField(default=True)

    meta = {'collection': 'users'}

