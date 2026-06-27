"""Audit log schemas for API response."""

from datetime import datetime

from pydantic import BaseModel


class AuditLogEntry(BaseModel):
    """Schema for audit log entries."""
    id: int
    timestamp: datetime
    actor_type: str
    action: str
    entity_type: str
    entity_id: int
    metadata: dict

    model_config = {"from_attributes": True}


class AuditLogFilter(BaseModel):
    """Query params for filtering audit log."""
    actor_type: str | None = None
    action: str | None = None
    entity_type: str | None = None
    from_date: str | None = None  # ISO-8601 date string
    to_date: str | None = None
