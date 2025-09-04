"""
数据库迁移脚本 - 添加新的字段和表
"""

import sqlite3
import os
import sys
from app import create_app, db

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """迁移数据库，添加新字段和表"""
    app = create_app('development')
    
    with app.app_context():
        # 获取数据库文件路径
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            db_path = db_uri
        
        print(f"数据库文件路径: {db_path}")
        
        # 直接使用SQLite连接执行迁移
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            print("开始数据库迁移...")
            
            # 检查是否已有service_types表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='service_types'")
            if not cursor.fetchone():
                print("创建service_types表...")
                cursor.execute('''
                CREATE TABLE service_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    default_duration INTEGER,
                    base_price DECIMAL(10,2),
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # 插入默认服务类型
                service_types = [
                    ('基础健康监测', '基本的生命体征监测，包括血压、心率、血糖等', 60, 200.00),
                    ('综合健康评估', '全面的健康状态评估和建议', 90, 350.00),
                    ('康复训练指导', '专业的康复训练指导和辅助', 120, 400.00),
                ]
                
                cursor.executemany('''
                INSERT INTO service_types (name, description, default_duration, base_price, is_active)
                VALUES (?, ?, ?, ?, 1)
                ''', service_types)
            
            # 检查是否已有payments表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payments'")
            if not cursor.fetchone():
                print("创建payments表...")
                cursor.execute('''
                CREATE TABLE payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appointment_id INTEGER NOT NULL,
                    patient_id INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    payment_method VARCHAR(20) NOT NULL,
                    payment_status VARCHAR(20) DEFAULT 'pending',
                    transaction_id VARCHAR(100),
                    payment_date TIMESTAMP,
                    refund_amount DECIMAL(10,2) DEFAULT 0,
                    refund_date TIMESTAMP,
                    refund_reason TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (appointment_id) REFERENCES appointments(id),
                    FOREIGN KEY (patient_id) REFERENCES patients(id)
                )
                ''')
            
            # 检查appointments表是否有新字段
            cursor.execute("PRAGMA table_info(appointments)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'service_type_id' not in columns:
                print("为appointments表添加service_type_id字段...")
                cursor.execute('ALTER TABLE appointments ADD COLUMN service_type_id INTEGER')
                cursor.execute('ALTER TABLE appointments ADD COLUMN end_time TIME')
                
                # 更新现有预约的状态枚举值
                print("更新appointments表状态字段...")
                # 注意：SQLite不支持直接修改枚举，我们需要创建新表并迁移数据
                
                # 先创建临时表
                cursor.execute('''
                CREATE TABLE appointments_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    recorder_id INTEGER NOT NULL,
                    service_type_id INTEGER,
                    scheduled_date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME,
                    appointment_type VARCHAR(20) DEFAULT 'regular',
                    status VARCHAR(20) DEFAULT 'scheduled',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(id),
                    FOREIGN KEY (recorder_id) REFERENCES users(id),
                    FOREIGN KEY (service_type_id) REFERENCES service_types(id)
                )
                ''')
                
                # 复制数据到新表
                cursor.execute('''
                INSERT INTO appointments_new (
                    id, patient_id, recorder_id, service_type_id, scheduled_date, 
                    start_time, end_time, appointment_type, status, notes, created_at, updated_at
                )
                SELECT 
                    id, patient_id, recorder_id, 1 as service_type_id, 
                    scheduled_date, start_time, NULL as end_time, 
                    'regular' as appointment_type, status, notes, created_at, updated_at
                FROM appointments
                ''')
                
                # 删除旧表
                cursor.execute('DROP TABLE appointments')
                
                # 重命名新表
                cursor.execute('ALTER TABLE appointments_new RENAME TO appointments')
                
                print("appointments表迁移完成")
            
            conn.commit()
            print("数据库迁移完成！")
            
        except Exception as e:
            conn.rollback()
            print(f"数据库迁移失败: {e}")
            raise e
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_database()