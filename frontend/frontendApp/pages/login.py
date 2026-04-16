import reflex as rx
from reflex.style import set_color_mode, color_mode
from ..state import LoginState
from ..styles import card_style, input_style, button_style, label_style, PRIMARY_COLOR
from ..components.language_switcher import language_switcher


def dark_mode_toggle() -> rx.Component:
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


def password_input() -> rx.Component:
    return rx.box(
        rx.input(
            placeholder=LoginState.translations["Enter your password"],
            on_change=LoginState.set_password,
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


@rx.page(route="/login", title="Personal Finance App", on_load=LoginState.on_load_reset)
def login_page() -> rx.Component:
    return rx.box(
        rx.center(
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
                        rx.input(
                            placeholder=LoginState.translations["name@example.com"],
                            on_change=LoginState.set_email,
                            type="email",
                            style=input_style
                        ),
                        spacing="2",
                        align="stretch",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text(LoginState.translations["Password"], style=label_style),
                            rx.spacer(),
                            rx.link(LoginState.translations["Forgot password?"], href="/forgot-password", font_weight="500",
                                    color=PRIMARY_COLOR),
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
                        rx.link(LoginState.translations["Sign up"], href="/register", color=PRIMARY_COLOR,
                                font_weight="500"),
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