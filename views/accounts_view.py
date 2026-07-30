from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PySide6.QtUiTools import QUiLoader

from models.bank_account import BankAccount


class AccountsView(QWidget):
    save_requested = Signal(str, float, str)
    update_requested = Signal(int, str, float, str)
    delete_requested = Signal(int)
    clear_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._editing_id: Optional[int] = None
        self._load_ui()
        self._setup_table()
        self._connect_signals()

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent.parent / "ui" / "accounts.ui"
        loader = QUiLoader()
        self._ui = loader.load(str(ui_path), self)

        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui)

        self._ui.lbl_title.setObjectName("lbl_title")
        self._ui.lbl_subtitle.setObjectName("lbl_subtitle")

    def _setup_table(self) -> None:
        header = self._ui.tbl_accounts.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self._ui.tbl_accounts.setColumnHidden(0, True)

    def _connect_signals(self) -> None:
        self._ui.btn_save.clicked.connect(self._on_save)
        self._ui.btn_clear.clicked.connect(self._on_clear)
        self._ui.btn_edit.clicked.connect(self._on_edit)
        self._ui.btn_delete.clicked.connect(self._on_delete)

    def _on_save(self) -> None:
        name = self._ui.txt_name.text().strip()
        balance = self._ui.spn_balance.value()
        currency = self._ui.cmb_currency.currentText()

        if self._editing_id is not None:
            self.update_requested.emit(self._editing_id, name, balance, currency)
        else:
            self.save_requested.emit(name, balance, currency)

    def _on_clear(self) -> None:
        self.clear_form()
        self.clear_requested.emit()

    def _on_edit(self) -> None:
        row = self._ui.tbl_accounts.currentRow()
        if row < 0:
            self.show_error("Selecione uma conta para editar.")
            return

        account_id = int(self._ui.tbl_accounts.item(row, 0).text())
        name = self._ui.tbl_accounts.item(row, 1).text()
        balance = self._ui.tbl_accounts.item(row, 2).data(Qt.UserRole)
        currency = self._ui.tbl_accounts.item(row, 3).text()

        self._editing_id = account_id
        self._ui.txt_name.setText(name)
        self._ui.spn_balance.setValue(float(balance) if balance is not None else 0.0)

        index = self._ui.cmb_currency.findText(currency)
        if index >= 0:
            self._ui.cmb_currency.setCurrentIndex(index)

        self._ui.btn_save.setText("Atualizar")
        self.clear_error()

    def _on_delete(self) -> None:
        row = self._ui.tbl_accounts.currentRow()
        if row < 0:
            self.show_error("Selecione uma conta para excluir.")
            return

        name = self._ui.tbl_accounts.item(row, 1).text()
        reply = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Deseja excluir a conta \"{name}\"?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        account_id = int(self._ui.tbl_accounts.item(row, 0).text())
        self.delete_requested.emit(account_id)

    def load_accounts(self, accounts: List[BankAccount]) -> None:
        self._ui.tbl_accounts.setRowCount(0)
        for account in accounts:
            row = self._ui.tbl_accounts.rowCount()
            self._ui.tbl_accounts.insertRow(row)

            self._ui.tbl_accounts.setItem(row, 0, QTableWidgetItem(str(account.id)))
            self._ui.tbl_accounts.setItem(row, 1, QTableWidgetItem(account.name))

            balance_item = QTableWidgetItem(f"R$ {account.balance:,.2f}")
            balance_item.setData(Qt.UserRole, account.balance)
            self._ui.tbl_accounts.setItem(row, 2, balance_item)

            self._ui.tbl_accounts.setItem(row, 3, QTableWidgetItem(account.currency))
            self._ui.tbl_accounts.setItem(
                row, 4, QTableWidgetItem("Sim" if account.is_active else "Não")
            )

    def clear_form(self) -> None:
        self._editing_id = None
        self._ui.txt_name.clear()
        self._ui.spn_balance.setValue(0.0)
        self._ui.cmb_currency.setCurrentIndex(0)
        self._ui.btn_save.setText("Salvar")
        self.clear_error()

    def show_error(self, message: str) -> None:
        self._ui.lbl_error.setText(message)

    def clear_error(self) -> None:
        self._ui.lbl_error.setText("")

    def show_success(self) -> None:
        self.clear_form()