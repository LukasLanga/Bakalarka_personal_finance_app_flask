# In frontend/frontendApp/styles.py

# This is the primary brand color. It's used for important buttons and links.
PRIMARY_COLOR = "#13EC5B"

# These color constants are no longer recommended for theme-aware apps.
# It's better to use Radix color schemes (e.g., color_scheme="gray")
# or theme variables (e.g., "var(--gray-11)") in your components.
# TEXT_COLOR = "#0F172A"
# LABEL_TEXT_COLOR = "#334155"
# SUBTLE_TEXT_COLOR = "#64748B"
# PLACEHOLDER_COLOR = "#94A3B8"
# BORDER_COLOR = "#F1F5F9"
# BACKGROUND_COLOR = "#F6F8F6"
# WHITE = "#FFFFFF"

# A base_style is no longer needed, as the rx.theme component handles
# global styles much more effectively for both light and dark modes.

card_style = {
    "width": "480px",
    "max_width": "90%",
    "border_radius": "12px",
    "padding": "0px",
    # In dark mode, the theme will apply a subtle background and border automatically.
    # In light mode, it will be white with a faint border.
}

input_style = {
    "border_radius": "8px",
    "height": "48px",
    "width": "100%",
}

label_style = {
    "font_weight": "500",
}

button_style = {
    "background_color": PRIMARY_COLOR,
    "box_shadow": f"0px 1px 2px rgba(19, 236, 91, 0.3)",
    "border_radius": "8px",
    "height": "48px",
    "width": "100%",
    "color": "#0F172A",
    "font_weight": "600",
    "_hover": {"opacity": 0.9},
}
