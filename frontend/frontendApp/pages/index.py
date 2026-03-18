import reflex as rx
from ..state import DashboardState
from ..components.sidebar import sidebar
from ..components.topbar import topbar
from ..components.transaction_modal import transaction_modal
from ..components.account_modal import account_modal
from ..components.manage_accounts_modal import manage_accounts_modal
from ..components.invitation_modal import invitation_modal
from ..styles import PRIMARY_COLOR
from ..components.transaction_row import transaction_row

def summary_card(title: str, value: str, icon: str, color_scheme: str) -> rx.Component:
    """A card for displaying a summary metric."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=24),
                    bg=rx.color(color_scheme, 3),
                    color=rx.color(color_scheme, 9),
                    border_radius="8px",
                    padding="8px",
                ),
                rx.spacer(),
                width="100%",
                align="center",
            ),
            rx.spacer(),
            rx.vstack(
                rx.text(DashboardState.translations[title], size="2", color_scheme="gray", weight="medium"),
                rx.heading(value, size="6", weight="bold"),
                spacing="1",
                align="start",
            ),
            spacing="3",
            height="100%",
        ),
        size="3",
        width="100%",
    )

def yearly_overview_chart() -> rx.Component:
    """A bar chart showing income vs. expenses for the last 12 months."""
    return rx.recharts.responsive_container(
        rx.recharts.bar_chart(
            rx.recharts.x_axis(data_key="month"),
            rx.recharts.y_axis(),
            rx.recharts.tooltip(),
            rx.recharts.bar(data_key="income", fill="var(--green-9)", name=DashboardState.translations["Income"], radius=[4, 4, 0, 0]),
            rx.recharts.bar(data_key="expenses", fill="var(--red-9)", name=DashboardState.translations["Expenses"], radius=[4, 4, 0, 0]),
            data=DashboardState.yearly_overview,
        ),
        min_height=250,
    )

def yearly_overview_card() -> rx.Component:
    """A card containing the yearly overview bar chart."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(DashboardState.translations["Overview"], size="4"),
                    rx.text(DashboardState.translations["Your income and expenses for the last 12 months."], color_scheme="gray", size="2"),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.box(bg="var(--green-9)", width="12px", height="12px", border_radius="full"),
                    rx.text(DashboardState.translations["Income"], size="2", color_scheme="gray"),
                    rx.box(bg="var(--red-9)", width="12px", height="12px", border_radius="full"),
                    rx.text(DashboardState.translations["Expenses"], size="2", color_scheme="gray"),
                    spacing="3",
                    align="center",
                ),
                width="100%",
            ),
            yearly_overview_chart(),
            spacing="4",
            width="100%",
        ),
        width="100%",
    )

