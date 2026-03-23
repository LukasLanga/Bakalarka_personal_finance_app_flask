import reflex as rx
from ..state.password_reset_state import ResetPasswordState
from ..styles import card_style, input_style, button_style, label_style
from .login import dark_mode_toggle
from ..components.language_switcher import language_switcher

@rx.page(route="/reset-password/[token]", title="Reset Password", on_load=ResetPasswordState.on_load_reset)
def reset_password_page() -> rx.Component:
    """The UI for the reset password page."""
    return rx.box(
        rx.center(
            rx.vstack(
                # Header Section
                rx.vstack(
                    rx.heading(ResetPasswordState.translations["reset_password"], size="7", font_weight="700"),
                    rx.text(ResetPasswordState.translations["reset_password_instructions"]),
                    align="center",
                    padding="32px 32px 8px",
                    width="100%",
                ),
                # Form
                rx.vstack(
                    rx.form(
                        rx.vstack(
                            rx.text(ResetPasswordState.translations["new_password"], style=label_style),
                            rx.input(
                                placeholder="***",
                                on_blur=ResetPasswordState.set_password,
                                type="password",
                                style=input_style
                            ),
                            rx.text(ResetPasswordState.translations["confirm_new_password"], style=label_style),
                            rx.input(
                                placeholder="***",
                                on_blur=ResetPasswordState.set_confirm_password,
                                type="password",
                                style=input_style
                            ),
                            rx.button(
                                rx.cond(
                                    ResetPasswordState.is_loading,
                                    rx.spinner(),
                                    ResetPasswordState.translations["reset_password"],
                                ),
                                style=button_style,
                                disabled=ResetPasswordState.is_loading,
                            ),
                            spacing="4",
                            align="stretch",
                            width="100%",
                        ),
                        on_submit=ResetPasswordState.handle_submit,
                    ),
                    rx.cond(
                        ResetPasswordState.message,
                        rx.callout(
                            ResetPasswordState.message,
                            icon="info",
                            color_scheme=rx.cond(ResetPasswordState.is_error, "red", "green"),
                            width="100%",
                        )
                    ),
                    spacing="5",
                    padding="0px 32px 24px",
                    width="100%",
                ),
                style=card_style,
                spacing="0",
            ),
            width="100%",
            min_height="100vh",
        ),
        rx.box(
            rx.hstack(
                dark_mode_toggle(),
                language_switcher(),
                spacing="2",
            ),
            position="absolute",
            top="1em",
            right="1em",
            z_index="10",
        ),
    )
