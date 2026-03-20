import reflex as rx
from typing import List, Dict, Any
from .base_state import BaseState
from .dashboard_state import DashboardState
from ..api import client
import httpx

class AddBankAccountState(BaseState):
    """State for the 'Add Bank Account' modal."""
    show_modal: bool = False
    available_accounts: List[Dict[str, Any]] = []
    selected_kb_account_id: str = ""
    is_loading: bool = False
    error_message: str = ""

    @rx.var
    def available_account_options(self) -> List[Dict[str, str]]:
        """Formats the available accounts for the rx.select component."""
        return [
            {"label": f"{acc.get('nameI18N', 'Unnamed')} ({acc.get('currency')})", "value": acc.get('id')}
            for acc in self.available_accounts
        ]

    async def open_modal(self):
        """Opens the modal and fetches the list of available bank accounts."""
        self.show_modal = True
        self.error_message = ""
        self.selected_kb_account_id = ""
        self.available_accounts = []
        yield

        async for event in self.fetch_available_accounts():
            yield event

    def close_modal(self, open: bool):
        self.show_modal = open

    def set_selected_kb_account_id(self, account_id: str):
        """Setter for the selected account ID."""
        self.selected_kb_account_id = account_id

    async def fetch_available_accounts(self):
        self.is_loading = True
        yield
        try:
            self.available_accounts = client.get_available_kb_accounts()
        except Exception as e:
            self.error_message = f"Failed to fetch accounts: {e}"
        finally:
            self.is_loading = False
            yield

    async def add_selected_account(self):
        """Adds the selected bank account to the user's profile."""
        if not self.selected_kb_account_id:
            self.error_message = "Please select an account to add."
            yield
            return

        selected_account_data = next((acc for acc in self.available_accounts if acc.get('id') == self.selected_kb_account_id), None)
        
        if not selected_account_data:
            self.error_message = "Selected account not found. Please refresh and try again."
            yield
            return

        self.is_loading = True
        self.error_message = ""
        yield

        try:
            client.sync_single_kb_account(selected_account_data)
            self.show_modal = False
            
            dashboard_state = await self.get_state(DashboardState)
            async for event in dashboard_state.on_page_load():
                yield event

        except Exception as e:
            self.error_message = f"Failed to add account: {e}"
            yield
        finally:
            self.is_loading = False
            yield
