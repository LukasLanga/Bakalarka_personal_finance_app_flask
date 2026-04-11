import reflex as rx
from reflex.style import set_color_mode, color_mode
from ..state import DashboardState
from ..models.models import Invitation
from .language_switcher import language_switcher


def dark_mode_toggle() -> rx.Component:
    """A segmented control to toggle between light and dark mode."""
    return rx.segmented_control.root(
        rx.segmented_control.item(
            rx.icon(tag="sun", size=20),
            value="light",
        ),
        rx.segmented_control.item(
            rx.icon(tag="moon", size=20),
            value="dark",
        ),
        on_change=set_color_mode,
        variant="classic",
        radius="large",
        value=color_mode,
    )


def invitation_item(invitation: Invitation) -> rx.Component:
    """A single item in the notification popover."""
    return rx.box(
        rx.vstack(
            rx.text(
                DashboardState.translations["Invitation to join "],
                rx.text(invitation.account_name, weight="bold"),
                size="2",
            ),
            rx.text(
                f"from {invitation.invited_by}",
                size="1",
                color_scheme="gray",
            ),
            rx.hstack(
                rx.button(
                    DashboardState.translations["Details"],
                    on_click=DashboardState.select_and_show_invitation(invitation),
                    size="1",
                ),
                rx.button(
                    DashboardState.translations["Decline"],
                    on_click=lambda: DashboardState.decline_invitation(invitation.token),
                    size="1",
                    variant="soft",
                    color_scheme="red",
                ),
                spacing="2",
                width="100%",
                justify="end",
                padding_top="8px",
            ),
            align_items="start",
            spacing="1",
        ),
        width="100%",
        padding="12px",
        border_bottom="1px solid var(--gray-a5)",
    )

def topbar() -> rx.Component:
    """A top bar with logout, language, and notification options."""
    return rx.box(
        rx.hstack(
            rx.icon(
                "menu",
                size=28,
                on_click=DashboardState.toggle_sidebar,
                display=["block", "block", "none", "none", "none"],
                cursor="pointer",
            ),
            rx.spacer(),
            rx.popover.root(
                rx.popover.trigger(
                    rx.box(
                        rx.button(
                            rx.icon("bell", size=16),
                            variant="soft",
                        ),
                        rx.cond(
                            DashboardState.pending_invitations_count > 0,
                            rx.box(
                                width="8px",
                                height="8px",
                                bg="red",
                                border_radius="50%",
                                position="absolute",
                                top="6px",
                                right="6px",
                                border="2px solid var(--gray-1)",
                            ),
                        ),
                        position="relative",
                    )
                ),
                rx.popover.content(
                    rx.vstack(
                        rx.cond(
                            DashboardState.pending_invitations_count > 0,
                            rx.foreach(
                                DashboardState.pending_invitations,
                                invitation_item,
                            ),
                            rx.text(DashboardState.translations["No new notifications."], padding="12px", size="2"),
                        ),
                        spacing="0",
                    ),
                    size="3",
                ),
            ),
            dark_mode_toggle(),
            language_switcher(),
            rx.button(
                rx.icon("log-out", size=16),
                on_click=DashboardState.logout,
                variant="soft",
                color_scheme="red",
            ),
            spacing="4",
            align="center",
        ),
        padding="16px 24px",
        position="fixed",
        top="0",
        left="0",
        right="0",
        z_index="99",
    )