import reflex as rx
from ..state.add_bank_account_state import AddBankAccountState
from ..state.dashboard_state import DashboardState

def add_bank_account_modal() -> rx.Component:
    """A modal for adding a new bank account from a PSD2 connection."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title(DashboardState.translations["add_bank_account_title"]),
            rx.alert_dialog.description(
                DashboardState.translations["add_bank_account_description"]
            ),
            rx.vstack(
                rx.cond(
                    AddBankAccountState.is_loading,
                    rx.center(rx.spinner()),
                    rx.select.root(
                        rx.select.trigger(placeholder=DashboardState.translations["select_an_account_placeholder"]),
                        rx.select.content(
                            rx.foreach(
                                AddBankAccountState.available_account_options,
                                lambda option: rx.select.item(option["label"], value=option["value"])
                            )
                        ),
                        on_change=AddBankAccountState.set_selected_kb_account_id,
                        value=AddBankAccountState.selected_kb_account_id,
                    ),
                ),
                rx.cond(
                    AddBankAccountState.error_message,
                    rx.callout.root(
                        rx.callout.icon(rx.icon("triangle_alert")),
                        rx.callout.text(AddBankAccountState.error_message),
                        color_scheme="red",
                        role="alert",
                    ),
                ),
                spacing="4",
                padding_top="1em",
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(
                        DashboardState.translations["Cancel"],
                        variant="soft",
                        color_scheme="gray",
                        on_click=AddBankAccountState.close_modal(False),
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        DashboardState.translations["add_account_button"],
                        on_click=AddBankAccountState.add_selected_account,
                        loading=AddBankAccountState.is_loading,
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
        open=AddBankAccountState.show_modal,
        on_open_change=AddBankAccountState.close_modal,
    )
