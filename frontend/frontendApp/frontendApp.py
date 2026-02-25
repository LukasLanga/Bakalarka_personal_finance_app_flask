import reflex as rx

from .pages import index, login, register

theme = rx.theme(
    appearance="light",
    has_background=True,
    radius="large",
    accent_color="grass",
)

app = rx.App(
    theme=theme,
)
