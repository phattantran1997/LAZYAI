from fastapi import APIRouter, HTTPException
from app.services.hint_service import generate_hint
from app.services.ai_service import generate_hint_and_quiz

router = APIRouter()

@router.post("/ask")
async def ask_question(question: str):
    try:
        # Generate a hint using the new hint service
        hint = generate_hint(question)
        # Generate suggested approach and quiz using existing logic
        _, suggested_approach, quiz = generate_hint_and_quiz(question)
        return {"hint": hint, "suggested_approach": suggested_approach, "quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 