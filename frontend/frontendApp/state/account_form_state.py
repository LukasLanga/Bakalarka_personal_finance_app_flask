import reflex as rx
from .base_state import BaseState
from .dashboard_state import DashboardState
from ..api import client

class AccountFormState(BaseState):
    """State for the account form."""
    name: str = ""
    bank_name: str = ""
    balance: float = 0.0
    currency: str = "EUR"
    error_message: str = ""
    is_loading: bool = False

    def set_name(self, value: str):
        self.name = value

    def set_bank_name(self, value: str):
        self.bank_name = value

    def set_balance(self, value: str):
        try:
            self.balance = float(value) if value else 0.0
        except ValueError:
            self.error_message = "Invalid balance. Please enter a number."

    def set_currency(self, value: str):
        self.currency = value

    async def handle_submit(self):
        self.is_loading = True
        self.error_message = ""
        try:
            if not self.name or not self.bank_name:
                self.error_message = self.translations["Name and Bank Name are required."]
                self.is_loading = False
                return

            client.create_account(
                name=self.name,
                bank_name=self.bank_name,
                balance=self.balance,
                currency=self.currency
            )
            
            self.name = ""
            self.bank_name = ""
            self.balance = 0.0
            self.currency = "EUR"
            
            return [DashboardState.toggle_account_modal, DashboardState.load_accounts, DashboardState.load_dashboard_summary]

        except Exception as e:
            self.error_message = f"Failed to create account: {e}"
        finally:
            self.is_loading = False
