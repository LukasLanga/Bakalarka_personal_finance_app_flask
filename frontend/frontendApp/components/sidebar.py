import reflex as rx
from ..state import BaseState, DashboardState
from ..state.add_bank_account_state import AddBankAccountState
from ..styles import PRIMARY_COLOR
from ..models.models import Account

def sidebar_user_profile() -> rx.Component:
    """Component for the user profile section in the sidebar."""
    return rx.hstack(
        rx.avatar(fallback=BaseState.logged_in_user.username[0], size="3"),
        rx.vstack(
            rx.text(BaseState.logged_in_user.username, font_weight="700"),
            rx.text(BaseState.logged_in_user.email, font_size="0.75em", color_scheme="gray"),
            align_items="flex-start",
            spacing="1",
        ),
        align="center",
        spacing="3",
    )

def sidebar_account_item(account: Account) -> rx.Component:
    """Component for a single account item in the sidebar."""
    is_selected = DashboardState.selected_account_id == account.id
    
    return rx.button(
        rx.hstack(
            rx.box(
                rx.icon("landmark", size=16),
                border_radius="8px",
                padding="8px",
            ),
            rx.vstack(
                rx.text(account.name, font_weight="700", font_size="0.9em"),
                rx.text(f"{account.balance} {account.currency}", font_size="0.75em", font_weight="600"),
                align_items="flex-start",
                spacing="1",
            ),
            rx.spacer(),
            rx.icon("chevron_right", color_scheme="gray"),
            align="center",
            width="100%",
        ),
        on_click=DashboardState.select_account(account.id),
        variant=rx.cond(is_selected, "solid", "ghost"),
        color_scheme=rx.cond(is_selected, "grass", "gray"),
        border_radius="12px",
        width="100%",
        padding="0.75em",
        height="auto",
        cursor="pointer",
    )

def sidebar_nav_link(text: str, href: str, icon: str) -> rx.Component:
    """A reusable component for navigation links in the sidebar."""
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20, color_scheme="gray"),
            rx.text(DashboardState.translations[text], font_weight="500"),
            spacing="3",
            align="center",
        ),
        href=href,
        width="100%",
        padding="0.75em 1em",
        border_radius="12px",
        _hover={"background_color": "var(--gray-a3)"},
    )

def bank_connection_alert_dialog() -> rx.Component:
    """Alert dialog for bank connection confirmation."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title(DashboardState.translations["bank_connect_dialog_title"]),
            rx.alert_dialog.description(
                DashboardState.translations["bank_connect_dialog_description"]
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(DashboardState.translations["No"], variant="soft", color_scheme="gray"),
                ),
                rx.alert_dialog.action(
                    rx.button(DashboardState.translations["Yes"], on_click=DashboardState.confirm_connect_to_bank),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
        open=DashboardState.show_bank_connect_alert,
        on_open_change=DashboardState.set_show_bank_connect_alert,
    )

def sidebar() -> rx.Component:
    """The main application sidebar."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                sidebar_user_profile(),
                rx.spacer(),
                rx.icon(
                    "x",
                    size=24,
                    on_click=DashboardState.toggle_sidebar,
                    display=["block", "block", "none", "none", "none"],
                    cursor="pointer",
                ),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(DashboardState.translations["Accounts"], font_weight="600", font_size="0.75em", letter_spacing="0.6px", text_transform="uppercase", color_scheme="gray"),
                    rx.spacer(),
                    rx.link(
                        DashboardState.translations["Add New"],
                        on_click=DashboardState.toggle_account_modal,
                        font_weight="500",
                        font_size="0.75em",
                        color=PRIMARY_COLOR,
                        cursor="pointer",
                    ),
                    justify="between",
                    width="100%",
                ),
                rx.foreach(DashboardState.accounts, sidebar_account_item),
                rx.button(
                    DashboardState.translations["Manage Accounts"],
                    on_click=DashboardState.toggle_manage_accounts_modal,
                    variant="soft",
                    width="100%",
                    margin_top="8px",
                ),
                spacing="3",
                width="100%",
            ),
            rx.divider(),
            rx.vstack(
                sidebar_nav_link("Dashboard", "/", "layout-dashboard"),
                sidebar_nav_link("Transactions", "/transactions", "arrow-left-right"),
                sidebar_nav_link("Categories", "/categories", "layout-grid"),
                spacing="2",
                width="100%",
            ),
            rx.divider(),
            rx.vstack(
                rx.text(DashboardState.translations["Bank Integration"], font_weight="600", font_size="0.75em", letter_spacing="0.6px", text_transform="uppercase", color_scheme="gray"),
                rx.cond(
                    ~DashboardState.is_kb_connected,
                    rx.button(
                        DashboardState.translations["Connect to Bank"],
                        on_click=DashboardState.toggle_bank_connect_alert,
                        loading=DashboardState.is_syncing,
                        variant="outline",
                        width="100%",
                    ),
                ),
                rx.button(
                    DashboardState.translations["Add Bank Account"],
                    on_click=AddBankAccountState.open_modal,
                    disabled=~DashboardState.is_kb_connected,
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            rx.spacer(),
            rx.cond(
                DashboardState.can_add_transaction,
                rx.button(
                    DashboardState.translations["Add Transaction"],
                    on_click=DashboardState.toggle_transaction_modal,
                    width="100%",
                    height="48px",
                    color_scheme="grass",
                    font_weight="700",
                ),
            ),
            bank_connection_alert_dialog(),
            padding="1.5em",
            spacing="5",
            width="288px",
            height="100vh",
            border_right="1px solid var(--gray-a5)",
            align_items="flex-start",
        ),
        position="fixed",
        top="0",
        left="0",
        z_index="100",
        display=[
            rx.cond(DashboardState.is_sidebar_collapsed, "none", "block"),
            rx.cond(DashboardState.is_sidebar_collapsed, "none", "block"),
            "block",
            "block",
            "block"
        ],
        width=["100%", "100%", "288px", "288px", "288px"],
        background_color=[
            "var(--gray-1)",
            "var(--gray-1)",
            "transparent",
            "transparent",
            "transparent"
        ],
        height="100vh",
    )
