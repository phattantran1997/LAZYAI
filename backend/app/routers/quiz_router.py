from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import evaluate_quiz

router = APIRouter()

# Create a model for incoming quiz answers
class QuizSubmission(BaseModel):
    answers: dict

@router.post("/submit-quiz")
async def submit_quiz(submission: QuizSubmission):
    try:
        feedback, final_answer = evaluate_quiz(submission.answers)
        return {"feedback": feedback, "final_answer": final_answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
