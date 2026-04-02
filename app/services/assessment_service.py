"""
Applicability and assessment logic.
Determines which PPWR requirements apply to a given packaging item
based on its type, materials, and food-contact status.
"""
import json
from app import db
from app.models.packaging import Packaging, Assessment
from app.models.requirement import Requirement
from app.models.document import Document


def get_applicable_requirements(packaging: Packaging) -> list[Requirement]:
    """Return requirements that apply to this packaging item."""
    all_reqs = Requirement.query.filter(Requirement.status.in_(['active', 'future'])).all()
    applicable = []
    pkg_materials = packaging.get_materials()
    pkg_has_food_contact = packaging.has_food_contact()

    for req in all_reqs:
        if _requirement_applies(req, packaging.packaging_type, pkg_materials, pkg_has_food_contact):
            applicable.append(req)
    return applicable


def _requirement_applies(req: Requirement, packaging_type: str, materials: list[str], has_food_contact: bool) -> bool:
    # Check packaging type filter
    req_types = req.get_packaging_types()
    if req_types and packaging_type not in req_types:
        return False

    # Check material filter
    req_materials = req.get_materials()
    if req_materials:
        material_match = any(
            mat.lower() in [m.lower() for m in req_materials]
            for mat in materials
        )
        if not material_match:
            return False

    # Check food contact
    if req.food_contact_relevant and not has_food_contact:
        return False

    return True


def run_assessment(packaging: Packaging):
    """Run full assessment for a packaging item: determine applicability, check evidence, create assessments."""
    applicable_reqs = get_applicable_requirements(packaging)

    # Remove old assessments for this packaging
    Assessment.query.filter_by(packaging_id=packaging.id).delete()

    for req in applicable_reqs:
        evidence_status = _check_evidence(packaging, req)
        overall = 'compliant' if evidence_status == 'complete' else 'open'

        assessment = Assessment(
            packaging_id=packaging.id,
            requirement_id=req.id,
            applicability_status='applicable',
            evidence_status=evidence_status,
            overall_status=overall,
            rationale=f'Auto-assessed based on packaging type, materials, and documents.',
        )
        db.session.add(assessment)

    db.session.commit()


def _check_evidence(packaging: Packaging, req: Requirement) -> str:
    """Check if required documents and fields exist for a requirement."""
    required_doc_types = req.get_required_document_types()
    required_fields = req.get_required_fields()

    if not required_doc_types and not required_fields:
        return 'complete'

    # Check required document types
    docs_ok = True
    if required_doc_types:
        existing_doc_types = set()
        for doc in Document.query.filter_by(packaging_id=packaging.id).all():
            existing_doc_types.add(doc.document_type)
        # Also check component-level docs
        for comp in packaging.components:
            for doc in Document.query.filter_by(component_id=comp.id).all():
                existing_doc_types.add(doc.document_type)

        for rdt in required_doc_types:
            if rdt not in existing_doc_types:
                docs_ok = False
                break

    # Check required fields on components
    fields_ok = True
    if required_fields:
        for comp in packaging.components:
            for field in required_fields:
                val = getattr(comp, field, None)
                if val is None or val == '':
                    fields_ok = False
                    break

    if docs_ok and fields_ok:
        return 'complete'
    elif docs_ok or fields_ok:
        return 'partial'
    return 'missing'
