import reflex as rx
from ..state.password_reset_state import ForgotPasswordState
from ..styles import card_style, input_style, button_style, label_style, PRIMARY_COLOR
from .login import dark_mode_toggle
from ..components.language_switcher import language_switcher

@rx.page(route="/forgot-password", title="Forgot Password", on_load=ForgotPasswordState.on_load_reset)
def forgot_password_page() -> rx.Component:
    """The UI for the forgot password page."""
    return rx.box(
        rx.center(
            rx.vstack(
                # Header Section
                rx.vstack(
                    rx.heading(ForgotPasswordState.translations["forgot_password"], size="7", font_weight="700"),
                    rx.text(ForgotPasswordState.translations["forgot_password_instructions"]),
                    align="center",
                    padding="32px 32px 8px",
                    width="100%",
                ),
                # Form
                rx.vstack(
                    rx.form(
                        rx.vstack(
                            rx.text(ForgotPasswordState.translations["email_address"], style=label_style),
                            rx.input(
                                placeholder="name@example.com",
                                on_blur=ForgotPasswordState.set_email,
                                type="email",
                                style=input_style
                            ),
                            rx.button(
                                rx.cond(
                                    ForgotPasswordState.is_loading,
                                    rx.spinner(),
                                    ForgotPasswordState.translations["send_reset_link"],
                                ),
                                style=button_style,
                                disabled=ForgotPasswordState.is_loading,
                            ),
                            spacing="4",
                            align="stretch",
                            width="100%",
                        ),
                        on_submit=ForgotPasswordState.handle_submit,
                    ),
                    rx.cond(
                        ForgotPasswordState.message,
                        rx.callout(
                            ForgotPasswordState.message,
                            icon="info",
                            color_scheme=rx.cond(ForgotPasswordState.is_error, "red", "green"),
                            width="100%",
                        )
                    ),
                    spacing="5",
                    padding="0px 32px 24px",
                    width="100%",
                ),
                # Footer section
                rx.center(
                    rx.link(ForgotPasswordState.translations["back_to_login"], href="/login", color=PRIMARY_COLOR, font_weight="500"),
                    border_top=f"1px solid var(--gray-a5)",
                    padding="16px",
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
