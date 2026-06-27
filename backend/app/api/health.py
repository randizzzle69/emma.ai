"""Health check router."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["system"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "emma-ai-backend", "version": "0.1.0"}
