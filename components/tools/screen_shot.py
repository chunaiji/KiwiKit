import sys
import os
import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QLabel, QSizePolicy,
    QSpinBox, QColorDialog, QLineEdit, QComboBox, QToolButton, QFrame
)
from PySide6.QtGui import QGuiApplication, QPainter, QColor, QPen, QMouseEvent, QPixmap, QFont, QAction, QIcon
from PySide6.QtCore import Qt, QRect, QPoint, Signal

from components.base_content import BaseContent
from components.base_bootstrap import Container, Row, Col, Spacer
from utils.logger import get_logger
from styles.constants import Colors
from styles.factory import ButtonStyles
from styles.widgets import SpinBoxStyles, ComboBoxStyles, LineEditStyles


class SnipOverlay(QWidget):
    """全屏截图蒙版，支持多屏幕，鼠标拖拽选取区域截图"""
    def __init__(self, callback):
        super().__init__()
        self.setWindowTitle("拖拽选取截屏区域，按Esc取消")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 初始化日志
        self.logger = get_logger(__name__)

        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False
        self.selection_rect = QRect()
        self.callback = callback  # 截图完成后回调，传递QPixmap

        try:
            # 设置窗口为所有屏幕联合区域
            virtual_geometry = QGuiApplication.primaryScreen().virtualGeometry()
            self.setGeometry(virtual_geometry)
            self.logger.info(f"截屏覆盖层初始化: {virtual_geometry}")

            # 组合所有屏幕为一张背景图
            self.background = QPixmap(virtual_geometry.size())
            self.background.fill(Qt.transparent)
            painter = QPainter(self.background)

            screen_count = 0
            for screen in QGuiApplication.screens():
                geo = screen.geometry()
                pix = screen.grabWindow(0)
                painter.drawPixmap(geo.topLeft() - virtual_geometry.topLeft(), pix)
                screen_count += 1
            painter.end()
            
            self.logger.info(f"已捕获 {screen_count} 个屏幕的背景图")
            
        except Exception as e:
            self.logger.error(f"截屏覆盖层初始化失败: {e}")
            raise

    def paintEvent(self, event):
        painter = QPainter(self)

        # 1. 绘制完整背景截图
        painter.drawPixmap(0, 0, self.background)

        # 2. 绘制半透明遮罩
        painter.fillRect(self.rect(), QColor(0, 0, 0, 76))  # 30% 黑色遮罩

        # 3. 如果有选区，绘制真实区域和边框
        if self.selection_rect.isValid():
            cropped = self.background.copy(self.selection_rect)
            painter.drawPixmap(self.selection_rect.topLeft(), cropped)

            pen = QPen(QColor(0, 255, 0), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.selection_rect.normalized())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = self.start_pos
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_selecting:
            self.end_pos = event.pos()
            self.selection_rect = QRect(self.start_pos, self.end_pos).normalized()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.end_pos = event.pos()
            self.selection_rect = QRect(self.start_pos, self.end_pos).normalized()
            self.is_selecting = False
            self.update()
            self.take_screenshot()
            self.close()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.selection_rect.isValid():
            self.is_selecting = False
            self.update()
            self.take_screenshot()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def take_screenshot(self):
        """执行截图"""
        try:
            self.hide()
            QGuiApplication.processEvents()

            # 检查选择区域是否有效
            if not self.selection_rect.isValid() or self.selection_rect.isEmpty():
                self.logger.warning("截屏区域无效")
                QMessageBox.warning(self, "失败", "截屏区域无效，请重新选择")
                return

            # 从背景图中截取选中区域
            screenshot = self.background.copy(self.selection_rect)
            
            if screenshot.isNull():
                self.logger.error("截图结果为空")
                QMessageBox.warning(self, "失败", "截屏失败，请重试")
                return

            # 记录截图信息
            size = screenshot.size()
            pos = self.selection_rect.topLeft()
            self.logger.info(f"截图成功: 位置({pos.x()}, {pos.y()}), 尺寸({size.width()}x{size.height()})")

            if self.callback:
                self.callback(screenshot)
                
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            QMessageBox.warning(self, "错误", f"截图失败:\n{e}")


