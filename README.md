# TrueMark

TrueMark is an application designed for **claim verification using supporting evidence**. It aims to evaluate the truthfulness of factual claims by retrieving external evidence from authoritative sources and analyzing evidence-claim relationships to deliver structured verdicts with transparent reasoning.

---

> [!NOTE]
> **Project Status: Project Initialization Phase**
> TrueMark is currently in its initial setup phase. No database connections, retrieval pipelines, API endpoints, or AI functionality are implemented yet. This repository currently contains the initialized architectural skeleton and dependency definitions.

---

## Project Structure

```text
TrueMark/
├── .env.example              # Template for environment variables and secrets (dummy placeholders)
├── .gitignore                # Git ignore rules (virtualenvs, cache, local DBs, .env)
├── README.md                 # Project overview, setup guide, and instructions
├── requirements.txt          # Python project dependencies
├── database/                 # Database package (Planned)
│   ├── __init__.py           # Package marker and documentation
│   ├── connection.py         # Database engine and session lifecycle scaffold (Not implemented)
│   └── models.py             # Schema and ORM model definitions scaffold (Not implemented)
├── retrieval/                # Evidence retrieval package (Planned)
│   └── __init__.py           # Package marker and planned responsibilities (Not implemented)
├── docs/                     # Architectural and design documentation
│   └── architecture.md       # Planned architecture and component responsibilities
└── tests/                    # Automated test suite
    ├── __init__.py           # Package marker
    └── test_structure.py     # Sanity check for project scaffolding
```

---

## Team Roles & Responsibilities

* **Rahul**: Responsible for database setup, evidence retrieval module, integration support, and deployment pipelines.
* **Collaborators**: Responsible for AI analysis reasoning engine, frontend/API presentation layers, and verification orchestration.

---

## Getting Started

### Prerequisites
* Python 3.10+ installed
* Git

### 1. Set Up Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create your local `.env` file from the provided example template:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

> [!CAUTION]
> Never commit your `.env` file or any real API keys to version control. The `.gitignore` file is pre-configured to exclude `.env`.

---

## Verifying the Project Structure

To verify that the project structure is intact, run pytest:

```bash
pytest
```

---

## Roadmap & Planned Milestones

1. **Phase 1: Project Initialization** (Current)
   - Minimal Python backend structure, dependency definitions, and architecture specifications.
2. **Phase 2: Database Setup** (Upcoming)
   - SQLAlchemy engine configuration, connection pooling, and ORM models for Claims, Evidence, and Verdicts.
3. **Phase 3: Evidence Retrieval Module** (Upcoming)
   - Integration with external search and authoritative knowledge providers.
4. **Phase 4: AI Analysis & Verification Engine** (Upcoming)
   - Claim verification prompt engineering, NLI inference, and verdict synthesis.
5. **Phase 5: Backend API & End-to-End Integration** (Upcoming)
   - RESTful endpoints exposing claim verification workflows.
