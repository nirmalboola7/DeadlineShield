from functools import wraps
from flask import request, jsonify, g
import jwt
from config import SECRET_KEY
from store import read_db

def create_token(user_id):
    return jwt.encode({'user_id': user_id}, SECRET_KEY, algorithm='HS256')

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required.'}), 401
        try:
            payload = jwt.decode(header.split(' ', 1)[1], SECRET_KEY, algorithms=['HS256'])
            db = read_db()
            user = next((u for u in db['users'] if u['user_id'] == payload.get('user_id')), None)
            if not user:
                return jsonify({'error': 'User account not found.'}), 401
            g.user = user
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid or expired token.'}), 401
        return fn(*args, **kwargs)
    return wrapper

def public_user(user):
    return {k: user.get(k) for k in ('user_id', 'name', 'email', 'college', 'department', 'created_at')}
