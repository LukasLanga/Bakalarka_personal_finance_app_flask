import reflex as rx
from .pages import index, login, register, transaction_detail, transactions, categories

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="large",
        accent_color="grass",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)
