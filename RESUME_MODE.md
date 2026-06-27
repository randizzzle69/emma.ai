# RESUME_MODE.md — How to Resume Emma.ai After Pause/Crash/Reset

## When to Use This File

Read this file **first** whenever you start a new session, after a context reset, crash, or interruption. It gets you back up to speed in under 60 seconds.

---

## 1. Read These Files (in order)

1. **PROJECT_CONTEXT.md** — What we're building and why
2. **BACKLOG.md** — Where we are right now (Now/Next/Later/Done)
3. **SESSION_LOG.md** — What happened last session
4. **DECISIONS.md** — Why we made key architecture choices
5. **RESUME_MODE.md** — This file (you're reading it)

## 2. Current Project State

| Field | Value |
|-------|-------|
| **Project** | Emma.ai — HR Generalist Digital Worker |
| **Phase** | Phase 1: MVP Foundation |
| **MVP Goal** | Working app with web UI, backend API, mock HR KB, triage/routing, feedback capture, and audit log |
| **Current Status** | Scaffolding complete. Ready for feature work. |
| **Tech Stack** | React/Vite + FastAPI + SQLite + Python agent layer |

## 3. Current Architecture (Simplified)

```
Emma.ai/
├── backend/            # FastAPI server
│   ├── main.py         # App entry point
│   ├── services/       # Agent business logic
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   └── db/             # SQLite + migrations
├── frontend/           # React + Vite SPA
│   ├── src/            # Components, pages, hooks
│   └── public/         # Static assets
├── docs/               # Extended documentation
├── tests/              # Test suite (backend + frontend)
├── README.md
├── PROJECT_CONTEXT.md
├── BACKLOG.md
├── DECISIONS.md
├── ARCHITECTURE.md
└── RESUME_MODE.md      ← You are here
```

## 4. Last Completed Task

**Task 1.0:** Project scaffolding + planning docs  
**Date:** 2026-06-26  
**Result:** All 8 planning files created, git repo initialized, first commit ready.

## 5. Next Recommended Task

**Task 1.1:** Set up backend (FastAPI project structure)  
- Create `backend/` directory
- Add `requirements.txt`, `Dockerfile`
- Initialize FastAPI app at `backend/main.py`
- Commit to git

## 6. Known Risks

| Risk | Mitigation |
|------|-----------|
| Context loss between sessions | All planning in git, this file exists |
| Scope creep | Strict backlog discipline — no work without BACKLOG entry |
| Over-engineering agent logic | Mock-first approach, validate UX first |
| SQLite scaling | Documented migration path via SQLAlchemy dialect switch |

## 7. How to Verify the App Works (When Ready)

### Backend verification:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# Visit http://localhost:8000/docs for auto-generated API docs
# Health check: curl http://localhost:8000/api/health
```

### Frontend verification:
```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:5173
```

### End-to-end smoke test (Phase 1):
1. Submit an HR question via web UI → verify it appears in database
2. Check Emma's mock response → verify it routes to the right category
3. Submit feedback (thumbs up/down) → verify stored in DB
4. View audit log → verify all interactions are logged
5. Restart both services → verify data persists

## 8. Commands to Restart the Environment

```bash
# Backend
cd ~/projects/Emma.ai/backend
uvicorn main:app --reload    # Hot reload mode
# or (prod)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd ~/projects/Emma.ai/frontend
npm run dev                   # Dev server
npm run build                 # Production build

# Full stack with Docker
cd ~/projects/Emma.ai
docker-compose up --build

# Git operations
cd ~/projects/Emma.ai
git status                    # Check state
git log --oneline             # Recent commits
git branch -M main            # Rename to main if needed
```

## 9. What Files to Read First When Resuming

**Always start here (this file), then:**

1. `PROJECT_CONTEXT.md` — Reset on project goals & business context
2. `BACKLOG.md` — See what's Next / Blocked / Done
3. `SESSION_LOG.md` — Review last session for continuity
4. `ARCHITECTURE.md` — Review system design if you forgot details
5. `DECISIONS.md` — Check why key things were built a certain way

## 10. Emergency Reset Procedure

If everything is lost (no files, no memory):

```bash
# 1. Check git history
cd ~/projects/Emma.ai
git log --oneline

# 2. If commits exist, restore to last good state
git reset --hard HEAD~N   # N = number of bad commits to undo

# 3. Re-read RESUME_MODE.md → go back to step 1 above
```

---

**This file is the single source of truth for session resumption.**  
**Last updated: 2026-06-26**
