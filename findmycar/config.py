from kivy.utils import get_color_from_hex

APP_NAME = "FindMyCar"
APP_VERSION = "1.0.0"

PRIMARY = get_color_from_hex("#1a237e")
PRIMARY_LIGHT = get_color_from_hex("#534bae")
PRIMARY_DARK = get_color_from_hex("#000051")
ACCENT = get_color_from_hex("#00e5ff")
BACKGROUND = get_color_from_hex("#0d1117")
SURFACE = get_color_from_hex("#161b22")
SURFACE_LIGHT = get_color_from_hex("#1c2333")
ERROR = get_color_from_hex("#cf6679")
ON_PRIMARY = get_color_from_hex("#ffffff")
ON_BACKGROUND = get_color_from_hex("#c9d1d9")
ON_SURFACE = get_color_from_hex("#c9d1d9")

THEME = {
    "primary": PRIMARY,
    "primary_light": PRIMARY_LIGHT,
    "primary_dark": PRIMARY_DARK,
    "accent": ACCENT,
    "background": BACKGROUND,
    "surface": SURFACE,
    "surface_light": SURFACE_LIGHT,
    "error": ERROR,
    "on_primary": ON_PRIMARY,
    "on_background": ON_BACKGROUND,
    "on_surface": ON_SURFACE,
}

SENSOR_UPDATE_INTERVAL = 0.1
POSITION_UPDATE_INTERVAL = 1.0

STORAGE_FILE = "parking_data.json"
