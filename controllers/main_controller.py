from PySide6.QtCore import QObject, Signal

from models.user import User
from services.account_service import AccountService
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from services.payable_receivable_service import PayableReceivableService
from controllers.accounts_controller import AccountsController
from controllers.categories_controller import CategoriesController
from controllers.transactions_controller import TransactionsController
from controllers.dashboard_controller import DashboardController
from controllers.reports_controller import ReportsController
from controllers.payable_receivable_controller import PayableReceivableController
from views.main_view import MainView
from config.settings import get_current_theme, get_chart_type, set_chart_type


class MainController(QObject):
    logout_requested = Signal()
    theme_change_requested = Signal(str)

    def __init__(
        self,
        view: MainView,
        account_service: AccountService,
        category_service: CategoryService,
        transaction_service: TransactionService,
        payable_service: PayableReceivableService,
        current_user: User,
    ) -> None:
        super().__init__()
        self._view = view
        self._account_service = account_service
        self._category_service = category_service
        self._transaction_service = transaction_service
        self._payable_service = payable_service
        self._current_user = current_user
        self._accounts_controller: AccountsController | None = None
        self._categories_controller: CategoriesController | None = None
        self._transactions_controller: TransactionsController | None = None
        self._dashboard_controller: DashboardController | None = None
        self._reports_controller: ReportsController | None = None
        self._payables_controller: PayableReceivableController | None = None
        self._connect_signals()
        self._setup_modules()

    def _connect_signals(self) -> None:
        self._view.navigate.connect(self._handle_navigate)
        self._view.logout_requested.connect(self.logout_requested.emit)

        settings_view = self._view.get_settings_view()
        if settings_view is not None:
            settings_view.theme_changed.connect(self._handle_theme_changed)
            settings_view.chart_type_changed.connect(self._handle_chart_type_changed)
            settings_view.recalculate_requested.connect(self._handle_recalculate)

    def _setup_modules(self) -> None:
        dashboard_view = self._view.get_dashboard_view()
        if dashboard_view is not None:
            self._dashboard_controller = DashboardController(
                dashboard_view,
                self._account_service,
                self._category_service,
                self._transaction_service,
                self._current_user,
            )

        accounts_view = self._view.get_accounts_view()
        if accounts_view is not None:
            self._accounts_controller = AccountsController(
                accounts_view,
                self._account_service,
                self._category_service,
                self._transaction_service,
                self._current_user,
            )

        categories_view = self._view.get_categories_view()
        if categories_view is not None:
            self._categories_controller = CategoriesController(
                categories_view,
                self._category_service,
                self._current_user,
            )

        transactions_view = self._view.get_transactions_view()
        if transactions_view is not None:
            self._transactions_controller = TransactionsController(
                transactions_view,
                self._transaction_service,
                self._account_service,
                self._category_service,
                self._current_user,
            )

        reports_view = self._view.get_reports_view()
        if reports_view is not None:
            self._reports_controller = ReportsController(
                reports_view,
                self._account_service,
                self._category_service,
                self._transaction_service,
                self._current_user,
            )

        payables_view = self._view.get_payables_view()
        if payables_view is not None:
            self._payables_controller = PayableReceivableController(
                payables_view,
                self._payable_service,
                self._account_service,
                self._category_service,
                self._current_user,
            )

        settings_view = self._view.get_settings_view()
        if settings_view is not None:
            settings_view.set_username(self._current_user.username)
            settings_view.set_theme(get_current_theme())
            settings_view.set_chart_type(get_chart_type())

    def _handle_theme_changed(self, theme: str) -> None:
        self.theme_change_requested.emit(theme)
        if self._dashboard_controller is not None:
            self._dashboard_controller.refresh()

    def _handle_chart_type_changed(self, chart_type: str) -> None:
        set_chart_type(chart_type)
        if self._dashboard_controller is not None:
            self._dashboard_controller.refresh()

    def _handle_recalculate(self) -> None:
        self._transaction_service.recalculate_account_balances(self._current_user.id)
        self._payable_service.recalculate_all(self._current_user.id)
        settings_view = self._view.get_settings_view()
        if settings_view is not None:
            settings_view.show_recalculate_success()
        if self._accounts_controller is not None:
            self._accounts_controller.refresh()
        if self._payables_controller is not None:
            self._payables_controller.refresh()
        if self._dashboard_controller is not None:
            self._dashboard_controller.refresh()

    def _handle_navigate(self, page: str) -> None:
        self._view.show_page(page)
        if page == "dashboard" and self._dashboard_controller is not None:
            self._dashboard_controller.refresh()
        elif page == "accounts" and self._accounts_controller is not None:
            self._accounts_controller.refresh()
        elif page == "categories" and self._categories_controller is not None:
            self._categories_controller.refresh()
        elif page == "transactions" and self._transactions_controller is not None:
            self._transactions_controller.refresh()
        elif page == "reports" and self._reports_controller is not None:
            self._reports_controller.refresh()