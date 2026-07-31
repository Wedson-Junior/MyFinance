from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtUiTools import QUiLoader

from config.settings import THEME_DARK, THEME_LIGHT


class SettingsView(QWidget):
    theme_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._updating_theme = False
        self._load_ui()
        self._setup_theme_combo()
        self._connect_signals()

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent.parent / "ui" / "settings.ui"
        loader = QUiLoader()
        self._ui = loader.load(str(ui_path), self)

        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui)

        self._ui.lbl_title.setObjectName("lbl_title")
        self._ui.lbl_subtitle.setObjectName("lbl_subtitle")

    def _setup_theme_combo(self) -> None:
        self._ui.cmb_theme.clear()
        self._ui.cmb_theme.addItem("Escuro", THEME_DARK)
        self._ui.cmb_theme.addItem("Claro", THEME_LIGHT)

    def _connect_signals(self) -> None:
        self._ui.cmb_theme.currentIndexChanged.connect(self._on_theme_changed)

    def _on_theme_changed(self) -> None:
        if self._updating_theme:
            return
        theme = self._ui.cmb_theme.currentData()
        if theme:
            self.theme_changed.emit(theme)

    def set_username(self, username: str) -> None:
        self._ui.lbl_username.setText(username)

    def set_theme(self, theme: str) -> None:
        self._updating_theme = True
        index = self._ui.cmb_theme.findData(theme)
        if index >= 0:
            self._ui.cmb_theme.setCurrentIndex(index)
        self._updating_theme = False