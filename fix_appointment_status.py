#!/usr/bin/env python3
"""
Fix appointment status database issue by updating 'in-progress' to 'confirmed'
"""

from app import create_app
from app.models.appointment import Appointment
from app import db

def fix_appointment_status():
    """Update any appointments with 'in-progress' status to 'confirmed'"""
    app = create_app()
    
    with app.app_context():
        try:
            # Use raw SQL to update records with invalid enum values
            from sqlalchemy import text
            result = db.session.execute(
                text("UPDATE appointments SET status = 'confirmed' WHERE status = 'in-progress'")
            )
            db.session.commit()
            
            print(f"Successfully updated {result.rowcount} appointments from 'in-progress' to 'confirmed'")
            
            # Verify the fix by counting appointments
            confirmed_count = db.session.execute(
                text("SELECT COUNT(*) FROM appointments WHERE status = 'confirmed'")
            ).scalar()
            print(f"Total confirmed appointments: {confirmed_count}")
            
        except Exception as e:
            print(f"Error fixing appointment status: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_appointment_status()