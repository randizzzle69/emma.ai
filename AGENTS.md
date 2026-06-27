# Emma.ai Agent Operating Rules

This repository is Emma.ai.

Emma.ai is an HR Generalist Digital Worker focused first on answering HR policy and rules questions from approved documents, capturing feedback, and improving accuracy over time.

## Mandatory Startup Procedure

At the start of every coding session, the agent must inspect:

1. `git status`
2. `git log --oneline --decorate -5`
3. `README.md` if present
4. `BACKLOG.md`
5. `DECISIONS.md` if present
6. `SESSION_LOG.md` if present
7. `RESUME_MODE.md` if present
8. Relevant backend and frontend source files

The agent must report only:

- current branch
- git status summary
- latest 3 commits
- backend framework detected
- frontend framework detected
- exact files planned for modification

Then the agent may begin implementation.

## Hard Rules

1. Work only in `~/projects/Emma.ai`.
2. Do not work on `invoice-ai`.
3. Do not redesign the app unless explicitly asked.
4. Do not create `.bak` files or backup folders.
5. Preserve existing functionality.
6. Work in small, verifiable steps.
7. After every code change, run a relevant test, build, import check, or sanity check.
8. If blocked after 3 attempts, stop and report the blocker.
9. Do not apologize or narrate intentions.
10. Do not say “I will now” unless immediately followed by an actual command or file change.
11. At the end of each session, update `SESSION_LOG.md` and `BACKLOG.md`.
12. Leave the repo in one of two states:
    - clean working tree, or
    - clearly reported uncommitted changes with exact next steps.

## Current MVP Priority

Build the first working Emma.ai policy Q&A chatbot.

The MVP must support:

1. Asking an HR policy/rules question.
2. Returning an answer from approved local policy documents.
3. Showing source references when possible.
4. Capturing user feedback:
   - thumbs up / thumbs down
   - optional comment
   - question
   - answer
   - source references
   - timestamp
5. Persisting feedback locally.
6. Keeping the solution simple and demoable.
