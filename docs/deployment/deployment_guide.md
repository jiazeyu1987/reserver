# 部署指南

## 1. 环境要求

### 系统要求
- Linux/Windows/macOS
- Python 3.9+
- MySQL 8.0+ 或 SQLite (开发环境)
- Redis (可选，用于缓存和会话存储)

### 依赖组件
- Flask 2.3+
- SQLAlchemy 2.0+
- MySQL 8.0+ (生产环境推荐)
- Redis (可选)
- Nginx (生产环境推荐)

## 2. 本地开发环境部署

### 2.1 安装依赖
```bash
# 克隆项目代码
git clone <项目地址>
cd FlaskServer

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装Python依赖
pip install -r requirements.txt
```

### 2.2 配置数据库
```sql
-- MySQL环境下创建数据库
CREATE DATABASE recorder_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2.3 初始化数据库
```bash
# 初始化数据库表结构
flask init_db

# 插入初始数据
python final_init.py
```

### 2.4 启动开发服务器
```bash
python run.py
```

服务器将在 `http://localhost:5000` 运行。

## 3. 生产环境部署

### 3.1 使用Docker部署 (推荐)

#### 3.1.1 构建和运行
```bash
# 构建Docker镜像
docker-compose build

# 启动所有服务
docker-compose up -d
```

#### 3.1.2 环境变量配置
在生产环境中，建议通过环境变量配置敏感信息：

```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@host:port/database

# JWT密钥
JWT_SECRET_KEY=your-jwt-secret-key

# Redis配置
REDIS_URL=redis://host:port/db

# 文件上传路径
UPLOAD_FOLDER=/path/to/uploads
```

### 3.2 手动部署

#### 3.2.1 安装系统依赖
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv nginx mysql-server redis-server

# CentOS/RHEL
sudo yum install python3 python3-pip nginx mysql-server redis
```

#### 3.2.2 配置MySQL
```sql
-- 创建数据库和用户
CREATE DATABASE recorder_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'recorder'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON recorder_db.* TO 'recorder'@'localhost';
FLUSH PRIVILEGES;
```

#### 3.2.3 部署应用
```bash
# 创建应用目录
sudo mkdir -p /var/www/recorder
sudo chown $USER:$USER /var/www/recorder

# 复制应用代码
cp -r . /var/www/recorder/

# 创建虚拟环境并安装依赖
cd /var/www/recorder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 初始化数据库
flask init_db
python final_init.py
```

#### 3.2.4 配置Gunicorn
```bash
# 安装Gunicorn
pip install gunicorn

# 启动应用
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

#### 3.2.5 配置Nginx
创建Nginx配置文件 `/etc/nginx/sites-available/recorder`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/recorder/uploads/;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/recorder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 4. 配置文件说明

### 4.1 config.py
核心配置文件，包含不同环境的配置：

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost/recorder_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### 4.2 环境变量
建议在生产环境中使用环境变量：

```bash
export FLASK_ENV=production
export DATABASE_URL=mysql+pymysql://user:password@host:port/database
export JWT_SECRET_KEY=your-jwt-secret-key
export REDIS_URL=redis://host:port/db
export UPLOAD_FOLDER=/path/to/uploads
```

## 5. 数据库迁移

使用Flask-Migrate进行数据库迁移：

```bash
# 初始化迁移仓库
flask db init

# 创建迁移脚本
flask db migrate -m "描述信息"

# 执行迁移
flask db upgrade
```

## 6. 备份与恢复

### 6.1 数据库备份
```bash
# MySQL备份
mysqldump -u user -p recorder_db > backup.sql

# SQLite备份
cp recorder.db recorder_backup.db
```

### 6.2 文件备份
```bash
# 备份上传文件
tar -czf uploads_backup.tar.gz uploads/
```

## 7. 监控与日志

### 7.1 日志配置
在生产环境中，建议配置日志轮转：

```python
# logging.conf
[loggers]
keys=root

[handlers]
keys=rotatingFileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=rotatingFileHandler

[handler_rotatingFileHandler]
class=handlers.RotatingFileHandler
level=INFO
formatter=simpleFormatter
args=('app.log', 'a', 10*1024*1024, 5)
```

### 7.2 健康检查
```bash
# 检查应用健康状态
curl http://localhost:5000/health
```

## 8. 安全配置

### 8.1 HTTPS配置
建议使用Let's Encrypt配置HTTPS：

```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com
```

### 8.2 防火墙配置
```bash
# Ubuntu/Debian
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 9. 性能优化

### 9.1 数据库优化
```sql
-- 创建索引优化查询性能
CREATE INDEX idx_patients_family_id ON patients(family_id);
CREATE INDEX idx_health_records_patient_date ON health_records(patient_id, visit_date DESC);
CREATE INDEX idx_appointments_recorder_date ON appointments(recorder_id, scheduled_date);
```

### 9.2 缓存配置
```python
# Redis缓存配置
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = os.environ.get('REDIS_URL')
CACHE_DEFAULT_TIMEOUT = 300
```

## 10. 故障排除

### 10.1 常见问题

#### 数据库连接失败
检查数据库服务是否运行，配置是否正确。

#### 权限错误
确保应用有足够的权限访问数据库和文件系统。

#### 内存不足
调整Gunicorn工作进程数量和应用内存使用。

### 10.2 日志查看
```bash
# 查看应用日志
tail -f app.log

# 查看系统日志
journalctl -u nginx
journalctl -u mysql
```