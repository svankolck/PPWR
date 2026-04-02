def test_gap_list(client):
    resp = client.get('/gaps/')
    assert resp.status_code == 200
    assert b'Gaps' in resp.data


def test_task_list(client):
    resp = client.get('/tasks/')
    assert resp.status_code == 200
    assert b'Tasks' in resp.data


def test_create_gap(client, db):
    resp = client.post('/gaps/create', data={
        'title': 'Test Gap',
        'severity': 'high',
        'status': 'open',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Test Gap' in resp.data


def test_create_task(client, db):
    resp = client.post('/tasks/create', data={
        'title': 'Test Task',
        'priority': 'medium',
        'status': 'todo',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Test Task' in resp.data
