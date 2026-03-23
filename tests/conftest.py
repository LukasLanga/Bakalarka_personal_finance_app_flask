import sys
import os
import pytest
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.app.db import db
from backend.app.models.user import User

@pytest.fixture
def test_app():
    """
    Create and configure a new app instance for each test function.
    This ensures a clean database for every test.
    """
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(test_app):
    """A test client for the app."""
    return test_app.test_client()

@pytest.fixture
def auth(client, test_app):
    """
    Provides an authenticated client and the user object.
    Creates a new user for each test function.
    """
    with test_app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.password = 'password'
        db.session.add(user)
        db.session.commit()

        client.post('/api/login', json={'email': 'test@example.com', 'password': 'password'})

        yield SimpleNamespace(client=client, user=user)

