import reflex as rx
from ..state import DashboardState, ManageAccountsState
from ..components.sidebar import sidebar
from ..components.topbar import topbar
from ..models.models import AccountUser

def user_access_row(user: AccountUser) -> rx.Component:
    """A row displaying a user with access to the account."""
    is_owner = user.role == "owner"
    can_manage = (ManageAccountsState.current_user_role == "owner") | (ManageAccountsState.current_user_role == "manager")

    return rx.hstack(
        rx.avatar(fallback=rx.cond(user.username, user.username[0], "U"), size="3"),
        rx.vstack(
            rx.text(user.username, weight="bold"),
            rx.text(user.email, size="2", color_scheme="gray"),
            align="start",
            spacing="0",
        ),
        rx.spacer(),
        rx.select(
            ["viewer", "editor", "manager", "owner"],
            value=user.role,
            on_change=lambda new_role: ManageAccountsState.update_user_role(user.id, new_role),
            is_disabled=is_owner or not can_manage,
        ),
        rx.button(
            ManageAccountsState.translations["Remove"],
            on_click=lambda: ManageAccountsState.remove_user(user.id),
            color_scheme="red",
            variant="soft",
            is_disabled=is_owner or not can_manage,
        ),
        align="center",
        width="100%",
        padding_y="8px",
    )

@rx.page(route="/accounts/[account_id]/access")
def account_access() -> rx.Component:
    """The page for managing access to a specific account."""
    return rx.box(
        topbar(),
        rx.hstack(
            sidebar(),
            rx.box(
                rx.vstack(
                    # Header
                    rx.vstack(
                        rx.heading(ManageAccountsState.translations["Account Access"], size="8", weight="bold"),
                        align="start",
                        width="100%",
                        padding_bottom="24px",
                        border_bottom="1px solid #F0F4F2",
                    ),
                    
                    spacing="6",
                    width="100%",
                    max_width="1200px",
                    margin="auto",
                ),
                padding="2em",
                padding_top="80px",
                margin_left=["0", "0", "288px", "288px", "288px"],
                width=["100%", "100%", "calc(100% - 288px)", "calc(100% - 288px)", "calc(100% - 288px)"],
            ),
            align_items="flex-start",
        ),
        background_color="#F6F8F7",
        min_height="100vh",
    )
