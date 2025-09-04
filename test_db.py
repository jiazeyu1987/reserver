import os
import sys
from app import create_app, db
from app.models.user import User
from app.models.patient import Family, Patient
from app.models.appointment import ServicePackage, PatientSubscription
from app.models.hospital import PartnerHospital, HospitalDepartment

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """测试数据库连接和表创建"""
    app = create_app('development')
    
    with app.app_context():
        # 打印所有已注册的表
        print("已注册的表:")
        for table in db.metadata.tables:
            print(f"  - {table}")
        
        # 尝试创建所有表
        print("\n创建所有表...")
        db.create_all()
        print("表创建完成")
        
        # 检查特定表是否存在
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n数据库中的表: {tables}")
        
        # 尝试插入一条测试数据
        try:
            user = User(
                username='test',
                phone='13800138000',
                password_hash='test_hash',
                role='admin',
                name='测试用户'
            )
            db.session.add(user)
            db.session.commit()
            print("测试数据插入成功")
            
            # 查询测试数据
            test_user = User.query.first()
            print(f"查询到用户: {test_user.username}")
            
            # 删除测试数据
            db.session.delete(test_user)
            db.session.commit()
            print("测试数据删除成功")
            
        except Exception as e:
            db.session.rollback()
            print(f"数据库操作失败: {e}")

if __name__ == '__main__':
    test_database()