from PySide6.QtWidgets import QMainWindow, QStackedWidget

from config.settings import (
    WINDOW_TITLE,
    MIN_WIDTH,
    MIN_HEIGHT,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
)
from database.database_manager import DatabaseManager
from services.user_service import UserService
from services.account_service import AccountService
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from views.login_view import LoginView
from views.main_view import MainView
from controllers.login_controller import LoginController
from controllers.main_controller import MainController
from models.user import User


class App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._db = DatabaseManager()
        self._db.initialize()
        self._user_service = UserService(self._db)
        self._account_service = AccountService(self._db)
        self._category_service = CategoryService(self._db)
        self._transaction_service = TransactionService(self._db)
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
        self._show_main()

    def _show_main(self) -> None:
        self._main_view = MainView()
        self._main_controller = MainController(
            self._main_view,
            self._account_service,
            self._category_service,
            self._transaction_service,
            self._current_user,
        )
        self._main_controller.logout_requested.connect(self._on_logout)

        self._stack.addWidget(self._main_view)
        self._stack.setCurrentWidget(self._main_view)
        self._main_view.show_page("dashboard")

    def _on_logout(self) -> None:
        self._current_user = None
        self.setWindowTitle(WINDOW_TITLE)

        while self._stack.count() > 0:
            widget = self._stack.widget(0)
            self._stack.removeWidget(widget)
            widget.deleteLater()

        self._show_login()

    def closeEvent(self, event) -> None:
        self._db.close()
        super().closeEvent(event)