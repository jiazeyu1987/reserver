import os
import sys
from app import create_app, db
from app.models.user import User

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_db():
    """调试数据库"""
    app = create_app('development')
    
    with app.app_context():
        # 打印数据库URL确认
        print(f"数据库URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 检查db对象
        print(f"db对象: {db}")
        print(f"db.metadata: {db.metadata}")
        print(f"db.metadata.tables: {db.metadata.tables}")
        
        # 检查User模型
        print(f"User模型: {User}")
        print(f"User.__table__: {User.__table__}")
        print(f"User.__tablename__: {User.__tablename__}")
        
        # 检查User表是否在metadata中
        if 'users' in db.metadata.tables:
            print("User表在metadata中")
        else:
            print("User表不在metadata中")
        
        # 手动将User表添加到metadata中
        print("手动注册表...")
        User.__table__.metadata = db.metadata
        if 'users' in db.metadata.tables:
            print("手动注册后，User表在metadata中")
        else:
            print("手动注册后，User表仍不在metadata中")
        
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
    debug_db()