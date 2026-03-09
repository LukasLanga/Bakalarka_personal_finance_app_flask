import reflex as rx
from ..state import DashboardState

def get_role_description(role: str) -> str:
    """Returns a description for a given account role."""
    descriptions = {
        "viewer": "As a Viewer, you can see account balances and transactions, but you cannot make any changes.",
        "editor": "As an Editor, you can view, add, and edit transactions, but you cannot change account settings.",
        "manager": "As a Manager, you have full editing rights and can manage access for other users.",
        "owner": "As the Owner, you have full control over the account, including deleting it."
    }
    return descriptions.get(role.lower(), "You have been invited to join this account.")

def invitation_detail_row(title: str, value: str) -> rx.Component:
    """A single row for displaying invitation details."""
    return rx.flex(
        rx.text(DashboardState.translations[title], color_scheme="gray", size="2", weight="medium"),
        rx.text(value, size="2", weight="bold"),
        justify="between",
        width="100%",
        padding_y="10px",
        border_bottom="1px solid #F1F5F9",
    )

def invitation_modal() -> rx.Component:
    """A modal to display invitation details and actions."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(DashboardState.translations["Account Invitation"]),
            rx.cond(
                DashboardState.selected_invitation,
                rx.vstack(
                    invitation_detail_row("From", DashboardState.selected_invitation.invited_by),
                    invitation_detail_row("Account", DashboardState.selected_invitation.account_name),
                    invitation_detail_row("Role", DashboardState.selected_invitation.role.capitalize()),
                    rx.box(
                        rx.text(
                            DashboardState.translations[get_role_description(DashboardState.selected_invitation.role)],
                            size="2",
                            color_scheme="gray",
                        ),
                        bg_color="#F8FAFC",
                        padding="12px",
                        border_radius="8px",
                        margin_top="10px",
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                DashboardState.translations["Close"],
                                variant="soft",
                                color_scheme="gray",
                                flex_grow=1,
                            )
                        ),
                        rx.dialog.close(
                            rx.button(
                                DashboardState.translations["Accept Invitation"],
                                on_click=DashboardState.accept_invitation,
                                color_scheme="green",
                                flex_grow=1,
                            )
                        ),
                        spacing="3",
                        width="100%",
                        margin_top="20px",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.text(DashboardState.translations["No invitation selected."]),
            ),
        ),
        open=DashboardState.show_invitation_modal,
        on_open_change=DashboardState.set_show_invitation_modal,
    )
