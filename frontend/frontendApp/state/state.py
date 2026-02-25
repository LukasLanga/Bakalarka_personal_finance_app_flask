import reflex as rx
from ..models.models import User, Account, DashboardSummary
from ..api import client
import httpx
from typing import List

class BaseState(rx.State):
    """Global state for authentication."""
    is_authenticated: bool = False
    logged_in_user: User | None = None

    def check_auth(self):
        """
        This event is called on every page load.
        It checks if the user is authenticated and redirects if not.
        If authentication is successful, it returns an event to be handled by the page's state.
        """
        public_routes = {"/login", "/register"}
        try:
            if self.is_authenticated:
                return self.on_auth_success()
            
            self.logged_in_user = client.get_current_user()
            self.is_authenticated = True
            return self.on_auth_success()
        except (httpx.HTTPStatusError, Exception):
            self.is_authenticated = False
            if self.router.page.path not in public_routes:
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
    is_loading: bool = False

    def load_dashboard_data(self):
        """Load all data needed for the dashboard."""
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

    def handle_login(self):
        self.error_message = ""
        if not self.email or not self.password:
            self.error_message = "Email and password are required."
            return
        self.is_loading = True
        try:
            if client.login(self.email, self.password):
                self.check_auth()
                return rx.redirect("/")
        except httpx.HTTPStatusError:
            self.error_message = "Invalid email or password."
        except Exception:
            self.error_message = "An unexpected error occurred."
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

    def handle_registration(self):
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
                    self.check_auth()
                    return rx.redirect("/")
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json().get("ERROR", "Registration failed.")
                self.error_message = error_detail
            except:
                self.error_message = "An unknown registration error occurred."
        except Exception:
            self.error_message = "An unexpected error occurred."
        finally:
            self.is_loading = False
            self.password = ""
            self.confirm_password = ""
