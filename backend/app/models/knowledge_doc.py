"""Knowledge document and chunk models for ingested policy PDFs."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.database import Base


class KnowledgeDocument(Base):
    """Metadata about an ingested policy document."""

    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(100), unique=True, nullable=False)
    source_file = Column(String(300), nullable=False)       # original PDF filename
    title = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False)
    effective_date = Column(String(30), nullable=True)
    version = Column(String(50), nullable=True)
    owner = Column(String(200), nullable=True)
    authority_level = Column(String(50), nullable=True)     # authoritative / advisory
    status = Column(String(30), default="active")           # active / archived
    page_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class KnowledgeChunk(Base):
    """A searchable text chunk extracted from a policy document."""

    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(100), nullable=False)       # FK to knowledge_documents.document_id
    chunk_index = Column(Integer, nullable=False)           # sequential index within doc
    section_title = Column(String(500), nullable=True)      # heading / context label
    content = Column(Text, nullable=False)                  # the actual text excerpt
    created_at = Column(DateTime, server_default=func.now())
