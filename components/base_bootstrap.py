from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem,
    QSizePolicy, QLabel, QPushButton, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt


class Col(QWidget):
    def __init__(self, widget=None, span=12, alignment=Qt.AlignmentFlag(0)):
        """
        创建一个占据 span 列的列容器，可选对齐方式。
        """
        super().__init__()
        self.span = span
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if widget:
            layout.addWidget(widget, alignment=alignment)
        else:
            layout.addStretch()


class Spacer(QWidget):
    def __init__(self, span=1):
        """
        空白占位符，占据 span 列
        """
        super().__init__()
        self.span = span


class Row(QHBoxLayout):
    def __init__(self, *cols, spacing=10, margins=(0, 0, 0, 0)):
        """
        创建一行，包含任意数量的 Col / Spacer 组件
        """
        super().__init__()
        self.setSpacing(spacing)
        self.setContentsMargins(*margins)

        for item in cols:
            if isinstance(item, (Col, Spacer)):
                self.addWidget(item, item.span)
            else:
                raise ValueError("Row 只能包含 Col 或 Spacer 实例")


class Container(QWidget):
    def __init__(self, *rows, spacing=10, margins=(10, 10, 10, 10)):
        """
        外部容器，用于组织多个 Row
        """
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        for row in rows:
            layout.addLayout(row)
