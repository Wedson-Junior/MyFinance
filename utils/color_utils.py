from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap, QBrush, QPen


PRESET_COLORS = [
    ("Verde", "#38A169"),
    ("Azul", "#3182CE"),
    ("Roxo", "#805AD5"),
    ("Amarelo", "#D69E2E"),
    ("Laranja", "#DD6B20"),
    ("Vermelho", "#E53E3E"),
    ("Rosa", "#D53F8C"),
    ("Cinza", "#718096"),
    ("Ciano", "#00B5D8"),
    ("Verde-água", "#319795"),
]

INCOME_COLOR = "#38A169"
EXPENSE_COLOR = "#E53E3E"


def normalize_hex(color: str | None) -> str:
    if not color:
        return "#718096"
    value = color.strip()
    if not value.startswith("#"):
        value = f"#{value}"
    qcolor = QColor(value)
    if not qcolor.isValid():
        return "#718096"
    return qcolor.name()


def color_icon(hex_color: str | None, size: int = 14) -> QIcon:
    color = QColor(normalize_hex(hex_color))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(color))
    painter.setPen(QPen(Qt.GlobalColor.transparent))
    painter.drawEllipse(1, 1, size - 2, size - 2)
    painter.end()
    return QIcon(pixmap)


def type_color(transaction_type: str) -> QColor:
    if transaction_type == "income":
        return QColor(INCOME_COLOR)
    if transaction_type == "expense":
        return QColor(EXPENSE_COLOR)
    return QColor("#A0AEC0")