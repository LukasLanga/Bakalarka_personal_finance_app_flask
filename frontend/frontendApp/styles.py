# In frontend/frontendApp/styles.py

PRIMARY_COLOR = "#13EC5B"
TEXT_COLOR = "#0F172A"
LABEL_TEXT_COLOR = "#334155"
SUBTLE_TEXT_COLOR = "#64748B"
PLACEHOLDER_COLOR = "#94A3B8"
BORDER_COLOR = "#F1F5F9"
BACKGROUND_COLOR = "#F6F8F6"
WHITE = "#FFFFFF"

base_style = {
    "color": TEXT_COLOR,
}

card_style = {
    "width": "480px",
    "max_width": "90%",
    "background_color": WHITE,
    "border": f"1px solid {BORDER_COLOR}",
    "box_shadow": "0px 8px 30px rgba(0, 0, 0, 0.04)",
    "border_radius": "12px",
    "padding": "0px",
}

input_style = {
    "background_color": "#F8FAFC",
    "border": "1px solid #E2E8F0",
    "border_radius": "8px",
    "height": "48px",
    "width": "100%",
    "color": TEXT_COLOR,
    "_placeholder": {"color": PLACEHOLDER_COLOR},
}

label_style = {
    "font_weight": "500",
    "color": LABEL_TEXT_COLOR,
}

button_style = {
    "background_color": PRIMARY_COLOR,
    "box_shadow": f"0px 1px 2px rgba(19, 236, 91, 0.3)",
    "border_radius": "8px",
    "height": "48px",
    "width": "100%",
    "color": TEXT_COLOR,
    "font_weight": "600",
    "_hover": {"opacity": 0.9},
}
