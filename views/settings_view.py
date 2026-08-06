from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtUiTools import QUiLoader

from config.settings import (
    THEME_DARK,
    THEME_LIGHT,
    CHART_TYPES,
)


class SettingsView(QWidget):
    theme_changed = Signal(str)
    chart_type_changed = Signal(str)
    recalculate_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._updating_theme = False
        self._updating_chart = False
        self._load_ui()
        self._setup_theme_combo()
        self._setup_chart_combo()
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

    def _setup_chart_combo(self) -> None:
        self._ui.cmb_chart_type.clear()
        for key, label in CHART_TYPES.items():
            self._ui.cmb_chart_type.addItem(label, key)

    def _connect_signals(self) -> None:
        self._ui.cmb_theme.currentIndexChanged.connect(self._on_theme_changed)
        self._ui.cmb_chart_type.currentIndexChanged.connect(self._on_chart_type_changed)
        self._ui.btn_recalculate.clicked.connect(self._on_recalculate)

    def _on_theme_changed(self) -> None:
        if self._updating_theme:
            return
        theme = self._ui.cmb_theme.currentData()
        if theme:
            self.theme_changed.emit(theme)

    def _on_chart_type_changed(self) -> None:
        if self._updating_chart:
            return
        chart_type = self._ui.cmb_chart_type.currentData()
        if chart_type:
            self.chart_type_changed.emit(chart_type)

    def _on_recalculate(self) -> None:
        reply = QMessageBox.question(
            self,
            "Recalcular saldos",
            "Recalcular todos os saldos das contas e das notas a prazo?\n\n"
            "Esta operação é segura e pode ser executada quantas vezes for necessário.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._ui.lbl_recalculate_status.setText("Recalculando...")
            self.recalculate_requested.emit()

    def set_username(self, username: str) -> None:
        self._ui.lbl_username.setText(username)

    def set_theme(self, theme: str) -> None:
        self._updating_theme = True
        index = self._ui.cmb_theme.findData(theme)
        if index >= 0:
            self._ui.cmb_theme.setCurrentIndex(index)
        self._updating_theme = False

    def set_chart_type(self, chart_type: str) -> None:
        self._updating_chart = True
        index = self._ui.cmb_chart_type.findData(chart_type)
        if index >= 0:
            self._ui.cmb_chart_type.setCurrentIndex(index)
        self._updating_chart = False

    def show_recalculate_success(self) -> None:
        self._ui.lbl_recalculate_status.setText("Saldos recalculados com sucesso.")
        QMessageBox.information(
            self,
            "Recálculo concluído",
            "Saldos das contas e notas a prazo foram recalculados.",
        )
