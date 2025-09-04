from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.appointment_service import AppointmentService
from app.utils.decorators import recorder_required
from app.utils.validators import validate_appointment
from datetime import datetime, date
import json

appointment_bp = Blueprint('appointment', __name__, url_prefix='/api/v1')

@appointment_bp.route('/appointments/today', methods=['GET'])
@jwt_required()
@recorder_required
def get_today_appointments():
    """获取今日预约列表"""
    try:
        recorder_id = int(get_jwt_identity())
        result = AppointmentService.get_today_appointments(recorder_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        current_app.logger.error(f"获取今日预约列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@appointment_bp.route('/appointments', methods=['GET'])
@jwt_required()
@recorder_required
def get_appointments():
    """获取预约列表"""
    try:
        recorder_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        status = request.args.get('status', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # 解析日期参数
        date_from_obj = None
        date_to_obj = None
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        result = AppointmentService.get_appointments(
            recorder_id, page, limit, status, date_from_obj, date_to_obj
        )
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        current_app.logger.error(f"获取预约列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@appointment_bp.route('/appointments', methods=['POST'])
@jwt_required()
@recorder_required
def create_appointment():
    """创建预约"""
    try:
        recorder_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 验证数据
        validation_error = validate_appointment(data)
        if validation_error:
            return jsonify({
                'code': 400,
                'message': validation_error
            }), 400
        
        # 添加记录员ID
        data['recorder_id'] = recorder_id
        
        appointment = AppointmentService.create_appointment(data)
        
        return jsonify({
            'code': 200,
            'message': '预约创建成功',
            'data': {
                'appointment_id': appointment.id
            }
        })
    except Exception as e:
        current_app.logger.error(f"创建预约失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
@recorder_required
def update_appointment(appointment_id):
    """更新预约"""
    try:
        recorder_id = int(get_jwt_identity())
        data = request.get_json()
        
        appointment = AppointmentService.update_appointment(appointment_id, recorder_id, data)
        
        if not appointment:
            return jsonify({
                'code': 404,
                'message': '预约不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '预约更新成功',
            'data': appointment.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"更新预约失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@appointment_bp.route('/appointments/<int:appointment_id>/complete', methods=['POST'])
@jwt_required()
@recorder_required
def complete_appointment(appointment_id):
    """完成预约"""
    try:
        recorder_id = int(get_jwt_identity())
        
        appointment = AppointmentService.complete_appointment(appointment_id, recorder_id)
        
        if not appointment:
            return jsonify({
                'code': 404,
                'message': '预约不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '预约已完成',
            'data': appointment.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"完成预约失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500