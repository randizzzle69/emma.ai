"""Audit log service — records every interaction in the audit trail."""

import json
from datetime import datetime
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


def _serialize(obj):
    """Recursively serialize values for JSON storage (handles enums, etc.)."""
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (list, tuple)):
        return [_serialize(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return obj


async def create_audit_entry(
    db: AsyncSession,
    actor_type: str,
    action: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    """Create a new audit log entry and persist it."""
    entry = AuditLog(
        timestamp=datetime.utcnow(),
        actor_type=actor_type,
        action=action,
        entity_type=entity_type or "system",
        entity_id=entity_id,
        metadata_json=json.dumps(metadata or {}),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_audit_logs(
    db: AsyncSession,
    actor_type: str | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditLog]:
    """Retrieve audit log entries with optional filters."""
    from sqlalchemy import select
    stmt = select(AuditLog).order_by(AuditLog.timestamp.desc())

    if actor_type:
        stmt = stmt.where(AuditLog.actor_type == actor_type)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)

    result = await db.execute(stmt.limit(limit).offset(offset))
    return list(result.scalars().all())
