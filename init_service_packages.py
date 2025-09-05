#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化10级上门医疗服务套餐数据
"""
import json
from app import create_app, db
from app.models.appointment import ServicePackage

def create_service_packages():
    """创建10级服务套餐"""
    
    packages_data = [
        {
            'package_level': 1,
            'name': '贴心关怀型',
            'description': '身体健康，仅需基础关怀的老年人',
            'price': 98.00,
            'duration_days': 30,
            'service_frequency': 1,  # 每月1次
            'target_users': '身体健康，仅需基础关怀的老年人',
            'staff_level': '护理员',
            'hospital_level': '社区卫生服务中心',
            'service_time': '工作日白天',
            'report_frequency': '无',
            'service_content': json.dumps([
                '每月1次上门探访',
                '基础健康咨询',
                '测量血压、体温',
                '生活起居指导'
            ], ensure_ascii=False),
            'monitoring_items': json.dumps([
                '血压', '体温'
            ], ensure_ascii=False),
            'additional_services': json.dumps([], ensure_ascii=False),
            'gifts_included': json.dumps(['节日慰问礼品'], ensure_ascii=False)
        },
        {
            'package_level': 2,
            'name': '基础保障型',
            'description': '身体状况稳定，需要定期基础监测的老年人',
            'price': 168.00,
            'duration_days': 30,
            'service_frequency': 2,  # 每月2次
            'target_users': '身体状况稳定，需要定期基础监测的老年人',
            'staff_level': '护理员',
            'hospital_level': '一级医疗机构',
            'service_time': '工作日全天',
            'report_frequency': '无',
            'service_content': json.dumps([
                '每月2次上门服务',
                '基础健康监测',
                '健康档案记录',
                '用药提醒服务'
            ], ensure_ascii=False),
            'monitoring_items': json.dumps([
                '血压', '血糖', '体温'
            ], ensure_ascii=False),
            'additional_services': json.dumps([], ensure_ascii=False),
            'gifts_included': json.dumps(['节日慰问礼品'], ensure_ascii=False)
        },
        {
            'package_level': 3,
            'name': '健康守护型',
            'description': '有轻微慢性病，需要定期监测的老年人',
            'price': 298.00,
            'duration_days': 30,
            'service_frequency': 4,  # 每月4次
            'target_users': '有轻微慢性病，需要定期监测的老年人',
            'staff_level': '护士',
            'hospital_level': '二级医疗机构',
            'service_time': '工作日全天，周末可预约',
            'report_frequency': '无',
            'service_content': json.dumps([
                '每月4次上门服务',
                '基础健康监测',
                '健康趋势分析',
                '用药指导和健康咨询'
            ], ensure_ascii=False),
            'monitoring_items': json.dumps([
                '血压', '血糖', '体温', '心率'
            ], ensure_ascii=False),
            'additional_services': json.dumps([], ensure_ascii=False),
            'gifts_included': json.dumps(['节日慰问礼品', '生日礼品'], ensure_ascii=False)
        },
        {
            'package_level': 4,
            'name': '专业护理型',
            'description': '有明确慢性病，需要专业护理指导的老年人',
            'price': 498.00,
            'duration_days': 30,
            'service_frequency': 6,  # 每月6次
            'target_users': '有明确慢性病，需要专业护理指导的老年人',
            'staff_level': '护士',
            'hospital_level': '二级医疗机构',
            'service_time': '工作日全天，周末可预约',
            'report_frequency': '月度健康报告',
            'service_content': json.dumps([
                '每月6次上门服务',
                '全面健康监测',
                '慢性病管理指导',
                '伤口护理等基础护理服务'
            ], ensure_ascii=False),
            'monitoring_items': json.dumps([
                '血压', '血糖', '体温', '心率', '血氧'
            ], ensure_ascii=False),
            'additional_services': json.dumps(['基础护理服务'], ensure_ascii=False),
            'gifts_included': json.dumps(['节日慰问礼品', '生日礼品'], ensure_ascii=False)
        },
        {
            'package_level': 5,
            'name': '贴心陪护型',
            'description': '行动不便，需要较多关注的老年人',
            'price': 798.00,
            'duration_days': 30,
            'service_frequency': 8,  # 每月8次
            'target_users': '行动不便，需要较多关注的老年人',
            'staff_level': '主管护师',
            'hospital_level': '二级医疗机构 + 部分三甲医院',
            'service_time': '每天可预约，节假日除外',
            'report_frequency': '周健康趋势分析报告',
            'service_content': json.dumps([
                '每月8次上门服务',
                '全面健康监测',
                '个性化护理方案',
                '康复训练指导'
            ], ensure_ascii=False),
            'monitoring_items': json.dumps([
                '血压', '血糖', '体温', '心率', '血氧', '体重'
            ], ensure_ascii=False),
            'additional_services': json.dumps(['康复训练指导'], ensure_ascii=False),
            'gifts_included': json.dumps(['节日慰问礼品', '生日礼品', '季度礼品'], ensure_ascii=False)
        },
        {
            'package_level': 6,
            'name': '高级护理型',
            'description': '有多种慢性病，需要高级护理的老年人',
            'price': 1280.00,
            'duration_days': 30,
            'service_frequency': 12,  # 每月12次
            'target_users': '有多种慢性病，需要高级护理的老年人',
            'staff_level': '主管护师',
            'hospital_level': '三级医疗机构',
            'service_time': '每天可预约，节假日除外',
            'report_frequency': '双周健康趋势分析报告',
            'service_content': json.dumps([
                '每月12次上门服务',
                '全面健康监测 + 专项检查',
                '个性化慢性病管理方案',
                '康复训练 + 理疗指导'
            ], ensure_ascii=False),
            'monitoring_items': json.dumps([
                '血压', '血糖', '体温', '心率', '血氧', '体重', '专项检查'
            ], ensure_ascii=False),
            'additional_services': json.dumps(['理疗指导', '营养膳食建议'], ensure_ascii=False),
            'gifts_included': json.dumps(['节日慰问礼品', '生日礼品', '季度礼品'], ensure_ascii=False)
        },
        {
            'package_level': 7,
            'name': '专家指导型',
            'description': '病情复杂，需要专家指导的老年人',
            'price': 1880.00,
            'duration_days': 30,
            'service_frequency': 16,  # 每月16次
            'target_users': '病情复杂，需要专家指导的老年人',
            'staff_level': '专家级护理师',
            'hospital_level': '三级甲等医疗机构 + 专家资源',
            'service_time': '每天可预约，节假日可协商',
            'report_frequency': '周健康趋势分析报告 + 专家建议',
            'service_content': json.dumps([
                '每月16次上门服务',
                '全面健康监测 + 专项检查 + 个性化检查',
                '专家级健康管理方案',
                '康复训练 + 理疗 + 心理疏导'
            ], ensure_ascii=False),
            'monitoring_items': json.dumps([
                '血压', '血糖', '体温', '心率', '血氧', '体重', '专项检查', '个性化检查'
            ], ensure_ascii=False),
            'additional_services': json.dumps(['心理疏导', '营养膳食', '运动处方'], ensure_ascii=False),
            'gifts_included': json.dumps(['节日慰问礼品', '生日礼品', '季度礼品', '年度体检'], ensure_ascii=False)
        },
        {
            'package_level': 8,
            'name': '专属护理型',
            'description': '高净值客户，对服务质量要求极高的老年人',
            'price': 2280.00,
            'duration_days': 30,
            'service_frequency': 20,  # 每月20次
            'target_users': '高净值客户，对服务质量要求极高的老年人',
            'staff_level': '专家级护理师',
            'hospital_level': '知名三甲医院 + 专家资源 + 特需门诊',
            'service_time': '每天可预约，节假日可协商',
            'report_frequency': '每周健康趋势分析报告 + 专家建议',
            'service_content': json.dumps([
                '每月20次上门服务',
                '全面健康监测 + 专项检查 + 个性化检查 + 预防性检查',
                '专属健康管理师服务',
                '康复训练 + 理疗 + 心理疏导 + 中医调理'
            ], ensure_ascii=False),
            'monitoring_items': json.dumps([
                '血压', '血糖', '体温', '心率', '血氧', '体重', '专项检查', '个性化检查', '预防性检查'
            ], ensure_ascii=False),
            'additional_services': json.dumps(['中医调理', '个性化营养膳食', '运动处方', '睡眠管理'], ensure_ascii=False),
            'gifts_included': json.dumps(['节日慰问礼品', '生日礼品', '季度礼品', '半年度体检'], ensure_ascii=False)
        },
        {
            'package_level': 9,
            'name': '全程陪护型',
            'description': '行动严重不便，需要高频次服务的老年人',
            'price': 2680.00,
            'duration_days': 30,
            'service_frequency': 25,  # 每月25次
            'target_users': '行动严重不便，需要高频次服务的老年人',
            'staff_level': '专家级护理师 + 合作医生',
            'hospital_level': '知名三甲医院 + 专家资源 + 特需门诊 + 急救网络',
            'service_time': '每天可预约，节假日可协商，紧急情况24小时响应',
            'report_frequency': '每周健康趋势分析报告 + 专家建议 + 医生会诊',
            'service_content': json.dumps([
                '每月25次上门服务',
                '全面健康监测 + 专项检查 + 个性化检查 + 预防性检查 + 应急检查',
                '专属健康管理师 + 家庭医生服务',
                '康复训练 + 理疗 + 心理疏导 + 中医调理 + 专业护理'
            ], ensure_ascii=False),
            'monitoring_items': json.dumps([
                '血压', '血糖', '体温', '心率', '血氧', '体重', '专项检查', '个性化检查', '预防性检查', '应急检查'
            ], ensure_ascii=False),
            'additional_services': json.dumps(['专业护理', '用药管理', '紧急医疗绿色通道'], ensure_ascii=False),
            'gifts_included': json.dumps(['节日慰问礼品', '生日礼品', '季度礼品', '半年度体检', '紧急医疗绿色通道'], ensure_ascii=False)
        },
        {
            'package_level': 10,
            'name': '尊享专家型',
            'description': '超高净值客户，要求最高级别服务的老年人',
            'price': 2980.00,
            'duration_days': 30,
            'service_frequency': 30,  # 每月30次
            'target_users': '超高净值客户，要求最高级别服务的老年人',
            'staff_level': '专家顾问团队',
            'hospital_level': '顶级三甲医院 + 知名专家 + 特需门诊 + 急救网络 + 国际医疗资源',
            'service_time': '每天可预约，节假日可协商，紧急情况24小时响应',
            'report_frequency': '每周健康趋势分析报告 + 专家建议 + 医生会诊 + 远程医疗咨询',
            'service_content': json.dumps([
                '每月30次上门服务（可按需增加）',
                '全面健康监测 + 专项检查 + 个性化检查 + 预防性检查 + 应急检查 + 远程监测',
                '专属健康管理师 + 家庭医生 + 专家顾问团队服务',
                '康复训练 + 理疗 + 心理疏导 + 中医调理 + 专业护理 + 临终关怀咨询'
            ], ensure_ascii=False),
            'monitoring_items': json.dumps([
                '血压', '血糖', '体温', '心率', '血氧', '体重', '专项检查', '个性化检查', '预防性检查', '应急检查', '远程监测'
            ], ensure_ascii=False),
            'additional_services': json.dumps([
                '基因检测分析', '远程医疗咨询', '临终关怀咨询', '专车接送', '国际医疗资源'
            ], ensure_ascii=False),
            'gifts_included': json.dumps([
                '节日慰问礼品', '生日礼品', '季度礼品', '年度高端体检', '紧急医疗绿色通道', '专车接送'
            ], ensure_ascii=False)
        }
    ]
    
    return packages_data

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建数据库表
            db.create_all()
            print("[成功] 数据库表创建成功")
            
            # 检查是否已经存在系统默认套餐
            existing_packages = ServicePackage.query.filter_by(is_system_default=True).count()
            if existing_packages > 0:
                print(f"[警告] 已存在 {existing_packages} 个系统默认套餐，跳过初始化")
                return
            
            # 创建10级服务套餐
            packages_data = create_service_packages()
            
            for package_data in packages_data:
                package_data['is_system_default'] = True  # 标记为系统默认套餐
                package = ServicePackage(**package_data)
                db.session.add(package)
            
            db.session.commit()
            print(f"[成功] 成功创建 {len(packages_data)} 个服务套餐")
            
            # 验证创建结果
            created_packages = ServicePackage.query.filter_by(is_system_default=True).all()
            print("\n[套餐列表] 已创建的套餐:")
            for pkg in created_packages:
                print(f"  {pkg.package_level}. {pkg.name} - {pkg.price}元/月 (每月{pkg.service_frequency}次服务)")
                
        except Exception as e:
            print(f"[错误] 创建套餐失败: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main()