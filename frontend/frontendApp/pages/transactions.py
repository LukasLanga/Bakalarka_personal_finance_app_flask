import reflex as rx
from ..state.state import BaseState, DashboardState, TransactionsState
from ..api import client
from ..models.models import Transaction, Account, Category
from ..components.sidebar import sidebar
from ..components.topbar import topbar
from ..components.transaction_modal import transaction_modal
from ..components.account_modal import account_modal
from ..components.manage_accounts_modal import manage_accounts_modal
from ..components.invitation_modal import invitation_modal
from ..styles import TEXT_COLOR, SUBTLE_TEXT_COLOR, BORDER_COLOR

def transaction_row(transaction: Transaction) -> rx.Component:
    """A single row for the transactions table."""
    detail_url = "/transaction/" + transaction.account_id.to_string() + "/" + transaction.id.to_string()

    return rx.table.row(
        rx.table.row_header_cell(
            rx.link(
                rx.text(transaction.name, weight="bold", color=TEXT_COLOR, size="2"),
                href=detail_url,
                underline="none",
                color="inherit",
                width="100%",
                display="block",
                padding_y="16px",
            )
        ),
        rx.table.cell(
            rx.link(
                rx.text(
                    TransactionsState.account_id_to_name[transaction.account_id.to_string()],
                    size="2",
                    color=SUBTLE_TEXT_COLOR
                ),
                href=detail_url,
                underline="none",
                color="inherit",
                width="100%",
                display="block",
                padding_y="16px",
            ),
            vertical_align="middle",
        ),
        rx.table.cell(
            rx.link(
                rx.box(
                    rx.text(rx.moment(transaction.date, format="DD MMMM YYYY"), size="2", weight="medium", color=SUBTLE_TEXT_COLOR),
                    bg="#F1F5F9",
                    padding="4px 8px",
                    border_radius="4px",
                    display="inline-block",
                ),
                href=detail_url,
                underline="none",
                color="inherit",
                width="100%",
                display="block",
                padding_y="16px",
            ),
            vertical_align="middle",
        ),
        rx.table.cell(
            rx.link(
                rx.text(
                    f"{transaction.amount:,.2f} {transaction.currency}",
                    weight="bold",
                    color=rx.cond(transaction.amount < 0, "#E11D48", "#059669"),
                    align="right",
                ),
                href=detail_url,
                underline="none",
                color="inherit",
                width="100%",
                display="block",
                padding_y="16px",
            ),
            vertical_align="middle",
        ),
        _hover={"background_color": "#F8FAFC"},
        border_bottom=f"1px solid {BORDER_COLOR}",
    )

@rx.page(route="/transactions", on_load=TransactionsState.load_data)
def transactions() -> rx.Component:
    return rx.box(
        topbar(),
        rx.hstack(
            sidebar(),
            rx.box(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.icon(
                            "menu",
                            size=24,
                            on_click=DashboardState.toggle_sidebar,
                            display=["block", "block", "none", "none", "none"],
                            cursor="pointer",
                        ),
                        rx.vstack(
                            rx.heading(TransactionsState.translations["Transactions"], size="8"),
                            rx.text(TransactionsState.translations["View and manage all your transactions."], color=SUBTLE_TEXT_COLOR),
                            align="start",
                            spacing="1",
                        ),
                        rx.spacer(),
                        align_center=True,
                        spacing="4",
                        width="100%",
                    ),
                    
                    # Filters and Search
                    rx.card(
                        rx.hstack(
                            rx.input(
                                rx.input.slot(rx.icon("search", size=16, color=SUBTLE_TEXT_COLOR)),
                                placeholder=TransactionsState.translations["Search by name or description"],
                                value=TransactionsState.search_query,
                                on_change=TransactionsState.set_search_query,
                                width="300px",
                                size="3",
                                variant="surface",
                            ),
                            rx.spacer(),
                            # Filters
                            rx.select(
                                TransactionsState.account_filter_options,
                                value=TransactionsState.selected_account_filter,
                                on_change=TransactionsState.set_selected_account_filter,
                                size="3",
                                variant="surface"
                            ),
                            rx.select(
                                TransactionsState.category_filter_options,
                                value=TransactionsState.selected_category_filter,
                                on_change=TransactionsState.set_selected_category_filter,
                                size="3",
                                variant="surface"
                            ),
                            width="100%",
                            align="center",
                        ),
                        width="100%",
                        size="2",
                    ),

                    rx.cond(
                        TransactionsState.is_loading,
                        rx.center(rx.spinner(), width="100%", height="50vh"),
                        rx.cond(
                            TransactionsState.error_message != "",
                            rx.center(
                                rx.vstack(
                                    rx.heading(TransactionsState.translations["Error Loading Transactions"], color="red"),
                                    rx.code_block(TransactionsState.error_message, language="json"),
                                ),
                                width="100%",
                                height="80vh",
                            ),
                            # Transactions Table
                            rx.box(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell(TransactionsState.translations["NAME"], color=SUBTLE_TEXT_COLOR, font_size="12px", letter_spacing="0.6px"),
                                            rx.table.column_header_cell(TransactionsState.translations["ACCOUNT"], color=SUBTLE_TEXT_COLOR, font_size="12px", letter_spacing="0.6px"),
                                            rx.table.column_header_cell(TransactionsState.translations["DATE"], color=SUBTLE_TEXT_COLOR, font_size="12px", letter_spacing="0.6px"),
                                            rx.table.column_header_cell(TransactionsState.translations["AMOUNT"], color=SUBTLE_TEXT_COLOR, font_size="12px", letter_spacing="0.6px", text_align="right"),
                                            border_bottom=f"1px solid {BORDER_COLOR}",
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            TransactionsState.filtered_transactions,
                                            transaction_row
                                        )
                                    ),
                                    variant="surface",
                                    size="2",
                                    width="100%",
                                ),
                                background="#FFFFFF",
                                border=f"1px solid {BORDER_COLOR}",
                                box_shadow="0px 1px 2px rgba(0, 0, 0, 0.05)",
                                border_radius="12px",
                                padding="0",
                                width="100%",
                                overflow="hidden",
                            ),
                        )
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
        transaction_modal(),
        account_modal(),
        manage_accounts_modal(),
        invitation_modal(),
        background_color="#F6F8F6",
        min_height="100vh",
    )
