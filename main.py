import sys

from PySide6.QtWidgets import QApplication

from app import App
from config.settings import load_theme


def main() -> None:
    application = QApplication(sys.argv)
    application.setStyle("Fusion")
    load_theme(application)

    window = App()
    window.show()

    sys.exit(application.exec())


if __name__ == "__main__":
    main()