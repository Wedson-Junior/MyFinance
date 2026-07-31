from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtCore import Signal, QDate
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidgetItem, QHeaderView
from PySide6.QtUiTools import QUiLoader

from models.transaction import Transaction
from models.bank_account import BankAccount
from models.category import Category


class ReportsView(QWidget):
    filter_requested = Signal(str, str, object, object, object)
    clear_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._load_ui()
        self._setup_combos()
        self._setup_table()
        self._setup_default_dates()
        self._connect_signals()

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent.parent / "ui" / "reports.ui"
        loader = QUiLoader()
        self._ui = loader.load(str(ui_path), self)

        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui)

        self._ui.lbl_title.setObjectName("lbl_title")
        self._ui.lbl_subtitle.setObjectName("lbl_subtitle")

    def _setup_combos(self) -> None:
        self._ui.cmb_type.clear()
        self._ui.cmb_type.addItem("Todos", None)
        self._ui.cmb_type.addItem("Receita", "income")
        self._ui.cmb_type.addItem("Despesa", "expense")

    def _setup_table(self) -> None:
        header = self._ui.tbl_report.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

    def _setup_default_dates(self) -> None:
        today = QDate.currentDate()
        first_day = QDate(today.year(), today.month(), 1)
        self._ui.date_from.setDate(first_day)
        self._ui.date_to.setDate(today)

    def _connect_signals(self) -> None:
        self._ui.btn_filter.clicked.connect(self._on_filter)
        self._ui.btn_clear.clicked.connect(self._on_clear)

    def _on_filter(self) -> None:
        date_from = self._ui.date_from.date().toString("yyyy-MM-dd")
        date_to = self._ui.date_to.date().toString("yyyy-MM-dd")
        transaction_type = self._ui.cmb_type.currentData()
        account_id = self._ui.cmb_account.currentData()
        category_id = self._ui.cmb_category.currentData()
        self.filter_requested.emit(
            date_from, date_to, transaction_type, account_id, category_id
        )

    def _on_clear(self) -> None:
        self._setup_default_dates()
        self._ui.cmb_type.setCurrentIndex(0)
        if self._ui.cmb_account.count() > 0:
            self._ui.cmb_account.setCurrentIndex(0)
        if self._ui.cmb_category.count() > 0:
            self._ui.cmb_category.setCurrentIndex(0)
        self.clear_requested.emit()

    def set_accounts(self, accounts: List[BankAccount]) -> None:
        self._ui.cmb_account.clear()
        self._ui.cmb_account.addItem("Todas as contas", None)
        for account in accounts:
            self._ui.cmb_account.addItem(account.name, account.id)

    def set_categories(self, categories: List[Category]) -> None:
        self._ui.cmb_category.clear()
        self._ui.cmb_category.addItem("Todas as categorias", None)
        for category in categories:
            self._ui.cmb_category.addItem(category.name, category.id)

    def load_report(
        self,
        transactions: List[Transaction],
        accounts_map: Dict[int, str],
        categories_map: Dict[int, str],
        total_income: float,
        total_expense: float,
    ) -> None:
        self._ui.tbl_report.setRowCount(0)
        for transaction in transactions:
            row = self._ui.tbl_report.rowCount()
            self._ui.tbl_report.insertRow(row)

            self._ui.tbl_report.setItem(row, 0, QTableWidgetItem(transaction.date))

            type_label = "Receita" if transaction.type == "income" else "Despesa"
            self._ui.tbl_report.setItem(row, 1, QTableWidgetItem(type_label))

            account_name = accounts_map.get(transaction.account_id, "-")
            self._ui.tbl_report.setItem(row, 2, QTableWidgetItem(account_name))

            category_name = categories_map.get(transaction.category_id, "-")
            self._ui.tbl_report.setItem(row, 3, QTableWidgetItem(category_name))

            self._ui.tbl_report.setItem(
                row, 4, QTableWidgetItem(f"R$ {transaction.amount:,.2f}")
            )
            self._ui.tbl_report.setItem(
                row, 5, QTableWidgetItem(transaction.description or "")
            )

        balance = total_income - total_expense
        self._ui.lbl_summary_income.setText(f"Receitas: R$ {total_income:,.2f}")
        self._ui.lbl_summary_expense.setText(f"Despesas: R$ {total_expense:,.2f}")
        self._ui.lbl_summary_balance.setText(f"Saldo do período: R$ {balance:,.2f}")