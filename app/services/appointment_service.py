from app.models.appointment import Appointment, ServiceType, Payment
from app.models.patient import Patient
from app import db
from sqlalchemy import and_, or_
from datetime import datetime, date
from flask import current_app

class AppointmentService:
    
    @staticmethod
    def get_today_appointments(recorder_id):
        """获取今日预约列表"""
        try:
            current_app.logger.info(f"AppointmentService.get_today_appointments - 获取记录员 {recorder_id} 的今日预约")
            
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
                .order_by(Appointment.start_time)\
                .all()
            
            current_app.logger.info(f"AppointmentService.get_today_appointments - 找到 {len(appointments)} 条今日预约")
            
            result = []
            for appointment in appointments:
                appointment_dict = appointment.to_dict(include_patient=True, include_payment=True)
                result.append(appointment_dict)
            
            return result
        except Exception as e:
            current_app.logger.error(f"AppointmentService.get_today_appointments - 获取今日预约失败: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def get_appointments(recorder_id, page=1, limit=20, status=None, date_from=None, date_to=None):
        """获取预约列表"""
        try:
            current_app.logger.info(f"AppointmentService.get_appointments - 获取记录员 {recorder_id} 的预约列表，页码: {page}, 每页: {limit}")
            
            query = db.session.query(Appointment)\
                .join(Patient)\
                .filter(Appointment.recorder_id == recorder_id)
            
            # 状态过滤
            if status:
                query = query.filter(Appointment.status == status)
                current_app.logger.info(f"AppointmentService.get_appointments - 按状态过滤: {status}")
            
            # 日期范围过滤
            if date_from:
                current_app.logger.info(f"AppointmentService.get_appointments - 添加开始日期过滤: {date_from} (类型: {type(date_from)})")
                query = query.filter(Appointment.scheduled_date >= date_from)
            
            if date_to:
                current_app.logger.info(f"AppointmentService.get_appointments - 添加结束日期过滤: {date_to} (类型: {type(date_to)})")
                query = query.filter(Appointment.scheduled_date <= date_to)
                
            # 🔍 调试：查看过滤后的SQL查询
            current_app.logger.info(f"🔍 调试：过滤后的SQL查询: {str(query)}")
            
            # 🔍 先查看过滤后的查询结果（未分页）
            filtered_appointments = query.all()
            current_app.logger.info(f"🔍 调试：过滤后的预约 (共{len(filtered_appointments)}条):")
            for appt in filtered_appointments:
                current_app.logger.info(f"  - ID:{appt.id}, 患者:{appt.patient.name}, 日期:{appt.scheduled_date}, 时间:{appt.start_time}")
            
            # 🔍 调试：查询该记录员的所有预约看看实际数据
            debug_query = db.session.query(Appointment)\
                .join(Patient)\
                .filter(Appointment.recorder_id == recorder_id)
            debug_appointments = debug_query.all()
            current_app.logger.info(f"🔍 调试：记录员 {recorder_id} 的所有预约:")
            for appt in debug_appointments:
                current_app.logger.info(f"  - ID:{appt.id}, 患者:{appt.patient.name}, 日期:{appt.scheduled_date}, 时间:{appt.start_time}")
            
            # 排序
            query = query.order_by(Appointment.scheduled_date.desc(), Appointment.start_time)
            
            total = query.count()
            appointments = query.offset((page - 1) * limit).limit(limit).all()
            
            current_app.logger.info(f"AppointmentService.get_appointments - 找到 {total} 条预约记录，返回 {len(appointments)} 条")
            
            result = []
            for appointment in appointments:
                appointment_dict = appointment.to_dict(include_patient=True, include_payment=True)
                result.append(appointment_dict)
            
            return {
                'appointments': result,
                'total': total,
                'page': page,
                'limit': limit,
                'totalPages': (total + limit - 1) // limit
            }
        except Exception as e:
            current_app.logger.error(f"AppointmentService.get_appointments - 获取预约列表失败: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def create_appointment(data, recorder_id):
        """创建预约"""
        try:
            current_app.logger.info(f"AppointmentService.create_appointment - 创建预约，记录员: {recorder_id}, 数据: {data}")
            
            # 创建预约记录
            appointment = Appointment(
                patient_id=data['patient_id'],
                recorder_id=recorder_id,
                service_type_id=data.get('service_type_id'),
                scheduled_date=datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date(),
                start_time=datetime.strptime(data['scheduled_time'], '%H:%M').time(),
                end_time=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
                appointment_type=data.get('appointment_type', 'regular'),
                status=data.get('status', 'scheduled'),
                notes=data.get('notes', '')
            )
            
            db.session.add(appointment)
            db.session.flush()  # 获取appointment.id
            
            # 创建支付记录（如果提供了支付信息）
            if data.get('payment'):
                payment_data = data['payment']
                payment = Payment(
                    appointment_id=appointment.id,
                    patient_id=data['patient_id'],
                    amount=payment_data.get('amount', 0),
                    payment_method=payment_data.get('payment_method', 'cash'),
                    payment_status=payment_data.get('payment_status', 'pending'),
                    notes=payment_data.get('notes', '')
                )
                db.session.add(payment)
            
            db.session.commit()
            current_app.logger.info(f"AppointmentService.create_appointment - 预约创建成功，ID: {appointment.id}")
            
            return appointment
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"AppointmentService.create_appointment - 创建预约失败: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def get_appointment_by_id(appointment_id, recorder_id=None):
        """根据ID获取预约详情"""
        try:
            current_app.logger.info(f"AppointmentService.get_appointment_by_id - 获取预约详情，ID: {appointment_id}, 记录员: {recorder_id}")
            
            query = db.session.query(Appointment).filter(Appointment.id == appointment_id)
            
            # 如果指定了recorder_id，验证权限
            if recorder_id:
                query = query.filter(Appointment.recorder_id == recorder_id)
            
            appointment = query.first()
            if not appointment:
                current_app.logger.warning(f"AppointmentService.get_appointment_by_id - 预约不存在或无权限，ID: {appointment_id}")
                return None
            
            current_app.logger.info(f"AppointmentService.get_appointment_by_id - 找到预约记录: {appointment.id}")
            return appointment.to_dict(include_patient=True, include_payment=True)
        except Exception as e:
            current_app.logger.error(f"AppointmentService.get_appointment_by_id - 获取预约详情失败: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def update_appointment(appointment_id, data, recorder_id=None):
        """更新预约信息"""
        try:
            current_app.logger.info(f"AppointmentService.update_appointment - 更新预约，ID: {appointment_id}, 记录员: {recorder_id}, 数据: {data}")
            
            query = db.session.query(Appointment).filter(Appointment.id == appointment_id)
            
            # 如果指定了recorder_id，验证权限
            if recorder_id:
                query = query.filter(Appointment.recorder_id == recorder_id)
            
            appointment = query.first()
            if not appointment:
                current_app.logger.warning(f"AppointmentService.update_appointment - 预约不存在或无权限，ID: {appointment_id}")
                return None
            
            # 更新预约字段
            if 'patient_id' in data:
                appointment.patient_id = data['patient_id']
            if 'service_type_id' in data:
                appointment.service_type_id = data['service_type_id']
            if 'scheduled_date' in data:
                appointment.scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date()
            if 'scheduled_time' in data:
                appointment.start_time = datetime.strptime(data['scheduled_time'], '%H:%M').time()
            if 'end_time' in data:
                appointment.end_time = datetime.strptime(data['end_time'], '%H:%M').time() if data['end_time'] else None
            if 'appointment_type' in data:
                appointment.appointment_type = data['appointment_type']
            if 'status' in data:
                appointment.status = data['status']
            if 'notes' in data:
                appointment.notes = data['notes']
            
            appointment.updated_at = datetime.utcnow()
            
            # 更新支付信息（如果提供）
            if 'payment' in data and data['payment']:
                payment_data = data['payment']
                
                # 查找现有支付记录
                payment = Payment.query.filter_by(appointment_id=appointment_id).first()
                if payment:
                    # 更新现有支付记录
                    current_app.logger.info(f"AppointmentService.update_appointment - 更新现有支付记录，ID: {payment.id}")
                    if 'amount' in payment_data:
                        payment.amount = payment_data['amount']
                    if 'payment_method' in payment_data:
                        payment.payment_method = payment_data['payment_method']
                    if 'payment_status' in payment_data:
                        payment.payment_status = payment_data['payment_status']
                    if 'notes' in payment_data:
                        payment.notes = payment_data['notes']
                    payment.updated_at = datetime.utcnow()
                else:
                    # 创建新支付记录
                    current_app.logger.info(f"AppointmentService.update_appointment - 创建新支付记录")
                    payment = Payment(
                        appointment_id=appointment.id,
                        patient_id=appointment.patient_id,
                        amount=payment_data.get('amount', 0),
                        payment_method=payment_data.get('payment_method', 'cash'),
                        payment_status=payment_data.get('payment_status', 'pending'),
                        notes=payment_data.get('notes', '')
                    )
                    db.session.add(payment)
            
            db.session.commit()
            current_app.logger.info(f"AppointmentService.update_appointment - 预约更新成功，ID: {appointment.id}")
            
            return appointment
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"AppointmentService.update_appointment - 更新预约失败: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def delete_appointment(appointment_id, recorder_id=None):
        """删除预约"""
        try:
            current_app.logger.info(f"AppointmentService.delete_appointment - 删除预约，ID: {appointment_id}, 记录员: {recorder_id}")
            
            query = db.session.query(Appointment).filter(Appointment.id == appointment_id)
            
            # 如果指定了recorder_id，验证权限
            if recorder_id:
                query = query.filter(Appointment.recorder_id == recorder_id)
            
            appointment = query.first()
            if not appointment:
                current_app.logger.warning(f"AppointmentService.delete_appointment - 预约不存在或无权限，ID: {appointment_id}")
                return False
            
            # 删除相关的支付记录（通过级联删除自动处理）
            db.session.delete(appointment)
            db.session.commit()
            
            current_app.logger.info(f"AppointmentService.delete_appointment - 预约删除成功，ID: {appointment_id}")
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"AppointmentService.delete_appointment - 删除预约失败: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def get_service_types():
        """获取所有服务类型"""
        try:
            current_app.logger.info("AppointmentService.get_service_types - 获取所有服务类型")
            
            service_types = ServiceType.query.filter_by(is_active=True).all()
            result = [st.to_dict() for st in service_types]
            
            current_app.logger.info(f"AppointmentService.get_service_types - 找到 {len(result)} 个服务类型")
            return result
        except Exception as e:
            current_app.logger.error(f"AppointmentService.get_service_types - 获取服务类型失败: {str(e)}", exc_info=True)
            raise e