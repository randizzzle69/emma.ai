# Emma.ai — HR Generalist Digital Worker

> An AI-powered digital worker designed to own HR service workflows for a convenience retail company. Not a chatbot. A *worker*.

## What Is Emma.ai?

Emma is an agent that:

- Answers employee and manager HR questions
- Triage HR issues and routes exceptions to the right person
- Documents outcomes in a structured audit trail
- Captures human feedback for continuous improvement
- Improves over time through learned interactions

**This is not a simple Q&A bot.** It's an agent that can own workflows, make decisions within defined boundaries, and escalate when needed.

## Phase 1 — MVP Foundation

| # | Feature | Status |
|---|---------|--------|
| 1 | Simple web UI (React + Vite) | Planned |
| 2 | Backend API (FastAPI) | Planned |
| 3 | HR question intake flow | Planned |
| 4 | Mock HR knowledge base | Planned |
| 5 | Exception / routing workflow | Planned |
| 6 | Human feedback capture | Planned |
| 7 | Basic audit log | Planned |
| 8 | Architecture for future integrations | Planned |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| Data | SQLite |
| Agent Logic | Python service layer |
| LLM | Local-first architecture (mock responses for MVP) |
| Container | Docker-ready structure |

## Project Structure

```
Emma.ai/
├── README.md              # This file
├── PROJECT_CONTEXT.md     # Deep project context & goals
├── BACKLOG.md             # Source-of-truth task backlog
├── DECISIONS.md           # Architecture & design decisions
├── SESSION_LOG.md         # Per-session work log
├── RESUME_MODE.md         # How to resume after pause/crash/reset
├── ARCHITECTURE.md        # System architecture diagrams
├── .gitignore             # Git ignores
├── backend/               # FastAPI server
├── frontend/              # React + Vite UI
├── docs/                  # Extended documentation
└── tests/                 # Test suite
```

## Quick Start (Phase 1)

See `RESUME_MODE.md` for the full resumption procedure. After scaffolding:

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Documentation Priority

When you need context, read in this order:

1. `RESUME_MODE.md` — How to get back on track
2. `PROJECT_CONTEXT.md` — What we're building and why
3. `BACKLOG.md` — Where we are right now
4. `SESSION_LOG.md` — What happened last time
5. `DECISIONS.md` — Why we made our choices
6. `ARCHITECTURE.md` — How the system is designed

---

**Status:** Phase 1 — Scaffolding complete. Feature work pending.
