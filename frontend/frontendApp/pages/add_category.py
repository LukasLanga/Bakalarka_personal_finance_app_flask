import reflex as rx
from ..state import BaseState
from ..api import client
from ..styles import TEXT_COLOR, SUBTLE_TEXT_COLOR, PRIMARY_COLOR, BORDER_COLOR

class AddCategoryState(BaseState):
    """State for the Add Category page."""
    category_name: str = ""
    category_type: str = "expense"
    error_message: str = ""
    is_loading: bool = False

    def set_category_name(self, name: str):
        self.category_name = name

    def set_category_type(self, type):
        self.category_type = type

    async def handle_submit(self):
        """Handle form submission to create a new category."""
        if not self.category_name:
            self.error_message = "Category name cannot be empty."
            return

        self.is_loading = True
        try:
            client.create_category(self.category_name, self.category_type)
            return rx.redirect("/categories")
        except Exception as e:
            self.error_message = f"Failed to create category: {e}"
        finally:
            self.is_loading = False

@rx.page(route="/categories/add")
def add_category() -> rx.Component:
    """The page for adding a new category."""
    return rx.box(
        rx.box(
            rx.hstack(
                rx.link(
                    rx.hstack(
                        rx.icon("arrow-left", size=20),
                        rx.text("Back to Categories"),
                        align="center",
                    ),
                    href="/categories",
                    color=SUBTLE_TEXT_COLOR,
                    underline="none",
                ),
                rx.spacer(),
                rx.heading("Create New Category", size="6"),
                rx.spacer(),
                width="100%",
            ),
            padding=["1em", "1em 2em", "1em 2.5em"],
            border_bottom=f"1px solid {BORDER_COLOR}",
            background_color="#FFFFFF",
        ),
        # Main Content
        rx.center(
            rx.card(
                rx.vstack(
                    # Header
                    rx.vstack(
                        rx.heading("Create a New Category", size="6", weight="bold"),
                        rx.text("Define a new category to better organize your spending.", color=SUBTLE_TEXT_COLOR),
                        spacing="1",
                        padding_bottom="24px",
                        border_bottom=f"1px solid #F1F5F9",
                        width="100%",
                    ),
                    # Form
                    rx.flex(
                        rx.vstack(
                            rx.text("Category Name", weight="bold", color=TEXT_COLOR),
                            rx.input(
                                placeholder="e.g. Monthly Groceries, Coffee...",
                                value=AddCategoryState.category_name,
                                on_change=AddCategoryState.set_category_name,
                                size="3",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Category Type", weight="bold", color=TEXT_COLOR),
                            rx.segmented_control.root(
                                rx.segmented_control.item("Expense", value="expense"),
                                rx.segmented_control.item("Income", value="income"),
                                value=AddCategoryState.category_type,
                                on_change=AddCategoryState.set_category_type,
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        spacing="6",
                        flex_direction=["column", "row"],
                        width="100%",
                    ),
                    # Actions
                    rx.hstack(
                        rx.button("Cancel", on_click=rx.redirect("/categories"), variant="soft", color_scheme="gray"),
                        rx.button(
                            "Create Category",
                            on_click=AddCategoryState.handle_submit,
                            is_loading=AddCategoryState.is_loading,
                            color_scheme="green",
                        ),
                        spacing="3",
                        justify="end",
                        width="100%",
                        padding_top="24px",
                        border_top=f"1px solid #F1F5F9",
                    ),
                    rx.cond(
                        AddCategoryState.error_message != "",
                        rx.callout.root(
                            rx.callout.icon(rx.icon("triangle_alert")),
                            rx.callout.text(AddCategoryState.error_message),
                            color_scheme="red",
                            margin_top="16px",
                        ),
                    ),
                    spacing="6",
                    width="100%",
                ),
                width="100%",
                max_width="800px",
            ),
            padding=["1em", "2em", "2.5em"],
            width="100%",
            height="calc(100vh - 65px)",
        ),
        background_color="#F6F8F7",
    )
