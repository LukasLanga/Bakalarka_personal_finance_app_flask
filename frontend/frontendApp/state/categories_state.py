import reflex as rx
from typing import List
from ..models.models import Category
from .base_state import BaseState
from ..api import client

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
    category_to_delete_id: int | None = None

    def reset_form(self):
        self.new_category_name = ""
        self.new_category_type = "Expense"
        self.error_message = ""

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
            self.categories = client.list_categories(self.get_http_client())
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

    def toggle_add_category_modal(self, open: bool | None = None):
        if open is None:
            self.show_add_category_modal = not self.show_add_category_modal
        else:
            self.show_add_category_modal = open
        if not self.show_add_category_modal:
            self.reset_form()

    def open_delete_confirmation(self, category_id: int):
        self.show_delete_confirmation = True
        self.category_to_delete_id = category_id

    def close_delete_confirmation(self):
        self.show_delete_confirmation = False
        self.category_to_delete_id = None

    async def create_category(self):
        if not self.new_category_name:
            self.error_message = "Category name cannot be empty."
            return

        try:
            client.create_category(self.get_http_client(), self.new_category_name, self.new_category_type.lower())
            self.toggle_add_category_modal(False)
            await self.load_categories()
        except Exception as e:
            self.error_message = f"Failed to create category: {e}"

    async def delete_category(self):
        if self.category_to_delete_id is None:
            self.error_message = "No category selected for deletion."
            return
        try:
            client.delete_category(self.get_http_client(), self.category_to_delete_id)
            self.close_delete_confirmation()
            await self.load_categories()
        except Exception as e:
            self.error_message = f"Failed to delete category: {e}"
