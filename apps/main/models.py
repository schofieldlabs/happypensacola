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
