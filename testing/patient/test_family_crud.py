import unittest
import json
from app import create_app, db
from app.models.user import User, Recorder
from app.models.patient import Family, Patient
from app.services.family_service import FamilyService
from flask_jwt_extended import create_access_token
from datetime import datetime

class FamilyTestCase(unittest.TestCase):
    
    def setUp(self):
        """测试前的设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # 创建数据库表
        db.create_all()
        
        # 创建测试用户（记录员和管理员）
        self.create_test_users()
        
        # 创建测试数据
        self.sample_family_data = {
            "householdHead": "张伟",
            "address": "朝阳区幸福小区3号楼502",
            "phone": "13800138001",
            "members": [
                {
                    "name": "张伟",
                    "age": 65,
                    "gender": "男",
                    "relationship": "户主",
                    "conditions": "高血压",
                    "packageType": "标准套餐"
                },
                {
                    "name": "李梅",
                    "age": 62,
                    "gender": "女",
                    "relationship": "配偶",
                    "conditions": "糖尿病",
                    "packageType": "VIP套餐",
                    "medications": "胰岛素"
                }
            ]
        }
    
    def tearDown(self):
        """测试后的清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_users(self):
        """创建测试用户"""
        # 创建管理员用户
        self.admin_user = User(
            username='test_admin',
            phone='13900000001',
            password_hash='hashed_password',
            role='admin',
            name='测试管理员'
        )
        db.session.add(self.admin_user)
        
        # 创建记录员用户
        self.recorder_user = User(
            username='test_recorder',
            phone='13900000002',
            password_hash='hashed_password',
            role='recorder',
            name='测试记录员'
        )
        db.session.add(self.recorder_user)
        db.session.flush()
        
        # 创建记录员详细信息
        self.recorder = Recorder(
            user_id=self.recorder_user.id,
            employee_id='EMP0001',
            is_on_duty=True
        )
        db.session.add(self.recorder)
        db.session.commit()
        
        # 生成JWT令牌
        with self.app.app_context():
            self.admin_token = create_access_token(identity=str(self.admin_user.id))
            self.recorder_token = create_access_token(identity=str(self.recorder_user.id))
    
    def get_auth_headers(self, token):
        """获取认证头部"""
        return {'Authorization': f'Bearer {token}'}
    
    # ========== 创建家庭档案测试 ==========
    
    def test_create_family_success(self):
        """测试成功创建家庭档案"""
        response = self.client.post(
            '/api/v1/families',
            data=json.dumps(self.sample_family_data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '家庭档案创建成功')
        
        # 验证返回的数据
        family_data = data['data']
        self.assertEqual(family_data['householdHead'], '张伟')
        self.assertEqual(family_data['address'], '朝阳区幸福小区3号楼502')
        self.assertEqual(family_data['phone'], '13800138001')
        self.assertEqual(family_data['totalMembers'], 2)
        self.assertEqual(len(family_data['members']), 2)
        
        # 验证成员数据
        member1 = family_data['members'][0]
        self.assertEqual(member1['name'], '张伟')
        self.assertEqual(member1['age'], 65)
        self.assertEqual(member1['gender'], '男')
        
        member2 = family_data['members'][1]
        self.assertEqual(member2['name'], '李梅')
        self.assertEqual(member2['medications'], ['胰岛素'])
    
    def test_create_family_missing_required_fields(self):
        """测试创建家庭档案缺少必填字段"""
        invalid_data = {
            "householdHead": "张伟"
            # 缺少 address, phone, members
        }
        
        response = self.client.post(
            '/api/v1/families',
            data=json.dumps(invalid_data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertIn('缺少必填字段', data['message'])
    
    def test_create_family_invalid_member_data(self):
        """测试创建家庭档案成员数据无效"""
        invalid_data = self.sample_family_data.copy()
        invalid_data['members'] = [
            {
                "name": "张伟",
                "age": 200,  # 无效年龄
                "gender": "未知",  # 无效性别
                "relationship": "户主"
            }
        ]
        
        response = self.client.post(
            '/api/v1/families',
            data=json.dumps(invalid_data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
    
    def test_create_family_unauthorized(self):
        """测试未授权创建家庭档案"""
        response = self.client.post(
            '/api/v1/families',
            data=json.dumps(self.sample_family_data),
            content_type='application/json'
            # 没有认证头部
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ========== 查询家庭档案测试 ==========
    
    def test_get_families_success(self):
        """测试成功获取家庭列表"""
        # 先创建一个家庭
        family = FamilyService.create_family(self.sample_family_data)
        
        response = self.client.get(
            '/api/v1/families',
            headers=self.get_auth_headers(self.recorder_token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertIsInstance(data['data']['families'], list)
        self.assertGreater(data['data']['total'], 0)
    
    def test_get_families_with_search(self):
        """测试带搜索条件获取家庭列表"""
        # 先创建一个家庭
        family = FamilyService.create_family(self.sample_family_data)
        
        response = self.client.get(
            '/api/v1/families?search=张伟',
            headers=self.get_auth_headers(self.recorder_token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        # 应该能找到匹配的家庭
        self.assertGreater(len(data['data']['families']), 0)
    
    def test_get_family_detail_success(self):
        """测试成功获取家庭详情"""
        # 先创建一个家庭
        family = FamilyService.create_family(self.sample_family_data)
        
        response = self.client.get(
            f'/api/v1/families/{family.id}',
            headers=self.get_auth_headers(self.recorder_token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        
        # 验证家庭详情数据
        family_data = data['data']
        self.assertEqual(family_data['householdHead'], '张伟')
        self.assertEqual(len(family_data['members']), 2)
    
    def test_get_family_detail_not_found(self):
        """测试获取不存在的家庭详情"""
        response = self.client.get(
            '/api/v1/families/99999',
            headers=self.get_auth_headers(self.recorder_token)
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 404)
        self.assertIn('不存在', data['message'])
    
    # ========== 更新家庭档案测试 ==========
    
    def test_update_family_success(self):
        """测试成功更新家庭信息"""
        # 先创建一个家庭
        family = FamilyService.create_family(self.sample_family_data)
        
        update_data = {
            "householdHead": "张伟修改",
            "address": "新地址",
            "phone": "13800138999"
        }
        
        response = self.client.put(
            f'/api/v1/families/{family.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '家庭信息更新成功')
        
        # 验证更新后的数据
        family_data = data['data']
        self.assertEqual(family_data['householdHead'], '张伟修改')
        self.assertEqual(family_data['address'], '新地址')
        self.assertEqual(family_data['phone'], '13800138999')
    
    def test_update_family_with_members(self):
        """测试更新家庭信息包含成员"""
        # 先创建一个家庭
        family = FamilyService.create_family(self.sample_family_data)
        
        update_data = {
            "householdHead": "张伟",
            "address": "朝阳区幸福小区3号楼502",
            "phone": "13800138001",
            "members": [
                {
                    "name": "张伟",
                    "age": 66,  # 年龄更新
                    "gender": "男",
                    "relationship": "户主",
                    "conditions": "高血压,糖尿病",  # 新增病症
                    "packageType": "VIP套餐"  # 套餐升级
                }
            ]
        }
        
        response = self.client.put(
            f'/api/v1/families/{family.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        
        # 验证成员更新
        family_data = data['data']
        self.assertEqual(len(family_data['members']), 1)
        member = family_data['members'][0]
        self.assertEqual(member['age'], 66)
        self.assertEqual(member['packageType'], 'VIP套餐')
    
    def test_update_family_not_found(self):
        """测试更新不存在的家庭"""
        update_data = {"householdHead": "不存在的家庭"}
        
        response = self.client.put(
            '/api/v1/families/99999',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 404)
    
    # ========== 删除家庭档案测试 ==========
    
    def test_delete_family_success(self):
        """测试成功删除家庭档案"""
        # 先创建一个家庭
        family = FamilyService.create_family(self.sample_family_data)
        
        response = self.client.delete(
            f'/api/v1/families/{family.id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '家庭档案删除成功')
        
        # 验证家庭已被删除
        deleted_family = Family.query.get(family.id)
        self.assertIsNone(deleted_family)
    
    def test_delete_family_not_found(self):
        """测试删除不存在的家庭"""
        response = self.client.delete(
            '/api/v1/families/99999',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 404)
    
    # ========== 家庭成员管理测试 ==========
    
    def test_add_family_member_success(self):
        """测试成功添加家庭成员"""
        # 先创建一个家庭
        family = FamilyService.create_family(self.sample_family_data)
        
        new_member_data = {
            "name": "张小明",
            "age": 30,
            "gender": "男",
            "relationship": "儿子",
            "conditions": "健康",
            "packageType": "基础套餐"
        }
        
        response = self.client.post(
            f'/api/v1/families/{family.id}/members',
            data=json.dumps(new_member_data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '家庭成员添加成功')
        
        # 验证成员数据
        member_data = data['data']
        self.assertEqual(member_data['name'], '张小明')
        self.assertEqual(member_data['age'], 30)
        self.assertEqual(member_data['relationship'], '儿子')
    
    def test_update_family_member_success(self):
        """测试成功更新家庭成员"""
        # 先创建一个家庭
        family = FamilyService.create_family(self.sample_family_data)
        member = family.members[0]  # 获取第一个成员
        
        update_data = {
            "name": "张伟更新",
            "age": 66,
            "packageType": "VIP套餐",
            "conditions": "高血压,糖尿病"
        }
        
        response = self.client.put(
            f'/api/v1/families/{family.id}/members/{member.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '家庭成员信息更新成功')
        
        # 验证更新后的数据
        member_data = data['data']
        self.assertEqual(member_data['name'], '张伟更新')
        self.assertEqual(member_data['age'], 66)
        self.assertEqual(member_data['packageType'], 'VIP套餐')
    
    def test_delete_family_member_success(self):
        """测试成功删除家庭成员（当有多个成员时）"""
        # 先创建一个有多个成员的家庭
        family = FamilyService.create_family(self.sample_family_data)
        member_to_delete = family.members[1]  # 删除第二个成员
        
        response = self.client.delete(
            f'/api/v1/families/{family.id}/members/{member_to_delete.id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '家庭成员删除成功')
        
        # 验证成员已被删除
        deleted_member = Patient.query.get(member_to_delete.id)
        self.assertIsNone(deleted_member)
    
    def test_delete_last_family_member_failure(self):
        """测试删除家庭最后一个成员失败"""
        # 创建只有一个成员的家庭
        single_member_data = self.sample_family_data.copy()
        single_member_data['members'] = [single_member_data['members'][0]]
        
        family = FamilyService.create_family(single_member_data)
        member = family.members[0]
        
        response = self.client.delete(
            f'/api/v1/families/{family.id}/members/{member.id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertIn('最后一个成员', data['message'])
    
    # ========== 权限测试 ==========
    
    def test_recorder_can_access_families(self):
        """测试记录员可以访问家庭列表"""
        response = self.client.get(
            '/api/v1/families',
            headers=self.get_auth_headers(self.recorder_token)
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_recorder_can_create_family(self):
        """测试记录员可以创建家庭"""
        response = self.client.post(
            '/api/v1/families',
            data=json.dumps(self.sample_family_data),
            content_type='application/json',
            headers=self.get_auth_headers(self.recorder_token)
        )
        
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()