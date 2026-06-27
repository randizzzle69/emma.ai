# ARCHITECTURE.md — Emma.ai System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User (Web Browser)                │
│                  ┌─────────────────────┐               │
│                  │   React + Vite SPA  │               │
│                  │   - Question Form   │               │
│                  │   - Response Viewer │               │
│                  │   - Feedback Panel  │               │
│                  │   - Audit Log UI    │               │
│                  └─────────┬───────────┘               │
└────────────────────────────┼───────────────────────────┘
                             │ HTTPS (REST API)
                             ▼
┌─────────────────────────────────────────────────────────┐
│                    Emma.ai Backend                      │
│                   FastAPI Application                   │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Routes   │→ │ Services │→ │ Models   │→ │  DB    │ │
│  │ (API)    │← │ (Agent)  │← │ (SQLAlch.)│← │(SQLite)│ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│        │              │                                   │
│        │              ▼                                   │
│        │      ┌──────────────┐                           │
│        │      │ Knowledge    │                           │
│        │      │ Base Service │                           │
│        │      └──────────────┘                           │
│        │                                              ┌────────────┐   │
│        │      ┌──────────────┐     ┌──────────────┐  │ Audit Log  │   │
│        │      │ Triage /     │→    │ Feedback     │←─│ Service    │   │
│        │      │ Routing      │     │ Service      │  └────────────┘   │
│        │      └──────────────┘     └──────────────┘                    │
│        └───────────────────────────────────────────────────────────────┘
│                                             │
│                              ┌──────────────────────┐                   │
│                              │  Agent Layer         │                   │
│                              │  (Interface + Mock)  │                   │
│                              │  ← → LLM Adapter     │                   │
│                              └──────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

## Data Flow: Question-to-Response

```
1. User submits question (via UI)
   ↓
2. POST /api/questions → FastAPI route validates input
   ↓
3. Store question in SQLite (status: "pending")
   ↓
4. Triage Service classifies question by category
   ├─ HR Policy  → answer from knowledge base
   ├─ Benefits   → answer from knowledge base
   ├─ Leave      → answer + auto-approve if eligible
   ├─ Payroll    → escalate to HR admin
   └─ Compliance → escalate to HR admin
   ↓
5. Response Service generates response
   ├─ Mock: lookup in KB + template fill
   └─ Future: LLM call via adapter interface
   ↓
6. Store response + audit log entry
   ↓
7. GET /api/questions/{id} → return response to UI
   ↓
8. User rates response (thumbs up/down)
   ↓
9. POST /api/feedback → store feedback, link to question
   ↓
10. Analytics: low-rated responses flagged for review
```

## API Endpoints (Phase 1 Plan)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/health` | Health check | None |
| POST | `/api/questions` | Submit HR question | None |
| GET | `/api/questions` | List questions (filterable) | Admin |
| GET | `/api/questions/{id}` | Get question + response | None |
| PATCH | `/api/questions/{id}/escalate` | Escalate to admin | None |
| POST | `/api/feedback` | Submit feedback | None |
| GET | `/api/admin/audit-log` | Full audit trail | Admin |
| GET | `/api/admin/knowledge-base` | View KB entries | Admin |
| POST | `/api/admin/knowledge-base` | Add/edit KB entry | Admin |

## Database Schema (Planned)

### `employees`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| name | TEXT | Employee name |
| email | TEXT | Contact email |
| store_id | TEXT | Store/location identifier |
| role | TEXT | employee / manager / hr_admin |
| created_at | DATETIME | ISO-8601 |

### `questions`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| employee_id | INTEGER FK | Reference to employees |
| category | TEXT | benefits / leave / payroll / policy / compliance / other |
| priority | TEXT | low / medium / high / urgent |
| question_text | TEXT | User's question |
| status | TEXT | pending / answered / escalated / resolved |
| response_text | TEXT | Emma's answer (nullable) |
| triage_rule | TEXT | Which rule matched (for audit) |
| created_at | DATETIME | ISO-8601 |
| updated_at | DATETIME | ISO-8601 |

### `knowledge_base`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| category | TEXT | benefits / leave / payroll / policy / compliance / other |
| title | TEXT | Policy/procedure name |
| content | TEXT | Full policy text (markdown supported) |
| tags | TEXT | Comma-separated search tags |
| effective_date | DATE | When this policy takes effect |
| expiry_date | DATE | When this policy expires (nullable) |
| updated_at | DATETIME | ISO-8601 |

### `feedback`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| question_id | INTEGER FK | Reference to questions |
| rating | INTEGER | 1 (thumbs down) or 2 (thumbs up) |
| comment | TEXT | Optional user comment |
| created_at | DATETIME | ISO-8601 |

### `audit_log`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| timestamp | DATETIME | ISO-8601 (indexed) |
| actor_type | TEXT | employee / manager / hr_admin / system |
| action | TEXT | question_submitted / response_generated / feedback_given / escalation_created / kb_updated |
| entity_type | TEXT | question / feedback / knowledge_base_entry |
| entity_id | INTEGER | Reference to affected record |
| metadata | TEXT | JSON blob with additional context |

### `escalations`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| question_id | INTEGER FK | Reference to questions |
| reason | TEXT | Why it was escalated |
| assigned_to | TEXT | HR admin identifier |
| status | TEXT | open / acknowledged / resolved / closed |
| created_at | DATETIME | ISO-8601 |
| updated_at | DATETIME | ISO-8601 |

---

## Key Interfaces (Phase 2 Prep)

### `ResponseGenerator` Interface
```python
class ResponseGenerator(Protocol):
    async def generate(self, question: Question, context: dict) -> str: ...
```
**Implementations:** `MockResponseGenerator` (Phase 1), `LocalLLMResponseGenerator` (Phase 2)

### `KnowledgeBaseQuery` Interface
```python
class KnowledgeBaseInterface(Protocol):
    async def search(self, query: str, category: str = None) -> list[KBResult]: ...
    async def get_by_id(self, id: int) -> KBEntry | None: ...
```

---

## Future Architecture Notes

### Phase 2 — Real LLM Integration
- Add `LocalLLMResponseGenerator` that wraps a local model (Ollama, llama.cpp)
- Keep mock behind an interface so tests don't change
- Add rate limiting and fallback to mock on failure

### Phase 3 — Integrations
- HRIS connector (REST adapter pattern)
- Email notification service
- Multi-channel input (Slack bot, Teams bot)

### Phase 4 — Intelligence
- Feedback-driven fine-tuning pipeline
- Auto-categorization with ML model
- Proactive HR policy alerts based on employee data

---

_Last updated: 2026-06-26_
