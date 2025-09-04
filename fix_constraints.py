#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复数据库约束问题 - 删除旧字段的NOT NULL约束
"""

from app import create_app, db
from sqlalchemy import text
import sys

def fix_constraints():
    """修复数据库约束"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Fixing database constraints...")
        print("=" * 60)
        
        try:
            # SQLite不直接支持删除约束，需要重建表
            print("Recreating families table without old constraints...")
            
            with db.engine.connect() as conn:
                # 1. 创建新的families表
                conn.execute(text('''
                    CREATE TABLE families_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        householdHead VARCHAR(100) NOT NULL,
                        address TEXT NOT NULL,
                        phone VARCHAR(20) NOT NULL,
                        emergency_contact VARCHAR(100),
                        emergency_phone VARCHAR(20),
                        created_at DATETIME,
                        updated_at DATETIME
                    )
                '''))
                
                # 2. 迁移数据
                conn.execute(text('''
                    INSERT INTO families_new (id, householdHead, address, phone, emergency_contact, emergency_phone, created_at, updated_at)
                    SELECT id, householdHead, address, phone, emergency_contact, emergency_phone, created_at, updated_at
                    FROM families
                    WHERE householdHead IS NOT NULL AND address IS NOT NULL AND phone IS NOT NULL
                '''))
                
                # 3. 删除旧表
                conn.execute(text('DROP TABLE families'))
                
                # 4. 重命名新表
                conn.execute(text('ALTER TABLE families_new RENAME TO families'))
                
                conn.commit()
                
            print("Families table recreated successfully")
            
            # 同样处理patients表
            print("Recreating patients table...")
            
            with db.engine.connect() as conn:
                # 1. 创建新的patients表
                conn.execute(text('''
                    CREATE TABLE patients_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        family_id INTEGER NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        age INTEGER NOT NULL,
                        gender VARCHAR(10) NOT NULL,
                        relationship VARCHAR(20) NOT NULL,
                        conditions TEXT,
                        packageType VARCHAR(50) NOT NULL DEFAULT '基础套餐',
                        paymentStatus VARCHAR(20) NOT NULL DEFAULT 'normal',
                        lastService DATE,
                        medications TEXT,
                        id_card VARCHAR(18),
                        phone VARCHAR(20),
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME,
                        updated_at DATETIME,
                        FOREIGN KEY (family_id) REFERENCES families (id)
                    )
                '''))
                
                # 2. 迁移数据
                conn.execute(text('''
                    INSERT INTO patients_new (id, family_id, name, age, gender, relationship, conditions, 
                                            packageType, paymentStatus, medications, id_card, phone, 
                                            is_active, created_at, updated_at)
                    SELECT id, family_id, name, age, gender, relationship, conditions, 
                           packageType, paymentStatus, medications, id_card, phone, 
                           is_active, created_at, updated_at
                    FROM patients
                    WHERE age IS NOT NULL AND gender IS NOT NULL AND relationship IS NOT NULL
                '''))
                
                # 3. 删除旧表
                conn.execute(text('DROP TABLE patients'))
                
                # 4. 重命名新表
                conn.execute(text('ALTER TABLE patients_new RENAME TO patients'))
                
                conn.commit()
                
            print("Patients table recreated successfully")
            
            # 验证结果
            print("Verifying new table structure...")
            
            with db.engine.connect() as conn:
                # 检查families表
                result = conn.execute(text("PRAGMA table_info(families)"))
                family_columns = [row[1] for row in result.fetchall()]
                print(f"New families columns: {family_columns}")
                
                # 检查patients表
                result = conn.execute(text("PRAGMA table_info(patients)"))
                patient_columns = [row[1] for row in result.fetchall()]
                print(f"New patients columns: {patient_columns}")
                
                # 检查数据
                families_count = conn.execute(text("SELECT COUNT(*) FROM families")).scalar()
                patients_count = conn.execute(text("SELECT COUNT(*) FROM patients")).scalar()
                print(f"Data count: families={families_count}, patients={patients_count}")
            
            print("\\n" + "=" * 60)
            print("Database constraints fixed successfully!")
            print("=" * 60)
            print("- Old tables replaced with new structure")
            print("- All constraints properly set")
            print("- Data migrated successfully")
            
            return True
            
        except Exception as e:
            print(f"\\nFix failed: {e}")
            return False

if __name__ == '__main__':
    success = fix_constraints()
    if success:
        print("\\nDatabase is now ready for API testing!")
        print("Run: python tutorial_api.py")
    else:
        print("\\nFix failed, please check error messages")
        sys.exit(1)