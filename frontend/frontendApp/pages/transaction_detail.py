import reflex as rx
from ..state import DashboardState, TransactionDetailState
from ..components.sidebar import sidebar
from ..components.topbar import topbar
from ..components.transaction_modal import transaction_modal
from ..components.account_modal import account_modal
from ..components.manage_accounts_modal import manage_accounts_modal
from ..styles import TEXT_COLOR, SUBTLE_TEXT_COLOR, PRIMARY_COLOR, BORDER_COLOR

@rx.page(route="/transaction/[account_id]/[transaction_id]", on_load=TransactionDetailState.get_transaction_detail)
def transaction_detail() -> rx.Component:
    can_edit = (TransactionDetailState.current_user_role == "editor") | (TransactionDetailState.current_user_role == "manager") | (TransactionDetailState.current_user_role == "owner")

    return rx.box(
        topbar(),
        rx.hstack(
            sidebar(),
            rx.box(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.link(
                            rx.hstack(
                                rx.icon("arrow_left", size=20),
                                rx.text(TransactionDetailState.translations["Back"], weight="medium"),
                                align="center",
                                spacing="2",
                                color=SUBTLE_TEXT_COLOR,
                            ),
                            href="/",
                        ),
                        rx.spacer(),
                        width="100%",
                        padding_bottom="20px",
                    ),
                    
                    rx.cond(
                        TransactionDetailState.is_loading,
                        rx.center(rx.spinner(), width="100%", height="50vh"),
                        rx.cond(
                            TransactionDetailState.transaction,
                            rx.card(
                                rx.vstack(
                                    rx.cond(
                                        ~TransactionDetailState.is_editing,
                                        rx.hstack(
                                            rx.hstack(
                                                rx.box(
                                                    rx.icon("receipt", size=32, color=PRIMARY_COLOR),
                                                    bg=rx.color("blue", 3),
                                                    padding="16px",
                                                    border_radius="12px",
                                                ),
                                                rx.vstack(
                                                    rx.heading(TransactionDetailState.transaction.name, size="6"),
                                                    spacing="1",
                                                ),
                                                align="center",
                                                spacing="4",
                                            ),
                                            rx.spacer(),
                                            rx.heading(
                                                f"${TransactionDetailState.transaction.amount:,.2f} {TransactionDetailState.transaction.currency}",
                                                size="8",
                                                color=rx.cond(TransactionDetailState.transaction.amount < 0, "red", "green"),
                                            ),
                                            width="100%",
                                            align="center",
                                            padding_bottom="32px",
                                            border_bottom=f"1px solid {BORDER_COLOR}",
                                        ),
                                    ),

                                    rx.cond(
                                        ~TransactionDetailState.is_editing,
                                        # Details (View Mode)
                                        rx.grid(
                                            rx.vstack(
                                                rx.text(TransactionDetailState.translations["Account"], weight="bold", color=rx.color("gray", 12)),
                                                rx.text(TransactionDetailState.account_name, color=SUBTLE_TEXT_COLOR),
                                                spacing="1",
                                            ),
                                            rx.vstack(
                                                rx.text(TransactionDetailState.translations["Date"], weight="bold", color=TEXT_COLOR),
                                                rx.text(rx.moment(TransactionDetailState.transaction.date, format="DD MMMM YYYY"), color=SUBTLE_TEXT_COLOR),
                                                spacing="1",
                                            ),
                                            rx.vstack(
                                                rx.text(TransactionDetailState.translations["Category"], weight="bold", color=TEXT_COLOR),
                                                rx.badge(TransactionDetailState.category_name, variant="soft"),
                                                spacing="1",
                                            ),
                                            rx.vstack(
                                                rx.text(TransactionDetailState.translations["Description"], weight="bold", color=TEXT_COLOR),
                                                rx.text(TransactionDetailState.transaction.description, color=SUBTLE_TEXT_COLOR),
                                                spacing="1",
                                            ),
                                            columns="2",
                                            gap="6",
                                            width="100%",
                                            padding_y="32px",
                                        ),
                                        # Details (Edit Mode)
                                        rx.flex(
                                            rx.vstack(
                                                rx.text(TransactionDetailState.translations["General Information"], weight="bold", size="2", color=rx.color("gray", 12)),
                                                rx.text(TransactionDetailState.translations["Name"], size="1", margin_bottom="-8px", color=rx.color("gray", 11)),
                                                rx.input(
                                                    value=TransactionDetailState.edit_name,
                                                    on_change=TransactionDetailState.set_edit_name,
                                                    placeholder=TransactionDetailState.translations["Transaction Name"],
                                                    width="100%",
                                                    color_scheme="gray",
                                                    variant="surface",
                                                ),
                                                rx.text(TransactionDetailState.translations["Description"], size="1", margin_bottom="-8px", color=rx.color("gray", 11)),
                                                rx.input(
                                                    value=TransactionDetailState.edit_description,
                                                    on_change=TransactionDetailState.set_edit_description,
                                                    placeholder=TransactionDetailState.translations["Description"],
                                                    width="100%",
                                                    color_scheme="gray",
                                                    variant="surface",
                                                ),
                                                rx.text(TransactionDetailState.translations["Date"], size="1", margin_bottom="-8px", color=rx.color("gray", 11)),
                                                rx.input(
                                                    value=TransactionDetailState.edit_date,
                                                    on_change=TransactionDetailState.set_edit_date,
                                                    type="date",
                                                    width="100%",
                                                    color_scheme="gray",
                                                    variant="surface",
                                                ),
                                                spacing="4",
                                                width="100%",
                                            ),
                                            rx.vstack(
                                                rx.text(TransactionDetailState.translations["Financial Details"], weight="bold", size="2", color=rx.color("gray", 12)),
                                                rx.text(TransactionDetailState.translations["Amount"], size="1", margin_bottom="-8px", color=rx.color("gray", 11)),
                                                rx.input(
                                                    value=TransactionDetailState.edit_amount.to_string(),
                                                    on_change=TransactionDetailState.set_edit_amount,
                                                    type="number",
                                                    placeholder=TransactionDetailState.translations["Amount"],
                                                    width="100%",
                                                    color_scheme="gray",
                                                    variant="surface",
                                                ),
                                                rx.text(TransactionDetailState.translations["Category"], size="1", margin_bottom="-8px", color=rx.color("gray", 11)),
                                                rx.select.root(
                                                    rx.select.trigger(
                                                        placeholder=TransactionDetailState.translations["Select Category"],
                                                        width = "100%"
                                                    ),
                                                    rx.select.content(
                                                        rx.foreach(
                                                            DashboardState.category_options, # Using category_options
                                                            lambda option: rx.select.item(option["label"], value=option["value"])
                                                        )
                                                    ),
                                                    value=TransactionDetailState.edit_category_name,
                                                    on_change=TransactionDetailState.set_edit_category_name,
                                                    width="100%",
                                                    color_scheme="gray",
                                                    variant="surface",
                                                ),
                                                spacing="4",
                                                width="100%",
                                            ),
                                            spacing="6",
                                            flex_direction=["column", "row"],
                                            width="100%",
                                            padding_y="32px",
                                        ),
                                    ),
                                    rx.cond(
                                        TransactionDetailState.error_message != "",
                                        rx.callout.root(
                                            rx.callout.icon(rx.icon("triangle_alert")),
                                            rx.callout.text(TransactionDetailState.error_message),
                                            color_scheme="red",
                                            margin_top="16px",
                                            width="100%",
                                        ),
                                    ),

                                    # Footer
                                    rx.hstack(
                                        rx.spacer(),
                                        rx.cond(
                                            TransactionDetailState.is_editing,
                                            rx.hstack(
                                                rx.button(TransactionDetailState.translations["Cancel"], on_click=TransactionDetailState.toggle_edit_mode, variant="soft", color_scheme="gray"),
                                                rx.button(TransactionDetailState.translations["Save"], on_click=TransactionDetailState.save_changes, variant="solid", color_scheme="blue"),
                                                spacing="3",
                                            ),
                                            rx.cond(
                                                can_edit,
                                                rx.hstack(
                                                    rx.button(TransactionDetailState.translations["Edit"], on_click=TransactionDetailState.toggle_edit_mode, variant="soft", color_scheme="blue"),
                                                    rx.button(TransactionDetailState.translations["Delete"], on_click=TransactionDetailState.delete_transaction, variant="soft", color_scheme="red"),
                                                    spacing="3",
                                                )
                                            ),
                                        ),
                                        width="100%",
                                        padding_top="20px",
                                        border_top=f"1px solid {BORDER_COLOR}",
                                    ),
                                    width="100%",
                                ),
                                size="4",
                                width="100%",
                                max_width="800px",
                            ),
                            rx.text(TransactionDetailState.translations["Transaction not found."]),
                        )

                    ),
                    spacing="5",
                    padding="2em",
                    width="100%",
                    align="center",
                ),
                padding_top="80px", # Adjust for topbar
                margin_left=["0", "0", "288px", "288px", "288px"],
                width=["100%", "100%", "calc(100% - 288px)", "calc(100% - 288px)", "calc(100% - 288px)"],
            ),
            align_items="flex-start",
        ),
        transaction_modal(),
        account_modal(),
        manage_accounts_modal(),
        background_color="#F6F8F6",
        min_height="100vh",
    )
