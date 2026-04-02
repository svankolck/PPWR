def test_document_list(client):
    resp = client.get('/documents/')
    assert resp.status_code == 200
    assert b'Documents' in resp.data


def test_document_upload_page(client):
    resp = client.get('/documents/upload')
    assert resp.status_code == 200
    assert b'Upload Document' in resp.data


def test_document_upload(client, db):
    resp = client.post('/documents/upload', data={
        'title': 'Test Document',
        'document_type': 'specification_sheet',
        'status': 'draft',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Test Document' in resp.data
