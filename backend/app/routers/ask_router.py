from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.hint_service import generate_hint
from app.services.ai_service import generate_hint_and_quiz

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        # Strip whitespace and validate the question
        question_text = request.question.strip()
        if not question_text:
            raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
        # Generate hint and quiz
        hint = generate_hint(question_text)
        _, suggested_approach, quiz = generate_hint_and_quiz(question_text)
        
        return {"hint": hint, "suggested_approach": suggested_approach, "quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))