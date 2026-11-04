# DeadlineShield

A full-stack academic workload manager built with React + Vite and Python Flask.
This version uses temporary JSON-file storage so the frontend and backend can be developed before MySQL integration.

## Requirements
- Node.js 20+
- Python 3.10+
- npm
- VS Code

## Run the backend (Terminal 1)
```bash
cd backend
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# If PowerShell blocks activation, use:
# .\venv\Scripts\python.exe -m pip install -r requirements.txt
pip install -r requirements.txt
copy .env.example .env
python app.py
```
Backend: http://localhost:5000

## Run the frontend (Terminal 2)
```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```
Frontend: http://localhost:5173

## Demo
Register a new account, log in, and create assignments, projects, exams or lab records.
The backend writes temporary data to `backend/data/db.json`.

## Important
- This is a development/demo version, not production-ready.
- JSON storage is temporary and not suitable for multiple concurrent users.
- Set a long random `SECRET_KEY` in `backend/.env`.
- Never commit `.env`, user data, uploads or virtual environments.
- Uploaded files are stored locally in `backend/uploads`.
- Revision currently demonstrates a safe upload workflow and sample revision questions. AI/PDF text extraction can be integrated in a later phase.
- MySQL integration is intentionally postponed. The API structure is designed so the storage layer can be replaced later.
