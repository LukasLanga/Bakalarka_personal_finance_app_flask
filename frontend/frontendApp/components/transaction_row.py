import reflex as rx
from ..models.models import EnrichedTransaction

def transaction_row(transaction: EnrichedTransaction) -> rx.Component:
    """A reusable component for displaying a single transaction row."""
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
                    transaction.account_name,
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
            display=["none", "none", "table-cell", "table-cell", "table-cell"],
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
