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
    selected_account_filter: str = ""
    selected_category_filter: str = ""
    current_page: int = 1
    total_pages: int = 1

    @rx.var
    def account_id_to_name(self) -> Dict[str, str]:
        return {str(acc.id): acc.name for acc in self.accounts}

    @rx.var
    def category_id_to_name(self) -> Dict[str, str]:
        return {str(cat.id): cat.name for cat in self.categories}

    @rx.var
    def account_filter_options(self) -> List[str]:
        return [self.translations["All Accounts"]] + [acc.name for acc in self.accounts]

    @rx.var
    def category_filter_options(self) -> List[str]:
        return [self.translations["All Categories"]] + [cat.name for cat in self.categories]

    @rx.var
    def filtered_transactions(self) -> List[Transaction]:
        return self.transactions

    async def set_search_query(self, value: str):
        self.search_query = value
        self.current_page = 1
        async for event in self.load_data():
            yield event

    async def set_selected_account_filter(self, value: str):
        self.selected_account_filter = value
        self.current_page = 1
        async for event in self.load_data():
            yield event

    async def set_selected_category_filter(self, value: str):
        self.selected_category_filter = value
        self.current_page = 1
        async for event in self.load_data():
            yield event

    async def set_page(self, page: int):
        self.current_page = page
        async for event in self.load_data():
            yield event

    async def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            async for event in self.load_data():
                yield event

    async def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            async for event in self.load_data():
                yield event

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

            # Check if the current filter values are valid, otherwise reset to the translated default.
            if self.selected_account_filter not in self.account_filter_options:
                self.selected_account_filter = self.translations["All Accounts"]
            if self.selected_category_filter not in self.category_filter_options:
                self.selected_category_filter = self.translations["All Categories"]

            account_id = None
            if self.selected_account_filter != self.translations["All Accounts"]:
                selected_acc = next((acc for acc in self.accounts if acc.name == self.selected_account_filter), None)
                if selected_acc:
                    account_id = selected_acc.id

            category_id = None
            if self.selected_category_filter != self.translations["All Categories"]:
                selected_cat = next((cat for cat in self.categories if cat.name == self.selected_category_filter), None)
                if selected_cat:
                    category_id = selected_cat.id

            data = client.get_all_transactions(
                page=self.current_page,
                search_query=self.search_query,
                account_id=account_id,
                category_id=category_id
            )
            self.transactions = data["transactions"]
            self.total_pages = data["total_pages"]
            self.current_page = data["current_page"]
        except Exception as e:
            self.error_message = f"Error loading data: {e}"
        finally:
            self.is_loading = False
