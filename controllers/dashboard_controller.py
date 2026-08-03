from datetime import date

from PySide6.QtCore import QObject

from models.user import User
from services.account_service import AccountService
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from views.dashboard_view import DashboardView


class DashboardController(QObject):
    def __init__(
        self,
        view: DashboardView,
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
        self.refresh()

    def refresh(self) -> None:
        accounts = self._account_service.get_by_user(self._current_user.id)
        total_balance = sum(account.balance for account in accounts)
        accounts_count = len(accounts)

        transactions = self._transaction_service.get_by_user(self._current_user.id)
        today = date.today()
        year_month = today.strftime("%Y-%m")

        monthly_income = 0.0
        monthly_expense = 0.0
        for transaction in transactions:
            if not transaction.date or not transaction.date.startswith(year_month):
                continue
            if transaction.type == "income":
                monthly_income += transaction.amount
            elif transaction.type == "expense":
                monthly_expense += transaction.amount

        self._view.set_summary(
            total_balance=total_balance,
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            accounts_count=accounts_count,
        )

        categories = self._category_service.get_by_user(
            self._current_user.id, include_system=True
        )
        categories_map = {
            category.id: category.name
            for category in categories
            if category.id is not None
        }

        self._view.load_recent_transactions(transactions, categories_map)