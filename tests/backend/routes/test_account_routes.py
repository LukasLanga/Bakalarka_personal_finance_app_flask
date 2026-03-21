import pytest
from backend.app.db import db
from backend.app.models.account import Account
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.user_account_access import UserAccountAccess
from backend.app.models.invitation import AccountRole
from datetime import date

def test_create_account_success(auth, test_app):
    """
    GIVEN a logged-in user
    WHEN a POST request is made to /api/createAccount
    THEN a new account is created and the user is given owner access.
    """
    account_data = {
        "name": "My New Bank",
        "bank_name": "Global Bank Inc.",
        "balance": 500.75,
        "currency": "USD"
    }
    response = auth.client.post('/api/createAccount', json=account_data)
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['name'] == "My New Bank"
    assert json_data['currency'] == "USD"

    with test_app.app_context():
        account = Account.query.get(json_data['id'])
        assert account is not None
        
        access = UserAccountAccess.query.filter_by(user_id=auth.user.id, account_id=account.id).first()
        assert access is not None
        assert access.role == AccountRole.OWNER.value

def test_get_accounts_list(auth, test_app):
    """
    GIVEN a user with access to multiple accounts
    WHEN a GET request is made to /api/accounts
    THEN a list of those accounts is returned.
    """
    with test_app.app_context():
        acc1 = Account(name="Personal Savings", balance=1000)
        acc2 = Account(name="Work Expenses", balance=200)
        db.session.add_all([acc1, acc2])
        db.session.flush()
        
        access1 = UserAccountAccess(user_id=auth.user.id, account_id=acc1.id, role=AccountRole.OWNER.value)
        access2 = UserAccountAccess(user_id=auth.user.id, account_id=acc2.id, role=AccountRole.EDITOR.value)
        db.session.add_all([access1, access2])
        db.session.commit()

    response = auth.client.get('/api/accounts')
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) == 2
    assert {acc['name'] for acc in json_data} == {"Personal Savings", "Work Expenses"}

def test_update_account_success(auth, test_app):
    """
    GIVEN a user has 'manager' access to an account
    WHEN a POST request is made to /api/updateAccount
    THEN the account details are updated.
    """
    account_id = None
    with test_app.app_context():
        account = Account(name="Original Name", balance=100)
        db.session.add(account)
        db.session.flush()
        access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.MANAGER.value)
        db.session.add(access)
        db.session.commit()
        account_id = account.id

    update_data = {
        "account_id": account_id,
        "name": "Updated Name"
    }
    response = auth.client.post('/api/updateAccount', json=update_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['name'] == "Updated Name"

    with test_app.app_context():
        updated_account = Account.query.get(account_id)
        assert updated_account.name == "Updated Name"

def test_delete_account_success(auth, test_app):
    """
    GIVEN a user is the OWNER of an account with no transactions
    WHEN a POST request is made to /api/deleteAccount
    THEN the account is deleted.
    """
    with test_app.app_context():
        account = Account(name="To Be Deleted", balance=0)
        db.session.add(account)
        db.session.flush()
        access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.OWNER.value)
        db.session.add(access)
        db.session.commit()
        account_id = account.id

    response = auth.client.post('/api/deleteAccount', json={"account_id": account_id})
    assert response.status_code == 200
    assert response.get_json()['success'] is True

    with test_app.app_context():
        deleted_account = Account.query.get(account_id)
        assert deleted_account is None

def test_delete_account_forbidden(auth, test_app):
    """
    GIVEN a user is only a MANAGER of an account
    WHEN a POST request is made to /api/deleteAccount
    THEN the request is forbidden.
    """
    with test_app.app_context():
        account = Account(name="Protected Account", balance=100)
        db.session.add(account)
        db.session.flush()
        access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.MANAGER.value)
        db.session.add(access)
        db.session.commit()
        account_id = account.id

    response = auth.client.post('/api/deleteAccount', json={"account_id": account_id})
    assert response.status_code == 403
    assert "Forbidden" in response.get_json()['message']

def test_delete_account_with_transactions_fails(auth, test_app):
    """
    GIVEN an account has transactions
    WHEN an OWNER tries to delete it
    THEN the operation should fail to preserve data integrity.
    """
    with test_app.app_context():
        account = Account(name="Active Account", balance=100)
        db.session.add(account)
        db.session.flush()
        access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.OWNER.value)
        db.session.add(access)
        
        transaction = Transaction(account_id=account.id, name="Test", amount=10, date=date.today(), description="", currency="EUR", source="manual")
        db.session.add(transaction)
        db.session.commit()
        account_id = account.id

    response = auth.client.post('/api/deleteAccount', json={"account_id": account_id})
    assert response.status_code == 400
    assert "Cannot delete account with transactions" in response.get_json()['error']

    with test_app.app_context():
        account_still_exists = Account.query.get(account_id)
        assert account_still_exists is not None
