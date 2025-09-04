"""
检查数据库表结构
"""

import sqlite3
import os
import sys
from app import create_app, db

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_tables():
    """检查数据库表结构"""
    app = create_app('development')
    
    with app.app_context():
        # 获取数据库文件路径
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            db_path = db_uri
        
        print(f"数据库文件路径: {db_path}")
        
        # 直接使用SQLite连接检查表
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 查看所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("\n现有表:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # 如果没有表，先创建
            if not tables:
                print("\n没有找到表，开始创建...")
                # 使用Flask-SQLAlchemy创建表
                db.create_all()
                print("表创建完成")
                
                # 重新查看表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print("\n新创建的表:")
                for table in tables:
                    print(f"  - {table[0]}")
            
            # 检查appointments表结构
            if any(table[0] == 'appointments' for table in tables):
                print("\nappointments表结构:")
                cursor.execute("PRAGMA table_info(appointments)")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'DEFAULT ' + str(col[4]) if col[4] else ''}")
            
        except Exception as e:
            print(f"检查失败: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    check_tables()