"""Mock HR knowledge base — serves as Emma's internal policy reference.

MOCK_KB contains legacy demo data and is NOT used as a fallback for real answers.
Real answers come from ingested policy documents (knowledge_documents/knowledge_chunks).
"""

from dataclasses import dataclass, field


@dataclass
class KBEntry:
    """Single knowledge base entry (HR policy/procedure)."""
    id: int
    category: str          # benefits / leave / payroll / policy / compliance / other
    title: str
    content: str
    tags: list[str] = field(default_factory=list)

    def matches(self, query: str) -> bool:
        """Simple relevance check for MVP (case-insensitive tag/keyword matching)."""
        combined = f"{self.title} {' '.join(self.tags)}".lower()
        return any(word in combined for word in query.lower().split())


# ── Mock KB content — legacy demo data only. NOT used as answer fallback. ─────────────

MOCK_KB: list[KBEntry] = [
    KBEntry(
        id=1, category="leave", title="PTO Policy",
        content=(
            "Full-time employees accrue PTO at 4 hours per pay period (biweekly). "
            "New hires receive a prorated amount based on their start date. "
            "Unused PTO carries over up to 80 hours. "
            "PTO requests should be submitted at least 2 weeks in advance for planned time off."
        ),
        tags=["pto", "time off", "vacation", "accrual"],
    ),
    KBEntry(
        id=2, category="leave", title="Sick Leave Policy",
        content=(
            "All employees receive 40 hours of sick leave per year. "
            "Sick leave can be used for personal illness, medical appointments, "
            "or caring for a family member with a health condition. "
            "No advance notice required for unexpected illness — call the store manager first."
        ),
        tags=["sick", "illness", "medical", "family"],
    ),
    KBEntry(
        id=3, category="payroll", title="Pay Schedule",
        content=(
            "Employees are paid biweekly every other Friday. "
            "Direct deposit is the standard pay method. "
            "Paper checks can be requested through the HR portal and take 5 business days to process. "
            "Overtime must be pre-approved by your store manager."
        ),
        tags=["pay", "salary", "direct deposit", "overtime"],
    ),
    KBEntry(
        id=4, category="benefits", title="Health Insurance Enrollment",
        content=(
            "Eligible employees can enroll in medical, dental, and vision plans. "
            "Open enrollment occurs annually in November. "
            "New hires have 30 days from their start date to enroll. "
            "Company covers 60% of individual medical premiums; dependents are additional."
        ),
        tags=["insurance", "medical", "dental", "vision", "enrollment"],
    ),
    KBEntry(
        id=5, category="policy", title="Dress Code — Store Staff",
        content=(
            "Store staff must wear company-branded uniforms: black pants, branded polo shirt, "
            "non-slip shoes. No open-toed shoes or sandals. "
            "Name badges must be worn at all times on the sales floor. "
            "Hats are allowed if they are company-branded."
        ),
        tags=["dress code", "uniform", "branded", "badge"],
    ),
    KBEntry(
        id=6, category="compliance", title="Workplace Harassment Policy",
        content=(
            "Emma.ai's parent company maintains a zero-tolerance harassment policy. "
            "Any form of harassment based on race, gender, religion, age, disability, or "
            "sexual orientation is prohibited. Employees who experience or witness harassment "
            "should report to their store manager, an HR representative, or use the anonymous hotline."
        ),
        tags=["harassment", "compliance", "zero tolerance", "reporting"],
    ),
    KBEntry(
        id=7, category="payroll", title="Wage and Hour — Non-Exempt Staff",
        content=(
            "Non-exempt employees are paid hourly with overtime at 1.5x after 40 hours per week. "
            "Employees must clock in/out for every shift. Meal breaks of 30 minutes are unpaid "
            "and required after 5 consecutive hours on duty. Rest breaks of 10 minutes are paid "
            "and provided for every 4 hours worked."
        ),
        tags=["wage", "hourly", "overtime", "break", "clock"],
    ),
    KBEntry(
        id=8, category="other", title="Employee Discount Program",
        content=(
            "All active employees receive a 15% discount on eligible in-store purchases. "
            "Discount applies Monday through Thursday only. Not valid on alcohol, cigarettes, "
            "gift cards, or promotional items. Cannot be combined with other offers."
        ),
        tags=["discount", "perk", "purchase", "employee benefit"],
    ),
]


