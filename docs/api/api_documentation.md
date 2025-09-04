# API接口文档

## 1. 认证相关接口

### 用户登录
```
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

**响应:**
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "access_token": "string",
        "refresh_token": "string",
        "user": {
            "id": 1,
            "username": "recorder001",
            "name": "张三",
            "role": "recorder",
            "avatar": "string"
        }
    }
}
```

### 刷新Token
```
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

**响应:**
```json
{
    "code": 200,
    "data": {
        "access_token": "string"
    }
}
```

## 2. 患者与家庭管理接口

### 获取记录员负责的家庭列表
```
GET /api/v1/families?page=1&limit=20&search=关键词
Authorization: Bearer <access_token>
```

**响应:**
```json
{
    "code": 200,
    "data": {
        "families": [
            {
                "id": 1,
                "family_name": "张家",
                "primary_address": "北京市朝阳区xxx",
                "contact_phone": "13800138000",
                "patient_count": 3,
                "active_subscriptions": 2
            }
        ],
        "total": 50,
        "page": 1,
        "limit": 20
    }
}
```

### 获取家庭详情
```
GET /api/v1/families/{family_id}
Authorization: Bearer <access_token>
```

**响应:**
```json
{
    "code": 200,
    "data": {
        "id": 1,
        "family_name": "张家",
        "primary_address": "北京市朝阳区xxx",
        "patients": [
            {
                "id": 1,
                "name": "张老三",
                "age": 75,
                "gender": "male",
                "relationship_to_head": "户主",
                "current_subscription": {
                    "package_name": "基础健康监护",
                    "status": "active",
                    "end_date": "2024-12-31"
                },
                "last_record": {
                    "date": "2024-01-15",
                    "notes": "血压正常，精神状态良好"
                }
            }
        ]
    }
}
```

## 3. 预约管理接口

### 获取今日预约列表
```
GET /api/v1/appointments/today
Authorization: Bearer <access_token>
```

**响应:**
```json
{
    "code": 200,
    "data": [
        {
            "id": 1,
            "patient": {
                "id": 1,
                "name": "张老三",
                "family_name": "张家",
                "address": "北京市朝阳区xxx"
            },
            "scheduled_time": "09:00",
            "status": "confirmed",
            "notes": "定期检查"
        }
    ]
}
```

### 获取预约列表
```
GET /api/v1/appointments?page=1&limit=20&status=scheduled&date_from=2024-01-01&date_to=2024-12-31
Authorization: Bearer <access_token>
```

### 创建预约
```
POST /api/v1/appointments
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "patient_id": 1,
    "scheduled_date": "2024-01-20",
    "scheduled_time": "14:00",
    "appointment_type": "regular",
    "notes": "定期健康检查"
}
```

### 更新预约
```
PUT /api/v1/appointments/{appointment_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "scheduled_date": "2024-01-21",
    "scheduled_time": "15:00",
    "status": "rescheduled",
    "notes": "用户要求改期"
}
```

### 完成预约
```
POST /api/v1/appointments/{appointment_id}/complete
Authorization: Bearer <access_token>
```

## 4. 健康记录接口

### 创建健康记录
```
POST /api/v1/health-records
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

表单字段:
- patient_id: 患者ID
- appointment_id: 预约ID（可选）
- visit_date: 拜访日期 (YYYY-MM-DD)
- visit_time: 拜访时间 (HH:MM)
- location_lat: GPS纬度（可选）
- location_lng: GPS经度（可选）
- vital_signs: 生命体征 (JSON字符串)
- symptoms: 症状记录
- notes: 记录员备注
- audio_file: 音频文件（可选）
- photos: 图片文件（可选，支持多文件）
- patient_signature: 患者签名图片（可选）
```

## 5. 医院预约接口

### 获取合作医院列表
```
GET /api/v1/hospitals?search=北京&department=内科
Authorization: Bearer <access_token>
```

**响应:**
```json
{
    "code": 200,
    "data": [
        {
            "id": 1,
            "name": "北京协和医院",
            "address": "北京市东城区帅府园一号",
            "level": "三甲",
            "departments": [
                {
                    "id": 1,
                    "name": "内科",
                    "available": true
                }
            ]
        }
    ]
}
```

### 获取医院科室列表
```
GET /api/v1/hospitals/{hospital_id}/departments
Authorization: Bearer <access_token>
```

### 获取科室医生列表
```
GET /api/v1/hospitals/{hospital_id}/departments/{department_id}/doctors
Authorization: Bearer <access_token>
```

### 创建医院预约
```
POST /api/v1/hospital-appointments
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "patient_id": 1,
    "hospital_id": 1,
    "department_id": 1,
    "doctor_id": 1,
    "appointment_date": "2024-01-20",
    "appointment_time": "14:00",
    "notes": "患者血压偏高，需要专家诊断"
}
```

### 获取医院预约详情
```
GET /api/v1/hospital-appointments/{appointment_id}
Authorization: Bearer <access_token>
```

### 更新医院预约结果
```
PUT /api/v1/hospital-appointments/{appointment_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "status": "confirmed",
    "appointment_number": "YY20240120001",
    "fee": 50.00,
    "result_notes": "预约成功，提醒患者携带身份证和医保卡"
}
```

## 6. 错误响应格式

所有API接口都遵循统一的错误响应格式：

```json
{
    "code": 400,
    "message": "错误描述信息"
}
```

### 常见错误码

- 200: 请求成功
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

## 7. 认证与权限

所有需要认证的接口都必须在请求头中包含：
```
Authorization: Bearer <access_token>
```

不同角色的权限：
- recorder (记录员): 可访问患者管理、预约管理、健康记录等核心功能
- doctor (医生): 可查看患者健康记录、下发医嘱
- admin (管理员): 可管理系统所有功能