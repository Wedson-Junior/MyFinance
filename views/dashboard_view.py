from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtCore import Signal, QDate, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QDateEdit,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PySide6.QtUiTools import QUiLoader

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from models.transaction import Transaction
from utils.color_utils import color_icon, normalize_hex, type_color, INCOME_COLOR, EXPENSE_COLOR
from config.settings import get_current_theme, THEME_DARK


class DashboardView(QWidget):
    filter_requested = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self._load_ui()
        self._setup_table()
        self._setup_chart_section()
        self._connect_signals()

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

    def _setup_chart_section(self) -> None:
        main_layout = self._ui.layout()
        recent_index = main_layout.indexOf(self._ui.lbl_recent_title)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self._lbl_filter = QLabel("Período do gráfico")
        self._date_from = QDateEdit()
        self._date_from.setCalendarPopup(True)
        self._date_from.setDisplayFormat("dd/MM/yyyy")
        self._date_from.setDate(QDate.currentDate().addMonths(-1))
        self._date_from.setMinimumHeight(36)

        self._date_to = QDateEdit()
        self._date_to.setCalendarPopup(True)
        self._date_to.setDisplayFormat("dd/MM/yyyy")
        self._date_to.setDate(QDate.currentDate())
        self._date_to.setMinimumHeight(36)

        self._btn_filter = QPushButton("Aplicar")
        self._btn_filter.setObjectName("btn_filter")
        self._btn_filter.setMinimumSize(100, 36)

        filter_row.addWidget(self._lbl_filter)
        filter_row.addWidget(self._date_from)
        filter_row.addWidget(QLabel("até"))
        filter_row.addWidget(self._date_to)
        filter_row.addWidget(self._btn_filter)
        filter_row.addStretch()

        filter_widget = QWidget()
        filter_widget.setLayout(filter_row)

        self._chart_frame = QFrame()
        self._chart_frame.setFrameShape(QFrame.StyledPanel)
        self._chart_frame.setMinimumHeight(280)
        chart_layout = QVBoxLayout(self._chart_frame)
        chart_layout.setContentsMargins(8, 8, 8, 8)

        self._figure = Figure(figsize=(8, 3.2), tight_layout=True)
        self._canvas = FigureCanvas(self._figure)
        self._canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chart_layout.addWidget(self._canvas)

        main_layout.insertWidget(recent_index, filter_widget)
        main_layout.insertWidget(recent_index + 1, self._chart_frame)

    def _connect_signals(self) -> None:
        self._btn_filter.clicked.connect(self._on_filter)

    def _on_filter(self) -> None:
        date_from = self._date_from.date().toString("yyyy-MM-dd")
        date_to = self._date_to.date().toString("yyyy-MM-dd")
        self.filter_requested.emit(date_from, date_to)

    def set_filter_dates(self, date_from: str, date_to: str) -> None:
        if date_from:
            self._date_from.setDate(QDate.fromString(date_from, "yyyy-MM-dd"))
        if date_to:
            self._date_to.setDate(QDate.fromString(date_to, "yyyy-MM-dd"))

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
        categories_color_map: Optional[Dict[int, str]] = None,
    ) -> None:
        if categories_color_map is None:
            categories_color_map = {}

        self._ui.tbl_recent.setRowCount(0)
        for transaction in transactions[:10]:
            row = self._ui.tbl_recent.rowCount()
            self._ui.tbl_recent.insertRow(row)

            self._ui.tbl_recent.setItem(row, 0, QTableWidgetItem(transaction.date))

            type_label = "Receita" if transaction.type == "income" else "Despesa"
            type_item = QTableWidgetItem(type_label)
            type_item.setForeground(type_color(transaction.type))
            self._ui.tbl_recent.setItem(row, 1, type_item)

            category_name = categories_map.get(transaction.category_id, "-")
            category_color = categories_color_map.get(transaction.category_id)
            category_item = QTableWidgetItem(color_icon(category_color), category_name)
            self._ui.tbl_recent.setItem(row, 2, category_item)

            amount_item = QTableWidgetItem(f"R$ {transaction.amount:,.2f}")
            amount_item.setForeground(type_color(transaction.type))
            self._ui.tbl_recent.setItem(row, 3, amount_item)

            self._ui.tbl_recent.setItem(
                row, 4, QTableWidgetItem(transaction.description or "")
            )

    def _chart_theme_colors(self) -> dict:
        if get_current_theme() == THEME_DARK:
            return {
                "text": "#E8EAF0",
                "grid": "#3A4255",
                "spine": "#4A5568",
                "legend_face": "#1A1F2A",
                "legend_edge": "#2A3140",
            }
        return {
            "text": "#1A202C",
            "grid": "#CBD5E0",
            "spine": "#A0AEC0",
            "legend_face": "#FFFFFF",
            "legend_edge": "#E2E8F0",
        }

    def _apply_axis_theme(self, axis, theme: dict) -> None:
        axis.set_facecolor("none")
        axis.title.set_color(theme["text"])
        axis.xaxis.label.set_color(theme["text"])
        axis.yaxis.label.set_color(theme["text"])
        axis.tick_params(colors=theme["text"])
        for spine in axis.spines.values():
            spine.set_color(theme["spine"])
        axis.yaxis.label.set_color(theme["text"])


    def _draw_pie(self, axis, pie_data: Optional[dict], title: str, theme: dict) -> None:
        values = (pie_data or {}).get("values") or []
        labels_pie = (pie_data or {}).get("labels") or []
        colors = [normalize_hex(c) for c in ((pie_data or {}).get("colors") or [])]
        if not values or sum(values) <= 0:
            axis.text(
                0.5,
                0.5,
                "Sem dados",
                ha="center",
                va="center",
                color=theme["text"],
            )
            axis.set_axis_off()
            axis.set_title(title, color=theme["text"])
            return

        wedges, texts, autotexts = axis.pie(
            values,
            labels=labels_pie,
            colors=colors if colors else None,
            autopct="%1.1f%%",
            startangle=90,
            textprops={"color": theme["text"]},
        )
        for autotext in autotexts:
            autotext.set_color("#FFFFFF")
            autotext.set_fontweight("bold")
        axis.set_title(title, color=theme["text"])

    def update_chart(
        self,
        chart_type: str,
        labels: List[str],
        income_values: List[float],
        expense_values: List[float],
        income_pie: Optional[dict] = None,
        expense_pie: Optional[dict] = None,
    ) -> None:
        theme = self._chart_theme_colors()
        self._figure.clear()

        if chart_type == "pie":
            axis_income = self._figure.add_subplot(121)
            axis_expense = self._figure.add_subplot(122)
            self._draw_pie(axis_income, income_pie, "Receitas por categoria", theme)
            self._draw_pie(axis_expense, expense_pie, "Despesas por categoria", theme)
            self._figure.patch.set_alpha(0.0)
            self._canvas.draw()
            return

        axis = self._figure.add_subplot(111)
        if not labels:
            axis.text(
                0.5,
                0.5,
                "Sem dados no período",
                ha="center",
                va="center",
                color=theme["text"],
            )
            axis.set_xticks([])
            axis.set_yticks([])
        else:
            x_positions = list(range(len(labels)))
            if chart_type == "line":
                axis.plot(
                    x_positions,
                    income_values,
                    color=INCOME_COLOR,
                    marker="o",
                    label="Receitas",
                )
                axis.plot(
                    x_positions,
                    expense_values,
                    color=EXPENSE_COLOR,
                    marker="o",
                    label="Despesas",
                )
            elif chart_type == "area":
                axis.fill_between(
                    x_positions,
                    income_values,
                    color=INCOME_COLOR,
                    alpha=0.35,
                    label="Receitas",
                )
                axis.fill_between(
                    x_positions,
                    expense_values,
                    color=EXPENSE_COLOR,
                    alpha=0.35,
                    label="Despesas",
                )
                axis.plot(x_positions, income_values, color=INCOME_COLOR)
                axis.plot(x_positions, expense_values, color=EXPENSE_COLOR)
            else:
                width = 0.38
                income_bars = [p - width / 2 for p in x_positions]
                expense_bars = [p + width / 2 for p in x_positions]
                axis.bar(
                    income_bars,
                    income_values,
                    width=width,
                    color=INCOME_COLOR,
                    label="Receitas",
                )
                axis.bar(
                    expense_bars,
                    expense_values,
                    width=width,
                    color=EXPENSE_COLOR,
                    label="Despesas",
                )

            axis.set_xticks(x_positions)
            display_labels = labels
            if len(labels) > 10:
                step = max(1, len(labels) // 8)
                display_labels = [
                    label if index % step == 0 else ""
                    for index, label in enumerate(labels)
                ]
            axis.set_xticklabels(display_labels, rotation=30, ha="right")
            legend = axis.legend(loc="upper left")
            legend.get_frame().set_facecolor(theme["legend_face"])
            legend.get_frame().set_edgecolor(theme["legend_edge"])
            for text_item in legend.get_texts():
                text_item.set_color(theme["text"])
            axis.set_ylabel("Valor (R$)")
            axis.grid(True, axis="y", linestyle="--", alpha=0.35, color=theme["grid"])

        self._apply_axis_theme(axis, theme)
        self._figure.patch.set_alpha(0.0)
        axis.set_facecolor("none")
        self._canvas.draw()
