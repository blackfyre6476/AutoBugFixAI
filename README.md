# AutoFix AI — Autonomous Bug Fixing Assistant

AutoFix AI is a full-stack application that autonomously investigates, patches, validates, and documents bug fixes for local code repositories — all without touching the original codebase until you explicitly approve.

## Architecture

```
autofix-ai/
├── backend/          # FastAPI + Python agents
│   ├── agents/       # RepositoryAnalyst, BugInvestigator, FixGenerator
│   ├── app/          # FastAPI app + API routers
│   ├── models/       # Pydantic models
│   ├── orchestrator/ # Pipeline engine
│   ├── repository/   # Git manager, patcher, auditor
│   └── sandbox/      # Isolated test runner
├── frontend/         # Next.js 14 + Tailwind UI
│   └── app/          # page.tsx — single-page UI
├── examples/         # Demo repositories with intentional bugs
│   ├── user_analytics_service/
│   └── buggy_calculator/
├── tests/            # Backend integration tests
└── docs/             # Architecture & setup guides
```

## Features

- **Analyze & Validate** — describe a bug, get an AI-generated fix proposal validated in an isolated sandbox
- **Audit Repository** — scan every source file for bug patterns (zero-division, missing dict `.get()`) — returns exact `file:line` location, no manual file path needed
- **Line-specific patches** — every candidate operation includes `file_path` + `line_number`
- **Review-first workflow** — the original repository is never modified until you check the approval box and click commit
- **Git integration** — approved fixes are committed to a new `autofix/<id>` branch

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**.

### API docs

Open **http://localhost:8000/docs** for the interactive Swagger UI.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/fixes/analyze` | Full pipeline: investigate → fix → validate |
| `POST` | `/api/v1/fixes/audit` | Scan repo for bug patterns, return file + line |
| `POST` | `/api/v1/fixes/apply-approved` | Apply approved fix to a new Git branch |
| `GET`  | `/api/v1/health` | Health check |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Optional. Enables LLM-powered fix generation |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | Override for OpenAI-compatible endpoints |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend URL for the frontend |

## Example Usage

### Audit mode (no file path needed)

```json
POST /api/v1/fixes/audit
{
  "repository_path": "C:/projects/my-service",
  "bug_description": "ZeroDivisionError when total_visitors is 0"
}
```

Response:
```json
{
  "candidates": [{
    "file_path": "analytics.py",
    "line_number": 3,
    "description": "Division without a zero-denominator guard",
    "search": "    return (conversions / total_visitors) * 100.0",
    "replacement": "    if total_visitors == 0:\n        return 0.0\n    return (conversions / total_visitors) * 100.0"
  }],
  "total_found": 1
}
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, httpx, GitPython
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Lucide icons
- **Testing**: pytest, pytest-anyio
