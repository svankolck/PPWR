from datetime import datetime
from app import db

DOCUMENT_TYPES = [
    'specification_sheet', 'material_declaration', 'food_contact_declaration',
    'recycled_content_statement', 'certificate', 'test_report',
    'substance_statement', 'supplier_declaration', 'artwork_label_file'
]

DOCUMENT_STATUSES = ['draft', 'received', 'approved', 'expired']


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    packaging_id = db.Column(db.Integer, db.ForeignKey('packaging.id'), nullable=True)
    component_id = db.Column(db.Integer, db.ForeignKey('packaging_components.id'), nullable=True)
    document_type = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    file_path = db.Column(db.String(500))
    version = db.Column(db.String(50))
    status = db.Column(db.String(50), default='draft')
    valid_from = db.Column(db.Date)
    valid_to = db.Column(db.Date)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewer = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text)

    component = db.relationship('PackagingComponent', backref='documents')
