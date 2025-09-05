from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.appointment import ServicePackage
from app.utils.decorators import recorder_required

service_package_bp = Blueprint('service_package', __name__, url_prefix='/api/v1')

@service_package_bp.route('/service-packages', methods=['GET'])
@jwt_required()
@recorder_required
def get_service_packages():
    """获取所有服务套餐"""
    try:
        current_app.logger.info("service_package.get_service_packages - 获取服务套餐列表")
        
        # 获取查询参数
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        package_level = request.args.get('level', type=int)
        
        # 构建查询
        query = ServicePackage.query
        
        if not include_inactive:
            query = query.filter(ServicePackage.is_active == True)
        
        if package_level:
            query = query.filter(ServicePackage.package_level == package_level)
        
        # 按套餐等级排序
        packages = query.order_by(ServicePackage.package_level).all()
        
        current_app.logger.info(f"service_package.get_service_packages - 找到 {len(packages)} 个套餐")
        
        result = [package.to_dict() for package in packages]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"service_package.get_service_packages - 获取套餐列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@service_package_bp.route('/service-packages/<int:package_id>', methods=['GET'])
@jwt_required()
@recorder_required
def get_service_package_detail(package_id):
    """获取服务套餐详情"""
    try:
        current_app.logger.info(f"service_package.get_service_package_detail - 获取套餐详情: {package_id}")
        
        package = ServicePackage.query.filter_by(id=package_id, is_active=True).first()
        
        if not package:
            return jsonify({
                'code': 404,
                'message': '套餐不存在或已下架'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': package.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"service_package.get_service_package_detail - 获取套餐详情失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

@service_package_bp.route('/service-packages/system-defaults', methods=['GET'])
@jwt_required()
@recorder_required
def get_system_default_packages():
    """获取系统默认的10级套餐"""
    try:
        current_app.logger.info("service_package.get_system_default_packages - 获取系统默认套餐")
        
        packages = ServicePackage.query.filter_by(
            is_system_default=True, 
            is_active=True
        ).order_by(ServicePackage.package_level).all()
        
        current_app.logger.info(f"service_package.get_system_default_packages - 找到 {len(packages)} 个系统默认套餐")
        
        result = [package.to_dict() for package in packages]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"service_package.get_system_default_packages - 获取系统默认套餐失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500