from app import db
from datetime import datetime
import json

class PartnerHospital(db.Model):
    __tablename__ = 'partner_hospitals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    level = db.Column(db.String(20))  # 医院等级
    departments = db.Column(db.Text)  # JSON格式存储科室信息
    cooperation_status = db.Column(db.Enum('active', 'inactive', 'suspended'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    departments_rel = db.relationship('HospitalDepartment', backref='hospital', cascade='all, delete-orphan')
    doctors = db.relationship('HospitalDoctor', backref='hospital')
    appointments = db.relationship('HospitalAppointment', backref='hospital')
    
    def get_departments(self):
        return json.loads(self.departments) if self.departments else []
    
    def set_departments(self, departments_list):
        self.departments = json.dumps(departments_list, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'level': self.level,
            'departments': self.get_departments(),
            'cooperation_status': self.cooperation_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class HospitalDepartment(db.Model):
    __tablename__ = 'hospital_departments'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('partner_hospitals.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    available_times = db.Column(db.Text)  # JSON格式存储可预约时间段
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    doctors = db.relationship('HospitalDoctor', backref='department')
    appointments = db.relationship('HospitalAppointment', backref='department')
    
    def get_available_times(self):
        return json.loads(self.available_times) if self.available_times else []
    
    def set_available_times(self, times_list):
        self.available_times = json.dumps(times_list, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'name': self.name,
            'description': self.description,
            'available_times': self.get_available_times(),
            'is_active': self.is_active
        }

class HospitalDoctor(db.Model):
    __tablename__ = 'hospital_doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('partner_hospitals.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('hospital_departments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(50))
    specialty = db.Column(db.Text)
    schedule = db.Column(db.Text)  # JSON格式存储出诊时间
    consultation_fee = db.Column(db.Numeric(8,2))
    is_available = db.Column(db.Boolean, default=True)
    
    # 关系
    appointments = db.relationship('HospitalAppointment', backref='doctor')
    
    def get_schedule(self):
        return json.loads(self.schedule) if self.schedule else []
    
    def set_schedule(self, schedule_list):
        self.schedule = json.dumps(schedule_list, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'department_id': self.department_id,
            'name': self.name,
            'title': self.title,
            'specialty': self.specialty,
            'consultation_fee': float(self.consultation_fee) if self.consultation_fee else None,
            'is_available': self.is_available
        }

class HospitalAppointment(db.Model):
    __tablename__ = 'hospital_appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    recorder_id = db.Column(db.Integer, db.ForeignKey('recorders.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('partner_hospitals.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('hospital_departments.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('hospital_doctors.id'))
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum('pending', 'confirmed', 'completed', 'cancelled'), default='pending')
    appointment_number = db.Column(db.String(50))  # 预约号
    fee = db.Column(db.Numeric(8,2))
    notes = db.Column(db.Text)
    result_notes = db.Column(db.Text)  # 预约结果备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'recorder_id': self.recorder_id,
            'hospital_id': self.hospital_id,
            'department_id': self.department_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.isoformat() if self.appointment_time else None,
            'status': self.status,
            'appointment_number': self.appointment_number,
            'fee': float(self.fee) if self.fee else None,
            'notes': self.notes,
            'result_notes': self.result_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }