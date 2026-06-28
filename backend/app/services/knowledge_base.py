"""Mock HR knowledge base — serves as Emma's internal policy reference.

MOCK_KB contains legacy demo data and is NOT used as a fallback for real answers.
Real answers come from ingested policy documents (knowledge_documents/knowledge_chunks).
"""

import re
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
    import sqlite3 as _sqlite3
    from app.services.document_ingestion import DB_PATH_DEFAULT
    try:
        conn = _sqlite3.connect(DB_PATH_DEFAULT)
        count = conn.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False


def _match_word(keyword: str, text: str) -> bool:
    """Check if keyword appears as a whole word in text (case-insensitive)."""
    return bool(re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))


_STOPWORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "out", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "because",
    "but", "and", "or", "if", "while", "that", "this", "these",
    "those", "it", "its", "what", "which", "who", "whom",
    "about", "up", "any", "am",
    # common nouns that appear everywhere in policy docs — not useful as search terms
    "company", "policy", "employee", "employees", "work", "workplace",
    "schedule", "lunch",
})

# Generic words that appear in almost every policy doc's chunk text.
# Even if they match the question, they don't make a chunk relevant.
# E.g. "personal" appears in credit card policy as "personal expense"
# but is meaningless for a question about installing software on an iPhone.
_GENERIC_MATCH_WORDS = frozenset({
    "company", "policy",
    "personal", "corporate",
    "requirement", "required",
    "responsible",
    "ensure",
})

# Multi-word domain terms that should match as phrases and earn high chunk scores.
# These are the HR-specific terms customers actually search for — they beat generic words.
# Plural-to-singular normalization for common HR search terms.
# Applied during tokenization so "gifts" → "gift", "vendors" → "vendor", etc.
_PLURAL_NORMALIZATION: dict[str, str] = {
    "gifts": "gift",
    "accepting": "accept",
    "accepted": "accept",
    "vendors": "vendor",
    "expenses": "expense",
    "days": "day",
    "schedules": "schedule",
}

_DOMAIN_PHRASES: list[tuple[str, float, frozenset[str]]] = [
    # (phrase_text, base_score, set_of_query_terms_required_to_activate_this_phrase)
    # Multi-word domain phrases — only boost when query signals this domain
    ("paid time off", 4.5, frozenset({"pto", "time off", "vacation", "day"})),
    ("time off", 3.0, frozenset({"time off", "pto", "day"})),
    ("sick leave", 3.5, frozenset({"sick", "leave"})),
    ("annual leave", 3.5, frozenset({"sick", "leave", "annual"})),
    ("gift and hospitality", 4.0, frozenset({"gift", "hospitality", "vendor"})),
    ("gift & hospitality", 4.0, frozenset({"gift", "hospitality", "vendor"})),
    ("credit card", 3.5, frozenset({"credit", "card", "expense", "travel"})),
    # Single-word HR-specific domain terms — only boost when query signals this domain
    ("pto", 3.0, frozenset({"pto", "vacation", "day", "time off"})),
    ("vacation", 2.5, frozenset({"pto", "vacation", "day", "time off"})),
    ("gift", 2.5, frozenset({"gift", "hospitality", "vendor"})),
    ("hospitality", 2.5, frozenset({"gift", "hospitality", "vendor"})),
    ("laptop", 2.5, frozenset({"laptop", "device", "personal use", "equipment"})),
    ("computer", 1.5, frozenset({"laptop", "computer", "device", "equipment"})),
]


# ── Intent inference and relevance gating ──────────────────────────────


class _Intent:
    DEVICE_SOFTWARE = "device_software"
    GIFT_HOSPITALITY = "gift_hospitality"
    CORPORATE_CARD = "corporate_card_expense"
    PTO_LEAVE = "pto_leave"
    UNKNOWN = "unknown"


# Intent → query terms that trigger it (normalized lowercase)
_INTENT_TRIGGERS: dict[str, frozenset[str]] = {
    _Intent.DEVICE_SOFTWARE: frozenset({
        "laptop", "phone", "iphone", "mobile", "device", "software",
        "install", "pc", "tablet", "personal use", "company device",
        "corporate device",
    }),
    _Intent.GIFT_HOSPITALITY: frozenset({
        "gift", "gifts", "vendor", "vendors", "hospitality", "accept",
        "accepted", "approval", "disclosure",
    }),
    _Intent.CORPORATE_CARD: frozenset({
        "credit card", "corporate card", "expense", "travel", "receipt",
        "reimbursement", "authorized use", "tpg credit card",
    }),
    _Intent.PTO_LEAVE: frozenset({
        "pto", "paid time off", "sick leave", "annual leave", "vacation",
        "time off", "days off", "accrual", "sick days",
    }),
}

