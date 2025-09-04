from app import db
from datetime import datetime

class ServicePackage(db.Model):
    __tablename__ = 'service_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10,2), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)  # 套餐时长（天）
    service_frequency = db.Column(db.Integer, nullable=False)  # 服务频率（次/月）
    service_items = db.Column(db.Text)  # JSON格式存储服务项目
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    subscriptions = db.relationship('PatientSubscription', backref='package')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'duration_days': self.duration_days,
            'service_frequency': self.service_frequency,
            'is_active': self.is_active,
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
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    appointment_type = db.Column(db.Enum('regular', 'makeup', 'emergency'), default='regular')
    status = db.Column(db.Enum('scheduled', 'confirmed', 'completed', 'cancelled', 'rescheduled'), default='scheduled')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    health_record = db.relationship('HealthRecord', backref='appointment', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'recorder_id': self.recorder_id,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'appointment_type': self.appointment_type,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }