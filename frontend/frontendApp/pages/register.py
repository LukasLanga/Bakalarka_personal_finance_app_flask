import reflex as rx
from ..state.state import RegisterState
from ..styles import base_style, card_style, input_style, button_style, label_style, PRIMARY_COLOR, SUBTLE_TEXT_COLOR, BACKGROUND_COLOR, BORDER_COLOR

def password_input(placeholder: str, on_blur_event, show_var, toggle_event) -> rx.Component:
    return rx.box(
        rx.input(
            placeholder=RegisterState.translations[placeholder],
            on_blur=on_blur_event,
            type=rx.cond(show_var, "text", "password"),
            style=input_style,
            padding_right="3.5em",
        ),
        rx.box(
            rx.icon(
                tag=rx.cond(show_var, "eye_off", "eye"),
                on_click=toggle_event,
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

@rx.page(route="/register", title="Register")
def register_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            # Header Section
            rx.vstack(
                rx.heading(RegisterState.translations["Create an Account"], size="7", font_weight="700"),
                rx.text(RegisterState.translations["Start making your financial life easier."], color=SUBTLE_TEXT_COLOR),
                align="center",
                padding="32px 32px 8px",
                width="100%",
            ),
            # Form
            rx.vstack(
                rx.vstack(
                    rx.text(RegisterState.translations["Username"], style=label_style),
                    rx.input(placeholder=RegisterState.translations["Enter your username"], on_blur=RegisterState.set_username, style=input_style),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
                rx.vstack(
                    rx.text(RegisterState.translations["Email Address"], style=label_style),
                    rx.input(placeholder=RegisterState.translations["name@example.com"], on_blur=RegisterState.set_email, type="email", style=input_style),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
                rx.vstack(
                    rx.text(RegisterState.translations["Password"], style=label_style),
                    password_input(
                        placeholder="Create a strong password",
                        on_blur_event=RegisterState.set_password,
                        show_var=RegisterState.show_password,
                        toggle_event=RegisterState.toggle_show_password,
                    ),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
                rx.vstack(
                    rx.text(RegisterState.translations["Confirm Password"], style=label_style),
                    password_input(
                        placeholder="Confirm your password",
                        on_blur_event=RegisterState.set_confirm_password,
                        show_var=RegisterState.show_confirm_password,
                        toggle_event=RegisterState.toggle_show_confirm_password,
                    ),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
                rx.button(
                    rx.cond(
                        RegisterState.is_loading,
                        rx.spinner(color="black"),
                        RegisterState.translations["Create Account"],
                    ),
                    on_click=RegisterState.handle_registration,
                    style=button_style,
                    disabled=RegisterState.is_loading,
                ),
                rx.cond(
                    RegisterState.error_message != "",
                    rx.text(RegisterState.error_message, color="red", text_align="center", width="100%"),
                ),
                spacing="5",
                padding="0px 32px 24px",
                width="100%",
            ),
            # Footer section
            rx.center(
                rx.text(
                    RegisterState.translations["Already have an account? "],
                    rx.link(RegisterState.translations["Log in"], href="/login", color=PRIMARY_COLOR, font_weight="500"),
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