class ScreenshotEditor(QLabel):
    """可编辑的截图预览器，支持添加文字和绘制图案"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 400)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: white; 
                border: 2px solid {Colors.BORDER_LIGHT}; 
                border-radius: 8px;
                padding: 15px;
                color: {Colors.TEXT_SECONDARY};
                font-size: 14px;
            }}
        """)
        self.setText("📷 点击【开始截屏】进行截图")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 编辑状态
        self.original_pixmap = None  # 原始截图
        self.edit_pixmap = None      # 编辑中的截图
        self.is_drawing = False
        self.last_point = QPoint()
        
        # 绘制工具设置
        self.pen_color = QColor(255, 0, 0)  # 红色
        self.pen_width = 3
        self.current_tool = "pen"  # pen, text, rectangle, circle
        
        # 文字工具设置
        self.text_content = ""
        self.text_font = QFont("Arial", 16, QFont.Bold)  # 更大字体，加粗显示
        self.text_color = QColor(0, 0, 0)
        
        # 形状绘制状态
        self.shape_start_point = None
        
    def set_screenshot(self, pixmap: QPixmap):
        """设置截图"""
        self.original_pixmap = pixmap.copy()
        self.edit_pixmap = pixmap.copy()
        self.update_display()
        
    def update_display(self):
        """更新显示"""
        if self.edit_pixmap:
            scaled_pixmap = self.edit_pixmap.scaled(
                self.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        
    def set_pen_color(self, color: QColor):
        """设置画笔颜色"""
        self.pen_color = color
        
    def set_pen_width(self, width: int):
        """设置画笔宽度"""
        self.pen_width = width
        
    def set_tool(self, tool: str):
        """设置当前工具"""
        self.current_tool = tool
        
    def set_text_content(self, text: str):
        """设置文字内容"""
        self.text_content = text
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.edit_pixmap:
            # 将鼠标坐标转换到原图坐标
            label_size = self.size()
            pixmap_size = self.edit_pixmap.size()
            
            # 计算缩放比例
            scale_x = pixmap_size.width() / label_size.width()
            scale_y = pixmap_size.height() / label_size.height()
            scale = max(scale_x, scale_y)
            
            # 计算实际显示区域
            display_w = int(pixmap_size.width() / scale)
            display_h = int(pixmap_size.height() / scale)
            offset_x = (label_size.width() - display_w) // 2
            offset_y = (label_size.height() - display_h) // 2
            
            # 转换坐标
            x = int((event.pos().x() - offset_x) * scale)
            y = int((event.pos().y() - offset_y) * scale)
            
            if 0 <= x < pixmap_size.width() and 0 <= y < pixmap_size.height():
                current_point = QPoint(x, y)
                self.last_point = current_point
                self.is_drawing = True
                
                if self.current_tool == "text" and self.text_content:
                    self.add_text(current_point)
                elif self.current_tool in ["rectangle", "circle"]:
                    self.shape_start_point = current_point
                    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_drawing and self.edit_pixmap and self.current_tool == "pen":
            # 转换坐标（同mousePressEvent）
            label_size = self.size()
            pixmap_size = self.edit_pixmap.size()
            
            scale_x = pixmap_size.width() / label_size.width()
            scale_y = pixmap_size.height() / label_size.height()
            scale = max(scale_x, scale_y)
            
            display_w = int(pixmap_size.width() / scale)
            display_h = int(pixmap_size.height() / scale)
            offset_x = (label_size.width() - display_w) // 2
            offset_y = (label_size.height() - display_h) // 2
            
            x = int((event.pos().x() - offset_x) * scale)
            y = int((event.pos().y() - offset_y) * scale)
            
            if 0 <= x < pixmap_size.width() and 0 <= y < pixmap_size.height():
                current_point = QPoint(x, y)
                self.draw_line(self.last_point, current_point)
                self.last_point = current_point
                
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            
            # 处理形状绘制
            if self.current_tool in ["rectangle", "circle"] and self.shape_start_point:
                # 转换坐标
                label_size = self.size()
                pixmap_size = self.edit_pixmap.size()
                
                scale_x = pixmap_size.width() / label_size.width()
                scale_y = pixmap_size.height() / label_size.height()
                scale = max(scale_x, scale_y)
                
                display_w = int(pixmap_size.width() / scale)
                display_h = int(pixmap_size.height() / scale)
                offset_x = (label_size.width() - display_w) // 2
                offset_y = (label_size.height() - display_h) // 2
                
                x = int((event.pos().x() - offset_x) * scale)
                y = int((event.pos().y() - offset_y) * scale)
                
                if 0 <= x < pixmap_size.width() and 0 <= y < pixmap_size.height():
                    end_point = QPoint(x, y)
                    
                    if self.current_tool == "rectangle":
                        self.add_rectangle(self.shape_start_point, end_point)
                    elif self.current_tool == "circle":
                        # 计算半径
                        dx = end_point.x() - self.shape_start_point.x()
                        dy = end_point.y() - self.shape_start_point.y()
                        radius = int((dx**2 + dy**2)**0.5)
                        self.add_circle(self.shape_start_point, radius)
                
                self.shape_start_point = None
            
    def draw_line(self, start: QPoint, end: QPoint):
        """在图片上画线"""
        painter = QPainter(self.edit_pixmap)
        pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(start, end)
        painter.end()
        self.update_display()
        
    def add_text(self, position: QPoint):
        """在指定位置添加文字"""
        painter = QPainter(self.edit_pixmap)
        
        # 设置文字颜色（使用画笔颜色）
        painter.setPen(QPen(self.pen_color))
        painter.setFont(self.text_font)
        
        # 设置抗锯齿
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        
        # 绘制文字（加上偏移，避免被边框遮挡）
        text_position = QPoint(position.x() + 5, position.y() + 20)
        painter.drawText(text_position, self.text_content)
        
        painter.end()
        self.update_display()
        
    def add_rectangle(self, start: QPoint, end: QPoint):
        """添加矩形"""
        painter = QPainter(self.edit_pixmap)
        pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(pen) 
        painter.setBrush(Qt.NoBrush)
        rect = QRect(start, end)
        painter.drawRect(rect.normalized())
        painter.end()
        self.update_display()
        
    def add_circle(self, center: QPoint, radius: int):
        """添加圆形"""
        painter = QPainter(self.edit_pixmap)
        pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, radius, radius)
        painter.end()
        self.update_display()
        
    def reset_to_original(self):
        """重置到原始截图"""
        if self.original_pixmap:
            self.edit_pixmap = self.original_pixmap.copy()
            self.update_display()
            
    def get_edited_pixmap(self):
        """获取编辑后的截图"""
        return self.edit_pixmap


