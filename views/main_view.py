from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QButtonGroup, QVBoxLayout
from PySide6.QtUiTools import QUiLoader

from config.settings import ICONS_DIR
from views.accounts_view import AccountsView
from views.categories_view import CategoriesView
from views.transactions_view import TransactionsView
from views.dashboard_view import DashboardView


class MainView(QWidget):
    navigate = Signal(str)
    logout_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._accounts_view: AccountsView | None = None
        self._categories_view: CategoriesView | None = None
        self._transactions_view: TransactionsView | None = None
        self._dashboard_view: DashboardView | None = None
        self._load_ui()
        self._setup_icons()
        self._setup_button_group()
        self._setup_dashboard_page()
        self._setup_accounts_page()
        self._setup_categories_page()
        self._setup_transactions_page()
        self._connect_signals()

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent.parent / "ui" / "main_window.ui"
        loader = QUiLoader()
        self._ui = loader.load(str(ui_path), self)

        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui)

        self._ui.lbl_dashboard_title.setObjectName("lbl_title")
        self._ui.lbl_accounts_title.setObjectName("lbl_title")
        self._ui.lbl_transactions_title.setObjectName("lbl_title")
        self._ui.lbl_categories_title.setObjectName("lbl_title")
        self._ui.lbl_reports_title.setObjectName("lbl_title")
        self._ui.lbl_settings_title.setObjectName("lbl_title")
        self._ui.lbl_about_title.setObjectName("lbl_title")
        self._ui.lbl_dashboard_subtitle.setObjectName("lbl_subtitle")

    def _setup_icons(self) -> None:
        icon_map = {
            self._ui.btn_dashboard: "dashbord.ico",
            self._ui.btn_accounts: "banco.ico",
            self._ui.btn_transactions: "movimentacoes.ico",
            self._ui.btn_categories: "banco.ico",
            self._ui.btn_reports: "relatorios.ico",
            self._ui.btn_settings: "configuracoes.ico",
            self._ui.btn_about: "sobre.ico",
            self._ui.btn_logout: "sair.ico",
        }
        for button, filename in icon_map.items():
            icon_path = ICONS_DIR / filename
            if icon_path.exists():
                button.setIcon(QIcon(str(icon_path)))

    def _setup_button_group(self) -> None:
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        buttons = [
            self._ui.btn_dashboard,
            self._ui.btn_accounts,
            self._ui.btn_transactions,
            self._ui.btn_categories,
            self._ui.btn_reports,
            self._ui.btn_settings,
            self._ui.btn_about,
        ]
        for button in buttons:
            self._nav_group.addButton(button)

    def _clear_page(self, page) -> None:
        while page.layout() and page.layout().count():
            item = page.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _setup_dashboard_page(self) -> None:
        page = self._ui.page_dashboard
        self._clear_page(page)
        self._dashboard_view = DashboardView()
        page.layout().addWidget(self._dashboard_view)

    def _setup_accounts_page(self) -> None:
        page = self._ui.page_accounts
        self._clear_page(page)
        self._accounts_view = AccountsView()
        page.layout().addWidget(self._accounts_view)

    def _setup_categories_page(self) -> None:
        page = self._ui.page_categories
        self._clear_page(page)
        self._categories_view = CategoriesView()
        page.layout().addWidget(self._categories_view)

    def _setup_transactions_page(self) -> None:
        page = self._ui.page_transactions
        self._clear_page(page)
        self._transactions_view = TransactionsView()
        page.layout().addWidget(self._transactions_view)

    def _connect_signals(self) -> None:
        self._ui.btn_dashboard.clicked.connect(lambda: self._on_navigate("dashboard"))
        self._ui.btn_accounts.clicked.connect(lambda: self._on_navigate("accounts"))
        self._ui.btn_transactions.clicked.connect(lambda: self._on_navigate("transactions"))
        self._ui.btn_categories.clicked.connect(lambda: self._on_navigate("categories"))
        self._ui.btn_reports.clicked.connect(lambda: self._on_navigate("reports"))
        self._ui.btn_settings.clicked.connect(lambda: self._on_navigate("settings"))
        self._ui.btn_about.clicked.connect(lambda: self._on_navigate("about"))
        self._ui.btn_logout.clicked.connect(self.logout_requested.emit)

    def _on_navigate(self, page: str) -> None:
        self.navigate.emit(page)

    def show_page(self, page: str) -> None:
        page_map = {
            "dashboard": 0,
            "accounts": 1,
            "transactions": 2,
            "categories": 3,
            "reports": 4,
            "settings": 5,
            "about": 6,
        }
        index = page_map.get(page, 0)
        self._ui.stack_content.setCurrentIndex(index)

        button_map = {
            "dashboard": self._ui.btn_dashboard,
            "accounts": self._ui.btn_accounts,
            "transactions": self._ui.btn_transactions,
            "categories": self._ui.btn_categories,
            "reports": self._ui.btn_reports,
            "settings": self._ui.btn_settings,
            "about": self._ui.btn_about,
        }
        button = button_map.get(page)
        if button:
            button.setChecked(True)

    def get_accounts_view(self) -> AccountsView | None:
        return self._accounts_view

    def get_categories_view(self) -> CategoriesView | None:
        return self._categories_view

    def get_transactions_view(self) -> TransactionsView | None:
        return self._transactions_view

    def get_dashboard_view(self) -> DashboardView | None:
        return self._dashboard_view