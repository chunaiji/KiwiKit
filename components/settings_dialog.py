"""
设置对话框组件
提供主题切换和其他设置选项
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QGroupBox, QPushButton, QSpacerItem,
    QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from styles.factory import enhanced_combo, primary_button, secondary_button
from styles import constants


class SettingsDialog(QDialog):
    """设置对话框"""
    
    theme_changed = Signal(str)  # 主题切换信号，传递主题名称
    
    def __init__(self, parent=None, current_theme="light"):
        super().__init__(parent)
        self.current_theme = current_theme
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        self._init_ui()
        self._setup_styles()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 标题
        title = QLabel("应用设置")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # 主题设置组
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout(theme_group)
        
        # 主题选择
        theme_selection_layout = QHBoxLayout()
        theme_label = QLabel("界面主题:")
        theme_label.setMinimumWidth(80)
        
        self.theme_combo = enhanced_combo()
        self.theme_combo.addItems(["浅色主题", "深色主题"])
        # 设置当前主题
        if self.current_theme == "dark":
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(0)
        
        theme_selection_layout.addWidget(theme_label)
        theme_selection_layout.addWidget(self.theme_combo)
        theme_layout.addLayout(theme_selection_layout)
        
        # 主题描述
        self.theme_desc = QLabel("选择应用的外观主题风格")
        theme_layout.addWidget(self.theme_desc)
        
        layout.addWidget(theme_group)
        
        # 弹簧间隔
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        self.cancel_btn = secondary_button("取消")
        self.apply_btn = primary_button("应用")
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_styles(self):
        """设置样式"""
        self._apply_theme_styles()
    
    def _apply_theme_styles(self):
        """应用当前主题的样式"""
        # 动态导入当前主题的常量
        if self.current_theme == "dark":
            from styles import constants_dark as theme_constants
        else:
            from styles import constants as theme_constants
        
        # 对话框样式
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme_constants.Colors.BACKGROUND_TERTIARY};
                border: 1px solid {theme_constants.Colors.BORDER_LIGHT};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {theme_constants.Colors.BORDER_LIGHT};
                border-radius: {theme_constants.Sizes.RADIUS_MEDIUM};
                margin-top: 8px;
                padding-top: 4px;
                background-color: {theme_constants.Colors.BACKGROUND_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {theme_constants.Colors.TEXT_PRIMARY};
                background-color: {theme_constants.Colors.BACKGROUND_PRIMARY};
            }}
            QLabel {{
                color: {theme_constants.Colors.TEXT_PRIMARY};
                font-size: {theme_constants.Sizes.FONT_MEDIUM};
            }}
            QFrame[frameShape="4"] {{
                color: {theme_constants.Colors.BORDER_LIGHT};
            }}
        """)
        
        # 更新主题描述的样式
        if hasattr(self, 'theme_desc'):
            self.theme_desc.setStyleSheet(f"color: {theme_constants.Colors.TEXT_SECONDARY}; font-size: {theme_constants.Sizes.FONT_SMALL};")
    
    def _connect_signals(self):
        """连接信号"""
        self.cancel_btn.clicked.connect(self.reject)
        self.apply_btn.clicked.connect(self._apply_settings)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
    
    def _on_theme_changed(self, theme_text):
        """主题选择改变"""
        # 更新当前主题预览
        new_theme = "dark" if theme_text == "深色主题" else "light"
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self._apply_theme_styles()  # 实时预览主题效果
    
    def _apply_settings(self):
        """应用设置"""
        # 获取选择的主题
        theme_index = self.theme_combo.currentIndex()
        theme_name = "dark" if theme_index == 1 else "light"
        
        # 如果主题有变化，发送信号
        if theme_name != self.current_theme:
            self.theme_changed.emit(theme_name)
        
        self.accept()
    
    def set_current_theme(self, theme_name):
        """设置当前主题"""
        self.current_theme = theme_name
        if theme_name == "dark":
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(0)
        # 更新样式以匹配当前主题
        self._apply_theme_styles()


class ThemeManager:
    """主题管理器，负责主题切换逻辑"""
    
    def __init__(self):
        self.current_theme = "light"
        self._original_constants = None
    
    def switch_theme(self, theme_name):
        """切换主题"""
        if theme_name == self.current_theme:
            return
        
        self.current_theme = theme_name
        
        # 保存原始常量（如果尚未保存）
        if self._original_constants is None:
            import styles.constants as constants_module
            self._original_constants = {
                'Colors': constants_module.Colors,
                'Sizes': constants_module.Sizes,
                'Shadows': constants_module.Shadows
            }
        
        # 根据主题切换常量
        import styles.constants as constants_module
        
        if theme_name == "dark":
            from styles import constants_dark
            constants_module.Colors = constants_dark.Colors
            constants_module.Sizes = constants_dark.Sizes
            constants_module.Shadows = constants_dark.Shadows
        else:  # light theme
            constants_module.Colors = self._original_constants['Colors']
            constants_module.Sizes = self._original_constants['Sizes']
            constants_module.Shadows = self._original_constants['Shadows']
    
    def get_current_theme(self):
        """获取当前主题名称"""
        return self.current_theme


# 全局主题管理器实例
theme_manager = ThemeManager()
