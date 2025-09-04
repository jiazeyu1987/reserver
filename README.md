# 记录员小程序后端服务

基于Flask和MySQL的后端服务，为上门医疗服务中的护理人员提供专业工作平台。

## 功能特性

- 患者家庭管理
- 灵活预约管理
- 套餐与服务管理
- 人员管理与交接
- 风险控制与证据保全
- 医疗协作平台
- 用户预约挂号系统

## 技术栈

- **Web框架**: Flask 2.3+
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy
- **认证**: Flask-JWT-Extended
- **缓存**: Redis
- **消息队列**: Celery + Redis
- **部署**: Docker + Docker Compose

## 快速开始

### 环境要求

- Python 3.9+
- MySQL 8.0+
- Redis
- Docker (可选，推荐)

### 本地开发环境搭建

1. 克隆项目代码
```bash
git clone <项目地址>
cd FlaskServer
```

2. 创建虚拟环境并安装依赖
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

3. 配置数据库
确保MySQL服务运行，并创建数据库：
```sql
CREATE DATABASE recorder_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. 初始化数据库
```bash
flask init_db
python init_db.py
```

5. 启动服务
```bash
python run.py
```

服务将在 `http://localhost:5000` 运行。

### Docker部署

使用Docker Compose一键部署：

```bash
docker-compose up -d
```

## API文档

### 认证相关

#### 用户登录
```
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

#### 刷新Token
```
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

### 患者与家庭管理

#### 获取记录员负责的家庭列表
```
GET /api/v1/families?page=1&limit=20&search=关键词
Authorization: Bearer <access_token>
```

#### 获取家庭详情
```
GET /api/v1/families/{family_id}
Authorization: Bearer <access_token>
```

### 预约管理

#### 获取今日预约列表
```
GET /api/v1/appointments/today
Authorization: Bearer <access_token>
```

#### 创建健康记录
```
POST /api/v1/health-records
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

### 医院预约

#### 获取合作医院列表
```
GET /api/v1/hospitals?search=北京&department=内科
Authorization: Bearer <access_token>
```

#### 创建医院预约
```
POST /api/v1/hospital-appointments
Authorization: Bearer <access_token>
```

## 数据库设计

### 核心表结构

1. **用户表 (users)** - 系统用户信息
2. **记录员表 (recorders)** - 记录员详细信息
3. **医生表 (doctors)** - 医生详细信息
4. **家庭表 (families)** - 患者家庭信息
5. **患者表 (patients)** - 患者基本信息
6. **服务套餐表 (service_packages)** - 服务套餐定义
7. **患者订阅表 (patient_subscriptions)** - 患者套餐订阅
8. **预约表 (appointments)** - 上门服务预约
9. **健康记录表 (health_records)** - 健康检查记录
10. **医嘱表 (medical_orders)** - 医生医嘱
11. **合作医院表 (partner_hospitals)** - 合作医院信息
12. **医院科室表 (hospital_departments)** - 医院科室信息
13. **医院医生表 (hospital_doctors)** - 医院医生信息
14. **医院预约表 (hospital_appointments)** - 医院预约信息

## 项目结构

```
FlaskServer/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   ├── health_record.py
│   │   └── hospital.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   ├── hospital.py
│   │   └── health.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── patient_service.py
│   │   ├── appointment_service.py
│   │   └── hospital_service.py
│   └── utils/
│       ├── __init__.py
│       ├── decorators.py
│       ├── validators.py
│       └── helpers.py
├── extensions.py
├── run.py
├── init_db.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 开发指南

### 添加新的API接口

1. 在 `app/views/` 目录下创建对应的视图文件
2. 在 `app/services/` 目录下创建业务逻辑服务
3. 在 `app/models/` 目录下创建或修改数据模型
4. 在 `app/__init__.py` 中注册新的蓝图

### 数据库迁移

使用Flask-Migrate进行数据库迁移：

```bash
# 初始化迁移仓库
flask db init

# 创建迁移脚本
flask db migrate -m "描述信息"

# 执行迁移
flask db upgrade
```

## 测试账号

系统初始化时会创建以下测试账号：

- 管理员: admin / admin123
- 记录员: recorder001 / recorder123
- 医生: doctor001 / doctor123

## 安全说明

- 所有API接口都需要JWT Token认证
- 密码使用SHA256加密存储
- 敏感操作需要相应权限验证
- 支持HTTPS部署

## 许可证

MIT License