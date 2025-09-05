import json
from datetime import datetime
from flask import request

def validate_health_record(request):
    """验证健康记录数据"""
    required_fields = ['patient_id', 'visit_date', 'visit_time']
    
    for field in required_fields:
        if field not in request.form or not request.form[field]:
            return f'缺少必填字段: {field}'
    
    # 验证日期格式
    try:
        datetime.strptime(request.form['visit_date'], '%Y-%m-%d')
    except ValueError:
        return '日期格式错误，应为YYYY-MM-DD'
    
    # 验证时间格式
    try:
        datetime.strptime(request.form['visit_time'], '%H:%M')
    except ValueError:
        return '时间格式错误，应为HH:MM'
    
    return None

def validate_family_data(data, is_update=False):
    """验证家庭数据"""
    from flask import current_app
    
    if not data:
        return '请求数据不能为空'
    
    # 创建时的必填字段
    if not is_update:
        # 户主基本信息必填字段
        required_household_fields = ['householdHead', 'householdHeadAge', 'householdHeadGender', 
                                   'householdHeadPackageType', 'address']
        
        for field in required_household_fields:
            if field not in data or not data[field]:
                return f'缺少户主信息必填字段: {field}'
        
        # 验证户主年龄
        try:
            age = int(data['householdHeadAge'])
            if age < 0 or age > 150:
                return '户主年龄应在0-150之间'
        except (ValueError, TypeError):
            return '户主年龄必须是数字'
        
        # 验证户主性别
        if data['householdHeadGender'] not in ['男', '女']:
            return '户主性别只能是"男"或"女"'
        
        # 验证户主套餐类型
        if data['householdHeadPackageType']:
            from app.models.appointment import ServicePackage
            valid_packages = [pkg.name for pkg in ServicePackage.query.filter_by(is_active=True).all()]
            if valid_packages and data['householdHeadPackageType'] not in valid_packages:
                return f'户主套餐类型必须是以下之一: {", ".join(valid_packages[:5])}'
        
        # 验证家庭成员数据（现在可以为空，因为户主不在members中）
        members = data.get('members', [])
        if not isinstance(members, list):
            return 'members字段必须是数组类型'
        
        for i, member in enumerate(members):
            member_error = validate_patient_data(member, is_member=True)
            if member_error:
                return f'第{i+1}个成员数据错误: {member_error}'
    
    return None

def validate_patient_data(data, is_update=False, is_member=False):
    """验证患者/家庭成员数据"""
    if not data:
        return '成员数据不能为空'
    
    # 创建时的必填字段
    if not is_update:
        required_fields = ['name', 'age', 'gender', 'relationship']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return f'缺少必填字段: {field}'
    
    # 验证年龄
    if 'age' in data:
        try:
            age = int(data['age'])
            if age < 0 or age > 150:
                return '年龄应在0-150之间'
        except (ValueError, TypeError):
            return '年龄必须是数字'
    
    # 验证性别
    if 'gender' in data and data['gender']:
        if data['gender'] not in ['男', '女']:
            return '性别只能是"男"或"女"'
    
    # 家庭成员不需要验证套餐类型（只有户主有套餐类型）
    # 套餐类型验证已移至户主信息验证中
    
    # 验证支付状态
    if 'paymentStatus' in data and data['paymentStatus']:
        valid_statuses = ['normal', 'overdue', 'suspended']
        if data['paymentStatus'] not in valid_statuses:
            return f'支付状态必须是: {", ".join(valid_statuses)}'
    
    # 成员手机号字段可以为空，不进行格式验证
    # 如果需要验证手机号格式，可以在这里添加，但现在跳过所有验证
    
    return None

def validate_appointment(data):
    """验证预约数据"""
    required_fields = ['patient_id', 'scheduled_date', 'scheduled_time']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return f'缺少必填字段: {field}'
    
    # 验证预约时间不能是过去时间
    try:
        appointment_datetime = datetime.combine(
            datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date(),
            datetime.strptime(data['scheduled_time'], '%H:%M').time()
        )
        
        if appointment_datetime <= datetime.now():
            return '预约时间不能是过去时间'
    except ValueError:
        return '日期或时间格式错误'
    
    return None

def validate_hospital_appointment(data):
    """验证医院预约数据"""
    required_fields = ['patient_id', 'hospital_id', 'department_id', 'appointment_date', 'appointment_time']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return f'缺少必填字段: {field}'
    
    # 验证日期格式
    try:
        datetime.strptime(data['appointment_date'], '%Y-%m-%d')
    except ValueError:
        return '日期格式错误，应为YYYY-MM-DD'
    
    # 验证时间格式
    try:
        datetime.strptime(data['appointment_time'], '%H:%M')
    except ValueError:
        return '时间格式错误，应为HH:MM'
    
    return None