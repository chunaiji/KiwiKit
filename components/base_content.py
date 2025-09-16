from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class BaseContent(QWidget):
    def __init__(self, title: str, content_widget: QWidget, parent=None):
        super().__init__(parent)
        self.title_text = title
        self.content_widget = content_widget

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 顶部标题
        self.title_label = QLabel(self.title_text)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #333333; margin-bottom: 10px;")
        layout.addWidget(self.title_label)

        # 中间内容区
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.content_widget)
        layout.setStretchFactor(self.content_widget, 1)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 底部状态栏
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self.status_label)

        # 延迟验证计时器（可选）
        self.validation_timer = QTimer(self)
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._on_validation_timeout)

    def _on_validation_timeout(self):
        """子类可以重写实现自动验证逻辑"""
        pass

    def set_status(self, text: str):
        """更新底部状态栏文本"""
        self.status_label.setText(text)
