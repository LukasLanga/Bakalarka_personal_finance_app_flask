import reflex as rx
from ..models.models import User, Account, DashboardSummary, Category, Transaction, Invitation, AccountUser
from ..api import client
import httpx
from typing import List

class BaseState(rx.State):
    """Global state for authentication."""
    is_authenticated: bool = False
    logged_in_user: User | None = None
    locale: str = "en"

    @rx.var
    def translations(self) -> dict:
        """The translations for the current locale."""
        return TRANSLATIONS.get(self.locale, TRANSLATIONS["en"])

    async def check_auth(self):
        """A placeholder auth check."""
        public_routes = {"/login", "/register"}
        try:
            if self.is_authenticated:
                return self.on_auth_success()
            
            self.logged_in_user = client.get_current_user()
            if not self.is_authenticated:
                self.logged_in_user = client.get_current_user()
            self.is_authenticated = True
        except (httpx.HTTPStatusError, Exception):
            self.is_authenticated = False
            if self.router.page.path not in public_routes:
                return rx.redirect("/login")
            current_path = self.router.page.raw_path
            if current_path not in public_routes:
                yield rx.redirect("/login")

    def set_locale(self, lang: str):
        self.locale = lang
        return rx.redirect(self.router.page.raw_path)

    def logout(self):
        self.is_authenticated = False
        self.logged_in_user = None
        return rx.redirect("/login")

    def on_auth_success(self):
        """
        A placeholder event that can be overridden by child states
        to load data after a successful authentication check.
        """
        return
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

class DashboardState(BaseState):
    """State for the main dashboard."""
    summary: DashboardSummary | None = None
    accounts: List[Account] = []
    pending_invitations: List[Invitation] = []
    is_loading: bool = False
    is_sidebar_collapsed: bool = True
    @rx.var
    def pending_invitations_count(self) -> int:
        return len(self.pending_invitations)

    def load_dashboard_data(self):
        """Load all data needed for the dashboard."""

    def toggle_sidebar(self):
        self.is_sidebar_collapsed = not self.is_sidebar_collapsed

    async def handle_manage_modal_change(self, open: bool):
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

    def on_auth_success(self):
        """
        This overrides the base method. It is called by check_auth
        after a successful authentication.
        """
        return self.load_dashboard_data

class LoginState(BaseState):
    """State for the login form."""
    email: str
    password: str
    error_message: str = ""
    is_loading: bool = False
    show_password: bool = False

    def set_email(self, value: str):
        self.email = value

    def set_password(self, value: str):
        self.password = value

    def toggle_show_password(self):
        self.show_password = not self.show_password

    async def handle_login(self):
        self.error_message = ""
        if not self.email or not self.password:
            self.error_message = self.translations["Email and password are required."]
            return
        self.is_loading = True
        try:
            if client.login(self.email, self.password):
                yield rx.redirect("/")
        except httpx.HTTPStatusError:
            self.error_message = "Invalid email or password."
        except Exception as e:
            self.error_message = f"An unexpected error occurred: {e}"
        finally:
            self.is_loading = False
            self.password = ""

class RegisterState(BaseState):
    """State for the registration form."""
    username: str
    email: str
    password: str
    confirm_password: str
    error_message: str = ""
    is_loading: bool = False
    show_password: bool = False
    show_confirm_password: bool = False

    def set_username(self, value: str):
        self.username = value

    def set_email(self, value: str):
        self.email = value

    def set_password(self, value: str):
        self.password = value

    def set_confirm_password(self, value: str):
        self.confirm_password = value

    def toggle_show_password(self):
        self.show_password = not self.show_password

    def toggle_show_confirm_password(self):
        self.show_confirm_password = not self.show_confirm_password

    async def handle_registration(self):
        self.error_message = ""
        if not self.username or not self.email or not self.password or not self.confirm_password:
            self.error_message = "All fields are required."
            return
        if self.password != self.confirm_password:
            self.error_message = "Passwords do not match."
            return
        self.is_loading = True
        try:
            if client.register(self.username, self.email, self.password):
                if client.login(self.email, self.password):
                    yield rx.redirect("/")
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json().get("ERROR", "Registration failed.")
                self.error_message = error_detail
            except:
                self.error_message = "An unknown registration error occurred."
        except Exception as e:
            self.error_message = f"An unexpected error occurred: {e}"
        finally:
            self.is_loading = False
            self.password = ""
            self.confirm_password = ""

class CategoriesState(BaseState):
    """State for the categories page."""
    categories: List[Category] = []
    new_category_name: str = ""
    new_category_type: str = "Expense"
    is_loading: bool = False
    error_message: str = ""
    filter_type: str = "all"
    show_add_category_modal: bool = False
    show_delete_confirmation: bool = False
    category_to_delete_name: str = ""

    @rx.var
    def filtered_categories(self) -> List[Category]:
        if self.filter_type == "all":
            return self.categories
        return [cat for cat in self.categories if cat.type.lower() == self.filter_type.lower()]

    async def load_categories(self):
        async for event in self.check_auth():
            yield event
        
        if not self.is_authenticated:
            return

        self.is_loading = True
        try:
            self.categories = client.list_categories()
        except Exception as e:
            self.error_message = f"Error loading categories: {e}"
        finally:
            self.is_loading = False

    def set_new_category_name(self, name: str):
        self.new_category_name = name

    def set_new_category_type(self, type):
        self.new_category_type = type

    def set_filter_type(self, type: str):
        self.filter_type = type

    def toggle_add_category_modal(self):
        self.show_add_category_modal = not self.show_add_category_modal

    def open_delete_confirmation(self, name: str):
        self.show_delete_confirmation = True
        self.category_to_delete_name = name

    def close_delete_confirmation(self):
        self.show_delete_confirmation = False
        self.category_to_delete_name = ""

    async def create_category(self):
        if not self.new_category_name:
            self.error_message = "Category name cannot be empty."
            return

        try:
            client.create_category(self.new_category_name, self.new_category_type.lower())
            self.new_category_name = ""
            self.toggle_add_category_modal()
            await self.load_categories()
        except Exception as e:
            self.error_message = f"Failed to create category: {e}"

    async def delete_category(self):
        try:
            client.delete_category(self.category_to_delete_name)
            self.close_delete_confirmation()
            await self.load_categories()
        except Exception as e:
            self.error_message = f"Failed to delete category: {e}"

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
