import os
from app import create_app, db
from app.models.user import User, Recorder, Doctor
from app.models.patient import Family, Patient
from app.models.appointment import ServicePackage, PatientSubscription, Appointment
from app.models.health_record import HealthRecord, MedicalOrder
from app.models.hospital import PartnerHospital, HospitalDepartment, HospitalDoctor, HospitalAppointment

# 获取配置环境
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

# 创建CLI命令
@app.cli.command()
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库初始化完成')

@app.cli.command()
def drop_db():
    """删除数据库"""
    db.drop_all()
    print('数据库已删除')

@app.cli.command()
def create_admin():
    """创建管理员用户"""
    from werkzeug.security import generate_password_hash
    
    username = input('请输入管理员用户名: ')
    password = input('请输入管理员密码: ')
    name = input('请输入管理员姓名: ')
    phone = input('请输入管理员手机号: ')
    
    admin = User(
        username=username,
        phone=phone,
        password_hash=generate_password_hash(password),
        role='admin',
        name=name
    )
    
    db.session.add(admin)
    db.session.commit()
    
    print(f'管理员用户 {username} 创建成功')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Recorder': Recorder,
        'Doctor': Doctor,
        'Family': Family,
        'Patient': Patient,
        'ServicePackage': ServicePackage,
        'PatientSubscription': PatientSubscription,
        'Appointment': Appointment,
        'HealthRecord': HealthRecord,
        'MedicalOrder': MedicalOrder,
        'PartnerHospital': PartnerHospital,
        'HospitalDepartment': HospitalDepartment,
        'HospitalDoctor': HospitalDoctor,
        'HospitalAppointment': HospitalAppointment
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)