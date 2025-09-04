#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库迁移脚本 - 更新家庭和患者表结构
将旧的表结构更新为符合客户端的新结构
"""

from app import create_app, db
from sqlalchemy import text
import sys

def run_migration():
    """运行数据库迁移"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Starting database migration...")
        print("=" * 60)
        
        try:
            # Step 1: Update families table
            print("\nStep 1: Updating families table structure...")
            
            # Check current table structure
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(families)"))
                columns = [row[1] for row in result.fetchall()]
            print(f"Current families columns: {columns}")
            
            # Add new columns if not exist
            if 'householdHead' not in columns:
                print("   Adding householdHead column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE families ADD COLUMN householdHead VARCHAR(100)'))
                    conn.commit()
            
            if 'address' not in columns:
                print("   Adding address column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE families ADD COLUMN address TEXT'))
                    conn.commit()
            
            if 'phone' not in columns:
                print("   Adding phone column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE families ADD COLUMN phone VARCHAR(20)'))
                    conn.commit()
            
            # Migrate existing data
            print("   Migrating existing data...")
            if 'family_name' in columns:
                with db.engine.connect() as conn:
                    conn.execute(text('UPDATE families SET householdHead = family_name WHERE householdHead IS NULL'))
                    conn.commit()
            if 'primary_address' in columns:
                with db.engine.connect() as conn:
                    conn.execute(text('UPDATE families SET address = primary_address WHERE address IS NULL'))
                    conn.commit()
            if 'contact_phone' in columns:
                with db.engine.connect() as conn:
                    conn.execute(text('UPDATE families SET phone = contact_phone WHERE phone IS NULL'))
                    conn.commit()
            
            print("Families table update completed")
            
            # Step 2: Update patients table
            print("\nStep 2: Updating patients table structure...")
            
            # Check current table structure
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(patients)"))
                columns = [row[1] for row in result.fetchall()]
            print(f"Current patients columns: {columns}")
            
            # Add new columns if not exist
            if 'age' not in columns:
                print("   Adding age column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE patients ADD COLUMN age INTEGER'))
                    conn.commit()
            
            if 'relationship' not in columns:
                print("   Adding relationship column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE patients ADD COLUMN relationship VARCHAR(20)'))
                    conn.commit()
            
            if 'conditions' not in columns:
                print("   Adding conditions column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE patients ADD COLUMN conditions TEXT'))
                    conn.commit()
            
            if 'packageType' not in columns:
                print("   Adding packageType column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE patients ADD COLUMN packageType VARCHAR(50) DEFAULT "基础套餐"'))
                    conn.commit()
            
            if 'paymentStatus' not in columns:
                print("   Adding paymentStatus column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE patients ADD COLUMN paymentStatus VARCHAR(20) DEFAULT "normal"'))
                    conn.commit()
            
            if 'lastService' not in columns:
                print("   Adding lastService column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE patients ADD COLUMN lastService DATE'))
                    conn.commit()
            
            if 'medications' not in columns:
                print("   Adding medications column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE patients ADD COLUMN medications TEXT'))
                    conn.commit()
            
            # Migrate patient data
            print("   Migrating patient data...")
            if 'birth_date' in columns:
                # Calculate age from birth date
                with db.engine.connect() as conn:
                    conn.execute(text('''
                        UPDATE patients 
                        SET age = CAST((julianday('now') - julianday(birth_date)) / 365.25 AS INTEGER)
                        WHERE age IS NULL AND birth_date IS NOT NULL
                    '''))
                    conn.commit()
            
            if 'relationship_to_head' in columns:
                with db.engine.connect() as conn:
                    conn.execute(text('UPDATE patients SET relationship = relationship_to_head WHERE relationship IS NULL'))
                    conn.commit()
            
            if 'medical_history' in columns:
                with db.engine.connect() as conn:
                    conn.execute(text('UPDATE patients SET conditions = medical_history WHERE conditions IS NULL'))
                    conn.commit()
            
            if 'current_medications' in columns:
                with db.engine.connect() as conn:
                    conn.execute(text('UPDATE patients SET medications = current_medications WHERE medications IS NULL'))
                    conn.commit()
            
            print("Patients table update completed")
            
            # Step 3: Verify migration results
            print("\nStep 3: Verifying migration results...")
            
            # Check families table
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(families)"))
                new_family_columns = [row[1] for row in result.fetchall()]
            print(f"New families columns: {new_family_columns}")
            
            # Check patients table
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(patients)"))
                new_patient_columns = [row[1] for row in result.fetchall()]
            print(f"New patients columns: {new_patient_columns}")
            
            # Check data
            with db.engine.connect() as conn:
                families_count = conn.execute(text("SELECT COUNT(*) FROM families")).scalar()
                patients_count = conn.execute(text("SELECT COUNT(*) FROM patients")).scalar()
            print(f"Data count: families={families_count}, patients={patients_count}")
            
            print("\n" + "=" * 60)
            print("Database migration completed successfully!")
            print("=" * 60)
            print("- families table updated to new structure")
            print("- patients table updated to new structure") 
            print("- existing data migrated successfully")
            print("\nYou can now re-run the API tutorial!")
            
            return True
            
        except Exception as e:
            print(f"\nMigration failed: {e}")
            print("Please check:")
            print("1. Database file permissions are correct")
            print("2. Database is not being used by other processes")
            print("3. SQLite version supports ALTER TABLE")
            return False

if __name__ == '__main__':
    success = run_migration()
    if success:
        print("\nPlease re-run the tutorial:")
        print("python tutorial_api.py")
    else:
        print("\nMigration failed, please check error messages")
        sys.exit(1)