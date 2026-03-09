import reflex as rx
from ..state import BaseState, CategoriesState, DashboardState
from ..components.sidebar import sidebar
from ..components.topbar import topbar
from ..components.transaction_modal import transaction_modal
from ..components.account_modal import account_modal
from ..components.manage_accounts_modal import manage_accounts_modal
from ..components.invitation_modal import invitation_modal
from ..styles import TEXT_COLOR, SUBTLE_TEXT_COLOR, BORDER_COLOR

def add_category_modal() -> rx.Component:
    """A modal to add a new category."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(CategoriesState.translations["Add New Category"]),
            rx.dialog.description(
                CategoriesState.translations["Enter the details for the new category."],
            ),
            rx.vstack(
                rx.text(CategoriesState.translations["Category Name"], weight="bold"),
                rx.input(
                    placeholder=CategoriesState.translations["e.g. Groceries"],
                    value=CategoriesState.new_category_name,
                    on_change=CategoriesState.set_new_category_name,
                ),
                rx.text(CategoriesState.translations["Category Type"], weight="bold"),
                rx.segmented_control.root(
                    rx.segmented_control.item(CategoriesState.translations["Expense"], value="Expense"),
                    rx.segmented_control.item(CategoriesState.translations["Income"], value="Income"),
                    value=CategoriesState.new_category_type,
                    on_change=CategoriesState.set_new_category_type,
                ),
                spacing="4",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(CategoriesState.translations["Cancel"], on_click=lambda: CategoriesState.toggle_add_category_modal(False), variant="soft", color_scheme="gray")
                ),
                rx.button(CategoriesState.translations["Add Category"], on_click=CategoriesState.create_category, color_scheme="green"),
                spacing="3",
                justify="end",
                margin_top="16px",
            ),
        ),
        open=CategoriesState.show_add_category_modal,
        on_open_change=CategoriesState.toggle_add_category_modal,
    )

@rx.page(route="/categories", on_load=CategoriesState.load_categories)
def categories() -> rx.Component:
    return rx.box(
        topbar(),
        rx.hstack(
            sidebar(),
            rx.box(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.vstack(
                            rx.heading(CategoriesState.translations["Categories"], size="8"),
                            rx.text(CategoriesState.translations["Manage your expense and income categories."], color=SUBTLE_TEXT_COLOR),
                            align="start",
                            spacing="1",
                        ),
                        rx.spacer(),
                        width="100%",
                    ),
                    
                    # Filters and Add Button
                    rx.hstack(
                        rx.tabs.root(
                            rx.tabs.list(
                                rx.tabs.trigger(CategoriesState.translations["All"], value="all"),
                                rx.tabs.trigger(CategoriesState.translations["Expenses"], value="expense"),
                                rx.tabs.trigger(CategoriesState.translations["Income"], value="income"),
                            ),
                            on_change=CategoriesState.set_filter_type,
                            default_value="all",
                        ),
                        rx.spacer(),
                        rx.button(CategoriesState.translations["Add Category"], on_click=lambda: CategoriesState.toggle_add_category_modal(True), color_scheme="green", size="3"),
                        width="100%",
                        justify="between",
                    ),

                    # Categories Table
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell(CategoriesState.translations["Name"]),
                                    rx.table.column_header_cell(CategoriesState.translations["Type"]),
                                    rx.table.column_header_cell(CategoriesState.translations["Usage Count"]),
                                    rx.table.column_header_cell(CategoriesState.translations["Actions"], text_align="right"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    CategoriesState.filtered_categories,
                                    lambda cat: rx.table.row(
                                        rx.table.cell(cat.name),
                                        rx.table.cell(rx.badge(cat.type.capitalize(), color_scheme=rx.cond(cat.type == "income", "blue", "red"))),
                                        rx.table.cell(cat.usage_count),
                                        rx.table.cell(
                                            rx.button(
                                                rx.icon("trash-2", size=16),
                                                on_click=CategoriesState.open_delete_confirmation(cat.name),
                                                size="1",
                                                color_scheme="red",
                                                variant="soft",
                                            ),
                                            text_align="right",
                                        ),
                                    )
                                )
                            ),
                            variant="surface",
                            size="2",
                        ),
                        width="100%",
                        border=f"1px solid {BORDER_COLOR}",
                        border_radius="12px",
                        overflow="hidden",
                    ),

                    spacing="5",
                    padding="2em",
                    width="100%",
                ),
                padding_top="80px", # Adjust for topbar
                margin_left=["0", "0", "288px", "288px", "288px"],
                width=["100%", "100%", "calc(100% - 288px)", "calc(100% - 288px)", "calc(100% - 288px)"],
            ),
            align_items="flex-start",
        ),
        add_category_modal(),
        transaction_modal(),
        account_modal(),
        manage_accounts_modal(),
        invitation_modal(),
        # Delete Category Confirmation
        rx.alert_dialog.root(
            rx.alert_dialog.content(
                rx.alert_dialog.title(CategoriesState.translations["Delete Category"]),
                rx.alert_dialog.description(
                    CategoriesState.translations["Are you sure you want to delete this category? This action cannot be undone."]
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        rx.button(CategoriesState.translations["Cancel"], on_click=CategoriesState.close_delete_confirmation, variant="soft", color_scheme="gray")
                    ),
                    rx.alert_dialog.action(
                        rx.button(CategoriesState.translations["Delete"], color_scheme="red", on_click=CategoriesState.delete_category)
                    ),
                    spacing="3",
                    justify="end",
                    margin_top="16px",
                ),
            ),
            open=CategoriesState.show_delete_confirmation,
        ),
        background_color="#F6F8F6",
        min_height="100vh",
    )
