from app.models.patient import Patient, Family
from app.models.appointment import ServicePackage, PatientSubscription
from app import db
from sqlalchemy import and_, or_
from datetime import datetime, date
from flask import current_app
import json

class FamilyService:
    
    @staticmethod
    def create_family(data, recorder_id=None):
        """创建家庭档案"""
        try:
            # 创建家庭记录
            family = Family(
                householdHead=data['householdHead'],
                address=data['address'],
                phone=data['phone'],
                emergency_contact=data.get('emergency_contact'),
                emergency_phone=data.get('emergency_phone')
            )
            
            db.session.add(family)
            db.session.flush()  # 获取family.id
            
            # 首先创建户主患者记录（户主信息独立管理）
            household_patient = Patient(
                family_id=family.id,
                name=data['householdHead'],
                age=int(data['householdHeadAge']),
                gender=data['householdHeadGender'],
                relationship='户主',
                conditions=data.get('householdHeadConditions', ''),
                packageType=data['householdHeadPackageType'],
                paymentStatus='normal',
                phone=data['phone'],  # 户主使用家庭电话
                medications=data.get('householdHeadMedications', '')
            )
            
            db.session.add(household_patient)
            db.session.flush()  # 获取patient.id
            
            # 为户主创建PatientSubscription记录
            if recorder_id:
                from app.models.appointment import ServicePackage, PatientSubscription
                
                # 查找对应的服务套餐
                package = ServicePackage.query.filter_by(name=household_patient.packageType).first()
                if not package:
                    # 如果套餐不存在，创建一个默认套餐
                    package = ServicePackage(
                        name=household_patient.packageType,
                        price=0.00,
                        duration_days=30,
                        service_frequency=4,
                        description=f'默认{household_patient.packageType}',
                        package_level=1,  # 设置默认等级
                        is_active=True,
                        is_system_default=False
                    )
                    db.session.add(package)
                    db.session.flush()
                
                # 创建户主的订阅记录
                from datetime import timedelta
                start_date = datetime.now().date()
                end_date = start_date + timedelta(days=package.duration_days)
                
                subscription = PatientSubscription(
                    patient_id=household_patient.id,
                    package_id=package.id,
                    recorder_id=recorder_id,
                    start_date=start_date,
                    end_date=end_date,
                    status='active'
                )
                db.session.add(subscription)
            
            # 创建其他家庭成员（不包含套餐类型）
            for member_data in data.get('members', []):
                patient = Patient(
                    family_id=family.id,
                    name=member_data['name'],
                    age=int(member_data['age']),
                    gender=member_data['gender'],
                    relationship=member_data['relationship'],
                    conditions=member_data.get('conditions', ''),
                    packageType='',  # 成员不设置套餐类型
                    paymentStatus='normal',
                    phone=member_data.get('phone'),
                    medications=member_data.get('medications', '')
                )
                
                # 如果conditions是列表，转换为字符串
                if isinstance(member_data.get('conditions'), list):
                    patient.set_conditions_list(member_data['conditions'])
                
                # 如果medications是列表，转换为字符串  
                if isinstance(member_data.get('medications'), list):
                    patient.set_medications_list(member_data['medications'])
                
                db.session.add(patient)
                # 注意：普通成员不创建PatientSubscription记录，因为只有户主有套餐
                
            db.session.commit()
            return family
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_families(recorder_id=None, page=1, limit=20, search=None):
        """获取家庭列表"""
        try:
            query = db.session.query(Family)
            
            # 如果指定了recorder_id，只查询该记录员负责的家庭
            if recorder_id:
                query = query.join(Patient)\
                    .join(PatientSubscription)\
                    .filter(PatientSubscription.recorder_id == recorder_id)\
                    .distinct()
            
            # 搜索过滤
            if search:
                query = query.filter(
                    or_(
                        Family.householdHead.contains(search),
                        Family.address.contains(search),
                        Family.phone.contains(search)
                    )
                )
            
            total = query.count()
            families = query.offset((page - 1) * limit).limit(limit).all()
            
            result = {
                'families': [family.to_dict(include_members=True) for family in families],
                'total': total,
                'page': page,
                'limit': limit,
                'totalPages': (total + limit - 1) // limit
            }
            return result
            
        except Exception as e:
            current_app.logger.error(f"FamilyService.get_families - 发生异常: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def get_family_by_id(family_id, recorder_id=None):
        """根据ID获取家庭详情"""
        query = db.session.query(Family).filter(Family.id == family_id)
        
        # 如果指定了recorder_id，验证权限
        if recorder_id:
            query = query.join(Patient)\
                .join(PatientSubscription)\
                .filter(PatientSubscription.recorder_id == recorder_id)
        
        family = query.first()
        if not family:
            return None
        
        return family.to_dict(include_members=True)
    
    @staticmethod
    def update_family(family_id, data, recorder_id=None):
        """更新家庭信息"""
        try:
            current_app.logger.info(f"FamilyService.update_family - 参数: family_id={family_id}, recorder_id={recorder_id}, data={data}")
            
            query = db.session.query(Family).filter(Family.id == family_id)
            current_app.logger.info("FamilyService.update_family - 创建基础查询")
            
            # 如果指定了recorder_id，验证权限
            if recorder_id:
                current_app.logger.info(f"FamilyService.update_family - 添加recorder_id过滤: {recorder_id}")
                query = query.join(Patient)\
                    .join(PatientSubscription)\
                    .filter(PatientSubscription.recorder_id == recorder_id)
            
            family = query.first()
            current_app.logger.info(f"FamilyService.update_family - 查询到的家庭: {family}")
            
            if not family:
                current_app.logger.error(f"FamilyService.update_family - 家庭不存在或无权限, family_id={family_id}")
                return None
            
            current_app.logger.info(f"FamilyService.update_family - 更新前家庭信息: householdHead={family.householdHead}, address={family.address}, phone={family.phone}")
            
            # 更新家庭基本信息
            if 'householdHead' in data:
                current_app.logger.info(f"更新householdHead: {family.householdHead} -> {data['householdHead']}")
                family.householdHead = data['householdHead']
            if 'address' in data:
                current_app.logger.info(f"更新address: {family.address} -> {data['address']}")
                family.address = data['address']
            if 'phone' in data:
                current_app.logger.info(f"更新phone: {family.phone} -> {data['phone']}")
                family.phone = data['phone']
            if 'emergency_contact' in data:
                current_app.logger.info(f"更新emergency_contact: {family.emergency_contact} -> {data['emergency_contact']}")
                family.emergency_contact = data['emergency_contact']
            if 'emergency_phone' in data:
                current_app.logger.info(f"更新emergency_phone: {family.emergency_phone} -> {data['emergency_phone']}")
                family.emergency_phone = data['emergency_phone']
            
            # 更新家庭成员（如果提供了members数据）
            if 'members' in data:
                current_app.logger.info("FamilyService.update_family - 更新家庭成员")
                # 删除现有成员（级联删除会自动处理关联数据）
                Patient.query.filter(Patient.family_id == family_id).delete()
                
                # 创建新的成员记录
                for i, member_data in enumerate(data['members']):
                    current_app.logger.info(f"创建第{i+1}个成员: {member_data}")
                    patient = Patient(
                        family_id=family.id,
                        name=member_data['name'],
                        age=int(member_data['age']),
                        gender=member_data['gender'],
                        relationship=member_data['relationship'],
                        conditions=member_data.get('conditions', ''),
                        packageType=member_data.get('packageType', '基础套餐'),
                        paymentStatus=member_data.get('paymentStatus', 'normal'),
                        phone=member_data.get('phone'),
                        medications=member_data.get('medications', '')
                    )
                    
                    # 处理列表格式的数据
                    if isinstance(member_data.get('conditions'), list):
                        patient.set_conditions_list(member_data['conditions'])
                    if isinstance(member_data.get('medications'), list):
                        patient.set_medications_list(member_data['medications'])
                    
                    db.session.add(patient)
            
            family.updated_at = datetime.utcnow()
            current_app.logger.info("FamilyService.update_family - 提交数据库更改")
            db.session.commit()
            
            current_app.logger.info(f"FamilyService.update_family - 更新后家庭信息: householdHead={family.householdHead}, address={family.address}, phone={family.phone}")
            return family
            
        except Exception as e:
            current_app.logger.error(f"FamilyService.update_family - 发生异常: {str(e)}", exc_info=True)
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_family(family_id, recorder_id=None):
        """删除家庭档案"""
        try:
            query = db.session.query(Family).filter(Family.id == family_id)
            
            # 如果指定了recorder_id，验证权限
            if recorder_id:
                query = query.join(Patient)\
                    .join(PatientSubscription)\
                    .filter(PatientSubscription.recorder_id == recorder_id)
            
            family = query.first()
            if not family:
                return False
            
            db.session.delete(family)  # 级联删除会自动删除关联的患者
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def add_family_member(family_id, member_data, recorder_id=None):
        """为家庭添加新成员"""
        try:
            # 验证家庭存在和权限
            query = db.session.query(Family).filter(Family.id == family_id)
            if recorder_id:
                query = query.join(Patient)\
                    .join(PatientSubscription)\
                    .filter(PatientSubscription.recorder_id == recorder_id)
            
            family = query.first()
            if not family:
                return None
            
            # 创建新成员
            patient = Patient(
                family_id=family_id,
                name=member_data['name'],
                age=int(member_data['age']),
                gender=member_data['gender'],
                relationship=member_data['relationship'],
                conditions=member_data.get('conditions', ''),
                packageType=member_data.get('packageType', '基础套餐'),
                paymentStatus=member_data.get('paymentStatus', 'normal'),
                phone=member_data.get('phone'),
                medications=member_data.get('medications', '')
            )
            
            # 处理列表格式的数据
            if isinstance(member_data.get('conditions'), list):
                patient.set_conditions_list(member_data['conditions'])
            if isinstance(member_data.get('medications'), list):
                patient.set_medications_list(member_data['medications'])
            
            db.session.add(patient)
            
            # 更新家庭更新时间
            family.updated_at = datetime.utcnow()
            
            db.session.commit()
            return patient
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_family_member(family_id, member_id, member_data, recorder_id=None):
        """更新家庭成员信息"""
        try:
            # 验证权限
            query = db.session.query(Patient)\
                .filter(and_(Patient.id == member_id, Patient.family_id == family_id))
            
            if recorder_id:
                query = query.join(PatientSubscription)\
                    .filter(PatientSubscription.recorder_id == recorder_id)
            
            patient = query.first()
            if not patient:
                return None
            
            # 更新成员信息
            if 'name' in member_data:
                patient.name = member_data['name']
            if 'age' in member_data:
                patient.age = int(member_data['age'])
            if 'gender' in member_data:
                patient.gender = member_data['gender']
            if 'relationship' in member_data:
                patient.relationship = member_data['relationship']
            if 'conditions' in member_data:
                if isinstance(member_data['conditions'], list):
                    patient.set_conditions_list(member_data['conditions'])
                else:
                    patient.conditions = member_data['conditions']
            if 'packageType' in member_data:
                patient.packageType = member_data['packageType']
            if 'paymentStatus' in member_data:
                patient.paymentStatus = member_data['paymentStatus']
            if 'phone' in member_data:
                patient.phone = member_data['phone']
            if 'medications' in member_data:
                if isinstance(member_data['medications'], list):
                    patient.set_medications_list(member_data['medications'])
                else:
                    patient.medications = member_data['medications']
            
            patient.updated_at = datetime.utcnow()
            
            # 更新家庭更新时间
            patient.family.updated_at = datetime.utcnow()
            
            db.session.commit()
            return patient
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod 
    def delete_family_member(family_id, member_id, recorder_id=None):
        """删除家庭成员"""
        try:
            # 验证权限
            query = db.session.query(Patient)\
                .filter(and_(Patient.id == member_id, Patient.family_id == family_id))
            
            if recorder_id:
                query = query.join(PatientSubscription)\
                    .filter(PatientSubscription.recorder_id == recorder_id)
            
            patient = query.first()
            if not patient:
                return False
            
            # 检查是否是家庭唯一成员
            family_member_count = Patient.query.filter(Patient.family_id == family_id).count()
            if family_member_count <= 1:
                raise ValueError("不能删除家庭的最后一个成员")
            
            # 先删除相关的PatientSubscription记录
            PatientSubscription.query.filter(PatientSubscription.patient_id == member_id).delete()
            
            db.session.delete(patient)
            
            # 更新家庭更新时间
            family = Family.query.get(family_id)
            if family:
                family.updated_at = datetime.utcnow()
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e