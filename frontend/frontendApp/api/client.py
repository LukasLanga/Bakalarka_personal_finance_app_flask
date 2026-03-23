import os
import httpx
from typing import List, Optional, Dict, Any
from ..models.models import User, Account, DashboardSummary, Category, Transaction, Invitation, AccountUser

API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:5000/api")
ROOT_URL = API_URL.removesuffix("/api")


def login(client: httpx.Client, email: str, password: str) -> bool:
    """
    Attempts to log in the user by calling the backend API.
    """
    response = client.post("/login", json={"email": email, "password": password})
    response.raise_for_status()
    return True

def logout(client: httpx.Client):
    """Logs the user out by calling the backend API."""
    response = client.post("/logout")
    response.raise_for_status()
    return True

def register(client: httpx.Client, username: str, email: str, password: str) -> bool:
    """
    Registers a new user by calling the backend API.
    """
    response = client.post("/register", json={"username": username, "email": email, "password": password})
    response.raise_for_status()
    return True


def get_current_user(client: httpx.Client) -> User:
    """
    Checks with the backend to see who is currently logged in.
    """
    response = client.get("/me")
    response.raise_for_status()
    return User(**response.json())


def get_accounts(client: httpx.Client) -> List[Account]:
    """Fetches all accounts for the current user."""
    response = client.get("/accounts")
    response.raise_for_status()
    return [Account(**acc) for acc in response.json()]


def list_categories(client: httpx.Client) -> List[Category]:
    """Fetches all categories for the current user."""
    response = client.get("/listCategories")
    response.raise_for_status()
    return [Category(**cat) for cat in response.json()]


def get_dashboard_summary(client: httpx.Client, account_id: Optional[int] = None, year: Optional[int] = None, month: Optional[int] = None) -> DashboardSummary:
    """Fetches the dashboard summary data."""
    params = {}
    if account_id:
        params["account_id"] = account_id
    if year:
        params["year"] = year
    if month:
        params["month"] = month
    response = client.get("/dashboardSummary", params=params)
    response.raise_for_status()
    return DashboardSummary(**response.json())


