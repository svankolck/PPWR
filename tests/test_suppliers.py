def test_supplier_list(client):
    resp = client.get('/suppliers/')
    assert resp.status_code == 200
    assert b'Suppliers' in resp.data


def test_create_supplier(client, db):
    resp = client.post('/suppliers/create', data={
        'name': 'Test Supplier',
        'supplier_code': 'TS-001',
        'country': 'Germany',
        'email': 'test@supplier.com',
        'status': 'active',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'TS-001' in resp.data


def test_supplier_detail(client, db):
    from app.models.supplier import Supplier
    s = Supplier(name='Detail Supplier', supplier_code='DS-001', country='NL')
    db.session.add(s)
    db.session.commit()

    resp = client.get(f'/suppliers/{s.id}')
    assert resp.status_code == 200
    assert b'Detail Supplier' in resp.data


def test_add_contact(client, db):
    from app.models.supplier import Supplier
    s = Supplier(name='Contact Test', supplier_code='CT-001')
    db.session.add(s)
    db.session.commit()

    resp = client.post(f'/suppliers/{s.id}/contacts/add', data={
        'name': 'John Doe',
        'email': 'john@test.com',
        'role': 'Manager',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'John Doe' in resp.data
