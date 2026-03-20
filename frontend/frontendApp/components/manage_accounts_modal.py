import reflex as rx
from ..state import DashboardState, ManageAccountsState
from ..models.models import AccountUser

def user_access_row(user: AccountUser) -> rx.Component:
    """A row displaying a user with access to the account."""
    is_current_user_in_row = user.id == DashboardState.logged_in_user.id
    is_row_owner = user.role == "owner"
    can_current_user_manage = ManageAccountsState.can_manage_users

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
            is_disabled=is_row_owner | (~can_current_user_manage),
        ),
        # Conditional remove/leave button
        rx.cond(
            is_current_user_in_row,
            # Show "Leave" button for self, unless owner
            rx.cond(
                ~is_row_owner,
                rx.button(
                    ManageAccountsState.translations["Leave"],
                    on_click=lambda: ManageAccountsState.remove_user(user.id),
                    color_scheme="red",
                    variant="soft",
                ),
            ),
            # Show "Remove" button for others, if manager/owner
            rx.cond(
                can_current_user_manage,
                 rx.button(
                    ManageAccountsState.translations["Remove"],
                    on_click=lambda: ManageAccountsState.remove_user(user.id),
                    color_scheme="red",
                    variant="soft",
                    is_disabled=is_row_owner,
                ),
            )
        ),
        align="center",
        width="100%",
        padding_y="8px",
    )

def edit_account_form() -> rx.Component:
    """The form for editing an account, including user management."""
    can_manage = ManageAccountsState.can_manage_users
    is_owner = ManageAccountsState.current_user_role == "owner"

    return rx.vstack(
        # Account Details Card (conditionally editable)
        rx.card(
            rx.vstack(
                rx.heading(ManageAccountsState.translations["Account Details"], size="5"),
                rx.text(ManageAccountsState.translations["Account Name"], size="2", margin_bottom="-8px", color_scheme="gray"),
                rx.input(
                    value=ManageAccountsState.edit_name,
                    on_change=ManageAccountsState.set_edit_name,
                    width="100%",
                    is_disabled=~can_manage,
                ),
                rx.text(ManageAccountsState.translations["Bank Name"], size="2", margin_bottom="-8px", color_scheme="gray"),
                rx.input(
                    value=ManageAccountsState.edit_bank_name,
                    on_change=ManageAccountsState.set_edit_bank_name,
                    width="100%",
                    is_disabled=~can_manage,
                ),
                rx.text(ManageAccountsState.translations["Currency"], size="2", margin_bottom="-8px", color_scheme="gray"),
                rx.select(
                    ["EUR", "USD", "GBP", "CZK"],
                    value=ManageAccountsState.edit_currency,
                    on_change=ManageAccountsState.set_edit_currency,
                    width="100%",
                    is_disabled=~can_manage,
                ),
                rx.cond(
                    can_manage,
                    rx.button(ManageAccountsState.translations["Save Account Details"], on_click=ManageAccountsState.save_changes, width="100%", margin_top="10px"),
                ),
                spacing="3",
                width="100%",
            )
        ),
        # Members Card (visible to all)
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading(ManageAccountsState.translations["Members"], size="5"),
                        rx.text(ManageAccountsState.translations["Users with access to this account"], size="2", color_scheme="gray"),
                        align="start",
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.badge(f"{ManageAccountsState.user_count} Members", color_scheme="gray", variant="soft", size="2"),
                    width="100%",
                    align="center",
                    padding="12px",
                    bg="rgba(249, 250, 251, 0.5)",
                    border_bottom="1px solid #F0F4F2",
                ),
                rx.vstack(
                    rx.foreach(
                        ManageAccountsState.account_users,
                        user_access_row,
                    ),
                    spacing="2",
                    width="100%",
                    padding="12px",
                ),
                spacing="0",
            ),
            width="100%",
        ),
        
        # Invite Card (only for managers/owners)
        rx.cond(
            can_manage,
            rx.card(
                rx.vstack(
                    rx.heading(ManageAccountsState.translations["Invite New Member"], size="5"),
                    rx.hstack(
                        rx.input(
                            placeholder=ManageAccountsState.translations["colleague@example.com"],
                            value=ManageAccountsState.invite_email,
                            on_change=ManageAccountsState.set_invite_email,
                            flex_grow=1,
                            size="3",
                        ),
                        rx.select(
                            ["viewer", "editor", "manager"],
                            value=ManageAccountsState.invite_role,
                            on_change=ManageAccountsState.set_invite_role,
                            size="3",
                        ),
                        rx.button(ManageAccountsState.translations["Send Invite"], on_click=ManageAccountsState.invite_user, size="3"),
                        spacing="3",
                        width="100%",
                    ),
                    rx.cond(
                        ManageAccountsState.invitation_sent_message != "",
                        rx.callout.root(
                            rx.callout.icon(rx.icon("check_check")),
                            rx.callout.text(ManageAccountsState.invitation_sent_message),
                            color_scheme="green",
                            margin_top="12px",
                        ),
                    ),
                    spacing="4",
                    width="100%",
                ),
                width="100%",
            ),
        ),
        
        # Delete Account Section (only for owners)
        rx.cond(
            is_owner,
            rx.card(
                rx.vstack(
                    rx.heading(ManageAccountsState.translations["Delete Account"], size="5", color_scheme="red"),
                    rx.text(ManageAccountsState.translations["This action is permanent and cannot be undone."]),
                    rx.button(
                        ManageAccountsState.translations["Delete this Account"],
                        on_click=ManageAccountsState.open_delete_confirmation(ManageAccountsState.account_to_edit.id),
                        color_scheme="red",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                )
            )
        ),
        spacing="4",
        width="100%",
    )

