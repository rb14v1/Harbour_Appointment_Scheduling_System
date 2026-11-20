# Appointment Scheduling Management System

Single-admin appointment scheduler. React + Vite + TypeScript frontend, Django REST Framework backend using PyMongo, and a local MongoDB replica set. No authentication.

## 1. One-time setup

### Install MongoDB Community Server
1. Download the Windows MSI from https://www.mongodb.com/try/download/community (version 9.0, package: MSI).
2. Run the installer, choose **Complete**.
3. **Untick "Install MongoDB as a Service"**. The start script runs MongoDB for you.
4. Finish the installer.

### Install backend dependencies
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
cd ..
```

### Install frontend dependencies
```powershell
cd frontend
npm install
cd ..
```

## 2. Run the app (three PowerShell windows)

**Window 1: MongoDB** (leave it open)
```powershell
.\scripts\start-mongo.ps1
```

**Window 2: Backend**
```powershell
cd backend
.\.venv\Scripts\python manage.py init_mongo
.\.venv\Scripts\python manage.py runserver 8000
```
`init_mongo` sets up the replica set on first run and applies any pending migrations. Re-running it is safe and never deletes data.

**Window 3: Frontend**
```powershell
cd frontend
npm run dev
```

Open http://localhost:5173. The app opens directly to the dashboard.

## 3. Database migrations

Migrations live in `backend/mongo_migrations/` as numbered files (`0001_initial_schema.py`, `0002_...`). Each file defines `VERSION`, `DESCRIPTION` and `up(db)`. Applied versions are recorded in the `schema_migrations` collection.

```powershell
cd backend
.\.venv\Scripts\python manage.py migrate_mongo --status   # list applied and pending
.\.venv\Scripts\python manage.py migrate_mongo            # apply pending
```

Rules for new migrations:
- Never edit a migration that has already been applied. Add a new numbered file instead.
- Make `up` idempotent (for example, `create_index` with the same name and spec).
- Never drop data in a migration unless the change is deliberate and reviewed.

## 4. Tests

Start MongoDB (Window 1) and run `init_mongo` once (Window 2), then:

```powershell
cd backend
.\.venv\Scripts\python manage.py test
```

Backend tests use the `appointment_scheduling_test` database only. Only that database is cleared.

```powershell
cd frontend
npm test
```

## Business rules

- Times are 15-minute aligned, end after start, and not in the past.
- One shared calendar. Overlaps are rejected with HTTP 409 (unique slot index inside a transaction).
- Cancelled appointments free their slots. Completed appointments keep theirs.
- Only scheduled appointments can be rescheduled, completed or cancelled.
- Customers and appointment types referenced by appointments cannot be deleted (409).
- Customer emails are unique (case-insensitive).
