from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtUiTools import QUiLoader

from config.settings import APP_NAME, APP_VERSION


class AboutView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._load_ui()

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent.parent / "ui" / "about.ui"
        loader = QUiLoader()
        self._ui = loader.load(str(ui_path), self)

        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui)

        self._ui.lbl_title.setObjectName("lbl_title")
        self._ui.lbl_subtitle.setObjectName("lbl_subtitle")
        self._ui.lbl_app_name.setText(APP_NAME)
        self._ui.lbl_version.setText(f"Versão {APP_VERSION}")