def search_kb(query: str, category: str | None = None) -> list[KBEntry]:
    """Search the mock knowledge base (legacy/demo only). Returns top 5 most relevant entries."""
    results = [entry for entry in MOCK_KB if entry.matches(query)]
    if category:
        results = [r for r in results if r.category == category]
    return results[:5]


# ── Ingested-doc aware query helpers ───────────────────────────────────────────────────


def has_ingested_documents(db_session) -> bool:
    """Check whether any policy documents have been ingested into the DB."""
    # Use plain sqlite3 check instead of SQLAlchemy (avoids async session issues)
    import sqlite3 as _sqlite3
    from app.services.document_ingestion import DB_PATH_DEFAULT
    try:
        conn = _sqlite3.connect(DB_PATH_DEFAULT)
        count = conn.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False


def search_ingested(db_session, query: str, category: str | None = None) -> list[dict]:
    """Search ingested policy chunks for relevance to the query.

    Searches ALL ingested chunks regardless of triage category.
    Ranks results by keyword count (how many keywords appear in chunk).
    Only uses ingested docs — MOCK_KB is NOT used here.
    """
    import sqlite3
    from app.services.document_ingestion import DB_PATH_DEFAULT

    if not has_ingested_documents(db_session):
        return []

    keywords = [w for w in query.lower().split() if len(w) > 2]
    if not keywords:
        keywords = [query[:3]]

    # Simple: get all chunks that match ANY keyword, with the matched content
    like_clauses = " OR ".join(["LOWER(kc.content) LIKE ?" for kw in keywords])
    params = ["%" + kw + "%" for kw in keywords]

    query_sql = (
        "SELECT doc.document_id, doc.title, doc.category, doc.effective_date, "
        "kc.chunk_index, kc.content FROM knowledge_chunks kc "
        "JOIN knowledge_documents doc ON doc.document_id = kc.document_id "
        f"WHERE ({like_clauses}) ORDER BY kc.chunk_index"
    )

    conn = sqlite3.connect(DB_PATH_DEFAULT)
    result = conn.execute(query_sql, params).fetchall()
    conn.close()

    # Score each doc by keyword match count, pick best chunk per doc
    docs_scored: dict[str, tuple[float, dict]] = {}
    for row in result:
        doc_id = row[0]
        title = row[1]
        cat_ = row[2]
        eff_date = row[3]
        chunk_idx = row[4]
        content = row[5]

        # Count how many keywords match this chunk
        score = sum(1 for kw in keywords if kw in content.lower())

        if doc_id not in docs_scored or score > docs_scored[doc_id][0]:
            docs_scored[doc_id] = (score, {
                "document_id": doc_id,
                "title": title,
                "category": cat_,
                "effective_date": eff_date,
                "chunk_index": chunk_idx,
                "content": content,
            })

    # Rank by score descending, then alphabetically for stability
    ranked = sorted(docs_scored.items(), key=lambda x: (-x[1][0], x[0]))
    return [v[1] for v in ranked[:5]]


