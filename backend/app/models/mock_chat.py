from mongoengine import Document

class MockChat(Document):
    question: str
    answer: str