def get_yearly_overview(client: httpx.Client, account_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetches the income and expenses for the last 12 months."""
    params = {}
    if account_id:
        params["account_id"] = account_id
    response = client.get("/yearly-overview", params=params)
    response.raise_for_status()
    return response.json()


def create_transaction(client: httpx.Client, name: str, amount: float, date: str, description: Optional[str], account_id: int, category_id: Optional[int], currency: str = "EUR"):
    payload = {
        "name": name,
        "amount": amount,
        "date": date,
        "description": description,
        "account_id": account_id,
        "category_id": category_id,
        "currency": currency,
    }
    try:
        response = client.post("/createTransaction", json=payload)
        response.raise_for_status()
        return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            raise Exception("You do not have permission to add transactions to this account.")
        raise e

def update_transaction(client: httpx.Client, transaction_id: int, account_id: int, name: Optional[str] = None, amount: Optional[float] = None, date: Optional[str] = None, description: Optional[str] = None, category_id: Optional[int] = None):
    payload = {
        "transaction_id": transaction_id,
        "account_id": account_id,
        "name": name,
        "amount": amount,
        "date": date,
        "description": description,
        "category_id": category_id,
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    response = client.post("/updateTransaction", json=payload)
    response.raise_for_status()
    return Transaction(**response.json())

def delete_transaction(client: httpx.Client, account_id: int, transaction_id: int) -> bool:
    """Deletes a transaction."""
    response = client.post("/deleteTransaction", json={"account_id": account_id, "transaction_id": transaction_id})
    response.raise_for_status()
    return True

def get_transaction(client: httpx.Client, account_id: int, transaction_id: int) -> Transaction:
    """Fetches a single transaction."""
    response = client.get("/getTransaction", params={"account_id": account_id, "transaction_id": transaction_id})
    response.raise_for_status()
    return Transaction(**response.json())

def get_all_transactions(client: httpx.Client, page: int = 1, per_page: int = 10, search_query: Optional[str] = None, account_id: Optional[int] = None, category_id: Optional[int] = None) -> Dict[str, Any]:
    """Fetches all transactions for the current user."""
    params = {"page": page, "per_page": per_page}
    if search_query:
        params["search_query"] = search_query
    if account_id:
        params["account_id"] = account_id
    if category_id:
        params["category_id"] = category_id

    response = client.get("/getAllTransactions", params=params)
    response.raise_for_status()
    data = response.json()
    data["transactions"] = [Transaction(**t) for t in data["transactions"]]
    return data

def create_account(client: httpx.Client, name: str, bank_name: str, balance: float, currency: str = "EUR"):
    """Creates a new account."""
    payload = {
        "name": name,
        "bank_name": bank_name,
        "balance": balance,
        "currency": currency,
    }
    response = client.post("/createAccount", json=payload)
    response.raise_for_status()
    return True

def update_account(client: httpx.Client, account_id: int, name: Optional[str] = None, bank_name: Optional[str] = None, currency: Optional[str] = None):
    """Updates an existing account."""
    payload = {
        "account_id": account_id,
        "name": name,
        "bank_name": bank_name,
        "currency": currency,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    
    response = client.post("/updateAccount", json=payload)
    response.raise_for_status()
    return Account(**response.json())

def delete_account(client: httpx.Client, account_id: int) -> bool:
    """Deletes an account."""
    response = client.post("/deleteAccount", json={"account_id": account_id})
    response.raise_for_status()
    return True

def create_category(client: httpx.Client, name: str, type: str) -> bool:
    """Creates a new category."""
    payload = {"name": name, "type": type}
    response = client.post("/createCategory", json=payload)
    response.raise_for_status()
    return True

def delete_category(client: httpx.Client, name: str) -> bool:
    """Deletes a category."""
    payload = {"name": name}
    response = client.post("/deleteCategory", json=payload)
    response.raise_for_status()
    return True

def get_pending_invitations(client: httpx.Client) -> List[Invitation]:
    """Fetches all pending invitations for the current user."""
    response = client.get("/invitations/pending")
    response.raise_for_status()
    return [Invitation(**inv) for inv in response.json()]

def accept_invitation(client: httpx.Client, token: str) -> bool:
    """Accepts an invitation."""
    response = client.post("/invitations/accept", json={"token": token})
    response.raise_for_status()
    return True

def decline_invitation(client: httpx.Client, token: str) -> bool:
    """Declines an invitation."""
    response = client.post("/invitations/decline", json={"token": token})
    response.raise_for_status()
    return True

def get_account_users(client: httpx.Client, account_id: int) -> List[AccountUser]:
    """Fetches all users for a specific account."""
    response = client.get(f"/accounts/{account_id}/users")
    response.raise_for_status()
    return [AccountUser(**user) for user in response.json()]

def update_user_role(client: httpx.Client, account_id: int, user_id: int, role: str) -> bool:
    """Updates a user's role on an account."""
    response = client.put(f"/accounts/{account_id}/users/{user_id}", json={"role": role})
    response.raise_for_status()
    return True

def remove_user_from_account(client: httpx.Client, account_id: int, user_id: int) -> bool:
    """Removes a user from an account."""
    response = client.delete(f"/accounts/{account_id}/users/{user_id}")
    response.raise_for_status()
    return True

def invite_user_to_account(client: httpx.Client, account_id: int, email: str, role: str) -> bool:
    """Invites a user to an account."""
    payload = {"invited_email": email, "role": role}
    response = client.post(f"/accounts/{account_id}/invitations", json=payload)
    response.raise_for_status()
    return True

def get_user_roles(client: httpx.Client) -> Dict[str, str]:
    """Fetches all roles for the current user."""
    response = client.get("/user-roles")
    response.raise_for_status()
    return response.json()

# --- KB Bank Integration ---

def get_kb_connection_status(client: httpx.Client) -> bool:
    """Checks if the user has a valid connection to KB bank."""
    response = client.get(f"{ROOT_URL}/kb/connection-status")
    response.raise_for_status()
    return response.json().get("connected", False)

def connect_to_kb_bank(client: httpx.Client):
    """Establishes the initial connection to the KB bank."""
    response = client.post(f"{ROOT_URL}/kb/token")
    response.raise_for_status()
    return response.json()

def get_available_kb_accounts(client: httpx.Client) -> List[Dict[str, Any]]:
    """Fetches bank accounts from KB that have not been added yet."""
    response = client.get(f"{ROOT_URL}/kb/available-accounts")
    response.raise_for_status()
    return response.json()

def sync_single_kb_account(client: httpx.Client, kb_account_data: Dict[str, Any]):
    """Triggers a sync for a single, specific KB account."""
    response = client.post(f"{ROOT_URL}/kb/sync-single-account", json=kb_account_data, timeout=120)
    response.raise_for_status()
    return response.json()
