from datetime import datetime
from app import db

SUPPLIER_STATUSES = ['active', 'inactive', 'pending', 'blocked']


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    supplier_code = db.Column(db.String(50), unique=True, nullable=False)
    country = db.Column(db.String(100))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    status = db.Column(db.String(50), default='active')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contacts = db.relationship('SupplierContact', backref='supplier', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='supplier', lazy='dynamic')
    gaps = db.relationship('Gap', backref='supplier', lazy='dynamic')
    tasks = db.relationship('Task', backref='supplier', lazy='dynamic')


class SupplierContact(db.Model):
    __tablename__ = 'supplier_contacts'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(200))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(50))
