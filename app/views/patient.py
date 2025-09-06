from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.patient_service import PatientService
from app.services.family_service import FamilyService
from app.utils.decorators import recorder_required, admin_or_recorder_required
from app.utils.validators import validate_health_record, validate_family_data, validate_patient_data
from app.utils.helpers import handle_file_upload
import json

patient_bp = Blueprint('patient', __name__, url_prefix='/api/v1')

# ========== 家庭档案管理接口 ==========

@patient_bp.route('/families', methods=['POST'])
@jwt_required()
@admin_or_recorder_required
def create_family():
    """创建家庭档案"""
    try:
        current_app.logger.info("进入create_family函数")
        current_app.logger.info(f"请求头: {dict(request.headers)}")
        
        # 获取Authorization头
        auth_header = request.headers.get('Authorization')
        current_app.logger.info(f"Authorization头: {auth_header}")
        
        data = request.get_json()
        current_app.logger.info(f"请求数据: {data}")
        
        if not data:
            current_app.logger.error("请求数据为空")
            return jsonify({
                'code': 422,
                'message': '请求数据不能为空'
            }), 422
            
        # 获取当前用户ID并验证
        current_user_identity = get_jwt_identity()
        current_app.logger.info(f"JWT identity: {current_user_identity}")
        
        if not current_user_identity:
            current_app.logger.error("JWT token无效 - current_user_identity为空")
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            recorder_id = int(current_user_identity)
            current_app.logger.info(f"转换后的recorder_id: {recorder_id}")
        except (ValueError, TypeError) as e:
            current_app.logger.error(f"用户ID格式错误: {current_user_identity}, 错误: {str(e)}")
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
        
        # 验证请求数据
        current_app.logger.info("开始验证请求数据")
        validation_error = validate_family_data(data)
        if validation_error:
            current_app.logger.error(f"数据验证失败: {validation_error}")
            return jsonify({
                'code': 422,
                'message': validation_error
            }), 422
        
        current_app.logger.info("数据验证通过，调用FamilyService.create_family")
        family = FamilyService.create_family(data, recorder_id)  # 传入recorder_id
        current_app.logger.info(f"家庭创建成功: {family.id}")
        
        return jsonify({
            'code': 200,
            'message': '家庭档案创建成功',
            'data': family.to_dict(include_members=True)
        })
        
    except Exception as e:
        current_app.logger.error(f"创建家庭档案失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@patient_bp.route('/families', methods=['GET'])
@jwt_required()
@recorder_required
def get_families():
    """获取家庭列表"""
    try:
        # 获取当前用户ID并验证
        current_user_identity = get_jwt_identity()
        if not current_user_identity:
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            recorder_id = int(current_user_identity)
        except (ValueError, TypeError) as e:
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
            
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '')
        
        result = FamilyService.get_families(recorder_id, page, limit, search)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        current_app.logger.error(f"获取家庭列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@patient_bp.route('/families/<int:family_id>', methods=['GET'])
@jwt_required()
@recorder_required
def get_family_detail(family_id):
    """获取家庭详情"""
    try:
        # 获取当前用户ID并验证
        current_user_identity = get_jwt_identity()
        if not current_user_identity:
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            recorder_id = int(current_user_identity)
        except (ValueError, TypeError):
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
            
        result = FamilyService.get_family_by_id(family_id, recorder_id)
        
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

@patient_bp.route('/families/<int:family_id>', methods=['PUT'])
@jwt_required()
@admin_or_recorder_required
def update_family(family_id):
    """更新家庭信息"""
    try:
        current_app.logger.info(f"进入update_family函数，family_id: {family_id}")
        current_app.logger.info(f"请求头: {dict(request.headers)}")
        
        # 获取Authorization头
        auth_header = request.headers.get('Authorization')
        current_app.logger.info(f"Authorization头: {auth_header}")
        
        data = request.get_json()
        current_app.logger.info(f"请求数据: {data}")
        
        if not data:
            current_app.logger.error("请求数据为空")
            return jsonify({
                'code': 422,
                'message': '请求数据不能为空'
            }), 422
            
        # 获取当前用户ID并验证
        current_user_identity = get_jwt_identity()
        current_app.logger.info(f"JWT identity: {current_user_identity}")
        
        if not current_user_identity:
            current_app.logger.error("JWT token无效 - current_user_identity为空")
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            recorder_id = int(current_user_identity)
            current_app.logger.info(f"转换后的recorder_id: {recorder_id}")
        except (ValueError, TypeError) as e:
            current_app.logger.error(f"用户ID格式错误: {current_user_identity}, 错误: {str(e)}")
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
        
        # 验证请求数据
        current_app.logger.info("开始验证请求数据")
        validation_error = validate_family_data(data, is_update=True)
        if validation_error:
            current_app.logger.error(f"数据验证失败: {validation_error}")
            return jsonify({
                'code': 422,
                'message': validation_error
            }), 422
        
        current_app.logger.info("数据验证通过，调用FamilyService.update_family")
        family = FamilyService.update_family(family_id, data, recorder_id)
        
        if not family:
            current_app.logger.error(f"家庭不存在或无权限访问，family_id: {family_id}, recorder_id: {recorder_id}")
            return jsonify({
                'code': 404,
                'message': '家庭不存在或无权限访问'
            }), 404
        
        current_app.logger.info(f"家庭信息更新成功，family_id: {family_id}")
        return jsonify({
            'code': 200,
            'message': '家庭信息更新成功',
            'data': family.to_dict(include_members=True)
        })
        
    except Exception as e:
        current_app.logger.error(f"更新家庭信息失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@patient_bp.route('/families/<int:family_id>', methods=['DELETE'])
@jwt_required()
@admin_or_recorder_required
def delete_family(family_id):
    """删除家庭档案"""
    try:
        # 获取当前用户ID并验证
        current_user_identity = get_jwt_identity()
        if not current_user_identity:
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            recorder_id = int(current_user_identity)
        except (ValueError, TypeError):
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
        success = FamilyService.delete_family(family_id, recorder_id)
        
        if not success:
            return jsonify({
                'code': 404,
                'message': '家庭不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '家庭档案删除成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"删除家庭档案失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

# ========== 家庭成员管理接口 ==========

@patient_bp.route('/families/<int:family_id>/members', methods=['POST'])
@jwt_required()
@admin_or_recorder_required
def add_family_member(family_id):
    """为家庭添加新成员"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 422,
                'message': '请求数据不能为空'
            }), 422
            
        # 获取当前用户ID并验证
        current_user_identity = get_jwt_identity()
        if not current_user_identity:
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            recorder_id = int(current_user_identity)
        except (ValueError, TypeError):
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
        
        # 验证请求数据
        validation_error = validate_patient_data(data)
        if validation_error:
            return jsonify({
                'code': 422,
                'message': validation_error
            }), 422
        
        patient = FamilyService.add_family_member(family_id, data, recorder_id)
        
        if not patient:
            return jsonify({
                'code': 404,
                'message': '家庭不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '家庭成员添加成功',
            'data': patient.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"添加家庭成员失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@patient_bp.route('/families/<int:family_id>/members/<int:member_id>', methods=['PUT'])
@jwt_required()
@admin_or_recorder_required
def update_family_member(family_id, member_id):
    """更新家庭成员信息"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 422,
                'message': '请求数据不能为空'
            }), 422
            
        # 获取当前用户ID并验证
        current_user_identity = get_jwt_identity()
        if not current_user_identity:
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            recorder_id = int(current_user_identity)
        except (ValueError, TypeError):
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
        
        # 验证请求数据
        validation_error = validate_patient_data(data, is_update=True)
        if validation_error:
            return jsonify({
                'code': 422,
                'message': validation_error
            }), 422
        
        patient = FamilyService.update_family_member(family_id, member_id, data, recorder_id)
        
        if not patient:
            return jsonify({
                'code': 404,
                'message': '家庭成员不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '家庭成员信息更新成功',
            'data': patient.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"更新家庭成员失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@patient_bp.route('/families/<int:family_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
@admin_or_recorder_required
def delete_family_member(family_id, member_id):
    """删除家庭成员"""
    try:
        # 获取当前用户ID并验证
        current_user_identity = get_jwt_identity()
        if not current_user_identity:
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            recorder_id = int(current_user_identity)
        except (ValueError, TypeError):
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
        success = FamilyService.delete_family_member(family_id, member_id, recorder_id)
        
        if not success:
            return jsonify({
                'code': 404,
                'message': '家庭成员不存在或无权限访问'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '家庭成员删除成功'
        })
        
    except ValueError as e:
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"删除家庭成员失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

# ========== 健康记录接口（保留原有功能） ==========

@patient_bp.route('/health-records', methods=['POST'])
@jwt_required()
@recorder_required
def create_health_record():
    """创建健康记录"""
    try:
        # 获取当前用户ID并验证
        current_user_identity = get_jwt_identity()
        if not current_user_identity:
            return jsonify({
                'code': 422,
                'message': 'JWT token无效'
            }), 422
            
        try:
            recorder_id = int(current_user_identity)
        except (ValueError, TypeError):
            return jsonify({
                'code': 422,
                'message': '用户ID格式错误'
            }), 422
        
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

# ========== 测试函数：随机选择家庭 ==========

@patient_bp.route('/families/random', methods=['GET'])
@jwt_required()
@recorder_required
def get_random_family():
    """随机选择一个家庭用于测试"""
    try:
        import random
        
        current_app.logger.info("🎲 测试函数：开始随机选择家庭")
        recorder_id = int(get_jwt_identity())
        
        # 获取记录员的所有家庭
        families = FamilyService.get_families(recorder_id)
        
        if not families:
            return jsonify({
                'code': 404,
                'message': '没有可用的家庭数据'
            }), 404
        
        # 随机选择一个家庭
        random_family = random.choice(families)
        current_app.logger.info(f"🎲 随机选中家庭ID: {random_family['id']}, 户主: {random_family['household_head']}")
        
        # 获取家庭详细信息，包括成员
        family_detail = FamilyService.get_family_by_id(random_family['id'], recorder_id)
        
        if not family_detail:
            return jsonify({
                'code': 404,
                'message': '获取家庭详情失败'
            }), 404
        
        current_app.logger.info(f"🎲 家庭详情获取成功，成员数量: {len(family_detail.get('members', []))}")
        
        return jsonify({
            'code': 200,
            'message': '随机选择家庭成功',
            'data': family_detail
        })
    except Exception as e:
        current_app.logger.error(f"随机选择家庭失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500