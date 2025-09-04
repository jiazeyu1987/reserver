"""Update family and patient models for client compatibility

Revision ID: update_family_patient_models
Revises: 
Create Date: 2025-01-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'update_family_patient_models'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 修改families表
    op.add_column('families', sa.Column('householdHead', sa.String(100), nullable=True))
    op.add_column('families', sa.Column('address', sa.Text(), nullable=True))  
    op.add_column('families', sa.Column('phone', sa.String(20), nullable=True))
    
    # 迁移现有数据
    op.execute("UPDATE families SET householdHead = family_name WHERE householdHead IS NULL")
    op.execute("UPDATE families SET address = primary_address WHERE address IS NULL") 
    op.execute("UPDATE families SET phone = contact_phone WHERE phone IS NULL")
    
    # 删除旧字段
    op.drop_column('families', 'family_name')
    op.drop_column('families', 'primary_address')
    op.drop_column('families', 'secondary_address') 
    op.drop_column('families', 'contact_phone')
    
    # 设置新字段为不可空
    op.alter_column('families', 'householdHead', nullable=False)
    op.alter_column('families', 'address', nullable=False)
    op.alter_column('families', 'phone', nullable=False)
    
    # 修改patients表
    op.add_column('patients', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('patients', sa.Column('relationship', sa.String(20), nullable=True))
    op.add_column('patients', sa.Column('conditions', sa.Text(), nullable=True))
    op.add_column('patients', sa.Column('packageType', sa.String(50), nullable=False, server_default='基础套餐'))
    op.add_column('patients', sa.Column('paymentStatus', sa.String(20), nullable=False, server_default='normal'))
    op.add_column('patients', sa.Column('lastService', sa.Date(), nullable=True))
    op.add_column('patients', sa.Column('medications', sa.Text(), nullable=True))
    
    # 迁移现有数据 - 从出生日期计算年龄
    op.execute("""
        UPDATE patients 
        SET age = YEAR(CURDATE()) - YEAR(birth_date) - (DATE_FORMAT(CURDATE(), '%m%d') < DATE_FORMAT(birth_date, '%m%d'))
        WHERE age IS NULL AND birth_date IS NOT NULL
    """)
    op.execute("UPDATE patients SET relationship = relationship_to_head WHERE relationship IS NULL")
    op.execute("UPDATE patients SET conditions = medical_history WHERE conditions IS NULL")
    
    # 修改gender字段类型
    op.alter_column('patients', 'gender', type_=sa.String(10))
    
    # 删除旧字段
    op.drop_column('patients', 'birth_date')
    op.drop_column('patients', 'relationship_to_head')
    op.drop_column('patients', 'medical_history')
    op.drop_column('patients', 'allergies')
    op.drop_column('patients', 'current_medications')
    op.drop_column('patients', 'service_preferences')
    
    # 设置新字段约束
    op.alter_column('patients', 'age', nullable=False)
    op.alter_column('patients', 'relationship', nullable=False)

def downgrade():
    # 恢复patients表
    op.add_column('patients', sa.Column('birth_date', sa.Date(), nullable=True))
    op.add_column('patients', sa.Column('relationship_to_head', sa.String(20), nullable=True))  
    op.add_column('patients', sa.Column('medical_history', sa.Text(), nullable=True))
    op.add_column('patients', sa.Column('allergies', sa.Text(), nullable=True))
    op.add_column('patients', sa.Column('current_medications', sa.Text(), nullable=True))
    op.add_column('patients', sa.Column('service_preferences', sa.Text(), nullable=True))
    
    # 恢复数据
    op.execute("""
        UPDATE patients 
        SET birth_date = DATE(CONCAT(YEAR(CURDATE()) - age, '-01-01'))
        WHERE birth_date IS NULL AND age IS NOT NULL
    """)
    op.execute("UPDATE patients SET relationship_to_head = relationship WHERE relationship_to_head IS NULL")
    op.execute("UPDATE patients SET medical_history = conditions WHERE medical_history IS NULL")
    
    # 删除新字段
    op.drop_column('patients', 'medications')
    op.drop_column('patients', 'lastService')
    op.drop_column('patients', 'paymentStatus')
    op.drop_column('patients', 'packageType')
    op.drop_column('patients', 'conditions')
    op.drop_column('patients', 'relationship')
    op.drop_column('patients', 'age')
    
    # 恢复families表
    op.add_column('families', sa.Column('family_name', sa.String(100), nullable=True))
    op.add_column('families', sa.Column('primary_address', sa.Text(), nullable=True))
    op.add_column('families', sa.Column('secondary_address', sa.Text(), nullable=True))
    op.add_column('families', sa.Column('contact_phone', sa.String(20), nullable=True))
    
    # 恢复数据
    op.execute("UPDATE families SET family_name = householdHead WHERE family_name IS NULL")
    op.execute("UPDATE families SET primary_address = address WHERE primary_address IS NULL")
    op.execute("UPDATE families SET contact_phone = phone WHERE contact_phone IS NULL")
    
    # 删除新字段
    op.drop_column('families', 'phone')
    op.drop_column('families', 'address')
    op.drop_column('families', 'householdHead')