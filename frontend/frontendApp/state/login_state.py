import reflex as rx
import httpx
from .base_state import BaseState
from ..api import client

class LoginState(BaseState):
    """State for the login form."""
    email: str = ""
    password: str = ""
    error_message: str = ""
    is_loading: bool = False
    show_password: bool = False

    def on_load_reset(self):
        """Reset the state when the page is loaded."""
        self.email = ""
        self.password = ""
        self.error_message = ""
        self.is_loading = False
        self.show_password = False

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
            if client.login(self.get_http_client(), self.email, self.password):
                yield rx.redirect("/")
        except httpx.HTTPStatusError:
            self.error_message = self.translations["Invalid email or password."]
        except Exception as e:
            self.error_message = f"An unexpected error occurred: {e}"
        finally:
            self.is_loading = False
            self.password = ""
