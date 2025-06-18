from mongoengine import Document, StringField, ListField, DateTimeField

class Unit(Document):   
    unit_name = StringField(required=True)
    unit_description = StringField(required=True)
    total_students: int = 0
    year = StringField(required=True)
    semester = StringField(required=True)