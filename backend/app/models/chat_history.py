from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class ChatHistory(Document):
    username = StringField(required=True)
    question = StringField(required=True)
    answer = StringField(required=True)
    date_created = DateTimeField(default=datetime.now)

    # meta = {
    #     'collection': 'chat_history',
    #     'indexes': [
    #         {'fields': ['user_id'], 'unique': False}
    #     ]
    # }
