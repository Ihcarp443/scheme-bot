# api/feedback.py

from fastapi import APIRouter
from pydantic import BaseModel
from db.feedback_repository import save_feedback

router = APIRouter()

class FeedbackRequest(BaseModel):
    thread_id: str
    answer: str
    feedback: str  # like/dislike


@router.post("/")
async def submit_feedback(req: FeedbackRequest):
    print(f"Received feedback: {req}")
    save_feedback(
        thread_id=req.thread_id,
        answer=req.answer,
        feedback=req.feedback
    )

    return {
        "success": True
    }