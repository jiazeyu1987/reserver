# 开发指南

## 1. 项目结构

```
FlaskServer/
├── app/                 # Flask应用核心代码
│   ├── __init__.py      # 应用初始化
│   ├── config.py        # 配置文件
│   ├── models/          # 数据库模型
│   ├── views/           # API视图
│   ├── services/        # 业务逻辑层
│   └── utils/           # 工具类和装饰器
├── docs/                # 项目文档
├── tests/               # 测试代码
├── migrations/          # 数据库迁移脚本
├── uploads/             # 上传文件目录
├── extensions.py        # Flask扩展初始化
├── run.py              # 应用启动文件
├── init_db.py          # 数据库初始化脚本
├── requirements.txt    # 依赖包列表
├── Dockerfile          # Docker配置
├── docker-compose.yml  # Docker Compose配置
└── README.md           # 项目说明文档
```

## 2. 开发环境搭建

### 2.1 克隆项目
```bash
git clone <项目地址>
cd FlaskServer
```

### 2.2 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2.3 安装依赖
```bash
pip install -r requirements.txt
```

### 2.4 数据库初始化
```bash
# 初始化数据库表结构
flask init_db

# 插入测试数据
python final_init.py
```

### 2.5 启动开发服务器
```bash
python run.py
```

## 3. 代码规范

### 3.1 Python代码规范
遵循PEP 8代码规范：

1. 缩进使用4个空格
2. 行长度不超过79个字符
3. 导入语句分组排序
4. 类名使用CamelCase
5. 函数和变量名使用snake_case

### 3.2 命名规范
```python
# 类名 - CamelCase
class UserService:
    pass

# 函数名 - snake_case
def get_user_by_id(user_id):
    pass

# 常量 - UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# 私有属性 - 下划线前缀
class User:
    def __init__(self):
        self._private_field = None
```

### 3.3 注释规范
```python
def calculate_age(birth_date):
    """
    计算用户年龄
    
    Args:
        birth_date (date): 用户出生日期
        
    Returns:
        int: 用户年龄
        
    Raises:
        ValueError: 当birth_date为未来日期时
    """
    if birth_date > datetime.date.today():
        raise ValueError("出生日期不能是未来日期")
    
    # 计算年龄逻辑
    today = datetime.date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age
```

## 4. 添加新功能

### 4.1 创建新模型
在 `app/models/` 目录下创建新模型文件：

```python
# app/models/example.py
from app import db
from datetime import datetime

class ExampleModel(db.Model):
    __tablename__ = 'example_table'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }
```

### 4.2 创建新服务
在 `app/services/` 目录下创建业务逻辑：

```python
# app/services/example_service.py
from app.models.example import ExampleModel
from app import db

class ExampleService:
    @staticmethod
    def create_example(name):
        """创建示例记录"""
        try:
            example = ExampleModel(name=name)
            db.session.add(example)
            db.session.commit()
            return example
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_example_by_id(example_id):
        """根据ID获取示例记录"""
        return db.session.query(ExampleModel).filter(
            ExampleModel.id == example_id
        ).first()
```

### 4.3 创建新API视图
在 `app/views/` 目录下创建API端点：

```python
# app/views/example.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.example_service import ExampleService
from app.utils.decorators import recorder_required

example_bp = Blueprint('example', __name__, url_prefix='/api/v1')

@example_bp.route('/examples', methods=['POST'])
@jwt_required()
@recorder_required
def create_example():
    """创建示例记录"""
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({
                'code': 400,
                'message': '名称不能为空'
            }), 400
        
        example = ExampleService.create_example(name)
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': example.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"创建示例记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500
```

### 4.4 注册新蓝图
在 `app/__init__.py` 中注册新蓝图：

```python
def create_app(config_name='default'):
    # ... 其他代码 ...
    
    # 注册蓝图
    from app.views.example import example_bp
    app.register_blueprint(example_bp)
    
    return app
```

## 5. 数据库迁移

### 5.1 初始化迁移
```bash
flask db init
```

### 5.2 创建迁移脚本
```bash
flask db migrate -m "添加示例表"
```

### 5.3 执行迁移
```bash
flask db upgrade
```

## 6. 测试

### 6.1 单元测试
在 `tests/` 目录下编写单元测试：

```python
# tests/test_example_service.py
import unittest
from app import create_app, db
from app.services.example_service import ExampleService

class TestExampleService(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_example(self):
        """测试创建示例记录"""
        example = ExampleService.create_example('测试示例')
        self.assertIsNotNone(example.id)
        self.assertEqual(example.name, '测试示例')
```

### 6.2 API测试
```python
# tests/test_example_api.py
import json
import unittest
from app import create_app, db

class TestExampleAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_example_api(self):
        """测试创建示例API"""
        response = self.client.post('/api/v1/examples',
                                  data=json.dumps({'name': '测试示例'}),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['data']['name'], '测试示例')
```

### 6.3 运行测试
```bash
# 运行所有测试
python -m unittest discover tests/

# 运行特定测试
python -m unittest tests.test_example_service
```

## 7. 错误处理

### 7.1 统一错误响应格式
```python
from flask import jsonify

def handle_validation_error(error):
    """处理验证错误"""
    return jsonify({
        'code': 400,
        'message': '请求参数验证失败',
        'details': str(error)
    }), 400

def handle_database_error(error):
    """处理数据库错误"""
    return jsonify({
        'code': 500,
        'message': '数据库操作失败'
    }), 500
```

### 7.2 日志记录
```python
import logging
from flask import current_app

def log_error(error, context=None):
    """记录错误日志"""
    current_app.logger.error(f"错误: {str(error)}", extra={
        'context': context or {}
    })
```

## 8. 性能优化

### 8.1 数据库查询优化
```python
# 使用索引和预加载
from sqlalchemy.orm import joinedload

def get_user_with_profiles(user_id):
    return db.session.query(User)\
        .options(joinedload(User.profiles))\
        .filter(User.id == user_id)\
        .first()
```

### 8.2 缓存策略
```python
from flask_caching import Cache

cache = Cache()

@cache.memoize(timeout=300)
def get_expensive_data(user_id):
    """缓存昂贵的计算结果"""
    # 复杂计算逻辑
    return result
```

## 9. 安全最佳实践

### 9.1 输入验证
```python
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
```

### 9.2 SQL注入防护
```python
# 使用ORM查询而不是原生SQL
# 好的做法
user = db.session.query(User).filter(User.username == username).first()

# 避免的做法
# db.session.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

### 9.3 XSS防护
```python
from markupsafe import escape

def sanitize_input(input_text):
    """清理用户输入"""
    return escape(input_text)
```

## 10. 调试技巧

### 10.1 启用调试模式
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

### 10.2 使用Flask调试器
```python
from flask import Flask
import pdb

app = Flask(__name__)

@app.route('/debug')
def debug_endpoint():
    pdb.set_trace()  # 设置断点
    return "调试中"
```

### 10.3 日志调试
```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 在代码中添加调试日志
app.logger.debug(f"调试信息: {variable}")
```