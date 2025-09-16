"""
文本对比工具组件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFileDialog, QMessageBox, QGroupBox, QSplitter
)
from PySide6.QtGui import QTextCharFormat, QColor, QTextCursor, QFont
from PySide6.QtCore import Qt

from components.base_content import BaseContent
from styles.constants import Colors
from styles.widgets import (
    ButtonStyles, TextEditStyles, GroupBoxStyles
)



class DraggableTextEdit(QTextEdit):
    """支持拖放文件的 QTextEdit，用于文本对比工具"""
    def __init__(self, parent=None, side="left"):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.side = side  # 标记是左侧还是右侧
        self.diff_tool = None  # 延迟设置 FileDiffTool 引用
        
        # 设置样式，使拖放区域更明显
        self.setStyleSheet("""
            QTextEdit {
                border: 2px dashed #cccccc;
                background-color: #fafafa;
            }
            QTextEdit:hover {
                border: 2px dashed #07c160;
                background-color: #f0f9ff;
            }
        """)

    def set_diff_tool(self, diff_tool):
        """设置 FileDiffTool 引用"""
        self.diff_tool = diff_tool

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # 检查是否有文件URL
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                event.acceptProposedAction()
                # 改变外观提示用户可以拖放
                self.setStyleSheet("""
                    QTextEdit {
                        border: 2px dashed #07c160;
                        background-color: #e8f5e8;
                    }
                """)
            else:
                event.ignore()
        else:
            super().dragEnterEvent(event)

    def dragLeaveEvent(self, event):
        # 恢复正常外观
        if hasattr(self, 'diff_tool') and self.diff_tool:
            self.setStyleSheet(TextEditStyles.get_code_style())
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                file_path = urls[0].toLocalFile()
                
                if not self.diff_tool:
                    return

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    # 设置内容并设为只读
                    self.setPlainText(content)
                    self.setReadOnly(True)

                    # 更新路径与文件名标签
                    filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
                    
                    if self.side == "left":
                        self.diff_tool.left_file_path = file_path
                        self.diff_tool.left_file_label.setText(f"已拖入: {filename}")
                        self.diff_tool.left_file_label.setStyleSheet(f"color: {Colors.WECHAT_GREEN}; padding: 5px; font-weight: bold;")
                    else:
                        self.diff_tool.right_file_path = file_path
                        self.diff_tool.right_file_label.setText(f"已拖入: {filename}")
                        self.diff_tool.right_file_label.setStyleSheet(f"color: {Colors.WECHAT_GREEN}; padding: 5px; font-weight: bold;")
                    
                    # 恢复正常样式
                    self.setStyleSheet(TextEditStyles.get_code_style())
                    
                    self.diff_tool._update_compare_btn_state()
                    self.diff_tool.set_status(f"✅ 文件拖放成功: {filename}")

                except Exception as e:
                    QMessageBox.warning(self, "拖放错误", f"读取文件失败：{str(e)}")
                    if self.diff_tool:
                        self.diff_tool.set_status("❌ 拖放失败")
                    # 恢复正常样式
                    if hasattr(self, 'diff_tool') and self.diff_tool:
                        self.setStyleSheet(TextEditStyles.get_code_style())
                        
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
            
    def clear(self):
        """清空内容时同时设置为可编辑状态"""
        super().clear()
        self.setReadOnly(False)
        # 恢复拖放提示样式
        if hasattr(self, 'diff_tool') and self.diff_tool:
            self.setStyleSheet("""
                QTextEdit {
                    border: 2px dashed #cccccc;
                    background-color: #fafafa;
                }
                QTextEdit:hover {
                    border: 2px dashed #07c160;
                    background-color: #f0f9ff;
                }
            """)


class FileDiffTool(BaseContent):
    def __init__(self):
        self.left_file_path = None
        self.right_file_path = None

        # 创建主要内容组件
        content_widget = self._create_content_widget()
        
        # 初始化基类
        super().__init__(title="📄 文本对比工具", content_widget=content_widget)
        
        # 设置文本编辑器的 diff_tool 引用
        self.left_text.set_diff_tool(self)
        self.right_text.set_diff_tool(self)

    
    def _create_content_widget(self):
        """创建主要内容区域组件 - 使用全局样式的传统布局"""
        
        # 主容器
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        
        # 创建文本编辑器
        self.left_text = DraggableTextEdit(side="left")
        self.left_text.setPlaceholderText("请粘贴原始代码或拖放文件到这里...")
        self.left_text.setObjectName("left_text")
        self.left_text.setStyleSheet(TextEditStyles.get_standard_style("left_text"))
        
        self.right_text = DraggableTextEdit(side="right")
        self.right_text.setPlaceholderText("请粘贴原始代码或拖放文件到这里...")
        self.right_text.setObjectName("right_text")
        self.right_text.setStyleSheet(TextEditStyles.get_standard_style("right_text"))
        
        # 使用水平布局创建左右对比面板
        text_compare_widget = QWidget()
        text_compare_layout = QHBoxLayout(text_compare_widget)
        text_compare_layout.setSpacing(15)
        
        # 左侧文本面板（包含文件选择器）
        left_panel = self._create_text_panel_with_selector("左侧文件", self.left_text, "left", "📄 选择左侧文件", self._choose_left_file)
        text_compare_layout.addWidget(left_panel)
        
        # 右侧文本面板（包含文件选择器）
        right_panel = self._create_text_panel_with_selector("右侧文件", self.right_text, "right", "📄 选择右侧文件", self._choose_right_file)
        text_compare_layout.addWidget(right_panel)
        
        main_layout.addWidget(text_compare_widget, 1)  # 给对比区域更多空间
        
        # 操作按钮区域 - 放在底部
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.clear_btn = QPushButton("🧹 清空结果")
        self.clear_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.clear_btn.clicked.connect(self._clear_results)
        
        self.compare_btn = QPushButton("🔍 开始对比")
        self.compare_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.compare_btn.clicked.connect(self._compare_files)
        self.compare_btn.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.compare_btn)
        
        main_layout.addWidget(button_widget)
        
        # 状态标签已由BaseContent类处理
        return main_widget
    
    def _create_file_selector(self, side, button_text, callback):
        """创建文件选择器组件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 选择按钮
        btn = QPushButton(button_text)
        btn.setStyleSheet(ButtonStyles.get_secondary_style())
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        
        # 文件名标签
        label = QLabel("未选择文件")
        label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 8px; font-size: 13px;")
        layout.addWidget(label, 1)
        
        # 存储引用
        if side == "left":
            self.left_file_btn = btn
            self.left_file_label = label
        else:
            self.right_file_btn = btn
            self.right_file_label = label
            
        return widget
    
    def _create_text_panel(self, title, text_edit):
        """创建文本面板组件"""
        panel = QGroupBox(title)
        panel.setStyleSheet(GroupBoxStyles.get_standard_style())
        layout = QVBoxLayout(panel)
        layout.addWidget(text_edit)
        return panel
    
    def _create_text_panel_with_selector(self, title, text_edit, side, button_text, callback):
        """创建包含文件选择器的文本面板组件"""
        panel = QGroupBox(title)
        panel.setStyleSheet(GroupBoxStyles.get_standard_style())
        layout = QVBoxLayout(panel)
        
        # 添加文件选择器
        file_selector = self._create_file_selector(side, button_text, callback)
        layout.addWidget(file_selector)
        
        # 添加文本编辑器
        layout.addWidget(text_edit)
        
        return panel
    
    def _choose_left_file(self):
        """选择左侧文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择左侧文件", 
            "", 
            "文本文件 (*.txt *.py *.js *.html *.css *.json *.xml *.md);;所有文件 (*.*)"
        )
        if file_path:
            self.left_file_path = file_path
            filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            self.left_file_label.setText(f"已选择: {filename}")
            self.left_file_label.setStyleSheet(f"color: {Colors.WECHAT_GREEN}; padding: 5px; font-weight: bold;")
            self._load_file_content(file_path, self.left_text)
            self._update_compare_btn_state()
    
    def _choose_right_file(self):
        """选择右侧文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择右侧文件", 
            "", 
            "文本文件 (*.txt *.py *.js *.html *.css *.json *.xml *.md);;所有文件 (*.*)"
        )
        if file_path:
            self.right_file_path = file_path
            filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            self.right_file_label.setText(f"已选择: {filename}")
            self.right_file_label.setStyleSheet(f"color: {Colors.WECHAT_GREEN}; padding: 5px; font-weight: bold;")
            self._load_file_content(file_path, self.right_text)
            self._update_compare_btn_state()
    
    def _load_file_content(self, file_path, text_edit):
        """加载文件内容到文本编辑器"""
        try:
            with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
                content = f.read()
            text_edit.setPlainText(content)
            text_edit.setReadOnly(True)
            # 恢复正常样式
            text_edit.setStyleSheet(TextEditStyles.get_code_style())
        except Exception as e:
            QMessageBox.warning(self, "文件读取警告", f"无法读取文件 {file_path}:\n{str(e)}")
    
    def _update_compare_btn_state(self):
        """更新对比按钮状态"""
        if self.left_file_path and self.right_file_path:
            self.compare_btn.setEnabled(True)
            self._update_status("点击'开始对比'按钮进行文件比较", "normal")
        else:
            self.compare_btn.setEnabled(False)
    
    def _clear_results(self):
        """清空对比结果"""
        self.left_text.clear()
        self.right_text.clear()
        self.left_file_path = None
        self.right_file_path = None
        self.left_file_label.setText("未选择文件")
        self.right_file_label.setText("未选择文件")
        self.left_file_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 5px;")
        self.right_file_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 5px;")
        self._update_compare_btn_state()
        self._update_status("请选择两个文件进行对比", "normal")
    
    def _compare_files(self):
        """对比两个文件"""
        if not self.left_file_path or not self.right_file_path:
            QMessageBox.warning(self, "警告", "请先选择两个文件！")
            return
            
        try:
            # 重新读取文件内容以确保最新
            with open(self.left_file_path, "r", encoding="utf-8", errors='ignore') as f:
                left_lines = f.readlines()
            with open(self.right_file_path, "r", encoding="utf-8", errors='ignore') as f:
                right_lines = f.readlines()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"文件读取失败：{str(e)}")
            return
        
        # 清除之前的高亮
        self._clear_highlights()
        
        max_lines = max(len(left_lines), len(right_lines))
        diff_count = 0
        
        # 设置不同类型的格式
        diff_format = QTextCharFormat()
        diff_format.setBackground(QColor("#ffeb3b"))  # 黄色背景表示不同
        
        missing_format = QTextCharFormat()
        missing_format.setBackground(QColor("#ffcdd2"))  # 浅红色背景表示缺失
        
        # 重新设置文本内容并进行逐行比较
        self.left_text.clear()
        self.right_text.clear()
        
        left_content = ""
        right_content = ""
        
        for i in range(max_lines):
            left_line = left_lines[i].rstrip('\n') if i < len(left_lines) else ""
            right_line = right_lines[i].rstrip('\n') if i < len(right_lines) else ""
            
            left_content += left_line + '\n'
            right_content += right_line + '\n'
            
            if left_line != right_line:
                diff_count += 1
        
        # 设置文本内容
        self.left_text.setPlainText(left_content)
        self.right_text.setPlainText(right_content)
        
        # 重新进行高亮处理
        for i in range(max_lines):
            left_line = left_lines[i].rstrip('\n') if i < len(left_lines) else ""
            right_line = right_lines[i].rstrip('\n') if i < len(right_lines) else ""
            
            if left_line != right_line:
                # 高亮不同的行
                if i < len(left_lines):
                    self._highlight_line(self.left_text, i, diff_format if left_line else missing_format)
                if i < len(right_lines):
                    self._highlight_line(self.right_text, i, diff_format if right_line else missing_format)
        
        # 更新状态
        if diff_count == 0:
            self._update_status("文件内容完全相同！", "success")
        else:
            self._update_status(f"共检测 {max_lines} 行，发现 {diff_count} 处差异", "warning")
    
    def _clear_highlights(self):
        """清除所有高亮"""
        # 清除左侧高亮
        cursor = self.left_text.textCursor()
        cursor.select(QTextCursor.Document)
        format = QTextCharFormat()
        format.setBackground(QColor("white"))
        cursor.setCharFormat(format)
        
        # 清除右侧高亮
        cursor = self.right_text.textCursor()
        cursor.select(QTextCursor.Document)
        format = QTextCharFormat()
        format.setBackground(QColor("white"))
        cursor.setCharFormat(format)
    
    def _highlight_line(self, text_edit: QTextEdit, line_number: int, fmt: QTextCharFormat):
        """高亮指定行"""
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.Start)
        
        # 移动到指定行
        for _ in range(line_number):
            cursor.movePosition(QTextCursor.Down)
            
        # 选中该行
        cursor.select(QTextCursor.LineUnderCursor)
        # 设置格式
        cursor.setCharFormat(fmt)
    
    def _update_status(self, message, status_type="normal"):
        """更新状态显示"""
        # BaseContent的set_status方法只接受文本参数
        self.set_status(message)
        

