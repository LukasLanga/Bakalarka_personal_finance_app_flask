import pytest
from backend.app.db import db
from backend.app.models.account import Account
from backend.app.models.user_account_access import UserAccountAccess
from backend.app.models.invitation import AccountRole
from backend.app.models.transaction import Transaction
from backend.app.models.category import Category
from datetime import date, timedelta

@pytest.fixture
def setup_transactions(auth, test_app):
    """Fixture to create accounts and transactions for dashboard testing."""
    with test_app.app_context():
        acc1 = Account(name="Primary Account", balance=1000)
        db.session.add(acc1)
        db.session.flush()
        access1 = UserAccountAccess(user_id=auth.user.id, account_id=acc1.id, role=AccountRole.OWNER.value)
        db.session.add(access1)

        acc2 = Account(name="Savings", balance=5000)
        db.session.add(acc2)
        db.session.flush()
        access2 = UserAccountAccess(user_id=auth.user.id, account_id=acc2.id, role=AccountRole.OWNER.value)
        db.session.add(access2)

        cat1 = Category(name="Groceries", type="expense", user_id=auth.user.id)
        cat2 = Category(name="Transport", type="expense", user_id=auth.user.id)
        db.session.add_all([cat1, cat2])
        db.session.commit()

        today = date.today()
        last_month = today - timedelta(days=30)

        t1 = Transaction(account_id=acc1.id, name="Salary", amount=2000, date=today.replace(day=1), description="", currency="EUR", source="manual")
        t2 = Transaction(account_id=acc1.id, name="Rent", amount=-800, date=today.replace(day=2), description="", currency="EUR", source="manual")
        t3 = Transaction(account_id=acc1.id, name="Groceries", amount=-150, date=today.replace(day=3), category_id=cat1.id, description="", currency="EUR", source="manual")
        t4 = Transaction(account_id=acc2.id, name="Bonus", amount=500, date=last_month, description="", currency="EUR", source="manual")
        t5 = Transaction(account_id=acc1.id, name="Bus Fare", amount=-50, date=today.replace(day=4), category_id=cat2.id, description="", currency="EUR", source="manual")

        db.session.add_all([t1, t2, t3, t4, t5])
        db.session.commit()
        
        yield {"acc1_id": acc1.id, "acc2_id": acc2.id}


def test_get_dashboard_summary_all_accounts(auth, setup_transactions):
    """
    GIVEN a user with transactions across multiple accounts
    WHEN a GET request is made to /api/dashboard/summary without an account_id
    THEN a summary of the current month across all accounts is returned.
    """
    response = auth.client.get('/api/dashboard/summary')
    
    assert response.status_code == 200
    summary = response.get_json()
    
    assert float(summary['monthly_income']) == 2000
    assert float(summary['monthly_expenses']) == 1000 # 800 + 150 + 50
    assert len(summary['recent_transactions']) > 0
    assert summary['recent_transactions'][0]['name'] == 'Bus Fare'

def test_get_dashboard_summary_single_account(auth, setup_transactions):
    """
    GIVEN a user with transactions
    WHEN a GET request is made to /api/dashboard/summary with a specific account_id
    THEN a summary for only that account is returned.
    """
    acc2_id = setup_transactions['acc2_id']
    last_month = date.today() - timedelta(days=30)
    
    url = f'/api/dashboard/summary?account_id={acc2_id}&year={last_month.year}&month={last_month.month}'
    response = auth.client.get(url)
    
    assert response.status_code == 200
    summary = response.get_json()
    
    assert float(summary['monthly_income']) == 500
    assert float(summary['monthly_expenses']) == 0
    assert len(summary['recent_transactions']) == 1
    assert summary['recent_transactions'][0]['name'] == 'Bonus'

def test_get_yearly_overview(auth, setup_transactions):
    """
    GIVEN a user with transactions over the last year
    WHEN a GET request is made to /api/dashboard/yearly-overview
    THEN a list of 12 months with aggregated income/expenses is returned.
    """
    response = auth.client.get('/api/dashboard/yearly-overview')
    
    assert response.status_code == 200
    overview = response.get_json()
    
    assert isinstance(overview, list)
    assert len(overview) == 12

    today = date.today()
    last_month_date = today - timedelta(days=30)
    
    current_month_str = today.strftime('%b')
    last_month_str = last_month_date.strftime('%b')

    current_month_data = next((item for item in overview if item["month"] == current_month_str), None)
    last_month_data = next((item for item in overview if item["month"] == last_month_str), None)

    assert current_month_data is not None
    assert float(current_month_data['income']) == 2000
    assert float(current_month_data['expenses']) == 1000

    assert last_month_data is not None
    assert float(last_month_data['income']) == 500
    assert float(last_month_data['expenses']) == 0

def test_dashboard_summary_spending_by_category(auth, setup_transactions):
    """
    GIVEN transactions with categories
    WHEN a GET request is made to /api/dashboard/summary
    THEN the spending_by_category field is correctly aggregated and ordered.
    """
    response = auth.client.get('/api/dashboard/summary')
    
    assert response.status_code == 200
    summary = response.get_json()
    
    spending = summary['spending_by_category']
    assert isinstance(spending, list)
    assert len(spending) == 2
    
    assert spending[0]['category_name'] == 'Groceries'
    assert float(spending[0]['amount']) == 150
    
    assert spending[1]['category_name'] == 'Transport'
    assert float(spending[1]['amount']) == 50

def test_dashboard_summary_no_transactions(auth, test_app):
    """
    GIVEN a user with an account but no transactions in a given month
    WHEN a GET request is made to /api/dashboard/summary for that month
    THEN a zeroed-out summary is returned.
    """
    with test_app.app_context():
        acc = Account(name="Empty Account", balance=0)
        db.session.add(acc)
        db.session.flush()
        access = UserAccountAccess(user_id=auth.user.id, account_id=acc.id, role=AccountRole.OWNER.value)
        db.session.add(access)
        db.session.commit()

    # Request summary for a month with no transactions
    response = auth.client.get('/api/dashboard/summary?year=2020&month=1')
    
    assert response.status_code == 200
    summary = response.get_json()
    
    assert float(summary['monthly_income']) == 0
    assert float(summary['monthly_expenses']) == 0
    assert len(summary['recent_transactions']) == 0
    assert len(summary['spending_by_category']) == 0
