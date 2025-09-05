from app import db
from datetime import datetime

class ServicePackage(db.Model):
    __tablename__ = 'service_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 套餐名称（如：贴心关怀型）
    description = db.Column(db.Text)  # 套餐描述
    price = db.Column(db.Numeric(10,2), nullable=False)  # 月费价格
    duration_days = db.Column(db.Integer, nullable=False)  # 套餐时长（天）
    service_frequency = db.Column(db.Integer, nullable=False)  # 服务频率（次/月）
    service_items = db.Column(db.Text)  # JSON格式存储服务项目
    
    # 新增字段用于10级套餐
    target_users = db.Column(db.Text)  # 目标用户群体描述
    staff_level = db.Column(db.String(50))  # 服务人员等级（护理员/护士/主管护师/专家）
    hospital_level = db.Column(db.String(100))  # 合作医院等级
    service_time = db.Column(db.String(200))  # 服务时间描述
    service_content = db.Column(db.Text)  # 详细服务内容（JSON格式）
    additional_services = db.Column(db.Text)  # 增值服务（JSON格式）
    monitoring_items = db.Column(db.Text)  # 健康监测项目（JSON格式）
    report_frequency = db.Column(db.String(50))  # 报告频率
    gifts_included = db.Column(db.Text)  # 包含的礼品（JSON格式）
    
    package_level = db.Column(db.Integer, nullable=False)  # 套餐等级（1-10）
    is_active = db.Column(db.Boolean, default=True)
    is_system_default = db.Column(db.Boolean, default=False)  # 是否为系统默认套餐
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    subscriptions = db.relationship('PatientSubscription', backref='package')
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'duration_days': self.duration_days,
            'service_frequency': self.service_frequency,
            'target_users': self.target_users,
            'staff_level': self.staff_level,
            'hospital_level': self.hospital_level,
            'service_time': self.service_time,
            'service_content': json.loads(self.service_content) if self.service_content else [],
            'additional_services': json.loads(self.additional_services) if self.additional_services else [],
            'monitoring_items': json.loads(self.monitoring_items) if self.monitoring_items else [],
            'report_frequency': self.report_frequency,
            'gifts_included': json.loads(self.gifts_included) if self.gifts_included else [],
            'package_level': self.package_level,
            'is_active': self.is_active,
            'is_system_default': self.is_system_default,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PatientSubscription(db.Model):
    __tablename__ = 'patient_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('service_packages.id'), nullable=False)
    recorder_id = db.Column(db.Integer, db.ForeignKey('recorders.id'))  # 分配的记录员
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('active', 'paused', 'cancelled', 'expired'), default='active')
    payment_status = db.Column(db.Enum('paid', 'unpaid', 'refunded'), default='unpaid')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'package_id': self.package_id,
            'recorder_id': self.recorder_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    recorder_id = db.Column(db.Integer, db.ForeignKey('recorders.id'), nullable=False)
    service_type_id = db.Column(db.Integer, db.ForeignKey('service_types.id'))  # 新增：服务类型外键
    scheduled_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)  # 重命名：开始时间
    end_time = db.Column(db.Time)  # 新增：结束时间
    appointment_type = db.Column(db.Enum('regular', 'makeup', 'emergency'), default='regular')
    status = db.Column(db.Enum('scheduled', 'confirmed', 'completed', 'cancelled', 'rescheduled'), default='scheduled')  # 新增confirmed和rescheduled状态
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    health_record = db.relationship('HealthRecord', backref='appointment', uselist=False)
    payments = db.relationship('Payment', backref='appointment', cascade='all, delete-orphan')
    
    def to_dict(self, include_patient=False, include_payment=False):
        from datetime import datetime, time
        
        # 计算持续时间
        duration_minutes = None
        if self.start_time and self.end_time:
            start_dt = datetime.combine(datetime.today(), self.start_time)
            end_dt = datetime.combine(datetime.today(), self.end_time)
            duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
        
        result = {
            'id': self.id,
            'patient_id': self.patient_id,
            'recorder_id': self.recorder_id,
            'service_type_id': self.service_type_id,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': duration_minutes,
            'appointment_type': self.appointment_type,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 包含患者信息
        if include_patient and hasattr(self, 'patient') and self.patient:
            result['patient'] = {
                'id': self.patient.id,
                'name': self.patient.name,
                'age': self.patient.age,
                'gender': self.patient.gender,
                'relationship': self.patient.relationship,
                'phone': self.patient.phone,
                'family_id': self.patient.family_id,
                'family': {
                    'householdHead': self.patient.family.householdHead if self.patient.family else '',
                    'address': self.patient.family.address if self.patient.family else '',
                    'phone': self.patient.family.phone if self.patient.family else ''
                } if self.patient.family else None
            }
        
        # 包含支付信息
        if include_payment and self.payments:
            latest_payment = self.payments[-1] if self.payments else None
            if latest_payment:
                result['payment'] = {
                    'id': latest_payment.id,
                    'amount': float(latest_payment.amount) if latest_payment.amount else 0,
                    'payment_status': latest_payment.payment_status,
                    'payment_method': latest_payment.payment_method,
                    'payment_date': latest_payment.payment_date.isoformat() if latest_payment.payment_date else None
                }
        
        return result

class ServiceType(db.Model):
    __tablename__ = 'service_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 服务类型名称
    description = db.Column(db.Text)  # 描述
    default_duration = db.Column(db.Integer)  # 默认时长（分钟）
    base_price = db.Column(db.Numeric(10,2))  # 基础价格
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    appointments = db.relationship('Appointment', backref='service_type')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'default_duration': self.default_duration,
            'base_price': float(self.base_price) if self.base_price else 0,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    payment_method = db.Column(db.Enum('wechat', 'alipay', 'cash', 'bank_card', 'other'), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded'), default='pending')
    transaction_id = db.Column(db.String(100))  # 第三方交易ID
    payment_date = db.Column(db.DateTime)
    refund_amount = db.Column(db.Numeric(10,2), default=0)
    refund_date = db.Column(db.DateTime)
    refund_reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'amount': float(self.amount) if self.amount else 0,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'refund_amount': float(self.refund_amount) if self.refund_amount else 0,
            'refund_date': self.refund_date.isoformat() if self.refund_date else None,
            'refund_reason': self.refund_reason,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }