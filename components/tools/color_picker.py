from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor, QColor, QGuiApplication, QPixmap, QPainter, QPen, QMouseEvent
from PySide6.QtWidgets import (
    QColorDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFormLayout, QGroupBox, QGridLayout
)
from components.base_content import BaseContent
from styles.factory import ButtonStyles, LineEditStyles, GroupBoxStyles
from styles.constants import Colors, Sizes


class ColorPickerOverlay(QWidget):
    """屏幕取色覆盖层，让用户点击选择颜色"""
    def __init__(self, callback):
        super().__init__()
        self.setWindowTitle("点击屏幕获取颜色，按Esc取消")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        self.callback = callback  # 取色完成后回调
        self.screen_pixmap = None
        
        # 设置窗口为所有屏幕联合区域
        virtual_geometry = QGuiApplication.primaryScreen().virtualGeometry()
        self.setGeometry(virtual_geometry)
        
        # 设置鼠标为十字准星
        self.setCursor(QCursor(Qt.CrossCursor))
        
        # 截取整个屏幕
        self._capture_screen()
    
    def _capture_screen(self):
        """截取整个屏幕"""
        virtual_geometry = QGuiApplication.primaryScreen().virtualGeometry()
        self.screen_pixmap = QPixmap(virtual_geometry.size())
        self.screen_pixmap.fill(Qt.transparent)
        
        painter = QPainter(self.screen_pixmap)
        for screen in QGuiApplication.screens():
            geo = screen.geometry()
            pix = screen.grabWindow(0)
            painter.drawPixmap(geo.topLeft() - virtual_geometry.topLeft(), pix)
        painter.end()
    
    def paintEvent(self, event):
        """绘制半透明覆盖层"""
        painter = QPainter(self)
        
        # 绘制背景截图
        if self.screen_pixmap:
            painter.drawPixmap(0, 0, self.screen_pixmap)
        
        # 绘制半透明遮罩
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))  # 40% 黑色遮罩
        
        # 在鼠标位置绘制十字准星
        mouse_pos = self.mapFromGlobal(QCursor.pos())
        pen = QPen(QColor(255, 255, 255), 2)
        painter.setPen(pen)
        
        # 绘制十字线
        painter.drawLine(mouse_pos.x() - 20, mouse_pos.y(), mouse_pos.x() + 20, mouse_pos.y())
        painter.drawLine(mouse_pos.x(), mouse_pos.y() - 20, mouse_pos.x(), mouse_pos.y() + 20)
        
        # 绘制中心点
        painter.drawRect(mouse_pos.x() - 2, mouse_pos.y() - 2, 4, 4)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标点击事件，获取点击位置的颜色"""
        if event.button() == Qt.LeftButton:
            click_pos = event.pos()
            
            # 从截图中获取像素颜色
            if self.screen_pixmap:
                image = self.screen_pixmap.toImage()
                if not image.isNull() and click_pos.x() < image.width() and click_pos.y() < image.height():
                    pixel_color = image.pixelColor(click_pos.x(), click_pos.y())
                    
                    # 转换为 Hex 颜色值
                    hex_color = "#{:02X}{:02X}{:02X}".format(
                        pixel_color.red(),
                        pixel_color.green(),
                        pixel_color.blue()
                    )
                    
                    if self.callback:
                        self.callback(hex_color, click_pos)
            
            self.close()
    
    def keyPressEvent(self, event):
        """按键事件，Esc键取消"""
        if event.key() == Qt.Key_Escape:
            self.close()
    
    def mouseMoveEvent(self, event):
        """鼠标移动时更新十字准星"""
        self.update()

class ColorPickerWidget(BaseContent):
    """颜色选择器工具界面"""

    def __init__(self):
        # 创建主体内容
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="🎨 颜色选择器", content_widget=content_widget)
        # 初始化状态
        self.set_status("ℹ️ 请输入 RGB 值或 Hex 颜色代码")
        self.pick_color_mode = False  # 标记是否处于颜色拾取模式

    def _create_content_widget(self):
        """创建主体内容界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # RGB输入区域
        rgb_group = QGroupBox("RGB 输入")
        rgb_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        rgb_layout = QGridLayout(rgb_group)
        
        # R输入
        rgb_layout.addWidget(QLabel("R:"), 0, 0)
        self.r_input = QLineEdit()
        self.r_input.setPlaceholderText("0-255")
        self.r_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.r_input.textChanged.connect(self._on_rgb_changed)
        rgb_layout.addWidget(self.r_input, 0, 1)
        
        # G输入
        rgb_layout.addWidget(QLabel("G:"), 0, 2)
        self.g_input = QLineEdit()
        self.g_input.setPlaceholderText("0-255")
        self.g_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.g_input.textChanged.connect(self._on_rgb_changed)
        rgb_layout.addWidget(self.g_input, 0, 3)
        
        # B输入
        rgb_layout.addWidget(QLabel("B:"), 0, 4)
        self.b_input = QLineEdit()
        self.b_input.setPlaceholderText("0-255")
        self.b_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.b_input.textChanged.connect(self._on_rgb_changed)
        rgb_layout.addWidget(self.b_input, 0, 5)
        
        layout.addWidget(rgb_group)
        
        # Hex输入区域
        hex_group = QGroupBox("Hex 输入")
        hex_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        hex_layout = QHBoxLayout(hex_group)
        
        hex_layout.addWidget(QLabel("Hex:"))
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("#FFFFFF")
        self.hex_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.hex_input.textChanged.connect(self._on_hex_changed)
        hex_layout.addWidget(self.hex_input)
        
        layout.addWidget(hex_group)
        
        # 颜色预览区域
        preview_group = QGroupBox("颜色预览")
        preview_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        preview_layout = QVBoxLayout(preview_group)
        
        self.color_preview = QLabel("颜色预览")
        self.color_preview.setMinimumHeight(80)
        self.color_preview.setAlignment(Qt.AlignCenter)
        self.color_preview.setStyleSheet(f"""
            QLabel {{
                background-color: #FFFFFF;
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: {Sizes.RADIUS_MEDIUM};
                font-size: {Sizes.FONT_MEDIUM};
                font-weight: bold;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        preview_layout.addWidget(self.color_preview)
        
        layout.addWidget(preview_group)
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        
        # 颜色选择器按钮
        self.color_dialog_btn = QPushButton("🎨 打开颜色选择器")
        self.color_dialog_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.color_dialog_btn.clicked.connect(self._open_color_dialog)
        button_layout.addWidget(self.color_dialog_btn)
        
        # 屏幕取色按钮
        self.pick_btn = QPushButton("🖱️ 屏幕取色")
        self.pick_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.pick_btn.clicked.connect(self.pick_color)
        button_layout.addWidget(self.pick_btn)
        
        layout.addLayout(button_layout)
        
        return widget

    def pick_color(self):
        """启动屏幕取色模式"""
        self._update_status("请点击屏幕任意位置获取颜色...", "normal")
        self.color_overlay = ColorPickerOverlay(self._handle_color_picked)
        self.color_overlay.show()
    
    def _handle_color_picked(self, hex_color, position):
        """处理屏幕取色结果"""
        self._set_color(hex_color)
        self._update_status(f"✅ 已采集颜色: {hex_color} (位置: {position.x()}, {position.y()})", "success")

    def _set_color(self, hex_color):
        """设置采集到的颜色并更新输入框与预览"""
        # 阻止信号触发避免循环
        self.r_input.blockSignals(True)
        self.g_input.blockSignals(True)
        self.b_input.blockSignals(True)
        self.hex_input.blockSignals(True)

        # 计算 RGB 值
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        # 更新输入框
        self.r_input.setText(str(r))
        self.g_input.setText(str(g))
        self.b_input.setText(str(b))
        self.hex_input.setText(hex_color)

        # 更新颜色预览
        self.update_preview(hex_color)

        # 恢复信号
        self.r_input.blockSignals(False)
        self.g_input.blockSignals(False)
        self.b_input.blockSignals(False)
        self.hex_input.blockSignals(False)

    def _open_color_dialog(self):
        """打开系统颜色选择对话框"""
        color = QColorDialog.getColor(Qt.white, self, "选择颜色")
        if color.isValid():
            hex_color = color.name()
            self._set_color(hex_color)
            self._update_status(f"✅ 已选择颜色: {hex_color}", "success")

    def _on_rgb_changed(self):
        """RGB输入变化时的处理"""
        try:
            r = int(self.r_input.text() or 0)
            g = int(self.g_input.text() or 0)
            b = int(self.b_input.text() or 0)
            
            # 验证范围
            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                hex_color = "#{:02X}{:02X}{:02X}".format(r, g, b)
                
                # 阻止Hex输入框的信号避免循环
                self.hex_input.blockSignals(True)
                self.hex_input.setText(hex_color)
                self.hex_input.blockSignals(False)
                
                self.update_preview(hex_color)
                self._update_status(f"✅ RGB({r}, {g}, {b}) = {hex_color}", "success")
            else:
                self._update_status("❌ RGB值必须在0-255范围内", "error")
        except ValueError:
            self._update_status("❌ 请输入有效的RGB数值", "error")

    def _on_hex_changed(self):
        """Hex输入变化时的处理"""
        hex_color = self.hex_input.text().strip()
        if not hex_color.startswith('#'):
            hex_color = '#' + hex_color
            
        try:
            if len(hex_color) == 7:
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
                
                # 阻止RGB输入框的信号避免循环
                self.r_input.blockSignals(True)
                self.g_input.blockSignals(True)
                self.b_input.blockSignals(True)
                
                self.r_input.setText(str(r))
                self.g_input.setText(str(g))
                self.b_input.setText(str(b))
                
                self.r_input.blockSignals(False)
                self.g_input.blockSignals(False)
                self.b_input.blockSignals(False)
                
                self.update_preview(hex_color)
                self._update_status(f"✅ {hex_color} = RGB({r}, {g}, {b})", "success")
            else:
                self._update_status("❌ Hex颜色格式应为 #RRGGBB", "error")
        except ValueError:
            self._update_status("❌ 请输入有效的Hex颜色值", "error")

    def update_preview(self, color):
        """更新颜色预览"""
        try:
            # 判断颜色深浅来设置文字颜色
            if color.startswith('#') and len(color) == 7:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                # 计算亮度 (0.299*R + 0.587*G + 0.114*B)
                brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                text_color = "#000000" if brightness > 0.5 else "#FFFFFF"
            else:
                text_color = Colors.TEXT_SECONDARY
            
            self.color_preview.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    border: 2px solid {Colors.BORDER_LIGHT};
                    border-radius: {Sizes.RADIUS_MEDIUM};
                    font-size: {Sizes.FONT_SMALL};
                    font-weight: bold;
                    color: {text_color};
                }}
            """)
            self.color_preview.setText(color)

        except Exception:
            self.color_preview.setStyleSheet(f"""
                QLabel {{
                    background-color: #FFFFFF;
                    border: 2px solid {Colors.BORDER_LIGHT};
                    border-radius: {Sizes.RADIUS_MEDIUM};
                    font-size: {Sizes.FONT_MEDIUM};
                    font-weight: bold;
                    color: {Colors.TEXT_SECONDARY};
                }}
            """)
            self.color_preview.setText("预览失败")

    def _update_status(self, message, status_type="normal"):
        """更新状态标签"""
        icons = {
            "success": "✅",
            "error": "❌", 
            "normal": "ℹ️"
        }
        
        icon = icons.get(status_type, icons["normal"])
        self.set_status(f"{icon} {message}")
