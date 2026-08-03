from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List, Tuple

from PySide6.QtCore import QObject

from models.user import User
from services.account_service import AccountService
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from views.dashboard_view import DashboardView
from config.settings import get_chart_type
from utils.color_utils import normalize_hex


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
        self._date_from = (date.today().replace(day=1)).isoformat()
        self._date_to = date.today().isoformat()
        self._view.set_filter_dates(self._date_from, self._date_to)
        self._view.filter_requested.connect(self._handle_filter)
        self.refresh()

    def _handle_filter(self, date_from: str, date_to: str) -> None:
        self._date_from = date_from
        self._date_to = date_to
        self._update_chart()

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
        categories_color_map = {
            category.id: normalize_hex(category.color)
            for category in categories
            if category.id is not None
        }

        self._view.load_recent_transactions(
            transactions, categories_map, categories_color_map
        )
        self._update_chart()

    def _update_chart(self) -> None:
        transactions = self._transaction_service.get_by_user(self._current_user.id)
        chart_type = get_chart_type()

        filtered = []
        for transaction in transactions:
            if not transaction.date:
                continue
            if self._date_from and transaction.date < self._date_from:
                continue
            if self._date_to and transaction.date > self._date_to:
                continue
            filtered.append(transaction)

        labels, income_values, expense_values = self._build_daily_series(filtered)
        income_pie, expense_pie = self._build_category_pies(filtered)

        self._view.update_chart(
            chart_type=chart_type,
            labels=labels,
            income_values=income_values,
            expense_values=expense_values,
            income_pie=income_pie,
            expense_pie=expense_pie,
        )

    def _build_daily_series(
        self, transactions: List
    ) -> Tuple[List[str], List[float], List[float]]:
        if not self._date_from or not self._date_to:
            return [], [], []

        start = date.fromisoformat(self._date_from)
        end = date.fromisoformat(self._date_to)
        if start > end:
            start, end = end, start

        income_by_day: Dict[str, float] = defaultdict(float)
        expense_by_day: Dict[str, float] = defaultdict(float)
        for transaction in transactions:
            if transaction.type == "income":
                income_by_day[transaction.date] += transaction.amount
            elif transaction.type == "expense":
                expense_by_day[transaction.date] += transaction.amount

        labels: List[str] = []
        income_values: List[float] = []
        expense_values: List[float] = []
        current = start
        while current <= end:
            key = current.isoformat()
            labels.append(current.strftime("%d/%m"))
            income_values.append(income_by_day.get(key, 0.0))
            expense_values.append(expense_by_day.get(key, 0.0))
            current += timedelta(days=1)

        return labels, income_values, expense_values

    def _build_category_pies(self, transactions: List) -> Tuple[dict, dict]:
        categories = self._category_service.get_by_user(
            self._current_user.id, include_system=True
        )
        names = {
            category.id: category.name
            for category in categories
            if category.id is not None
        }
        colors = {
            category.id: normalize_hex(category.color)
            for category in categories
            if category.id is not None
        }

        income_totals: Dict[int, float] = defaultdict(float)
        expense_totals: Dict[int, float] = defaultdict(float)
        for transaction in transactions:
            if transaction.type == "income":
                income_totals[transaction.category_id] += transaction.amount
            elif transaction.type == "expense":
                expense_totals[transaction.category_id] += transaction.amount

        def to_pie(totals: Dict[int, float]) -> dict:
            sorted_items = sorted(totals.items(), key=lambda item: item[1], reverse=True)
            return {
                "labels": [names.get(category_id, str(category_id)) for category_id, _ in sorted_items],
                "values": [amount for _, amount in sorted_items],
                "colors": [colors.get(category_id, "#718096") for category_id, _ in sorted_items],
            }

        return to_pie(income_totals), to_pie(expense_totals)
