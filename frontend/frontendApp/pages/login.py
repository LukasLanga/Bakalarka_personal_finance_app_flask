import reflex as rx
from ..state.state import LoginState
from ..styles import base_style, card_style, input_style, button_style, label_style, PRIMARY_COLOR, SUBTLE_TEXT_COLOR, BACKGROUND_COLOR, BORDER_COLOR

def password_input() -> rx.Component:
    return rx.box(
        rx.input(
            placeholder="Enter your password",
            on_blur=LoginState.set_password,
            type=rx.cond(LoginState.show_password, "text", "password"),
            style=input_style,
            padding_right="3.5em",
        ),
        rx.box(
            rx.icon(
                tag=rx.cond(LoginState.show_password, "eye_off", "eye"),
                on_click=LoginState.toggle_show_password,
                cursor="pointer",
                color=SUBTLE_TEXT_COLOR,
            ),
            position="absolute",
            right="1em",
            top="50%",
            transform="translateY(-50%)",
        ),
        position="relative",
        width="100%",
    )

@rx.page(route="/login", title="Login")
def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            # Header Section
            rx.vstack(
                rx.heading("Log In", size="7", font_weight="700"),
                rx.text("Welcome back! Please enter your details.", color=SUBTLE_TEXT_COLOR),
                align="center",
                padding="32px 32px 8px",
                width="100%",
            ),
            # Form
            rx.vstack(
                rx.vstack(
                    rx.text("Email Address", style=label_style),
                    rx.input(placeholder="name@example.com", on_blur=LoginState.set_email, type="email", style=input_style),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text("Password", style=label_style),
                        rx.spacer(),
                        rx.link("Forgot password?", href="#", font_weight="500", color=PRIMARY_COLOR),
                        justify="between",
                        width="100%",
                    ),
                    password_input(),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
                rx.button(
                    rx.cond(
                        LoginState.is_loading,
                        rx.spinner(color="black"),
                        "Log In",
                    ),
                    on_click=LoginState.handle_login,
                    style=button_style,
                    disabled=LoginState.is_loading,
                ),
                rx.cond(
                    LoginState.error_message != "",
                    rx.text(LoginState.error_message, color="red", text_align="center", width="100%"),
                ),
                spacing="5",
                padding="0px 32px 24px",
                width="100%",
            ),
            # Footer section
            rx.center(
                rx.text(
                    "Don't have an account? ",
                    rx.link("Sign up", href="/register", color=PRIMARY_COLOR, font_weight="500"),
                    color="#475569",
                ),
                background_color="#F8FAFC",
                border_top=f"1px solid {BORDER_COLOR}",
                padding="16px",
                width="100%",
            ),
            style=card_style,
            spacing="0",
        ),
        background=BACKGROUND_COLOR,
        width="100%",
        min_height="100vh",
        style=base_style,
    )
