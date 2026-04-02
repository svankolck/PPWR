from datetime import datetime
import json
from app import db

REQUIREMENT_STATUSES = ['active', 'future', 'pending_interpretation']
REQUIREMENT_CATEGORIES = [
    'recycled_content', 'recyclability', 'minimisation',
    'reuse', 'labelling', 'food_contact', 'substance_restrictions',
    'compostability', 'documentation', 'design_for_recycling'
]


class Requirement(db.Model):
    __tablename__ = 'requirements'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')
    applies_to_packaging_types = db.Column(db.Text)  # JSON list
    applies_to_materials = db.Column(db.Text)  # JSON list
    food_contact_relevant = db.Column(db.Boolean, default=False)
    required_fields_json = db.Column(db.Text)  # JSON list
    required_document_types_json = db.Column(db.Text)  # JSON list
    severity_default = db.Column(db.String(50), default='medium')
    effective_from = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text)

    def get_packaging_types(self):
        if self.applies_to_packaging_types:
            return json.loads(self.applies_to_packaging_types)
        return []

    def get_materials(self):
        if self.applies_to_materials:
            return json.loads(self.applies_to_materials)
        return []

    def get_required_fields(self):
        if self.required_fields_json:
            return json.loads(self.required_fields_json)
        return []

    def get_required_document_types(self):
        if self.required_document_types_json:
            return json.loads(self.required_document_types_json)
        return []
