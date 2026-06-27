# DECISIONS.md — Architecture & Design Decisions

> Log of key decisions made for Emma.ai. Each entry has a rationale so future-Sparky knows *why*, not just *what*.

---

## D001: Use FastAPI for Backend

**Decision:** Python FastAPI over Node/Express or Go.  
**Rationale:** The agent logic is inherently Python (LLM integration, knowledge base queries, NLP). Using Python for the API avoids a language boundary between framework and agent layer. FastAPI gives us async support, auto-generated docs, and Pydantic validation.  
**Alternatives considered:** Node.js/Express, Go/Gin, Rust/Actix.  
**Status:** ✅ Approved

---

## D002: SQLite for Phase 1 Data Store

**Decision:** SQLite with potential migration path to Postgres later.  
**Rationale:** Phase 1 doesn't need concurrent writes at scale. SQLite is zero-config, requires no running process, and the entire app can be self-contained. Migration to Postgres when needed is straightforward (SQLAlchemy supports both via dialect switching).  
**Alternatives considered:** PostgreSQL, MongoDB, DynamoDB.  
**Status:** ✅ Approved  
**Migration note:** Use SQLAlchemy ORM so the database backend is a configuration switch away.

---

## D003: Mock-First Strategy

**Decision:** Simulated HR knowledge base and response generation for MVP. No real LLM calls during Phase 1.  
**Design an interface/adapter layer from day one that can swap mock → real without changing API contracts.**  
**Rationale:** We need to validate the user experience, workflow, and routing logic before worrying about AI quality. Mock responses let us iterate the UI and backend faster. When we add LLM integration, the interface is already defined.  
**Risk:** If mock data looks too "fake," it may not accurately represent end-user needs. Mitigation: use realistic HR policy content (not dummy text).  
**Status:** ✅ Approved

---

## D004: Agent Logic as Python Service Layer

**Decision:** Business logic (question classification, knowledge base lookup, response generation) lives in a separate `services/` module, not inline with FastAPI routes.  
**Rationale:** Keeps the API layer thin and testable. The agent service can be swapped later (mock → LLM-based) without touching route handlers. Enables unit testing of business logic independently.  
**Status:** ✅ Approved

---

## D005: Rule-Based Triage for MVP

**Decision:** Initial triage uses keyword/category matching rules, not ML classification.  
**Rationale:** Simple to implement, debug, and audit. HR questions naturally fall into categories (benefits, leave, payroll, policy, compliance, other). Rules are explicit and configurable without retraining models. Later phases can add NLP classification on top.  
**Status:** ✅ Approved

---

## D006: React + Vite for Frontend

**Decision:** React with Vite over Next.js or Svelte.  
**Rationale:** Vite is fast for dev iteration. React has broad ecosystem support. Next.js adds complexity (SSR, routing) that we don't need yet — a separate backend API is clearer for our architecture. We're building an SPA consumed by the FastAPI backend, not a content-heavy app.  
**Alternatives considered:** Next.js (SSR), Svelte (lightweight but smaller ecosystem), plain HTML/JS (too limiting).  
**Status:** ✅ Approved

---

## D007: Full Audit Trail Design

**Decision:** Every interaction gets an `audit_log` entry with: timestamp, actor type (employee/manager/hr_admin), action, entity_id, metadata JSON.  
**Rationale:** HR data is sensitive. Compliance audits may require showing exactly what Emma responded to whom and when. Structured logs enable both compliance and the feedback-improvement loop (which interactions got low ratings?).  
**Status:** ✅ Approved

---

## D008: Docker-Ready but Not Docker-First for MVP

**Decision:** Write a `Dockerfile` and `docker-compose.yml`, but don't require Docker to run locally. The app should work with just `pip install` and `npm install`.  
**Rationale:** Docker is useful for deployment and consistency, but it adds setup friction during development. Phase 1 developers should be able to start the backend in 2 commands and frontend in 1 command without Docker knowledge.  
**Status:** ✅ Approved

---

## Open Decisions

| # | Question | Notes |
|---|----------|-------|
| D009 | Should we use Alembic for migrations or raw SQL? | SQLite is simple; Alembic may be overkill for now. Decision pending schema stabilization. |
| D010 | Auth strategy for admin endpoints? | Basic auth, API keys, or JWT? Depends on deployment target. Defer until Phase 2 planning. |
| D011 | Knowledge base format: SQL tables or JSON fixtures? | SQL allows CRUD at runtime. JSON fixtures are simpler to version-control. Trade-off pending. |

---

_Last updated: 2026-06-26_
