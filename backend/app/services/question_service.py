"""Question service — handles all question lifecycle logic."""

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question
from app.schemas.question import QuestionCreate
from app.services.triage import classify_question, TriageAction
from app.services.knowledge_base import search_kb
from app.services.audit_log import create_audit_entry


async def submit_question(
    db: AsyncSession,
    question_in: QuestionCreate,
) -> dict:
    """Submit a new HR question and run it through triage."""

    # 1. Create the question record
    question = Question(
        employee_name=question_in.employee_name,
        store_id=question_in.store_id,
        category=question_in.category,
        priority=question_in.priority,
        question_text=question_in.question_text,
        status="pending",
    )
    db.add(question)
    await db.flush()  # Get the ID

    # 2. Triage: classify and generate mock response
    category, action, matched = classify_question(question_in.question_text)

    question.triage_action = _enum_str(action)
    question.triage_keywords = json.dumps(matched)
    question.category = _enum_str(category)

    # 3. Generate mock response based on triage result — prefer ingested docs over MOCK_KB
    kb_results = search_kb(question_in.question_text, category=_enum_str(category))
    
    # Check if we have ingested documents (use plain sqlite3 check)
    has_ingested = False
    try:
        import sqlite3 as _sqlite3
        from app.services.document_ingestion import DB_PATH_DEFAULT as _DB_PATH
        _conn = _sqlite3.connect(_DB_PATH)
        _cnt = _conn.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0]
        has_ingested = _cnt > 0
        _conn.close()
    except Exception:
        pass
    
    response_text = _generate_mock_response(
        action, category, kb_results, matched,
        question_in.question_text,
        db, has_ingested,
    )

    if action == TriageAction.ANSWER:
        question.status = "answered"
    elif action == TriageAction.ESCALATE_HR:
        question.status = "escalated"
        question.response_text = (
            f"**Escalated to HR.** Your question about {_enum_str(category)} has been routed to an HR representative. "
            f"You'll receive a response within 1 business day."
        )
    else:
        question.status = "escalated"
        question.response_text = (
            f"**Routed to your store manager:** This issue requires in-person coordination. "
            f"Your store manager has been notified."
        )

    question.response_text = response_text
    question.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(question)

    # 4. Log the audit trail
    await create_audit_entry(
        db,
        actor_type="employee" if "manager" not in question.employee_name.lower() else "manager",
        action="question_submitted",
        entity_type="question",
        entity_id=question.id,
        metadata={"category": _enum_str(category), "triage_action": _enum_str(action), "matched_keywords": matched},
    )

    return _question_to_dict(question)


async def get_question(db: AsyncSession, question_id: int) -> dict | None:
    """Retrieve a single question by ID."""
    result = await db.execute(select(Question).where(Question.id == question_id))
    q = result.scalar_one_or_none()
    if not q:
        return None
    return _question_to_dict(q)


async def list_questions(
    db: AsyncSession,
    category: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """List questions with optional filters."""
    stmt = (
        select(Question)
        .order_by(Question.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if category:
        stmt = stmt.where(Question.category == category)
    if status:
        stmt = stmt.where(Question.status == status)
    if priority:
        stmt = stmt.where(Question.priority == priority)

    result = await db.execute(stmt)
    return [_question_to_dict(q) for q in result.scalars().all()]


def _generate_mock_response(action, category, kb_results, matched_keywords, question_text, db=None, has_ingested=False):
    """Generate a plausible mock response based on triage action and KB lookup.

    If has_ingested is True, only uses ingested policy documents for answers.
    MOCK_KB entries are used only as fallback demo content when no ingested docs exist.
    """
    cat_str = _enum_str(category)

    if action == TriageAction.ESCALATE_HR:
        return (
            f"**Escalated to HR.** Your question about {_enum_str(category)} has been routed to an HR representative. "
            f"Expected response time: 1 business day."
        )

    if action == TriageAction.ESCALATE_MANAGER:
        return (
            f"**Routed to your store manager:** This issue requires in-person coordination. "
            f"Your store manager has been notified."
        )

    # If ingested docs exist, search them FIRST and ONLY them for real answers.
    if has_ingested and db is not None:
        from app.services.knowledge_base import search_ingested
        ingested_results = search_ingested(db, question_text, category=_enum_str(category))
        if ingested_results:
            top = ingested_results[0]
            effective = top.get('effective_date', 'N/A') or 'N/A'
            return (
                f"**Emma's Answer:**\n\n"
                f"{top['content']}\n\n"
                f"*Based on our {_enum_str(category)} policy: '{top['title']}' (effective {effective})*\n"
                f"*Source document: '{top['title']}' — chunk index {top['chunk_index']}*"
            )
        # No ingested match → canonical "I don't know"
        return (
            f"**Emma's Answer:**\n\n"
            f"I don't have enough information from our current policy documents to answer this accurately. "
            f"Please contact HR directly at hr@company.com or call (555) 123-4567."
        )

    # Fallback: no ingested docs — use MOCK_KB for legacy/demo purposes
    if kb_results:
        top = kb_results[0]
        return (
            f"**Emma's Answer:**\n\n"
            f"{top.content}\n\n"
            f"*Based on our {_enum_str(category)} policy: '{top.title}'*\n"
            f"*Keywords matched: {', '.join(kb_results[0].tags[:5])}*"
        )

    if matched_keywords:
        return (
            f"**Emma's Answer:**\n\n"
            f"I understood your question about {matched_keywords[0]} "
            f"({len(matched_keywords)} relevant keyword(s) detected).\n\n"
            f"While I couldn't find a specific policy entry matching your exact phrasing, "
            f"the {_enum_str(category)} team recommends:\n\n"
            f"- Check your employee handbook for section on {_enum_str(category)} policies\n"
            f"- Reach out to HR directly for case-specific details\n\n"
            f"*If you need more help, just ask!*"
        )

    return (
        f"**Emma's Answer:**\n\n"
        f"I found some general information on {_enum_str(category)} that may be helpful:\n\n"
        f"- Review the relevant section of your employee handbook\n"
        f"- Contact HR for personalized guidance\n\n"
        f"*I can help refine my answer — feel free to rephrase your question!*"
    )


def _question_to_dict(q) -> dict:
    """Convert a Question ORM object to a serializable dict."""
    return {
        "id": q.id,
        "employee_name": q.employee_name,
        "store_id": q.store_id,
        "category": q.category,
        "priority": q.priority,
        "question_text": q.question_text,
        "response_text": q.response_text,
        "status": q.status,
        "triage_action": q.triage_action,
        "triage_keywords": json.loads(q.triage_keywords) if q.triage_keywords else [],
        "created_at": q.created_at.isoformat() if q.created_at else None,
        "updated_at": q.updated_at.isoformat() if q.updated_at else None,
    }


def _enum_str(val):
    """Safely convert an enum or plain value to its string representation."""
    if hasattr(val, "value"):
        return val.value
    return str(val)
