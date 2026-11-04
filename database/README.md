# Database integration — later phase

MySQL is intentionally not enabled in this first milestone. The current Flask API stores development data in `backend/data/db.json`.

Later we will:
1. Create the `deadlineshield` MySQL database and normalized tables.
2. Add SQLAlchemy models and migrations.
3. Replace `store.py` calls with repository/database operations.
4. Preserve the React API routes so the frontend does not need a redesign.
