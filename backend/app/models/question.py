"""Question database model."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_name = Column(String(200), nullable=False)
    store_id = Column(String(50), nullable=True)
    category = Column(String(50), nullable=False)  # benefits/leave/payroll/policy/compliance/other
    priority = Column(String(20), nullable=False)   # low/medium/high/urgent
    question_text = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending/answered/escalated/resolved
    response_text = Column(Text, nullable=True)
    triage_action = Column(String(30), nullable=True)  # answer/escalate_hr/escalate_manager
    triage_keywords = Column(Text, nullable=True)  # JSON string of matched keywords
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
