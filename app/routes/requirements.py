import json
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models.requirement import Requirement, REQUIREMENT_CATEGORIES, REQUIREMENT_STATUSES
from app.models.packaging import PACKAGING_TYPES

requirements_bp = Blueprint('requirements', __name__, url_prefix='/requirements')


@requirements_bp.route('/')
@login_required
def list_requirements():
    category_filter = request.args.get('category')
    query = Requirement.query
    if category_filter:
        query = query.filter_by(category=category_filter)
    items = query.order_by(Requirement.code).all()
    return render_template('requirements/list.html', items=items,
                           categories=REQUIREMENT_CATEGORIES, current_category=category_filter)


@requirements_bp.route('/<int:id>')
@login_required
def detail(id):
    req = Requirement.query.get_or_404(id)
    return render_template('requirements/detail.html', req=req)


@requirements_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        req = _build_requirement(Requirement(), request.form)
        db.session.add(req)
        db.session.commit()
        flash('Requirement created.', 'success')
        return redirect(url_for('requirements.list_requirements'))
    return render_template('requirements/form.html', req=None, categories=REQUIREMENT_CATEGORIES,
                           statuses=REQUIREMENT_STATUSES, packaging_types=PACKAGING_TYPES)


@requirements_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    req = Requirement.query.get_or_404(id)
    if request.method == 'POST':
        _build_requirement(req, request.form)
        db.session.commit()
        flash('Requirement updated.', 'success')
        return redirect(url_for('requirements.detail', id=req.id))
    return render_template('requirements/form.html', req=req, categories=REQUIREMENT_CATEGORIES,
                           statuses=REQUIREMENT_STATUSES, packaging_types=PACKAGING_TYPES)


def _build_requirement(req, form):
    req.code = form['code']
    req.name = form['name']
    req.category = form['category']
    req.description = form.get('description')
    req.status = form.get('status', 'active')
    req.food_contact_relevant = form.get('food_contact_relevant') == 'on'
    req.severity_default = form.get('severity_default', 'medium')

    pkg_types = form.getlist('applies_to_packaging_types')
    req.applies_to_packaging_types = json.dumps(pkg_types) if pkg_types else None

    materials = form.get('applies_to_materials', '')
    if materials.strip():
        req.applies_to_materials = json.dumps([m.strip() for m in materials.split(',')])
    else:
        req.applies_to_materials = None

    req_fields = form.get('required_fields', '')
    if req_fields.strip():
        req.required_fields_json = json.dumps([f.strip() for f in req_fields.split(',')])
    else:
        req.required_fields_json = None

    doc_types = form.getlist('required_document_types')
    req.required_document_types_json = json.dumps(doc_types) if doc_types else None

    req.notes = form.get('notes')
    return req
