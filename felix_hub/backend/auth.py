import os
import jwt
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

def generate_jwt_token(mechanic_id):
    payload = {
        'mechanic_id': mechanic_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Требуется авторизация'}), 401
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.mechanic_id = payload['mechanic_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Токен истёк'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Недействительный токен'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def get_jwt_identity():
    return request.mechanic_id
