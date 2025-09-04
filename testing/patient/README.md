# 家庭档案管理API文档

本文档说明了新增的家庭档案管理功能，包括API接口、数据库更新和测试方法。

## 🔄 数据库变更

### 主要变更
1. **Family表结构更新**：
   - `family_name` → `householdHead` (户主姓名)
   - `primary_address` → `address` (家庭地址)
   - `contact_phone` → `phone` (联系电话)
   - 新增 `get_last_service_date()` 方法

2. **Patient表结构更新**：
   - `birth_date` → `age` (直接存储年龄)
   - `relationship_to_head` → `relationship` (关系)
   - `medical_history` → `conditions` (健康状况，简单文本)
   - 新增 `packageType` (套餐类型)
   - 新增 `paymentStatus` (支付状态)
   - 新增 `lastService` (最近服务日期)
   - 新增 `medications` (用药情况)

### 数据迁移
```bash
cd server
# 运行数据库迁移
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    # 执行迁移脚本
    exec(open('migrations/versions/update_family_patient_models.py').read())
"
```

## 🚀 API接口

### 基础URL
```
http://localhost:5000/api/v1
```

### 认证
所有API都需要JWT认证，在请求头中包含：
```
Authorization: Bearer <access_token>
```

### 权限说明
- **admin**: 可以执行所有操作
- **recorder**: 可以执行所有操作（查看权限受限于自己负责的家庭）

## 📋 家庭档案管理接口

### 1. 创建家庭档案
```http
POST /families
```

**请求体：**
```json
{
  "householdHead": "张伟",
  "address": "朝阳区幸福小区3号楼502",
  "phone": "13800138001",
  "emergency_contact": "张小明",
  "emergency_phone": "13800138002",
  "members": [
    {
      "name": "张伟",
      "age": 65,
      "gender": "男",
      "relationship": "户主",
      "conditions": "高血压,糖尿病",
      "packageType": "标准套餐",
      "phone": "13800138003",
      "medications": "降压药,胰岛素"
    },
    {
      "name": "李梅",
      "age": 62,
      "gender": "女", 
      "relationship": "配偶",
      "conditions": "关节炎",
      "packageType": "VIP套餐"
    }
  ]
}
```

**响应：**
```json
{
  "code": 200,
  "message": "家庭档案创建成功",
  "data": {
    "id": 1,
    "householdHead": "张伟",
    "address": "朝阳区幸福小区3号楼502",
    "phone": "13800138001",
    "totalMembers": 2,
    "lastService": null,
    "created_at": "2025-01-14T10:30:00",
    "members": [
      {
        "id": 1,
        "name": "张伟",
        "age": 65,
        "gender": "男",
        "relationship": "户主",
        "conditions": ["高血压", "糖尿病"],
        "packageType": "标准套餐",
        "paymentStatus": "normal",
        "medications": ["降压药", "胰岛素"]
      }
    ]
  }
}
```

### 2. 获取家庭列表
```http
GET /families?page=1&limit=20&search=张伟
```

**查询参数：**
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20）
- `search`: 搜索关键词（可选）

### 3. 获取家庭详情
```http
GET /families/{family_id}
```

### 4. 更新家庭信息
```http
PUT /families/{family_id}
```

**请求体：**（可部分更新）
```json
{
  "householdHead": "张伟（更新）",
  "address": "新地址",
  "members": [
    {
      "name": "张伟",
      "age": 66,
      "gender": "男",
      "relationship": "户主",
      "conditions": "高血压,糖尿病,高血脂",
      "packageType": "VIP套餐"
    }
  ]
}
```

### 5. 删除家庭档案
```http
DELETE /families/{family_id}
```

## 👥 家庭成员管理接口

### 1. 添加家庭成员
```http
POST /families/{family_id}/members
```

**请求体：**
```json
{
  "name": "张小明",
  "age": 30,
  "gender": "男",
  "relationship": "儿子",
  "conditions": "健康",
  "packageType": "基础套餐",
  "phone": "13800138004"
}
```

