# TrueMark AI — Round 3-ready project

TrueMark is a React/Vite frontend and FastAPI backend. This archive is cleaned for GitHub (no embedded `.git` history, Python bytecode, or test caches) and includes a Round 3 Control Center.

## Round 3 features included

- **Image/document review:** PNG, JPG/JPEG, PDF, and DOCX uploads call the existing FastAPI verification endpoint. The API returns available brand-rule, image palette/logo and document checks. Contrast and alt text are explicitly marked unsupported where the file format/API cannot reliably verify them.
- **Governance insights:** team/channel selectors and a rule-ambiguity review panel. The visible sample counts are labelled as sample data; connect them to persistent governance events for production reporting.
- **Measured reliability:** a small planted-error demonstration set, displayed detection rate, and dismiss action that changes the demo metric. It is not represented as a validated ML benchmark.
- **Multi-channel drift guard:** compares source and adapted text with a token-overlap score and lists additions/removals; includes a rule-based suggested draft.
- **Slack/email notifications:** prepares an email draft or opens a supplied Slack URL. Automatic unattended delivery requires a secure server-side integration and is intentionally not faked in the browser.
- **Accessibility pass:** labelled inputs, live status messages, visible keyboard focus, and responsive layouts.

Existing content analysis, brand guidelines, assets, review/approval, and version-history screens are retained.

## Run locally in VS Code (Windows PowerShell)

Prerequisites: Python 3.11+ and Node.js LTS.

1. Extract the ZIP, then open the extracted `TrueMark-Round3` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Install backend dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r backend/requirements.txt
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again.

4. Start the backend in terminal 1:

   ```powershell
   cd backend
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

   Open `http://127.0.0.1:8000/docs` to verify the API is running.

5. Open a **second** terminal at the project root and start the frontend:

   ```powershell
   cd frontend
   npm ci
   Copy-Item .env.example .env.local
   # Edit .env.local and set VITE_API_BASE_URL=http://127.0.0.1:8000
   npm run dev
   ```

6. Open the local URL printed by Vite (usually `http://localhost:5173`). Select **Round 3 Control Center** from the left navigation.

Keep both terminals running while testing. If `npm ci` fails, resolve the Node/npm install error first; do not skip the dependency install.

## Deploy using Vercel

**Important:** I cannot publish to your Vercel/GitHub accounts from this archive alone. You must push the code and trigger deployment while signed in. A working public frontend link also depends on a live backend URL.

### A. Push this cleaned project to your GitHub repository

This archive intentionally does not include the ZIP's old `.git` folder.

1. Create a backup of your existing repository folder.
2. Copy the extracted project files into the local clone of your repository (do not copy a nested `TrueMark-Round3` folder; copy its contents).
3. In PowerShell at the repository root:

   ```powershell
   git status
   git add .
   git commit -m "Add Round 3 governance and reliability features"
   git push origin main
   ```

   If Git says there is no remote, run `git remote add origin https://github.com/mokshagna-27/TrueMark.git` once, then push. If the repository already has a remote, do not add it again.

### B. Deploy the frontend on Vercel

1. Import/select the GitHub repository in Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework preset: **Vite**. Build command: `npm run build`. Output directory: `dist`. Install command: `npm ci`.
4. Add environment variable `VITE_API_BASE_URL` with the deployed FastAPI backend origin, e.g. `https://truemark-blue.vercel.app` (no trailing slash).
5. Deploy. This gives the public frontend URL to submit.

### C. Backend

The frontend calls `POST /api/v1/verification/file` on the backend configured by `VITE_API_BASE_URL`. The backend must be deployed separately and must include this updated code/dependencies. Check `https://YOUR-BACKEND-DOMAIN/docs` and `/health` (if enabled) before testing the frontend. Redeploy the backend after pushing this version; then redeploy the frontend if you changed `VITE_API_BASE_URL`.

The frontend URL is the single public link users open, but the backend remains a separate service. This project cannot become a single self-contained Vercel deployment merely by setting one URL: Vercel's static frontend and FastAPI runtime are deployed as separate services in this setup.

## Notes and honest limitations

- Existing database configuration and storage behaviour are retained; local browser demo data may not sync across browsers or users.
- Image palette/logo checks require a configured brand profile. Alt text and contrast may be unavailable from raw uploaded files; the API reports that instead of claiming a pass.
- Governance chart values in this Round 3 panel are demonstration values until connected to persistent event records.
- The reliability score is based on the included small sample and is intended to demonstrate the workflow, not to claim production accuracy.
- Slack automation requires a server-side webhook integration. Never put webhook secrets in frontend environment variables.
- Do not commit `.env` files, API secrets, database passwords, or webhook URLs.

## Main paths

- `frontend/src/components/RoundThree.tsx` — Round 3 control center
- `backend/app/api/file_verification.py` — file validation and checks
- `backend/main.py` — FastAPI application and CORS
- `frontend/vercel.json` — Vercel SPA routing
