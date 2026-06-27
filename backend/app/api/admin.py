"""Admin API endpoints — audit log, knowledge base, and document ingestion."""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.audit import AuditLogEntry, AuditLogFilter
from app.services.audit_log import get_audit_logs
from app.services.knowledge_base import MOCK_KB
from app.services.document_ingestion import ingest_documents_sync
router = APIRouter()


@router.get("/audit-log")
async def get_audit(
    actor_type: str | None = Query(None),
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """View the full audit log."""
    logs = await get_audit_logs(db, actor_type, action, entity_type, limit, offset)

    return {
        "total": len(logs),
        "entries": [
            {
                "id": l.id,
                "timestamp": l.timestamp.isoformat() if l.timestamp else None,
                "actor_type": l.actor_type,
                "action": l.action,
                "entity_type": l.entity_type,
                "entity_id": l.entity_id,
                "metadata": json.loads(l.metadata_json or "{}"),
            }
            for l in logs
        ],
    }


@router.get("/knowledge-base")
async def get_knowledge_base():
    """View all knowledge base entries (mock data)."""
    return [
        {
            "id": entry.id,
            "category": entry.category,
            "title": entry.title,
            "content": entry.content,
            "tags": entry.tags,
        }
        for entry in MOCK_KB
    ]


@router.post("/knowledge-base")
async def add_knowledge_base_entry(
    body: dict,
):
    """Admin-only: add a new KB entry (mock — no persistent store yet)."""
    return {"status": "pending", "message": "KB write-back coming in Phase 2. Entry logged for review."}


@router.post("/ingest")
async def ingest_documents_endpoint():
    """Ingest policy documents listed in the manifest CSV.

    Reads data/policies/manifest/policy_manifest.csv, extracts text from each PDF
    via pdfplumber, chunks content, and stores metadata + chunks in SQLite.
    Idempotent — re-runs clear existing ingested data before inserting.
    """
    try:
        report = ingest_documents_sync()
        return {
            "status": "ok",
            "documents_found": report.documents_found,
            "documents_ingested": report.documents_ingested,
            "chunks_created": report.chunks_created,
            "errors": report.errors,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")


@router.get("/ingest-status")
async def ingest_status_endpoint(db: AsyncSession = Depends(get_db)):
    """Show current ingestion status and document metadata."""
    from app.services.knowledge_base import get_ingestion_status
    status = get_ingestion_status(db)
    return {
        "documents_ingested": status.get("documents_ingested", 0),
        "total_chunks": status.get("total_chunks", 0),
        "documents": status.get("documents", []),
    }


@router.get("/feedback")
async def get_feedback_endpoint(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Return recent feedback entries with linked question context.

    Each entry includes:
      - feedback id
      - question id + text + response summary
      - rating (1=thumbs down, 2=thumbs up)
      - comment
      - source references if available
      - created timestamp
    """
    from sqlalchemy import select as _select
    from app.models.feedback import Feedback
    from app.models.question import Question

    stmt = (
        _select(Feedback, Question)
        .outerjoin(Question, Feedback.question_id == Question.id)
        .order_by(Feedback.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    rows = result.all()

    entries = []
    for fb, q in rows:
        source_refs = ""
        if q and q.triage_keywords:
            try:
                kws = json.loads(q.triage_keywords)
                source_refs = f"Keywords: {', '.join(kws)}. " if kws else ""
            except (json.JSONDecodeError, TypeError):
                pass
        entries.append({
            "id": fb.id,
            "question_id": q.id if q else fb.question_id,
            "question_text": q.question_text if q else "",
            "answer_text": q.response_text[:300] if q and q.response_text else "",
            "rating": fb.rating,
            "rating_label": "thumbs_up" if fb.rating == 2 else "thumbs_down",
            "comment": fb.comment or "",
            "source_references": source_refs,
            "created_at": fb.created_at.isoformat() if fb.created_at else None,
        })

    return {"total": len(rows), "entries": entries}
