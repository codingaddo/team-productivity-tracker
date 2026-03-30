# Team Productivity Tracker

Internal time and productivity tracker for MCP Testing Sprint 2.

## Stack
- Backend: FastAPI (Python) managed with `uv`
- Frontend: Next.js + TypeScript
- CI: GitHub Actions
- Deployment: Railway

## Repository layout
- `backend/` - FastAPI service and Python project metadata
- `frontend/` - Next.js TypeScript app
- `.github/workflows/ci.yml` - basic validation pipeline

## Local development

### Backend
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment variables
Set these in Railway and locally as needed:
- `DATABASE_URL`
- `AUTH_SECRET`
- `JWT_SECRET`
- `NEXT_PUBLIC_API_BASE_URL`

## Notes
This repository is the single source of truth for backend, frontend, infrastructure, and deployment automation.
