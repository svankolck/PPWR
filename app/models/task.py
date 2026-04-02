from datetime import datetime
from app import db

TASK_STATUSES = ['todo', 'in_progress', 'done', 'cancelled']
TASK_PRIORITIES = ['low', 'medium', 'high', 'urgent']


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    gap_id = db.Column(db.Integer, db.ForeignKey('gaps.id'), nullable=True)
    packaging_id = db.Column(db.Integer, db.ForeignKey('packaging.id'), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    assigned_to = db.Column(db.String(150))
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='todo')
    priority = db.Column(db.String(50), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    gap = db.relationship('Gap', backref='tasks')
