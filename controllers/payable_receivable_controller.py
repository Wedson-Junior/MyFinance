from PySide6.QtCore import QObject

from models.user import User
from services.payable_receivable_service import PayableReceivableService
from services.account_service import AccountService
from services.category_service import CategoryService
from views.payable_receivable_view import PayableReceivableView


class PayableReceivableController(QObject):
    def __init__(
        self,
        view: PayableReceivableView,
        payable_service: PayableReceivableService,
        account_service: AccountService,
        category_service: CategoryService,
        current_user: User,
    ) -> None:
        super().__init__()
        self._view = view
        self._payable_service = payable_service
        self._account_service = account_service
        self._category_service = category_service
        self._current_user = current_user
        self._connect_signals()
        self.refresh()

    def _connect_signals(self) -> None:
        self._view.save_requested.connect(self._handle_save)
        self._view.update_requested.connect(self._handle_update)
        self._view.delete_requested.connect(self._handle_delete)
        self._view.payment_requested.connect(self._handle_payment)
        self._view.clear_requested.connect(self._view.clear_form)
        self._view.type_changed.connect(self._handle_type_changed)

    def refresh(self) -> None:
        accounts = self._account_service.get_by_user(self._current_user.id)
        self._view.set_accounts(accounts)
        expense_categories = self._category_service.get_by_user(
            self._current_user.id, type="expense", include_system=False
        )
        income_categories = self._category_service.get_by_user(
            self._current_user.id, type="income", include_system=False
        )
        self._view.set_category_lists(expense_categories, income_categories)
        items = self._payable_service.get_by_user(self._current_user.id)
        self._view.load_items(items)

    def _handle_type_changed(self, note_type: str) -> None:
        category_type = "expense" if note_type == "payable" else "income"
        categories = self._category_service.get_by_user(
            self._current_user.id, type=category_type, include_system=False
        )
        self._view.set_categories(categories)

    def _handle_save(
        self,
        note_type: str,
        description: str,
        amount: float,
        due_date: str,
        account_id,
        category_id,
        notes: str,
    ) -> None:
        self._view.clear_error()
        if not description:
            self._view.show_error("Informe a descrição.")
            return
        if amount <= 0:
            self._view.show_error("Informe um valor maior que zero.")
            return
        if not due_date:
            self._view.show_error("Informe a data de vencimento.")
            return
        if note_type not in ("payable", "receivable"):
            self._view.show_error("Tipo inválido.")
            return
        if not account_id:
            self._view.show_error("Selecione a conta bancária.")
            return
        if not category_id:
            self._view.show_error("Selecione a categoria.")
            return

        item = self._payable_service.create(
            user_id=self._current_user.id,
            type=note_type,
            description=description,
            original_amount=amount,
            due_date=due_date,
            account_id=account_id,
            category_id=category_id,
            notes=notes if notes else None,
        )
        if item is None:
            self._view.show_error("Erro ao criar nota.")
            return
        self._view.show_success()
        self.refresh()

    def _handle_update(
        self,
        item_id: int,
        note_type: str,
        description: str,
        amount: float,
        due_date: str,
        account_id,
        category_id,
        notes: str,
    ) -> None:
        self._view.clear_error()
        existing = self._payable_service.get_by_id(item_id)
        if existing is None:
            self._view.show_error("Nota não encontrada.")
            return
        if not description:
            self._view.show_error("Informe a descrição.")
            return
        if amount <= 0:
            self._view.show_error("Informe um valor maior que zero.")
            return
        if not account_id:
            self._view.show_error("Selecione a conta bancária.")
            return
        if not category_id:
            self._view.show_error("Selecione a categoria.")
            return

        existing.type = note_type
        existing.description = description
        existing.original_amount = amount
        existing.due_date = due_date
        existing.account_id = account_id
        existing.category_id = category_id
        existing.notes = notes if notes else None
        existing.remaining_amount = max(amount - existing.paid_amount, 0.0)
        self._payable_service.update(existing)
        self._payable_service.refresh_amounts(item_id)
        self._view.show_success()
        self.refresh()

    def _handle_delete(self, item_id: int) -> None:
        self._view.clear_error()
        self._payable_service.delete(item_id)
        self._view.clear_form()
        self.refresh()

    def _handle_payment(
        self,
        item_id: int,
        amount: float,
        payment_date: str,
        account_id: int,
        category_id: int,
    ) -> None:
        self._view.clear_error()
        if amount <= 0:
            self._view.show_error("Informe o valor.")
            return
        if not account_id:
            self._view.show_error("Selecione a conta bancária.")
            return
        if not category_id:
            self._view.show_error("Selecione a categoria da movimentação.")
            return

        item = self._payable_service.get_by_id(item_id)
        if item is None:
            self._view.show_error("Nota não encontrada.")
            return
        if item.status == "settled":
            self._view.show_error("Esta nota já está quitada.")
            return
        if item.status == "cancelled":
            self._view.show_error("Esta nota está cancelada.")
            return
        if amount > item.remaining_amount + 0.0001:
            self._view.show_error("Valor maior que o restante da nota.")
            return

        category_type = "expense" if item.type == "payable" else "income"
        categories = self._category_service.get_by_user(
            self._current_user.id, type=category_type, include_system=False
        )
        valid_ids = {c.id for c in categories}
        if category_id not in valid_ids:
            self._view.show_error("Categoria inválida para o tipo da nota.")
            return

        ok = self._payable_service.add_haver(
            item_id=item_id,
            user_id=self._current_user.id,
            account_id=account_id,
            category_id=category_id,
            amount=amount,
            payment_date=payment_date,
        )
        if not ok:
            self._view.show_error("Não foi possível registrar a movimentação.")
            return
        self._view.show_success()
        self.refresh()
