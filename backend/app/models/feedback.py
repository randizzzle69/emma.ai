"""Feedback database model."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.db.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1=thumbs down, 2=thumbs up
    comment = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
