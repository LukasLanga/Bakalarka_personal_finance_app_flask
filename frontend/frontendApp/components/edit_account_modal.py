import reflex as rx
from ..state import DashboardState

def edit_account_modal() -> rx.Component:
    """A modal to edit an existing account."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Edit Account", size="6", margin_bottom="4px"),
            rx.dialog.description(
                "Update the details of your account below.",
                size="2",
                margin_bottom="20px",
                color_scheme="gray",
            ),
            rx.vstack(
                rx.text("Account Information", weight="bold", size="2"),
                rx.text("Account Name", size="1", margin_bottom="-8px", color_scheme="gray"),
                rx.input(
                    value=DashboardState.edit_account_name,
                    on_change=DashboardState.set_edit_account_name,
                    placeholder="e.g. Personal Savings",
                    width="100%",
                ),
                rx.text("Bank Name", size="1", margin_bottom="-8px", color_scheme="gray"),
                rx.input(
                    value=DashboardState.edit_account_bank_name,
                    on_change=DashboardState.set_edit_account_bank_name,
                    placeholder="e.g. Chase",
                    width="100%",
                ),
                rx.text("Currency", size="1", margin_bottom="-8px", color_scheme="gray"),
                rx.select(
                    ["EUR", "USD", "GBP", "CZK"],
                    value=DashboardState.edit_account_currency,
                    on_change=DashboardState.set_edit_account_currency,
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            rx.cond(
                DashboardState.error_message != "",
                rx.callout.root(
                    rx.callout.icon(rx.icon("triangle_alert")),
                    rx.callout.text(DashboardState.error_message),
                    color_scheme="red",
                    margin_top="16px",
                    width="100%",
                ),
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        on_click=DashboardState.close_edit_account_modal,
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button(
                        "Delete",
                        on_click=DashboardState.delete_account,
                        variant="soft",
                        color_scheme="red",
                    ),
                    rx.button(
                        "Save Changes",
                        on_click=DashboardState.save_account_changes,
                        is_loading=DashboardState.is_loading,
                    ),
                    spacing="3",
                ),
                spacing="3",
                justify="between",
                margin_top="24px",
                width="100%",
            ),
            max_width="512px",
        ),
        open=DashboardState.show_edit_account_modal,
    )
