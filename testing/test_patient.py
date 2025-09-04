import unittest
import json
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.patient import Family, Patient
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

class PatientTestCase(unittest.TestCase):
    """患者与家庭管理接口测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # 创建测试数据库表
        db.create_all()
        
        # 创建测试记录员用户
        self.test_recorder = User(
            username='testrecorder',
            phone='13800138001',
            password_hash=generate_password_hash('testpassword'),
            role='recorder',
            name='测试记录员'
        )
        db.session.add(self.test_recorder)
        db.session.commit()
        
        # 生成访问令牌
        self.access_token = create_access_token(identity=str(self.test_recorder.id))
        self.auth_header = {'Authorization': f'Bearer {self.access_token}'}
        
        # 创建测试家庭和患者数据
        self.test_family = Family(
            family_name='测试家庭',
            primary_address='北京市朝阳区测试街道100号',
            contact_phone='13800138001'
        )
        db.session.add(self.test_family)
        db.session.commit()
        
        self.test_patient = Patient(
            family_id=self.test_family.id,
            name='测试患者',
            gender='male',
            birth_date=datetime.strptime('1990-01-01', '%Y-%m-%d').date(),
            relationship_to_head='本人'
        )
        db.session.add(self.test_patient)
        db.session.commit()
        
        # 创建患者订阅以关联记录员
        from app.models.appointment import PatientSubscription, ServicePackage
        from datetime import date, timedelta
        
        # 创建测试服务套餐
        test_package = ServicePackage(
            name='基础护理套餐',
            description='基础护理服务',
            price=100.00,
            duration_days=30,
            service_frequency=4,
            service_items='基础护理服务内容'
        )
        db.session.add(test_package)
        db.session.commit()
        
        subscription = PatientSubscription(
            patient_id=self.test_patient.id,
            package_id=test_package.id,
            recorder_id=self.test_recorder.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active'
        )
        db.session.add(subscription)
        db.session.commit()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_families_success(self):
        """测试成功获取家庭列表"""
        response = self.client.get('/api/v1/families',
                                 headers=self.auth_header)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertIn('data', data)
    
    def test_get_family_detail_success(self):
        """测试成功获取家庭详情"""
        response = self.client.get(f'/api/v1/families/{self.test_family.id}',
                                 headers=self.auth_header)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertIn('data', data)
        self.assertEqual(data['data']['id'], self.test_family.id)
    
    def test_get_family_detail_not_found(self):
        """测试获取不存在的家庭详情"""
        response = self.client.get('/api/v1/families/99999',
                                 headers=self.auth_header)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 404)
        self.assertEqual(data['message'], '家庭不存在或无权限访问')

if __name__ == '__main__':
    unittest.main()