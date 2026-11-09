
import os

from flask import Flask, jsonify
from flask_cors import CORS

from config import PORT
from routes.auth import bp as auth_bp
from routes.activities import bp as activities_bp
from routes.dashboard import bp as dashboard_bp
from routes.revision import bp as revision_bp
from routes.subject_routes import bp as subjects_bp
from routes.notification_routes import bp as notifications_bp

from store import get_connection


app = Flask(__name__)

frontend_urls = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)

allowed_origins = [
    url.strip()
    for url in frontend_urls.split(",")
    if url.strip()
]

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": allowed_origins
        }
    }
)

# Register API routes.
app.register_blueprint(auth_bp)
app.register_blueprint(activities_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(revision_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(notifications_bp)


@app.get("/")
def home():
    return jsonify({
        "name": "LEARNOVA API",
        "status": "running",
        "database": "TiDB Cloud MySQL"
    })


@app.get("/api/health")
def health():
    """Check database connectivity without loading application tables."""

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        if not result or result[0] != 1:
            raise RuntimeError("Database health check failed.")

        return jsonify({
            "status": "ok",
            "database": "connected",
            "message": "LEARNOVA backend is ready."
        }), 200

    except Exception:
        app.logger.exception("Database health check failed.")

        return jsonify({
            "status": "error",
            "database": "unavailable",
            "message": "Database connection failed."
        }), 503

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.errorhandler(404)
def not_found(_):
    return jsonify({
        "error": "Endpoint not found."
    }), 404


@app.errorhandler(500)
def server_error(_):
    return jsonify({
        "error": "Internal server error."
    }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False
    )
