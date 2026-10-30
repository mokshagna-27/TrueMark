# Integration notes

## Round 2 — analyzer integration and hardening

- **Analyzer is now wired into the web app.** `/api/v1/analysis/text` and the
  document check in `/api/v1/verification/file` run the full
  `truemark_analyzer` pipeline (privacy-disclosure, unsupported-claim and
  brand-voice rules, your required/forbidden terms, PII detection, retrieval of
  approved sources, optional LLM review) through
  `backend/app/api/core/models/services/analyzer_service.py`. The response keeps
  the shape the frontend already used and adds `llm_state`, `pii_detected`,
  `retrieved_sources` and per-finding `matched_text`.
- **Optional AI review.** Set `TRUEMARK_LLM_API_KEY` + `TRUEMARK_LLM_MODEL`
  (and optionally `TRUEMARK_LLM_BASE_URL`) in `.env`. Only PII-redacted text is
  sent. If the LLM call fails, the rule-based report is still returned and the
  UI says AI review was unavailable. Without a key everything is rule-based.
- `backend/requirements.txt` was missing `python-dotenv` (imported by
  `database.py`) and `pydantic`; a backend-only install would crash. Fixed.
- Deprecated `@app.on_event("startup")` replaced with a lifespan handler.
- CORS: extra origins via `CORS_ORIGINS` env var (comma-separated) instead of
  editing code; `*.vercel.app` still allowed.
- SQLite fallback uses `/tmp` on Vercel/Lambda (project dir is read-only there).
  Use Postgres via `DATABASE_URL` for persistent data in production.
- `api/index.py` also puts the repo root on `sys.path` so the analyzer imports
  on Vercel.
- `frontend/.env.example` pointed at the original author's Vercel backend; it
  now defaults to `http://127.0.0.1:8000`.
- UI: engine badge, matched text, AI-unavailable notice and consulted sources
  shown in the analysis report.
- New `tests/test_backend_api.py` (health, analysis, PII, LLM-failure fallback,
  file uploads, versions CRUD, brand profiles). Suite: **79 passed, 0 skipped**
  (the real-analyzer smoke test now runs by default against the bundled
  pipeline).
- `start.sh` / `start.ps1`: one-command local start.

## Round 1 (earlier)

This copy of the project has been verified to run end-to-end (backend boots,
frontend builds and talks to the backend, full test suite passes). Changes
made while integrating:

1. **`backend/app/api/core/database.py`** — the app used to hard-crash on
   startup if `DATABASE_URL` wasn't set. It now falls back to a local SQLite
   file (`truemark_local.db`) automatically, so the backend runs immediately
   without requiring a Postgres server. Set `DATABASE_URL` in `.env` to use
   real Postgres (e.g. for production).
2. **Missing `__init__.py` files** added under `backend/app/` so the `app.*`
   package imports are explicit rather than relying on implicit namespace
   packages.
3. **`frontend/src/App.tsx`** — the Version History screen had three fetch
   calls hardcoded to `https://truemark-blue.vercel.app`, bypassing the
   configurable `VITE_API_BASE_URL` that every other screen uses. These now
   use the same `API_BASE` pattern (defaulting to
   `http://127.0.0.1:8000` locally), so Version History works against
   whatever backend you actually run/deploy instead of always hitting the
   original author's Vercel instance.
4. Removed `frontend/src/app.backup.tsx`, an unused duplicate that wasn't
   imported anywhere and only added confusion.
5. Added a working root `.env` (SQLite fallback, placeholder API keys) so the
   backend runs out of the box; `frontend/.env.example` still documents
   `VITE_API_BASE_URL` for the frontend (copy it to `.env.local`).

## What's in this project

- **`backend/` + `frontend/`** — the actual running web app (FastAPI +
  React/Vite), described in `README.md`. This is what `npm run dev` /
  `uvicorn main:app` serve.
- **`database/`, `retrieval/`, `truemark_analyzer/`, `evaluation/`,
  `migrations/`, `tests/`** — a separate claim-verification analyzer/CLI
  pipeline and its evaluation harness (own models, own DB connection code).
  The analyzer is now used by the web API (see Round 2 above); the
  evaluation harness remains a standalone CLI.

## Verified locally

- `pip install -r backend/requirements.txt` then
  `python -m uvicorn main:app --reload` inside `backend/` → server starts,
  `/health`, `/api/v1/analysis/text`, `/api/v1/versions` (GET/POST/DELETE)
  all confirmed working against the SQLite fallback DB.
- `npm ci && npm run build` inside `frontend/` → builds cleanly with no
  TypeScript errors.
- `pytest` at the repo root → 66 passed, 1 skipped.

See `README.md` for full run/deploy instructions (unchanged).
