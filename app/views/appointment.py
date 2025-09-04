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
        
        # 详细记录请求参数
        current_app.logger.info("=" * 60)
        current_app.logger.info("📥 后端收到预约列表请求")
        current_app.logger.info(f"  - recorder_id: {recorder_id}")
        current_app.logger.info(f"  - 完整URL: {request.url}")
        current_app.logger.info(f"  - 查询字符串: {request.query_string.decode()}")
        current_app.logger.info(f"  - 请求方法: {request.method}")
        current_app.logger.info(f"  - 所有参数: {dict(request.args)}")
        
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        status = request.args.get('status', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        current_app.logger.info(f"  - 解析后的参数:")
        current_app.logger.info(f"    * page: {page}")
        current_app.logger.info(f"    * limit: {limit}")
        current_app.logger.info(f"    * status: '{status}'")
        current_app.logger.info(f"    * date_from: '{date_from}'")
        current_app.logger.info(f"    * date_to: '{date_to}'")
        
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
        
        current_app.logger.info("🔍 调用Service层查询预约")
        current_app.logger.info(f"  - 传递给Service的参数:")
        current_app.logger.info(f"    * recorder_id: {recorder_id}")
        current_app.logger.info(f"    * page: {page}, limit: {limit}")
        current_app.logger.info(f"    * status: '{status}'")
        current_app.logger.info(f"    * date_from_obj: {date_from_obj}")
        current_app.logger.info(f"    * date_to_obj: {date_to_obj}")
        
        result = AppointmentService.get_appointments(
            recorder_id, page, limit, status, date_from_obj, date_to_obj
        )
        
        current_app.logger.info("📤 后端返回预约列表响应")
        current_app.logger.info(f"  - 总预约数: {result['total']}")
        current_app.logger.info(f"  - 返回预约数: {len(result['appointments'])}")
        current_app.logger.info(f"  - 分页信息: 第{result['page']}页，每页{result['limit']}条")
        current_app.logger.info("=" * 60)
        
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
        current_app.logger.info("appointment.create_appointment - 开始创建预约")
        recorder_id = int(get_jwt_identity())
        data = request.get_json()
        
        current_app.logger.info(f"appointment.create_appointment - 请求数据: {data}")
        
        # 验证数据
        validation_error = validate_appointment(data)
        if validation_error:
            current_app.logger.warning(f"appointment.create_appointment - 数据验证失败: {validation_error}")
            return jsonify({
                'code': 422,
                'message': validation_error
            }), 422
        
        appointment = AppointmentService.create_appointment(data, recorder_id)
        
        return jsonify({
            'code': 200,
            'message': '预约创建成功',
            'data': appointment.to_dict(include_patient=True, include_payment=True)
        })
    except Exception as e:
        current_app.logger.error(f"appointment.create_appointment - 创建预约失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
@recorder_required
def update_appointment(appointment_id):
    """更新预约"""
    try:
        current_app.logger.info(f"appointment.update_appointment - 更新预约: {appointment_id}")
        recorder_id = int(get_jwt_identity())
        data = request.get_json()
        
        current_app.logger.info(f"appointment.update_appointment - 更新数据: {data}")
        
        appointment = AppointmentService.update_appointment(appointment_id, data, recorder_id)
        
        if appointment is None:
            return jsonify({
                'code': 404,
                'message': '预约不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '预约更新成功',
            'data': appointment.to_dict(include_patient=True, include_payment=True)
        })
    except Exception as e:
        current_app.logger.error(f"appointment.update_appointment - 更新预约失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
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

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
@recorder_required
def get_appointment_detail(appointment_id):
    """获取预约详情"""
    try:
        current_app.logger.info(f"appointment.get_appointment_detail - 获取预约详情: {appointment_id}")
        recorder_id = int(get_jwt_identity())
        
        appointment = AppointmentService.get_appointment_by_id(appointment_id, recorder_id)
        
        if not appointment:
            return jsonify({
                'code': 404,
                'message': '预约不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': appointment
        })
    except Exception as e:
        current_app.logger.error(f"appointment.get_appointment_detail - 获取预约详情失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
@recorder_required
def delete_appointment(appointment_id):
    """删除预约"""
    try:
        current_app.logger.info(f"appointment.delete_appointment - 删除预约: {appointment_id}")
        recorder_id = int(get_jwt_identity())
        
        result = AppointmentService.delete_appointment(appointment_id, recorder_id)
        
        if not result:
            return jsonify({
                'code': 404,
                'message': '预约不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '预约删除成功'
        })
    except Exception as e:
        current_app.logger.error(f"appointment.delete_appointment - 删除预约失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@appointment_bp.route('/service-types', methods=['GET'])
@jwt_required()
@recorder_required
def get_service_types():
    """获取所有服务类型"""
    try:
        current_app.logger.info("appointment.get_service_types - 获取所有服务类型")
        
        service_types = AppointmentService.get_service_types()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': service_types
        })
    except Exception as e:
        current_app.logger.error(f"appointment.get_service_types - 获取服务类型失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500