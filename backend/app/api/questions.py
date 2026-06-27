"""Question API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionListFilter
from app.services import question_service
from app.services.audit_log import create_audit_entry

router = APIRouter()


@router.post("", response_model=QuestionResponse, status_code=201)
async def create_question(
    question: QuestionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Submit a new HR question to Emma."""
    result = await question_service.submit_question(db, question)

    # Audit the submission
    await create_audit_entry(
        db,
        actor_type="employee",
        action="question_submitted",
        entity_type="question",
        entity_id=result["id"],
        metadata={"category": result["category"], "priority": result["priority"]},
    )

    return result


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single question and its response."""
    result = await question_service.get_question(db, question_id)
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result


@router.get("", response_model=list[QuestionResponse])
async def list_questions(
    category: str | None = Query(None),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List questions with optional filters."""
    return await question_service.list_questions(db, category, status, priority, limit, offset)
