from app import db
from datetime import datetime, date
import json

class Family(db.Model):
    __tablename__ = 'families'
    
    id = db.Column(db.Integer, primary_key=True)
    # 修改为符合客户端的字段名
    householdHead = db.Column(db.String(100), nullable=False)  # 户主姓名
    address = db.Column(db.Text, nullable=False)  # 家庭地址
    phone = db.Column(db.String(20), nullable=False)  # 联系电话
    emergency_contact = db.Column(db.String(100))  # 紧急联系人（可选）
    emergency_phone = db.Column(db.String(20))  # 紧急联系电话（可选）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    members = db.relationship('Patient', backref='family', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_members=False):
        result = {
            'id': self.id,
            'householdHead': self.householdHead,
            'address': self.address,
            'phone': self.phone,
            'totalMembers': len(self.members),
            'lastService': self.get_last_service_date(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_members:
            result['members'] = [member.to_dict() for member in self.members if member.is_active]
            
        return result
    
    def get_last_service_date(self):
        """获取最近服务日期"""
        from app.models.health_record import HealthRecord
        last_record = db.session.query(HealthRecord)\
            .join(Patient)\
            .filter(Patient.family_id == self.id)\
            .order_by(HealthRecord.visit_date.desc())\
            .first()
        return last_record.visit_date.strftime('%Y-%m-%d') if last_record else None

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 姓名
    age = db.Column(db.Integer, nullable=False)  # 年龄（改为直接存储年龄）
    gender = db.Column(db.String(10), nullable=False)  # 性别：男/女
    relationship = db.Column(db.String(20), nullable=False)  # 与户主关系
    conditions = db.Column(db.Text)  # 健康状况（简单文本）
    packageType = db.Column(db.String(50), nullable=False, default='基础套餐')  # 套餐类型
    paymentStatus = db.Column(db.String(20), nullable=False, default='normal')  # 支付状态
    lastService = db.Column(db.Date)  # 最近服务日期
    medications = db.Column(db.Text)  # 用药情况（简单文本）
    id_card = db.Column(db.String(18))  # 身份证号（可选）
    phone = db.Column(db.String(20))  # 个人电话（可选）
    is_active = db.Column(db.Boolean, default=True)  # 是否激活
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    health_records = db.relationship('HealthRecord', backref='patient', lazy=True)
    subscriptions = db.relationship('PatientSubscription', backref='patient', lazy=True)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    hospital_appointments = db.relationship('HospitalAppointment', backref='patient', lazy=True)
    medical_orders = db.relationship('MedicalOrder', backref='patient', lazy=True)
    
    @property
    def birth_date(self):
        """根据年龄计算出生年份（估算）"""
        current_year = date.today().year
        return date(current_year - self.age, 1, 1)  # 简化为1月1日
    
    def get_conditions_list(self):
        """将健康状况字符串转为列表"""
        if not self.conditions:
            return []
        return [condition.strip() for condition in self.conditions.split(',') if condition.strip()]
    
    def set_conditions_list(self, conditions_list):
        """将健康状况列表转为字符串存储"""
        self.conditions = ', '.join(conditions_list) if conditions_list else ''
    
    def get_medications_list(self):
        """将用药情况字符串转为列表"""
        if not self.medications:
            return []
        return [med.strip() for med in self.medications.split(',') if med.strip()]
    
    def set_medications_list(self, medications_list):
        """将用药情况列表转为字符串存储"""
        self.medications = ', '.join(medications_list) if medications_list else ''
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'relationship': self.relationship,
            'conditions': self.get_conditions_list(),
            'packageType': self.packageType,
            'paymentStatus': self.paymentStatus,
            'lastService': self.lastService.strftime('%Y-%m-%d') if self.lastService else None,
            'medications': self.get_medications_list(),
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }