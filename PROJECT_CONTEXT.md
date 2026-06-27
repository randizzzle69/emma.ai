# PROJECT_CONTEXT.md — Emma.ai

## Project Identity

| Field | Value |
|-------|-------|
| **Name** | Emma.ai |
| **Type** | HR Generalist Digital Worker |
| **Domain** | Convenience Retail Company |
| **Phase 1 Goal** | Working MVP foundation with mock data |
| **Tech Stack** | React/Vite + FastAPI + SQLite + Python agent layer |
| **LLM Strategy** | Local-first, mock responses for MVP |

## Business Context

Emma.ai serves a convenience retail company. HR in this domain means:

- High employee turnover (retail)
- Multiple store locations needing consistent HR policy answers
- Manager self-service needs (scheduling conflicts, leave approvals, etc.)
- Compliance-sensitive questions (labor law, wage/hour)
- Mix of deskless workers and office staff

**Emma's job:** Reduce the load on the HR team by handling routine queries, triaging issues, and routing exceptions — all while maintaining a full audit trail.

## Core Requirements

### Must-Have (Phase 1)

1. **HR Question Intake** — Employees/managers submit questions through a web form
2. **Knowledge Base** — Mock HR policies, benefits, procedures stored in SQLite
3. **Response Generation** — Emma "answers" using the knowledge base + agent logic
4. **Triage & Routing** — Simple classification: answer now / escalate to HR / escalate to manager
5. **Human Feedback** — Users rate responses (thumbs up/down) to improve over time
6. **Audit Log** — Every interaction logged with timestamp, actor, and outcome
7. **Web UI** — Clean interface for employees and managers

### Nice-to-Have (Later Phases)

- Real LLM integration (local or cloud)
- Multi-channel support (Slack, Teams, email)
- Integration with real HRIS/payroll systems
- Manager approval workflows
- Analytics dashboard
- Multilingual support
- Scheduling & shift management hints
- Document generation (offer letters, policy acknowledgments)

## Non-Goals for Phase 1

- Real HR system integrations
- Real email/SMS delivery
- Actual document signing
- Multi-department org chart integration
- Compliance certification

## Key Design Decisions

- **Mock-first:** Use mock data and simulated responses until we validate the UX and workflows
- **Local LLM-ready:** Architect for local models from day one, but don't require them for MVP
- **SQLite over Postgres:** Simple enough for Phase 1; migration path is documented
- **Separate agent layer:** Business logic lives in Python services, not in framework routes
- **Full audit trail:** Every interaction is logged and queryable

## Success Criteria (Phase 1)

| Metric | Target |
|--------|--------|
| Employee can submit an HR question | ✓ |
| Emma provides a plausible response | ✓ |
| Response can be rated with feedback | ✓ |
| Exceptions can be escalated & tracked | ✓ |
| Admin can review audit logs | ✓ |
| All data persists across restarts | ✓ |

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Context loss between OpenClaw sessions | Blocking | RESUME_MODE.md + all planning files committed to git |
| Scope creep beyond MVP | Delayed delivery | Strict backlog discipline; everything goes through BACKLOG.md |
| Over-engineering agent logic | Wasted effort | Mock responses first, validate UX, then add intelligence |
| SQLite scaling limits | Migration cost later | Document migration path early; monitor patterns |

---

_Last updated: 2026-06-26_
_Status: Phase 1 scaffolding complete, feature work pending_