# Intent → allowed document title / category signals
_INTENT_ALLOWED_SOURCES: dict[str, list[str]] = {
    _Intent.DEVICE_SOFTWARE: [
        "employee laptop user policy",
    ],
    _Intent.GIFT_HOSPITALITY: [
        "gift & hospitality policy",
        "gift and hospitality policy",
    ],
    _Intent.CORPORATE_CARD: [
        "tpg corporate credit card policy",
        "tpg credit card expense & procurement policy",
        "corporate credit card",
    ],
    _Intent.PTO_LEAVE: [
        "texas petroleum group",  # TPG Employee Handbook covers PTO
        "pg employee handbook",
        "sick leave policy",
        "pto policy",
    ],
}

# Intent → meaningful chunk content terms (not just doc title)
_INTENT_CHUNK_TERMS: dict[str, frozenset[str]] = {
    _Intent.DEVICE_SOFTWARE: frozenset({
        "laptop", "phone", "iphone", "mobile", "device", "software",
        "install", "pc", "tablet", "equipment", "personal use",
        "company property", "corporate property", "issued", "provided",
    }),
    _Intent.GIFT_HOSPITALITY: frozenset({
        "gift", "gifts", "vendor", "vendors", "hospitality", "accept",
        "disclose", "approval", "bribe", "kickback", "per diem",
        "entertainment", "meals", "lodging",
    }),
    _Intent.CORPORATE_CARD: frozenset({
        "credit card", "corporate card", "ccc", "expense", "travel",
        "receipt", "reimbursement", "cardholder", "procurement",
    }),
    _Intent.PTO_LEAVE: frozenset({
        "pto", "paid time off", "sick leave", "annual leave", "vacation",
        "time away from work", "days of pto", "accrue", "accrual",
        "leave entitlement", "bereavement leave", "jury duty",
    }),
}


def _infer_intent(query: str) -> str:
    """Infer the intent of a user's question from query keywords.

    Returns one of the _Intent constants. Falls back to UNKNOWN if no
    domain-specific terms are detected.
    """
    tokens = _tokenize(query)
    # Also check for multi-word phrases in the original query
    query_lower = query.lower()

    best_intent: str | None = None
    best_score = 0

    for intent, triggers in _INTENT_TRIGGERS.items():
        score = 0
        for trigger in triggers:
            if len(trigger) > 3:  # multi-word term check via substring
                if trigger in query_lower:
                    score += 3.0
            else:  # single-word check via keyword matching
                for t in tokens:
                    if t == trigger or _PLURAL_NORMALIZATION.get(t, t) == trigger:
                        score += 1.0
                        break

        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent or _Intent.UNKNOWN


def _is_chunk_relevant_to_intent(
    doc_title_lower: str,
    chunk_content_lower: str,
    intent: str,
) -> bool:
    """Check if a retrieved chunk is relevant to the inferred intent.

    Both document-level AND content-level checks must pass.
    Returns True only if the chunk is clearly relevant.
    """
    allowed_sources = _INTENT_ALLOWED_SOURCES.get(intent, [])
    chunk_terms = _INTENT_CHUNK_TERMS.get(intent, frozenset())

    # For unknown intent: require very strong match (multiple domain terms in content)
    if intent == _Intent.UNKNOWN:
        matches = 0
        for term in chunk_terms:
            if term in chunk_content_lower:
                matches += 1
        return matches >= 3

    # Check document-level relevance: doc title must be in allowed sources
    doc_matches_any = False
    for allowed in allowed_sources:
        if allowed in doc_title_lower:
            doc_matches_any = True
            break

    if not doc_matches_any:
        # Document doesn't match intent — this chunk is irrelevant
        return False

    # Check content-level relevance: must have at least one intent-specific term
    if not chunk_terms.intersection(set(chunk_content_lower.split())):
        # Try substring matching for multi-word terms
        has_term = False
        for term in chunk_terms:
            if len(term) > 3 and term in chunk_content_lower:
                has_term = True
                break
            elif _match_word(term, chunk_content_lower):
                has_term = True
                break
        if not has_term:
            return False

    return True




