"""
检查数据库中的用户
"""

import os
import sys
from app import create_app, db
from app.models.user import User

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_users():
    """检查用户"""
    app = create_app('development')
    
    with app.app_context():
        # 查询所有用户
        users = User.query.all()
        print(f"用户数量: {len(users)}")
        
        for user in users:
            print(f"用户: {user.username}, {user.name}, {user.role}")
            print(f"  密码哈希: {user.password_hash}")
        
        if len(users) == 0:
            print("数据库中没有用户！")

if __name__ == '__main__':
    check_users()