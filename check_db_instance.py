"""
检查db实例是否一致
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_db_instance():
    """检查db实例"""
    from app import create_app, db
    from app.models.user import User
    
    print(f"app中的db id: {id(db)}")
    
    app = create_app('development')
    
    with app.app_context():
        print(f"app_context中的db id: {id(db)}")
        
        # 检查User模型
        print(f"User模型: {User}")
        print(f"User.metadata: {User.metadata}")
        print(f"db.metadata: {db.metadata}")
        print(f"db.engine: {db.engine}")
        
        # 检查User表
        user_table = User.__table__
        print(f"User.__table__: {user_table}")
        print(f"User.__table__.metadata: {user_table.metadata}")
        print(f"User.__table__.metadata is db.metadata: {user_table.metadata is db.metadata}")

if __name__ == '__main__':
    check_db_instance()