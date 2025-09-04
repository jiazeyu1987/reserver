from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.hospital_service import HospitalService
from app.utils.decorators import recorder_required
from app.utils.validators import validate_hospital_appointment

hospital_bp = Blueprint('hospital', __name__, url_prefix='/api/v1')

@hospital_bp.route('/hospitals', methods=['GET'])
@jwt_required()
@recorder_required
def get_hospitals():
    """获取合作医院列表"""
    try:
        search = request.args.get('search', '')
        department = request.args.get('department', '')
        
        result = HospitalService.get_hospitals(search, department)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        current_app.logger.error(f"获取合作医院列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@hospital_bp.route('/hospitals/<int:hospital_id>/departments', methods=['GET'])
@jwt_required()
@recorder_required
def get_hospital_departments(hospital_id):
    """获取医院科室列表"""
    try:
        result = HospitalService.get_hospital_departments(hospital_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        current_app.logger.error(f"获取医院科室列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@hospital_bp.route('/hospitals/<int:hospital_id>/departments/<int:department_id>/doctors', methods=['GET'])
@jwt_required()
@recorder_required
def get_department_doctors(hospital_id, department_id):
    """获取科室医生列表"""
    try:
        result = HospitalService.get_department_doctors(hospital_id, department_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        current_app.logger.error(f"获取科室医生列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@hospital_bp.route('/hospital-appointments', methods=['POST'])
@jwt_required()
@recorder_required
def create_hospital_appointment():
    """创建医院预约"""
    try:
        recorder_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 验证数据
        validation_error = validate_hospital_appointment(data)
        if validation_error:
            return jsonify({
                'code': 400,
                'message': validation_error
            }), 400
        
        # 添加记录员ID
        data['recorder_id'] = recorder_id
        
        appointment = HospitalService.create_hospital_appointment(data)
        
        return jsonify({
            'code': 200,
            'message': '医院预约申请提交成功',
            'data': {
                'appointment_id': appointment.id,
                'status': appointment.status
            }
        })
    except Exception as e:
        current_app.logger.error(f"创建医院预约失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@hospital_bp.route('/hospital-appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
@recorder_required
def get_hospital_appointment(appointment_id):
    """获取医院预约详情"""
    try:
        recorder_id = get_jwt_identity()
        result = HospitalService.get_hospital_appointment(appointment_id, recorder_id)
        
        if not result:
            return jsonify({
                'code': 404,
                'message': '预约不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        current_app.logger.error(f"获取医院预约详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@hospital_bp.route('/hospital-appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
@recorder_required
def update_hospital_appointment(appointment_id):
    """更新医院预约结果"""
    try:
        recorder_id = int(get_jwt_identity())
        data = request.get_json()
        
        result = HospitalService.update_hospital_appointment(appointment_id, recorder_id, data)
        
        if not result:
            return jsonify({
                'code': 404,
                'message': '预约不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '预约结果更新成功',
            'data': result
        })
    except Exception as e:
        current_app.logger.error(f"更新医院预约结果失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500