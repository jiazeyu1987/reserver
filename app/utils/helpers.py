import os
import uuid
import json
from datetime import datetime
from flask import request, current_app
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
import redis

# Redis客户端
redis_client = None

def get_redis_client():
    """获取Redis客户端实例"""
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis.from_url(current_app.config.get('REDIS_URL', 'redis://localhost:6379/0'))
    return redis_client

def get_client_ip():
    """获取客户端IP地址"""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip

def allowed_file(filename, file_type):
    """检查文件类型是否允许"""
    ALLOWED_EXTENSIONS = {
        'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
        'audio': {'mp3', 'wav', 'aac', 'm4a'},
        'document': {'pdf', 'doc', 'docx', 'txt'}
    }
    
    if file_type not in ALLOWED_EXTENSIONS:
        return False
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[file_type]

def handle_file_upload(file, file_type):
    """处理文件上传"""
    if not file or not allowed_file(file.filename, file_type):
        return None
    
    try:
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # 创建上传目录
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], file_type)
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # 如果是图片，生成缩略图
        if file_type == 'image':
            generate_thumbnail(file_path)
        
        # 返回文件URL
        return f"/static/uploads/{file_type}/{unique_filename}"
    except Exception as e:
        current_app.logger.error(f"文件上传失败: {str(e)}")
        return None

def generate_thumbnail(image_path):
    """生成缩略图"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # 保存缩略图
            name, ext = os.path.splitext(image_path)
            thumbnail_path = f"{name}_thumb{ext}"
            img.save(thumbnail_path)
    except UnidentifiedImageError:
        current_app.logger.error(f"无法识别的图片文件: {image_path}")
    except Exception as e:
        current_app.logger.error(f"生成缩略图失败: {str(e)}")

def cache_key(prefix, *args):
    """生成缓存键"""
    key_parts = [prefix] + [str(arg) for arg in args]
    return ":".join(key_parts)

def set_cache(key, value, expire=3600):
    """设置缓存"""
    try:
        redis_client = get_redis_client()
        redis_client.setex(key, expire, json.dumps(value, ensure_ascii=False, default=str))
        return True
    except Exception as e:
        current_app.logger.error(f"设置缓存失败: {str(e)}")
        return False

def get_cache(key):
    """获取缓存"""
    try:
        redis_client = get_redis_client()
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        current_app.logger.error(f"获取缓存失败: {str(e)}")
        return None

def delete_cache(key):
    """删除缓存"""
    try:
        redis_client = get_redis_client()
        redis_client.delete(key)
        return True
    except Exception as e:
        current_app.logger.error(f"删除缓存失败: {str(e)}")
        return False