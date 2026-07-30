from PySide6.QtCore import QObject

from models.user import User
from services.account_service import AccountService
from views.accounts_view import AccountsView


class AccountsController(QObject):
    def __init__(
        self,
        view: AccountsView,
        account_service: AccountService,
        current_user: User,
    ) -> None:
        super().__init__()
        self._view = view
        self._account_service = account_service
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

    def _handle_save(self, name: str, balance: float, currency: str) -> None:
        self._view.clear_error()

        if not name:
            self._view.show_error("Informe o nome da conta.")
            return

        account = self._account_service.create(
            user_id=self._current_user.id,
            name=name,
            balance=balance,
            currency=currency,
        )

        if account is None:
            self._view.show_error("Erro ao criar conta.")
            return

        self._view.show_success()
        self.refresh()

    def _handle_update(self, account_id: int, name: str, balance: float, currency: str) -> None:
        self._view.clear_error()

        if not name:
            self._view.show_error("Informe o nome da conta.")
            return

        existing = self._account_service.get_by_id(account_id)
        if existing is None:
            self._view.show_error("Conta não encontrada.")
            return

        existing.name = name
        existing.balance = balance
        existing.currency = currency
        self._account_service.update(existing)

        self._view.show_success()
        self.refresh()

    def _handle_delete(self, account_id: int) -> None:
        self._view.clear_error()
        self._account_service.delete(account_id)
        self._view.clear_form()
        self.refresh()