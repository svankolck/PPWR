"""
Seed data for PPWR Compliance Workspace.
Run with: python -m seeds.seed_data
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.packaging import Packaging, PackagingComponent, Assessment
from app.models.supplier import Supplier, SupplierContact
from app.models.document import Document
from app.models.requirement import Requirement
from app.models.gap import Gap
from app.models.task import Task
from app.models.audit_log import AuditLog
from datetime import date, datetime


def seed():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # --- Users ---
        admin = User(username='admin', email='admin@ppwr.local', full_name='Admin User', role='admin')
        admin.set_password('admin')
        analyst = User(username='analyst', email='analyst@ppwr.local', full_name='Maria Analyst', role='user')
        analyst.set_password('analyst')
        db.session.add_all([admin, analyst])
        db.session.flush()

        # --- Suppliers ---
        suppliers = [
            Supplier(name='PackFilm GmbH', supplier_code='SUP-001', country='Germany', email='info@packfilm.de', phone='+49 30 1234567', status='active', notes='Primary film supplier for EU operations'),
            Supplier(name='NordicBoard AB', supplier_code='SUP-002', country='Sweden', email='supply@nordicboard.se', phone='+46 8 987654', status='active', notes='Certified FSC cardboard supplier'),
            Supplier(name='GlassPack Italia', supplier_code='SUP-003', country='Italy', email='export@glasspackit.com', phone='+39 02 555666', status='active'),
            Supplier(name='ResinCo Poland', supplier_code='SUP-004', country='Poland', email='sales@resinco.pl', phone='+48 22 111222', status='active', notes='Recycled PET resin supplier'),
            Supplier(name='MetalCap France', supplier_code='SUP-005', country='France', email='contact@metalcap.fr', phone='+33 1 444555', status='pending', notes='New supplier, pending qualification'),
        ]
        db.session.add_all(suppliers)
        db.session.flush()

        # Supplier contacts
        contacts = [
            SupplierContact(supplier_id=suppliers[0].id, name='Hans Mueller', email='h.mueller@packfilm.de', role='Sales Manager'),
            SupplierContact(supplier_id=suppliers[0].id, name='Anna Weber', email='a.weber@packfilm.de', role='Quality Manager'),
            SupplierContact(supplier_id=suppliers[1].id, name='Erik Johansson', email='erik.j@nordicboard.se', role='Account Manager'),
            SupplierContact(supplier_id=suppliers[2].id, name='Marco Rossi', email='m.rossi@glasspackit.com', role='Export Director'),
            SupplierContact(supplier_id=suppliers[3].id, name='Katarzyna Nowak', email='k.nowak@resinco.pl', role='Technical Sales'),
        ]
        db.session.add_all(contacts)

        # --- Packaging Items ---
        packaging_items = [
            Packaging(code='PKG-001', name='Premium Olive Oil Bottle 500ml', sku_or_product_family='Olive Oil Range', market='EU', packaging_type='sales', owner_name='Maria Analyst', status='in_review', notes='Primary SKU for premium olive oil line'),
            Packaging(code='PKG-002', name='Breakfast Cereal Box 750g', sku_or_product_family='Cereal Family', market='EU', packaging_type='sales', owner_name='Maria Analyst', status='draft'),
            Packaging(code='PKG-003', name='6-Pack Juice Multipack', sku_or_product_family='Juice Range', market='EU', packaging_type='grouped', owner_name='Admin User', status='missing_evidence'),
            Packaging(code='PKG-004', name='Euro Pallet Stretch Wrap', sku_or_product_family='Logistics', market='EU', packaging_type='transport', owner_name='Admin User', status='draft'),
            Packaging(code='PKG-005', name='E-commerce Shipping Box M', sku_or_product_family='E-commerce', market='EU', packaging_type='e-commerce', owner_name='Maria Analyst', status='at_risk'),
            Packaging(code='PKG-006', name='Yogurt Cup 150g', sku_or_product_family='Dairy Range', market='EU', packaging_type='sales', owner_name='Maria Analyst', status='draft'),
            Packaging(code='PKG-007', name='Detergent Refill Pouch 1L', sku_or_product_family='Home Care', market='EU', packaging_type='sales', owner_name='Admin User', status='approved'),
            Packaging(code='PKG-008', name='Wine Bottle Gift Set Tray', sku_or_product_family='Wine Range', market='EU', packaging_type='grouped', owner_name='Admin User', status='in_review'),
        ]
        db.session.add_all(packaging_items)
        db.session.flush()

        # --- Components ---
        components = [
            # PKG-001: Olive Oil Bottle
            PackagingComponent(packaging_id=packaging_items[0].id, name='Glass bottle 500ml', material='glass', weight_grams=350, recycled_content_pct=45, food_contact=True, supplier_id=suppliers[2].id),
            PackagingComponent(packaging_id=packaging_items[0].id, name='Metal cap', material='aluminium', weight_grams=8, recycled_content_pct=30, food_contact=True, supplier_id=suppliers[4].id),
            PackagingComponent(packaging_id=packaging_items[0].id, name='Paper label', material='paper', weight_grams=3, recycled_content_pct=80, food_contact=False, supplier_id=suppliers[1].id),

            # PKG-002: Cereal Box
            PackagingComponent(packaging_id=packaging_items[1].id, name='Cardboard outer box', material='cardboard', weight_grams=85, recycled_content_pct=90, food_contact=False, supplier_id=suppliers[1].id),
            PackagingComponent(packaging_id=packaging_items[1].id, name='LDPE inner bag', material='plastic', weight_grams=6, recycled_content_pct=0, food_contact=True, supplier_id=suppliers[0].id),

            # PKG-003: Juice Multipack
            PackagingComponent(packaging_id=packaging_items[2].id, name='Shrink wrap film', material='plastic', weight_grams=12, recycled_content_pct=None, food_contact=False, supplier_id=suppliers[0].id, notes='Missing recycled content data'),
            PackagingComponent(packaging_id=packaging_items[2].id, name='Cardboard tray', material='cardboard', weight_grams=45, recycled_content_pct=70, food_contact=False, supplier_id=suppliers[1].id),

            # PKG-004: Stretch Wrap
            PackagingComponent(packaging_id=packaging_items[3].id, name='LLDPE stretch film', material='plastic', weight_grams=280, recycled_content_pct=15, food_contact=False, supplier_id=suppliers[0].id),

            # PKG-005: E-commerce Box
            PackagingComponent(packaging_id=packaging_items[4].id, name='Corrugated box', material='cardboard', weight_grams=320, recycled_content_pct=85, food_contact=False, supplier_id=suppliers[1].id),
            PackagingComponent(packaging_id=packaging_items[4].id, name='Void fill paper', material='paper', weight_grams=40, recycled_content_pct=100, food_contact=False, supplier_id=None, notes='No supplier assigned yet'),
            PackagingComponent(packaging_id=packaging_items[4].id, name='Adhesive tape', material='plastic', weight_grams=5, recycled_content_pct=None, food_contact=False, supplier_id=None),

            # PKG-006: Yogurt Cup
            PackagingComponent(packaging_id=packaging_items[5].id, name='PP cup', material='plastic', weight_grams=7, recycled_content_pct=0, food_contact=True, supplier_id=suppliers[3].id),
            PackagingComponent(packaging_id=packaging_items[5].id, name='Aluminium foil lid', material='aluminium', weight_grams=1.5, recycled_content_pct=0, food_contact=True, supplier_id=suppliers[4].id),
            PackagingComponent(packaging_id=packaging_items[5].id, name='Cardboard sleeve', material='cardboard', weight_grams=5, recycled_content_pct=80, food_contact=False, supplier_id=suppliers[1].id),

            # PKG-007: Detergent Pouch
            PackagingComponent(packaging_id=packaging_items[6].id, name='Multi-layer pouch', material='plastic', weight_grams=18, recycled_content_pct=30, food_contact=False, supplier_id=suppliers[0].id),
            PackagingComponent(packaging_id=packaging_items[6].id, name='Spout cap', material='plastic', weight_grams=4, recycled_content_pct=20, food_contact=False, supplier_id=suppliers[3].id),

            # PKG-008: Wine Gift Tray
            PackagingComponent(packaging_id=packaging_items[7].id, name='Rigid cardboard tray', material='cardboard', weight_grams=180, recycled_content_pct=60, food_contact=False, supplier_id=suppliers[1].id),
            PackagingComponent(packaging_id=packaging_items[7].id, name='PET window film', material='plastic', weight_grams=8, recycled_content_pct=50, food_contact=False, supplier_id=suppliers[0].id),
        ]
        db.session.add_all(components)
        db.session.flush()

        # --- Requirements ---
        requirements = [
            Requirement(
                code='PPWR-RC-01', name='Recycled Content Targets for Plastic Packaging',
                category='recycled_content',
                description='Plastic packaging must meet minimum recycled content thresholds. Contact-sensitive plastic: 10% by 2030, 50% by 2040. All other plastic: 35% by 2030, 65% by 2040.',
                status='active', severity_default='high',
                applies_to_packaging_types=None,
                applies_to_materials=json.dumps(['plastic']),
                food_contact_relevant=False,
                required_fields_json=json.dumps(['recycled_content_pct']),
                required_document_types_json=json.dumps(['recycled_content_statement']),
            ),
            Requirement(
                code='PPWR-RCY-01', name='Design for Recycling',
                category='recyclability',
                description='All packaging placed on the EU market must be designed for recycling by 2030 and recycled at scale by 2035.',
                status='active', severity_default='high',
                required_document_types_json=json.dumps(['specification_sheet']),
            ),
            Requirement(
                code='PPWR-MIN-01', name='Packaging Minimisation',
                category='minimisation',
                description='Packaging weight and volume must be minimised to the minimum necessary for safety, hygiene, and consumer acceptance.',
                status='active', severity_default='medium',
                required_fields_json=json.dumps(['weight_grams']),
                required_document_types_json=json.dumps(['specification_sheet']),
            ),
            Requirement(
                code='PPWR-RU-01', name='Reuse Targets for Transport Packaging',
                category='reuse',
                description='Transport packaging must meet reuse targets: 40% by 2030, 70% by 2040.',
                status='active', severity_default='high',
                applies_to_packaging_types=json.dumps(['transport']),
                required_document_types_json=json.dumps(['certificate']),
            ),
            Requirement(
                code='PPWR-FC-01', name='Food Contact Compliance Declaration',
                category='food_contact',
                description='All food-contact packaging components must have valid food contact declarations per Regulation (EC) 1935/2004.',
                status='active', severity_default='critical',
                food_contact_relevant=True,
                required_document_types_json=json.dumps(['food_contact_declaration']),
            ),
            Requirement(
                code='PPWR-LBL-01', name='Packaging Labelling Requirements',
                category='labelling',
                description='Packaging must carry harmonised labelling for material identification and consumer sorting instructions.',
                status='active', severity_default='medium',
                required_document_types_json=json.dumps(['artwork_label_file']),
            ),
            Requirement(
                code='PPWR-SUB-01', name='Substance Restrictions (SVHC)',
                category='substance_restrictions',
                description='Packaging must not contain substances of very high concern above defined thresholds. PFAS restrictions apply broadly.',
                status='active', severity_default='critical',
                required_document_types_json=json.dumps(['substance_statement']),
            ),
            Requirement(
                code='PPWR-ECO-01', name='E-commerce Empty Space Ratio',
                category='minimisation',
                description='E-commerce packaging must limit empty space to max 50% of the total volume.',
                status='future', severity_default='medium',
                applies_to_packaging_types=json.dumps(['e-commerce']),
                required_fields_json=json.dumps(['weight_grams']),
            ),
            Requirement(
                code='PPWR-DOC-01', name='Supplier Material Declaration',
                category='documentation',
                description='Each supplier must provide a material declaration for all supplied packaging components.',
                status='active', severity_default='medium',
                required_document_types_json=json.dumps(['material_declaration', 'supplier_declaration']),
            ),
        ]
        db.session.add_all(requirements)
        db.session.flush()

        # --- Documents ---
        documents = [
            Document(title='PackFilm LDPE Specification Sheet', document_type='specification_sheet', supplier_id=suppliers[0].id, packaging_id=packaging_items[1].id, status='approved', version='2.1', valid_from=date(2024, 1, 1), valid_to=date(2026, 12, 31)),
            Document(title='NordicBoard FSC Certificate', document_type='certificate', supplier_id=suppliers[1].id, status='approved', version='1.0', valid_from=date(2024, 3, 1), valid_to=date(2025, 3, 1)),
            Document(title='GlassPack Food Contact Declaration - Glass', document_type='food_contact_declaration', supplier_id=suppliers[2].id, packaging_id=packaging_items[0].id, status='approved', valid_from=date(2024, 6, 1), valid_to=date(2026, 6, 1)),
            Document(title='ResinCo rPET Recycled Content Statement', document_type='recycled_content_statement', supplier_id=suppliers[3].id, status='received', version='1.2'),
            Document(title='Olive Oil Bottle Label Artwork v3', document_type='artwork_label_file', packaging_id=packaging_items[0].id, status='approved', version='3.0'),
            Document(title='PackFilm Substance Statement 2024', document_type='substance_statement', supplier_id=suppliers[0].id, status='approved', valid_from=date(2024, 1, 1), valid_to=date(2025, 12, 31)),
            Document(title='Detergent Pouch Material Declaration', document_type='material_declaration', packaging_id=packaging_items[6].id, supplier_id=suppliers[0].id, status='approved', version='1.0'),
            Document(title='Cereal Box Specification', document_type='specification_sheet', packaging_id=packaging_items[1].id, status='draft', version='0.9'),
            Document(title='NordicBoard Supplier Declaration 2024', document_type='supplier_declaration', supplier_id=suppliers[1].id, status='approved', valid_from=date(2024, 1, 1), valid_to=date(2025, 12, 31)),
            Document(title='Expired Test Report - Stretch Film', document_type='test_report', supplier_id=suppliers[0].id, packaging_id=packaging_items[3].id, status='expired', valid_from=date(2022, 1, 1), valid_to=date(2023, 12, 31)),
        ]
        db.session.add_all(documents)
        db.session.flush()

        # --- Gaps ---
        gaps = [
            Gap(packaging_id=packaging_items[2].id, title='Missing recycled content % for Shrink wrap film', description='Component "Shrink wrap film" has no recycled content percentage recorded.', severity='medium', owner='Maria Analyst', status='open'),
            Gap(packaging_id=packaging_items[4].id, title='No supplier assigned for Void fill paper', description='Component "Void fill paper" is not linked to any supplier.', severity='high', owner='Admin User', status='open'),
            Gap(packaging_id=packaging_items[4].id, title='No supplier assigned for Adhesive tape', description='Component "Adhesive tape" has no supplier and no recycled content data.', severity='high', owner='Admin User', status='open'),
            Gap(packaging_id=packaging_items[4].id, requirement_id=requirements[7].id, title='Missing documentation for e-commerce empty space compliance', description='PKG-005 is e-commerce packaging but has no documentation regarding empty space ratio.', severity='medium', owner='Maria Analyst', status='open'),
            Gap(packaging_id=packaging_items[0].id, requirement_id=requirements[4].id, title='Missing food contact declaration for metal cap', description='Metal cap supplier (MetalCap France) has not provided food contact declaration.', severity='critical', owner='Maria Analyst', status='in_progress'),
            Gap(packaging_id=packaging_items[5].id, title='Yogurt cup PP has 0% recycled content', description='PP cup currently uses 0% recycled content. PPWR requires minimum thresholds.', severity='high', owner='Admin User', status='open'),
        ]
        db.session.add_all(gaps)
        db.session.flush()

        # --- Tasks ---
        tasks = [
            Task(gap_id=gaps[0].id, packaging_id=packaging_items[2].id, title='Request recycled content data from PackFilm', description='Contact PackFilm GmbH to provide recycled content percentage for shrink wrap film.', assigned_to='Maria Analyst', due_date=date(2025, 6, 30), status='todo', priority='medium'),
            Task(gap_id=gaps[1].id, packaging_id=packaging_items[4].id, title='Source supplier for void fill paper', description='Identify and qualify a supplier for void fill paper used in e-commerce box.', assigned_to='Admin User', due_date=date(2025, 5, 15), status='in_progress', priority='high'),
            Task(gap_id=gaps[4].id, packaging_id=packaging_items[0].id, supplier_id=suppliers[4].id, title='Request food contact declaration from MetalCap', description='MetalCap France must provide food contact declaration for aluminium caps.', assigned_to='Maria Analyst', due_date=date(2025, 4, 30), status='in_progress', priority='urgent'),
            Task(packaging_id=packaging_items[1].id, title='Complete cereal box specification review', assigned_to='Admin User', due_date=date(2025, 7, 1), status='todo', priority='low'),
            Task(packaging_id=packaging_items[5].id, gap_id=gaps[5].id, title='Evaluate rPP alternatives for yogurt cup', description='Research recycled PP suppliers to meet future PPWR targets.', assigned_to='Maria Analyst', due_date=date(2025, 9, 1), status='todo', priority='high'),
        ]
        db.session.add_all(tasks)

        # --- Audit Log ---
        audit_entries = [
            AuditLog(entity_type='packaging', entity_id=packaging_items[0].id, action='created', user_name='admin', details_json=json.dumps({'code': 'PKG-001'})),
            AuditLog(entity_type='packaging', entity_id=packaging_items[0].id, action='assessed', user_name='analyst'),
            AuditLog(entity_type='packaging', entity_id=packaging_items[6].id, action='created', user_name='admin', details_json=json.dumps({'code': 'PKG-007'})),
            AuditLog(entity_type='packaging', entity_id=packaging_items[6].id, action='approved', user_name='admin'),
        ]
        db.session.add_all(audit_entries)

        db.session.commit()
        print('Seed data loaded successfully!')
        print(f'  Users: 2 (admin/admin, analyst/analyst)')
        print(f'  Suppliers: {len(suppliers)}')
        print(f'  Packaging items: {len(packaging_items)}')
        print(f'  Components: {len(components)}')
        print(f'  Requirements: {len(requirements)}')
        print(f'  Documents: {len(documents)}')
        print(f'  Gaps: {len(gaps)}')
        print(f'  Tasks: {len(tasks)}')


if __name__ == '__main__':
    seed()
