# API接口详细测试计划

## 1. 认证相关接口

### 1.1 用户登录 POST /api/v1/auth/login

**测试用例1: 正常登录**
- 输入: 正确的用户名和密码
- 期望输出: 返回200状态码，包含access_token和refresh_token

**测试用例2: 用户名错误**
- 输入: 错误的用户名，正确密码
- 期望输出: 返回401状态码，提示用户名或密码错误

**测试用例3: 密码错误**
- 输入: 正确的用户名，错误密码
- 期望输出: 返回401状态码，提示用户名或密码错误

**测试用例4: 缺少参数**
- 输入: 缺少用户名或密码
- 期望输出: 返回400状态码，提示参数缺失

### 1.2 刷新Token POST /api/v1/auth/refresh

**测试用例1: 正常刷新**
- 输入: 有效的refresh_token
- 期望输出: 返回200状态码，包含新的access_token

**测试用例2: 无效Token**
- 输入: 无效的refresh_token
- 期望输出: 返回401状态码，提示认证失败

## 2. 患者与家庭管理接口

### 2.1 获取记录员负责的家庭列表 GET /api/v1/families

**测试用例1: 正常获取**
- 输入: 有效的access_token
- 期望输出: 返回200状态码，包含家庭列表数据

**测试用例2: 无效Token**
- 输入: 无效的access_token
- 期望输出: 返回401状态码，提示认证失败

**测试用例3: 分页参数测试**
- 输入: 带page和limit参数的请求
- 期望输出: 返回正确的分页数据

### 2.2 获取家庭详情 GET /api/v1/families/{family_id}

**测试用例1: 正常获取**
- 输入: 有效的access_token和存在的family_id
- 期望输出: 返回200状态码，包含家庭详情数据

**测试用例2: 无效Token**
- 输入: 无效的access_token
- 期望输出: 返回401状态码，提示认证失败

**测试用例3: 不存在的family_id**
- 输入: 有效的access_token和不存在的family_id
- 期望输出: 返回404状态码，提示资源不存在

## 3. 预约管理接口

### 3.1 获取今日预约列表 GET /api/v1/appointments/today

**测试用例1: 正常获取**
- 输入: 有效的access_token
- 期望输出: 返回200状态码，包含今日预约列表

### 3.2 获取预约列表 GET /api/v1/appointments

**测试用例1: 正常获取**
- 输入: 有效的access_token
- 期望输出: 返回200状态码，包含预约列表

### 3.3 创建预约 POST /api/v1/appointments

**测试用例1: 正常创建**
- 输入: 有效的access_token和完整的预约信息
- 期望输出: 返回200状态码，包含创建的预约信息

**测试用例2: 参数缺失**
- 输入: 缺少必要参数的预约信息
- 期望输出: 返回400状态码，提示参数错误

### 3.4 更新预约 PUT /api/v1/appointments/{appointment_id}

**测试用例1: 正常更新**
- 输入: 有效的access_token和存在的appointment_id
- 期望输出: 返回200状态码，包含更新后的预约信息

### 3.5 完成预约 POST /api/v1/appointments/{appointment_id}/complete

**测试用例1: 正常完成**
- 输入: 有效的access_token和存在的appointment_id
- 期望输出: 返回200状态码，提示预约完成

## 4. 健康记录接口

### 4.1 创建健康记录 POST /api/v1/health-records

**测试用例1: 正常创建**
- 输入: 有效的access_token和完整的健康记录信息
- 期望输出: 返回200状态码，包含创建的健康记录信息

## 5. 医院预约接口

### 5.1 获取合作医院列表 GET /api/v1/hospitals

**测试用例1: 正常获取**
- 输入: 有效的access_token
- 期望输出: 返回200状态码，包含医院列表

### 5.2 获取医院科室列表 GET /api/v1/hospitals/{hospital_id}/departments

**测试用例1: 正常获取**
- 输入: 有效的access_token和存在的hospital_id
- 期望输出: 返回200状态码，包含科室列表

### 5.3 获取科室医生列表 GET /api/v1/hospitals/{hospital_id}/departments/{department_id}/doctors

**测试用例1: 正常获取**
- 输入: 有效的access_token、存在的hospital_id和department_id
- 期望输出: 返回200状态码，包含医生列表

### 5.4 创建医院预约 POST /api/v1/hospital-appointments

**测试用例1: 正常创建**
- 输入: 有效的access_token和完整的医院预约信息
- 期望输出: 返回200状态码，包含创建的预约信息

### 5.5 获取医院预约详情 GET /api/v1/hospital-appointments/{appointment_id}

**测试用例1: 正常获取**
- 输入: 有效的access_token和存在的appointment_id
- 期望输出: 返回200状态码，包含预约详情

### 5.6 更新医院预约结果 PUT /api/v1/hospital-appointments/{appointment_id}

**测试用例1: 正常更新**
- 输入: 有效的access_token和存在的appointment_id
- 期望输出: 返回200状态码，包含更新后的预约信息