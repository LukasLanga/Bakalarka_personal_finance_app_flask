import reflex as rx
from typing import List, Dict, Any, Optional
from ..models.models import Account, Category, DashboardSummary, Invitation, EnrichedTransaction
from .base_state import BaseState
from ..api import client
import httpx
from datetime import datetime

PIE_CHART_COLORS = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]

class DashboardState(BaseState):
    """State for the main dashboard."""
    accounts: List[Account] = []
    categories: List[Category] = []
    dashboard_summary: Optional[DashboardSummary] = None
    yearly_overview: List[Dict[str, Any]] = []
    pending_invitations: List[Invitation] = []
    user_roles: Dict[str, str] = {}
    is_loading: bool = False
    is_syncing: bool = False
    is_kb_connected: bool = False
    show_transaction_modal: bool = False
    show_account_modal: bool = False
    show_manage_accounts_modal: bool = False
    show_invitation_modal: bool = False
    selected_invitation: Optional[Invitation] = None
    is_sidebar_collapsed: bool = True
    error_message: str = ""
    selected_account_id: int | None = None
    selected_year: int = datetime.now().year
    selected_month: int = datetime.now().month

    @rx.var
    def selected_month_str(self) -> str:
        """Returns the selected month and year as a formatted string."""
        return f"{self.selected_month:02d}.{self.selected_year}"

    async def next_month(self):
        """Moves to the next month."""
        if self.selected_month == 12:
            self.selected_month = 1
            self.selected_year += 1
        else:
            self.selected_month += 1
        self.load_dashboard_summary()
        yield

    async def prev_month(self):
        """Moves to the previous month."""
        if self.selected_month == 1:
            self.selected_month = 12
            self.selected_year -= 1
        else:
            self.selected_month -= 1
        self.load_dashboard_summary()
        yield

    @rx.var
    def pending_invitations_count(self) -> int:
        return len(self.pending_invitations)

    @rx.var
    def can_add_transaction(self) -> bool:
        """Check if the user has editor rights on at least one account."""
        editable_roles = ["editor", "manager", "owner"]
        for role in self.user_roles.values():
            if role in editable_roles:
                return True
        return False

    @rx.var
    def account_options(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionaries with account names and ids."""
        return [{"label": acc.name, "value": str(acc.id)} for acc in self.accounts]

    @rx.var
    def category_names(self) -> List[str]:
        return [cat.name for cat in self.categories]

    @rx.var
    def category_options(self) -> List[Dict[str, str]]:
        """Returns a list of dictionaries with category names for the select component."""
        return [{"label": cat.name, "value": cat.name} for cat in self.categories]

    @rx.var
    def spending_by_category_dict(self) -> List[Dict[str, Any]]:
        if self.dashboard_summary and self.dashboard_summary.spending_by_category:
            total_spending = sum(item.amount for item in self.dashboard_summary.spending_by_category)
            if total_spending == 0:
                return []

            data_with_colors = []
            for i, item in enumerate(self.dashboard_summary.spending_by_category):
                item_dict = item.dict()
                item_dict["fill"] = PIE_CHART_COLORS[i % len(PIE_CHART_COLORS)]
                item_dict["percentage"] = round((item.amount / total_spending) * 100)
                data_with_colors.append(item_dict)
            return data_with_colors
        return []

    @rx.var
    def account_id_to_name(self) -> Dict[str, str]:
        return {str(acc.id): acc.name for acc in self.accounts}

    @rx.var
    def enriched_recent_transactions(self) -> List[EnrichedTransaction]:
        """Combines recent transactions with their account names."""
        if not self.dashboard_summary:
            return []
        enriched = []
        for t in self.dashboard_summary.recent_transactions:
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

    @rx.var
    def selected_account_currency(self) -> str:
        if self.selected_account_id:
            for acc in self.accounts:
                if acc.id == self.selected_account_id:
                    return acc.currency
        elif self.accounts:
             return self.accounts[0].currency
        return "EUR"

    async def on_page_load(self):
        self.show_transaction_modal = False
        self.show_account_modal = False
        self.show_manage_accounts_modal = False
        
        async for event in self.check_auth():
            yield event
        if not self.is_authenticated:
            return

        self.is_loading = True
        yield

        try:
            self.load_kb_connection_status()
            async for event in self.load_accounts():
                yield event
            
            if not self.is_authenticated:
                return

            if self.selected_account_id is None and self.accounts:
                self.selected_account_id = self.accounts[0].id

            self.load_user_roles()
            self.load_dashboard_summary()
            self.load_yearly_overview()
            self.load_pending_invitations()
        except Exception as e:
            self.error_message = f"Error loading dashboard data: {e}"
        finally:
            self.is_loading = False
            yield

    def toggle_sidebar(self):
        self.is_sidebar_collapsed = not self.is_sidebar_collapsed

    async def toggle_transaction_modal(self):
        from .transaction_form_state import TransactionFormState
        self.show_transaction_modal = not self.show_transaction_modal
        if not self.show_transaction_modal:
            form_state = await self.get_state(TransactionFormState)
            form_state.reset_form()
        else:
            self.load_categories()

    async def toggle_account_modal(self):
        from .account_form_state import AccountFormState
        self.show_account_modal = not self.show_account_modal
        if not self.show_account_modal:
            form_state = await self.get_state(AccountFormState)
            form_state.error_message = ""

    def toggle_manage_accounts_modal(self):
        self.show_manage_accounts_modal = not self.show_manage_accounts_modal

    async def handle_manage_modal_change(self, open: bool):
        from .manage_accounts_state import ManageAccountsState
        self.show_manage_accounts_modal = open
        if not open:
            manage_state = await self.get_state(ManageAccountsState)
            manage_state.cancel_edit()

    def set_show_invitation_modal(self, open: bool):
        self.show_invitation_modal = open
        if not open:
            self.selected_invitation = None

    def select_and_show_invitation(self, inv: Invitation):
        self.selected_invitation = inv
        self.show_invitation_modal = True

    async def select_account(self, account_id: int):
        self.selected_account_id = account_id
        self.load_dashboard_summary()
        self.load_yearly_overview()
        yield

    async def load_accounts(self):
        try:
            self.accounts = client.get_accounts()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                self.is_authenticated = False
                yield rx.redirect("/login")
            else:
                self.error_message = f"Error loading accounts: {e}"
        except Exception as e:
            self.error_message = f"Error loading accounts: {e}"

    def load_user_roles(self):
        try:
            self.user_roles = client.get_user_roles()
        except Exception as e:
            print(f"Error loading user roles: {e}")

    def load_categories(self):
        try:
            self.categories = client.list_categories()
        except Exception as e:
            print(f"Error loading categories: {e}")

    def load_dashboard_summary(self):
        try:
            self.dashboard_summary = client.get_dashboard_summary(
                account_id=self.selected_account_id,
                year=self.selected_year,
                month=self.selected_month,
            )
        except Exception as e:
            print(f"Error loading dashboard summary: {e}")

    def load_yearly_overview(self):
        try:
            self.yearly_overview = client.get_yearly_overview(account_id=self.selected_account_id)
        except Exception as e:
            print(f"Error loading yearly overview: {e}")

    def load_pending_invitations(self):
        try:
            self.pending_invitations = client.get_pending_invitations()
        except Exception as e:
            print(f"Error loading invitations: {e}")

    async def accept_invitation(self):
        if not self.selected_invitation:
            return
        try:
            client.accept_invitation(self.selected_invitation.token)
            self.set_show_invitation_modal(False)
            self.load_pending_invitations()
            async for event in self.load_accounts():
                yield event
        except Exception as e:
            print(f"Error accepting invitation: {e}")

    async def decline_invitation(self, token: str):
        try:
            client.decline_invitation(token)
            self.load_pending_invitations()
            yield
        except Exception as e:
            print(f"Error declining invitation: {e}")

    def navigate_to_transaction(self, account_id: int, transaction_id: int):
        return rx.redirect(f"/transaction/{account_id}/{transaction_id}")

    # --- Bank Integration Event Handlers ---
    def load_kb_connection_status(self):
        try:
            self.is_kb_connected = client.get_kb_connection_status()
        except Exception:
            self.is_kb_connected = False

    async def connect_to_bank(self):
        self.is_syncing = True
        self.error_message = ""
        try:
            client.connect_to_kb_bank()
            self.is_kb_connected = True
        except httpx.HTTPStatusError as e:
            self.error_message = f"Failed to connect: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            self.error_message = f"An unexpected error occurred: {str(e)}"
        finally:
            self.is_syncing = False
            yield
