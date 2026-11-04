from flask import Blueprint, jsonify, g
from store import read_db
from utils import login_required
from services.notification_service import generate_notifications

bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

@bp.get("")
@login_required
def get_notifications():
    db = read_db()
    activities = db.get("activities", [])

    notifications = generate_notifications(
        activities,
        g.user["user_id"]
    )

    return jsonify({
        "count": len(notifications),
        "notifications": notifications
    })