def account_management_list() -> rx.Component:
    """The list of accounts to manage."""
    return rx.vstack(
        rx.hstack(
            rx.button(DashboardState.translations["New Account"], on_click=DashboardState.toggle_account_modal, size="2"),
            width="100%",
            justify="between",
        ),
        rx.text(DashboardState.translations["Select an account to manage its settings and user access."]),
        rx.foreach(
            DashboardState.accounts,
            lambda acc: rx.card(
                rx.hstack(
                    rx.vstack(
                        rx.text(acc.name, weight="bold"),
                        rx.text(acc.bank_name, size="2", color="gray"),
                        align="start",
                    ),
                    rx.spacer(),
                    rx.button(DashboardState.translations["Edit"], on_click=lambda: ManageAccountsState.start_edit(acc), size="1", variant="outline"),
                    width="100%",
                    align="center",
                ),
                width="100%",
            )
        ),
        spacing="3",
        width="100%",
    )

def manage_accounts_modal() -> rx.Component:
    """A modal to manage accounts."""
    return rx.fragment(
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title(DashboardState.translations["Manage Accounts"]),
                rx.vstack(
                    rx.cond(
                        ManageAccountsState.is_editing,
                        edit_account_form(),
                        account_management_list(),
                    ),
                    rx.dialog.close(
                        rx.button(
                            DashboardState.translations["Close"],
                            on_click=DashboardState.toggle_manage_accounts_modal,
                            variant="soft",
                            color_scheme="gray",
                            margin_top="16px",
                            width="100%",
                        )
                    ),
                    spacing="4",
                    width="100%",
                )
            ),
            open=DashboardState.show_manage_accounts_modal,
            on_open_change=DashboardState.handle_manage_modal_change,
        ),
        # Separate delete confirmation dialog
        rx.alert_dialog.root(
            rx.alert_dialog.content(
                rx.alert_dialog.title(ManageAccountsState.translations["Delete Account"]),
                rx.alert_dialog.description(
                    ManageAccountsState.translations["Are you sure you want to delete this account? All associated transactions will also be deleted. This action cannot be undone."]
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        rx.button(ManageAccountsState.translations["Cancel"], on_click=ManageAccountsState.close_delete_confirmation, variant="soft", color_scheme="gray")
                    ),
                    rx.alert_dialog.action(
                        rx.button(ManageAccountsState.translations["Delete"], color_scheme="red", on_click=ManageAccountsState.delete_account)
                    ),
                    spacing="3",
                    justify="end",
                    margin_top="16px",
                ),
            ),
            open=ManageAccountsState.show_delete_confirmation,
        ),
    )
