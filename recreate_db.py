"""
重新创建数据库
"""

import os
import sys
from app import create_app, db
from app.models.user import User, Recorder, Doctor
from app.models.patient import Family, Patient
from app.models.appointment import ServicePackage, PatientSubscription, Appointment, ServiceType, Payment
from app.models.hospital import PartnerHospital, HospitalDepartment
from werkzeug.security import generate_password_hash
from datetime import datetime, date, time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def recreate_database():
    """重新创建数据库"""
    app = create_app('development')
    
    with app.app_context():
        print("删除所有表...")
        db.drop_all()
        
        print("创建所有表...")
        db.create_all()
        
        print("插入测试数据...")
        
        # 创建管理员
        admin = User(
            username='admin',
            phone='13800138000',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            name='系统管理员'
        )
        db.session.add(admin)
        
        # 创建记录员
        recorder_user = User(
            username='recorder001',
            phone='13800138001',
            password_hash=generate_password_hash('recorder123'),
            role='recorder',
            name='记录员001'
        )
        db.session.add(recorder_user)
        db.session.flush()
        
        recorder = Recorder(
            user_id=recorder_user.id,
            employee_id='EMP001',
            is_on_duty=True
        )
        db.session.add(recorder)
        
        # 创建测试家庭和患者
        family = Family(
            householdHead='张老三',
            address='北京市朝阳区某某街道100号',
            phone='13800138003',
            emergency_contact='张太太',
            emergency_phone='13800138004'
        )
        db.session.add(family)
        db.session.flush()
        
        patient1 = Patient(
            family_id=family.id,
            name='张老三',
            age=74,
            gender='男',
            relationship='户主',
            conditions='高血压',
            packageType='基础套餐',
            paymentStatus='normal',
            phone='13800138005',
            is_active=True
        )
        db.session.add(patient1)
        
        patient2 = Patient(
            family_id=family.id,
            name='张小三',
            age=44,
            gender='女',
            relationship='女儿',
            conditions='无特殊疾病',
            packageType='高级套餐',
            paymentStatus='normal',
            phone='13800138006',
            is_active=True
        )
        db.session.add(patient2)
        
        # 创建服务类型
        service_type1 = ServiceType(
            name='基础健康监测',
            description='基本的生命体征监测，包括血压、心率、血糖等',
            default_duration=60,
            base_price=200.00,
            is_active=True
        )
        db.session.add(service_type1)
        
        service_type2 = ServiceType(
            name='综合健康评估',
            description='全面的健康状态评估和建议',
            default_duration=90,
            base_price=350.00,
            is_active=True
        )
        db.session.add(service_type2)
        
        service_type3 = ServiceType(
            name='康复训练指导',
            description='专业的康复训练指导和辅助',
            default_duration=120,
            base_price=400.00,
            is_active=True
        )
        db.session.add(service_type3)
        
        db.session.flush()
        
        # 创建示例预约
        appointment1 = Appointment(
            patient_id=patient1.id,
            recorder_id=recorder.id,
            service_type_id=service_type1.id,
            scheduled_date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            appointment_type='regular',
            status='scheduled',
            notes='第一次健康监测'
        )
        db.session.add(appointment1)
        db.session.flush()
        
        # 为预约创建支付记录
        payment1 = Payment(
            appointment_id=appointment1.id,
            patient_id=patient1.id,
            amount=200.00,
            payment_method='wechat',
            payment_status='pending',
            notes='微信支付'
        )
        db.session.add(payment1)
        
        appointment2 = Appointment(
            patient_id=patient2.id,
            recorder_id=recorder.id,
            service_type_id=service_type2.id,
            scheduled_date=date.today(),
            start_time=time(14, 0),
            end_time=time(15, 30),
            appointment_type='regular',
            status='confirmed',
            notes='综合健康评估预约'
        )
        db.session.add(appointment2)
        db.session.flush()
        
        payment2 = Payment(
            appointment_id=appointment2.id,
            patient_id=patient2.id,
            amount=350.00,
            payment_method='alipay',
            payment_status='paid',
            notes='支付宝已付'
        )
        db.session.add(payment2)
        
        # 提交所有更改
        try:
            db.session.commit()
            print("数据库重新创建完成！")
            print("\n登录信息：")
            print("管理员: admin / admin123")
            print("记录员: recorder001 / recorder123")
        except Exception as e:
            db.session.rollback()
            print(f"数据库创建失败: {e}")
            raise e

if __name__ == '__main__':
    recreate_database()