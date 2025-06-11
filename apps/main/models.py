from .extensions import db
from datetime import datetime

class CalendarCredential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(50))  # 'ralph' or 'jessica'
    token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    token_uri = db.Column(db.String(500))
    client_id = db.Column(db.String(500))
    client_secret = db.Column(db.String(500))
    scopes = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50))  # 'mediation' or 'wellness'
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    appointment_time = db.Column(db.DateTime)
    google_event_id = db.Column(db.String(200))
    stripe_payment_id = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
