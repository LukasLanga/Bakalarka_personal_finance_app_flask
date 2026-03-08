import reflex as rx
from ..state.state import BaseState

def language_switcher() -> rx.Component:
    """A component to switch the language."""
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                rx.hstack(
                    rx.icon("globe", size=16),
                    rx.text(BaseState.locale.upper()),
                    rx.icon("chevron-down", size=16),
                    align="center",
                    spacing="2",
                ),
                variant="soft",
            )
        ),
        rx.menu.content(
            rx.menu.item(
                "English", on_click=lambda: BaseState.set_locale("en")
            ),
            rx.menu.item(
                "Slovenčina", on_click=lambda: BaseState.set_locale("sk")
            ),
            rx.menu.item(
                "Čeština", on_click=lambda: BaseState.set_locale("cz")
            ),
        ),
    )
