import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory
from flask_login import login_required
from werkzeug.utils import secure_filename
from app import db
from app.models.document import Document, DOCUMENT_TYPES, DOCUMENT_STATUSES
from app.models.packaging import Packaging
from app.models.supplier import Supplier
from app.models.packaging import PackagingComponent
from app.services.audit_service import log_action
from datetime import datetime

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')


@documents_bp.route('/')
@login_required
def list_documents():
    type_filter = request.args.get('type')
    status_filter = request.args.get('status')
    search = request.args.get('search', '')
    query = Document.query
    if type_filter:
        query = query.filter_by(document_type=type_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search:
        query = query.filter(Document.title.ilike(f'%{search}%'))
    items = query.order_by(Document.uploaded_at.desc()).all()
    return render_template('documents/list.html', items=items, document_types=DOCUMENT_TYPES,
                           document_statuses=DOCUMENT_STATUSES, current_type=type_filter,
                           current_status=status_filter, search=search)


@documents_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    packaging_items = Packaging.query.order_by(Packaging.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    components = PackagingComponent.query.order_by(PackagingComponent.name).all()

    if request.method == 'POST':
        file = request.files.get('file')
        file_path = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            # Add timestamp to avoid collisions
            ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = f"{ts}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_path = filename  # store relative path

        valid_from = request.form.get('valid_from')
        valid_to = request.form.get('valid_to')

        doc = Document(
            title=request.form['title'],
            document_type=request.form['document_type'],
            packaging_id=_parse_int(request.form.get('packaging_id')),
            supplier_id=_parse_int(request.form.get('supplier_id')),
            component_id=_parse_int(request.form.get('component_id')),
            version=request.form.get('version'),
            status=request.form.get('status', 'draft'),
            valid_from=datetime.strptime(valid_from, '%Y-%m-%d').date() if valid_from else None,
            valid_to=datetime.strptime(valid_to, '%Y-%m-%d').date() if valid_to else None,
            file_path=file_path,
            notes=request.form.get('notes'),
        )
        db.session.add(doc)
        db.session.commit()
        log_action('document', doc.id, 'uploaded')
        flash('Document uploaded.', 'success')
        return redirect(url_for('documents.list_documents'))

    return render_template('documents/upload.html', document_types=DOCUMENT_TYPES,
                           document_statuses=DOCUMENT_STATUSES, packaging_items=packaging_items,
                           suppliers=suppliers, components=components)


@documents_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    doc = Document.query.get_or_404(id)
    packaging_items = Packaging.query.order_by(Packaging.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    components = PackagingComponent.query.order_by(PackagingComponent.name).all()

    if request.method == 'POST':
        doc.title = request.form['title']
        doc.document_type = request.form['document_type']
        doc.packaging_id = _parse_int(request.form.get('packaging_id'))
        doc.supplier_id = _parse_int(request.form.get('supplier_id'))
        doc.component_id = _parse_int(request.form.get('component_id'))
        doc.version = request.form.get('version')
        doc.status = request.form.get('status', 'draft')
        valid_from = request.form.get('valid_from')
        valid_to = request.form.get('valid_to')
        doc.valid_from = datetime.strptime(valid_from, '%Y-%m-%d').date() if valid_from else None
        doc.valid_to = datetime.strptime(valid_to, '%Y-%m-%d').date() if valid_to else None
        doc.notes = request.form.get('notes')
        db.session.commit()
        log_action('document', doc.id, 'updated')
        flash('Document updated.', 'success')
        return redirect(url_for('documents.list_documents'))

    return render_template('documents/edit.html', doc=doc, document_types=DOCUMENT_TYPES,
                           document_statuses=DOCUMENT_STATUSES, packaging_items=packaging_items,
                           suppliers=suppliers, components=components)


@documents_bp.route('/download/<path:filename>')
@login_required
def download(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


def _parse_int(val):
    if val and val.strip():
        try:
            return int(val)
        except ValueError:
            return None
    return None
