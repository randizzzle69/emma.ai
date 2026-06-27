"""Policy document ingestion — reads manifest CSV, extracts PDF text, stores in SQLite."""

import csv
import os
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

BASE_DIR = Path(__file__).resolve().parents[3]  # ~/projects/Emma.ai
MANIFEST_PATH = BASE_DIR / "data" / "policies" / "manifest" / "policy_manifest.csv"
RAW_DIR = BASE_DIR / "data" / "policies" / "raw"
DB_PATH_DEFAULT = str(BASE_DIR / "backend" / "data" / "emma.db")


@dataclass
class IngestionReport:
    documents_found: int = 0
    documents_ingested: int = 0
    chunks_created: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "documents_found": self.documents_found,
            "documents_ingested": self.documents_ingested,
            "chunks_created": self.chunks_created,
            "errors": self.errors,
        }


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[tuple[int, str]]:
    """Split text into overlapping chunks of ~chunk_size chars.

    Returns list of (chunk_index, chunk_text)."""
    if not text or not text.strip():
        return []

    chunks: list[tuple[int, str]] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append((len(chunks), chunk))
        if end >= len(text):
            break
        start = end - overlap

    return chunks


def _read_manifest() -> list[dict] | None:
    """Read policy manifest CSV. Returns list of row dicts or None on error."""
    if not MANIFEST_PATH.exists():
        print(f"[ingest] Manifest not found: {MANIFEST_PATH}")
        return None
    try:
        with open(MANIFEST_PATH, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        print(f"[ingest] Error reading manifest: {e}")
        return None


def _extract_pdf_text(pdf_path: Path) -> tuple[str, int, list[str]]:
    """Extract text from a PDF using pdfplumber.

    Returns (full_text, page_count, errors)."""
    errors: list[str] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            parts: list[str] = []
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    parts.append(f"[Page {i + 1}]\n{text}")
            full_text = "\n\n".join(parts)
            return full_text, page_count, errors
    except Exception as e:
        errors.append(f"Error extracting {pdf_path.name}: {e}")
        return "", 0, errors


# ── Plain-SQL helpers for sqlite3.Connection ───────────────────────────────────

_DOC_INSERT = (
    "INSERT OR REPLACE INTO knowledge_documents "
    "(document_id, source_file, title, category, effective_date, version, owner, authority_level, status, page_count) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)"
)

_CHUNK_INSERT = (
    "INSERT INTO knowledge_chunks (document_id, chunk_index, content) VALUES (?, ?, ?)"
)


def _ingest_into_conn(conn, rows: list[dict]) -> IngestionReport:
    """Ingest documents using a plain sqlite3.Connection (no SQLAlchemy)."""
    report = IngestionReport()
    report.documents_found = len(rows)

    for row in rows:
        doc_id = row["document_id"]
        title = row["title"]
        source_file = row["source_file"]
        pdf_path = RAW_DIR / source_file

        if not pdf_path.exists():
            report.errors.append(f"PDF not found: {pdf_path}")
            continue

        text_content, page_count, errors = _extract_pdf_text(pdf_path)
        report.errors.extend(errors)

        if not text_content.strip():
            report.errors.append(f"No extractable text in {source_file}")
            continue

        chunks = _chunk_text(text_content)

        conn.execute(_DOC_INSERT, (
            doc_id, source_file, title, row["category"],
            row.get("effective_date") or None,
            row.get("version") or None,
            row.get("owner") or None,
            row.get("authority_level") or None,
            page_count,
        ))

        for idx, chunk_text in chunks:
            conn.execute(_CHUNK_INSERT, (doc_id, idx, chunk_text))

        report.documents_ingested += 1
        report.chunks_created += len(chunks)
        print(f"  ✅ '{title}': {len(chunks)} chunks, {page_count} pages")

    conn.commit()
    print(f"[ingest] done found={report.documents_found} ingested={report.documents_ingested} chunks={report.chunks_created}")
    return report


def ingest_documents_sync() -> IngestionReport:
    """Ingest documents listed in the policy manifest into SQLite.

    Uses plain sqlite3 (no async/session requirements).
    Idempotent — runs full clear+re-insert each time.
    """
    import sqlite3
    conn = sqlite3.connect(DB_PATH_DEFAULT)

    # Clear existing ingested data first
    try:
        conn.execute("DELETE FROM knowledge_chunks")
        conn.execute("DELETE FROM knowledge_documents")
    except Exception:
        pass

    rows = _read_manifest()
    if rows is None:
        report = IngestionReport()
        report.errors.append(f"Manifest not found at {MANIFEST_PATH}")
        conn.close()
        return report

    return _ingest_into_conn(conn, rows)
