from datetime import datetime, timedelta, timezone
from collections import Counter
from flask import Blueprint, jsonify, g
from store import read_db
from utils import login_required

bp = Blueprint('dashboard', __name__, url_prefix='/api')

@bp.get('/dashboard')
@login_required
def dashboard():
    db = read_db(); items = [a for a in db['activities'] if a['user_id'] == g.user['user_id']]
    now = datetime.now(timezone.utc); due_soon = 0; dates = Counter()
    for a in items:
        try:
            due = datetime.fromisoformat(a['due_date'].replace('Z','+00:00'))
            if due.tzinfo is None: due = due.replace(tzinfo=timezone.utc)
            if now <= due <= now + timedelta(hours=48) and a['status'] != 'Completed': due_soon += 1
            if a['status'] != 'Completed' and due.date() >= now.date(): dates[due.date().isoformat()] += 1
        except (ValueError, TypeError, KeyError): pass
    overload = [{'date':d,'count':n} for d,n in dates.items() if n >= 2]
    stats = {'total':len(items),'exams':sum(1 for a in items if a['activity_type']=='Exam' and a['status']!='Completed'),
             'due_soon':due_soon,'completed':sum(1 for a in items if a['status']=='Completed')}
    items.sort(key=lambda a:a.get('due_date',''))
    return jsonify({'stats':stats,'activities':items,'overload':overload})

@bp.get('/analytics')
@login_required
def analytics():
    db=read_db(); items=[a for a in db['activities'] if a['user_id']==g.user['user_id']]
    total=len(items); completed=sum(a['status']=='Completed' for a in items)
    now=datetime.now(timezone.utc); overdue=0
    for a in items:
        try:
            due=datetime.fromisoformat(a['due_date'].replace('Z','+00:00'))
            if due.tzinfo is None: due=due.replace(tzinfo=timezone.utc)
            if due < now and a['status']!='Completed': overdue+=1
        except (ValueError,TypeError): pass
    by_type=dict(Counter(a['activity_type'] for a in items))
    return jsonify({'total':total,'completed':completed,'pending':total-completed,'overdue':overdue,
                    'completion_rate':round(completed/total*100) if total else 0,'by_type':by_type})
