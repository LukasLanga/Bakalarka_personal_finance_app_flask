import pytest
from backend.app.db import db
from backend.app.models.account import Account
from backend.app.models.user import User
from backend.app.models.category import Category
from backend.app.models.user_account_access import UserAccountAccess
from backend.app.models.invitation import AccountRole
from backend.app.models.transaction import Transaction
from datetime import date

@pytest.fixture
def setup_account(auth, test_app):
    """Fixture to create an account and give the authenticated user owner access."""
    with test_app.app_context():
        account = Account(name="Test Account", balance=1000)
        db.session.add(account)
        db.session.flush()
        access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.OWNER.value)
        db.session.add(access)
        db.session.commit()
        yield account

def test_create_transaction_success(auth, setup_account, test_app):
    """Test creating a transaction successfully."""
    transaction_data = {
        "account_id": setup_account.id,
        "name": "Coffee",
        "amount": -5.50,
        "date": "2024-01-15",
        "description": "Morning coffee",
        "currency": "EUR",
        "source": "manual"
    }
    response = auth.client.post('/api/createTransaction', json=transaction_data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['name'] == "Coffee"

def test_get_transactions_by_account(auth, setup_account, test_app):
    """Test listing transactions for a specific account."""
    with test_app.app_context():
        t1 = Transaction(account_id=setup_account.id, name="Lunch", amount=-12, date=date.today(), description="", currency="EUR", source="manual")
        t2 = Transaction(account_id=setup_account.id, name="Salary", amount=2000, date=date.today(), description="", currency="EUR", source="manual")
        db.session.add_all([t1, t2])
        db.session.commit()

    response = auth.client.get(f'/api/getTransactionsByAccount?account_id={setup_account.id}')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 2

def test_create_transaction_forbidden(auth, test_app):
    """Test creating a transaction on an account the user does not have access to."""
    with test_app.app_context():
        other_user = User(username="other", email="other@e.com", password="pw")
        other_account = Account(name="Secret Account", balance=999)
        db.session.add_all([other_user, other_account])
        db.session.flush()
        access = UserAccountAccess(user_id=other_user.id, account_id=other_account.id, role=AccountRole.OWNER.value)
        db.session.add(access)
        db.session.commit()
        account_id = other_account.id

    transaction_data = {"account_id": account_id, "name": "Fraud", "amount": -100, "date": "2024-01-15"}
    response = auth.client.post('/api/createTransaction', json=transaction_data)
    assert response.status_code == 403

def test_get_transactions_forbidden(auth, test_app):
    """Test listing transactions from an account the user does not have access to."""
    with test_app.app_context():
        other_user = User(username="other2", email="other2@e.com", password="pw")
        other_account = Account(name="Other Account", balance=500)
        db.session.add_all([other_user, other_account])
        db.session.flush()
        access = UserAccountAccess(user_id=other_user.id, account_id=other_account.id, role=AccountRole.OWNER.value)
        db.session.add(access)
        db.session.commit()
        account_id = other_account.id

    response = auth.client.get(f'/api/getTransactionsByAccount?account_id={account_id}')
    assert response.status_code == 403

def test_delete_transaction_success(auth, setup_account, test_app):
    """Test deleting a transaction successfully."""
    with test_app.app_context():
        transaction = Transaction(account_id=setup_account.id, name="To Delete", amount=-50, date=date.today(), description="", currency="EUR", source="manual")
        db.session.add(transaction)
        db.session.commit()
        transaction_id = transaction.id

    delete_data = {"account_id": setup_account.id, "transaction_id": transaction_id}
    response = auth.client.post('/api/deleteTransaction', json=delete_data)
    assert response.status_code == 200

def test_update_transaction_success(auth, setup_account, test_app):
    """Test updating a transaction successfully."""
    with test_app.app_context():
        transaction = Transaction(account_id=setup_account.id, name="Original", amount=-100, date=date.today(), description="Old", currency="EUR", source="manual")
        db.session.add(transaction)
        db.session.commit()
        transaction_id = transaction.id

    update_data = {"transaction_id": transaction_id, "account_id": setup_account.id, "name": "Updated"}
    response = auth.client.post('/api/updateTransaction', json=update_data)
    assert response.status_code == 200
    assert response.get_json()['name'] == "Updated"

def test_get_all_transactions_pagination(auth, setup_account, test_app):
    """Test pagination for getAllTransactions."""
    with test_app.app_context():
        for i in range(15):
            db.session.add(Transaction(account_id=setup_account.id, name=f"T{i}", amount=-1, date=date.today(), description="", currency="EUR", source="manual"))
        db.session.commit()

    response = auth.client.get('/api/getAllTransactions?page=2&per_page=10')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data['transactions']) == 5

