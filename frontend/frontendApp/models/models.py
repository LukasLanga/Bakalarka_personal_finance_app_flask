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
    bank_name: str
    currency: str

class Transaction(BaseModel):
    id: int
    name: str
    amount: float
    date: str
    description: Optional[str]
    category_id: Optional[int]

class SpendingByCategory(BaseModel):
    category_name: str
    amount: float

class DashboardSummary(BaseModel):
    total_balance: float
    monthly_income: float
    monthly_expenses: float
    recent_transactions: List[Transaction]
    spending_by_category: List[SpendingByCategory]
