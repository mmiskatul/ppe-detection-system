# PPE Detection Admin Dashboard

Production-ready realtime admin dashboard for PPE analytics with FastAPI, MongoDB (Motor), and Socket.IO.

## Backend

1. Install dependencies:

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure environment:

```bash
copy .env.example .env
```

3. Run API (Socket.IO is mounted at `/ws/analytics`):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Configure environment:

```bash
copy .env.example .env
```

3. Run dev server:

```bash
npm run dev
```

## Notes

- Default admin credentials come from `ADMIN_USERNAME` and `ADMIN_PASSWORD`.
- Realtime analytics update automatically on `prevention_saved`, `incident_saved`, and `analytics_updated`.
