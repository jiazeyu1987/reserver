#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models.user import User, Recorder
from werkzeug.security import generate_password_hash

def create_recorder_accounts():
    app = create_app()
    
    with app.app_context():
        # 创建10个recorder账号
        for i in range(1, 11):
            username = f"recorder{i:03d}"  # recorder001, recorder002, etc.
            phone = f"138001380{i:02d}"  # 13800138001, 13800138002, etc.
            name = f"记录员{i:03d}"
            employee_id = f"EMP{i:04d}"  # EMP0001, EMP0002, etc.
            
            # 检查用户是否已存在
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"用户 {username} 已存在，跳过")
                continue
            
            # 检查手机号是否已存在
            existing_phone = User.query.filter_by(phone=phone).first()
            if existing_phone:
                print(f"手机号 {phone} 已存在，跳过")
                continue
            
            try:
                # 创建User记录
                user = User(
                    username=username,
                    phone=phone,
                    password_hash=generate_password_hash('recorder123'),
                    role='recorder',
                    name=name,
                    status='active'
                )
                db.session.add(user)
                db.session.flush()  # 获取user.id
                
                # 创建对应的Recorder记录
                recorder = Recorder(
                    user_id=user.id,
                    employee_id=employee_id,
                    is_on_duty=True
                )
                db.session.add(recorder)
                
                print(f"创建用户: {username} (密码: recorder123, 手机: {phone})")
                
            except Exception as e:
                print(f"创建用户 {username} 失败: {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print("\n所有recorder账号创建完成！")
        except Exception as e:
            print(f"提交数据库失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_recorder_accounts()