#!/usr/bin/env python3
"""
测试家庭列表和创建用户功能，诊断422错误
"""
import requests
import json
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.dirname(current_dir)
sys.path.append(server_dir)

from app import create_app, db
from app.models.user import User, Recorder
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash


class FamilyErrorDebugger:
    def __init__(self, base_url='http://127.0.0.1:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_auth_and_create_user(self):
        """测试认证和创建用户"""
        print("=== 测试认证和用户创建 ===")
        
        # 创建Flask应用上下文进行测试
        app = create_app()
        with app.app_context():
            db.create_all()
            
            # 1. 创建测试用户
            print("1. 创建测试用户...")
            try:
                # 检查是否已存在测试用户
                existing_user = User.query.filter_by(username='test_recorder_debug').first()
                if existing_user:
                    print("   测试用户已存在，删除旧用户")
                    db.session.delete(existing_user)
                    db.session.commit()
                
                # 创建新的测试记录员用户
                test_user = User(
                    username='test_recorder_debug',
                    phone='13900000999',
                    password_hash=generate_password_hash('password123'),
                    role='recorder',
                    name='测试记录员用户'
                )
                db.session.add(test_user)
                db.session.flush()
                
                # 创建记录员详细信息
                test_recorder = Recorder(
                    user_id=test_user.id,
                    employee_id='DEBUG001',
                    is_on_duty=True
                )
                db.session.add(test_recorder)
                db.session.commit()
                
                print(f"   [OK] 用户创建成功，用户ID: {test_user.id}")
                
                # 生成JWT token
                token = create_access_token(identity=str(test_user.id))
                print(f"   [OK] JWT token生成成功: {token[:50]}...")
                
                return token, test_user.id
                
            except Exception as e:
                print(f"   [ERROR] 用户创建失败: {str(e)}")
                return None, None
    
    def test_get_families_with_token(self, token):
        """测试获取家庭列表"""
        print("\n=== 测试获取家庭列表 ===")
        
        # 测试不同的请求参数组合
        test_cases = [
            {"params": {}, "description": "无参数请求"},
            {"params": {"page": 1}, "description": "仅指定页码"},
            {"params": {"page": 1, "limit": 20}, "description": "指定页码和限制"},
            {"params": {"page": 1, "limit": 20, "search": ""}, "description": "包含空搜索参数"},
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"{i}. {case['description']}")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            try:
                url = f"{self.base_url}/api/v1/families"
                response = self.session.get(url, headers=headers, params=case['params'])
                
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 422:
                    print("   [ERROR] 422 错误，响应内容:")
                    try:
                        error_data = response.json()
                        print(f"      - 错误代码: {error_data.get('code')}")
                        print(f"      - 错误消息: {error_data.get('message')}")
                    except:
                        print(f"      - 原始响应: {response.text}")
                elif response.status_code == 200:
                    print("   [OK] 请求成功")
                    try:
                        data = response.json()
                        print(f"      - 返回数据: {data.get('message')}")
                        families_data = data.get('data', {})
                        print(f"      - 家庭数量: {families_data.get('total', 0)}")
                    except:
                        print("      - 无法解析响应JSON")
                else:
                    print(f"   ✗ 其他错误: {response.status_code}")
                    print(f"      - 响应: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                print("   ✗ 连接失败，请确保服务器正在运行")
            except Exception as e:
                print(f"   ✗ 请求异常: {str(e)}")
            
            print()
    
    def test_create_family_with_token(self, token):
        """测试创建家庭"""
        print("=== 测试创建家庭 ===")
        
        # 测试数据
        family_data = {
            "householdHead": "测试家庭户主",
            "address": "测试地址123号",
            "phone": "13800138000",
            "members": [
                {
                    "name": "测试成员1",
                    "age": 65,
                    "gender": "男",
                    "relationship": "户主",
                    "conditions": "高血压",
                    "packageType": "标准套餐"
                }
            ]
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print("1. 发送创建家庭请求...")
        try:
            url = f"{self.base_url}/api/v1/families"
            response = self.session.post(url, headers=headers, json=family_data)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 422:
                print("   ✗ 422 错误，响应内容:")
                try:
                    error_data = response.json()
                    print(f"      - 错误代码: {error_data.get('code')}")
                    print(f"      - 错误消息: {error_data.get('message')}")
                except:
                    print(f"      - 原始响应: {response.text}")
            elif response.status_code == 200:
                print("   ✓ 创建成功")
                try:
                    data = response.json()
                    print(f"      - 消息: {data.get('message')}")
                    family_info = data.get('data', {})
                    print(f"      - 家庭ID: {family_info.get('id')}")
                    print(f"      - 户主: {family_info.get('householdHead')}")
                except:
                    print("      - 无法解析响应JSON")
            else:
                print(f"   ✗ 其他错误: {response.status_code}")
                print(f"      - 响应: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ✗ 连接失败，请确保服务器正在运行")
        except Exception as e:
            print(f"   ✗ 请求异常: {str(e)}")
    
    def test_without_token(self):
        """测试无token的请求"""
        print("\n=== 测试无认证请求 ===")
        
        print("1. 测试无token获取家庭列表...")
        try:
            url = f"{self.base_url}/api/v1/families"
            response = self.session.get(url)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 401:
                print("   ✓ 正确返回401未授权")
            else:
                print(f"   ? 意外状态码: {response.text}")
        except Exception as e:
            print(f"   ✗ 请求异常: {str(e)}")
            
        print("\n2. 测试无token创建家庭...")
        try:
            url = f"{self.base_url}/api/v1/families"
            response = self.session.post(url, json={"test": "data"})
            print(f"   状态码: {response.status_code}")
            if response.status_code == 401:
                print("   ✓ 正确返回401未授权")
            else:
                print(f"   ? 意外状态码: {response.text}")
        except Exception as e:
            print(f"   ✗ 请求异常: {str(e)}")
    
    def test_invalid_token(self):
        """测试无效token"""
        print("\n=== 测试无效认证 ===")
        
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature"
        ]
        
        for i, token in enumerate(invalid_tokens, 1):
            print(f"{i}. 测试无效token: {token[:30]}...")
            
            headers = {'Authorization': f'Bearer {token}'}
            
            try:
                url = f"{self.base_url}/api/v1/families"
                response = self.session.get(url, headers=headers)
                print(f"   状态码: {response.status_code}")
                
                if response.status_code in [401, 422]:
                    try:
                        error_data = response.json()
                        print(f"   错误消息: {error_data.get('message')}")
                    except:
                        print(f"   响应: {response.text}")
                else:
                    print(f"   意外响应: {response.text}")
            except Exception as e:
                print(f"   ✗ 请求异常: {str(e)}")
            print()
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始诊断家庭API 422错误...")
        print("=" * 50)
        
        # 1. 测试无认证请求
        self.test_without_token()
        
        # 2. 测试无效token
        self.test_invalid_token()
        
        # 3. 创建用户并获取有效token
        token, user_id = self.test_auth_and_create_user()
        
        if token and user_id:
            # 4. 测试有效token的请求
            self.test_get_families_with_token(token)
            
            # 5. 测试创建家庭
            self.test_create_family_with_token(token)
        else:
            print("\n⚠️  无法获取有效token，跳过认证相关测试")
        
        print("\n" + "=" * 50)
        print("测试完成！")
        
        # 6. 给出诊断建议
        print("\n=== 诊断建议 ===")
        print("如果看到422错误，可能的原因包括：")
        print("1. JWT token格式问题或过期")
        print("2. 用户权限不足（需要recorder或admin权限）") 
        print("3. 请求数据格式验证失败")
        print("4. 数据库连接问题")
        print("5. 装饰器中的用户ID转换问题")


def main():
    """主函数"""
    debugger = FamilyErrorDebugger()
    debugger.run_all_tests()


if __name__ == '__main__':
    main()