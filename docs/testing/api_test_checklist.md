# API接口测试清单

## 1. 认证相关接口

- [x] POST /api/v1/auth/login - 用户登录
- [x] POST /api/v1/auth/refresh - 刷新Token
- [ ] POST /api/v1/auth/register - 用户注册
- [ ] GET /health - 健康检查

## 2. 患者与家庭管理接口

- [x] GET /api/v1/families - 获取记录员负责的家庭列表
- [x] GET /api/v1/families/{family_id} - 获取家庭详情

## 3. 预约管理接口

- [x] GET /api/v1/appointments/today - 获取今日预约列表
- [x] GET /api/v1/appointments - 获取预约列表
- [x] POST /api/v1/appointments - 创建预约
- [x] PUT /api/v1/appointments/{appointment_id} - 更新预约
- [x] POST /api/v1/appointments/{appointment_id}/complete - 完成预约

## 4. 健康记录接口

- [x] POST /api/v1/health-records - 创建健康记录

## 5. 医院预约接口

- [x] GET /api/v1/hospitals - 获取合作医院列表
- [x] GET /api/v1/hospitals/{hospital_id}/departments - 获取医院科室列表
- [x] GET /api/v1/hospitals/{hospital_id}/departments/{department_id}/doctors - 获取科室医生列表
- [x] POST /api/v1/hospital-appointments - 创建医院预约
- [x] GET /api/v1/hospital-appointments/{appointment_id} - 获取医院预约详情
- [x] PUT /api/v1/hospital-appointments/{appointment_id} - 更新医院预约结果

## 测试状态说明

- [ ] 未测试
- [x] 测试成功
- [!] 测试失败