"""
Gap detection service.
Scans a packaging item and creates gaps for missing data/documents.
"""
from app import db
from app.models.packaging import Packaging, Assessment
from app.models.requirement import Requirement
from app.models.document import Document
from app.models.gap import Gap


def generate_gaps(packaging: Packaging):
    """Generate gaps for a packaging item based on assessments and missing data."""
    gaps_created = []

    # Basic data gaps for components
    for comp in packaging.components:
        if comp.weight_grams is None:
            gaps_created.append(_create_gap(
                packaging, None, None,
                f'Missing weight for component "{comp.name}"',
                f'Component "{comp.name}" has no weight recorded.',
                'medium',
            ))
        if comp.recycled_content_pct is None:
            gaps_created.append(_create_gap(
                packaging, None, None,
                f'Missing recycled content % for component "{comp.name}"',
                f'Component "{comp.name}" has no recycled content percentage.',
                'medium',
            ))
        if comp.supplier_id is None:
            gaps_created.append(_create_gap(
                packaging, None, None,
                f'No supplier assigned for component "{comp.name}"',
                f'Component "{comp.name}" is not linked to any supplier.',
                'high',
            ))

    # Requirement-based gaps
    assessments = Assessment.query.filter_by(packaging_id=packaging.id).all()
    for assessment in assessments:
        if assessment.evidence_status in ('missing', 'partial'):
            req = Requirement.query.get(assessment.requirement_id)
            if not req:
                continue

            # Check which specific documents are missing
            required_doc_types = req.get_required_document_types()
            existing_doc_types = set()
            for doc in Document.query.filter_by(packaging_id=packaging.id).all():
                existing_doc_types.add(doc.document_type)
            for comp in packaging.components:
                for doc in Document.query.filter_by(component_id=comp.id).all():
                    existing_doc_types.add(doc.document_type)

            for rdt in required_doc_types:
                if rdt not in existing_doc_types:
                    doc_label = rdt.replace('_', ' ').title()
                    gaps_created.append(_create_gap(
                        packaging, req.id, None,
                        f'Missing document: {doc_label}',
                        f'Requirement "{req.name}" requires a {doc_label} but none is attached.',
                        req.severity_default,
                    ))

    db.session.commit()
    return gaps_created


def _create_gap(packaging, requirement_id, supplier_id, title, description, severity):
    # Avoid duplicates
    existing = Gap.query.filter_by(
        packaging_id=packaging.id,
        title=title,
        status='open',
    ).first()
    if existing:
        return existing

    gap = Gap(
        packaging_id=packaging.id,
        requirement_id=requirement_id,
        supplier_id=supplier_id,
        title=title,
        description=description,
        severity=severity,
        status='open',
    )
    db.session.add(gap)
    return gap
