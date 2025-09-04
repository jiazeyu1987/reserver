from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app import db

def recorder_required(f):
    """记录员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == int(current_user_id)).first()
        
        if not user or user.role != 'recorder':
            return jsonify({
                'code': 403,
                'message': '权限不足，需要记录员权限'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == int(current_user_id)).first()
        
        if not user or user.role != 'admin':
            return jsonify({
                'code': 403,
                'message': '权限不足，需要管理员权限'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def admin_or_recorder_required(f):
    """管理员或记录员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == int(current_user_id)).first()
        
        if not user or user.role not in ['admin', 'recorder']:
            return jsonify({
                'code': 403,
                'message': '权限不足，需要管理员或记录员权限'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    """医生权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == int(current_user_id)).first()
        
        if not user or user.role != 'doctor':
            return jsonify({
                'code': 403,
                'message': '权限不足，需要医生权限'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function