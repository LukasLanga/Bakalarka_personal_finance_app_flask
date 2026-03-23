import reflex as rx
from typing import List, Union, Dict, Any
from datetime import datetime
from ..models.models import Account, Category
from .base_state import BaseState
from ..api import client

class TransactionFormState(BaseState):
    """State for the transaction form."""
    form_account_id: str = ""
    category_name: str = ""
    name: str = ""
    amount: float = 0.0
    date: str = str(datetime.utcnow().date())
    description: str = ""
    error_message: str = ""
    is_loading: bool = False
    currency: str = "EUR"

    def reset_form(self):
        self.form_account_id = ""
        self.category_name = ""
        self.name = ""
        self.amount = 0.0
        self.date = str(datetime.utcnow().date())
        self.description = ""
        self.error_message = ""
        self.is_loading = False
        self.currency = "EUR"

    def set_name(self, value: str):
        self.name = value

    def set_amount(self, value: str):
        try:
            self.amount = float(value) if value else 0.0
        except ValueError:
            self.error_message = self.translations["Invalid amount. Please enter a number."]

    def set_date(self, value: str):
        self.date = value

    def set_description(self, value: str):
        self.description = value

    async def set_form_account_id(self, value: str):
        from .dashboard_state import DashboardState
        self.form_account_id = value
        dashboard_state = await self.get_state(DashboardState)
        for acc in dashboard_state.accounts:
            acc_id = acc.get("id") if isinstance(acc, dict) else acc.id
            if str(acc_id) == value: # Compare string with string
                self.currency = acc.get("currency") if isinstance(acc, dict) else acc.currency
                break

    def set_category_name(self, value: str):
        self.category_name = value

    async def handle_submit(self, accounts: List[Union[Account, Dict[str, Any]]], categories: List[Union[Category, Dict[str, Any]]]):
        from .dashboard_state import DashboardState
        self.is_loading = True
        self.error_message = ""
        try:
            def get_name(item):
                return item.get("name") if isinstance(item, dict) else item.name
            
            def get_id(item):
                return item.get("id") if isinstance(item, dict) else item.id
            
            def get_currency(item):
                return item.get("currency") if isinstance(item, dict) else item.currency

            if not self.name.strip():
                self.error_message = self.translations["Transaction name cannot be empty."]
                self.is_loading = False
                return

            if not self.form_account_id:
                self.error_message = self.translations["Please select a valid account."]
                self.is_loading = False
                return

            selected_account_id_int = int(self.form_account_id)
            selected_account = next((acc for acc in accounts if get_id(acc) == selected_account_id_int), None)
            if not selected_account:
                self.error_message = self.translations["Invalid account selected."]
                self.is_loading = False
                return

            selected_category = next((cat for cat in categories if get_name(cat) == self.category_name), None)
            if not selected_category:
                self.error_message = self.translations["Please select a valid category."]
                self.is_loading = False
                return

            client.create_transaction(
                self.get_http_client(),
                account_id=selected_account_id_int,
                category_id=get_id(selected_category),
                name=self.name,
                amount=self.amount,
                date=self.date,
                description=self.description,
                currency=get_currency(selected_account)
            )
            
            self.reset_form()
            return [DashboardState.toggle_transaction_modal, DashboardState.load_accounts, DashboardState.load_dashboard_summary]

        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_loading = False
