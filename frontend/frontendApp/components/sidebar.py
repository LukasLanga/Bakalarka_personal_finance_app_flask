import reflex as rx
from ..state.state import BaseState, DashboardState
from ..styles import PRIMARY_COLOR, BORDER_COLOR, SUBTLE_TEXT_COLOR, TEXT_COLOR
from ..models.models import Account

def sidebar_user_profile() -> rx.Component:
    """Component for the user profile section in the sidebar."""
    return rx.hstack(
        rx.avatar(fallback=BaseState.logged_in_user.username[0], size="3"),
        rx.vstack(
            rx.text(BaseState.logged_in_user.username, font_weight="700", color=TEXT_COLOR),
            rx.text(BaseState.logged_in_user.email, font_size="0.75em", color=SUBTLE_TEXT_COLOR),
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
                rx.icon("landmark", size=16, color=rx.cond(is_selected, "#FFFFFF", PRIMARY_COLOR)),
                bg=rx.cond(is_selected, PRIMARY_COLOR, rx.color("green", 3)),
                border_radius="8px",
                padding="8px",
            ),
            rx.vstack(
                rx.text(account.name, font_weight="700", font_size="0.9em", color=TEXT_COLOR),
                rx.text(f"{account.balance} {account.currency}", font_size="0.75em", color=rx.cond(is_selected, PRIMARY_COLOR, PRIMARY_COLOR), font_weight="600"),
                align_items="flex-start",
                spacing="1",
            ),
            rx.spacer(),
            rx.icon("chevron_right", color=SUBTLE_TEXT_COLOR),
            align="center",
            width="100%",
        ),
        on_click=DashboardState.select_account(account.id),
        background=rx.cond(is_selected, "#F0FDF4", "#F8FAFC"),
        border=rx.cond(is_selected, f"1px solid {PRIMARY_COLOR}", f"1px solid {BORDER_COLOR}"),
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
            rx.icon(icon, size=20, color=SUBTLE_TEXT_COLOR),
            rx.text(DashboardState.translations[text], font_weight="500", color=TEXT_COLOR),
            spacing="3",
            align="center",
        ),
        href=href,
        width="100%",
        padding="0.75em 1em",
        border_radius="12px",
        _hover={"background_color": BORDER_COLOR},
    )

def sidebar() -> rx.Component:
    """The main application sidebar."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                sidebar_user_profile(),
                rx.spacer(),
                # Close button for mobile
                rx.icon(
                    "x",
                    size=24,
                    color=SUBTLE_TEXT_COLOR,
                    on_click=DashboardState.toggle_sidebar,
                    display=["block", "block", "none", "none", "none"], # Visible only on mobile/tablet
                    cursor="pointer",
                ),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(DashboardState.translations["Accounts"], font_weight="600", font_size="0.75em", letter_spacing="0.6px", text_transform="uppercase", color=SUBTLE_TEXT_COLOR),
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
            rx.spacer(),
            rx.cond(
                DashboardState.can_add_transaction,
                rx.button(
                    DashboardState.translations["Add Transaction"],
                    on_click=DashboardState.toggle_transaction_modal,
                    width="100%",
                    height="48px",
                    background=PRIMARY_COLOR,
                    color=TEXT_COLOR,
                    font_weight="700",
                ),
            ),
            padding="1.5em",
            spacing="5",
            width="288px",
            height="100vh",
            background_color="#FFFFFF",
            border_right=f"1px solid {BORDER_COLOR}",
            align_items="flex-start",
        ),
        position="fixed",
        top="0",
        left="0",
        z_index="100",
        display=[
            rx.cond(DashboardState.is_sidebar_collapsed, "none", "block"), # Mobile
            rx.cond(DashboardState.is_sidebar_collapsed, "none", "block"), # Tablet
            "block", # Desktop
            "block",
            "block"
        ],
        width=["100%", "100%", "288px", "288px", "288px"],
        background_color=[
            rx.cond(DashboardState.is_sidebar_collapsed, "transparent", "rgba(0,0,0,0.5)"), # Mobile
            rx.cond(DashboardState.is_sidebar_collapsed, "transparent", "rgba(0,0,0,0.5)"), # Tablet
            "transparent", # Desktop
            "transparent",
            "transparent"
        ],
        height="100vh",
    )