class ScreenshotWidget(BaseContent):
    def __init__(self):
        # 创建主体内容
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="📸 截屏工具", content_widget=content_widget)
        
        # 初始化日志
        self.logger = get_logger(__name__)
        self.current_screenshot = None  # 用于存储当前截图
        
        # 初始化状态
        self.set_status("ℹ️ 点击【开始截屏】开始截图")

    def _create_content_widget(self):
        """创建主体内容界面"""
        container = Container()
        
        # 编辑工具栏
        self._create_editing_toolbar(container)
        
        # 图片预览区域 - 占据大部分空间
        preview_row = Row()
        self.image_editor = ScreenshotEditor()
        self.image_editor.setMinimumSize(700, 500)  # 更大的预览区域
        preview_col = Col(widget=self.image_editor, span=12, alignment=Qt.AlignCenter)
        preview_row.addWidget(preview_col)
        container.layout().addLayout(preview_row)
        
        # 添加间距
        spacer_widget = Spacer()
        spacer_widget.setFixedHeight(15)
        container.layout().addWidget(spacer_widget)
        
        # 底部按钮区域 - 在同一行
        bottom_row = Row()
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 开始截屏按钮
        self.screenshot_btn = QPushButton("📸 开始截屏")
        self.screenshot_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.screenshot_btn.clicked.connect(self.start_snip)
        self.screenshot_btn.setMinimumHeight(40)
        button_layout.addWidget(self.screenshot_btn)
        
        # 添加弹性空间
        button_layout.addStretch()
        
        # 保存截图按钮
        self.save_btn = QPushButton("💾 保存截图")
        self.save_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.save_btn.clicked.connect(self.save_screenshot)
        self.save_btn.setEnabled(False)  # 初始状态禁用
        self.save_btn.setMinimumHeight(40)
        button_layout.addWidget(self.save_btn)
        
        bottom_col = Col(widget=button_widget, span=12)
        bottom_row.addWidget(bottom_col)
        container.layout().addLayout(bottom_row)
        
        return container
        
    def _create_editing_toolbar(self, container):
        """创建编辑工具栏"""
        toolbar_row = Row()
        
        # 工具栏容器
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        # 工具选择
        tool_label = QLabel("工具:")
        tool_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
        toolbar_layout.addWidget(tool_label)
        
        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["🖊️ 画笔", "📝 文字", "⬜ 矩形", "⭕ 圆形"])
        self.tool_combo.setObjectName("tool_combo")
        self.tool_combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("tool_combo"))
        self.tool_combo.currentTextChanged.connect(self._on_tool_changed)
        toolbar_layout.addWidget(self.tool_combo)
        
        # 分隔线
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        toolbar_layout.addWidget(separator1)
        
        # 颜色选择
        color_label = QLabel("颜色:")
        color_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
        toolbar_layout.addWidget(color_label)
        
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(30, 25)
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb(255, 0, 0);
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid {Colors.PRIMARY};
            }}
        """)
        self.color_btn.clicked.connect(self._choose_color)
        toolbar_layout.addWidget(self.color_btn)
        
        # 画笔粗细
        width_label = QLabel("粗细:")
        width_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
        toolbar_layout.addWidget(width_label)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 20)
        self.width_spin.setValue(3)
        self.width_spin.setObjectName("width_spinbox")
        self.width_spin.setStyleSheet(SpinBoxStyles.get_enhanced_style("width_spinbox"))
        self.width_spin.valueChanged.connect(self._on_width_changed)
        toolbar_layout.addWidget(self.width_spin)
        
        # 分隔线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        toolbar_layout.addWidget(separator2)
        
        # 文字输入
        text_label = QLabel("文字:")
        text_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
        toolbar_layout.addWidget(text_label)
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("输入要添加的文字...")
        self.text_input.setMinimumWidth(150)
        self.text_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.text_input.textChanged.connect(self._on_text_changed)
        toolbar_layout.addWidget(self.text_input)
        
        # 分隔线
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.VLine)
        separator3.setFrameShadow(QFrame.Sunken)
        toolbar_layout.addWidget(separator3)
        
        # 重置按钮
        self.reset_btn = QPushButton("🔄 重置")
        self.reset_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.reset_btn.clicked.connect(self._reset_image)
        self.reset_btn.setEnabled(False)
        toolbar_layout.addWidget(self.reset_btn)
        
        # 使用说明
        help_label = QLabel("💡 画笔：拖拽绘制 | 文字：单击添加 | 矩形/圆形：拖拽绘制")
        help_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-style: italic;")
        toolbar_layout.addWidget(help_label)
        
        # 添加弹性空间
        toolbar_layout.addStretch()
        
        # 工具栏样式
        toolbar_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BACKGROUND_LIGHT};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 8px;
                margin-bottom: 10px;
            }}
        """)
        
        toolbar_col = Col(widget=toolbar_widget, span=12)
        toolbar_row.addWidget(toolbar_col)
        container.layout().addLayout(toolbar_row)
        
    def _on_tool_changed(self, tool_text):
        """工具切换"""
        tool_map = {
            "🖊️ 画笔": "pen",
            "📝 文字": "text", 
            "⬜ 矩形": "rectangle",
            "⭕ 圆形": "circle"
        }
        tool = tool_map.get(tool_text, "pen")
        self.image_editor.set_tool(tool)
        
        # 更新状态提示
        if hasattr(self, 'current_screenshot') and self.current_screenshot:
            if tool == "pen":
                self.set_status("🖊️ 画笔模式：在图片上拖拽绘制")
            elif tool == "text":
                self.set_status("📝 文字模式：在图片上单击添加文字（需先输入文字内容）")
            elif tool == "rectangle":
                self.set_status("⬜ 矩形模式：在图片上拖拽绘制矩形")
            elif tool == "circle":
                self.set_status("⭕ 圆形模式：在图片上拖拽绘制圆形")
        
    def _choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor(self.image_editor.pen_color, self, "选择颜色")
        if color.isValid():
            self.image_editor.set_pen_color(color)
            self.color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgb({color.red()}, {color.green()}, {color.blue()});
                    border: 2px solid {Colors.BORDER_LIGHT};
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    border: 2px solid {Colors.PRIMARY};
                }}
            """)
            
    def _on_width_changed(self, width):
        """画笔粗细改变"""
        self.image_editor.set_pen_width(width)
        
    def _on_text_changed(self, text):
        """文字内容改变"""
        self.image_editor.set_text_content(text)
        
        # 如果当前是文字工具，更新提示
        if self.image_editor.current_tool == "text" and hasattr(self, 'current_screenshot') and self.current_screenshot:
            if text.strip():
                self.set_status("📝 文字已准备好，在图片上单击添加文字")
            else:
                self.set_status("📝 请先输入要添加的文字内容")
        
    def _reset_image(self):
        """重置图片"""
        self.image_editor.reset_to_original()

    def start_snip(self):
        """开始截屏"""
        try:
            self.logger.info("用户开始截屏")
            self.set_status("📷 请拖拽选择截屏区域，按Esc取消")
            
            self.overlay = SnipOverlay(self.handle_screenshot)
            self.overlay.show()
            
        except Exception as e:
            self.logger.error(f"启动截屏失败: {e}")
            self.set_status(f"❌ 启动截屏失败: {e}")
            QMessageBox.warning(self, "错误", f"启动截屏失败:\n{e}")

    def handle_screenshot(self, pixmap: QPixmap):
        """处理截图结果"""
        try:
            if pixmap.isNull():
                self.logger.warning("截图为空")
                self.set_status("⚠️ 截图为空，请重新截屏")
                return
            
            self.current_screenshot = pixmap  # 保存截图
            
            # 设置到编辑器中
            self.image_editor.set_screenshot(pixmap)
            
            # 启用相关按钮
            self.save_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
            
            # 记录截图信息
            size = pixmap.size()
            self.logger.info(f"截图成功: {size.width()}x{size.height()}")
            self.set_status(f"✅ 截图完成 ({size.width()}x{size.height()})，可编辑并保存")
            
        except Exception as e:
            self.logger.error(f"处理截图失败: {e}")
            self.set_status(f"❌ 处理截图失败: {e}")

    def save_screenshot(self):
        """保存截图"""
        try:
            # 获取编辑后的图片
            edited_pixmap = self.image_editor.get_edited_pixmap()
            if not edited_pixmap or edited_pixmap.isNull():
                QMessageBox.information(self, "无截图", "当前没有截图可保存。")
                return

            # 选择保存目录
            folder = QFileDialog.getExistingDirectory(self, "选择保存截图的目录")
            if not folder:
                return

            # 生成文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(folder, f"screenshot_{timestamp}.png")

            # 保存编辑后的文件
            if edited_pixmap.save(file_path, "PNG"):
                self.logger.info(f"截图保存成功: {file_path}")
                self.set_status(f"✅ 截图已保存: {os.path.basename(file_path)}")
                QMessageBox.information(self, "保存成功", f"截图已保存到:\n{file_path}")
            else:
                self.logger.error(f"截图保存失败: {file_path}")
                self.set_status("❌ 截图保存失败")
                QMessageBox.warning(self, "保存失败", "截图保存失败，请检查文件路径和权限")
                
        except Exception as e:
            self.logger.error(f"保存截图异常: {e}")
            self.set_status(f"❌ 保存失败: {e}")
            QMessageBox.warning(self, "错误", f"保存截图时发生错误:\n{e}")
