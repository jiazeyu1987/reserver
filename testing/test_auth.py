import unittest
import json
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

class AuthTestCase(unittest.TestCase):
    """认证接口测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # 创建测试数据库表
        db.create_all()
        
        # 创建测试用户
        self.test_user = User(
            username='testuser',
            phone='13800138000',
            password_hash=generate_password_hash('testpassword'),
            role='recorder',
            name='测试用户'
        )
        db.session.add(self.test_user)
        db.session.commit()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_login_success(self):
        """测试成功登录"""
        response = self.client.post('/api/v1/auth/login',
                                  data=json.dumps({
                                      'username': 'testuser',
                                      'password': 'testpassword'
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertIn('access_token', data['data'])
        self.assertIn('refresh_token', data['data'])
        self.assertIn('user', data['data'])
    
    def test_login_with_phone_success(self):
        """测试使用手机号登录成功"""
        response = self.client.post('/api/v1/auth/login',
                                  data=json.dumps({
                                      'username': '13800138000',
                                      'password': 'testpassword'
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
    
    def test_login_invalid_credentials(self):
        """测试无效用户名/密码"""
        response = self.client.post('/api/v1/auth/login',
                                  data=json.dumps({
                                      'username': 'testuser',
                                      'password': 'wrongpassword'
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 401)
        self.assertEqual(data['message'], '用户名或密码错误')
    
    def test_login_missing_fields(self):
        """测试缺少必填字段"""
        response = self.client.post('/api/v1/auth/login',
                                  data=json.dumps({
                                      'username': 'testuser'
                                      # 缺少密码
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertEqual(data['message'], '用户名和密码不能为空')
    
    def test_register_success(self):
        """测试成功注册"""
        response = self.client.post('/api/v1/auth/register',
                                  data=json.dumps({
                                      'username': 'newuser',
                                      'phone': '13900139000',
                                      'password': 'newpassword',
                                      'name': '新用户',
                                      'role': 'recorder'
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '注册成功')
        self.assertIn('user_id', data['data'])
    
    def test_register_duplicate_username(self):
        """测试重复用户名注册"""
        response = self.client.post('/api/v1/auth/register',
                                  data=json.dumps({
                                      'username': 'testuser',  # 重复用户名
                                      'phone': '13900139000',
                                      'password': 'newpassword',
                                      'name': '新用户',
                                      'role': 'recorder'
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertEqual(data['message'], '用户名已存在')
    
    def test_register_invalid_phone_format(self):
        """测试无效手机号格式"""
        response = self.client.post('/api/v1/auth/register',
                                  data=json.dumps({
                                      'username': 'newuser',
                                      'phone': '123456',  # 无效手机号
                                      'password': 'newpassword',
                                      'name': '新用户',
                                      'role': 'recorder'
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 400)
        self.assertEqual(data['message'], '手机号格式不正确')

if __name__ == '__main__':
    unittest.main()