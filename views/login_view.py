from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from PySide6.QtUiTools import QUiLoader


class LoginView(QWidget):
    login_requested = Signal(str, str)
    register_requested = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self._load_ui()
        self._connect_signals()

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent.parent / "ui" / "login.ui"
        loader = QUiLoader()
        self._ui = loader.load(str(ui_path), self)

        layout = self.layout()
        if layout is None:
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui)

    def _connect_signals(self) -> None:
        self._ui.btn_login.clicked.connect(self._on_login_clicked)
        self._ui.btn_register.clicked.connect(self._on_register_clicked)
        self._ui.txt_password.returnPressed.connect(self._on_login_clicked)

    def _on_login_clicked(self) -> None:
        username = self._ui.txt_username.text().strip()
        password = self._ui.txt_password.text()
        self.login_requested.emit(username, password)

    def _on_register_clicked(self) -> None:
        username = self._ui.txt_username.text().strip()
        password = self._ui.txt_password.text()
        self.register_requested.emit(username, password)

    def show_error(self, message: str) -> None:
        self._ui.lbl_error.setText(message)

    def clear_error(self) -> None:
        self._ui.lbl_error.setText("")

    def clear_fields(self) -> None:
        self._ui.txt_username.clear()
        self._ui.txt_password.clear()
        self.clear_error()