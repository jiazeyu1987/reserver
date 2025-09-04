from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('recorder', 'admin', 'doctor'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(255))
    status = db.Column(db.Enum('active', 'inactive', 'suspended'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    recorder = db.relationship('Recorder', backref='user', uselist=False, cascade='all, delete-orphan')
    doctor = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'role': self.role,
            'avatar': self.avatar,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Recorder(db.Model):
    __tablename__ = 'recorders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    qualification_cert = db.Column(db.String(255))  # 资格证件URL
    health_cert = db.Column(db.String(255))  # 健康证URL
    cert_expiry_date = db.Column(db.Date)
    work_area = db.Column(db.Text)  # JSON格式存储工作区域
    is_on_duty = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    appointments = db.relationship('Appointment', backref='recorder')
    health_records = db.relationship('HealthRecord', backref='recorder')
    hospital_appointments = db.relationship('HospitalAppointment', backref='recorder')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'qualification_cert': self.qualification_cert,
            'health_cert': self.health_cert,
            'cert_expiry_date': self.cert_expiry_date.isoformat() if self.cert_expiry_date else None,
            'is_on_duty': self.is_on_duty,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    hospital = db.Column(db.String(100))
    department = db.Column(db.String(100))
    title = db.Column(db.String(50))  # 职称
    consultation_fee = db.Column(db.Numeric(8,2))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    medical_orders = db.relationship('MedicalOrder', backref='doctor')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'license_number': self.license_number,
            'specialty': self.specialty,
            'hospital': self.hospital,
            'department': self.department,
            'title': self.title,
            'consultation_fee': float(self.consultation_fee) if self.consultation_fee else None,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }