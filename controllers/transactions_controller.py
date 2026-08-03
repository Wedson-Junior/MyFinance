from PySide6.QtCore import QObject

from models.user import User
from models.transaction import Transaction
from services.transaction_service import TransactionService
from services.account_service import AccountService
from services.category_service import CategoryService
from views.transactions_view import TransactionsView


class TransactionsController(QObject):
    def __init__(
        self,
        view: TransactionsView,
        transaction_service: TransactionService,
        account_service: AccountService,
        category_service: CategoryService,
        current_user: User,
    ) -> None:
        super().__init__()
        self._view = view
        self._transaction_service = transaction_service
        self._account_service = account_service
        self._category_service = category_service
        self._current_user = current_user
        self._connect_signals()
        self.refresh()

    def _connect_signals(self) -> None:
        self._view.save_requested.connect(self._handle_save)
        self._view.update_requested.connect(self._handle_update)
        self._view.delete_requested.connect(self._handle_delete)
        self._view.clear_requested.connect(self._view.clear_form)
        self._view.type_changed.connect(self._handle_type_changed)

    def refresh(self) -> None:
        accounts = self._account_service.get_by_user(self._current_user.id)
        self._view.set_accounts(accounts)

        all_categories = self._category_service.get_by_user(
            self._current_user.id, include_system=True
        )
        self._view.set_category_names(all_categories)

        transactions = self._transaction_service.get_by_user(self._current_user.id)
        self._view.load_transactions(transactions)

        categories_for_type = self._category_service.get_by_user(
            self._current_user.id, type="income", include_system=False
        )
        self._view.set_categories(categories_for_type)

    def _handle_type_changed(self, category_type: str) -> None:
        categories = self._category_service.get_by_user(
            self._current_user.id, type=category_type, include_system=False
        )
        self._view.set_categories(categories)

    def _handle_save(
        self,
        account_id: int,
        category_id: int,
        transaction_type: str,
        amount: float,
        description: str,
        date: str,
        is_recurring: bool,
    ) -> None:
        self._view.clear_error()

        if not account_id:
            self._view.show_error("Selecione uma conta.")
            return
        if not category_id:
            self._view.show_error("Selecione uma categoria.")
            return
        if transaction_type not in ("income", "expense"):
            self._view.show_error("Tipo inválido.")
            return
        if amount <= 0:
            self._view.show_error("Informe um valor maior que zero.")
            return
        if not date:
            self._view.show_error("Informe a data.")
            return

        transaction = self._transaction_service.create(
            user_id=self._current_user.id,
            account_id=account_id,
            category_id=category_id,
            type=transaction_type,
            amount=amount,
            description=description if description else None,
            date=date,
            is_recurring=is_recurring,
        )

        if transaction is None:
            self._view.show_error("Erro ao criar lançamento.")
            return

        self._view.show_success()
        self.refresh()

    def _handle_update(
        self,
        transaction_id: int,
        account_id: int,
        category_id: int,
        transaction_type: str,
        amount: float,
        description: str,
        date: str,
        is_recurring: bool,
    ) -> None:
        self._view.clear_error()

        if not account_id:
            self._view.show_error("Selecione uma conta.")
            return
        if not category_id:
            self._view.show_error("Selecione uma categoria.")
            return
        if transaction_type not in ("income", "expense"):
            self._view.show_error("Tipo inválido.")
            return
        if amount <= 0:
            self._view.show_error("Informe um valor maior que zero.")
            return

        existing = self._transaction_service.get_by_id(transaction_id)
        if existing is None:
            self._view.show_error("Lançamento não encontrado.")
            return

        existing.account_id = account_id
        existing.category_id = category_id
        existing.type = transaction_type
        existing.amount = amount
        existing.description = description if description else None
        existing.date = date
        existing.is_recurring = is_recurring

        self._transaction_service.update(existing)
        self._view.show_success()
        self.refresh()

    def _handle_delete(self, transaction_id: int) -> None:
        self._view.clear_error()
        self._transaction_service.delete(transaction_id)
        self._view.clear_form()
        self.refresh()