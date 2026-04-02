import json
from app.models.packaging import Packaging, PackagingComponent, Assessment
from app.models.requirement import Requirement
from app.services.assessment_service import get_applicable_requirements, run_assessment
from app.services.gap_service import generate_gaps


def test_requirement_applicability_by_material(app, db):
    req = Requirement(
        code='TEST-RC', name='Plastic recycled content', category='recycled_content',
        status='active', applies_to_materials=json.dumps(['plastic']),
        required_fields_json=json.dumps(['recycled_content_pct']),
    )
    db.session.add(req)

    pkg = Packaging(code='T-001', name='Test Pkg', packaging_type='sales')
    db.session.add(pkg)
    db.session.flush()

    comp = PackagingComponent(packaging_id=pkg.id, name='Film', material='plastic', weight_grams=10)
    db.session.add(comp)
    db.session.commit()

    applicable = get_applicable_requirements(pkg)
    assert any(r.code == 'TEST-RC' for r in applicable)


def test_requirement_not_applicable_wrong_material(app, db):
    req = Requirement(
        code='TEST-RC2', name='Plastic only', category='recycled_content',
        status='active', applies_to_materials=json.dumps(['plastic']),
    )
    db.session.add(req)

    pkg = Packaging(code='T-002', name='Glass Pkg', packaging_type='sales')
    db.session.add(pkg)
    db.session.flush()

    comp = PackagingComponent(packaging_id=pkg.id, name='Bottle', material='glass', weight_grams=300)
    db.session.add(comp)
    db.session.commit()

    applicable = get_applicable_requirements(pkg)
    assert not any(r.code == 'TEST-RC2' for r in applicable)


def test_food_contact_requirement(app, db):
    req = Requirement(
        code='TEST-FC', name='Food contact', category='food_contact',
        status='active', food_contact_relevant=True,
    )
    db.session.add(req)

    pkg = Packaging(code='T-003', name='Food Pkg', packaging_type='sales')
    db.session.add(pkg)
    db.session.flush()

    comp = PackagingComponent(packaging_id=pkg.id, name='Cup', material='plastic', food_contact=True)
    db.session.add(comp)
    db.session.commit()

    applicable = get_applicable_requirements(pkg)
    assert any(r.code == 'TEST-FC' for r in applicable)


def test_run_assessment(app, db):
    req = Requirement(
        code='TEST-A', name='Test Req', category='documentation',
        status='active',
    )
    db.session.add(req)

    pkg = Packaging(code='T-004', name='Assessment Pkg', packaging_type='sales')
    db.session.add(pkg)
    db.session.commit()

    run_assessment(pkg)
    assessments = Assessment.query.filter_by(packaging_id=pkg.id).all()
    assert len(assessments) >= 1


def test_gap_generation(app, db):
    pkg = Packaging(code='T-005', name='Gap Pkg', packaging_type='sales')
    db.session.add(pkg)
    db.session.flush()

    comp = PackagingComponent(packaging_id=pkg.id, name='Test Comp', material='plastic')
    db.session.add(comp)
    db.session.commit()

    gaps = generate_gaps(pkg)
    # Should detect missing weight, recycled content, and supplier
    titles = [g.title for g in gaps]
    assert any('weight' in t.lower() for t in titles)
    assert any('recycled' in t.lower() for t in titles)
    assert any('supplier' in t.lower() for t in titles)