def test_get_all_transactions_search(auth, setup_account, test_app):
    """Test search functionality for getAllTransactions."""
    with test_app.app_context():
        db.session.add_all([
            Transaction(account_id=setup_account.id, name="Unique Coffee", amount=-5, date=date.today(), description="Morning", currency="EUR", source="manual"),
            Transaction(account_id=setup_account.id, name="Groceries", amount=-100, date=date.today(), description="Weekly shop", currency="EUR", source="manual")
        ])
        db.session.commit()

    response = auth.client.get('/api/getAllTransactions?search_query=Unique')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data['transactions']) == 1
    assert json_data['transactions'][0]['name'] == 'Unique Coffee'

def test_get_all_transactions_filter_by_account(auth, test_app):
    """Test filtering by account_id for getAllTransactions."""
    with test_app.app_context():
        acc1 = Account(name="Acc1", balance=100)
        acc2 = Account(name="Acc2", balance=100)
        db.session.add_all([acc1, acc2])
        db.session.flush()
        
        db.session.add_all([
            UserAccountAccess(user_id=auth.user.id, account_id=acc1.id, role=AccountRole.OWNER.value),
            UserAccountAccess(user_id=auth.user.id, account_id=acc2.id, role=AccountRole.OWNER.value)
        ])
        db.session.add_all([
            Transaction(account_id=acc1.id, name="From Acc1", amount=-10, date=date.today(), description="", currency="EUR", source="manual"),
            Transaction(account_id=acc2.id, name="From Acc2", amount=-20, date=date.today(), description="", currency="EUR", source="manual")
        ])
        db.session.commit()
        acc1_id = acc1.id

    response = auth.client.get(f'/api/getAllTransactions?account_id={acc1_id}')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data['transactions']) == 1
    assert json_data['transactions'][0]['name'] == 'From Acc1'

def test_create_transaction_with_other_users_category_fails(auth, test_app, setup_account):
    """Test that a user cannot assign a category they do not own to a transaction."""
    with test_app.app_context():
        other_user = User(username="other_cat_user", email="othercat@e.com", password="pw")
        db.session.add(other_user)
        db.session.flush()
        other_category = Category(name="Secret Category", type="expense", user_id=other_user.id)
        db.session.add(other_category)
        db.session.commit()
        other_category_id = other_category.id

    transaction_data = {
        "account_id": setup_account.id,
        "name": "Bad Category",
        "amount": -50,
        "date": "2024-01-15",
        "description": "Trying to use another user's category",
        "currency": "EUR",
        "source": "manual",
        "category_id": other_category_id
    }
    response = auth.client.post('/api/createTransaction', json=transaction_data)
    assert response.status_code == 500
    assert "Category not found or does not belong to user" in response.get_json()['error']

def test_create_transaction_missing_required_data(auth, setup_account):
    """Test that creating a transaction with missing required fields fails."""
    transaction_data = {
        "account_id": setup_account.id,
        "amount": -5.50,
        "date": "2024-01-15",
        "description": "Missing name",
        "currency": "EUR",
        "source": "manual"
    }
    response = auth.client.post('/api/createTransaction', json=transaction_data)
    assert response.status_code == 500
