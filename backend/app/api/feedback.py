"""Feedback API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.audit_log import create_audit_entry

router = APIRouter()


@router.post("", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback on an Emma AI response."""
    from app.models.feedback import Feedback
    from sqlalchemy import select

    # Validate the linked question exists
    from app.models.question import Question
    result = await db.execute(select(Question).where(Question.id == feedback.question_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    rating_label = "thumbs_up" if feedback.rating == 2 else "thumbs_down"
    fb = Feedback(
        question_id=feedback.question_id,
        rating=feedback.rating,
        comment=feedback.comment or "",
    )
    db.add(fb)
    await db.commit()
    await db.refresh(fb)

    # Audit trail
    await create_audit_entry(
        db,
        actor_type="employee",
        action="feedback_given",
        entity_type="feedback",
        entity_id=fb.id,
        metadata={"rating": feedback.rating, "rating_label": rating_label, "comment": feedback.comment},
    )

    return FeedbackResponse(
        id=fb.id,
        question_id=fb.question_id,
        rating=fb.rating,
        comment=fb.comment,
        created_at=fb.created_at,
    )