def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation via regex word-boundary extraction,
    remove stopwords, and normalize common plural/verb variants."""
    import string
    text = text.lower()
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(translator)
    tokens = [w for w in text.split() if len(w) > 1 and w not in _STOPWORDS]
    normalized = []
    for t in tokens:
        base = _PLURAL_NORMALIZATION.get(t, t)
        normalized.append(base)
    return list(dict.fromkeys(normalized))


def _score_chunks(rows, keywords) -> list[dict]:
    """Score all fetched rows against keywords using word-boundary matching.

    Scoring strategy:
      Pass 1 — Identify the most relevant document(s) by matching keywords
               against document metadata (title, category, source_file).
      Pass 2 — Score each chunk normally, then apply a +5.0 bonus for chunks
               from any pass-1 winning document.

    This ensures a query like 'gift' correctly hits the Gift policy by its title,
    not by accumulated domain-term noise across competing docs' chunks.

    Minimum threshold = 3.5 to prevent generic single-word matches alone.
    """
    doc_scores: dict[str, float] = {}
    for row in rows:
        doc_id = row[0]
        title = (row[1] or "").lower()
        cat_ = (row[2] or "").lower()
        source_file = (row[4] or "").lower()
        if doc_id not in doc_scores:
            m_score = 0.0
            for kw in keywords:
                if _match_word(kw, row[1] or ""):
                    m_score += 4.0
                elif _match_word(kw, row[2] or ""):
                    m_score += 3.0
                elif _match_word(kw, row[4] or ""):
                    m_score += 3.0
            doc_scores[doc_id] = m_score

    best_meta = max(doc_scores.values()) if doc_scores else 0.0
    winning_docs: set[str] = set(
        did for did, sc in doc_scores.items() if sc >= best_meta * 0.8 and sc > 0
    )

    scored_chunks: list[tuple[float, dict]] = []
    for row in rows:
        doc_id = row[0]
        title = row[1] or ""
        cat_ = row[2] or ""
        eff_date = row[3] or "N/A"
        source_file = row[4] or ""
        chunk_idx = row[5]
        content = row[6]

        score = 0.0
        for phrase, base_score, required_terms in _DOMAIN_PHRASES:
            if not required_terms.intersection(set(keywords)):
                continue
            if phrase.lower() in (content or "").lower():
                score += base_score

        for kw in keywords:
            if _match_word(kw, content):
                score += 2.0
            elif _match_word(kw, title):
                score += 1.5
            elif _match_word(kw, cat_):
                score += 1.0
            elif _match_word(kw, source_file):
                score += 1.0

        if doc_id in winning_docs:
            score += 5.0

        if score >= 3.5:
            scored_chunks.append((score, {
                "document_id": doc_id,
                "title": title,
                "category": cat_,
                "effective_date": eff_date,
                "source_file": source_file,
                "chunk_index": chunk_idx,
                "content": content,
            }))

    scored_chunks.sort(key=lambda x: (-x[0], x[1]["document_id"]))

    seen = set()
    deduped = []
    for sc in scored_chunks:
        key = (sc[1]["document_id"], sc[1]["chunk_index"])
        if key not in seen:
            seen.add(key)
            deduped.append(sc)

    return [v[1] for v in deduped[:5]]


def search_ingested(db_session, query: str, category: str | None = None) -> list[dict]:
    """Search ingested policy chunks for relevance to the query."""
    import sqlite3
    from app.services.document_ingestion import DB_PATH_DEFAULT

    if not has_ingested_documents(db_session):
        return []

    keywords = _tokenize(query)
    if not keywords:
        keywords = [query[:3]]

    conn = sqlite3.connect(DB_PATH_DEFAULT)
    rows = conn.execute(
        "SELECT doc.document_id, doc.title, doc.category, doc.effective_date, "
        "doc.source_file, kc.chunk_index, kc.content "
        "FROM knowledge_chunks kc "
        "JOIN knowledge_documents doc ON doc.document_id = kc.document_id"
    ).fetchall()
    conn.close()

    return _score_chunks(rows, keywords)


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
                    "document_id": d[0], "title": d[1], "category": d[2],
                    "effective_date": d[3], "version": d[4], "owner": d[5],
                    "authority_level": d[6], "page_count": d[7],
                }
                for d in docs
            ],
        }
    except Exception:
        return {"documents_ingested": 0, "total_chunks": 0, "documents": [], "error": "No ingestion data found"}


def has_ingested_docs() -> bool:
    """Check if any policy documents exist in the DB. No session needed."""
    import sqlite3
    try:
        conn = sqlite3.connect(DB_PATH_DEFAULT)
        cnt = conn.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0]
        conn.close()
        return cnt > 0
    except Exception:
        return False


def search_ingested_by_query(query: str, category: str | None = None) -> list[dict]:
    """Search ingested policy chunks by query. No session needed."""
    if not has_ingested_docs():
        return []

    import sqlite3
    keywords = _tokenize(query)
    if not keywords:
        keywords = [query[:3]]

    conn = sqlite3.connect(DB_PATH_DEFAULT)
    rows = conn.execute(
        "SELECT doc.document_id, doc.title, doc.category, doc.effective_date, "
        "doc.source_file, kc.chunk_index, kc.content "
        "FROM knowledge_chunks kc "
        "JOIN knowledge_documents doc ON doc.document_id = kc.document_id"
    ).fetchall()
    conn.close()

    return _score_chunks(rows, keywords)


def _get_db_conn():
    """Create a plain sqlite3 connection to the database."""
    import sqlite3 as sqlite
    from pathlib import Path
    db_path = str(Path(__file__).resolve().parents[4] / "backend" / "data" / "emma.db")
    return sqlite.connect(db_path)
