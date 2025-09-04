from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models.user import User
from app import db
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'code': 400,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 查找用户
        user = db.session.query(User).filter(
            (User.username == username) | (User.phone == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'code': 401,
                'message': '用户名或密码错误'
            }), 401
        
        if user.status != 'active':
            return jsonify({
                'code': 403,
                'message': '用户账户已被禁用'
            }), 403
        
        # 更新最后登录时间
        user.last_login = db.func.now()
        db.session.commit()
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
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
        current_app.logger.error(f"登录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'code': 200,
            'data': {
                'access_token': new_token
            }
        })
    except Exception as e:
        current_app.logger.error(f"刷新令牌失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册（仅用于开发测试）"""
    try:
        data = request.get_json()
        username = data.get('username')
        phone = data.get('phone')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'recorder')
        
        # 验证输入
        if not username or not phone or not password or not name:
            return jsonify({
                'code': 400,
                'message': '所有字段都是必填的'
            }), 400
        
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify({
                'code': 400,
                'message': '手机号格式不正确'
            }), 400
        
        # 检查用户名是否已存在
        if db.session.query(User).filter(User.username == username).first():
            return jsonify({
                'code': 400,
                'message': '用户名已存在'
            }), 400
        
        # 检查手机号是否已存在
        if db.session.query(User).filter(User.phone == phone).first():
            return jsonify({
                'code': 400,
                'message': '手机号已存在'
            }), 400
        
        # 创建新用户
        user = User(
            username=username,
            phone=phone,
            role=role,
            name=name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': {
                'user_id': user.id
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"注册失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500