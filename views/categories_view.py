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

from models.category import Category


class CategoriesView(QWidget):
    save_requested = Signal(str, str, str)
    update_requested = Signal(int, str, str, str)
    delete_requested = Signal(int)
    clear_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._editing_id: Optional[int] = None
        self._load_ui()
        self._setup_type_combo()
        self._setup_table()
        self._connect_signals()

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent.parent / "ui" / "categories.ui"
        loader = QUiLoader()
        self._ui = loader.load(str(ui_path), self)

        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._ui)

        self._ui.lbl_title.setObjectName("lbl_title")
        self._ui.lbl_subtitle.setObjectName("lbl_subtitle")

    def _setup_type_combo(self) -> None:
        self._ui.cmb_type.clear()
        self._ui.cmb_type.addItem("Receita", "income")
        self._ui.cmb_type.addItem("Despesa", "expense")

    def _setup_table(self) -> None:
        header = self._ui.tbl_categories.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self._ui.tbl_categories.setColumnHidden(0, True)

    def _connect_signals(self) -> None:
        self._ui.btn_save.clicked.connect(self._on_save)
        self._ui.btn_clear.clicked.connect(self._on_clear)
        self._ui.btn_edit.clicked.connect(self._on_edit)
        self._ui.btn_delete.clicked.connect(self._on_delete)

    def _on_save(self) -> None:
        name = self._ui.txt_name.text().strip()
        category_type = self._ui.cmb_type.currentData()
        color = self._ui.txt_color.text().strip() or ""

        if self._editing_id is not None:
            self.update_requested.emit(self._editing_id, name, category_type, color)
        else:
            self.save_requested.emit(name, category_type, color)

    def _on_clear(self) -> None:
        self.clear_form()
        self.clear_requested.emit()

    def _on_edit(self) -> None:
        row = self._ui.tbl_categories.currentRow()
        if row < 0:
            self.show_error("Selecione uma categoria para editar.")
            return

        category_id = int(self._ui.tbl_categories.item(row, 0).text())
        name = self._ui.tbl_categories.item(row, 1).text()
        category_type = self._ui.tbl_categories.item(row, 2).data(Qt.UserRole)
        color = self._ui.tbl_categories.item(row, 3).text()

        self._editing_id = category_id
        self._ui.txt_name.setText(name)

        index = self._ui.cmb_type.findData(category_type)
        if index >= 0:
            self._ui.cmb_type.setCurrentIndex(index)

        self._ui.txt_color.setText(color)
        self._ui.btn_save.setText("Atualizar")
        self.clear_error()

    def _on_delete(self) -> None:
        row = self._ui.tbl_categories.currentRow()
        if row < 0:
            self.show_error("Selecione uma categoria para excluir.")
            return

        name = self._ui.tbl_categories.item(row, 1).text()
        reply = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Deseja excluir a categoria \"{name}\"?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        category_id = int(self._ui.tbl_categories.item(row, 0).text())
        self.delete_requested.emit(category_id)

    def load_categories(self, categories: List[Category]) -> None:
        self._ui.tbl_categories.setRowCount(0)
        for category in categories:
            row = self._ui.tbl_categories.rowCount()
            self._ui.tbl_categories.insertRow(row)

            self._ui.tbl_categories.setItem(row, 0, QTableWidgetItem(str(category.id)))
            self._ui.tbl_categories.setItem(row, 1, QTableWidgetItem(category.name))

            type_label = "Receita" if category.type == "income" else "Despesa"
            type_item = QTableWidgetItem(type_label)
            type_item.setData(Qt.UserRole, category.type)
            self._ui.tbl_categories.setItem(row, 2, type_item)

            self._ui.tbl_categories.setItem(row, 3, QTableWidgetItem(category.color or ""))
            self._ui.tbl_categories.setItem(
                row, 4, QTableWidgetItem("Sim" if category.is_active else "Não")
            )

    def clear_form(self) -> None:
        self._editing_id = None
        self._ui.txt_name.clear()
        self._ui.cmb_type.setCurrentIndex(0)
        self._ui.txt_color.clear()
        self._ui.btn_save.setText("Salvar")
        self.clear_error()

    def show_error(self, message: str) -> None:
        self._ui.lbl_error.setText(message)

    def clear_error(self) -> None:
        self._ui.lbl_error.setText("")

    def show_success(self) -> None:
        self.clear_form()