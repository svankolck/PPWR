"""Calculate packaging status based on assessments and gaps."""
from app.models.packaging import Packaging, Assessment
from app.models.gap import Gap


def calculate_status(packaging: Packaging) -> str:
    assessments = Assessment.query.filter_by(packaging_id=packaging.id).all()
    open_gaps = Gap.query.filter_by(packaging_id=packaging.id, status='open').count()
    critical_gaps = Gap.query.filter_by(packaging_id=packaging.id, status='open', severity='critical').count()

    if not assessments:
        return 'draft'

    if critical_gaps > 0:
        return 'at_risk'

    all_compliant = all(a.overall_status == 'compliant' for a in assessments)
    if all_compliant and open_gaps == 0:
        return 'approved'

    any_missing = any(a.evidence_status == 'missing' for a in assessments)
    if any_missing:
        return 'missing_evidence'

    return 'in_review'
