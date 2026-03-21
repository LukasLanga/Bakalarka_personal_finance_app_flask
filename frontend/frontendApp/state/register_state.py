import reflex as rx
import httpx
from .base_state import BaseState
from ..api import client

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
            if client.register(self.get_http_client(), self.username, self.email, self.password):
                if client.login(self.get_http_client(), self.email, self.password):
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
