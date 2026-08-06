from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Signal, Qt, QDate
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QDialog,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QDateEdit,
    QPushButton,
    QFormLayout,
    QDialogButtonBox,
)
from PySide6.QtUiTools import QUiLoader

from models.payable_receivable import PayableReceivable
from models.bank_account import BankAccount
from models.category import Category


STATUS_LABELS = {
    "pending": "Pendente",
    "partial": "Parcial",
    "settled": "Quitado",
    "overdue": "Vencido",
    "cancelled": "Cancelado",
}


class PaymentDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        title: str,
        accounts: List[BankAccount],
        categories: List[Category],
        remaining: float,
        amount_locked: bool,
        default_account_id: Optional[int] = None,
        default_category_id: Optional[int] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._cmb_account = QComboBox()
        self._cmb_account.setMinimumHeight(36)
        for account in accounts:
            self._cmb_account.addItem(account.name, account.id)
        if default_account_id is not None:
            index = self._cmb_account.findData(default_account_id)
            if index >= 0:
                self._cmb_account.setCurrentIndex(index)
        self._cmb_account.setEnabled(False)

        self._cmb_category = QComboBox()
        self._cmb_category.setMinimumHeight(36)
        for category in categories:
            self._cmb_category.addItem(category.name, category.id)
        if default_category_id is not None:
            index = self._cmb_category.findData(default_category_id)
            if index >= 0:
                self._cmb_category.setCurrentIndex(index)
        self._cmb_category.setEnabled(False)

        self._spn_amount = QDoubleSpinBox()
        self._spn_amount.setPrefix("R$ ")
        self._spn_amount.setDecimals(2)
        self._spn_amount.setMaximum(999999999.99)
        self._spn_amount.setMinimumHeight(36)
        self._spn_amount.setValue(remaining if amount_locked else 0.0)
        self._spn_amount.setEnabled(not amount_locked)
        if not amount_locked and remaining > 0:
            self._spn_amount.setMaximum(remaining)

        self._date_payment = QDateEdit()
        self._date_payment.setCalendarPopup(True)
        self._date_payment.setDisplayFormat("dd/MM/yyyy")
        self._date_payment.setDate(QDate.currentDate())
        self._date_payment.setMinimumHeight(36)

        form.addRow("Conta bancária", self._cmb_account)
        form.addRow("Categoria", self._cmb_category)
        form.addRow("Valor", self._spn_amount)
        form.addRow("Data", self._date_payment)
        layout.addLayout(form)

        if amount_locked:
            layout.addWidget(QLabel(f"Valor restante a quitar: R$ {remaining:,.2f}"))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def payment_data(self) -> tuple:
        return (
            self._spn_amount.value(),
            self._date_payment.date().toString("yyyy-MM-dd"),
            self._cmb_account.currentData(),
            self._cmb_category.currentData(),
        )


class PayableReceivableView(QWidget):
    save_requested = Signal(str, str, float, str, object, object, str)
    update_requested = Signal(int, str, str, float, str, object, object, str)
    delete_requested = Signal(int)
    payment_requested = Signal(int, float, str, int, int)
    clear_requested = Signal()
    type_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._editing_id: Optional[int] = None
        self._accounts: List[BankAccount] = []
        self._categories: List[Category] = []
        self._expense_categories: List[Category] = []
        self._income_categories: List[Category] = []
        self._load_ui()
        self._setup_combos()
        self._setup_table()
        self._connect_signals()

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent.parent / "ui" / "payable_receivable.ui"
        loader = QUiLoader()
        self._ui = loader.load(str(ui_path), self)
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui)
        self._ui.lbl_title.setObjectName("lbl_title")
        self._ui.lbl_subtitle.setObjectName("lbl_subtitle")
        self._ui.date_due.setDate(QDate.currentDate())

    def _setup_combos(self) -> None:
        self._ui.cmb_type.clear()
        self._ui.cmb_type.addItem("A pagar", "payable")
        self._ui.cmb_type.addItem("A receber", "receivable")

    def _setup_table(self) -> None:
        header = self._ui.tbl_items.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        for col in range(3, 9):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self._ui.tbl_items.setColumnHidden(0, True)

    def _connect_signals(self) -> None:
        self._ui.btn_save.clicked.connect(self._on_save)
        self._ui.btn_clear.clicked.connect(self._on_clear)
        self._ui.btn_edit.clicked.connect(self._on_edit)
        self._ui.btn_delete.clicked.connect(self._on_delete)
        self._ui.btn_haver.clicked.connect(lambda: self._open_payment_dialog(False))
        self._ui.btn_settle.clicked.connect(lambda: self._open_payment_dialog(True))
        self._ui.cmb_type.currentIndexChanged.connect(self._on_type_changed)

    def _on_type_changed(self) -> None:
        note_type = self._ui.cmb_type.currentData()
        if note_type:
            self.type_changed.emit(note_type)

    def _selected_row_data(self) -> Optional[dict]:
        row = self._ui.tbl_items.currentRow()
        if row < 0:
            return None
        return {
            "id": int(self._ui.tbl_items.item(row, 0).text()),
            "type": self._ui.tbl_items.item(row, 1).data(Qt.UserRole),
            "description": self._ui.tbl_items.item(row, 2).text(),
            "remaining": float(self._ui.tbl_items.item(row, 5).text().replace("R$ ", "").replace(".", "").replace(",", ".") )
            if False else self._ui.tbl_items.item(row, 5).data(Qt.UserRole),
            "status": self._ui.tbl_items.item(row, 7).text(),
            "account_id": self._ui.tbl_items.item(row, 0).data(Qt.UserRole + 1),
            "category_id": self._ui.tbl_items.item(row, 0).data(Qt.UserRole + 2),
        }

    def _open_payment_dialog(self, settle: bool) -> None:
        row = self._ui.tbl_items.currentRow()
        if row < 0:
            self.show_error("Selecione uma nota na tabela.")
            return

        item_id = int(self._ui.tbl_items.item(row, 0).text())
        remaining = self._ui.tbl_items.item(row, 5).data(Qt.UserRole)
        if remaining is None:
            remaining = 0.0
        remaining = float(remaining)
        status_label = self._ui.tbl_items.item(row, 7).text()
        if status_label == STATUS_LABELS["settled"]:
            self.show_error("Esta nota já está quitada.")
            return
        if status_label == STATUS_LABELS["cancelled"]:
            self.show_error("Esta nota está cancelada.")
            return
        if remaining <= 0:
            self.show_error("Não há valor restante nesta nota.")
            return
        if not self._accounts:
            self.show_error("Cadastre uma conta bancária antes.")
            return
        note_type = self._ui.tbl_items.item(row, 1).data(Qt.UserRole)
        payment_categories = (
            self._income_categories if note_type == "receivable" else self._expense_categories
        )
        if not payment_categories:
            self.show_error("Cadastre uma categoria antes.")
            return

        default_account_id = self._ui.tbl_items.item(row, 0).data(Qt.UserRole + 1)
        default_category_id = self._ui.tbl_items.item(row, 0).data(Qt.UserRole + 2)
        if default_account_id is None:
            self.show_error("Defina a conta bancária na nota antes de haver ou quitar.")
            return
        if default_category_id is None:
            self.show_error("Defina a categoria na nota antes de haver ou quitar.")
            return
        title = "Quitar nota" if settle else "Registrar haver"

        dialog = PaymentDialog(
            self,
            title=title,
            accounts=self._accounts,
            categories=payment_categories,
            remaining=remaining,
            amount_locked=settle,
            default_account_id=default_account_id,
            default_category_id=default_category_id,
        )
        if dialog.exec() != QDialog.Accepted:
            return

        amount, payment_date, account_id, category_id = dialog.payment_data()
        if not account_id:
            self.show_error("Selecione a conta bancária.")
            return
        if not category_id:
            self.show_error("Selecione a categoria da movimentação.")
            return
        if amount <= 0:
            self.show_error("Informe um valor maior que zero.")
            return

        self.payment_requested.emit(
            item_id,
            amount,
            payment_date,
            int(account_id),
            int(category_id),
        )

    def _on_save(self) -> None:
        note_type = self._ui.cmb_type.currentData() or "payable"
        description = self._ui.txt_description.text().strip()
        amount = self._ui.spn_amount.value()
        due_date = self._ui.date_due.date().toString("yyyy-MM-dd")
        account_id = self._ui.cmb_account.currentData()
        category_id = self._ui.cmb_category.currentData()
        notes = self._ui.txt_notes.text().strip()
        if self._editing_id is not None:
            self.update_requested.emit(
                self._editing_id,
                note_type,
                description,
                amount,
                due_date,
                account_id,
                category_id,
                notes,
            )
        else:
            self.save_requested.emit(
                note_type,
                description,
                amount,
                due_date,
                account_id,
                category_id,
                notes,
            )

    def _on_clear(self) -> None:
        self.clear_form()
        self.clear_requested.emit()

    def _on_edit(self) -> None:
        row = self._ui.tbl_items.currentRow()
        if row < 0:
            self.show_error("Selecione uma nota para editar.")
            return
        item_id = int(self._ui.tbl_items.item(row, 0).text())
        note_type = self._ui.tbl_items.item(row, 1).data(Qt.UserRole)
        description = self._ui.tbl_items.item(row, 2).text()
        amount = self._ui.tbl_items.item(row, 3).data(Qt.UserRole)
        due_date = self._ui.tbl_items.item(row, 6).data(Qt.UserRole)
        notes = self._ui.tbl_items.item(row, 8).text()
        account_id = self._ui.tbl_items.item(row, 0).data(Qt.UserRole + 1)
        category_id = self._ui.tbl_items.item(row, 0).data(Qt.UserRole + 2)

        self._editing_id = item_id
        type_index = self._ui.cmb_type.findData(note_type)
        if type_index >= 0:
            self._ui.cmb_type.setCurrentIndex(type_index)
        self._ui.txt_description.setText(description)
        self._ui.spn_amount.setValue(float(amount) if amount is not None else 0.0)
        if due_date:
            self._ui.date_due.setDate(QDate.fromString(due_date, "yyyy-MM-dd"))
        if account_id is not None:
            idx = self._ui.cmb_account.findData(account_id)
            if idx >= 0:
                self._ui.cmb_account.setCurrentIndex(idx)
        if category_id is not None:
            idx = self._ui.cmb_category.findData(category_id)
            if idx >= 0:
                self._ui.cmb_category.setCurrentIndex(idx)
        self._ui.txt_notes.setText(notes)
        self._ui.btn_save.setText("Atualizar")
        self.clear_error()

    def _on_delete(self) -> None:
        row = self._ui.tbl_items.currentRow()
        if row < 0:
            self.show_error("Selecione uma nota para excluir.")
            return
        description = self._ui.tbl_items.item(row, 2).text()
        reply = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Deseja excluir a nota \"{description}\"?\n\n"
            "Todas as movimentações vinculadas também serão excluídas "
            "e os saldos revertidos.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        item_id = int(self._ui.tbl_items.item(row, 0).text())
        self.delete_requested.emit(item_id)

    def set_accounts(self, accounts: List[BankAccount]) -> None:
        self._accounts = list(accounts)
        current = self._ui.cmb_account.currentData()
        self._ui.cmb_account.clear()
        self._ui.cmb_account.addItem("Conta bancária", None)
        for account in accounts:
            self._ui.cmb_account.addItem(account.name, account.id)
        if current is not None:
            index = self._ui.cmb_account.findData(current)
            if index >= 0:
                self._ui.cmb_account.setCurrentIndex(index)

    def set_category_lists(
        self,
        expense_categories: List[Category],
        income_categories: List[Category],
    ) -> None:
        self._expense_categories = list(expense_categories)
        self._income_categories = list(income_categories)
        note_type = self._ui.cmb_type.currentData() or "payable"
        if note_type == "receivable":
            self.set_categories(income_categories)
        else:
            self.set_categories(expense_categories)

    def set_categories(self, categories: List[Category]) -> None:
        self._categories = list(categories)
        current = self._ui.cmb_category.currentData()
        self._ui.cmb_category.clear()
        self._ui.cmb_category.addItem("Categoria", None)
        for category in categories:
            self._ui.cmb_category.addItem(category.name, category.id)
        if current is not None:
            index = self._ui.cmb_category.findData(current)
            if index >= 0:
                self._ui.cmb_category.setCurrentIndex(index)

    def load_items(self, items: List[PayableReceivable]) -> None:
        self._ui.tbl_items.setRowCount(0)
        for item in items:
            row = self._ui.tbl_items.rowCount()
            self._ui.tbl_items.insertRow(row)

            id_item = QTableWidgetItem(str(item.id))
            id_item.setData(Qt.UserRole + 1, item.account_id)
            id_item.setData(Qt.UserRole + 2, item.category_id)
            self._ui.tbl_items.setItem(row, 0, id_item)

            type_label = "A pagar" if item.type == "payable" else "A receber"
            type_item = QTableWidgetItem(type_label)
            type_item.setData(Qt.UserRole, item.type)
            self._ui.tbl_items.setItem(row, 1, type_item)

            self._ui.tbl_items.setItem(row, 2, QTableWidgetItem(item.description))

            original_item = QTableWidgetItem(f"R$ {item.original_amount:,.2f}")
            original_item.setData(Qt.UserRole, item.original_amount)
            self._ui.tbl_items.setItem(row, 3, original_item)

            paid_item = QTableWidgetItem(f"R$ {item.paid_amount:,.2f}")
            paid_item.setData(Qt.UserRole, item.paid_amount)
            self._ui.tbl_items.setItem(row, 4, paid_item)

            remaining_item = QTableWidgetItem(f"R$ {item.remaining_amount:,.2f}")
            remaining_item.setData(Qt.UserRole, item.remaining_amount)
            self._ui.tbl_items.setItem(row, 5, remaining_item)

            due_item = QTableWidgetItem(item.due_date)
            due_item.setData(Qt.UserRole, item.due_date)
            self._ui.tbl_items.setItem(row, 6, due_item)

            self._ui.tbl_items.setItem(
                row, 7, QTableWidgetItem(STATUS_LABELS.get(item.status, item.status))
            )
            self._ui.tbl_items.setItem(row, 8, QTableWidgetItem(item.notes or ""))

    def clear_form(self) -> None:
        self._editing_id = None
        self._ui.cmb_type.setCurrentIndex(0)
        self._ui.txt_description.clear()
        self._ui.spn_amount.setValue(0.0)
        self._ui.date_due.setDate(QDate.currentDate())
        self._ui.cmb_account.setCurrentIndex(0)
        self._ui.cmb_category.setCurrentIndex(0)
        self._ui.txt_notes.clear()
        self._ui.btn_save.setText("Salvar")
        self.clear_error()

    def show_error(self, message: str) -> None:
        self._ui.lbl_error.setText(message)

    def clear_error(self) -> None:
        self._ui.lbl_error.setText("")

    def show_success(self) -> None:
        self.clear_form()