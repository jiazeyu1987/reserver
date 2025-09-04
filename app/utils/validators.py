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