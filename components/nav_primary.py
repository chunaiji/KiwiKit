"""
左侧一级导航栏组件
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QBrush, QColor, QPainterPath
from styles.generator import StyleGenerator
from styles.constants import Colors
from config.nav_config import get_nav_primary_items

# 导入日志系统
from utils.logger import info, error, warning, log_system_event

class UserAvatar(QLabel):
    """用户头像组件 - 微信风格"""
    clicked = Signal()

    def __init__(self):
        super().__init__()
        size = 40
        pixmap = QPixmap("images/2d12c446704444ecb5a0e12eca299845.jpg")
        
        if not pixmap.isNull():
            rounded_pixmap = self._rounded_pixmap(pixmap, size, radius=8)
            self.setPixmap(rounded_pixmap)
        else:
            self.setText("👤")
        
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QLabel {{
                color: white;
                border: none;
                font-size: 18px;
                background: transparent;
            }}
            QLabel:hover {{
                background: {Colors.HOVER_GRAY};
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
    
    def refresh_styles(self):
        """刷新样式 - 支持主题切换"""
        # 重新导入当前主题的颜色常量
        from styles.constants import Colors
        self.setStyleSheet(f"""
            QLabel {{
                color: white;
                border: none;
                font-size: 18px;
                background: transparent;
            }}
            QLabel:hover {{
                background: {Colors.HOVER_GRAY};
            }}
        """)

    def _rounded_pixmap(self, src_pixmap, size, radius):
        """返回圆角头像"""
        # 缩放图片并裁剪为正方形
        src_pixmap = src_pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        rounded = QPixmap(size, size)
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, size, size, radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, src_pixmap)
        painter.end()

        return rounded


class NavButton(QPushButton):
    """导航按钮组件 - 微信风格"""
    def __init__(self, icon, text, is_active=False, img_path=None):
        super().__init__()
        self.icon_text = icon
        self.button_text = text
        self.is_active = is_active
        self.img_path = img_path
        self.setFixedSize(48, 48)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(text)
        # 使用QVBoxLayout实现真正居中
        self._icon_label = QLabel()
        self._icon_label.setAlignment(Qt.AlignCenter)
        self._icon_label.setFixedSize(48, 48)
        if img_path:
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self._icon_label.setPixmap(scaled)
            else:
                self._icon_label.setText(icon)
        else:
            self._icon_label.setText(icon)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(self._icon_label, alignment=Qt.AlignCenter)
        layout.addStretch()
        self.update_style()
    
    def update_style(self):
        # 重新导入当前主题的颜色常量
        from styles.constants import Colors
        
        if self.is_active:
            # 按钮样式 - 激活状态使用小一点的圆角正方形背景
            button_style = f"""
                QPushButton {{
                    background: {Colors.WECHAT_GREEN};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 18px;
                    text-align: center;

                }}
                QPushButton:hover {{
                    background: {Colors.WECHAT_GREEN_HOVER};
                }}
            """
            # 内部图标样式
            icon_style = f"""
                QLabel {{
                    background: transparent;
                    color: white;
                    font-size: 18px;
                }}
            """
        else:
            # 按钮样式 - 非激活状态透明背景
            button_style = f"""
                QPushButton {{
                    background: transparent;
                    color: {Colors.TEXT_SECONDARY};
                    border: none;
                    border-radius: 6px;
                    font-size: 18px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background: {Colors.HOVER_GRAY};
                    border-radius: 6px;
                    margin: 4px;
                }}
            """
            # 内部图标样式
            icon_style = f"""
                QLabel {{
                    background: transparent;
                    color: {Colors.TEXT_SECONDARY};
                    font-size: 18px;
                }}
            """
        
        self.setStyleSheet(button_style)
        self._icon_label.setStyleSheet(icon_style)
    
    def set_active(self, active):
        self.is_active = active
        self.update_style()
    
    def refresh_styles(self):
        """刷新样式 - 支持主题切换"""
        self.update_style()

class NavPrimary(QWidget):
    # 信号定义
    nav_changed = Signal(str)
    settings_clicked = Signal()
    user_clicked = Signal()
    
    def __init__(self):
        try:
            super().__init__()
            info("开始初始化主导航组件")
            
            self.current_nav = "home"  # 默认选中首页
            self._setup_ui()
            self._apply_styles()
            self._connect_signals()
            
            log_system_event("主导航组件初始化完成", f"默认选中: {self.current_nav}")
            info("主导航组件初始化完成")
            
        except Exception as e:
            error(f"主导航组件初始化失败: {e}")
            log_system_event("主导航初始化失败", f"错误: {e}")
            raise
    
    def _setup_ui(self):
        """设置UI布局 - 微信风格"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 16)  # 增加左右边距
        layout.setAlignment(Qt.AlignCenter)  # 整体居中
            
        # 用户头像
        self.user_avatar = UserAvatar()
        self.user_avatar.clicked.connect(self.user_clicked.emit)
        layout.addWidget(self.user_avatar, 0, Qt.AlignCenter)
        
        # 间距
        layout.addSpacing(12)
        
        # 创建导航按钮 - 微信风格
        self.nav_buttons = {}
        nav_items = get_nav_primary_items()

        for item in nav_items:
            btn = NavButton(item["icon"], item["text"], item["key"] == self.current_nav, img_path=item.get("img"))
            btn.clicked.connect(lambda checked, k=item["key"]: self._on_nav_clicked(k))
            self.nav_buttons[item["key"]] = btn
            layout.addWidget(btn, 0, Qt.AlignCenter)
        
        # 弹性空间
        layout.addStretch()
        
        # 底部设置按钮
        self.settings_btn = NavButton("⚙️", "设置")
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self.settings_btn, 0, Qt.AlignCenter)
    
    def _apply_styles(self):
        from styles.constants import Colors
        self.setStyleSheet(f"""
            QWidget {{
                background: "#f7f7f7";
                border-right: 1px solid {Colors.BORDER_LIGHT};
                min-width: 64px;
                max-width: 64px;
            }}
        """)

    
    def _connect_signals(self):
        """连接信号"""
        pass
    
    def _on_nav_clicked(self, nav_key):
        """处理导航点击"""
        if nav_key != self.current_nav:
            # 更新按钮状态
            if self.current_nav in self.nav_buttons:
                self.nav_buttons[self.current_nav].set_active(False)
            
            self.current_nav = nav_key
            self.nav_buttons[nav_key].set_active(True)
            
            # 发送信号
            self.nav_changed.emit(nav_key)
    
    def refresh_styles(self):
        """刷新样式 - 支持主题切换"""
        # 重新应用主组件样式
        self._apply_styles()
        
        # 刷新用户头像样式
        self.user_avatar.refresh_styles()
        
        # 刷新所有导航按钮样式
        for btn in self.nav_buttons.values():
            btn.refresh_styles()
        
        # 刷新设置按钮样式
        self.settings_btn.refresh_styles()
