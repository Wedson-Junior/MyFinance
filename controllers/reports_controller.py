from typing import Optional

from PySide6.QtCore import QObject

from models.user import User
from services.account_service import AccountService
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from views.reports_view import ReportsView


class ReportsController(QObject):
    def __init__(
        self,
        view: ReportsView,
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
        self._connect_signals()
        self.refresh()

    def _connect_signals(self) -> None:
        self._view.filter_requested.connect(self._handle_filter)
        self._view.clear_requested.connect(self._handle_clear)

    def refresh(self) -> None:
        accounts = self._account_service.get_by_user(self._current_user.id)
        categories = self._category_service.get_by_user(self._current_user.id)
        self._view.set_accounts(accounts)
        self._view.set_categories(categories)
        self._apply_filter(None, None, None, None, None)

    def _handle_clear(self) -> None:
        self.refresh()

    def _handle_filter(
        self,
        date_from: str,
        date_to: str,
        transaction_type: Optional[str],
        account_id: Optional[int],
        category_id: Optional[int],
    ) -> None:
        self._apply_filter(date_from, date_to, transaction_type, account_id, category_id)

    def _apply_filter(
        self,
        date_from: Optional[str],
        date_to: Optional[str],
        transaction_type: Optional[str],
        account_id: Optional[int],
        category_id: Optional[int],
    ) -> None:
        transactions = self._transaction_service.get_by_user(self._current_user.id)

        filtered = []
        total_income = 0.0
        total_expense = 0.0

        for transaction in transactions:
            if date_from and transaction.date < date_from:
                continue
            if date_to and transaction.date > date_to:
                continue
            if transaction_type and transaction.type != transaction_type:
                continue
            if account_id is not None and transaction.account_id != account_id:
                continue
            if category_id is not None and transaction.category_id != category_id:
                continue

            filtered.append(transaction)
            if transaction.type == "income":
                total_income += transaction.amount
            elif transaction.type == "expense":
                total_expense += transaction.amount

        accounts = self._account_service.get_by_user(self._current_user.id)
        categories = self._category_service.get_by_user(self._current_user.id)

        accounts_map = {
            account.id: account.name
            for account in accounts
            if account.id is not None
        }
        categories_map = {
            category.id: category.name
            for category in categories
            if category.id is not None
        }

        self._view.load_report(
            filtered, accounts_map, categories_map, total_income, total_expense
        )