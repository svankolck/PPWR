def test_dashboard(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Dashboard' in resp.data


def test_dashboard_requires_login(app):
    with app.test_client() as c:
        resp = c.get('/')
        assert resp.status_code == 302
