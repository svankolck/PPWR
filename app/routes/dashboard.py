from flask import Blueprint, render_template
from flask_login import login_required
from app.models.packaging import Packaging
from app.models.gap import Gap
from app.models.task import Task
from app.models.document import Document
from app import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    total_packaging = Packaging.query.count()
    status_counts = dict(
        db.session.query(Packaging.status, db.func.count(Packaging.id))
        .group_by(Packaging.status).all()
    )
    type_counts = dict(
        db.session.query(Packaging.packaging_type, db.func.count(Packaging.id))
        .group_by(Packaging.packaging_type).all()
    )
    open_gaps = Gap.query.filter(Gap.status.in_(['open', 'in_progress'])).count()
    critical_gaps = Gap.query.filter_by(status='open', severity='critical').count()
    open_tasks = Task.query.filter(Task.status.in_(['todo', 'in_progress'])).count()
    expired_docs = Document.query.filter_by(status='expired').count()

    at_risk = Packaging.query.filter_by(status='at_risk').count()
    missing_evidence = Packaging.query.filter_by(status='missing_evidence').count()

    recent_gaps = Gap.query.order_by(Gap.created_at.desc()).limit(5).all()
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()

    return render_template('dashboard/index.html',
                           total_packaging=total_packaging,
                           status_counts=status_counts,
                           type_counts=type_counts,
                           open_gaps=open_gaps,
                           critical_gaps=critical_gaps,
                           open_tasks=open_tasks,
                           expired_docs=expired_docs,
                           at_risk=at_risk,
                           missing_evidence=missing_evidence,
                           recent_gaps=recent_gaps,
                           recent_tasks=recent_tasks)
