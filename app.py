from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget

from config.settings import (
    WINDOW_TITLE,
    MIN_WIDTH,
    MIN_HEIGHT,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
)
from database.database_manager import DatabaseManager
from services.user_service import UserService
from views.login_view import LoginView
from controllers.login_controller import LoginController
from models.user import User


class App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._db = DatabaseManager()
        self._db.initialize()
        self._user_service = UserService(self._db)
        self._current_user: User | None = None

        self._setup_window()
        self._setup_ui()
        self._show_login()

    def _setup_window(self) -> None:
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)

    def _setup_ui(self) -> None:
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

    def _show_login(self) -> None:
        self._login_view = LoginView()
        self._login_controller = LoginController(self._login_view, self._user_service)
        self._login_controller.login_success.connect(self._on_login_success)

        self._stack.addWidget(self._login_view)
        self._stack.setCurrentWidget(self._login_view)

    def _on_login_success(self, user: User) -> None:
        self._current_user = user
        self.setWindowTitle(f"{WINDOW_TITLE} - {user.username}")
        # Placeholder até o Step 6 (Dashboard)
        from PySide6.QtWidgets import QLabel
        placeholder = QLabel(f"Bem-vindo, {user.username}!\n\nDashboard em breve (Step 6)")
        placeholder.setStyleSheet("font-size: 18pt; color: white;")
        placeholder.setAlignment(placeholder.alignment() | 0x84)
        self._stack.addWidget(placeholder)
        self._stack.setCurrentWidget(placeholder)

    def closeEvent(self, event) -> None:
        self._db.close()
        super().closeEvent(event)