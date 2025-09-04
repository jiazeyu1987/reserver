from app.models.appointment import Appointment
from app.models.patient import Patient
from app import db
from sqlalchemy import and_, or_
from datetime import datetime, date

class AppointmentService:
    
    @staticmethod
    def get_today_appointments(recorder_id):
        """获取今日预约列表"""
        today = date.today()
        appointments = db.session.query(Appointment)\
            .join(Patient)\
            .filter(
                and_(
                    Appointment.recorder_id == recorder_id,
                    Appointment.scheduled_date == today,
                    Appointment.status.in_(['scheduled', 'confirmed'])
                )
            )\
            .order_by(Appointment.scheduled_time)\
            .all()
        
        result = []
        for appointment in appointments:
            result.append({
                'id': appointment.id,
                'patient': {
                    'id': appointment.patient.id,
                    'name': appointment.patient.name,
                    'family_name': appointment.patient.family.family_name if appointment.patient.family else '',
                    'address': appointment.patient.family.primary_address if appointment.patient.family else ''
                },
                'scheduled_time': appointment.scheduled_time.isoformat() if appointment.scheduled_time else None,
                'status': appointment.status,
                'notes': appointment.notes
            })
        
        return result
    
    @staticmethod
    def get_appointments(recorder_id, page=1, limit=20, status=None, date_from=None, date_to=None):
        """获取预约列表"""
        query = db.session.query(Appointment)\
            .join(Patient)\
            .filter(Appointment.recorder_id == recorder_id)
        
        # 状态过滤
        if status:
            query = query.filter(Appointment.status == status)
        
        # 日期范围过滤
        if date_from:
            query = query.filter(Appointment.scheduled_date >= date_from)
        
        if date_to:
            query = query.filter(Appointment.scheduled_date <= date_to)
        
        # 排序
        query = query.order_by(Appointment.scheduled_date.desc(), Appointment.scheduled_time)
        
        total = query.count()
        appointments = query.offset((page - 1) * limit).limit(limit).all()
        
        result = []
        for appointment in appointments:
            result.append({
                'id': appointment.id,
                'patient': {
                    'id': appointment.patient.id,
                    'name': appointment.patient.name
                },
                'scheduled_date': appointment.scheduled_date.isoformat() if appointment.scheduled_date else None,
                'scheduled_time': appointment.scheduled_time.isoformat() if appointment.scheduled_time else None,
                'appointment_type': appointment.appointment_type,
                'status': appointment.status,
                'created_at': appointment.created_at.isoformat() if appointment.created_at else None
            })
        
        return {
            'appointments': result,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    @staticmethod
    def create_appointment(data):
        """创建预约"""
        try:
            appointment = Appointment(
                patient_id=int(data['patient_id']),
                recorder_id=int(data['recorder_id']),
                scheduled_date=datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date(),
                scheduled_time=datetime.strptime(data['scheduled_time'], '%H:%M').time(),
                appointment_type=data.get('appointment_type', 'regular'),
                notes=data.get('notes', '')
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            return appointment
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_appointment(appointment_id, recorder_id, data):
        """更新预约"""
        appointment = db.session.query(Appointment)\
            .filter(
                and_(
                    Appointment.id == appointment_id,
                    Appointment.recorder_id == recorder_id
                )
            ).first()
        
        if not appointment:
            return None
        
        # 更新字段
        if 'scheduled_date' in data:
            appointment.scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date()
        
        if 'scheduled_time' in data:
            appointment.scheduled_time = datetime.strptime(data['scheduled_time'], '%H:%M').time()
        
        if 'appointment_type' in data:
            appointment.appointment_type = data['appointment_type']
        
        if 'status' in data:
            appointment.status = data['status']
        
        if 'notes' in data:
            appointment.notes = data['notes']
        
        appointment.updated_at = datetime.utcnow()
        
        db.session.commit()
        return appointment
    
    @staticmethod
    def complete_appointment(appointment_id, recorder_id):
        """完成预约"""
        appointment = db.session.query(Appointment)\
            .filter(
                and_(
                    Appointment.id == appointment_id,
                    Appointment.recorder_id == recorder_id
                )
            ).first()
        
        if not appointment:
            return None
        
        appointment.status = 'completed'
        appointment.updated_at = datetime.utcnow()
        
        db.session.commit()
        return appointment