def recent_transactions_table() -> rx.Component:
    """A table to display recent transactions."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(DashboardState.translations["Recent Transactions"], size="4"),
                rx.spacer(),
                rx.link(DashboardState.translations["View All"], href="/transactions", size="2", color=PRIMARY_COLOR, weight="bold"),
                width="100%",
                align="center",
                padding_bottom="24px",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell(DashboardState.translations["NAME"]),
                        rx.table.column_header_cell(DashboardState.translations["ACCOUNT"]),
                        rx.table.column_header_cell(DashboardState.translations["DATE"]),
                        rx.table.column_header_cell(DashboardState.translations["AMOUNT"], text_align="right"),
                        border_bottom="1px solid var(--gray-a5)",
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        DashboardState.enriched_recent_transactions,
                        transaction_row
                    )
                ),
                variant="ghost",
                size="2",
                width="100%",
            ),
            spacing="0",
            width="100%",
        ),
        width="100%",
    )

def spending_by_category_pie_chart() -> rx.Component:
    """A pie chart for spending by category."""
    return rx.recharts.responsive_container(
        rx.recharts.pie_chart(
            rx.recharts.pie(
                rx.foreach(
                    DashboardState.spending_by_category_dict,
                    lambda item: rx.recharts.cell(fill=item["fill"]),
                ),
                data=DashboardState.spending_by_category_dict,
                data_key="amount",
                name_key="category_name",
                cx="50%",
                cy="50%",
                inner_radius="60%",
                outer_radius="80%",
                label_line=False,
            ),
            rx.recharts.tooltip(),
        ),
        min_height=250,
    )

def custom_legend() -> rx.Component:
    """A custom legend for the pie chart."""
    return rx.vstack(
        rx.foreach(
            DashboardState.spending_by_category_dict,
            lambda item: rx.grid(
                rx.hstack(
                    rx.box(bg=item["fill"], width="12px", height="12px", border_radius="4px"),
                    rx.text(item["category_name"], size="2", white_space="nowrap"),
                    spacing="2",
                    align="center",
                ),
                rx.text(f"{item['percentage']:.0f}%", size="2", weight="bold", text_align="right"),
                grid_template_columns="1fr auto",
                gap="4",
                width="100%",
            )
        ),
        spacing="2",
        width="100%",
        max_width="240px",
    )

def spending_by_category_list() -> rx.Component:
    """A card containing the spending by category pie chart and legend."""
    return rx.card(
        rx.vstack(
            rx.heading(DashboardState.translations["Spending by Category"], size="4", padding_bottom="4"),
            rx.cond(
                DashboardState.spending_by_category_dict,
                rx.vstack(
                    spending_by_category_pie_chart(),
                    custom_legend(),
                    spacing="4",
                    width="100%",
                    align="center",
                ),
                rx.center(
                    rx.text(DashboardState.translations["No spending data to display for this period."]),
                    min_height="350px",
                    width="100%",
                ),
            ),
            rx.hstack(
                rx.button(
                    rx.icon(tag="chevron-left"),
                    on_click=DashboardState.prev_month,
                    variant="ghost",
                ),
                rx.spacer(),
                rx.text(DashboardState.selected_month_str, weight="bold"),
                rx.spacer(),
                rx.button(
                    rx.icon(tag="chevron-right"),
                    on_click=DashboardState.next_month,
                    variant="ghost",
                ),
                width="100%",
                align="center",
                padding_top="1em",
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
    )

def dashboard_content() -> rx.Component:
    """The main content of the dashboard, shown when data is loaded."""
    return rx.vstack(
        # Summary Cards
        rx.grid(
            summary_card("Total Balance", f"{DashboardState.dashboard_summary.total_balance:,.2f} {DashboardState.selected_account_currency}", "wallet", "green"),
            summary_card("Monthly Income", f"{DashboardState.dashboard_summary.monthly_income:,.2f} {DashboardState.selected_account_currency}", "arrow_up", "blue"),
            summary_card("Monthly Expenses", f"{DashboardState.dashboard_summary.monthly_expenses:,.2f} {DashboardState.selected_account_currency}", "arrow_down", "red"),
            columns={"base": "1", "md": "3"},
            gap="4",
            width="100%",
        ),
        # Yearly Overview and Spending by Category
        rx.grid(
            yearly_overview_card(),
            spending_by_category_list(),
            columns={"base": "1", "lg": "2fr 1fr"},
            gap="4",
            width="100%",
        ),
        # Recent Transactions
        recent_transactions_table(),
        spacing="5",
        width="100%",
    )

@rx.page(route="/", on_load=DashboardState.on_page_load, title="Personal Finance App")
def index() -> rx.Component:
    """The main dashboard page."""
    return rx.box(
        topbar(),
        rx.hstack(
            sidebar(),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.heading(DashboardState.translations["Dashboard"], size="8"),
                            rx.text(DashboardState.translations["Welcome back! Here is your financial overview."], color_scheme="gray"),
                            align="start",
                            spacing="1",
                        ),
                        rx.spacer(),
                        align="center",
                        spacing="4",
                        width="100%",
                    ),
                    rx.cond(
                        DashboardState.is_loading,
                        rx.center(rx.spinner(), width="100%", height="80vh"),
                        rx.cond(
                            DashboardState.error_message != "",
                            rx.center(
                                rx.vstack(
                                    rx.heading(DashboardState.translations["Error Loading Dashboard"], color="red"),
                                    rx.code_block(DashboardState.error_message, language="json"),
                                ),
                                width="100%",
                                height="80vh",
                            ),
                            rx.cond(
                                DashboardState.dashboard_summary,
                                dashboard_content(),
                                rx.center(rx.text(DashboardState.translations["No dashboard data available."]), height="80vh"),
                            )
                        )
                    ),
                    spacing="5",
                    padding="2em",
                    width="100%",
                ),
                padding_top="80px",
                margin_left=["0", "0", "288px", "288px", "288px"],
                width=["100%", "100%", "calc(100% - 288px)", "calc(100% - 288px)", "calc(100% - 288px)"],
            ),
            align_items="flex-start",
        ),
        transaction_modal(),
        account_modal(),
        manage_accounts_modal(),
        invitation_modal(),
    )