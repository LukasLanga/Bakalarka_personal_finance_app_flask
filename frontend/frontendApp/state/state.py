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

class DashboardState(BaseState):
    """State for the main dashboard."""
    summary: DashboardSummary | None = None
    accounts: List[Account] = []
    pending_invitations: List[Invitation] = []
    is_loading: bool = False
    @rx.var
    def pending_invitations_count(self) -> int:
        return len(self.pending_invitations)

    def load_dashboard_data(self):
        """Load all data needed for the dashboard."""
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

        self.is_loading = True
        try:
            self.summary = client.get_dashboard_summary()
            self.accounts = client.get_accounts()
        except Exception as e:
            print(f"Error loading dashboard: {e}")
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
