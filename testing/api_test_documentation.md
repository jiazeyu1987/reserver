# API接口测试文档

## 1. 概述

本文档详细描述了FlaskServer项目的API接口测试方案，包括各接口的测试用例、测试方法和预期结果。

## 2. 测试环境

- Python 3.9+
- Flask 2.3+
- MySQL 8.0+
- Redis

## 3. 测试工具

- pytest (推荐)
- unittest (Python内置)
- Postman (可选)
- curl (可选)

## 4. 接口测试清单

### 4.1 认证接口 (`/api/v1/auth/`)

#### 4.1.1 用户登录 `/api/v1/auth/login` [POST]
- 测试正常登录
- 测试无效用户名/密码
- 测试禁用账户登录
- 测试缺少参数

#### 4.1.2 刷新令牌 `/api/v1/auth/refresh` [POST]
- 测试使用有效刷新令牌
- 测试使用无效刷新令牌

#### 4.1.3 用户注册 `/api/v1/auth/register` [POST]
- 测试正常注册
- 测试重复用户名
- 测试重复手机号
- 测试无效手机号格式
- 测试缺少必填字段

### 4.2 患者与家庭管理接口 (`/api/v1/families`)

#### 4.2.1 获取家庭列表 `/api/v1/families` [GET]
- 测试正常获取列表
- 测试分页功能
- 测试搜索功能
- 测试无权限访问

#### 4.2.2 获取家庭详情 `/api/v1/families/<int:family_id>` [GET]
- 测试正常获取详情
- 测试不存在的家庭ID
- 测试无权限访问其他记录员的家庭

### 4.3 预约管理接口 (`/api/v1/appointments`)

#### 4.3.1 获取今日预约列表 `/api/v1/appointments/today` [GET]
- 测试正常获取今日预约
- 测试无预约情况
- 测试无权限访问

#### 4.3.2 获取预约列表 `/api/v1/appointments` [GET]
- 测试正常获取预约列表
- 测试分页功能
- 测试状态筛选
- 测试日期范围筛选

#### 4.3.3 创建预约 `/api/v1/appointments` [POST]
- 测试正常创建预约
- 测试无效数据
- 测试缺少必填字段

#### 4.3.4 更新预约 `/api/v1/appointments/<int:appointment_id>` [PUT]
- 测试正常更新预约
- 测试更新不存在的预约
- 测试更新他人预约

#### 4.3.5 完成预约 `/api/v1/appointments/<int:appointment_id>/complete` [POST]
- 测试正常完成预约
- 测试完成不存在的预约
- 测试完成他人预约

### 4.4 健康记录接口 (`/api/v1/health-records`)

#### 4.4.1 创建健康记录 `/api/v1/health-records` [POST]
- 测试正常创建健康记录
- 测试带文件上传的健康记录
- 测试无效数据

### 4.5 医院预约接口 (`/api/v1/hospitals`, `/api/v1/hospital-appointments`)

#### 4.5.1 获取合作医院列表 `/api/v1/hospitals` [GET]
- 测试正常获取医院列表
- 测试搜索功能
- 测试科室筛选

#### 4.5.2 获取医院科室列表 `/api/v1/hospitals/<int:hospital_id>/departments` [GET]
- 测试正常获取科室列表
- 测试不存在的医院ID

#### 4.5.3 获取科室医生列表 `/api/v1/hospitals/<int:hospital_id>/departments/<int:department_id>/doctors` [GET]
- 测试正常获取医生列表
- 测试不存在的医院或科室ID

#### 4.5.4 创建医院预约 `/api/v1/hospital-appointments` [POST]
- 测试正常创建医院预约
- 测试无效数据
- 测试缺少必填字段

#### 4.5.5 获取医院预约详情 `/api/v1/hospital-appointments/<int:appointment_id>` [GET]
- 测试正常获取预约详情
- 测试不存在的预约ID
- 测试无权限访问他人预约

#### 4.5.6 更新医院预约结果 `/api/v1/hospital-appointments/<int:appointment_id>` [PUT]
- 测试正常更新预约结果
- 测试更新不存在的预约
- 测试更新他人预约

### 4.6 健康检查接口 (`/health`)

#### 4.6.1 健康检查 `/health` [GET]
- 测试数据库正常连接
- 测试Redis正常连接
- 测试服务整体健康状态

## 5. 测试数据准备

### 5.1 测试用户
- 管理员用户: admin / admin123
- 记录员用户: recorder001 / recorder123
- 医生用户: doctor001 / doctor123

### 5.2 测试数据
- 家庭数据
- 患者数据
- 预约数据
- 合作医院数据

## 6. 测试执行

### 6.1 运行所有测试
```bash
python -m pytest testing/ -v
```

### 6.2 运行特定模块测试
```bash
python -m pytest testing/test_auth.py -v
python -m pytest testing/test_patient.py -v
python -m pytest testing/test_appointment.py -v
```

## 7. 测试报告

测试结果将包含以下信息:
- 测试用例名称
- 测试执行状态 (通过/失败)
- 错误信息 (如果失败)
- 执行时间