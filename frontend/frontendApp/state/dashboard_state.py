import reflex as rx
from typing import List, Dict, Any, Optional
from ..models.models import Account, Category, DashboardSummary, Invitation
from .base_state import BaseState
from ..api import client
import httpx

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
    show_transaction_modal: bool = False
    show_account_modal: bool = False
    show_manage_accounts_modal: bool = False
    show_invitation_modal: bool = False
    selected_invitation: Optional[Invitation] = None
    is_sidebar_collapsed: bool = True
    error_message: str = ""
    selected_account_id: int | None = None

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
    def account_names(self) -> List[str]:
        return [acc.name for acc in self.accounts]

    @rx.var
    def category_names(self) -> List[str]:
        return [cat.name for cat in self.categories]

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
        if self.is_authenticated:
            async for event in self.load_accounts():
                yield event
            
            if self.selected_account_id is None and self.accounts:
                self.selected_account_id = self.accounts[0].id
            
            await self.load_user_roles()
            await self.load_dashboard_summary()
            await self.load_yearly_overview()
            await self.load_pending_invitations()

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
        await self.load_dashboard_summary()
        await self.load_yearly_overview()

    async def load_accounts(self):
        self.is_loading = True
        self.error_message = ""
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
        finally:
            self.is_loading = False

    async def load_user_roles(self):
        try:
            self.user_roles = client.get_user_roles()
        except Exception as e:
            print(f"Error loading user roles: {e}")

    def load_categories(self):
        try:
            self.categories = client.list_categories()
        except Exception as e:
            print(f"Error loading categories: {e}")

    async def load_dashboard_summary(self):
        try:
            self.dashboard_summary = client.get_dashboard_summary(account_id=self.selected_account_id)
        except Exception as e:
            print(f"Error loading dashboard summary: {e}")

    async def load_yearly_overview(self):
        try:
            self.yearly_overview = client.get_yearly_overview(account_id=self.selected_account_id)
        except Exception as e:
            print(f"Error loading yearly overview: {e}")

    async def load_pending_invitations(self):
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
            await self.load_pending_invitations()
            return self.load_accounts()
        except Exception as e:
            print(f"Error accepting invitation: {e}")

    async def decline_invitation(self, token: str):
        try:
            client.decline_invitation(token)
            await self.load_pending_invitations()
        except Exception as e:
            print(f"Error declining invitation: {e}")

    def navigate_to_transaction(self, account_id: int, transaction_id: int):
        return rx.redirect(f"/transaction/{account_id}/{transaction_id}")
