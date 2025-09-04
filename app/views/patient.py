from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.patient_service import PatientService
from app.utils.decorators import recorder_required
from app.utils.validators import validate_health_record
from app.utils.helpers import handle_file_upload
import json

patient_bp = Blueprint('patient', __name__, url_prefix='/api/v1')

@patient_bp.route('/families', methods=['GET'])
@jwt_required()
@recorder_required
def get_families():
    """获取家庭列表"""
    try:
        recorder_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '')
        
        result = PatientService.get_recorder_families(recorder_id, page, limit, search)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        current_app.logger.error(f"获取家庭列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@patient_bp.route('/families/<int:family_id>', methods=['GET'])
@jwt_required()
@recorder_required
def get_family_detail(family_id):
    """获取家庭详情"""
    try:
        recorder_id = int(get_jwt_identity())
        result = PatientService.get_family_detail(family_id, recorder_id)
        
        if not result:
            return jsonify({
                'code': 404,
                'message': '家庭不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        current_app.logger.error(f"获取家庭详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@patient_bp.route('/health-records', methods=['POST'])
@jwt_required()
@recorder_required
def create_health_record():
    """创建健康记录"""
    try:
        recorder_id = int(get_jwt_identity())
        
        # 验证请求数据
        validation_error = validate_health_record(request)
        if validation_error:
            return jsonify({
                'code': 400,
                'message': validation_error
            }), 400
        
        # 处理文件上传
        data = request.form.to_dict()
        data['recorder_id'] = recorder_id
        
        # 处理音频文件
        if 'audio_file' in request.files:
            audio_file = request.files['audio_file']
            data['audio_file'] = handle_file_upload(audio_file, 'audio')
        
        # 处理照片文件
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            photo_urls = [handle_file_upload(photo, 'image') for photo in photos]
            data['photos'] = json.dumps(photo_urls)
        
        # 处理患者签名
        if 'patient_signature' in request.files:
            signature_file = request.files['patient_signature']
            data['patient_signature'] = handle_file_upload(signature_file, 'image')
        
        # 处理生命体征数据
        if 'vital_signs' in data:
            try:
                vital_signs = json.loads(data['vital_signs'])
                data['vital_signs'] = json.dumps(vital_signs)
            except json.JSONDecodeError:
                data['vital_signs'] = '{}'
        
        record = PatientService.create_health_record(data)
        
        return jsonify({
            'code': 200,
            'message': '健康记录创建成功',
            'data': {
                'record_id': record.id
            }
        })
    except Exception as e:
        current_app.logger.error(f"创建健康记录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500