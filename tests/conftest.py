import pytest
from app import create_app, db as _db
from app.models.user import User


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.create_all()
        # Create test user
        user = User(username='testuser', email='test@test.com', full_name='Test User')
        user.set_password('testpass')
        _db.session.add(user)
        _db.session.commit()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    with app.test_client() as client:
        # Login
        client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
        yield client
