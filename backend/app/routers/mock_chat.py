from fastapi import APIRouter
from pydantic import BaseModel
from app.services.mock_chat_service import post_questions_service

router = APIRouter(prefix='/chat', tags=['chat'])

# Define the Pydantic model to validate incoming data
class MessageRequest(BaseModel):
    message: str
    unit_name: str

@router.post('/ask')
def post_questions(request: MessageRequest):
    data = post_questions_service(request)
    return {"text": data}
