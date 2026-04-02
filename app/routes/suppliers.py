from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models.supplier import Supplier, SupplierContact, SUPPLIER_STATUSES
from app.models.document import Document
from app.models.packaging import PackagingComponent
from app.services.audit_service import log_action

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')


@suppliers_bp.route('/')
@login_required
def list_suppliers():
    search = request.args.get('search', '')
    query = Supplier.query
    if search:
        query = query.filter(
            db.or_(Supplier.name.ilike(f'%{search}%'), Supplier.supplier_code.ilike(f'%{search}%'))
        )
    items = query.order_by(Supplier.name).all()
    return render_template('suppliers/list.html', items=items, search=search)


@suppliers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        supplier = Supplier(
            name=request.form['name'],
            supplier_code=request.form['supplier_code'],
            country=request.form.get('country'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            status=request.form.get('status', 'active'),
            notes=request.form.get('notes'),
        )
        db.session.add(supplier)
        db.session.commit()
        log_action('supplier', supplier.id, 'created')
        flash('Supplier created.', 'success')
        return redirect(url_for('suppliers.detail', id=supplier.id))
    return render_template('suppliers/form.html', supplier=None, statuses=SUPPLIER_STATUSES)


@suppliers_bp.route('/<int:id>')
@login_required
def detail(id):
    supplier = Supplier.query.get_or_404(id)
    contacts = supplier.contacts.all()
    documents = Document.query.filter_by(supplier_id=supplier.id).all()
    components = PackagingComponent.query.filter_by(supplier_id=supplier.id).all()
    return render_template('suppliers/detail.html', supplier=supplier, contacts=contacts,
                           documents=documents, components=components)


@suppliers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    supplier = Supplier.query.get_or_404(id)
    if request.method == 'POST':
        supplier.name = request.form['name']
        supplier.supplier_code = request.form['supplier_code']
        supplier.country = request.form.get('country')
        supplier.email = request.form.get('email')
        supplier.phone = request.form.get('phone')
        supplier.status = request.form.get('status', 'active')
        supplier.notes = request.form.get('notes')
        db.session.commit()
        log_action('supplier', supplier.id, 'updated')
        flash('Supplier updated.', 'success')
        return redirect(url_for('suppliers.detail', id=supplier.id))
    return render_template('suppliers/form.html', supplier=supplier, statuses=SUPPLIER_STATUSES)


@suppliers_bp.route('/<int:id>/contacts/add', methods=['POST'])
@login_required
def add_contact(id):
    supplier = Supplier.query.get_or_404(id)
    contact = SupplierContact(
        supplier_id=supplier.id,
        name=request.form['name'],
        email=request.form.get('email'),
        role=request.form.get('role'),
        phone=request.form.get('phone'),
    )
    db.session.add(contact)
    db.session.commit()
    flash('Contact added.', 'success')
    return redirect(url_for('suppliers.detail', id=supplier.id))


@suppliers_bp.route('/contacts/<int:id>/delete', methods=['POST'])
@login_required
def delete_contact(id):
    contact = SupplierContact.query.get_or_404(id)
    supplier_id = contact.supplier_id
    db.session.delete(contact)
    db.session.commit()
    flash('Contact removed.', 'info')
    return redirect(url_for('suppliers.detail', id=supplier_id))
