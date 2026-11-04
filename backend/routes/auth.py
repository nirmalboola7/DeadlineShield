from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from store import read_db, write_db, next_id
from utils import create_token, login_required, public_user

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.post('/register')
def register():
    data = request.get_json(silent=True) or {}
    name, email, password = (str(data.get(k, '')).strip() for k in ('name', 'email', 'password'))
    if not name or not email or len(password) < 8:
        return jsonify({'error': 'Name, valid email and a password of at least 8 characters are required.'}), 400
    db = read_db()
    if any(u['email'].lower() == email.lower() for u in db['users']):
        return jsonify({'error': 'An account with this email already exists.'}), 409
    user = {'user_id': next_id(db['users'], 'user_id'), 'name': name, 'email': email.lower(),
            'password_hash': generate_password_hash(password), 'college': data.get('college',''),
            'department': data.get('department',''), 'created_at': datetime.now(timezone.utc).isoformat()}
    db['users'].append(user); write_db(db)
    return jsonify({'token': create_token(user['user_id']), 'user': public_user(user)}), 201

@bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    email, password = str(data.get('email','')).lower().strip(), str(data.get('password',''))
    db = read_db()
    user = next((u for u in db['users'] if u['email'] == email), None)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Incorrect email or password.'}), 401
    return jsonify({'token': create_token(user['user_id']), 'user': public_user(user)})

@bp.get('/me')
@login_required
def me():
    return jsonify({'user': public_user(g.user)})

@bp.put('/profile')
@login_required
def update_profile():
    data = request.get_json(silent=True) or {}; db = read_db()
    user = next(u for u in db['users'] if u['user_id'] == g.user['user_id'])
    user['name'] = str(data.get('name', user['name'])).strip() or user['name']
    user['college'] = str(data.get('college', user.get('college',''))).strip()
    user['department'] = str(data.get('department', user.get('department',''))).strip()
    write_db(db)
    return jsonify({'user': public_user(user)})

@bp.post('/logout')
@login_required
def logout():
    # JWT is stateless in this demo. The frontend removes its token.
    return jsonify({'message': 'Signed out. Remove the token on the client.'})
