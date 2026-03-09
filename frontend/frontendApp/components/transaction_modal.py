import reflex as rx
from ..state import DashboardState, TransactionFormState

def transaction_modal() -> rx.Component:
    """A modal to add a new transaction."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(DashboardState.translations["Add New Transaction"], size="6", margin_bottom="4px"),
            rx.dialog.description(
                DashboardState.translations["Enter the details of your transaction below."],
                size="2",
                margin_bottom="20px",
                color_scheme="gray",
            ),
            rx.flex(
                # Left Column: Basic Info
                rx.vstack(
                    rx.text(DashboardState.translations["General Information"], weight="bold", size="2"),
                    rx.text(DashboardState.translations["Name"], size="1", margin_bottom="-8px", color_scheme="gray"),
                    rx.input(
                        placeholder=DashboardState.translations["Transaction Name"],
                        on_change=TransactionFormState.set_name,
                        width="100%",
                    ),
                    rx.text(DashboardState.translations["Description"], size="1", margin_bottom="-8px", color_scheme="gray"),
                    rx.input(
                        placeholder=DashboardState.translations["Description"],
                        on_change=TransactionFormState.set_description,
                        width="100%",
                    ),
                    rx.text(DashboardState.translations["Date"], size="1", margin_bottom="-8px", color_scheme="gray"),
                    rx.input(
                        placeholder=DashboardState.translations["Date"],
                        on_change=TransactionFormState.set_date,
                        type="date",
                        default_value=TransactionFormState.date,
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                # Right Column: Financial Details
                rx.vstack(
                    rx.text(DashboardState.translations["Financial Details"], weight="bold", size="2"),
                    rx.text(DashboardState.translations["Amount"], size="1", margin_bottom="-8px", color_scheme="gray"),
                    rx.input(
                        rx.input.slot(
                            rx.text(TransactionFormState.currency, size="1", weight="bold")
                        ),
                        placeholder="0.00",
                        on_change=TransactionFormState.set_amount,
                        type="number",
                        width="100%",
                    ),
                    rx.text(DashboardState.translations["Account"], size="1", margin_bottom="-8px", color_scheme="gray"),
                    rx.select(
                        DashboardState.account_names,
                        placeholder=DashboardState.translations["Select Account"],
                        value=TransactionFormState.account_name,
                        on_change=TransactionFormState.set_account_name,
                        width="100%",
                    ),
                    rx.text(DashboardState.translations["Category"], size="1", margin_bottom="-8px", color_scheme="gray"),
                    rx.select(
                        DashboardState.category_names,
                        placeholder=DashboardState.translations["Select Category"],
                        value=TransactionFormState.category_name,
                        on_change=TransactionFormState.set_category_name,
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                spacing="6",
                flex_direction=["column", "row"], # Stack on mobile, row on desktop
                width="100%",
            ),
            rx.cond(
                TransactionFormState.error_message != "",
                rx.callout.root(
                    rx.callout.icon(rx.icon("triangle_alert")),
                    rx.callout.text(TransactionFormState.error_message),
                    color_scheme="red",
                    margin_top="16px",
                    width="100%",
                ),
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        DashboardState.translations["Cancel"],
                        on_click=DashboardState.toggle_transaction_modal,
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.button(
                    DashboardState.translations["Save Transaction"],
                    on_click=TransactionFormState.handle_submit(DashboardState.accounts, DashboardState.categories),
                    is_loading=TransactionFormState.is_loading,
                ),
                spacing="3",
                justify="end",
                margin_top="24px",
            ),
            max_width="800px", # Increased width for a better layout
        ),
        open=DashboardState.show_transaction_modal,
    )
