import json
from flask_login import current_user
from app import db
from app.models.audit_log import AuditLog


def log_action(entity_type: str, entity_id: int, action: str, details: dict = None):
    user_name = current_user.username if current_user and current_user.is_authenticated else 'system'
    entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_name=user_name,
        details_json=json.dumps(details) if details else None,
    )
    db.session.add(entry)
    db.session.commit()