### 2. 更新家庭成员
```http
PUT /families/{family_id}/members/{member_id}
```

### 3. 删除家庭成员
```http
DELETE /families/{family_id}/members/{member_id}
```

**注意：** 不能删除家庭的最后一个成员。

## 🧪 测试

### 运行单元测试
```bash
cd server/testing/patient
python run_family_tests.py
```

### API演示脚本
```bash
cd server/testing/patient
python demo_family_api.py
```

演示脚本将执行以下操作：
1. 创建家庭档案
2. 查询家庭列表
3. 获取家庭详情
4. 更新家庭信息
5. 添加家庭成员
6. 更新成员信息
7. 删除成员
8. 删除家庭档案

## 📝 数据验证

### 家庭数据验证
- `householdHead`: 必填，户主姓名
- `address`: 必填，家庭地址
- `phone`: 必填，11位手机号
- `members`: 必填，至少包含一个成员

### 成员数据验证
- `name`: 必填，姓名
- `age`: 必填，0-150之间的整数
- `gender`: 必填，"男"或"女"
- `relationship`: 必填，与户主关系
- `packageType`: 可选，"基础套餐"/"标准套餐"/"VIP套餐"
- `paymentStatus`: 可选，"normal"/"overdue"/"suspended"
- `phone`: 可选，11位手机号

## 🔧 使用示例

### Python客户端示例
```python
import requests

# 登录获取token
login_response = requests.post('http://localhost:5000/api/v1/auth/login', json={
    'phone': 'admin',
    'password': 'admin123'
})
token = login_response.json()['data']['tokens']['access_token']

headers = {'Authorization': f'Bearer {token}'}

# 创建家庭档案
family_data = {
    "householdHead": "测试户主",
    "address": "测试地址123号",
    "phone": "13900001234",
    "members": [{
        "name": "测试户主",
        "age": 50,
        "gender": "男",
        "relationship": "户主",
        "packageType": "基础套餐"
    }]
}

response = requests.post('http://localhost:5000/api/v1/families', 
                        json=family_data, headers=headers)
print(response.json())
```

### JavaScript客户端示例
```javascript
// 创建家庭档案
const createFamily = async () => {
  const familyData = {
    householdHead: "测试户主",
    address: "测试地址123号", 
    phone: "13900001234",
    members: [{
      name: "测试户主",
      age: 50,
      gender: "男",
      relationship: "户主",
      packageType: "基础套餐"
    }]
  };

  try {
    const response = await fetch('/api/v1/families', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(familyData)
    });

    const result = await response.json();
    console.log('家庭创建成功:', result);
  } catch (error) {
    console.error('创建失败:', error);
  }
};
```

## 🚨 错误处理

### 常见错误码
- **400**: 请求参数错误，数据验证失败
- **401**: 未授权，需要登录
- **403**: 权限不足
- **404**: 资源不存在
- **500**: 服务器内部错误

### 错误响应格式
```json
{
  "code": 400,
  "message": "缺少必填字段: householdHead"
}
```

## 💡 最佳实践

1. **批量操作**: 创建家庭时一次性传入所有成员，避免多次API调用
2. **数据验证**: 客户端应进行基础验证，减少无效请求
3. **错误处理**: 妥善处理各种错误情况，给用户友好提示
4. **权限控制**: 记录员只能操作自己负责的家庭
5. **数据备份**: 删除操作不可恢复，建议实现软删除

## 🔄 与客户端集成

客户端现有的家庭档案创建表单可直接使用这些API：

```javascript
// 客户端表单数据
const newFamily = {
  householdHead: "张伟",
  address: "朝阳区幸福小区3号楼502", 
  phone: "13800138001",
  members: [
    {
      name: "张伟",
      age: "65",
      gender: "男",
      relationship: "户主",
      conditions: "高血压",
      packageType: "基础套餐"
    }
  ]
};

// 提交到服务器
const response = await api.post('/families', newFamily);
```

这样客户端无需修改现有数据结构，服务器会自动处理数据转换和存储。