
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from store import read_db, write_db, next_id
from utils import login_required

bp = Blueprint('activities', __name__, url_prefix='/api/activities')

VALID_TYPES = {
    'Assignment', 'Project', 'Exam', 'Lab Record', 'Other'
}

VALID_PRIORITIES = {'Low', 'Medium', 'High'}

VALID_STATUSES = {'Pending', 'In Progress', 'Completed'}


def owned(items, activity_id, user_id):
    return next(
        (
            a for a in items
            if a['activity_id'] == activity_id
            and a['user_id'] == user_id
        ),
        None
    )


@bp.get('')
@login_required
def list_activities():
    db = read_db()

    items = [
        a for a in db['activities']
        if a['user_id'] == g.user['user_id']
    ]

    items.sort(key=lambda a: a.get('due_date', ''))

    return jsonify(items)


@bp.post('')
@login_required
def create_activity():
    data = request.get_json(silent=True) or {}

    title = str(data.get('title', '')).strip()
    due_date = str(data.get('due_date', '')).strip()
    activity_type = data.get('activity_type', 'Assignment')

    if not title or not due_date or activity_type not in VALID_TYPES:
        return jsonify({
            'error': 'Title, due date and a valid activity type are required.'
        }), 400

    try:
        datetime.fromisoformat(due_date.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({
            'error': 'Due date must be a valid ISO date/time.'
        }), 400

    db = read_db()

    item = {
        'activity_id': next_id(db['activities'], 'activity_id'),
        'user_id': g.user['user_id'],
        'title': title,
        'description': str(data.get('description', '')),
        'activity_type': activity_type,
        'subject': str(data.get('subject', '')),
        'due_date': due_date,
        'priority': (
            data.get('priority')
            if data.get('priority') in VALID_PRIORITIES
            else 'Medium'
        ),
        # New activities always start as Pending.
        'status': 'Pending',
        'created_at': datetime.now(timezone.utc).isoformat()
    }

    db['activities'].append(item)
    write_db(db)

    return jsonify(item), 201


@bp.route('/<int:activity_id>', methods=['PUT', 'PATCH', 'DELETE'])
@login_required
def modify_activity(activity_id):
    db = read_db()

    item = owned(
        db['activities'],
        activity_id,
        g.user['user_id']
    )

    if not item:
        return jsonify({'error': 'Activity not found.'}), 404

    # Delete activity
    if request.method == 'DELETE':
        db['activities'] = [
            a for a in db['activities']
            if a['activity_id'] != activity_id
        ]

        write_db(db)

        return jsonify({'message': 'Activity deleted.'})

    data = request.get_json(silent=True) or {}

    allowed = {
        'title',
        'description',
        'activity_type',
        'subject',
        'due_date',
        'priority',
        'status'
    }

    was_completed = item.get('status') == 'Completed'

    # Validate and update activity fields
    for key, value in data.items():

        if key not in allowed:
            continue

        if key == 'activity_type' and value not in VALID_TYPES:
            return jsonify({'error': 'Invalid activity type.'}), 400

        if key == 'priority' and value not in VALID_PRIORITIES:
            return jsonify({'error': 'Invalid priority.'}), 400

        if key == 'status' and value not in VALID_STATUSES:
            return jsonify({'error': 'Invalid status.'}), 400

        if key == 'due_date':
            try:
                datetime.fromisoformat(
                    str(value).replace('Z', '+00:00')
                )
            except ValueError:
                return jsonify({'error': 'Invalid due date.'}), 400

        item[key] = value

    points_awarded = 0

    # Award XP only on the first transition to Completed.
    if not was_completed and item.get('status') == 'Completed':

        from gamification import award_completion

        item['completed_at'] = datetime.now(timezone.utc).isoformat()

        points_awarded = award_completion(db, item)

    write_db(db)

    return jsonify({
        'activity': item,
        'points_awarded': points_awarded
    })

