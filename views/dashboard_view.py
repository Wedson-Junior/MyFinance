from pathlib import Path
from typing import List, Dict

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidgetItem, QHeaderView
from PySide6.QtUiTools import QUiLoader

from models.transaction import Transaction


class DashboardView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._load_ui()
        self._setup_table()

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent.parent / "ui" / "dashboard.ui"
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
        header = self._ui.tbl_recent.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

    def set_summary(
        self,
        total_balance: float,
        monthly_income: float,
        monthly_expense: float,
        accounts_count: int,
    ) -> None:
        self._ui.lbl_balance_value.setText(f"R$ {total_balance:,.2f}")
        self._ui.lbl_income_value.setText(f"R$ {monthly_income:,.2f}")
        self._ui.lbl_expense_value.setText(f"R$ {monthly_expense:,.2f}")
        self._ui.lbl_accounts_value.setText(str(accounts_count))

    def load_recent_transactions(
        self,
        transactions: List[Transaction],
        categories_map: Dict[int, str],
    ) -> None:
        self._ui.tbl_recent.setRowCount(0)
        for transaction in transactions[:10]:
            row = self._ui.tbl_recent.rowCount()
            self._ui.tbl_recent.insertRow(row)

            self._ui.tbl_recent.setItem(row, 0, QTableWidgetItem(transaction.date))

            type_label = "Receita" if transaction.type == "income" else "Despesa"
            self._ui.tbl_recent.setItem(row, 1, QTableWidgetItem(type_label))

            category_name = categories_map.get(transaction.category_id, "-")
            self._ui.tbl_recent.setItem(row, 2, QTableWidgetItem(category_name))

            amount_text = f"R$ {transaction.amount:,.2f}"
            self._ui.tbl_recent.setItem(row, 3, QTableWidgetItem(amount_text))

            self._ui.tbl_recent.setItem(
                row, 4, QTableWidgetItem(transaction.description or "")
            )