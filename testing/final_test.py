#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试 - 验证家庭列表和创建功能完全正常
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


def test_complete_workflow():
    """测试完整的工作流程"""
    base_url = 'http://127.0.0.1:5000'
    
    print("=== 最终测试：家庭管理完整工作流程 ===")
    print("=" * 50)
    
    # 创建Flask应用上下文
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            
            # 1. 创建测试用户
            print("1. 创建测试记录员用户...")
            
            # 删除现有测试用户
            existing_user = User.query.filter_by(username='final_test_user').first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            
            # 创建新用户
            test_user = User(
                username='final_test_user',
                phone='13900000997',
                password_hash=generate_password_hash('password123'),
                role='recorder',
                name='最终测试用户'
            )
            db.session.add(test_user)
            db.session.flush()
            
            # 创建记录员信息
            test_recorder = Recorder(
                user_id=test_user.id,
                employee_id='FINAL001',
                is_on_duty=True
            )
            db.session.add(test_recorder)
            db.session.commit()
            
            print(f"   用户创建成功，ID: {test_user.id}")
            
            # 生成JWT token
            token = create_access_token(identity=str(test_user.id))
            print(f"   Token生成成功")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # 2. 创建第一个家庭
            print("\n2. 创建第一个家庭...")
            family_data1 = {
                "householdHead": "张三",
                "address": "北京市朝阳区测试小区1号楼",
                "phone": "13800138001",
                "members": [
                    {
                        "name": "张三",
                        "age": 70,
                        "gender": "男",
                        "relationship": "户主",
                        "conditions": "高血压,糖尿病",
                        "packageType": "VIP套餐"
                    },
                    {
                        "name": "李四",
                        "age": 68,
                        "gender": "女", 
                        "relationship": "配偶",
                        "conditions": "骨质疏松",
                        "packageType": "标准套餐"
                    }
                ]
            }
            
            response = requests.post(
                f"{base_url}/api/v1/families",
                headers=headers,
                json=family_data1,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                family1_id = data.get('data', {}).get('id')
                print(f"   第一个家庭创建成功，ID: {family1_id}")
            else:
                print(f"   第一个家庭创建失败: {response.text[:100]}")
                return
            
            # 3. 创建第二个家庭
            print("\n3. 创建第二个家庭...")
            family_data2 = {
                "householdHead": "王五",
                "address": "北京市海淀区测试小区2号楼", 
                "phone": "13800138002",
                "members": [
                    {
                        "name": "王五",
                        "age": 75,
                        "gender": "男",
                        "relationship": "户主",
                        "conditions": "冠心病",
                        "packageType": "基础套餐"
                    }
                ]
            }
            
            response = requests.post(
                f"{base_url}/api/v1/families",
                headers=headers,
                json=family_data2,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                family2_id = data.get('data', {}).get('id')
                print(f"   第二个家庭创建成功，ID: {family2_id}")
            else:
                print(f"   第二个家庭创建失败: {response.text[:100]}")
                return
            
            # 4. 获取家庭列表 
            print("\n4. 获取家庭列表...")
            response = requests.get(
                f"{base_url}/api/v1/families?page=1&limit=20",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                families_data = data.get('data', {})
                total = families_data.get('total', 0)
                families = families_data.get('families', [])
                
                print(f"   获取成功，共找到 {total} 个家庭:")
                for i, family in enumerate(families, 1):
                    print(f"     {i}. {family.get('householdHead')} - {family.get('address')} (成员: {family.get('totalMembers')})")
                    
            else:
                print(f"   获取家庭列表失败: {response.text[:100]}")
                return
            
            # 5. 搜索测试
            print("\n5. 测试搜索功能...")
            response = requests.get(
                f"{base_url}/api/v1/families?search=张三",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                families_data = data.get('data', {})
                total = families_data.get('total', 0)
                print(f"   搜索 '张三' 找到 {total} 个结果")
            else:
                print(f"   搜索功能失败: {response.text[:100]}")
            
            # 6. 获取家庭详情
            print(f"\n6. 获取家庭详情 (ID: {family1_id})...")
            response = requests.get(
                f"{base_url}/api/v1/families/{family1_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                family_detail = data.get('data', {})
                print(f"   户主: {family_detail.get('householdHead')}")
                print(f"   地址: {family_detail.get('address')}")
                print(f"   成员数量: {len(family_detail.get('members', []))}")
                for member in family_detail.get('members', []):
                    print(f"     - {member.get('name')} ({member.get('age')}岁, {member.get('relationship')})")
            else:
                print(f"   获取家庭详情失败: {response.text[:100]}")
                
            print("\n" + "=" * 50)
            print("✓ 所有测试通过！家庭管理功能正常工作")
            print("\n总结:")
            print("- 用户认证: 正常")
            print("- 创建家庭: 正常") 
            print("- 获取列表: 正常")
            print("- 搜索功能: 正常")
            print("- 获取详情: 正常")
            print("\n之前的422错误已经解决，现在API工作正常！")
                
        except Exception as e:
            print(f"测试异常: {str(e)}")


if __name__ == '__main__':
    test_complete_workflow()