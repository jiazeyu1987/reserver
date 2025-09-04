#!/usr/bin/env python3
"""
测试API功能
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api/v1'

def test_login():
    """测试登录功能"""
    print("1. 测试登录...")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'username': 'recorder001',
        'password': 'recorder123'
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"[SUCCESS] 登录成功: {data['data']['user']['name']}")
        return data['data']['access_token']
    else:
        print(f"[ERROR] 登录失败: {response.status_code} - {response.text}")
        return None

def test_service_types(token):
    """测试获取服务类型"""
    print("\n2. 测试获取服务类型...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/service-types', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"[SUCCESS] 获取服务类型成功，共 {len(data['data'])} 种服务类型:")
        for service_type in data['data']:
            print(f"   - {service_type['name']}: {service_type['base_price']} yuan")
        return data['data']
    else:
        print(f"[ERROR] 获取服务类型失败: {response.status_code} - {response.text}")
        return []

def test_today_appointments(token):
    """测试获取今日预约"""
    print("\n3. 测试获取今日预约...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/appointments/today', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        appointments = data['data']['appointments'] if isinstance(data['data'], dict) else data['data']
        print(f"[SUCCESS] 获取今日预约成功，共 {len(appointments)} 条预约:")
        for appt in appointments:
            print(f"   - {appt['start_time']} {appt['patient']['name']} ({appt['status']})")
        return appointments
    else:
        print(f"[ERROR] 获取今日预约失败: {response.status_code} - {response.text}")
        return []

def test_families(token):
    """测试获取家庭列表"""
    print("\n4. 测试获取家庭列表...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/families', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        families = data['data']['families']
        print(f"[SUCCESS] 获取家庭列表成功，共 {len(families)} 个家庭:")
        for family in families:
            print(f"   - {family['householdHead']} (成员: {family['totalMembers']})")
        return families
    else:
        print(f"[ERROR] 获取家庭列表失败: {response.status_code} - {response.text}")
        return []

def test_create_appointment(token, families, service_types):
    """测试创建预约"""
    print("\n5. 测试创建预约...")
    
    if not families or not service_types:
        print("[ERROR] 缺少必要数据，跳过创建预约测试")
        return None
    
    # 获取第一个家庭的第一个成员
    family = families[0]
    if not family['members']:
        print("[ERROR] 家庭没有成员，跳过创建预约测试")
        return None
    
    patient = family['members'][0]
    service_type = service_types[0]
    
    headers = {'Authorization': f'Bearer {token}'}
    appointment_data = {
        'patient_id': patient['id'],
        'service_type_id': service_type['id'],
        'scheduled_date': '2025-09-04',
        'start_time': '16:00',
        'end_time': '17:00',
        'appointment_type': 'regular',
        'status': 'scheduled',
        'notes': '测试预约',
        'payment': {
            'amount': service_type['base_price'],
            'payment_method': 'wechat',
            'payment_status': 'pending',
            'notes': '微信支付'
        }
    }
    
    response = requests.post(f'{BASE_URL}/appointments', json=appointment_data, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        appointment = data['data']
        print(f"[SUCCESS] 创建预约成功: ID {appointment['id']}")
        print(f"   患者: {appointment['patient']['name']}")
        print(f"   时间: {appointment['start_time']} - {appointment['end_time']}")
        print(f"   费用: {appointment['payment']['amount']} yuan")
        return appointment
    else:
        print(f"[ERROR] 创建预约失败: {response.status_code} - {response.text}")
        return None

def main():
    """主测试函数"""
    print("开始API功能测试...\n")
    
    # 登录获取token
    token = test_login()
    if not token:
        print("[ERROR] 登录失败，无法继续测试")
        return
    
    # 测试各项功能
    service_types = test_service_types(token)
    appointments = test_today_appointments(token)
    families = test_families(token)
    
    # 测试创建预约
    new_appointment = test_create_appointment(token, families, service_types)
    
    print("\n" + "="*50)
    print("测试完成！")
    print("="*50)

if __name__ == '__main__':
    main()