
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, g

from store import get_connection, to_json_datetime
from utils import login_required


bp = Blueprint('dashboard', __name__, url_prefix='/api')


def serialize_activity(item):
    """Convert database datetime values into JSON-friendly strings."""

    result = dict(item)

    for key, value in result.items():
        if hasattr(value, 'isoformat'):
            result[key] = to_json_datetime(value)

    return result


@bp.get('/dashboard')
@login_required
def dashboard():
    user_id = g.user['user_id']

    # TiDB DATETIME values are stored as UTC without timezone information.
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    next_48_hours = now + timedelta(hours=48)
    today = now.date()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch only the activities needed by this user's dashboard.
        cursor.execute(
            """
            SELECT *
            FROM activities
            WHERE user_id = %s
            ORDER BY due_date ASC, activity_id DESC
            """,
            (user_id,)
        )

        items = [
            serialize_activity(item)
            for item in cursor.fetchall()
        ]

        # Let the database calculate dashboard statistics.
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(
                    SUM(status = 'Completed'), 0
                ) AS completed,
                COALESCE(
                    SUM(
                        activity_type = 'Exam'
                        AND status <> 'Completed'
                    ), 0
                ) AS exams,
                COALESCE(
                    SUM(
                        due_date >= %s
                        AND due_date <= %s
                        AND status <> 'Completed'
                    ), 0
                ) AS due_soon
            FROM activities
            WHERE user_id = %s
            """,
            (now, next_48_hours, user_id)
        )

        stats = cursor.fetchone()

        # Calculate overload dates directly in SQL.
        cursor.execute(
            """
            SELECT
                DATE(due_date) AS due_day,
                COUNT(*) AS activity_count
            FROM activities
            WHERE user_id = %s
              AND status <> 'Completed'
              AND due_date IS NOT NULL
              AND DATE(due_date) >= %s
            GROUP BY DATE(due_date)
            HAVING COUNT(*) >= 2
            ORDER BY due_day ASC
            """,
            (user_id, today)
        )

        overload = [
            {
                'date': row['due_day'].isoformat(),
                'count': row['activity_count']
            }
            for row in cursor.fetchall()
        ]

        return jsonify({
            'stats': {
                'total': int(stats['total']),
                'exams': int(stats['exams']),
                'due_soon': int(stats['due_soon']),
                'completed': int(stats['completed'])
            },
            'activities': items,
            'overload': overload
        })

    finally:
        cursor.close()
        connection.close()


@bp.get('/analytics')
@login_required
def analytics():
    user_id = g.user['user_id']

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # One aggregate query for total, completed and overdue counts.
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(
                    SUM(status = 'Completed'), 0
                ) AS completed,
                COALESCE(
                    SUM(
                        due_date IS NOT NULL
                        AND due_date < %s
                        AND status <> 'Completed'
                    ), 0
                ) AS overdue
            FROM activities
            WHERE user_id = %s
            """,
            (now, user_id)
        )

        stats = cursor.fetchone()

        # Count activity types in the database.
        cursor.execute(
            """
            SELECT
                activity_type,
                COUNT(*) AS activity_count
            FROM activities
            WHERE user_id = %s
            GROUP BY activity_type
            """,
            (user_id,)
        )

        by_type = {
            row['activity_type']: int(row['activity_count'])
            for row in cursor.fetchall()
        }

        total = int(stats['total'])
        completed = int(stats['completed'])

        return jsonify({
            'total': total,
            'completed': completed,
            'pending': total - completed,
            'overdue': int(stats['overdue']),
            'completion_rate': (
                round(completed / total * 100)
                if total else 0
            ),
            'by_type': by_type
        })

    finally:
        cursor.close()
        connection.close()


@bp.get('/leaderboard')
@login_required
def leaderboard():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Aggregate XP and completion statistics in the database.
        # LEFT JOIN keeps students who have not earned XP yet.
        cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.college,
                u.department,
                COUNT(a.award_id) AS completed,
                COALESCE(SUM(a.points), 0) AS xp,
                COALESCE(
                    SUM(a.activity_type = 'Project'), 0
                ) AS projects,
                COALESCE(
                    SUM(a.activity_type = 'Exam'), 0
                ) AS exams
            FROM users AS u
            LEFT JOIN completion_awards AS a
                ON a.user_id = u.user_id
            GROUP BY
                u.user_id,
                u.name,
                u.college,
                u.department
            ORDER BY
                xp DESC,
                completed DESC,
                u.name ASC
            """
        )

        rows = cursor.fetchall()
        students = []

        for row in rows:
            xp = int(row['xp'] or 0)
            completed = int(row['completed'] or 0)
            projects = int(row['projects'] or 0)
            exams = int(row['exams'] or 0)

            badges = []

            definitions = [
                (
                    "First Step",
                    "ðŸŒ±",
                    "Complete your first activity",
                    completed >= 1
                ),
                (
                    "Focused Learner",
                    "ðŸ”¥",
                    "Complete 5 activities",
                    completed >= 5
                ),
                (
                    "Task Master",
                    "ðŸ†",
                    "Complete 10 activities",
                    completed >= 10
                ),
                (
                    "Project Finisher",
                    "ðŸš€",
                    "Complete 2 projects",
                    projects >= 2
                ),
                (
                    "Exam Champion",
                    "ðŸŽ“",
                    "Complete 2 exams",
                    exams >= 2
                ),
                (
                    "XP Champion",
                    "ðŸ’Ž",
                    "Earn 500 XP",
                    xp >= 500
                )
            ]

            for name, icon, description, earned in definitions:
                if earned:
                    badges.append({
                        'name': name,
                        'icon': icon,
                        'description': description
                    })

            students.append({
                'user_id': row['user_id'],
                'name': row.get('name') or 'Student',
                'college': row.get('college') or '',
                'department': row.get('department') or '',
                'xp': xp,
                'completed': completed,
                'projects': projects,
                'exams': exams,
                'badges': badges
            })

        # Assign ranks after sorting.
        for index, student in enumerate(students, start=1):
            student['rank'] = index

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

    finally:
        cursor.close()
        connection.close()
