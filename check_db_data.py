from app import create_app, db
from app.models.patient import Family
from app.models.user import User
from app.models.appointment import PatientSubscription

app = create_app()
with app.app_context():
    print('Family count:', db.session.query(Family).count())
    families = db.session.query(Family).all()
    for f in families:
        print(f'Family: {f.family_name}, ID: {f.id}')
    
    print('User count:', db.session.query(User).count())
    users = db.session.query(User).all()
    for u in users:
        print(f'User: {u.username}, ID: {u.id}, Role: {u.role}')
        
    print('Subscription count:', db.session.query(PatientSubscription).count())
    subscriptions = db.session.query(PatientSubscription).all()
    for s in subscriptions:
        print(f'Subscription: Patient ID {s.patient_id}, Recorder ID {s.recorder_id}')