import json
from pathlib import Path

from PySide6.QtWidgets import QApplication


BASE_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = BASE_DIR / "resources"
STYLES_DIR = RESOURCES_DIR / "styles"
ICONS_DIR = RESOURCES_DIR / "icons"
IMAGES_DIR = RESOURCES_DIR / "images"
DATA_DIR = BASE_DIR / "data"

APP_NAME = "MyFinance"
APP_VERSION = "0.1.0"
WINDOW_TITLE = "MyFinance"
MIN_WIDTH = 1024
MIN_HEIGHT = 600
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720

THEME_DARK = "dark"
THEME_LIGHT = "light"
THEME_FILES = {
    THEME_DARK: STYLES_DIR / "dark.qss",
    THEME_LIGHT: STYLES_DIR / "light.qss",
}
PREFERENCES_FILE = DATA_DIR / "preferences.json"
DATABASE_PATH = DATA_DIR / "myfinance.db"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_preferences() -> dict:
    _ensure_data_dir()
    if not PREFERENCES_FILE.exists():
        return {"theme": THEME_DARK}
    try:
        with open(PREFERENCES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data, dict):
                return {"theme": THEME_DARK}
            return data
    except (json.JSONDecodeError, OSError):
        return {"theme": THEME_DARK}


def save_preferences(preferences: dict) -> None:
    _ensure_data_dir()
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as file:
        json.dump(preferences, file, indent=2)


def get_current_theme() -> str:
    preferences = load_preferences()
    theme = preferences.get("theme", THEME_DARK)
    if theme not in THEME_FILES:
        return THEME_DARK
    return theme


def set_current_theme(theme: str) -> None:
    if theme not in THEME_FILES:
        theme = THEME_DARK
    preferences = load_preferences()
    preferences["theme"] = theme
    save_preferences(preferences)


def apply_theme(app: QApplication, theme: str | None = None) -> None:
    if theme is None:
        theme = get_current_theme()
    if theme not in THEME_FILES:
        theme = THEME_DARK

    theme_file = THEME_FILES[theme]
    if theme_file.exists():
        with open(theme_file, "r", encoding="utf-8") as file:
            app.setStyleSheet(file.read())
    else:
        app.setStyleSheet("")


def load_theme(app: QApplication) -> None:
    apply_theme(app)