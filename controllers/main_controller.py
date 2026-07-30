from PySide6.QtCore import QObject, Signal

from views.main_view import MainView


class MainController(QObject):
    logout_requested = Signal()

    def __init__(self, view: MainView) -> None:
        super().__init__()
        self._view = view
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._view.navigate.connect(self._handle_navigate)
        self._view.logout_requested.connect(self.logout_requested.emit)

    def _handle_navigate(self, page: str) -> None:
        self._view.show_page(page)