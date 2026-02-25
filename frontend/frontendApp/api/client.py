import os
import httpx
from typing import List
from ..models.models import User, Account, DashboardSummary

API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:5000/api")

http_client = httpx.Client(base_url=API_URL, follow_redirects=True)


def login(email: str, password: str) -> bool:
    """
    Attempts to log in the user by calling the backend API.
    """
    response = http_client.post("/login", json={"email": email, "password": password})
    response.raise_for_status()
    return True


def register(username: str, email: str, password: str) -> bool:
    """
    Registers a new user by calling the backend API.
    """
    response = http_client.post("/register", json={"username": username, "email": email, "password": password})
    response.raise_for_status()
    return True


def get_current_user() -> User:
    """
    Checks with the backend to see who is currently logged in.
    """
    response = http_client.get("/me")
    response.raise_for_status()
    return User(**response.json())


def get_accounts() -> List[Account]:
    """Fetches all accounts for the current user."""
    response = http_client.get("/accounts")
    response.raise_for_status()
    return [Account(**acc) for acc in response.json()]


def get_dashboard_summary() -> DashboardSummary:
    """Fetches the dashboard summary data."""
    response = http_client.get("/dashboard-summary")
    response.raise_for_status()
    return DashboardSummary(**response.json())
