"""
头部组件 - 微信风格
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from styles.generator import StyleGenerator
from styles.constants import Colors

class Header(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置UI布局 - 微信风格"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 左侧区域（对应左侧导航栏宽度）
        left_area = QWidget()
        left_area.setFixedWidth(64)
        left_area.setStyleSheet("background: #2e2e2e;")
        layout.addWidget(left_area)
        
        
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QWidget {
                height: 38px;
                min-height: 38px;
                max-height: 38px;
            }
        """)
