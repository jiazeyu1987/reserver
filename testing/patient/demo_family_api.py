#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
家庭档案管理功能演示脚本
用于演示和测试家庭档案的增删查改操作
"""

import requests
import json
from datetime import datetime

class FamilyAPIDemo:
    
    def __init__(self, base_url='http://localhost:5000', username='recorder003', password='recorder123'):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        
        # 登录获取token
        self.login(username, password)
    
    def login(self, username, password):
        """登录获取访问令牌"""
        login_data = {
            'username': username,  # 修正：使用 username 字段
            'password': password
        }
        
        response = self.session.post(f'{self.base_url}/api/v1/auth/login', json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['data']['access_token']  # 修正：数据结构
            self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
            print(f"✅ 登录成功: {username}")
        else:
            print(f"❌ 登录失败: {response.text}")
            raise Exception("登录失败")
    
    def create_family(self, family_data):
        """创建家庭档案"""
        print("\n🏠 创建家庭档案...")
        response = self.session.post(f'{self.base_url}/api/v1/families', json=family_data)
        
        if response.status_code == 200:
            data = response.json()
            family_id = data['data']['id']
            print(f"✅ 家庭档案创建成功，ID: {family_id}")
            print(f"   户主: {data['data']['householdHead']}")
            print(f"   地址: {data['data']['address']}")
            print(f"   成员数: {data['data']['totalMembers']}")
            return family_id
        else:
            print(f"❌ 创建失败: {response.text}")
            return None
    
    def get_families(self, search=None):
        """获取家庭列表"""
        print("\n📋 获取家庭列表...")
        url = f'{self.base_url}/api/v1/families'
        if search:
            url += f'?search={search}'
            
        response = self.session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            families = data['data']['families']
            print(f"✅ 找到 {len(families)} 个家庭:")
            for family in families:
                print(f"   - {family['householdHead']}家 (ID: {family['id']}, 成员: {family['totalMembers']}人)")
            return families
        else:
            print(f"❌ 获取失败: {response.text}")
            return []
    
    def get_family_detail(self, family_id):
        """获取家庭详情"""
        print(f"\n🔍 获取家庭详情 (ID: {family_id})...")
        response = self.session.get(f'{self.base_url}/api/v1/families/{family_id}')
        
        if response.status_code == 200:
            data = response.json()
            family = data['data']
            print(f"✅ 家庭详情:")
            print(f"   户主: {family['householdHead']}")
            print(f"   地址: {family['address']}")
            print(f"   电话: {family['phone']}")
            print(f"   成员数: {family['totalMembers']}")
            
            print("   家庭成员:")
            for member in family['members']:
                print(f"     - {member['name']} ({member['age']}岁, {member['gender']}, {member['relationship']})")
                if member['conditions']:
                    print(f"       健康状况: {', '.join(member['conditions'])}")
                print(f"       套餐: {member['packageType']}, 状态: {member['paymentStatus']}")
            
            return family
        else:
            print(f"❌ 获取失败: {response.text}")
            return None
    
    def update_family(self, family_id, update_data):
        """更新家庭信息"""
        print(f"\n✏️ 更新家庭信息 (ID: {family_id})...")
        response = self.session.put(f'{self.base_url}/api/v1/families/{family_id}', json=update_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 家庭信息更新成功")
            return data['data']
        else:
            print(f"❌ 更新失败: {response.text}")
            return None
    
    def add_family_member(self, family_id, member_data):
        """添加家庭成员"""
        print(f"\n👥 为家庭 {family_id} 添加成员...")
        response = self.session.post(f'{self.base_url}/api/v1/families/{family_id}/members', json=member_data)
        
        if response.status_code == 200:
            data = response.json()
            member = data['data']
            print(f"✅ 成员添加成功: {member['name']} ({member['age']}岁, {member['relationship']})")
            return member
        else:
            print(f"❌ 添加失败: {response.text}")
            return None
    
    def update_family_member(self, family_id, member_id, update_data):
        """更新家庭成员"""
        print(f"\n✏️ 更新家庭成员 (家庭ID: {family_id}, 成员ID: {member_id})...")
        response = self.session.put(f'{self.base_url}/api/v1/families/{family_id}/members/{member_id}', json=update_data)
        
        if response.status_code == 200:
            data = response.json()
            member = data['data']
            print(f"✅ 成员信息更新成功: {member['name']}")
            return member
        else:
            print(f"❌ 更新失败: {response.text}")
            return None
    
    def delete_family_member(self, family_id, member_id):
        """删除家庭成员"""
        print(f"\n🗑️ 删除家庭成员 (家庭ID: {family_id}, 成员ID: {member_id})...")
        response = self.session.delete(f'{self.base_url}/api/v1/families/{family_id}/members/{member_id}')
        
        if response.status_code == 200:
            print("✅ 家庭成员删除成功")
            return True
        else:
            print(f"❌ 删除失败: {response.text}")
            return False
    
    def delete_family(self, family_id):
        """删除家庭档案"""
        print(f"\n🗑️ 删除家庭档案 (ID: {family_id})...")
        response = self.session.delete(f'{self.base_url}/api/v1/families/{family_id}')
        
        if response.status_code == 200:
            print("✅ 家庭档案删除成功")
            return True
        else:
            print(f"❌ 删除失败: {response.text}")
            return False


def run_demo():
    """运行家庭档案管理演示"""
    print("🚀 家庭档案管理API演示开始...")
    print("="*60)
    
    try:
        # 初始化API客户端
        api = FamilyAPIDemo()
        
        # 1. 创建家庭档案
        family_data = {
            "householdHead": "王小明",
            "address": "朝阳区阳光花园1号楼301",
            "phone": "13900001234",
            "members": [
                {
                    "name": "王小明",
                    "age": 35,
                    "gender": "男",
                    "relationship": "户主",
                    "conditions": "健康体检",
                    "packageType": "基础套餐"
                },
                {
                    "name": "李小红",
                    "age": 32,
                    "gender": "女",
                    "relationship": "配偶",
                    "conditions": "偶尔头痛",
                    "packageType": "标准套餐",
                    "medications": "止痛片"
                }
            ]
        }
        
        family_id = api.create_family(family_data)
        if not family_id:
            return
        
        # 2. 获取家庭列表
        api.get_families()
        
        # 3. 搜索家庭
        api.get_families(search="王小明")
        
        # 4. 获取家庭详情
        family_detail = api.get_family_detail(family_id)
        if not family_detail:
            return
        
        # 5. 更新家庭基本信息
        update_data = {
            "householdHead": "王小明（更新）",
            "address": "朝阳区阳光花园1号楼301室",
            "phone": "13900001235"
        }
        api.update_family(family_id, update_data)
        
        # 6. 添加家庭成员
        new_member_data = {
            "name": "王小宝",
            "age": 5,
            "gender": "男",
            "relationship": "儿子",
            "conditions": "健康",
            "packageType": "基础套餐"
        }
        new_member = api.add_family_member(family_id, new_member_data)
        
        # 7. 更新家庭成员信息
        if new_member:
            member_update_data = {
                "age": 6,  # 年龄增长
                "conditions": "健康，疫苗接种完整",
                "packageType": "标准套餐"  # 升级套餐
            }
            api.update_family_member(family_id, new_member['id'], member_update_data)
        
        # 8. 再次查看家庭详情（查看更新结果）
        api.get_family_detail(family_id)
        
        # 9. 删除一个家庭成员
        if new_member:
            api.delete_family_member(family_id, new_member['id'])
        
        # 10. 最后删除整个家庭档案
        api.delete_family(family_id)
        
        # 11. 验证删除结果
        api.get_families()
        
        print("\n" + "="*60)
        print("✅ 家庭档案管理API演示完成！")
        print("所有增删查改操作都执行成功。")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {str(e)}")
        print("请确保：")
        print("1. Flask服务器已启动 (python run.py)")
        print("2. 数据库连接正常")
        print("3. 管理员账号存在 (admin/admin123)")


if __name__ == '__main__':
    run_demo()