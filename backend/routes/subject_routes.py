from flask import Blueprint, request, jsonify, g
from datetime import datetime, timezone
from store import read_db, write_db, next_id
from utils import login_required

bp = Blueprint("subjects", __name__, url_prefix="/api/subjects")

@bp.get("")
@login_required
def get_subjects():
    db = read_db()
    subjects = db.setdefault("subjects", [])
    user_subjects = [
        s for s in subjects
        if s.get("user_id") == g.user["user_id"]
    ]
    return jsonify(user_subjects)

@bp.post("")
@login_required
def add_subject():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()

    if not name:
        return jsonify({"error": "Subject name is required."}), 400

    db = read_db()
    subjects = db.setdefault("subjects", [])

    existing = next(
        (s for s in subjects
         if s.get("user_id") == g.user["user_id"]
         and s.get("name", "").lower() == name.lower()),
        None
    )

    if existing:
        return jsonify({"error": "This subject already exists."}), 409

    subject = {
        "subject_id": next_id(subjects, "subject_id"),
        "user_id": g.user["user_id"],
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    subjects.append(subject)
    write_db(db)

    return jsonify(subject), 201

@bp.delete("/<int:subject_id>")
@login_required
def delete_subject(subject_id):
    db = read_db()
    subjects = db.setdefault("subjects", [])

    subject = next(
        (s for s in subjects
         if s.get("subject_id") == subject_id
         and s.get("user_id") == g.user["user_id"]),
        None
    )

    if not subject:
        return jsonify({"error": "Subject not found."}), 404

    db["subjects"] = [
        s for s in subjects
        if not (
            s.get("subject_id") == subject_id
            and s.get("user_id") == g.user["user_id"]
        )
    ]

    write_db(db)
    return jsonify({"message": "Subject deleted."})
