from PySide6.QtCore import QObject, Signal

from models.user import User
from services.account_service import AccountService
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from controllers.accounts_controller import AccountsController
from controllers.categories_controller import CategoriesController
from controllers.transactions_controller import TransactionsController
from views.main_view import MainView


class MainController(QObject):
    logout_requested = Signal()

    def __init__(
        self,
        view: MainView,
        account_service: AccountService,
        category_service: CategoryService,
        transaction_service: TransactionService,
        current_user: User,
    ) -> None:
        super().__init__()
        self._view = view
        self._account_service = account_service
        self._category_service = category_service
        self._transaction_service = transaction_service
        self._current_user = current_user
        self._accounts_controller: AccountsController | None = None
        self._categories_controller: CategoriesController | None = None
        self._transactions_controller: TransactionsController | None = None
        self._connect_signals()
        self._setup_modules()

    def _connect_signals(self) -> None:
        self._view.navigate.connect(self._handle_navigate)
        self._view.logout_requested.connect(self.logout_requested.emit)

    def _setup_modules(self) -> None:
        accounts_view = self._view.get_accounts_view()
        if accounts_view is not None:
            self._accounts_controller = AccountsController(
                accounts_view,
                self._account_service,
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

    def _handle_navigate(self, page: str) -> None:
        self._view.show_page(page)
        if page == "accounts" and self._accounts_controller is not None:
            self._accounts_controller.refresh()
        elif page == "categories" and self._categories_controller is not None:
            self._categories_controller.refresh()
        elif page == "transactions" and self._transactions_controller is not None:
            self._transactions_controller.refresh()