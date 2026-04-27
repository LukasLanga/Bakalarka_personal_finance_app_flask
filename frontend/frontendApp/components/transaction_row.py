import reflex as rx
from ..models.models import EnrichedTransaction

def transaction_row(transaction: EnrichedTransaction) -> rx.Component:
    """A reusable component for displaying a single transaction row."""
    detail_url = f"/transaction/{transaction.account_id}/{transaction.id}"

    return rx.link(
        rx.table.row(
            rx.table.row_header_cell(
                rx.text(
                    transaction.name,
                    weight="bold",
                    size="2",
                    white_space="normal",
                    word_break="break-word",
                    max_width=["120px", "150px", "250px", "300px", "350px"],
                ),
                padding_y="16px",
            ),
            rx.table.cell(
                rx.text(
                    transaction.account_name,
                    size="2",
                    color_scheme="gray"
                ),
                vertical_align="middle",
                display=["none", "none", "table-cell", "table-cell", "table-cell"],
                padding_y="16px",
            ),
            rx.table.cell(
                rx.badge(rx.moment(transaction.date, format="DD MMMM YYYY"), variant="soft", color_scheme="gray"),
                vertical_align="middle",
                padding_y="16px",
                display=["none", "none", "table-cell", "table-cell", "table-cell"],
            ),
            rx.table.cell(
                rx.text(
                    f"{transaction.amount:,.2f} {transaction.currency}",
                    weight="bold",
                    color=rx.cond(transaction.amount < 0, "var(--red-9)", "var(--green-9)"),
                    align="right",
                ),
                vertical_align="middle",
                padding_y="16px",
            ),
            _hover={"background_color": "var(--gray-a3)"},
            border_bottom="1px solid var(--gray-a5)",
            width="100%",
        ),
        href=detail_url,
        underline="none",
        color="inherit",
        display="contents",
    )
