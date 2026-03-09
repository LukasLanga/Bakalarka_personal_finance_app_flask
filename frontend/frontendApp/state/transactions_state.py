import reflex as rx
from typing import List, Dict
from ..models.models import Transaction, Account, Category
from .base_state import BaseState
from ..api import client

class TransactionsState(BaseState):
    """State for the transactions page."""
    transactions: List[Transaction] = []
    accounts: List[Account] = []
    categories: List[Category] = []
    is_loading: bool = False
    error_message: str = ""
    search_query: str = ""
    selected_account_filter: str = "All Accounts"
    selected_category_filter: str = "All Categories"

    @rx.var
    def account_id_to_name(self) -> Dict[str, str]:
        return {str(acc.id): acc.name for acc in self.accounts}

    @rx.var
    def category_id_to_name(self) -> Dict[str, str]:
        return {str(cat.id): cat.name for cat in self.categories}

    @rx.var
    def account_filter_options(self) -> List[str]:
        return ["All Accounts"] + [acc.name for acc in self.accounts]

    @rx.var
    def category_filter_options(self) -> List[str]:
        return ["All Categories"] + [cat.name for cat in self.categories]

    @rx.var
    def filtered_transactions(self) -> List[Transaction]:
        filtered = self.transactions
        
        if self.search_query:
            query = self.search_query.lower()
            filtered = [
                t for t in filtered
                if query in t.name.lower() or query in (t.description or "").lower()
            ]
        
        if self.selected_account_filter != "All Accounts":
            selected_acc = next((acc for acc in self.accounts if acc.name == self.selected_account_filter), None)
            if selected_acc:
                filtered = [t for t in filtered if t.account_id == selected_acc.id]

        if self.selected_category_filter != "All Categories":
            selected_cat = next((cat for cat in self.categories if cat.name == self.selected_category_filter), None)
            if selected_cat:
                filtered = [t for t in filtered if t.category_id == selected_cat.id]

        return filtered

    def set_search_query(self, value: str):
        self.search_query = value

    def set_selected_account_filter(self, value: str):
        self.selected_account_filter = value

    def set_selected_category_filter(self, value: str):
        self.selected_category_filter = value

    async def load_data(self):
        async for event in self.check_auth():
            yield event
        
        if not self.is_authenticated:
            return

        self.is_loading = True
        self.error_message = ""
        try:
            self.accounts = client.get_accounts()
            self.categories = client.list_categories()
            self.transactions = client.get_all_transactions()
        except Exception as e:
            self.error_message = f"Error loading data: {e}"
        finally:
            self.is_loading = False
