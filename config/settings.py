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

THEME_FILE = STYLES_DIR / "dark.qss"
DATABASE_PATH = DATA_DIR / "myfinance.db"


def load_theme(app: QApplication) -> None:
    if THEME_FILE.exists():
        with open(THEME_FILE, "r", encoding="utf-8") as file:
            app.setStyleSheet(file.read())