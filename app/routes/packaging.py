from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models.packaging import Packaging, PackagingComponent, PACKAGING_TYPES, PACKAGING_STATUSES, Assessment
from app.models.supplier import Supplier
from app.models.document import Document
from app.models.gap import Gap
from app.models.task import Task
from app.models.audit_log import AuditLog
from app.services.audit_service import log_action
from app.services.assessment_service import run_assessment
from app.services.gap_service import generate_gaps
from app.services.status_service import calculate_status

packaging_bp = Blueprint('packaging', __name__, url_prefix='/packaging')


@packaging_bp.route('/')
@login_required
def list_packaging():
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')
    search = request.args.get('search', '')

    query = Packaging.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(packaging_type=type_filter)
    if search:
        query = query.filter(
            db.or_(Packaging.name.ilike(f'%{search}%'), Packaging.code.ilike(f'%{search}%'))
        )
    items = query.order_by(Packaging.updated_at.desc()).all()
    return render_template('packaging/list.html', items=items, packaging_types=PACKAGING_TYPES,
                           statuses=PACKAGING_STATUSES, current_status=status_filter,
                           current_type=type_filter, search=search)


@packaging_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        pkg = Packaging(
            code=request.form['code'],
            name=request.form['name'],
            sku_or_product_family=request.form.get('sku_or_product_family'),
            market=request.form.get('market'),
            packaging_type=request.form['packaging_type'],
            owner_name=request.form.get('owner_name'),
            notes=request.form.get('notes'),
        )
        db.session.add(pkg)
        db.session.commit()
        log_action('packaging', pkg.id, 'created')
        flash('Packaging item created.', 'success')
        return redirect(url_for('packaging.detail', id=pkg.id))
    return render_template('packaging/form.html', packaging=None, packaging_types=PACKAGING_TYPES)


@packaging_bp.route('/<int:id>')
@login_required
def detail(id):
    pkg = Packaging.query.get_or_404(id)
    components = pkg.components.all()
    documents = Document.query.filter_by(packaging_id=pkg.id).all()
    assessments = Assessment.query.filter_by(packaging_id=pkg.id).all()
    gaps = Gap.query.filter_by(packaging_id=pkg.id).all()
    tasks = Task.query.filter_by(packaging_id=pkg.id).all()
    suppliers = set()
    for c in components:
        if c.supplier:
            suppliers.add(c.supplier)
    audit_logs = AuditLog.query.filter_by(entity_type='packaging', entity_id=pkg.id).order_by(AuditLog.timestamp.desc()).all()
    return render_template('packaging/detail.html', pkg=pkg, components=components,
                           documents=documents, assessments=assessments, gaps=gaps,
                           tasks=tasks, suppliers=list(suppliers), audit_logs=audit_logs)


@packaging_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    pkg = Packaging.query.get_or_404(id)
    if request.method == 'POST':
        pkg.code = request.form['code']
        pkg.name = request.form['name']
        pkg.sku_or_product_family = request.form.get('sku_or_product_family')
        pkg.market = request.form.get('market')
        pkg.packaging_type = request.form['packaging_type']
        pkg.owner_name = request.form.get('owner_name')
        pkg.notes = request.form.get('notes')
        db.session.commit()
        log_action('packaging', pkg.id, 'updated')
        flash('Packaging item updated.', 'success')
        return redirect(url_for('packaging.detail', id=pkg.id))
    return render_template('packaging/form.html', packaging=pkg, packaging_types=PACKAGING_TYPES)


@packaging_bp.route('/<int:id>/archive', methods=['POST'])
@login_required
def archive(id):
    pkg = Packaging.query.get_or_404(id)
    pkg.status = 'archived'
    db.session.commit()
    log_action('packaging', pkg.id, 'archived')
    flash('Packaging item archived.', 'info')
    return redirect(url_for('packaging.list_packaging'))


@packaging_bp.route('/<int:id>/assess', methods=['POST'])
@login_required
def assess(id):
    pkg = Packaging.query.get_or_404(id)
    run_assessment(pkg)
    pkg.status = calculate_status(pkg)
    db.session.commit()
    log_action('packaging', pkg.id, 'assessed')
    flash('Assessment completed.', 'success')
    return redirect(url_for('packaging.detail', id=pkg.id))


@packaging_bp.route('/<int:id>/generate-gaps', methods=['POST'])
@login_required
def gen_gaps(id):
    pkg = Packaging.query.get_or_404(id)
    gaps = generate_gaps(pkg)
    pkg.status = calculate_status(pkg)
    db.session.commit()
    log_action('packaging', pkg.id, 'gaps_generated', {'count': len(gaps)})
    flash(f'{len(gaps)} gaps generated/found.', 'success')
    return redirect(url_for('packaging.detail', id=pkg.id))
