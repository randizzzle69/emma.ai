"""Audit log database model."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, server_default=func.now())
    actor_type = Column(String(20), nullable=False)  # employee/manager/hr_admin/system
    action = Column(String(50), nullable=False)  # question_submitted/response_generated/etc
    entity_type = Column(String(30), nullable=True)  # question/feedback/knowledge_base_entry
    entity_id = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON blob with additional context
