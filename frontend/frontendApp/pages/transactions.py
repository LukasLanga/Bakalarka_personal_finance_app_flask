import reflex as rx
from ..state import BaseState, DashboardState, TransactionsState
from ..api import client
from ..models.models import Transaction, Account, Category
from ..components.sidebar import sidebar
from ..components.topbar import topbar
from ..components.transaction_modal import transaction_modal
from ..components.account_modal import account_modal
from ..components.manage_accounts_modal import manage_accounts_modal
from ..components.invitation_modal import invitation_modal

def transaction_row(transaction: Transaction) -> rx.Component:
    """A single row for the transactions table."""
    detail_url = f"/transaction/{transaction.account_id}/{transaction.id}"

    return rx.table.row(
        rx.table.row_header_cell(
            rx.link(
                rx.text(transaction.name, weight="bold", size="2"),
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
                    TransactionsState.account_id_to_name.get(str(transaction.account_id), "N/A"),
                    size="2",
                    color_scheme="gray"
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
                rx.badge(rx.moment(transaction.date, format="DD MMMM YYYY"), variant="soft", color_scheme="gray"),
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
                    color=rx.cond(transaction.amount < 0, "var(--red-9)", "var(--green-9)"),
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
        _hover={"background_color": "var(--gray-a3)"},
        border_bottom="1px solid var(--gray-a5)",
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
                        rx.vstack(
                            rx.heading(TransactionsState.translations["Transactions"], size="8"),
                            rx.text(TransactionsState.translations["View and manage all your transactions."], color_scheme="gray"),
                            align="start",
                            spacing="1",
                        ),
                        rx.spacer(),
                        align_items="center",
                        spacing="4",
                        width="100%",
                    ),
                    
                    # Filters and Search
                    rx.card(
                        rx.hstack(
                            rx.input(
                                rx.input.slot(rx.icon("search", size=16)),
                                placeholder=TransactionsState.translations["Search by name or description"],
                                value=TransactionsState.search_query,
                                on_change=TransactionsState.set_search_query,
                                width="300px",
                                size="3",
                                variant="surface",
                            ),
                            rx.spacer(),
                            # Filters
                            rx.select.root(
                                rx.select.trigger(placeholder=TransactionsState.translations["All Accounts"]),
                                rx.select.content(
                                    rx.foreach(
                                        TransactionsState.account_filter_options,
                                        lambda option: rx.select.item(option, value=option)
                                    )
                                ),
                                value=TransactionsState.selected_account_filter,
                                on_change=TransactionsState.set_selected_account_filter,
                                size="3",
                                variant="surface"
                            ),
                            rx.select.root(
                                rx.select.trigger(placeholder=TransactionsState.translations["All Categories"]),
                                rx.select.content(
                                    rx.foreach(
                                        TransactionsState.category_filter_options,
                                        lambda option: rx.select.item(option, value=option)
                                    )
                                ),
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
                                            rx.table.column_header_cell(TransactionsState.translations["NAME"]),
                                            rx.table.column_header_cell(TransactionsState.translations["ACCOUNT"]),
                                            rx.table.column_header_cell(TransactionsState.translations["DATE"]),
                                            rx.table.column_header_cell(TransactionsState.translations["AMOUNT"], text_align="right"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            TransactionsState.filtered_transactions,
                                            transaction_row
                                        )
                                    ),
                                    variant="ghost",
                                    size="2",
                                    width="100%",
                                ),
                                background_color="var(--gray-a2)",
                                padding="1rem",
                                border_radius="var(--radius-3)",
                                width="100%",
                            ),
                        )
                    ),
                    rx.hstack(
                        rx.button(TransactionsState.translations["Previous"], on_click=TransactionsState.prev_page, disabled=TransactionsState.current_page <= 1),
                        rx.text(
                            f"{TransactionsState.translations['Page']} {TransactionsState.current_page} {TransactionsState.translations['of']} {TransactionsState.total_pages}"
                        ),
                        rx.button(TransactionsState.translations["Next"], on_click=TransactionsState.next_page, disabled=TransactionsState.current_page >= TransactionsState.total_pages),
                        justify="center",
                        align="center",
                        spacing="4",
                        margin_top="1em",
                        width="100%",
                    ),
                    
                    spacing="5",
                    padding="2em",
                    width="100%",
                ),
                padding_top="80px", # Adjust for topbar
                margin_left=["0", "0", "288px", "288px", "288px"],
                width="100%",
                padding_x="2em",
            ),
            align_items="flex-start",
        ),
        transaction_modal(),
        account_modal(),
        manage_accounts_modal(),
        invitation_modal(),
        min_height="100vh",
    )
