from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app import db

def recorder_required(f):
    """记录员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        
        if not current_user_id:
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            user_id = int(current_user_id)
        except (ValueError, TypeError) as e:
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
            
        user = db.session.query(User).filter(User.id == user_id).first()
        
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
        if not current_user_id:
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            user_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
            
        user = db.session.query(User).filter(User.id == user_id).first()
        
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
        current_app.logger.info(f"进入admin_or_recorder_required装饰器，函数名: {f.__name__}")
        
        current_user_id = get_jwt_identity()
        current_app.logger.info(f"admin_or_recorder_required - JWT identity: {current_user_id}")
        
        if not current_user_id:
            current_app.logger.error("admin_or_recorder_required - JWT token无效")
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            user_id = int(current_user_id)
            current_app.logger.info(f"admin_or_recorder_required - 转换后的user_id: {user_id}")
        except (ValueError, TypeError) as e:
            current_app.logger.error(f"admin_or_recorder_required - 用户ID格式错误: {current_user_id}, 错误: {str(e)}")
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
            
        user = db.session.query(User).filter(User.id == user_id).first()
        current_app.logger.info(f"admin_or_recorder_required - 查询到的用户: {user}, 角色: {user.role if user else 'None'}")
        
        if not user or user.role not in ['admin', 'recorder']:
            current_app.logger.error(f"admin_or_recorder_required - 权限不足，用户角色: {user.role if user else 'None'}")
            return jsonify({
                'code': 403,
                'message': '权限不足，需要管理员或记录员权限'
            }), 403
        
        current_app.logger.info("admin_or_recorder_required - 权限验证通过")
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    """医生权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            user_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
            
        user = db.session.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'doctor':
            return jsonify({
                'code': 403,
                'message': '权限不足，需要医生权限'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function