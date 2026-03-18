import reflex as rx
from ..state import LoginState
from ..styles import card_style, input_style, button_style, label_style, PRIMARY_COLOR

def password_input() -> rx.Component:
    return rx.box(
        rx.input(
            placeholder=LoginState.translations["Enter your password"],
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
                rx.heading(LoginState.translations["Log In"], size="7", font_weight="700"),
                rx.text(LoginState.translations["Welcome back! Please enter your details."]),
                align="center",
                padding="32px 32px 8px",
                width="100%",
            ),
            # Form
            rx.vstack(
                rx.vstack(
                    rx.text(LoginState.translations["Email Address"], style=label_style),
                    rx.input(placeholder=LoginState.translations["name@example.com"], on_blur=LoginState.set_email, type="email", style=input_style),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text(LoginState.translations["Password"], style=label_style),
                        rx.spacer(),
                        rx.link(LoginState.translations["Forgot password?"], href="#", font_weight="500", color=PRIMARY_COLOR),
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
                        rx.spinner(),
                        LoginState.translations["Log In"],
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
                    LoginState.translations["Don't have an account? "],
                    rx.link(LoginState.translations["Sign up"], href="/register", color=PRIMARY_COLOR, font_weight="500"),
                ),
                border_top=f"1px solid var(--gray-a5)",
                padding="16px",
                width="100%",
            ),
            style=card_style,
            spacing="0",
        ),
        width="100%",
        min_height="100vh",
    )
