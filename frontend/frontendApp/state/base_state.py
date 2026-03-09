import reflex as rx
from ..models.models import User
from ..api import client
import httpx
from ..locale import TRANSLATIONS

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
            if not self.is_authenticated:
                self.logged_in_user = client.get_current_user()
            self.is_authenticated = True
        except (httpx.HTTPStatusError, Exception):
            self.is_authenticated = False
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
