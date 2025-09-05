from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
from celery import Celery

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
cache = Cache()
celery = Celery()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # 加载配置
    from app.config import config
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    cache.init_app(app)
    
    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        app.logger.error("JWT token已过期")
        return {'code': 422, 'message': 'JWT token已过期'}, 422
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        from flask import request
        auth_header = request.headers.get('Authorization', 'None')
        app.logger.error(f"JWT token无效: {error}")
        app.logger.error(f"Authorization头内容: {auth_header}")
        if auth_header and 'Bearer ' in auth_header:
            token_part = auth_header.replace('Bearer ', '')
            app.logger.error(f"Token部分: {token_part[:50]}...（长度：{len(token_part)}）")
            segments = token_part.count('.')
            app.logger.error(f"Token段数: {segments + 1}")
        return {'code': 422, 'message': 'JWT token无效'}, 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        from flask import request
        auth_header = request.headers.get('Authorization', 'None')
        app.logger.error(f"缺少JWT token: {error}")
        app.logger.error(f"Authorization头内容: {auth_header}")
        return {'code': 422, 'message': '缺少JWT token'}, 422
    
    # 初始化Celery
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # 注册蓝图
    from app.views.auth import auth_bp
    from app.views.patient import patient_bp
    from app.views.appointment import appointment_bp
    from app.views.hospital import hospital_bp
    from app.views.health import health_bp
    from app.views.service_package import service_package_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(hospital_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(service_package_bp)
    
    return app