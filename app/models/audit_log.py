from datetime import datetime
from app import db


class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(150))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details_json = db.Column(db.Text)
