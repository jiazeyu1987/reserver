# 安全指南

## 1. 概述

本文档描述了记录员小程序后端服务的安全策略、最佳实践和防护措施，确保系统符合医疗数据隐私保护法规和行业安全标准。

## 2. 认证与授权

### 2.1 用户认证
系统采用JWT (JSON Web Token) 进行用户认证：

1. **登录认证**: 用户通过用户名/手机号和密码进行认证
2. **令牌生成**: 成功认证后生成访问令牌和刷新令牌
3. **令牌有效期**: 
   - 访问令牌: 2小时
   - 刷新令牌: 30天
4. **令牌刷新**: 通过刷新令牌获取新的访问令牌

### 2.2 角色权限控制
系统支持三种用户角色：

1. **记录员 (recorder)**: 一线护理人员，可访问核心业务功能
2. **医生 (doctor)**: 医疗专业人员，可查看健康记录和下发医嘱
3. **管理员 (admin)**: 系统管理者，拥有所有权限

### 2.3 权限装饰器
使用装饰器实现细粒度权限控制：

```python
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

def recorder_required(f):
    """记录员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == current_user_id).first()
        
        if not user or user.role != 'recorder':
            return jsonify({
                'code': 403,
                'message': '权限不足，需要记录员权限'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function
```

## 3. 数据加密

### 3.1 密码加密
使用 Werkzeug 的安全哈希函数存储用户密码：

```python
from werkzeug.security import generate_password_hash, check_password_hash

# 密码加密
password_hash = generate_password_hash(password)

# 密码验证
is_valid = check_password_hash(password_hash, password)
```

### 3.2 敏感数据加密
对于特别敏感的数据，使用 cryptography 库进行加密：

```python
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, password=None):
        if password is None:
            password = os.environ.get('ENCRYPTION_KEY', 'default-key').encode()
        
        salt = b'stable_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher_suite = Fernet(key)
    
    def encrypt(self, data):
        """加密数据"""
        if isinstance(data, str):
            data = data.encode()
        encrypted_data = self.cipher_suite.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data):
        """解密数据"""
        encrypted_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        return decrypted_data.decode()
```

## 4. 数据传输安全

### 4.1 HTTPS强制使用
在生产环境中强制使用HTTPS协议：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # 强制HTTPS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

### 4.2 安全头设置
在响应中添加安全头：

```python
@app.after_request
def after_request(response):
    # 防止MIME类型嗅探
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # 防止点击劫持
    response.headers['X-Frame-Options'] = 'DENY'
    
    # XSS防护
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 强制HTTPS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response
```

## 5. 输入验证与防护

### 5.1 SQL注入防护
使用ORM查询而不是原生SQL，防止SQL注入攻击：

```python
# 安全的做法 - 使用ORM
user = db.session.query(User).filter(User.username == username).first()

# 危险的做法 - 字符串拼接SQL
# db.session.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

### 5.2 XSS防护
对用户输入进行转义处理：

```python
from markupsafe import escape

def sanitize_input(input_text):
    """清理用户输入，防止XSS攻击"""
    return escape(input_text)
```

### 5.3 CSRF防护
使用Flask-WTF提供的CSRF保护：

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# 在表单中包含CSRF令牌
<form method="POST">
    {{ form.csrf_token }}
    <!-- 表单字段 -->
</form>
```

## 6. 文件上传安全

### 6.1 文件类型验证
严格验证上传文件类型：

```python
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
```

### 6.2 文件大小限制
限制上传文件大小：

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

### 6.3 文件存储安全
将上传文件存储在安全目录中，并使用随机文件名：

```python
import uuid
from werkzeug.utils import secure_filename

def handle_file_upload(file, file_type):
    """安全处理文件上传"""
    if not file or not allowed_file(file.filename, file_type):
        return None
    
    # 生成唯一文件名
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    
    # 创建上传目录
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], file_type)
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    # 返回文件URL
    return f"/static/uploads/{file_type}/{unique_filename}"
```

## 7. API安全

### 7.1 速率限制
实施API调用速率限制：

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route("/api/v1/data")
@limiter.limit("10 per minute")
def get_data():
    return jsonify({"data": "sensitive information"})
```

### 7.2 请求频率控制
```python
class SecurityMiddleware:
    def check_rate_limit(self):
        """检查请求频率限制"""
        client_ip = request.remote_addr
        cache_key = f"rate_limit:{client_ip}"
        
        # 获取当前请求数
        current_requests = cache.get(cache_key) or 0
        
        # 每分钟最多100次请求
        if current_requests >= 100:
            return False
        
        # 增加请求计数
        cache.set(cache_key, current_requests + 1, timeout=60)
        return True
```

## 8. 数据库安全

### 8.1 连接安全
使用安全的数据库连接字符串：

```python
# 使用环境变量存储数据库凭证
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'mysql+pymysql://user:password@localhost/recorder_db'
```

### 8.2 查询安全
使用参数化查询防止SQL注入：

```python
# 安全的查询方式
user = db.session.query(User).filter(User.username == username).first()

