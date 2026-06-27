"""Feedback schemas for API request/response."""

from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    """Schema for submitting feedback on an Emma response."""
    question_id: int = Field(..., gt=0, description="ID of the question being rated")
    rating: int = Field(..., ge=1, le=2,
                        description="Rating: 1 = thumbs down, 2 = thumbs up")
    comment: str = Field("", max_length=500,
                         description="Optional comment explaining the rating")


class FeedbackResponse(BaseModel):
    """Schema for returned feedback data."""
    id: int
    question_id: int
    rating: int
    comment: str
    created_at: datetime

    model_config = {"from_attributes": True}
