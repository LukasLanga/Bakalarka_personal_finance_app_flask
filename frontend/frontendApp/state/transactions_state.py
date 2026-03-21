import reflex as rx
from typing import List, Dict
from ..models.models import Transaction, Account, Category, EnrichedTransaction
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
        options = [self.translations.get("All Accounts", "All Accounts")]
        options.extend(acc.name for acc in self.accounts)
        return options

    @rx.var
    def category_filter_options(self) -> List[str]:
        options = [self.translations.get("All Categories", "All Categories")]
        options.extend(cat.name for cat in self.categories)
        return options

    @rx.var
    def enriched_transactions(self) -> List[EnrichedTransaction]:
        """Combines transactions with their account names."""
        enriched = []
        for t in self.transactions:
            account_name = self.account_id_to_name.get(str(t.account_id), "N/A")
            enriched.append(
                EnrichedTransaction(
                    id=t.id,
                    name=t.name,
                    amount=t.amount,
                    date=t.date,
                    description=t.description,
                    category_id=t.category_id,
                    account_id=t.account_id,
                    currency=t.currency,
                    account_name=account_name,
                )
            )
        return enriched

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
        yield

        try:
            accounts = client.get_accounts(self.get_http_client())
            categories = client.list_categories(self.get_http_client())

            all_accounts_str = self.translations.get("All Accounts", "All Accounts")
            all_categories_str = self.translations.get("All Categories", "All Categories")

            if self.selected_account_filter not in [acc.name for acc in accounts] and self.selected_account_filter != all_accounts_str:
                self.selected_account_filter = all_accounts_str
            if self.selected_category_filter not in [cat.name for cat in categories] and self.selected_category_filter != all_categories_str:
                self.selected_category_filter = all_categories_str

            account_id = None
            if self.selected_account_filter != all_accounts_str:
                selected_acc = next((acc for acc in accounts if acc.name == self.selected_account_filter), None)
                if selected_acc:
                    account_id = selected_acc.id

            category_id = None
            if self.selected_category_filter != all_categories_str:
                selected_cat = next((cat for cat in categories if cat.name == self.selected_category_filter), None)
                if selected_cat:
                    category_id = selected_cat.id

            data = client.get_all_transactions(
                self.get_http_client(),
                page=self.current_page,
                search_query=self.search_query,
                account_id=account_id,
                category_id=category_id
            )
            
            self.accounts = accounts
            self.categories = categories
            self.transactions = data["transactions"]
            self.total_pages = data["total_pages"]
            self.current_page = data["current_page"]

        except Exception as e:
            self.error_message = f"Error loading data: {e}"
        finally:
            self.is_loading = False
            yield
