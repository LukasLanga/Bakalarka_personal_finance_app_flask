import reflex as rx
from ..state import DashboardState, AccountFormState

def account_modal() -> rx.Component:
    """A modal to add a new account."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(DashboardState.translations["Add New Account"], size="6", margin_bottom="4px"),
            rx.dialog.description(
                DashboardState.translations["Enter the details of your new account below."],
                size="2",
                margin_bottom="20px",
                color_scheme="gray",
            ),
            rx.vstack(
                rx.text(DashboardState.translations["Account Information"], weight="bold", size="2"),
                rx.text(DashboardState.translations["Account Name"], size="1", margin_bottom="-8px", color_scheme="gray"),
                rx.input(
                    placeholder=DashboardState.translations["e.g. Personal Savings"],
                    on_change=AccountFormState.set_name,
                    width="100%",
                ),
                rx.text(DashboardState.translations["Bank Name"], size="1", margin_bottom="-8px", color_scheme="gray"),
                rx.input(
                    placeholder=DashboardState.translations["e.g. Chase"],
                    on_change=AccountFormState.set_bank_name,
                    width="100%",
                ),
                rx.text(DashboardState.translations["Initial Balance"], size="1", margin_bottom="-8px", color_scheme="gray"),
                rx.input(
                    placeholder="0.00",
                    on_change=AccountFormState.set_balance,
                    type="number",
                    width="100%",
                ),
                rx.text(DashboardState.translations["Currency"], size="1", margin_bottom="-8px", color_scheme="gray"),
                rx.select(
                    ["EUR", "USD", "GBP", "CZK"],
                    value=AccountFormState.currency,
                    on_change=AccountFormState.set_currency,
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            rx.cond(
                AccountFormState.error_message != "",
                rx.callout.root(
                    rx.callout.icon(rx.icon("triangle_alert")),
                    rx.callout.text(AccountFormState.error_message),
                    color_scheme="red",
                    margin_top="16px",
                    width="100%",
                ),
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        DashboardState.translations["Cancel"],
                        on_click=DashboardState.toggle_account_modal,
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.button(
                    DashboardState.translations["Create Account"],
                    on_click=AccountFormState.handle_submit,
                    is_loading=AccountFormState.is_loading,
                ),
                spacing="3",
                justify="end",
                margin_top="24px",
            ),
            max_width="512px",
        ),
        open=DashboardState.show_account_modal,
    )
