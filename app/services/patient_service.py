from app.models.patient import Patient, Family
from app.models.health_record import HealthRecord
from app.models.appointment import PatientSubscription, Appointment
from app import db
from sqlalchemy import and_, or_
from datetime import datetime, date
import json

class PatientService:
    
    @staticmethod
    def get_recorder_families(recorder_id, page=1, limit=20, search=None):
        """获取记录员负责的家庭列表"""
        query = db.session.query(Family)\
            .join(Patient)\
            .join(PatientSubscription)\
            .filter(PatientSubscription.recorder_id == recorder_id)\
            .distinct()
        
        if search:
            query = query.filter(
                or_(
                    Family.family_name.contains(search),
                    Family.primary_address.contains(search),
                    Patient.name.contains(search)
                )
            )
        
        total = query.count()
        families = query.offset((page - 1) * limit).limit(limit).all()
        
        return {
            'families': [family.to_dict() for family in families],
            'total': total,
            'page': page,
            'limit': limit
        }
    
    @staticmethod
    def get_family_detail(family_id, recorder_id):
        """获取家庭详情（包含患者信息）"""
        family = db.session.query(Family)\
            .join(Patient)\
            .join(PatientSubscription)\
            .filter(
                and_(
                    Family.id == family_id,
                    PatientSubscription.recorder_id == recorder_id
                )
            ).first()
        
        if not family:
            return None
        
        # 获取患者详细信息
        patients_data = []
        for patient in family.patients:
            # 获取最新健康记录
            last_record = db.session.query(HealthRecord)\
                .filter(HealthRecord.patient_id == patient.id)\
                .order_by(HealthRecord.created_at.desc())\
                .first()
            
            # 获取当前套餐
            current_subscription = db.session.query(PatientSubscription)\
                .filter(
                    and_(
                        PatientSubscription.patient_id == patient.id,
                        PatientSubscription.status == 'active'
                    )
                )\
                .first()
            
            patient_data = patient.to_dict()
            patient_data['last_record'] = last_record.to_dict() if last_record else None
            patient_data['current_subscription'] = current_subscription.to_dict() if current_subscription else None
            patients_data.append(patient_data)
        
        result = family.to_dict()
        result['patients'] = patients_data
        return result
    
    @staticmethod
    def create_health_record(data):
        """创建健康记录"""
        try:
            record = HealthRecord(
                patient_id=int(data['patient_id']),
                recorder_id=int(data['recorder_id']),
                appointment_id=int(data.get('appointment_id')) if data.get('appointment_id') else None,
                visit_date=datetime.strptime(data['visit_date'], '%Y-%m-%d').date(),
                visit_time=datetime.strptime(data['visit_time'], '%H:%M').time(),
                location_lat=float(data.get('location_lat')) if data.get('location_lat') else None,
                location_lng=float(data.get('location_lng')) if data.get('location_lng') else None,
                location_address=data.get('location_address'),
                vital_signs=data.get('vital_signs'),
                symptoms=data.get('symptoms'),
                notes=data.get('notes'),
                audio_file=data.get('audio_file'),
                photos=data.get('photos'),
                patient_signature=data.get('patient_signature')
            )
            
            db.session.add(record)
            db.session.commit()
            
            return record
        except Exception as e:
            db.session.rollback()
            raise e