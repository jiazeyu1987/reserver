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

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        current_app.logger.info("=== 开始注册请求 ===")
        
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据无效'
            }), 400
        
        # 获取必填字段
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirmPassword', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        id_card = data.get('idCard', '').strip()
        address = data.get('address', '').strip()
        name = data.get('name', '').strip()
        
        current_app.logger.info(f"注册数据: username='{username}', email='{email}', phone='{phone}', name='{name}'")
        
        # 验证必填字段
        required_fields = {
            'username': username,
            'password': password,
            'confirmPassword': confirm_password,
            'email': email,
            'phone': phone,
            'idCard': id_card,
            'address': address,
            'name': name
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            return jsonify({
                'code': 400,
                'message': f'缺少必填字段: {", ".join(missing_fields)}'
            }), 400
        
        # 验证密码一致性
        if password != confirm_password:
            return jsonify({
                'code': 400,
                'message': '两次输入的密码不一致'
            }), 400
        
        # 验证密码强度
        if len(password) < 6:
            return jsonify({
                'code': 400,
                'message': '密码长度不能少于6位'
            }), 400
        
        # 验证邮箱格式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'code': 400,
                'message': '邮箱格式不正确'
            }), 400
        
        # 验证手机号格式
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            return jsonify({
                'code': 400,
                'message': '手机号格式不正确'
            }), 400
        
        # 验证身份证号格式
        id_card_pattern = r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]$'
        if not re.match(id_card_pattern, id_card):
            return jsonify({
                'code': 400,
                'message': '身份证号格式不正确'
            }), 400
        
        # 检查用户名是否已存在
        existing_user = db.session.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({
                'code': 400,
                'message': '用户名已存在'
            }), 400
        
        # 检查邮箱是否已存在
        existing_email = db.session.query(User).filter_by(email=email).first()
        if existing_email:
            return jsonify({
                'code': 400,
                'message': '邮箱已被注册'
            }), 400
        
        # 检查手机号是否已存在
        existing_phone = db.session.query(User).filter_by(phone=phone).first()
        if existing_phone:
            return jsonify({
                'code': 400,
                'message': '手机号已被注册'
            }), 400
        
        # 检查身份证号是否已存在
        existing_id_card = db.session.query(User).filter_by(id_card=id_card).first()
        if existing_id_card:
            return jsonify({
                'code': 400,
                'message': '身份证号已被注册'
            }), 400
        
        # 创建新用户
        new_user = User(
            username=username,
            name=name,
            phone=phone,
            email=email,
            id_card=id_card,
            address=address,
            role='recorder',  # 默认注册为记录员角色
            status='active'
        )
        new_user.set_password(password)
        
        # 保存到数据库
        db.session.add(new_user)
        db.session.commit()
        
        current_app.logger.info(f"用户注册成功: id={new_user.id}, username='{new_user.username}'")
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))
        
        current_app.logger.info("=== 注册成功 ===")
        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': new_user.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"注册过程中发生异常: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500
