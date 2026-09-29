# AutoFix AI Setup & Developer Guide

Follow this step-by-step guide to set up and run AutoFix AI on your local environment.

---

## 🛠 Local Environment Setup

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ & npm 9+
- Git
- Docker Desktop (for container sandbox execution)

---

### 2. Setting Up Environment Variables
Copy `.env.example` to `.env` in the project root:

```bash
cp .env.example .env
```

Ensure `.env` contains:
```env
APP_NAME="AutoFix AI"
ENVIRONMENT="development"
LOG_LEVEL="INFO"
BACKEND_PORT=8000
FRONTEND_PORT=3000
CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
OPENAI_API_KEY=""
OPENAI_MODEL="gpt-4o-mini"
```

---

### 3. Backend Setup & Run

1. Navigate to backend directory or project root:
   ```bash
   cd backend
   ```
2. Create virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate virtual environment:
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
   - Linux / macOS: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Launch FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
6. Open `http://localhost:8000/docs` in your browser to inspect Swagger API docs.

---

### 4. Frontend Setup & Run

1. Open a separate terminal and navigate to `frontend`:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Launch Next.js development server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:3000` in your browser to access the dashboard.

---

### 5. Running Automated Tests

Run the backend pytest suite:
```bash
python -m pytest tests/ -v
```

---

### 6. Running via Docker Compose

```bash
docker-compose up --build
```
Both backend (`:8000`) and frontend (`:3000`) will spin up inside containers.

## 7. Run an Analysis

Use the dashboard or send a request with an absolute path to a local Python repository:

```bash
curl -X POST http://localhost:8000/api/v1/fixes/analyze \
  -H "Content-Type: application/json" \
  -d '{"repository_path":"C:/projects/example","bug_description":"Paste the stack trace here","test_command":"pytest"}'
```

The API returns the root-cause assessment, an LLM-assisted or heuristic proposal, test evidence, a regression result, and a pull-request-ready summary. It does not alter the supplied repository.