# 避免字符串拼接
# user = db.session.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

## 9. 日志与审计

### 9.1 操作日志记录
记录所有重要操作：

```python
class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    operation_type = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer)
    operation_details = db.Column(db.Text)  # JSON格式存储操作详情
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def log_operation(operation_type, resource_type):
    """操作日志装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # 记录操作日志
            try:
                user_id = get_jwt_identity()
                log = OperationLog(
                    user_id=user_id,
                    operation_type=operation_type,
                    resource_type=resource_type,
                    operation_details=json.dumps({
                        'url': request.url,
                        'method': request.method,
                        'args': request.args.to_dict(),
                        'status_code': result[1] if isinstance(result, tuple) else 200
                    }, ensure_ascii=False),
                    ip_address=get_client_ip(),
                    user_agent=request.headers.get('User-Agent')
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f"操作日志记录失败: {str(e)}")
            
            return result
        return decorated_function
    return decorator
```

### 9.2 安全事件日志
记录安全相关事件：

```python
import logging

# 配置安全日志
security_logger = logging.getLogger('security')
security_handler = logging.FileHandler('security.log')
security_handler.setLevel(logging.WARNING)
security_logger.addHandler(security_handler)

def log_security_event(event_type, details):
    """记录安全事件"""
    security_logger.warning(f"安全事件: {event_type} - {details}")
```

## 10. 隐私保护

### 10.1 数据最小化
只收集和存储业务必需的用户数据：

```python
class Patient(db.Model):
    __tablename__ = 'patients'
    
    # 只存储必要的医疗信息
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum('male', 'female'), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20))  # 可选
    medical_history = db.Column(db.Text)  # 敏感信息加密存储
```

### 10.2 数据保留策略
实施数据保留和删除策略：

```python
def cleanup_old_data():
    """清理过期数据"""
    from datetime import datetime, timedelta
    
    # 删除一年前的旧日志
    cutoff_date = datetime.now() - timedelta(days=365)
    old_logs = db.session.query(OperationLog).filter(
        OperationLog.created_at < cutoff_date
    )
    old_logs.delete()
    db.session.commit()
```

## 11. 安全监控

### 11.1 异常检测
监控异常行为模式：

```python
def detect_suspicious_activity():
    """检测可疑活动"""
    # 检测SQL注入模式
    dangerous_patterns = [
        r"(\b(union|select|insert|delete|update|drop|create|alter)\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bor\b.*=.*\bor\b)",
        r"(\band\b.*=.*\band\b)"
    ]
    
    query_string = request.query_string.decode().lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, query_string, re.IGNORECASE):
            log_security_event("SQL注入尝试", f"可疑查询: {query_string}")
            return True
    
    return False
```

### 11.2 定期安全检查
实施定期安全检查任务：

```python
@celery.task
def security_audit():
    """安全审计任务"""
    # 检查弱密码
    weak_password_users = check_weak_passwords()
    
    # 检查未授权访问
    unauthorized_access_attempts = check_unauthorized_access()
    
    # 生成安全报告
    generate_security_report(weak_password_users, unauthorized_access_attempts)
```

## 12. 应急响应

### 12.1 安全事件响应流程
1. **检测**: 系统自动检测或用户报告安全事件
2. **评估**: 安全团队评估事件严重程度
3. **遏制**: 立即采取措施防止事件扩大
4. **调查**: 深入调查事件原因和影响范围
5. **恢复**: 修复漏洞，恢复正常服务
6. **总结**: 编写事件报告，改进安全措施

### 12.2 数据泄露应急处理
```python
def handle_data_breach(breached_data):
    """处理数据泄露事件"""
    # 1. 立即隔离受影响的系统
    isolate_affected_systems()
    
    # 2. 通知相关用户
    notify_affected_users(breached_data)
    
    # 3. 报告监管部门
    report_to_regulators()
    
    # 4. 启动调查
    start_investigation()
    
    # 5. 加强安全措施
    enhance_security_measures()
```

## 13. 合规性

### 13.1 医疗数据隐私法规
确保符合相关医疗数据隐私保护法规：

1. **数据加密**: 所有敏感数据必须加密存储
2. **访问控制**: 严格的权限管理和访问日志
3. **数据最小化**: 只收集业务必需的数据
4. **用户同意**: 明确告知数据使用目的并获得用户同意
5. **数据保留**: 实施合理的数据保留和删除策略

### 13.2 定期合规检查
```python
@celery.task
def compliance_check():
    """合规性检查任务"""
    # 检查数据加密状态
    check_data_encryption()
    
    # 检查访问日志完整性
    check_access_logs()
    
    # 检查用户同意记录
    check_user_consent()
    
    # 生成合规报告
    generate_compliance_report()
```