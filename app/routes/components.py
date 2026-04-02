from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models.packaging import Packaging, PackagingComponent
from app.models.supplier import Supplier
from app.services.audit_service import log_action

components_bp = Blueprint('components', __name__, url_prefix='/components')


@components_bp.route('/create/<int:packaging_id>', methods=['GET', 'POST'])
@login_required
def create(packaging_id):
    pkg = Packaging.query.get_or_404(packaging_id)
    suppliers = Supplier.query.order_by(Supplier.name).all()
    if request.method == 'POST':
        comp = PackagingComponent(
            packaging_id=pkg.id,
            name=request.form['name'],
            material=request.form.get('material'),
            weight_grams=_parse_float(request.form.get('weight_grams')),
            recycled_content_pct=_parse_float(request.form.get('recycled_content_pct')),
            food_contact=request.form.get('food_contact') == 'on',
            supplier_id=_parse_int(request.form.get('supplier_id')),
            notes=request.form.get('notes'),
        )
        db.session.add(comp)
        db.session.commit()
        log_action('component', comp.id, 'created', {'packaging_id': pkg.id})
        flash('Component added.', 'success')
        return redirect(url_for('packaging.detail', id=pkg.id))
    return render_template('components/form.html', pkg=pkg, component=None, suppliers=suppliers)


@components_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    comp = PackagingComponent.query.get_or_404(id)
    suppliers = Supplier.query.order_by(Supplier.name).all()
    if request.method == 'POST':
        comp.name = request.form['name']
        comp.material = request.form.get('material')
        comp.weight_grams = _parse_float(request.form.get('weight_grams'))
        comp.recycled_content_pct = _parse_float(request.form.get('recycled_content_pct'))
        comp.food_contact = request.form.get('food_contact') == 'on'
        comp.supplier_id = _parse_int(request.form.get('supplier_id'))
        comp.notes = request.form.get('notes')
        db.session.commit()
        log_action('component', comp.id, 'updated')
        flash('Component updated.', 'success')
        return redirect(url_for('packaging.detail', id=comp.packaging_id))
    return render_template('components/form.html', pkg=comp.packaging, component=comp, suppliers=suppliers)


@components_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    comp = PackagingComponent.query.get_or_404(id)
    pkg_id = comp.packaging_id
    db.session.delete(comp)
    db.session.commit()
    log_action('component', id, 'deleted', {'packaging_id': pkg_id})
    flash('Component deleted.', 'info')
    return redirect(url_for('packaging.detail', id=pkg_id))


def _parse_float(val):
    if val and val.strip():
        try:
            return float(val)
        except ValueError:
            return None
    return None


def _parse_int(val):
    if val and val.strip():
        try:
            return int(val)
        except ValueError:
            return None
    return None
