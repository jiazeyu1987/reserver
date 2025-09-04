# API接口测试目录

## 目录结构

```
testing/
├── api_test_documentation.md  # API测试文档
├── run_tests.py               # 测试运行器
├── test_auth.py              # 认证接口测试
├── test_patient.py           # 患者管理接口测试
├── test_appointment.py       # 预约管理接口测试
└── test_hospital.py          # 医院预约接口测试
```

## 测试运行方法

### 1. 运行所有测试
```bash
python testing/run_tests.py
```

### 2. 运行单个测试模块
```bash
python testing/test_auth.py
python testing/test_patient.py
python testing/test_appointment.py
python testing/test_hospital.py
```

### 3. 使用pytest运行测试（需要安装pytest）
```bash
pip install pytest

# 运行所有测试
pytest testing/ -v

# 运行特定测试文件
pytest testing/test_auth.py -v
```

## 测试环境要求

1. Python 3.9+
2. 项目依赖已安装（`pip install -r requirements.txt`）
3. 测试使用内存数据库，无需额外配置MySQL

## 测试覆盖范围

### 认证接口测试 (`test_auth.py`)
- 用户登录接口
- 刷新令牌接口
- 用户注册接口

### 患者管理接口测试 (`test_patient.py`)
- 获取家庭列表接口
- 获取家庭详情接口

### 预约管理接口测试 (`test_appointment.py`)
- 获取今日预约列表接口
- 获取预约列表接口
- 创建预约接口
- 更新预约接口
- 完成预约接口

### 医院预约接口测试 (`test_hospital.py`)
- 获取合作医院列表接口
- 获取医院科室列表接口
- 获取科室医生列表接口
- 创建医院预约接口

## 测试数据

测试会自动创建所需的测试数据，包括：
- 测试用户（记录员）
- 测试家庭和患者
- 测试服务套餐
- 测试医院、科室和医生

测试结束后会自动清理所有测试数据。

## 测试文档

详细的测试用例和预期结果请参考 [api_test_documentation.md](api_test_documentation.md) 文件。