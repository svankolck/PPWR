from datetime import datetime
from app import db

GAP_SEVERITIES = ['low', 'medium', 'high', 'critical']
GAP_STATUSES = ['open', 'in_progress', 'resolved', 'accepted', 'closed']


class Gap(db.Model):
    __tablename__ = 'gaps'

    id = db.Column(db.Integer, primary_key=True)
    packaging_id = db.Column(db.Integer, db.ForeignKey('packaging.id'), nullable=True)
    requirement_id = db.Column(db.Integer, db.ForeignKey('requirements.id'), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(50), default='medium')
    owner = db.Column(db.String(150))
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requirement = db.relationship('Requirement', backref='gaps')
