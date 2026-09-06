from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_dependencies import get_current_user
from app.models.user import User

from app.services.chatbot_service import chat_with_ai


router = APIRouter(
    prefix="/api/ai",
    tags=["AI Chatbot"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    response = chat_with_ai(
        user_id=current_user.id,
        message=request.message,
        db=db
    )

    return {
        "response": response
    }

