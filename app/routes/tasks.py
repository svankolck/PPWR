from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app import db
from app.models.task import Task, TASK_STATUSES, TASK_PRIORITIES
from app.models.packaging import Packaging
from app.models.supplier import Supplier
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_bp.route('/')
@login_required
def list_tasks():
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    query = Task.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    items = query.order_by(Task.created_at.desc()).all()
    return render_template('tasks/list.html', items=items, statuses=TASK_STATUSES,
                           priorities=TASK_PRIORITIES, current_status=status_filter,
                           current_priority=priority_filter)


@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    packaging_items = Packaging.query.order_by(Packaging.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()

    if request.method == 'POST':
        due_date = request.form.get('due_date')
        task = Task(
            packaging_id=_parse_int(request.form.get('packaging_id')),
            supplier_id=_parse_int(request.form.get('supplier_id')),
            title=request.form['title'],
            description=request.form.get('description'),
            assigned_to=request.form.get('assigned_to'),
            due_date=datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None,
            status=request.form.get('status', 'todo'),
            priority=request.form.get('priority', 'medium'),
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created.', 'success')
        return redirect(url_for('tasks.list_tasks'))

    return render_template('tasks/form.html', task=None, packaging_items=packaging_items,
                           suppliers=suppliers, statuses=TASK_STATUSES, priorities=TASK_PRIORITIES)


@tasks_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    task = Task.query.get_or_404(id)
    packaging_items = Packaging.query.order_by(Packaging.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()

    if request.method == 'POST':
        due_date = request.form.get('due_date')
        task.packaging_id = _parse_int(request.form.get('packaging_id'))
        task.supplier_id = _parse_int(request.form.get('supplier_id'))
        task.title = request.form['title']
        task.description = request.form.get('description')
        task.assigned_to = request.form.get('assigned_to')
        task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None
        task.status = request.form.get('status', 'todo')
        task.priority = request.form.get('priority', 'medium')
        db.session.commit()
        flash('Task updated.', 'success')
        return redirect(url_for('tasks.list_tasks'))

    return render_template('tasks/form.html', task=task, packaging_items=packaging_items,
                           suppliers=suppliers, statuses=TASK_STATUSES, priorities=TASK_PRIORITIES)


def _parse_int(val):
    if val and val.strip():
        try:
            return int(val)
        except ValueError:
            return None
    return None
