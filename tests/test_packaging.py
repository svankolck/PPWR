def test_packaging_list_requires_login(app):
    with app.test_client() as c:
        resp = c.get('/packaging/')
        assert resp.status_code == 302  # redirect to login


def test_packaging_list(client):
    resp = client.get('/packaging/')
    assert resp.status_code == 200
    assert b'Packaging Register' in resp.data


def test_create_packaging(client, db):
    resp = client.post('/packaging/create', data={
        'code': 'TEST-001',
        'name': 'Test Packaging',
        'packaging_type': 'sales',
        'market': 'EU',
        'owner_name': 'Test',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'TEST-001' in resp.data


def test_edit_packaging(client, db):
    from app.models.packaging import Packaging
    pkg = Packaging(code='EDIT-001', name='Edit Me', packaging_type='sales')
    db.session.add(pkg)
    db.session.commit()

    resp = client.post(f'/packaging/{pkg.id}/edit', data={
        'code': 'EDIT-001',
        'name': 'Edited Name',
        'packaging_type': 'transport',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Edited Name' in resp.data


def test_packaging_detail(client, db):
    from app.models.packaging import Packaging
    pkg = Packaging(code='DET-001', name='Detail Test', packaging_type='sales')
    db.session.add(pkg)
    db.session.commit()

    resp = client.get(f'/packaging/{pkg.id}')
    assert resp.status_code == 200
    assert b'DET-001' in resp.data


def test_archive_packaging(client, db):
    from app.models.packaging import Packaging
    pkg = Packaging(code='ARC-001', name='Archive Me', packaging_type='sales')
    db.session.add(pkg)
    db.session.commit()

    resp = client.post(f'/packaging/{pkg.id}/archive', follow_redirects=True)
    assert resp.status_code == 200
    updated = Packaging.query.get(pkg.id)
    assert updated.status == 'archived'
