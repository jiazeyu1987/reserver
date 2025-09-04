import os
import sys
from app import create_app, db
from app.models.user import User

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simple_test():
    """简单测试"""
    app = create_app('development')
    
    with app.app_context():
        # 打印数据库URL确认
        print(f"数据库URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 检查User模型是否正确注册
        print(f"User模型表名: {User.__tablename__}")
        print(f"User模型表对象: {User.__table__}")
        
        # 尝试创建表
        print("尝试创建表...")
        try:
            db.create_all()
            print("表创建成功")
        except Exception as e:
            print(f"表创建失败: {e}")
        
        # 检查表是否真的创建了
        try:
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"数据库中的表: {tables}")
        except Exception as e:
            print(f"检查表时出错: {e}")

if __name__ == '__main__':
    simple_test()