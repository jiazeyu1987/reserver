from flask import Blueprint, jsonify, current_app
from extensions import db
import redis

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        current_app.logger.error(f"数据库连接检查失败: {str(e)}")
        db_status = 'unhealthy'
    
    try:
        # 检查Redis连接
        redis_client = redis.Redis.from_url(current_app.config['REDIS_URL'])
        redis_client.ping()
        redis_status = 'healthy'
    except Exception as e:
        current_app.logger.error(f"Redis连接检查失败: {str(e)}")
        redis_status = 'unhealthy'
    
    status = 'healthy' if db_status == 'healthy' and redis_status == 'healthy' else 'unhealthy'
    status_code = 200 if status == 'healthy' else 503
    
    return jsonify({
        'status': status,
        'database': db_status,
        'redis': redis_status,
        'timestamp': datetime.utcnow().isoformat()
    }), status_code

# 导入datetime
from datetime import datetime