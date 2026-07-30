from pathlib import Path
from typing import List, Optional, Dict

from PySide6.QtCore import Signal, Qt, QDate
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PySide6.QtUiTools import QUiLoader

from models.transaction import Transaction
from models.bank_account import BankAccount
from models.category import Category


class TransactionsView(QWidget):
    save_requested = Signal(int, int, str, float, str, str, bool)
    update_requested = Signal(int, int, int, str, float, str, str, bool)
    delete_requested = Signal(int)
    clear_requested = Signal()
    type_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._editing_id: Optional[int] = None
        self._accounts_map: Dict[int, str] = {}
        self._categories_map: Dict[int, str] = {}
        self._load_ui()
        self._setup_combos()
        self._setup_table()
        self._connect_signals()

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent.parent / "ui" / "transactions.ui"
        loader = QUiLoader()
        self._ui = loader.load(str(ui_path), self)

        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui)

        self._ui.lbl_title.setObjectName("lbl_title")
        self._ui.lbl_subtitle.setObjectName("lbl_subtitle")
        self._ui.date_transaction.setDate(QDate.currentDate())

    def _setup_combos(self) -> None:
        self._ui.cmb_type.clear()
        self._ui.cmb_type.addItem("Receita", "income")
        self._ui.cmb_type.addItem("Despesa", "expense")

    def _setup_table(self) -> None:
        header = self._ui.tbl_transactions.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self._ui.tbl_transactions.setColumnHidden(0, True)

    def _connect_signals(self) -> None:
        self._ui.btn_save.clicked.connect(self._on_save)
        self._ui.btn_clear.clicked.connect(self._on_clear)
        self._ui.btn_edit.clicked.connect(self._on_edit)
        self._ui.btn_delete.clicked.connect(self._on_delete)
        self._ui.cmb_type.currentIndexChanged.connect(self._on_type_changed)

    def _on_type_changed(self) -> None:
        category_type = self._ui.cmb_type.currentData()
        if category_type:
            self.type_changed.emit(category_type)

    def _on_save(self) -> None:
        account_id = self._ui.cmb_account.currentData()
        category_id = self._ui.cmb_category.currentData()
        transaction_type = self._ui.cmb_type.currentData()
        amount = self._ui.spn_amount.value()
        description = self._ui.txt_description.text().strip()
        date = self._ui.date_transaction.date().toString("yyyy-MM-dd")
        is_recurring = self._ui.chk_recurring.isChecked()

        if self._editing_id is not None:
            self.update_requested.emit(
                self._editing_id,
                account_id if account_id else 0,
                category_id if category_id else 0,
                transaction_type or "",
                amount,
                description,
                date,
                is_recurring,
            )
        else:
            self.save_requested.emit(
                account_id if account_id else 0,
                category_id if category_id else 0,
                transaction_type or "",
                amount,
                description,
                date,
                is_recurring,
            )

    def _on_clear(self) -> None:
        self.clear_form()
        self.clear_requested.emit()

    def _on_edit(self) -> None:
        row = self._ui.tbl_transactions.currentRow()
        if row < 0:
            self.show_error("Selecione um lançamento para editar.")
            return

        transaction_id = int(self._ui.tbl_transactions.item(row, 0).text())
        date_str = self._ui.tbl_transactions.item(row, 1).data(Qt.UserRole)
        transaction_type = self._ui.tbl_transactions.item(row, 2).data(Qt.UserRole)
        account_id = self._ui.tbl_transactions.item(row, 3).data(Qt.UserRole)
        category_id = self._ui.tbl_transactions.item(row, 4).data(Qt.UserRole)
        amount = self._ui.tbl_transactions.item(row, 5).data(Qt.UserRole)
        description = self._ui.tbl_transactions.item(row, 6).text()
        is_recurring = self._ui.tbl_transactions.item(row, 7).data(Qt.UserRole)

        self._editing_id = transaction_id

        type_index = self._ui.cmb_type.findData(transaction_type)
        if type_index >= 0:
            self._ui.cmb_type.setCurrentIndex(type_index)

        account_index = self._ui.cmb_account.findData(account_id)
        if account_index >= 0:
            self._ui.cmb_account.setCurrentIndex(account_index)

        category_index = self._ui.cmb_category.findData(category_id)
        if category_index >= 0:
            self._ui.cmb_category.setCurrentIndex(category_index)

        self._ui.spn_amount.setValue(float(amount) if amount is not None else 0.0)
        self._ui.txt_description.setText(description)
        if date_str:
            self._ui.date_transaction.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
        self._ui.chk_recurring.setChecked(bool(is_recurring))
        self._ui.btn_save.setText("Atualizar")
        self.clear_error()

    def _on_delete(self) -> None:
        row = self._ui.tbl_transactions.currentRow()
        if row < 0:
            self.show_error("Selecione um lançamento para excluir.")
            return

        description = self._ui.tbl_transactions.item(row, 6).text() or "este lançamento"
        reply = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Deseja excluir \"{description}\"?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        transaction_id = int(self._ui.tbl_transactions.item(row, 0).text())
        self.delete_requested.emit(transaction_id)

    def set_accounts(self, accounts: List[BankAccount]) -> None:
        self._accounts_map = {a.id: a.name for a in accounts if a.id is not None}
        current = self._ui.cmb_account.currentData()
        self._ui.cmb_account.clear()
        for account in accounts:
            self._ui.cmb_account.addItem(account.name, account.id)
        if current is not None:
            index = self._ui.cmb_account.findData(current)
            if index >= 0:
                self._ui.cmb_account.setCurrentIndex(index)

    def set_categories(self, categories: List[Category]) -> None:
        self._categories_map = {c.id: c.name for c in categories if c.id is not None}
        current = self._ui.cmb_category.currentData()
        self._ui.cmb_category.clear()
        for category in categories:
            self._ui.cmb_category.addItem(category.name, category.id)
        if current is not None:
            index = self._ui.cmb_category.findData(current)
            if index >= 0:
                self._ui.cmb_category.setCurrentIndex(index)

    def load_transactions(self, transactions: List[Transaction]) -> None:
        self._ui.tbl_transactions.setRowCount(0)
        for transaction in transactions:
            row = self._ui.tbl_transactions.rowCount()
            self._ui.tbl_transactions.insertRow(row)

            self._ui.tbl_transactions.setItem(row, 0, QTableWidgetItem(str(transaction.id)))

            date_item = QTableWidgetItem(transaction.date)
            date_item.setData(Qt.UserRole, transaction.date)
            self._ui.tbl_transactions.setItem(row, 1, date_item)

            type_label = "Receita" if transaction.type == "income" else "Despesa"
            type_item = QTableWidgetItem(type_label)
            type_item.setData(Qt.UserRole, transaction.type)
            self._ui.tbl_transactions.setItem(row, 2, type_item)

            account_name = self._accounts_map.get(transaction.account_id, str(transaction.account_id))
            account_item = QTableWidgetItem(account_name)
            account_item.setData(Qt.UserRole, transaction.account_id)
            self._ui.tbl_transactions.setItem(row, 3, account_item)

            category_name = self._categories_map.get(transaction.category_id, str(transaction.category_id))
            category_item = QTableWidgetItem(category_name)
            category_item.setData(Qt.UserRole, transaction.category_id)
            self._ui.tbl_transactions.setItem(row, 4, category_item)

            amount_item = QTableWidgetItem(f"R$ {transaction.amount:,.2f}")
            amount_item.setData(Qt.UserRole, transaction.amount)
            self._ui.tbl_transactions.setItem(row, 5, amount_item)

            self._ui.tbl_transactions.setItem(
                row, 6, QTableWidgetItem(transaction.description or "")
            )

            recurring_item = QTableWidgetItem("Sim" if transaction.is_recurring else "Não")
            recurring_item.setData(Qt.UserRole, transaction.is_recurring)
            self._ui.tbl_transactions.setItem(row, 7, recurring_item)

    def clear_form(self) -> None:
        self._editing_id = None
        self._ui.cmb_type.setCurrentIndex(0)
        self._ui.spn_amount.setValue(0.0)
        self._ui.txt_description.clear()
        self._ui.date_transaction.setDate(QDate.currentDate())
        self._ui.chk_recurring.setChecked(False)
        self._ui.btn_save.setText("Salvar")
        self.clear_error()

    def show_error(self, message: str) -> None:
        self._ui.lbl_error.setText(message)

    def clear_error(self) -> None:
        self._ui.lbl_error.setText("")

    def show_success(self) -> None:
        self.clear_form()