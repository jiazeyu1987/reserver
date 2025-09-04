from app import create_app, db
from app.models.appointment import PatientSubscription

app = create_app()
with app.app_context():
    # 更新订阅记录，将记录员ID从1改为2
    subscriptions = db.session.query(PatientSubscription).all()
    for subscription in subscriptions:
        print(f'Before: Subscription ID {subscription.id}, Patient ID {subscription.patient_id}, Recorder ID {subscription.recorder_id}')
        subscription.recorder_id = 2  # recorder001的ID
        print(f'After: Subscription ID {subscription.id}, Patient ID {subscription.patient_id}, Recorder ID {subscription.recorder_id}')
    
    db.session.commit()
    print("Subscription records updated successfully!")