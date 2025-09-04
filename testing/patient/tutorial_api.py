#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
家庭档案管理API使用教程脚本
逐步演示如何使用新的家庭档案管理接口
"""

import requests
import json
import time

class FamilyAPITutorial:
    
    def __init__(self):
        self.base_url = 'http://localhost:5000/api/v1'
        self.access_token = None
        
    def step_1_login(self):
        """第1步：登录获取访问令牌"""
        print("=" * 60)
        print("📝 第1步：登录获取访问令牌")
        print("=" * 60)
        
        login_data = {
            'username': 'recorder003',  # 修正：使用 username 字段
            'password': 'recorder123'
        }
        
        print(f"🔄 正在登录: {login_data['username']}")
        
        try:
            response = requests.post(f'{self.base_url}/auth/login', json=login_data)
            
            print(f"📡 请求URL: {self.base_url}/auth/login")
            print(f"📤 请求数据: {json.dumps(login_data, ensure_ascii=False, indent=2)}")
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['data']['access_token']  # 修正：数据结构
                print(f"✅ 登录成功！")
                print(f"🎫 访问令牌: {self.access_token[:50]}...")
                return True
            else:
                print(f"❌ 登录失败: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败！请确保服务器已启动:")
            print("   cd server && python run.py")
            return False
        except Exception as e:
            print(f"❌ 登录出错: {e}")
            return False
    
    def get_headers(self):
        """获取认证请求头"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def step_2_create_family(self):
        """第2步：创建家庭档案"""
        print("\n" + "=" * 60)
        print("👨‍👩‍👧‍👦 第2步：创建家庭档案")
        print("=" * 60)
        
        # 准备家庭数据（符合客户端格式）
        family_data = {
            "householdHead": "王小明",
            "address": "朝阳区阳光花园1号楼301室",
            "phone": "13900001234",
            "emergency_contact": "王小红",
            "emergency_phone": "13900001235",
            "members": [
                {
                    "name": "王小明",
                    "age": 35,
                    "gender": "男",
                    "relationship": "户主",
                    "conditions": "健康体检",
                    "packageType": "基础套餐",
                    "phone": "13900001234"
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
        
        print(f"🔄 创建家庭档案...")
        print(f"📤 请求数据:")
        print(json.dumps(family_data, ensure_ascii=False, indent=2))
        
        try:
            response = requests.post(
                f'{self.base_url}/families',
                json=family_data,
                headers=self.get_headers()
            )
            
            print(f"📡 请求URL: {self.base_url}/families")
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                family_id = data['data']['id']
                print(f"✅ 家庭档案创建成功！")
                print(f"🆔 家庭ID: {family_id}")
                print(f"👨‍👩‍👧‍👦 户主: {data['data']['householdHead']}")
                print(f"🏠 地址: {data['data']['address']}")
                print(f"📞 电话: {data['data']['phone']}")
                print(f"👥 成员数: {data['data']['totalMembers']}")
                return family_id
            else:
                print(f"❌ 创建失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 创建出错: {e}")
            return None
    
    def step_3_get_families(self):
        """第3步：获取家庭列表"""
        print("\n" + "=" * 60)
        print("📋 第3步：获取家庭列表")
        print("=" * 60)
        
        print("🔄 获取家庭列表...")
        
        try:
            response = requests.get(
                f'{self.base_url}/families',
                headers=self.get_headers()
            )
            
            print(f"📡 请求URL: {self.base_url}/families")
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                families = data['data']['families']
                print(f"✅ 获取成功！共找到 {len(families)} 个家庭:")
                
                for i, family in enumerate(families, 1):
                    print(f"  {i}. {family['householdHead']}家")
                    print(f"     🆔 ID: {family['id']}")
                    print(f"     🏠 地址: {family['address']}")
                    print(f"     📞 电话: {family['phone']}")
                    print(f"     👥 成员: {family['totalMembers']}人")
                    print(f"     🕐 创建时间: {family['created_at']}")
                    print()
                
                return families
            else:
                print(f"❌ 获取失败: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 获取出错: {e}")
            return []
    
    def step_4_get_family_detail(self, family_id):
        """第4步：获取家庭详情"""
        print("\n" + "=" * 60)
        print(f"🔍 第4步：获取家庭详情 (ID: {family_id})")
        print("=" * 60)
        
        print(f"🔄 获取家庭 {family_id} 的详细信息...")
        
        try:
            response = requests.get(
                f'{self.base_url}/families/{family_id}',
                headers=self.get_headers()
            )
            
            print(f"📡 请求URL: {self.base_url}/families/{family_id}")
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                family = data['data']
                
                print(f"✅ 获取成功！家庭详情:")
                print(f"🆔 ID: {family['id']}")
                print(f"👨‍👩‍👧‍👦 户主: {family['householdHead']}")
                print(f"🏠 地址: {family['address']}")
                print(f"📞 电话: {family['phone']}")
                print(f"👥 总成员数: {family['totalMembers']}")
                print(f"🩺 最近服务: {family.get('lastService', '暂无')}")
                
                print(f"\n👥 家庭成员详情:")
                for i, member in enumerate(family['members'], 1):
                    print(f"  {i}. {member['name']} (ID: {member['id']})")
                    print(f"     👤 {member['age']}岁, {member['gender']}, {member['relationship']}")
                    print(f"     💊 健康状况: {', '.join(member['conditions']) if member['conditions'] else '无'}")
                    print(f"     📦 套餐: {member['packageType']}")
                    print(f"     💳 支付状态: {member['paymentStatus']}")
                    if member.get('medications'):
                        print(f"     💉 用药: {', '.join(member['medications'])}")
                    if member.get('phone'):
                        print(f"     📱 电话: {member['phone']}")
                    print()
                
                return family
            else:
                print(f"❌ 获取失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取出错: {e}")
            return None
    
    def step_5_update_family(self, family_id):
        """第5步：更新家庭信息"""
        print("\n" + "=" * 60)
        print(f"✏️ 第5步：更新家庭信息 (ID: {family_id})")
        print("=" * 60)
        
        update_data = {
            "householdHead": "王小明（已更新）",
            "address": "朝阳区阳光花园1号楼301室（更新地址）",
            "phone": "13900009999",
            "emergency_contact": "王小红（更新）"
        }
        
        print(f"🔄 更新家庭 {family_id} 的信息...")
        print(f"📤 更新数据:")
        print(json.dumps(update_data, ensure_ascii=False, indent=2))
        
        try:
            response = requests.put(
                f'{self.base_url}/families/{family_id}',
                json=update_data,
                headers=self.get_headers()
            )
            
            print(f"📡 请求URL: {self.base_url}/families/{family_id}")
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                family = data['data']
                print(f"✅ 更新成功！")
                print(f"👨‍👩‍👧‍👦 新户主: {family['householdHead']}")
                print(f"🏠 新地址: {family['address']}")
                print(f"📞 新电话: {family['phone']}")
                return True
            else:
                print(f"❌ 更新失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 更新出错: {e}")
            return False
    
    def step_6_add_member(self, family_id):
        """第6步：添加家庭成员"""
        print("\n" + "=" * 60)
        print(f"👤➕ 第6步：添加家庭成员 (家庭ID: {family_id})")
        print("=" * 60)
        
        new_member = {
            "name": "王小宝",
            "age": 8,
            "gender": "男",
            "relationship": "儿子", 
            "conditions": "健康",
            "packageType": "基础套餐"
        }
        
        print(f"🔄 为家庭 {family_id} 添加新成员...")
        print(f"📤 成员数据:")
        print(json.dumps(new_member, ensure_ascii=False, indent=2))
        
        try:
            response = requests.post(
                f'{self.base_url}/families/{family_id}/members',
                json=new_member,
                headers=self.get_headers()
            )
            
            print(f"📡 请求URL: {self.base_url}/families/{family_id}/members")
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                member = data['data']
                print(f"✅ 成员添加成功！")
                print(f"🆔 成员ID: {member['id']}")
                print(f"👤 姓名: {member['name']}")
                print(f"👤 年龄: {member['age']}岁")
                print(f"👤 关系: {member['relationship']}")
                return member['id']
            else:
                print(f"❌ 添加失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 添加出错: {e}")
            return None
    
    def step_7_update_member(self, family_id, member_id):
        """第7步：更新家庭成员"""
        print("\n" + "=" * 60)
        print(f"✏️ 第7步：更新家庭成员 (家庭ID: {family_id}, 成员ID: {member_id})")
        print("=" * 60)
        
        update_data = {
            "age": 9,  # 年龄增长
            "conditions": "健康，已完成疫苗接种",
            "packageType": "标准套餐",  # 升级套餐
            "phone": "13900001236"  # 添加电话
        }
        
        print(f"🔄 更新成员 {member_id} 的信息...")
        print(f"📤 更新数据:")
        print(json.dumps(update_data, ensure_ascii=False, indent=2))
        
        try:
            response = requests.put(
                f'{self.base_url}/families/{family_id}/members/{member_id}',
                json=update_data,
                headers=self.get_headers()
            )
            
            print(f"📡 请求URL: {self.base_url}/families/{family_id}/members/{member_id}")
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                member = data['data']
                print(f"✅ 成员更新成功！")
                print(f"👤 姓名: {member['name']}")
                print(f"👤 年龄: {member['age']}岁")
                print(f"📦 套餐: {member['packageType']}")
                print(f"📱 电话: {member.get('phone', '无')}")
                return True
            else:
                print(f"❌ 更新失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 更新出错: {e}")
            return False
    
    def step_8_search_families(self):
        """第8步：搜索家庭"""
        print("\n" + "=" * 60)
        print("🔍 第8步：搜索家庭")
        print("=" * 60)
        
        search_term = "王小明"
        print(f"🔄 搜索关键词: '{search_term}'")
        
        try:
            response = requests.get(
                f'{self.base_url}/families?search={search_term}',
                headers=self.get_headers()
            )
            
            print(f"📡 请求URL: {self.base_url}/families?search={search_term}")
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                families = data['data']['families']
                print(f"✅ 搜索成功！找到 {len(families)} 个匹配的家庭:")
                
                for family in families:
                    print(f"  - {family['householdHead']}家 (ID: {family['id']})")
                    
                return families
            else:
                print(f"❌ 搜索失败: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 搜索出错: {e}")
            return []
    
    def step_9_delete_member(self, family_id, member_id):
        """第9步：删除家庭成员"""
        print("\n" + "=" * 60)
        print(f"🗑️ 第9步：删除家庭成员 (家庭ID: {family_id}, 成员ID: {member_id})")
        print("=" * 60)
        
        print(f"🔄 删除成员 {member_id}...")
        
        try:
            response = requests.delete(
                f'{self.base_url}/families/{family_id}/members/{member_id}',
                headers=self.get_headers()
            )
            
            print(f"📡 请求URL: {self.base_url}/families/{family_id}/members/{member_id}")
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 成员删除成功！")
                return True
            else:
                print(f"❌ 删除失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 删除出错: {e}")
            return False
    
    def step_10_delete_family(self, family_id):
        """第10步：删除家庭档案"""
        print("\n" + "=" * 60)
        print(f"🗑️ 第10步：删除家庭档案 (ID: {family_id})")
        print("=" * 60)
        
        print(f"🔄 删除家庭档案 {family_id}...")
        print("⚠️  注意：删除家庭档案将同时删除所有家庭成员！")
        
        try:
            response = requests.delete(
                f'{self.base_url}/families/{family_id}',
                headers=self.get_headers()
            )
            
            print(f"📡 请求URL: {self.base_url}/families/{family_id}")
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 家庭档案删除成功！")
                return True
            else:
                print(f"❌ 删除失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 删除出错: {e}")
            return False
    
    def run_tutorial(self):
        """运行完整教程"""
        print("🎓 家庭档案管理API使用教程")
        print("本教程将逐步演示如何使用新的家庭档案管理接口")
        print("请确保服务器已启动: cd server && python run.py")
        print()
        
        input("按回车键开始教程...")
        
        # 第1步：登录
        if not self.step_1_login():
            print("❌ 登录失败，无法继续教程")
            return
        
        input("\n按回车键继续下一步...")
        
        # 第2步：创建家庭
        family_id = self.step_2_create_family()
        if not family_id:
            print("❌ 创建家庭失败，无法继续教程")
            return
        
        input("\n按回车键继续下一步...")
        
        # 第3步：获取家庭列表
        self.step_3_get_families()
        
        input("\n按回车键继续下一步...")
        
        # 第4步：获取家庭详情
        family_detail = self.step_4_get_family_detail(family_id)
        if not family_detail:
            print("❌ 获取家庭详情失败")
            return
        
        input("\n按回车键继续下一步...")
        
        # 第5步：更新家庭信息
        self.step_5_update_family(family_id)
        
        input("\n按回车键继续下一步...")
        
        # 第6步：添加家庭成员
        new_member_id = self.step_6_add_member(family_id)
        
        input("\n按回车键继续下一步...")
        
        # 第7步：更新家庭成员
        if new_member_id:
            self.step_7_update_member(family_id, new_member_id)
        
        input("\n按回车键继续下一步...")
        
        # 第8步：搜索家庭
        self.step_8_search_families()
        
        input("\n按回车键继续下一步...")
        
        # 第9步：删除家庭成员
        if new_member_id:
            self.step_9_delete_member(family_id, new_member_id)
        
        input("\n按回车键继续最后一步...")
        
        # 第10步：删除家庭档案
        self.step_10_delete_family(family_id)
        
        print("\n" + "=" * 60)
        print("🎉 恭喜！家庭档案管理API教程完成！")
        print("=" * 60)
        print("📚 您已学会：")
        print("  ✅ 1. 登录获取访问令牌")
        print("  ✅ 2. 创建家庭档案")
        print("  ✅ 3. 获取家庭列表")
        print("  ✅ 4. 获取家庭详情")
        print("  ✅ 5. 更新家庭信息")
        print("  ✅ 6. 添加家庭成员")
        print("  ✅ 7. 更新家庭成员")
        print("  ✅ 8. 搜索家庭")
        print("  ✅ 9. 删除家庭成员")
        print("  ✅ 10. 删除家庭档案")
        print()
        print("🚀 现在您可以在自己的项目中使用这些API了！")


if __name__ == '__main__':
    tutorial = FamilyAPITutorial()
    tutorial.run_tutorial()