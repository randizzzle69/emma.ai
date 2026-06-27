# BACKLOG.md — Emma.ai Task Backlog

> **Source of truth.** No work without the backlog. Move items as you go. Every completed item gets a `[date]` tag in Done.

---

## Now (In Progress)

| # | Task | Owner | Est. | Notes |
|---|------|-------|------|-------|
| — | — | — | — | Nothing currently blocked |

---

## Next (Ready to Start)

| # | Task | Owner | Est. | Notes |
|---|------|-------|------|-------|
| 1.9 | Frontend — question submission form | Sparky | ~2h | ✅ Complete — QuestionForm.jsx |
| 1.10 | Frontend — responses & feedback UI | Sparky | ~2h | ✅ Complete — ResponseDetail.jsx |
| 1.11 | Frontend — admin/audit log viewer | Sparky | ~2h | ✅ Complete — AdminPanel.jsx |
| 1.8 | Frontend scaffold + wiring | Sparky | ~1h | ✅ Complete — App.jsx + Nav + Router-less SPA |

---

## Later (Backlog — Not Started)

| # | Task | Owner | Est. | Notes |
|---|------|-------|------|-------|
| 2.0 | Docker compose for full stack (backend + frontend) | TBD | - | docker-compose.yml |
| 2.1 | Integration tests E2E flow | TBD | - | Mock → respond → feedback → audit trail |
| 2.2 | Security review (auth, input validation) | TBD | - | Basic auth for admin endpoints |
| 2.3 | LLM integration service interface (mock → real swap) | TBD | - | Interface first, implementation later |
| 3.0 | Phase 2: Real LLM integration | TBD | - | Post-MVP planning |

---

## Now (In Progress)

| # | Task | Owner | Est. | Notes |
|---|------|-------|------|-------|
| — | — | — | — | Nothing currently blocked |

---

## Blocked

| # | Task | Blocker | Notes |
|---|------|---------|-------|
| — | — | None | — |

---

## Done

| # | Task | Date | Commit |
|---|------|------|--------|
| 1.0 | Project scaffolding + planning docs (README, CONTEXT, BACKLOG, DECISIONS, SESSION_LOG, RESUME_MODE, ARCHITECTURE, .gitignore) | 2026-06-26 | `5d21cca` |
| 1.2 | Backend DB schema + models (questions, feedback, audit_log, knowledge_base) | 2026-06-26 | `dac1497` |
| 1.3 | HR knowledge base service (mock data layer + query API) | 2026-06-26 | `dac1497` |
| 1.4 | Question intake API endpoints (POST/GET /questions, filters) | 2026-06-26 | `dac1497` |
| 1.5 | Triage/routing logic (classify → answer/escalate via keyword rules) | 2026-06-26 | `dac1497` |
| 1.6 | Feedback capture endpoints | 2026-06-26 | `dac1497` |
| 1.7 | Audit log service | 2026-06-26 | `dac1497` |
| 1.1 | Backend project setup (FastAPI, dir structure, requirements.txt, Dockerfile) | 2026-06-26 | `dac1497` |
| 1.9 | Frontend question submission form | 2026-06-26 | pending |
| 1.10 | Frontend response viewer + feedback UI | 2026-06-26 | pending |
| 1.11 | Frontend admin/audit log viewer | 2026-06-26 | pending |
| 1.8 | Frontend scaffold + wiring (App.jsx, nav, api service, styles) | 2026-06-26 | pending |

---

**Status:** Phase 1 backend + frontend MVP complete. Ready for integration tests and Docker compose.
**Last updated:** 2026-06-26

**Status:** Phase 1 backend + frontend MVP verified and demoable. No new code needed — all required endpoints, KB docs, and frontend wiring already exist. Backend smoke-tested live (health, question POST/GET/list, feedback POST, audit log GET, KB list). All imports clean. Ready for next-phase work.
**Last updated:** 2026-06-27
