from app import db
from datetime import datetime
import json

class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    recorder_id = db.Column(db.Integer, db.ForeignKey('recorders.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    visit_date = db.Column(db.Date, nullable=False)
    visit_time = db.Column(db.Time, nullable=False)
    location_lat = db.Column(db.Numeric(10,8))  # GPS纬度
    location_lng = db.Column(db.Numeric(11,8))  # GPS经度
    location_address = db.Column(db.Text)
    vital_signs = db.Column(db.Text)  # JSON格式存储生命体征
    symptoms = db.Column(db.Text)  # 症状记录
    notes = db.Column(db.Text)  # 记录员备注
    audio_file = db.Column(db.String(255))  # 录音文件URL
    photos = db.Column(db.Text)  # JSON格式存储照片URLs
    patient_signature = db.Column(db.String(255))  # 患者签名图片URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    medical_orders = db.relationship('MedicalOrder', backref='health_record')
    
    def get_vital_signs(self):
        return json.loads(self.vital_signs) if self.vital_signs else {}
    
    def set_vital_signs(self, vital_signs_dict):
        self.vital_signs = json.dumps(vital_signs_dict, ensure_ascii=False)
    
    def get_photos(self):
        return json.loads(self.photos) if self.photos else []
    
    def set_photos(self, photos_list):
        self.photos = json.dumps(photos_list, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'recorder_id': self.recorder_id,
            'appointment_id': self.appointment_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'visit_time': self.visit_time.isoformat() if self.visit_time else None,
            'location_lat': float(self.location_lat) if self.location_lat else None,
            'location_lng': float(self.location_lng) if self.location_lng else None,
            'location_address': self.location_address,
            'vital_signs': self.get_vital_signs(),
            'symptoms': self.symptoms,
            'notes': self.notes,
            'audio_file': self.audio_file,
            'photos': self.get_photos(),
            'patient_signature': self.patient_signature,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MedicalOrder(db.Model):
    __tablename__ = 'medical_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    health_record_id = db.Column(db.Integer, db.ForeignKey('health_records.id'))
    order_type = db.Column(db.Enum('medication', 'examination', 'lifestyle', 'followup'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    dosage = db.Column(db.String(100))  # 用于药物医嘱
    frequency = db.Column(db.String(50))  # 用于药物医嘱
    duration = db.Column(db.String(50))  # 用于药物医嘱
    notes = db.Column(db.Text)
    status = db.Column(db.Enum('active', 'completed', 'cancelled'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'health_record_id': self.health_record_id,
            'order_type': self.order_type,
            'content': self.content,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'duration': self.duration,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }