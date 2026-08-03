from datetime import date

from PySide6.QtCore import QObject

from models.user import User
from services.account_service import AccountService
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from views.accounts_view import AccountsView

INITIAL_BALANCE_CATEGORY = "Saldo inicial"


class AccountsController(QObject):
    def __init__(
        self,
        view: AccountsView,
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
        self._view.save_requested.connect(self._handle_save)
        self._view.update_requested.connect(self._handle_update)
        self._view.delete_requested.connect(self._handle_delete)
        self._view.clear_requested.connect(self._view.clear_form)

    def refresh(self) -> None:
        accounts = self._account_service.get_by_user(self._current_user.id)
        self._view.load_accounts(accounts)

    def _handle_save(self, name: str, initial_amount: float, currency: str) -> None:
        self._view.clear_error()

        if not name:
            self._view.show_error("Informe o nome da conta.")
            return

        account = self._account_service.create(
            user_id=self._current_user.id,
            name=name,
            balance=0.0,
            currency=currency,
        )

        if account is None:
            self._view.show_error("Erro ao criar conta.")
            return

        if initial_amount > 0:
            category = self._category_service.get_or_create(
                user_id=self._current_user.id,
                name=INITIAL_BALANCE_CATEGORY,
                type="income",
                color="#2B6CB0",
            )
            if category is None:
                self._view.show_error("Conta criada, mas falhou ao registrar o saldo inicial.")
                self.refresh()
                return

            transaction = self._transaction_service.create(
                user_id=self._current_user.id,
                account_id=account.id,
                category_id=category.id,
                type="income",
                amount=initial_amount,
                description="Saldo inicial da conta",
                date=date.today().isoformat(),
                is_recurring=False,
            )
            if transaction is None:
                self._view.show_error("Conta criada, mas falhou ao registrar o saldo inicial.")
                self.refresh()
                return

        self._view.show_success()
        self.refresh()

    def _handle_update(self, account_id: int, name: str, currency: str) -> None:
        self._view.clear_error()

        if not name:
            self._view.show_error("Informe o nome da conta.")
            return

        existing = self._account_service.get_by_id(account_id)
        if existing is None:
            self._view.show_error("Conta não encontrada.")
            return

        existing.name = name
        existing.currency = currency
        self._account_service.update(existing)

        self._view.show_success()
        self.refresh()

    def _handle_delete(self, account_id: int) -> None:
        self._view.clear_error()
        self._account_service.delete(account_id)
        self._view.clear_form()
        self.refresh()
