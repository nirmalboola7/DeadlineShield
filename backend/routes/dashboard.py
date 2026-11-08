
from datetime import datetime, timedelta, timezone
from collections import Counter

from flask import Blueprint, jsonify, g

from store import read_db
from utils import login_required
from gamification import get_student_performance


bp = Blueprint('dashboard', __name__, url_prefix='/api')


# ==========================================
# DASHBOARD API
# ==========================================

@bp.get('/dashboard')
@login_required
def dashboard():

    db = read_db()

    items = [
        a for a in db['activities']
        if a['user_id'] == g.user['user_id']
    ]

    now = datetime.now(timezone.utc)

    due_soon = 0
    dates = Counter()

    for activity in items:

        try:
            due = datetime.fromisoformat(
                activity['due_date'].replace('Z', '+00:00')
            )

            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)

            if (
                now <= due <= now + timedelta(hours=48)
                and activity['status'] != 'Completed'
            ):
                due_soon += 1

            if (
                activity['status'] != 'Completed'
                and due.date() >= now.date()
            ):
                dates[due.date().isoformat()] += 1

        except (ValueError, TypeError, KeyError):
            pass

    overload = [
        {'date': date, 'count': count}
        for date, count in dates.items()
        if count >= 2
    ]

    stats = {
        'total': len(items),

        'exams': sum(
            1 for a in items
            if a['activity_type'] == 'Exam'
            and a['status'] != 'Completed'
        ),

        'due_soon': due_soon,

        'completed': sum(
            1 for a in items
            if a['status'] == 'Completed'
        )
    }

    items.sort(key=lambda a: a.get('due_date', ''))

    return jsonify({
        'stats': stats,
        'activities': items,
        'overload': overload
    })


# ==========================================
# ANALYTICS API
# ==========================================

@bp.get('/analytics')
@login_required
def analytics():

    db = read_db()

    items = [
        a for a in db['activities']
        if a['user_id'] == g.user['user_id']
    ]

    total = len(items)

    completed = sum(
        a['status'] == 'Completed'
        for a in items
    )

    now = datetime.now(timezone.utc)
    overdue = 0

    for activity in items:

        try:
            due = datetime.fromisoformat(
                activity['due_date'].replace('Z', '+00:00')
            )

            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)

            if due < now and activity['status'] != 'Completed':
                overdue += 1

        except (ValueError, TypeError):
            pass

    by_type = dict(
        Counter(a['activity_type'] for a in items)
    )

    return jsonify({
        'total': total,
        'completed': completed,
        'pending': total - completed,
        'overdue': overdue,
        'completion_rate': round(completed / total * 100) if total else 0,
        'by_type': by_type
    })


# ==========================================
# STUDENT LEADERBOARD API
# ==========================================

@bp.get('/leaderboard')
@login_required
def leaderboard():

    db = read_db()

    students = get_student_performance(db)

    current_user_id = g.user['user_id']

    current_student = next(
        (
            student for student in students
            if student['user_id'] == current_user_id
        ),
        None
    )

    return jsonify({
        'leaderboard': students,
        'my_performance': current_student
    })
