from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models.gap import Gap, GAP_SEVERITIES, GAP_STATUSES
from app.models.packaging import Packaging
from app.models.requirement import Requirement
from app.models.supplier import Supplier
from app.models.task import Task
from datetime import datetime

gaps_bp = Blueprint('gaps', __name__, url_prefix='/gaps')


@gaps_bp.route('/')
@login_required
def list_gaps():
    status_filter = request.args.get('status')
    severity_filter = request.args.get('severity')
    query = Gap.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if severity_filter:
        query = query.filter_by(severity=severity_filter)
    items = query.order_by(Gap.created_at.desc()).all()
    return render_template('gaps/list.html', items=items, severities=GAP_SEVERITIES,
                           statuses=GAP_STATUSES, current_status=status_filter,
                           current_severity=severity_filter)


@gaps_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    packaging_items = Packaging.query.order_by(Packaging.name).all()
    requirements = Requirement.query.order_by(Requirement.code).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()

    if request.method == 'POST':
        due_date = request.form.get('due_date')
        gap = Gap(
            packaging_id=_parse_int(request.form.get('packaging_id')),
            requirement_id=_parse_int(request.form.get('requirement_id')),
            supplier_id=_parse_int(request.form.get('supplier_id')),
            title=request.form['title'],
            description=request.form.get('description'),
            severity=request.form.get('severity', 'medium'),
            owner=request.form.get('owner'),
            due_date=datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None,
            status=request.form.get('status', 'open'),
        )
        db.session.add(gap)
        db.session.commit()
        flash('Gap created.', 'success')
        return redirect(url_for('gaps.list_gaps'))

    return render_template('gaps/form.html', gap=None, packaging_items=packaging_items,
                           requirements=requirements, suppliers=suppliers,
                           severities=GAP_SEVERITIES, statuses=GAP_STATUSES)


@gaps_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    gap = Gap.query.get_or_404(id)
    packaging_items = Packaging.query.order_by(Packaging.name).all()
    requirements = Requirement.query.order_by(Requirement.code).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()

    if request.method == 'POST':
        due_date = request.form.get('due_date')
        gap.packaging_id = _parse_int(request.form.get('packaging_id'))
        gap.requirement_id = _parse_int(request.form.get('requirement_id'))
        gap.supplier_id = _parse_int(request.form.get('supplier_id'))
        gap.title = request.form['title']
        gap.description = request.form.get('description')
        gap.severity = request.form.get('severity', 'medium')
        gap.owner = request.form.get('owner')
        gap.due_date = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None
        gap.status = request.form.get('status', 'open')
        db.session.commit()
        flash('Gap updated.', 'success')
        return redirect(url_for('gaps.list_gaps'))

    return render_template('gaps/form.html', gap=gap, packaging_items=packaging_items,
                           requirements=requirements, suppliers=suppliers,
                           severities=GAP_SEVERITIES, statuses=GAP_STATUSES)


@gaps_bp.route('/<int:id>/create-task', methods=['POST'])
@login_required
def create_task(id):
    gap = Gap.query.get_or_404(id)
    task = Task(
        gap_id=gap.id,
        packaging_id=gap.packaging_id,
        supplier_id=gap.supplier_id,
        title=f'Resolve: {gap.title}',
        description=gap.description,
        priority='high' if gap.severity in ('high', 'critical') else 'medium',
        status='todo',
    )
    db.session.add(task)
    db.session.commit()
    flash('Task created from gap.', 'success')
    return redirect(url_for('tasks.list_tasks'))


def _parse_int(val):
    if val and val.strip():
        try:
            return int(val)
        except ValueError:
            return None
    return None