def get_ingestion_status(db_session) -> dict:
    """Return ingestion status for the admin UI."""
    import sqlite3
    from app.services.document_ingestion import DB_PATH_DEFAULT
    try:
        conn = sqlite3.connect(DB_PATH_DEFAULT)
        docs = conn.execute(
            "SELECT document_id, title, category, effective_date, version, owner, authority_level, page_count FROM knowledge_documents ORDER BY id"
        ).fetchall()
        rows_total = conn.execute("SELECT COUNT(*) FROM knowledge_chunks").fetchone()[0]
        chunks_total = rows_total if rows_total else 0
        conn.close()
        return {
            "documents_ingested": len(docs),
            "total_chunks": chunks_total,
            "documents": [
                {
                    "document_id": d[0],
                    "title": d[1],
                    "category": d[2],
                    "effective_date": d[3],
                    "version": d[4],
                    "owner": d[5],
                    "authority_level": d[6],
                    "page_count": d[7],
                }
                for d in docs
            ],
        }
    except Exception:
        return {"documents_ingested": 0, "total_chunks": 0, "documents": [], "error": "No ingestion data found"}


# ── Direct helper for question_service (no session dependency) ────────────────

from app.services.document_ingestion import DB_PATH_DEFAULT as _KB_DB_PATH


def has_ingested_docs() -> bool:
    """Check if any policy documents exist in the DB. No session needed."""
    import sqlite3
    try:
        conn = sqlite3.connect(_KB_DB_PATH)
        cnt = conn.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0]
        conn.close()
        return cnt > 0
    except Exception:
        return False


def search_ingested_by_query(query: str, category: str | None = None) -> list[dict]:
    """Search ingested policy chunks by query. No session needed.

    Searches ALL ingested chunks regardless of triage category.
    Ranks results by keyword relevance (more matches = higher rank).
    Returns up to 5 docs with best-match chunk.
    """
    if not has_ingested_docs():
        return []

    import sqlite3
    keywords = [w for w in query.lower().split() if len(w) > 2]
    if not keywords:
        keywords = [query[:3]]

    # Get all matching chunks with a relevance score
    # Score = count of how many keywords appear in the chunk
    like_parts = []
    params: list[str] = []
    for i, kw in enumerate(keywords):
        like_parts.append(f"CASE WHEN LOWER(kc.content) LIKE ? THEN 1 ELSE 0 END AS score{i}")
        params.append("%" + kw + "%")

    query_sql = (
        "SELECT doc.document_id, doc.title, doc.category, doc.effective_date, "
        f'{", ".join(like_parts)}, kc.chunk_index, kc.content FROM knowledge_chunks kc '
        "JOIN knowledge_documents doc ON doc.document_id = kc.document_id "
        "WHERE (" + " OR ".join([f"LOWER(kc.content) LIKE ?" for kw in keywords]) + ")"
    )

    # Add category filter from triage ONLY as a soft hint, not hard filter
    if category:
        query_sql += f" AND doc.category LIKE '%{category}%'"

    query_sql += " ORDER BY kc.chunk_index"

    try:
        conn = sqlite3.connect(_KB_DB_PATH)
        result = conn.execute(query_sql, params).fetchall()
        conn.close()
    except Exception:
        return []

    # Score and rank by document: sum of keyword matches
    docs_scored: dict[str, tuple[float, dict]] = {}
    for row in result:
        doc_id = row[0]
        title = row[1]
        cat_ = row[2]
        eff_date = row[3]
        # scores are columns 4 to 4+len(keywords)-1
        score = sum(row[i] for i in range(4, 4 + len(keywords)))
        content = row[-1]
        chunk_idx = row[-2]

        if doc_id not in docs_scored or score > docs_scored[doc_id][0]:
            docs_scored[doc_id] = (score, {
                "document_id": doc_id,
                "title": title,
                "category": cat_,
                "effective_date": eff_date,
                "chunk_index": chunk_idx,
                "content": content,
            })

    # Return docs sorted by relevance score descending, then alphabetically by doc_id for stability
    ranked = sorted(docs_scored.items(), key=lambda x: (-x[1][0], x[0]))
    return [v[1] for v in ranked[:5]]


def _get_db_conn():
    """Create a plain sqlite3 connection to the database."""
    import sqlite3 as sqlite
    from pathlib import Path
    db_path = str(Path(__file__).resolve().parents[4] / "backend" / "data" / "emma.db")
    return sqlite.connect(db_path)
