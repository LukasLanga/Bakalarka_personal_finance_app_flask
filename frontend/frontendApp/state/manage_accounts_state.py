import reflex as rx
from typing import List
from ..models.models import Account, AccountUser
from .base_state import BaseState
from .dashboard_state import DashboardState
from ..api import client

class ManageAccountsState(BaseState):
    """State for managing accounts."""
    is_editing: bool = False
    account_to_edit: Account | None = None
    account_users: List[AccountUser] = []
    edit_name: str = ""
    edit_bank_name: str = ""
    edit_currency: str = ""
    error_message: str = ""
    
    # Invitation form state
    invite_email: str = ""
    invite_role: str = "viewer"
    
    show_delete_confirmation: bool = False
    account_to_delete_id: int | None = None

    @rx.var
    def user_count(self) -> int:
        return len(self.account_users)

    @rx.var
    def current_user_role(self) -> str:
        if self.logged_in_user and self.account_users:
            for user in self.account_users:
                if user.id == self.logged_in_user.id:
                    return user.role
        return ""

    @rx.var
    def can_manage_users(self) -> bool:
        """Check if the current user can manage other users on this account."""
        return self.current_user_role in ["manager", "owner"]

    def set_edit_name(self, value: str):
        self.edit_name = value

    def set_edit_bank_name(self, value: str):
        self.edit_bank_name = value

    def set_edit_currency(self, value: str):
        self.edit_currency = value

    def set_invite_email(self, value: str):
        self.invite_email = value

    def set_invite_role(self, value: str):
        self.invite_role = value

    async def start_edit(self, account: Account):
        self.is_editing = True
        self.account_to_edit = account
        self.edit_name = account.name
        self.edit_bank_name = account.bank_name or ""
        self.edit_currency = account.currency
        await self.load_account_users()

    def cancel_edit(self):
        self.is_editing = False
        self.account_to_edit = None
        self.account_users = []
        self.edit_name = ""
        self.edit_bank_name = ""
        self.edit_currency = ""
        self.invite_email = ""
        self.invite_role = "viewer"
        self.error_message = ""

    def open_delete_confirmation(self, account_id: int):
        self.show_delete_confirmation = True
        self.account_to_delete_id = account_id

    def close_delete_confirmation(self):
        self.show_delete_confirmation = False
        self.account_to_delete_id = None

    async def load_account_users(self):
        if not self.account_to_edit:
            return
        try:
            self.account_users = client.get_account_users(self.account_to_edit.id)
        except Exception as e:
            self.error_message = f"Failed to load users: {e}"

    async def save_changes(self):
        try:
            client.update_account(
                account_id=self.account_to_edit.id,
                name=self.edit_name,
                bank_name=self.edit_bank_name,
                currency=self.edit_currency,
            )
            self.cancel_edit()
            return [DashboardState.load_accounts, DashboardState.load_dashboard_summary]
        except Exception as e:
            self.error_message = f"Failed to update account: {e}"

    async def delete_account(self):
        try:
            client.delete_account(self.account_to_delete_id)
            self.close_delete_confirmation()
            return [DashboardState.load_accounts, DashboardState.load_dashboard_summary]
        except Exception as e:
            self.error_message = f"Failed to delete account: {e}"

    async def update_user_role(self, user_id: int, role: str):
        try:
            client.update_user_role(self.account_to_edit.id, user_id, role)
            await self.load_account_users()
        except Exception as e:
            self.error_message = f"Failed to update role: {e}"

    async def remove_user(self, user_id: int):
        try:
            is_self_removal = user_id == self.logged_in_user.id
            client.remove_user_from_account(self.account_to_edit.id, user_id)
            
            if is_self_removal:
                # If user removes themselves, close the modal and refresh accounts
                return [self.cancel_edit, DashboardState.toggle_manage_accounts_modal, DashboardState.load_accounts]
            else:
                # If removing another user, just refresh the list
                await self.load_account_users()

        except Exception as e:
            self.error_message = f"Failed to remove user: {e}"

    async def invite_user(self):
        if not self.invite_email:
            self.error_message = "Email cannot be empty."
            return
        try:
            client.invite_user_to_account(
                account_id=self.account_to_edit.id,
                email=self.invite_email,
                role=self.invite_role,
            )
            self.invite_email = "" # Clear email after sending
        except Exception as e:
            self.error_message = f"Failed to send invitation: {e}"
