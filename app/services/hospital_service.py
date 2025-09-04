from app.models.hospital import PartnerHospital, HospitalDepartment, HospitalDoctor, HospitalAppointment
from app.models.patient import Patient
from app import db
from sqlalchemy import and_, or_
from datetime import datetime

class HospitalService:
    
    @staticmethod
    def get_hospitals(search=None, department=None):
        """获取合作医院列表"""
        query = db.session.query(PartnerHospital)\
            .filter(PartnerHospital.cooperation_status == 'active')
        
        if search:
            query = query.filter(
                or_(
                    PartnerHospital.name.contains(search),
                    PartnerHospital.address.contains(search)
                )
            )
        
        if department:
            query = query.filter(PartnerHospital.departments.contains(department))
        
        hospitals = query.order_by(PartnerHospital.name).all()
        
        result = []
        for hospital in hospitals:
            result.append(hospital.to_dict())
        
        return result
    
    @staticmethod
    def get_hospital_departments(hospital_id):
        """获取医院科室列表"""
        departments = db.session.query(HospitalDepartment)\
            .filter(
                and_(
                    HospitalDepartment.hospital_id == hospital_id,
                    HospitalDepartment.is_active == True
                )
            )\
            .order_by(HospitalDepartment.name)\
            .all()
        
        result = []
        for department in departments:
            result.append(department.to_dict())
        
        return result
    
    @staticmethod
    def get_department_doctors(hospital_id, department_id):
        """获取科室医生列表"""
        doctors = db.session.query(HospitalDoctor)\
            .filter(
                and_(
                    HospitalDoctor.hospital_id == hospital_id,
                    HospitalDoctor.department_id == department_id,
                    HospitalDoctor.is_available == True
                )
            )\
            .order_by(HospitalDoctor.name)\
            .all()
        
        result = []
        for doctor in doctors:
            result.append(doctor.to_dict())
        
        return result
    
    @staticmethod
    def create_hospital_appointment(data):
        """创建医院预约"""
        try:
            appointment = HospitalAppointment(
                patient_id=int(data['patient_id']),
                recorder_id=int(data['recorder_id']),
                hospital_id=int(data['hospital_id']),
                department_id=int(data['department_id']),
                doctor_id=int(data['doctor_id']) if data.get('doctor_id') else None,
                appointment_date=datetime.strptime(data['appointment_date'], '%Y-%m-%d').date(),
                appointment_time=datetime.strptime(data['appointment_time'], '%H:%M').time(),
                notes=data.get('notes', '')
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            return appointment
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_hospital_appointment(appointment_id, recorder_id):
        """获取医院预约详情"""
        appointment = db.session.query(HospitalAppointment)\
            .join(Patient)\
            .join(PartnerHospital)\
            .join(HospitalDepartment)\
            .filter(
                and_(
                    HospitalAppointment.id == appointment_id,
                    HospitalAppointment.recorder_id == recorder_id
                )
            ).first()
        
        if not appointment:
            return None
        
        result = appointment.to_dict()
        result['patient_name'] = appointment.patient.name
        result['hospital_name'] = appointment.hospital.name
        result['department_name'] = appointment.department.name
        
        if appointment.doctor:
            result['doctor_name'] = appointment.doctor.name
        
        return result
    
    @staticmethod
    def update_hospital_appointment(appointment_id, recorder_id, data):
        """更新医院预约结果"""
        appointment = db.session.query(HospitalAppointment)\
            .filter(
                and_(
                    HospitalAppointment.id == appointment_id,
                    HospitalAppointment.recorder_id == recorder_id
                )
            ).first()
        
        if not appointment:
            return None
        
        # 更新字段
        if 'status' in data:
            appointment.status = data['status']
        
        if 'appointment_number' in data:
            appointment.appointment_number = data['appointment_number']
        
        if 'fee' in data:
            appointment.fee = data['fee']
        
        if 'result_notes' in data:
            appointment.result_notes = data['result_notes']
        
        appointment.updated_at = datetime.utcnow()
        
        db.session.commit()
        return appointment.to_dict()