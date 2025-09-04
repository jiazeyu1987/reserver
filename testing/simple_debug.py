#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版家庭API 422错误诊断脚本
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


def test_family_api():
    """测试家庭API"""
    base_url = 'http://127.0.0.1:5000'
    
    print("开始诊断家庭API 422错误...")
    print("=" * 50)
    
    # 创建Flask应用上下文
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            
            # 1. 创建测试用户
            print("1. 创建测试用户...")
            
            # 删除现有测试用户
            existing_user = User.query.filter_by(username='test_debug').first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            
            # 创建新用户
            test_user = User(
                username='test_debug',
                phone='13900000998',
                password_hash=generate_password_hash('password123'),
                role='recorder',
                name='测试用户'
            )
            db.session.add(test_user)
            db.session.flush()
            
            # 创建记录员信息
            test_recorder = Recorder(
                user_id=test_user.id,
                employee_id='DEBUG002',
                is_on_duty=True
            )
            db.session.add(test_recorder)
            db.session.commit()
            
            print(f"   用户创建成功，ID: {test_user.id}")
            
            # 生成JWT token
            token = create_access_token(identity=str(test_user.id))
            print(f"   Token生成成功: {token[:30]}...")
            
            # 2. 测试获取家庭列表
            print("\n2. 测试获取家庭列表...")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # 测试不同参数
            test_params = [
                {},
                {'page': 1},
                {'page': 1, 'limit': 20},
                {'page': 1, 'limit': 20, 'search': ''}
            ]
            
            for i, params in enumerate(test_params, 1):
                print(f"   测试 {i}: 参数 {params}")
                try:
                    response = requests.get(
                        f"{base_url}/api/v1/families",
                        headers=headers,
                        params=params,
                        timeout=10
                    )
                    print(f"     状态码: {response.status_code}")
                    
                    if response.status_code == 422:
                        try:
                            error_data = response.json()
                            print(f"     422错误: {error_data.get('message', 'Unknown error')}")
                        except:
                            print(f"     原始响应: {response.text[:200]}")
                    elif response.status_code == 200:
                        print("     成功!")
                        try:
                            data = response.json()
                            families_data = data.get('data', {})
                            print(f"     家庭数量: {families_data.get('total', 0)}")
                        except:
                            print("     JSON解析失败")
                    else:
                        print(f"     其他错误: {response.text[:100]}")
                        
                except requests.exceptions.ConnectionError:
                    print("     连接失败 - 服务器未运行?")
                except Exception as e:
                    print(f"     异常: {str(e)}")
            
            # 3. 测试创建家庭
            print("\n3. 测试创建家庭...")
            
            family_data = {
                "householdHead": "测试户主",
                "address": "测试地址123",
                "phone": "13800138888",
                "members": [
                    {
                        "name": "测试成员",
                        "age": 60,
                        "gender": "男",
                        "relationship": "户主",
                        "conditions": "高血压",
                        "packageType": "标准套餐"
                    }
                ]
            }
            
            try:
                response = requests.post(
                    f"{base_url}/api/v1/families",
                    headers=headers,
                    json=family_data,
                    timeout=10
                )
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 422:
                    try:
                        error_data = response.json()
                        print(f"   422错误: {error_data.get('message', 'Unknown error')}")
                    except:
                        print(f"   原始响应: {response.text[:200]}")
                elif response.status_code == 200:
                    print("   创建成功!")
                    try:
                        data = response.json()
                        family_info = data.get('data', {})
                        print(f"   家庭ID: {family_info.get('id', 'Unknown')}")
                    except:
                        print("   JSON解析失败")
                else:
                    print(f"   其他错误: {response.text[:100]}")
                    
            except requests.exceptions.ConnectionError:
                print("   连接失败 - 服务器未运行?")
            except Exception as e:
                print(f"   异常: {str(e)}")
            
            # 4. 测试无token请求
            print("\n4. 测试无token请求...")
            try:
                response = requests.get(f"{base_url}/api/v1/families", timeout=5)
                print(f"   状态码: {response.status_code}")
                if response.status_code == 401:
                    print("   正确返回401未授权")
            except Exception as e:
                print(f"   异常: {str(e)}")
                
        except Exception as e:
            print(f"应用初始化失败: {str(e)}")
    
    print("\n" + "=" * 50)
    print("测试完成!")
    
    print("\n可能的422错误原因:")
    print("1. JWT token格式问题")
    print("2. 用户权限不足")
    print("3. 数据验证失败")
    print("4. 装饰器中的用户ID转换问题")


if __name__ == '__main__':
    test_family_api()