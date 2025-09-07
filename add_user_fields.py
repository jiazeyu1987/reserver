#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为用户表添加注册功能所需的新字段
运行方法: python add_user_fields.py
"""

from app import create_app, db
from app.models.user import User

def add_user_fields():
    """添加用户表的新字段"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查数据库连接
            print("检查数据库连接...")
            db.engine.connect()
            print("[SUCCESS] 数据库连接成功")
            
            # 创建所有表（如果不存在）
            print("创建/更新数据库表...")
            db.create_all()
            print("[SUCCESS] 数据库表创建/更新完成")
            
            # 检查新字段是否已经存在
            print("检查新字段是否需要添加...")
            
            # 使用原生SQL添加字段（如果不存在）
            connection = db.engine.connect()
            
            # 添加邮箱字段（先不加UNIQUE约束）
            try:
                connection.execute(db.text("ALTER TABLE users ADD COLUMN email VARCHAR(255)"))
                print("[SUCCESS] 添加 email 字段成功")
            except Exception as e:
                if "Duplicate column name" in str(e) or "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("[INFO] email 字段已存在")
                else:
                    print(f"[WARNING] 添加 email 字段时出错: {e}")
            
            # 添加身份证号字段（先不加UNIQUE约束）
            try:
                connection.execute(db.text("ALTER TABLE users ADD COLUMN id_card VARCHAR(20)"))
                print("[SUCCESS] 添加 id_card 字段成功")
            except Exception as e:
                if "Duplicate column name" in str(e) or "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("[INFO] id_card 字段已存在")
                else:
                    print(f"[WARNING] 添加 id_card 字段时出错: {e}")
            
            # 添加地址字段
            try:
                connection.execute(db.text("ALTER TABLE users ADD COLUMN address TEXT"))
                print("[SUCCESS] 添加 address 字段成功")
            except Exception as e:
                if "Duplicate column name" in str(e) or "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("[INFO] address 字段已存在")
                else:
                    print(f"[WARNING] 添加 address 字段时出错: {e}")
            
            connection.close()
            
            # 验证字段是否添加成功
            print("\n验证字段添加结果...")
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('users')
            column_names = [col['name'] for col in columns]
            
            required_fields = ['email', 'id_card', 'address']
            for field in required_fields:
                if field in column_names:
                    print(f"[SUCCESS] {field} 字段存在")
                else:
                    print(f"[ERROR] {field} 字段不存在")
            
            print(f"\n当前用户表字段: {column_names}")
            print("\n[COMPLETED] 数据库迁移完成！")
            
        except Exception as e:
            print(f"[ERROR] 数据库迁移失败: {e}")
            raise

if __name__ == "__main__":
    add_user_fields()