from app import db
from datetime import datetime
import json

class Family(db.Model):
    __tablename__ = 'families'
    
    id = db.Column(db.Integer, primary_key=True)
    family_name = db.Column(db.String(100), nullable=False)
    primary_address = db.Column(db.Text, nullable=False)
    secondary_address = db.Column(db.Text)
    contact_phone = db.Column(db.String(20), nullable=False)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    patients = db.relationship('Patient', backref='family', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'family_name': self.family_name,
            'primary_address': self.primary_address,
            'contact_phone': self.contact_phone,
            'patient_count': len(self.patients),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum('male', 'female'), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    id_card = db.Column(db.String(18))
    phone = db.Column(db.String(20))
    relationship_to_head = db.Column(db.String(20), nullable=False)  # 与户主关系
    medical_history = db.Column(db.Text)  # JSON string
    allergies = db.Column(db.Text)
    current_medications = db.Column(db.Text)  # JSON string
    service_preferences = db.Column(db.Text)  # JSON string
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    health_records = db.relationship('HealthRecord', backref='patient', lazy=True)
    subscriptions = db.relationship('PatientSubscription', backref='patient', lazy=True)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    hospital_appointments = db.relationship('HospitalAppointment', backref='patient', lazy=True)
    medical_orders = db.relationship('MedicalOrder', backref='patient', lazy=True)
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    def get_medical_history(self):
        return json.loads(self.medical_history) if self.medical_history else []
    
    def set_medical_history(self, history_list):
        self.medical_history = json.dumps(history_list, ensure_ascii=False)
    
    def get_current_medications(self):
        return json.loads(self.current_medications) if self.current_medications else []
    
    def set_current_medications(self, medications_list):
        self.current_medications = json.dumps(medications_list, ensure_ascii=False)
    
    def get_service_preferences(self):
        return json.loads(self.service_preferences) if self.service_preferences else {}
    
    def set_service_preferences(self, preferences_dict):
        self.service_preferences = json.dumps(preferences_dict, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'phone': self.phone,
            'relationship_to_head': self.relationship_to_head,
            'medical_history': self.get_medical_history(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }