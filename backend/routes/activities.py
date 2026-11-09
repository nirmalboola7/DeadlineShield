
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, g

from store import (
    get_connection,
    to_mysql_datetime,
    to_json_datetime
)
from utils import login_required

bp = Blueprint('activities', __name__, url_prefix='/api/activities')

VALID_TYPES = {
    'Assignment', 'Project', 'Exam', 'Lab Record', 'Other'
}

VALID_PRIORITIES = {'Low', 'Medium', 'High'}

VALID_STATUSES = {'Pending', 'In Progress', 'Completed'}

ALLOWED_FIELDS = {
    'title',
    'description',
    'activity_type',
    'subject',
    'due_date',
    'priority',
    'status'
}


def serialize_activity(item):
    """Convert database datetime values into JSON-friendly strings."""

    if not item:
        return item

    result = dict(item)

    for field in ('due_date', 'created_at', 'completed_at'):
        if field in result:
            result[field] = to_json_datetime(result[field])

    return result


def validate_due_date(value):
    """Validate and convert an ISO date into a MySQL UTC datetime."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError("Due date is required.")

    try:
        parsed = datetime.fromisoformat(
            value.strip().replace('Z', '+00:00')
        )
        return to_mysql_datetime(parsed)

    except (ValueError, TypeError):
        raise ValueError("Due date must be a valid ISO date/time.")


@bp.get('')
@login_required
def list_activities():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM activities
            WHERE user_id = %s
            ORDER BY due_date ASC, activity_id DESC
            """,
            (g.user['user_id'],)
        )

        items = cursor.fetchall()

        return jsonify([
            serialize_activity(item)
            for item in items
        ])

    finally:
        cursor.close()
        connection.close()


@bp.post('')
@login_required
def create_activity():
    data = request.get_json(silent=True) or {}

    title = str(data.get('title', '')).strip()
    activity_type = data.get('activity_type', 'Assignment')

    if not title:
        return jsonify({'error': 'Title is required.'}), 400

    if not isinstance(activity_type, str) or activity_type not in VALID_TYPES:
        return jsonify({'error': 'Invalid activity type.'}), 400

    try:
        due_date = validate_due_date(data.get('due_date'))
    except ValueError as error:
        return jsonify({'error': str(error)}), 400

    priority = data.get('priority', 'Medium')

    if priority not in VALID_PRIORITIES:
        priority = 'Medium'

    created_at = datetime.now(timezone.utc).replace(tzinfo=None)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        cursor.execute(
            """
            INSERT INTO activities (
                user_id,
                title,
                description,
                activity_type,
                subject,
                due_date,
                priority,
                status,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                g.user['user_id'],
                title,
                str(data.get('description') or ''),
                activity_type,
                str(data.get('subject') or ''),
                due_date,
                priority,
                'Pending',
                created_at
            )
        )

        activity_id = cursor.lastrowid

        cursor.execute(
            """
            SELECT *
            FROM activities
            WHERE activity_id = %s AND user_id = %s
            """,
            (activity_id, g.user['user_id'])
        )

        item = cursor.fetchone()

        connection.commit()

        return jsonify(serialize_activity(item)), 201

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


@bp.route('/<int:activity_id>', methods=['PUT', 'PATCH', 'DELETE'])
@login_required
def modify_activity(activity_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        # Lock this user's activity while it is being modified.
        cursor.execute(
            """
            SELECT *
            FROM activities
            WHERE activity_id = %s AND user_id = %s
            FOR UPDATE
            """,
            (activity_id, g.user['user_id'])
        )

        item = cursor.fetchone()

        if not item:
            connection.rollback()
            return jsonify({'error': 'Activity not found.'}), 404

        if request.method == 'DELETE':
            cursor.execute(
                """
                DELETE FROM activities
                WHERE activity_id = %s AND user_id = %s
                """,
                (activity_id, g.user['user_id'])
            )

            connection.commit()

            return jsonify({'message': 'Activity deleted.'})

        data = request.get_json(silent=True) or {}

        was_completed = item.get('status') == 'Completed'

        updates = {}

        for key, value in data.items():

            if key not in ALLOWED_FIELDS:
                continue

            if key == 'title':
                value = str(value or '').strip()

                if not value:
                    connection.rollback()
                    return jsonify({'error': 'Title cannot be empty.'}), 400

            elif key == 'activity_type':
                if not isinstance(value, str) or value not in VALID_TYPES:
                    connection.rollback()
                    return jsonify({'error': 'Invalid activity type.'}), 400

            elif key == 'priority':
                if value not in VALID_PRIORITIES:
                    connection.rollback()
                    return jsonify({'error': 'Invalid priority.'}), 400

            elif key == 'status':
                if value not in VALID_STATUSES:
                    connection.rollback()
                    return jsonify({'error': 'Invalid status.'}), 400

            elif key == 'due_date':
                try:
                    value = validate_due_date(value)
                except ValueError as error:
                    connection.rollback()
                    return jsonify({'error': str(error)}), 400

            elif key in ('description', 'subject'):
                value = str(value or '')

            updates[key] = value

        item.update(updates)

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Record the first transition to Completed.
        if not was_completed and item.get('status') == 'Completed':
            item['completed_at'] = now
            updates['completed_at'] = now

        if updates:
            set_clause = ', '.join(
                f'`{column}` = %s'
                for column in updates
            )

            values = [
                to_mysql_datetime(value)
                if column in ('due_date', 'completed_at')
                else value
                for column, value in updates.items()
            ]

            values.extend([
                activity_id,
                g.user['user_id']
            ])

            cursor.execute(
                f"""
                UPDATE activities
                SET {set_clause}
                WHERE activity_id = %s AND user_id = %s
                """,
                values
            )

        points_awarded = 0

        # Award XP only on the first completion.
        if not was_completed and item.get('status') == 'Completed':

            from gamification import calculate_points

            # Use ISO strings for the existing XP calculation.
            points = calculate_points({
                **item,
                'due_date': to_json_datetime(item.get('due_date')),
                'completed_at': to_json_datetime(item.get('completed_at'))
            })

            cursor.execute(
                """
                SELECT award_id
                FROM completion_awards
                WHERE activity_id = %s
                LIMIT 1
                """,
                (activity_id,)
            )

            existing_award = cursor.fetchone()

            if not existing_award:
                cursor.execute(
                    """
                    INSERT INTO completion_awards (
                        activity_id,
                        user_id,
                        activity_type,
                        points,
                        awarded_at
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        activity_id,
                        g.user['user_id'],
                        item.get('activity_type'),
                        points,
                        now
                    )
                )

                points_awarded = points

        # Fetch the final database version.
        cursor.execute(
            """
            SELECT *
            FROM activities
            WHERE activity_id = %s AND user_id = %s
            """,
            (activity_id, g.user['user_id'])
        )

        updated_item = cursor.fetchone()

        connection.commit()

        return jsonify({
            'activity': serialize_activity(updated_item),
            'points_awarded': points_awarded
        })

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
