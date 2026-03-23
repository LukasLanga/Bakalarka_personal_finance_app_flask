import reflex as rx
import httpx
import asyncio
from .base_state import BaseState
from ..api.client import API_URL

class ForgotPasswordState(BaseState):
    """State for the forgot password form."""
    email: str = ""
    is_loading: bool = False
    message: str = ""
    is_error: bool = False

    def on_load_reset(self):
        self.email = ""
        self.is_loading = False
        self.message = ""
        self.is_error = False

    async def handle_submit(self):
        if not self.email:
            self.is_error = True
            self.message = self.translations["Email is required"]
            return

        self.is_loading = True
        self.message = ""
        self.is_error = False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{API_URL}/forgot-password", json={"email": self.email})
                response.raise_for_status()
                self.message = self.translations["if_account_exists"]
        except httpx.HTTPStatusError as e:
            try:
                self.message = e.response.json().get("ERROR", "An unknown error occurred.")
            except:
                self.message = f"Error: {e.response.status_code} - Could not process the request."
            self.is_error = True
        except Exception as e:
            self.message = f"An unexpected error occurred: {str(e)}"
            self.is_error = True
        finally:
            self.is_loading = False

class ResetPasswordState(BaseState):
    """State for the reset password form."""
    password: str = ""
    confirm_password: str = ""
    is_loading: bool = False
    message: str = ""
    is_error: bool = False

    def on_load_reset(self):
        self.password = ""
        self.confirm_password = ""
        self.is_loading = False
        self.message = ""
        self.is_error = False

    async def handle_submit(self):
        if not self.password or not self.confirm_password:
            self.is_error = True
            self.message = self.translations["All fields are required."]
            return
            
        if self.password != self.confirm_password:
            self.is_error = True
            self.message = self.translations["password_mismatch"]
            return

        self.is_loading = True
        self.message = ""
        self.is_error = False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{API_URL}/reset-password/{self.token}", json={"password": self.password})
                response.raise_for_status()
                self.message = self.translations["password_reset_success"]
                await asyncio.sleep(3)
                return rx.redirect("/login")
        except httpx.HTTPStatusError as e:
            try:
                self.message = e.response.json().get("ERROR", "An unknown error occurred.")
            except:
                 self.message = f"Error: {e.response.status_code} - Could not process the request."
            self.is_error = True
        except Exception as e:
            self.message = f"An unexpected error occurred: {str(e)}"
            self.is_error = True
        finally:
            self.is_loading = False
