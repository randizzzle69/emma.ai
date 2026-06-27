"""Emma.ai — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import engine, Base, register_models
from app.api import health, questions, feedback, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown hooks."""
    # Import all models to register their metadata with Base
    register_models()
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: (placeholder for cleanup tasks)


app = FastAPI(
    title="Emma.ai — HR Generalist Digital Worker",
    description="Backend API for Emma.ai HR service workflows.",
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(health.router, prefix="/api")
app.include_router(questions.router, prefix="/api/questions")
app.include_router(feedback.router, prefix="/api/feedback")
app.include_router(admin.router, prefix="/api/admin")


@app.get("/api/health", tags=["system"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "emma-ai-backend", "version": "0.1.0"}
