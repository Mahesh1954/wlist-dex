"""
FILE: constants.py
PURPOSE: App settings - RED NEON TRON ARES Theme
"""

APP_TITLE = "W-LIST"
APP_WIDTH = 950
APP_HEIGHT = 750
APP_ICON = None

# RED NEON TRON ARES Theme
COLORS = {
    # Primary Red Neon
    "primary": "#FF0033",        # Bright Red Neon
    "primary_light": "#FF3366",   # Light Red
    "primary_dark": "#CC0029",   # Dark Red
    
    # Secondary
    "secondary": "#FF6600",       # Orange Red
    "secondary_light": "#FF9933",
    "secondary_dark": "#CC5200",
    
    # Accent
    "accent": "#FF0000",         # Pure Red
    "accent_light": "#FF3333",
    
    # Background Colors (Dark)
    "bg_main": "#0D0D0D",        # Deep Black
    "bg_card": "#1A1A1A",        # Dark Gray
    "bg_secondary": "#141414",   # Slightly lighter
    "bg_input": "#1F0000",       # Red tinted dark
    
    # Text Colors
    "text_primary": "#FFFFFF",    # White
    "text_secondary": "#AA4444", # Muted Red
    "text_light": "#FF6666",     # Light Red Text
    "text_dark": "#000000",      # Black
    
    # Status Colors (Red/Orange versions)
    "success": "#00FF66",        # Green (keep for completed)
    "warning": "#FFAA00",        # Orange
    "danger": "#FF0033",         # Red
    "info": "#00AAFF",           # Blue (for contrast)
    "purple": "#AA00FF",         # Purple
    
    # Border/Glow
    "border": "#330000",         # Dark Red
    "border_focus": "#FF0033",   # Bright Red
}

# Fonts
FONTS = {
    "title": ("Courier New", 28, "bold"),
    "heading": ("Courier New", 16, "bold"),
    "subheading": ("Courier New", 14, "bold"),
    "normal": ("Courier New", 12),
    "small": ("Courier New", 10),
    "button": ("Courier New", 11, "bold"),
    "money": ("Courier New", 14, "bold"),
    "percentage": ("Courier New", 12, "bold"),
}

BUTTON_WIDTH = 15
BUTTON_HEIGHT = 2

CURRENCY_SYMBOL = "Rs"
CURRENCY_DECIMAL_PLACES = 2
