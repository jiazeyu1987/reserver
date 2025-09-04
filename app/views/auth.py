from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models.user import User
from app import db
import re
import json

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        # 详细记录请求数据
        current_app.logger.info("=== 开始登录请求 ===")
        current_app.logger.info(f"请求方法: {request.method}")
        current_app.logger.info(f"请求URL: {request.url}")
        current_app.logger.info(f"请求头: {dict(request.headers)}")
        
        data = request.get_json()
        current_app.logger.info(f"请求体(原始): {request.get_data()}")
        current_app.logger.info(f"解析的JSON数据: {data}")
        
        username = data.get('username') if data else None
        password = data.get('password') if data else None
        
        current_app.logger.info(f"提取的用户名: '{username}' (类型: {type(username)})")
        current_app.logger.info(f"提取的密码: '{'*' * len(password) if password else None}' (长度: {len(password) if password else 0})")
        
        if not username or not password:
            current_app.logger.warning("用户名或密码为空")
            return jsonify({
                'code': 400,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 查找用户 - 详细日志
        current_app.logger.info(f"正在查找用户: username='{username}'")
        user = db.session.query(User).filter(
            (User.username == username) | (User.phone == username)
        ).first()
        
        if not user:
            current_app.logger.warning(f"未找到用户: '{username}'")
            # 列出所有用户进行调试
            all_users = db.session.query(User).all()
            current_app.logger.info(f"数据库中的所有用户: {[(u.username, u.phone) for u in all_users]}")
            return jsonify({
                'code': 401,
                'message': '用户名或密码错误'
            }), 401
        
        current_app.logger.info(f"找到用户: id={user.id}, username='{user.username}', phone='{user.phone}', status='{user.status}'")
        
        # 验证密码
        password_valid = user.check_password(password)
        current_app.logger.info(f"密码验证结果: {password_valid}")
        
        if not password_valid:
            current_app.logger.warning(f"用户 '{username}' 密码错误")
            return jsonify({
                'code': 401,
                'message': '用户名或密码错误'
            }), 401
        
        if user.status != 'active':
            current_app.logger.warning(f"用户 '{username}' 状态不是active: {user.status}")
            return jsonify({
                'code': 403,
                'message': '用户账户已被禁用'
            }), 403
        
        # 更新最后登录时间
        user.last_login = db.func.now()
        db.session.commit()
        current_app.logger.info(f"已更新用户 '{username}' 的最后登录时间")
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        current_app.logger.info(f"已为用户 '{username}' 创建令牌")
        
        current_app.logger.info("=== 登录成功 ===")
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
        })
    except Exception as e:
        current_app.logger.error(f"登录过程中发生异常: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500
