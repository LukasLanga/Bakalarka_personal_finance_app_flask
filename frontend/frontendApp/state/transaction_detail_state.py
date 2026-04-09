import reflex as rx
from datetime import datetime
from ..models.models import Transaction
from .base_state import BaseState
from .dashboard_state import DashboardState
from ..api import client

class TransactionDetailState(BaseState):
    """State for the transaction detail page."""
    transaction: Transaction | None = None
    account_name: str = ""
    category_name: str = ""
    is_loading: bool = False
    error_message: str = ""
    current_user_role: str = ""
    
    # Edit mode state
    is_editing: bool = False
    edit_name: str = ""
    edit_amount: float = 0.0
    edit_date: str = ""
    edit_description: str = ""
    edit_category_id: str = ""

    def set_edit_name(self, value: str):
        self.edit_name = value

    def set_edit_amount(self, value: str):
        try:
            self.edit_amount = float(value) if value else 0.0
        except ValueError:
            self.error_message = self.translations["Invalid amount. Please enter a number."]

    def set_edit_date(self, value: str):
        self.edit_date = value

    def set_edit_description(self, value: str):
        self.edit_description = value

    def set_edit_category_id(self, value: str):
        self.edit_category_id = value

    async def get_transaction_detail(self):
        """Fetch transaction details based on URL params."""
        self.is_editing = False
        self.error_message = ""
        self.transaction = None

        async for event in self.check_auth():
            yield event
        
        if not self.is_authenticated:
            return

        self.is_loading = True
        try:
            account_id = int(self.router.page.params.get("account_id", 0))
            transaction_id = int(self.router.page.params.get("transaction_id", 0))
            
            if not account_id or not transaction_id:
                self.error_message = "Missing transaction or account ID."
                return

            self.transaction = client.get_transaction(self.get_http_client(), account_id, transaction_id)
            
            # Fetch account name
            accounts = client.get_accounts(self.get_http_client())
            account = next((acc for acc in accounts if acc.id == account_id), None)
            self.account_name = account.name if account else "Unknown Account"

            # Fetch category name
            if self.transaction.category_id:
                categories = client.list_categories(self.get_http_client())
                category = next((cat for cat in categories if cat.id == self.transaction.category_id), None)
                self.category_name = category.name if category else "Uncategorized"
            else:
                self.category_name = "Uncategorized"

            # Fetch user role for this account
            users = client.get_account_users(self.get_http_client(), account_id)
            current_user_access = next((u for u in users if u.id == self.logged_in_user.id), None)
            if current_user_access:
                self.current_user_role = current_user_access.role

        except Exception as e:
            self.error_message = f"Error loading transaction: {e}"
        finally:
            self.is_loading = False

    def toggle_edit_mode(self):
        self.is_editing = not self.is_editing
        if self.is_editing and self.transaction:
            self.edit_name = self.transaction.name
            self.edit_amount = self.transaction.amount
            
            if self.transaction.date:
                date_str = str(self.transaction.date)
                try:
                    parsed_date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
                    self.edit_date = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    try:
                        parsed_date = datetime.fromisoformat(date_str)
                        self.edit_date = parsed_date.strftime("%Y-%m-%d")
                    except ValueError:
                        self.edit_date = date_str[:10]
            else:
                self.edit_date = ""

            self.edit_description = self.transaction.description or ""
            self.edit_category_id = str(self.transaction.category_id) if self.transaction.category_id else ""
            return DashboardState.load_categories
        return

    async def save_changes(self):
        self.is_loading = True
        self.error_message = ""

        try:
            # Validation checks
            if not self.edit_name.strip():
                self.error_message = self.translations["Transaction name cannot be empty."]
                self.is_loading = False
                return

            if self.edit_amount == 0.0:
                self.error_message = self.translations["Transaction amount cannot be zero."]
                self.is_loading = False
                return

            if not self.edit_category_id:
                self.error_message = self.translations["Please select a valid category."]
                self.is_loading = False
                return
            
            category_id_int = int(self.edit_category_id)

            updated_transaction = client.update_transaction(
                self.get_http_client(),
                transaction_id=self.transaction.id,
                account_id=self.transaction.account_id,
                name=self.edit_name,
                amount=self.edit_amount,
                date=self.edit_date,
                description=self.edit_description,
                category_id=category_id_int
            )
            
            self.transaction = updated_transaction
            categories = client.list_categories(self.get_http_client())
            selected_category = next((cat for cat in categories if cat.id == category_id_int), None)
            self.category_name = selected_category.name if selected_category else "Uncategorized"

            self.is_editing = False
            
            return [DashboardState.load_dashboard_summary]

        except Exception as e:
            self.error_message = f"Failed to update transaction: {e}"
        finally:
            self.is_loading = False

    async def delete_transaction(self):
        if not self.transaction:
            return None

        self.is_loading = True
        try:
            client.delete_transaction(self.get_http_client(), self.transaction.account_id, self.transaction.id)
            return [DashboardState.load_dashboard_summary, rx.redirect("/")]
        except Exception as e:
            self.error_message = f"Failed to delete transaction: {e}"
            self.is_loading = False
