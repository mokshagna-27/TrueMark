#!/usr/bin/env bash
# One-command local start (macOS/Linux): backend on :8000, frontend on :5173
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r backend/requirements.txt
[ -f frontend/.env.local ] || cp frontend/.env.example frontend/.env.local
(cd frontend && npm ci --silent)
(cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000) &
BACK=$!
trap "kill $BACK" EXIT
(cd frontend && npm run dev)
