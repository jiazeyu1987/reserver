import requests
import json
import time

# 测试配置
BASE_URL = 'http://localhost:5000'
TEST_USER = {
    'username': 'recorder001',
    'password': 'recorder123'
}

class APITestClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.refresh_token = None
    
    def login(self):
        """用户登录获取token"""
        url = f"{self.base_url}/api/v1/auth/login"
        data = {
            'username': TEST_USER['username'],
            'password': TEST_USER['password']
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.access_token = result['data']['access_token']
            self.refresh_token = result['data']['refresh_token']
            print("[SUCCESS] 登录成功")
            return True
        else:
            print(f"[ERROR] 登录失败: {response.status_code} - {response.text}")
            return False
    
    def get_headers(self):
        """获取认证头部"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def test_create_appointment(self):
        """测试创建预约接口"""
        print("\n--- 测试创建预约接口 ---")
        url = f"{self.base_url}/api/v1/appointments"
        
        # 首先获取一个患者ID
        families_response = requests.get(
            f"{self.base_url}/api/v1/families", 
            headers=self.get_headers()
        )
        
        if families_response.status_code != 200:
            print("[ERROR] 获取家庭列表失败")
            return False
            
        families_data = families_response.json()
        if not families_data.get('data') or len(families_data['data']['families']) == 0:
            print("[ERROR] 没有可用的家庭数据")
            return False
            
        family_id = families_data['data']['families'][0]['id']
        
        # 获取该家庭的患者
        family_detail_response = requests.get(
            f"{self.base_url}/api/v1/families/{family_id}",
            headers=self.get_headers()
        )
        
        if family_detail_response.status_code != 200:
            print("[ERROR] 获取家庭详情失败")
            return False
            
        family_detail = family_detail_response.json()
        if not family_detail.get('data') or len(family_detail['data']['patients']) == 0:
            print("[ERROR] 家庭中没有患者")
            return False
            
        patient_id = family_detail['data']['patients'][0]['id']
        
        # 创建预约
        data = {
            'patient_id': patient_id,
            'scheduled_date': '2025-12-31',
            'scheduled_time': '14:30',
            'appointment_type': 'regular',
            'notes': '测试预约'
        }
        
        response = requests.post(url, json=data, headers=self.get_headers())
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("[SUCCESS] 创建预约成功")
                return result['data'].get('appointment_id')
            else:
                print(f"[ERROR] 创建预约失败: {result.get('message')}")
                return False
        else:
            print(f"[ERROR] 创建预约请求失败: {response.status_code} - {response.text}")
            return False
    
    def test_update_appointment(self, appointment_id):
        """测试更新预约接口"""
        print("\n--- 测试更新预约接口 ---")
        url = f"{self.base_url}/api/v1/appointments/{appointment_id}"
        
        data = {
            'scheduled_date': '2025-12-30',
            'scheduled_time': '15:00',
            'notes': '更新后的测试预约'
        }
        
        response = requests.put(url, json=data, headers=self.get_headers())
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("[SUCCESS] 更新预约成功")
                return True
            else:
                print(f"[ERROR] 更新预约失败: {result.get('message')}")
                return False
        else:
            print(f"[ERROR] 更新预约请求失败: {response.status_code} - {response.text}")
            return False
    
    def test_complete_appointment(self, appointment_id):
        """测试完成预约接口"""
        print("\n--- 测试完成预约接口 ---")
        url = f"{self.base_url}/api/v1/appointments/{appointment_id}/complete"
        
        response = requests.post(url, headers=self.get_headers())
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("[SUCCESS] 完成预约成功")
                return True
            else:
                print(f"[ERROR] 完成预约失败: {result.get('message')}")
                return False
        else:
            print(f"[ERROR] 完成预约请求失败: {response.status_code} - {response.text}")
            return False
    
    def test_create_hospital_appointment(self):
        """测试创建医院预约接口"""
        print("\n--- 测试创建医院预约接口 ---")
        url = f"{self.base_url}/api/v1/hospital-appointments"
        
        # 获取合作医院
        hospitals_response = requests.get(
            f"{self.base_url}/api/v1/hospitals",
            headers=self.get_headers()
        )
        
        if hospitals_response.status_code != 200:
            print("[ERROR] 获取合作医院列表失败")
            return False
            
        hospitals_data = hospitals_response.json()
        if not hospitals_data.get('data') or len(hospitals_data['data']) == 0:
            print("[ERROR] 没有可用的合作医院")
            return False
            
        hospital_id = hospitals_data['data'][0]['id']
        
        # 获取医院科室
        departments_response = requests.get(
            f"{self.base_url}/api/v1/hospitals/{hospital_id}/departments",
            headers=self.get_headers()
        )
        
        if departments_response.status_code != 200:
            print("[ERROR] 获取医院科室列表失败")
            return False
            
        departments_data = departments_response.json()
        if not departments_data.get('data') or len(departments_data['data']) == 0:
            print("[ERROR] 医院没有科室")
            return False
            
        department_id = departments_data['data'][0]['id']
        
        # 获取患者ID（同上）
        families_response = requests.get(
            f"{self.base_url}/api/v1/families", 
            headers=self.get_headers()
        )
        
        if families_response.status_code != 200:
            print("[ERROR] 获取家庭列表失败")
            return False
            
        families_data = families_response.json()
        if not families_data.get('data') or len(families_data['data']['families']) == 0:
            print("[ERROR] 没有可用的家庭数据")
            return False
            
        family_id = families_data['data']['families'][0]['id']
        
        family_detail_response = requests.get(
            f"{self.base_url}/api/v1/families/{family_id}",
            headers=self.get_headers()
        )
        
        if family_detail_response.status_code != 200:
            print("[ERROR] 获取家庭详情失败")
            return False
            
        family_detail = family_detail_response.json()
        if not family_detail.get('data') or len(family_detail['data']['patients']) == 0:
            print("[ERROR] 家庭中没有患者")
            return False
            
        patient_id = family_detail['data']['patients'][0]['id']
        
        # 创建医院预约
        data = {
            'patient_id': patient_id,
            'hospital_id': hospital_id,
            'department_id': department_id,
            'appointment_date': '2025-12-31',
            'appointment_time': '10:00',
            'notes': '测试医院预约'
        }
        
        response = requests.post(url, json=data, headers=self.get_headers())
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("[SUCCESS] 创建医院预约成功")
                return result['data'].get('appointment_id')
            else:
                print(f"[ERROR] 创建医院预约失败: {result.get('message')}")
                return False
        else:
            print(f"[ERROR] 创建医院预约请求失败: {response.status_code} - {response.text}")
            return False
    
    def test_get_hospital_appointment(self, appointment_id):
        """测试获取医院预约详情接口"""
        print("\n--- 测试获取医院预约详情接口 ---")
        url = f"{self.base_url}/api/v1/hospital-appointments/{appointment_id}"
        
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("[SUCCESS] 获取医院预约详情成功")
                return True
            else:
                print(f"[ERROR] 获取医院预约详情失败: {result.get('message')}")
                return False
        else:
            print(f"[ERROR] 获取医院预约详情请求失败: {response.status_code} - {response.text}")
            return False
    
    def test_update_hospital_appointment(self, appointment_id):
        """测试更新医院预约结果接口"""
        print("\n--- 测试更新医院预约结果接口 ---")
        url = f"{self.base_url}/api/v1/hospital-appointments/{appointment_id}"
        
        data = {
            'status': 'confirmed',
            'appointment_number': 'A001',
            'fee': 50.00,
            'result_notes': '预约已确认'
        }
        
        response = requests.put(url, json=data, headers=self.get_headers())
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("[SUCCESS] 更新医院预约结果成功")
                return True
            else:
                print(f"[ERROR] 更新医院预约结果失败: {result.get('message')}")
                return False
        else:
            print(f"[ERROR] 更新医院预约结果请求失败: {response.status_code} - {response.text}")
            return False

def main():
    """主测试函数"""
    print("开始API接口测试...")
    
    client = APITestClient()
    
    # 登录
    if not client.login():
        return
    
    # 测试预约管理接口
    print("\n" + "="*50)
    print("测试预约管理接口")
    print("="*50)
    
    # 测试创建预约
    appointment_id = client.test_create_appointment()
    if not appointment_id:
        print("创建预约测试失败，跳过后续预约测试")
    else:
        # 测试更新预约
        client.test_update_appointment(appointment_id)
        
        # 测试完成预约
        client.test_complete_appointment(appointment_id)
    
    # 测试医院预约接口
    print("\n" + "="*50)
    print("测试医院预约接口")
    print("="*50)
    
    # 测试创建医院预约
    hospital_appointment_id = client.test_create_hospital_appointment()
    if not hospital_appointment_id:
        print("创建医院预约测试失败，跳过后续医院预约测试")
    else:
        # 测试获取医院预约详情
        client.test_get_hospital_appointment(hospital_appointment_id)
        
        # 测试更新医院预约结果
        client.test_update_hospital_appointment(hospital_appointment_id)
    
    print("\n" + "="*50)
    print("API接口测试完成")
    print("="*50)

if __name__ == '__main__':
    main()