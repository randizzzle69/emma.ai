"""Database configuration and engine setup."""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# SQLite with asyncio support — no external DB process needed
DB_PATH = os.environ.get("EMMA_DB_PATH", "./data/emma.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency for FastAPI to get an async DB session."""
    async with async_session_factory() as session:
        yield session


def register_models():
    """Import all models to ensure their metadata is registered with Base.

    Called once during app startup before create_all().
    Models must NOT import this module at the top level — use local imports instead.
    """
    import app.models.question  # noqa: F401
    import app.models.feedback  # noqa: F401
    import app.models.audit_log  # noqa: F401
    import app.models.knowledge_doc  # noqa: F401
