import reflex as rx
from ..models.models import User
from ..api import client
import httpx
from ..locale import TRANSLATIONS
from ..api.client import API_URL

_session_clients = {}

class BaseState(rx.State):
    """Global state for authentication."""
    is_authenticated: bool = False
    logged_in_user: User | None = None
    locale: str = "en"

    def get_http_client(self) -> httpx.Client:
        """
        Returns a session-specific httpx client.
        Uses the session token to get/create a client from a global store.
        """
        token = self.router.session.client_token
        if token not in _session_clients:
            _session_clients[token] = httpx.Client(base_url=API_URL, follow_redirects=True)
        return _session_clients[token]

    @rx.var
    def translations(self) -> dict:
        """The translations for the current locale."""
        return TRANSLATIONS.get(self.locale, TRANSLATIONS["en"])

    async def check_auth(self):
        """A placeholder auth check."""
        public_routes = {"/login", "/register", "/forgot-password", "/reset-password"}
        try:
            if not self.is_authenticated:
                self.logged_in_user = client.get_current_user(self.get_http_client())
            self.is_authenticated = True
        except (httpx.HTTPStatusError, Exception):
            self.is_authenticated = False
            current_path = self.router.page.path
            # Allow access to public routes even if not authenticated
            if not any(current_path.startswith(route) for route in public_routes):
                yield rx.redirect("/login")

    def set_locale(self, lang: str):
        self.locale = lang
        return rx.redirect(self.router.page.raw_path)

    def logout(self):
        token = self.router.session.client_token
        try:
            client.logout(self.get_http_client())
        except Exception as e:
            print(f"Error during backend logout: {e}")
        finally:
            self.is_authenticated = False
            self.logged_in_user = None
            
            # Clean up the client from the global store
            if token in _session_clients:
                _session_clients[token].close()
                del _session_clients[token]

            return rx.redirect("/login")
