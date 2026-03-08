from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: int
    username: str
    email: str

class Account(BaseModel):
    id: int
    name: str
    balance: float
    bank_name: Optional[str] = None
    currency: str

class Category(BaseModel):
    id: int
    name: str
    type: str
    usage_count: int = 0

class Transaction(BaseModel):
    id: int
    name: str
    amount: float
    date: str
    description: Optional[str]
    category_id: Optional[int]
    account_id: int
    currency: str = "EUR"

class SpendingByCategory(BaseModel):
    category_name: str
    amount: float

class DashboardSummary(BaseModel):
    total_balance: float
    monthly_income: float
    monthly_expenses: float
    recent_transactions: List[Transaction]
    spending_by_category: List[SpendingByCategory]

class Invitation(BaseModel):
    id: int
    token: str
    account_name: str
    invited_by: str
    role: str

class AccountUser(BaseModel):
    id: int
    username: str
    email: str
    role: str
