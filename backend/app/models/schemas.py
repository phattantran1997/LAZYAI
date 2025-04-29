from pydantic import BaseModel

class Question(BaseModel):
    question: str

class QuizAnswers(BaseModel):
    answers: dict 