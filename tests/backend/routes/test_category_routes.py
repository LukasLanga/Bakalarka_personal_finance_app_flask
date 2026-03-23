import pytest
from backend.app.db import db
from backend.app.models.category import Category
from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.transaction import Transaction
from backend.app.models.user_account_access import UserAccountAccess
from backend.app.models.invitation import AccountRole
from datetime import date

def test_create_category_success(auth, test_app):
    """
    GIVEN a logged-in user
    WHEN a POST request is made to /api/createCategory
    THEN a new category is created for that user.
    """
    category_data = {
        "name": "Groceries",
        "type": "expense"
    }
    response = auth.client.post('/api/createCategory', json=category_data)
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['name'] == "Groceries"
    assert json_data['type'] == "expense"

    with test_app.app_context():
        category = Category.query.get(json_data['id'])
        assert category is not None
        assert category.user_id == auth.user.id

def test_list_categories_success(auth, test_app):
    """
    GIVEN a user has several categories
    WHEN a GET request is made to /api/listCategories
    THEN a list of those categories is returned.
    """
    with test_app.app_context():
        cat1 = Category(name="Salary", type="income", user_id=auth.user.id)
        cat2 = Category(name="Rent", type="expense", user_id=auth.user.id)
        db.session.add_all([cat1, cat2])
        db.session.commit()

    response = auth.client.get('/api/listCategories')
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) == 2
    assert {cat['name'] for cat in json_data} == {"Salary", "Rent"}

def test_delete_category_success(auth, test_app):
    """
    GIVEN a user owns a category with no transactions
    WHEN a POST request is made to /api/deleteCategory
    THEN the category is deleted.
    """
    category_name = "To Be Deleted"
    with test_app.app_context():
        category = Category(name=category_name, type="expense", user_id=auth.user.id)
        db.session.add(category)
        db.session.commit()
        category_id = category.id

    response = auth.client.post('/api/deleteCategory', json={"name": category_name})
    assert response.status_code == 200
    assert response.get_json()['success'] is True

    with test_app.app_context():
        deleted_category = Category.query.get(category_id)
        assert deleted_category is None

def test_delete_category_forbidden(auth, test_app):
    """
    GIVEN a category owned by another user
    WHEN a user tries to delete it via /api/deleteCategory
    THEN the operation should fail.
    """
    category_name = "Secret Category"
    with test_app.app_context():
        other_user = User(username="otheruser", email="other@user.com", password="pw")
        db.session.add(other_user)
        db.session.flush()
        
        other_category = Category(name=category_name, type="expense", user_id=other_user.id)
        db.session.add(other_category)
        db.session.commit()

    response = auth.client.post('/api/deleteCategory', json={"name": category_name})
    
    assert response.status_code == 400 
    assert "Category not found" in response.get_json().get('error', '')

    with test_app.app_context():
        category_still_exists = Category.query.filter_by(name=category_name).first()
        assert category_still_exists is not None

def test_delete_category_with_transactions_fails(auth, test_app):
    """
    GIVEN a category is assigned to existing transactions
    WHEN a user tries to delete it
    THEN the operation should fail to preserve data integrity.
    """
    category_name = "Holiday"
    with test_app.app_context():
        account = Account(name="Test Account", balance=1000)
        db.session.add(account)
        db.session.flush()
        access = UserAccountAccess(user_id=auth.user.id, account_id=account.id, role=AccountRole.OWNER.value)
        db.session.add(access)

        category = Category(name=category_name, type="expense", user_id=auth.user.id)
        db.session.add(category)
        db.session.flush()
        
        transaction = Transaction(
            account_id=account.id,
            category_id=category.id,
            name="Flight tickets",
            amount=-500,
            date=date.today(),
            description="",
            currency="EUR",
            source="manual"
        )
        db.session.add(transaction)
        db.session.commit()
        category_id = category.id

    response = auth.client.post('/api/deleteCategory', json={"name": category_name})
    
    assert response.status_code == 400
    expected_error = f"Cannot delete category '{category_name}' as it is currently in use."
    assert expected_error in response.get_json().get('error', '')

    with test_app.app_context():
        category_still_exists = Category.query.get(category_id)
        assert category_still_exists is not None
