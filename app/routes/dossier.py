from flask import Blueprint, render_template, make_response
from flask_login import login_required
from app.models.packaging import Packaging, Assessment
from app.models.document import Document
from app.models.gap import Gap
from app.models.task import Task
from app.models.audit_log import AuditLog

dossier_bp = Blueprint('dossier', __name__, url_prefix='/dossier')


@dossier_bp.route('/<int:packaging_id>')
@login_required
def view(packaging_id):
    pkg = Packaging.query.get_or_404(packaging_id)
    components = pkg.components.all()
    suppliers = set()
    for c in components:
        if c.supplier:
            suppliers.add(c.supplier)
    documents = Document.query.filter_by(packaging_id=pkg.id).all()
    # Also grab component-level docs
    for c in components:
        for doc in Document.query.filter_by(component_id=c.id).all():
            if doc not in documents:
                documents.append(doc)
    assessments = Assessment.query.filter_by(packaging_id=pkg.id).all()
    gaps = Gap.query.filter_by(packaging_id=pkg.id).all()
    tasks = Task.query.filter_by(packaging_id=pkg.id).all()
    audit_logs = AuditLog.query.filter_by(entity_type='packaging', entity_id=pkg.id).order_by(AuditLog.timestamp.desc()).limit(20).all()

    return render_template('dossier/view.html', pkg=pkg, components=components,
                           suppliers=list(suppliers), documents=documents,
                           assessments=assessments, gaps=gaps, tasks=tasks,
                           audit_logs=audit_logs)


@dossier_bp.route('/<int:packaging_id>/export')
@login_required
def export_html(packaging_id):
    pkg = Packaging.query.get_or_404(packaging_id)
    components = pkg.components.all()
    suppliers = set()
    for c in components:
        if c.supplier:
            suppliers.add(c.supplier)
    documents = Document.query.filter_by(packaging_id=pkg.id).all()
    for c in components:
        for doc in Document.query.filter_by(component_id=c.id).all():
            if doc not in documents:
                documents.append(doc)
    assessments = Assessment.query.filter_by(packaging_id=pkg.id).all()
    gaps = Gap.query.filter_by(packaging_id=pkg.id).all()
    tasks = Task.query.filter_by(packaging_id=pkg.id).all()

    html = render_template('dossier/export.html', pkg=pkg, components=components,
                           suppliers=list(suppliers), documents=documents,
                           assessments=assessments, gaps=gaps, tasks=tasks)
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename=dossier_{pkg.code}.html'
    return response
