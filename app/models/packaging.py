from datetime import datetime
from app import db

PACKAGING_TYPES = ['sales', 'grouped', 'transport', 'e-commerce']
PACKAGING_STATUSES = ['draft', 'in_review', 'missing_evidence', 'at_risk', 'approved', 'archived']


class Packaging(db.Model):
    __tablename__ = 'packaging'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    sku_or_product_family = db.Column(db.String(200))
    market = db.Column(db.String(100))
    packaging_type = db.Column(db.String(50), nullable=False)
    owner_name = db.Column(db.String(150))
    status = db.Column(db.String(50), default='draft')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    components = db.relationship('PackagingComponent', backref='packaging', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='packaging', lazy='dynamic')
    assessments = db.relationship('Assessment', backref='packaging', lazy='dynamic', cascade='all, delete-orphan')
    gaps = db.relationship('Gap', backref='packaging', lazy='dynamic')
    tasks = db.relationship('Task', backref='packaging', lazy='dynamic')

    def get_materials(self):
        return list(set(c.material for c in self.components if c.material))

    def has_food_contact(self):
        return any(c.food_contact for c in self.components)


class PackagingComponent(db.Model):
    __tablename__ = 'packaging_components'

    id = db.Column(db.Integer, primary_key=True)
    packaging_id = db.Column(db.Integer, db.ForeignKey('packaging.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    material = db.Column(db.String(100))
    weight_grams = db.Column(db.Float)
    recycled_content_pct = db.Column(db.Float)
    food_contact = db.Column(db.Boolean, default=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', backref='components')


class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    packaging_id = db.Column(db.Integer, db.ForeignKey('packaging.id'), nullable=False)
    requirement_id = db.Column(db.Integer, db.ForeignKey('requirements.id'), nullable=False)
    applicability_status = db.Column(db.String(50), default='applicable')  # applicable, not_applicable, under_review
    evidence_status = db.Column(db.String(50), default='missing')  # complete, partial, missing
    overall_status = db.Column(db.String(50), default='open')  # open, compliant, non_compliant, waived
    rationale = db.Column(db.Text)
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow)

    requirement = db.relationship('Requirement', backref='assessments')
