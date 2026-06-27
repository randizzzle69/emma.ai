"""Question schemas for API request/response."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    """Schema for creating a new HR question."""
    category: str = Field(..., pattern="^(benefits|leave|payroll|policy|compliance|other)$",
                          description="Question category")
    priority: str = Field(..., pattern="^(low|medium|high|urgent)$",
                          description="Question priority")
    question_text: str = Field(..., min_length=10, max_length=4000,
                               description="The employee's question or concern")
    employee_name: str = Field(..., min_length=2, max_length=200,
                               description="Name of the person asking")
    store_id: Optional[str] = Field(None, max_length=50,
                                    description="Store/location identifier (for multi-store)")


class QuestionResponse(BaseModel):
    """Schema for returned question data."""
    id: int
    category: str
    priority: str
    status: str
    question_text: str
    response_text: Optional[str] = None
    triage_action: Optional[str] = None
    matched_keywords: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    employee_name: str
    store_id: Optional[str] = None

    model_config = {"from_attributes": True}


class QuestionListFilter(BaseModel):
    """Query params for listing/filtering questions."""
    category: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    store_id: Optional[str] = None
