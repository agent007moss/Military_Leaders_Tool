# MilitaryTool (MVP backend)

## Prereqs
- Python 3.11+
- PostgreSQL 15+
- (Optional) uv (recommended)

## Setup (Windows PowerShell)
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"

Copy env:
cp ..\.env.example ..\.env  (or manually create .env)

Run migrations:
alembic upgrade head

Run API:
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Swagger:
http://127.0.0.1:8000/docs