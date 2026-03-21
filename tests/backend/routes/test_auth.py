import pytest
from backend.app.db import db
from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.user_account_access import UserAccountAccess

def test_register_success(client, test_app):
    """
    GIVEN a new user's details
    WHEN a POST request is made to /api/register
    THEN check that the user is created, gets a default account, and is logged in.
    """
    register_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    }
    response = client.post('/api/register', json=register_data)

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['username'] == 'newuser'
    assert json_data['email'] == 'new@example.com'

    with test_app.app_context():
        user = User.query.filter_by(email='new@example.com').first()
        assert user is not None
        
        access = UserAccountAccess.query.filter_by(user_id=user.id).first()
        assert access is not None
        
        account = Account.query.get(access.account_id)
        assert account is not None
        assert account.name == "Cash"

        me_response = client.get('/api/me')
        assert me_response.status_code == 200
        assert me_response.get_json()['id'] == user.id

def test_register_duplicate_email(client, test_app):
    """
    GIVEN an email that already exists
    WHEN a POST request is made to /api/register with that email
    THEN check that the response is 400.
    """
    with test_app.app_context():
        existing_user = User(username='existinguser', email='exists@example.com')
        existing_user.password = 'password'
        db.session.add(existing_user)
        db.session.commit()

    register_data = {
        "username": "anotheruser",
        "email": "exists@example.com",
        "password": "password123"
    }
    response = client.post('/api/register', json=register_data)
    assert response.status_code == 400
    assert "Email address already registered" in response.get_json()['ERROR']

def test_login_invalid_password(client, test_app):
    """
    GIVEN a user exists
    WHEN a POST request is made to /api/login with the wrong password
    THEN check that the response is 401.
    """
    # Use the user created by the 'auth' fixture setup
    with test_app.app_context():
        user = User(username='loginuser', email='login@example.com')
        user.password = 'correct_password'
        db.session.add(user)
        db.session.commit()

    login_data = {
        "email": "login@example.com",
        "password": "wrong_password"
    }
    response = client.post('/api/login', json=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.get_json()['ERROR']

def test_get_me_success(auth, test_app):
    """
    GIVEN a logged-in user (from the 'auth' fixture)
    WHEN a GET request is made to /api/me
    THEN check that the user's details are returned.
    """
    response = auth.client.get('/api/me')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id'] == auth.user.id
    assert json_data['email'] == auth.user.email
