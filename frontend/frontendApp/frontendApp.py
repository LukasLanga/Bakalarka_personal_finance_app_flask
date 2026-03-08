import reflex as rx
from .styles import base_style
from .pages import index, login, register, transaction_detail, transactions, categories

app = rx.App(
    style=base_style,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)
