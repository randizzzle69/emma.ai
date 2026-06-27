# BACKLOG.md — Emma.ai Task Backlog

> **Source of truth.** No work without the backlog. Move items as you go. Every completed item gets a `[date]` tag in Done.

---

## Now (In Progress)

| # | Task | Owner | Est. | Notes |
|---|------|-------|------|-------|
| 1.0 | ✅ Project scaffolding + planning docs | Sparky | Done | Completed 2026-06-26 | `5d21cca` |
| 1.1 | ⏳ Backend project setup (FastAPI, dir structure, requirements.txt, Dockerfile) | Sparky | 2h | In progress — starting now |

---

## Next (Ready to Start)

| # | Task | Owner | Est. | Notes |
|---|------|-------|------|-------|
| 1.2 | Design database schema (employees, questions, responses, feedback, audit_log) | TBD | 1h | SQLite migrations via Alembic or raw SQL |
| 1.2 | Design database schema (employees, questions, responses, feedback, audit_log) | TBD | 1h | SQLite migrations via Alembic or raw SQL |
| 1.3 | Implement HR knowledge base service (mock data layer + query API) | TBD | 3h | CRUD for policies, FAQ entries |
| 1.4 | Implement question intake API endpoints | TBD | 2h | POST /api/questions, GET /api/questions/{id} |
| 1.5 | Implement triage/routing logic (classify → answer/escalate) | TBD | 3h | Rule-based routing for MVP |
| 1.6 | Implement feedback capture endpoints | TBD | 1h | POST /api/feedback |
| 1.7 | Implement audit log service | TBD | 2h | Log every interaction with metadata |
| 1.8 | Set up frontend (React + Vite, folder structure) | TBD | 1h | `frontend/` directory |
| 1.9 | Build question submission UI page | TBD | 2h | Form with description, category, priority |
| 1.10 | Build response viewing & feedback UI | TBD | 2h | View answer, thumbs up/down |
| 1.11 | Build admin/audit log viewer | TBD | 2h | Table of all interactions |

---

## Later (Backlog — Not Started)

| # | Task | Owner | Est. | Notes |
|---|------|-------|------|-------|
| 1.12 | LLM integration service interface (mock → real swap) | TBD | - | Interface first, implementation later |
| 1.13 | Integration tests end-to-end flow | TBD | - | Mock → respond → feedback → audit trail |
| 1.14 | Docker compose for full stack | TBD | - | docker-compose.yml with backend + frontend |
| 1.15 | Security review (auth, input validation) | TBD | - | Basic auth for admin endpoints |
| 2.0 | Phase 2: Real LLM integration | TBD | - | Post-MVP planning |

---

## Blocked

| # | Task | Blocker | Notes |
|---|------|---------|-------|
| — | — | None | — |

---

## Done

| # | Task | Date | Commit |
|---|------|------|--------|
| 1.0 | Project scaffolding + planning docs | 2026-06-26 | `5d21cca` |

---

**Status:** Backend scaffolding in progress.
**Last updated:** 2026-06-26
