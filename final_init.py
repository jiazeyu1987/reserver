"""
最终版数据库初始化脚本
确保在db.create_all()之前正确导入所有模型并插入测试数据
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """初始化数据库"""
    from app import create_app, db
    from app.models.user import User, Recorder, Doctor
    from app.models.patient import Family, Patient
    from app.models.appointment import ServicePackage, PatientSubscription
    from app.models.hospital import PartnerHospital, HospitalDepartment
    from werkzeug.security import generate_password_hash
    from datetime import datetime, date
    
    app = create_app('development')
    
    with app.app_context():
        # 关键：在create_all之前导入所有模型
        # 这确保模型被正确注册到db.metadata中
        
        # 打印数据库URL确认
        print(f"数据库URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 检查模型是否正确注册
        print(f"已注册的表: {list(db.metadata.tables.keys())}")
        
        # 创建所有表
        print("正在创建数据库表...")
        db.create_all()
        print("数据库表创建完成")
        
        # 检查表是否真的创建了
        try:
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"数据库中的表: {tables}")
        except Exception as e:
            print(f"检查表时出错: {e}")
        
        # 检查是否已有数据
        try:
            user_count = db.session.query(User).count()
            if user_count > 0:
                print("数据库已有数据，跳过初始化")
                return
        except Exception as e:
            print(f"检查数据时出错: {e}")
            print("继续初始化...")
        
        # 如果没有表，说明创建失败
        if not tables:
            print("警告：没有表被创建！")
            return
        
        # 创建测试用户
        print("创建测试用户...")
        
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
        
        # 创建医生
        doctor_user = User(
            username='doctor001',
            phone='13800138002',
            password_hash=generate_password_hash('doctor123'),
            role='doctor',
            name='医生001'
        )
        db.session.add(doctor_user)
        db.session.flush()
        
        doctor = Doctor(
            user_id=doctor_user.id,
            license_number='DOC001',
            specialty='内科',
            hospital='协和医院',
            department='心内科',
            title='主治医师'
        )
        db.session.add(doctor)
        db.session.flush()
        
        # 创建测试家庭和患者
        print("创建测试家庭和患者...")
        
        family = Family(
            family_name='张氏家庭',
            primary_address='北京市朝阳区某某街道100号',
            contact_phone='13800138003',
            emergency_contact='张太太',
            emergency_phone='13800138004'
        )
        db.session.add(family)
        db.session.flush()
        
        patient1 = Patient(
            family_id=family.id,
            name='张老三',
            gender='male',
            birth_date=date(1950, 5, 15),
            phone='13800138005',
            relationship_to_head='户主',
            is_active=True
        )
        db.session.add(patient1)
        db.session.flush()
        
        patient2 = Patient(
            family_id=family.id,
            name='张小三',
            gender='female',
            birth_date=date(1980, 8, 20),
            phone='13800138006',
            relationship_to_head='女儿',
            is_active=True
        )
        db.session.add(patient2)
        db.session.flush()
        
        # 创建服务套餐
        print("创建服务套餐...")
        
        package1 = ServicePackage(
            name='基础健康监护',
            description='每月4次基础健康检查服务',
            price=800.00,
            duration_days=30,
            service_frequency=4
        )
        db.session.add(package1)
        db.session.flush()
        
        package2 = ServicePackage(
            name='高级健康监护',
            description='每月8次全面健康检查服务',
            price=1500.00,
            duration_days=30,
            service_frequency=8
        )
        db.session.add(package2)
        db.session.flush()
        
        # 创建患者订阅
        print("创建患者订阅...")
        
        subscription1 = PatientSubscription(
            patient_id=patient1.id,
            package_id=package1.id,
            recorder_id=recorder.id,
            start_date=date.today(),
            end_date=date(2024, 12, 31),
            status='active',
            payment_status='paid'
        )
        db.session.add(subscription1)
        
        subscription2 = PatientSubscription(
            patient_id=patient2.id,
            package_id=package2.id,
            recorder_id=recorder.id,
            start_date=date.today(),
            end_date=date(2024, 12, 31),
            status='active',
            payment_status='paid'
        )
        db.session.add(subscription2)
        
        # 创建合作医院
        print("创建合作医院...")
        
        hospital = PartnerHospital(
            name='北京协和医院',
            address='北京市东城区帅府园1号',
            phone='010-69151188',
            level='三甲',
            cooperation_status='active'
        )
        db.session.add(hospital)
        db.session.flush()
        
        department = HospitalDepartment(
            hospital_id=hospital.id,
            name='心内科',
            description='心血管疾病诊疗科室',
            is_active=True
        )
        db.session.add(department)
        
        # 提交所有更改
        try:
            db.session.commit()
            print("数据库初始化完成！")
            print("\n登录信息：")
            print("管理员: admin / admin123")
            print("记录员: recorder001 / recorder123")
            print("医生: doctor001 / doctor123")
        except Exception as e:
            db.session.rollback()
            print(f"数据库初始化失败: {e}")

if __name__ == '__main__':
    init_database()