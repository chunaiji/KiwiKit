"""
正则表达式测试工具组件
"""

import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QMessageBox, QSplitter, QGroupBox, 
    QPushButton, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor

from components.base_content import BaseContent
from styles.constants import Colors
from styles.widgets import (
    ButtonStyles, ComboBoxStyles, TextEditStyles, 
    GroupBoxStyles
)

class RegexFormatterWidget(BaseContent):
    """正则表达式测试工具界面"""
    
    def __init__(self):
        # 常用正则表达式示例
        self.regex_examples = {
            "邮箱地址": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "手机号（中国）": r"1[3-9]\d{9}",
            "IPv4 地址": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "日期 (YYYY-MM-DD)": r"\b\d{4}-\d{2}-\d{2}\b",
            "URL": r"https?://[^\s]+",
            "身份证号（18位）": r"\d{17}[\dXx]",
            "中文汉字": r"[\u4e00-\u9fa5]+",
            "邮政编码": r"\b\d{6}\b",
            "IPv6 地址": r"\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b",
            "浮点数": r"[+-]?\d+\.\d+",
            "正整数": r"\b[1-9]\d*\b",
            "负整数": r"\b-\d+\b",
            "车牌号（中国）": r"\b[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼][A-Z][A-Z0-9]{5}\b",
            "银行卡号（16~19位）": r"\b\d{16,19}\b",
            "MAC 地址": r"\b([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b",
            "时间（24小时制 HH:MM:SS）": r"\b([01]\d|2[0-3]):[0-5]\d:[0-5]\d\b",
            "QQ号": r"\b[1-9][0-9]{4,}\b",
            "微信号": r"\b[a-zA-Z][-_a-zA-Z0-9]{5,19}\b",
            "HTML标签": r"</?[\w\s=\"/.':;#-\/\?]+>",
            "十六进制颜色码": r"#(?:[0-9a-fA-F]{3}){1,2}\b",
            "文件路径（Windows）": r"[a-zA-Z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*",
            "文件路径（Linux/Mac）": r"/(?:[^/\0]+/)*[^/\0]*",
            "Base64 编码": r"(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?",
            "JSON 格式粗略匹配": r"\{[^{}]*\}",
            
            # 扩展部分
            "国际手机号（国际格式）": r"^\+?(\d{1,3})?(\d{1,4})?[-.\s]?\(?(\d{1,4})\)?[-.\s]?(\d{1,4})[-.\s]?\d{1,4}$",
            "HTML注释": r"<!--.*?-->",
            "HTML链接标签": r"<a\s+(?:[^>]*?\s+)?href=(\"[^\"]*\")[^>]*>.*?</a>",
            "邮政编码（国际）": r"\b\d{5}(-\d{4})?\b",  # 美国ZIP代码：例如12345 或 12345-6789
            "UUID": r"\b([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\b",
            "日期时间（YYYY-MM-DD HH:MM:SS）": r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b",
            "MAC地址（短横线分隔）": r"\b([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}\b",
            "文件扩展名（常见格式）": r"\.[a-zA-Z0-9]+",
            "数字（包含千分位）": r"\b\d{1,3}(?:,\d{3})*\b",  # 支持千分位的数字，例如 1,000,000
            "数字（带小数点，支持逗号和点分隔符）": r"\b\d{1,3}(?:[,.]\d{3})*\b",  # 支持千分位和小数点，如 1,000.1234
            "IPv4 子网掩码": r"^(255|254|252|248|240|224|192|128|0)\.(255|254|252|248|240|224|192|128|0)\.(255|254|252|248|240|224|192|128|0)\.(255|254|252|248|240|224|192|128|0)$",
            "字符串包含特定单词（不区分大小写）": r"(?i)\b(?:word1|word2|word3)\b",
            "非ASCII字符": r"[^\x00-\x7F]",  # 匹配所有非ASCII字符
            "汉字或数字（中文和数字）": r"[\u4e00-\u9fa5\d]+",  # 匹配中文或数字
            "十六进制数（不带#）": r"[0-9a-fA-F]{6}\b",
            "链接中的IP地址": r"https?://(\d{1,3}\.){3}\d{1,3}",
            "负浮点数": r"-\d+\.\d+",
            "正浮点数": r"\d+\.\d+",
            "包含字母和数字的字符串": r"^(?=.*[a-zA-Z])(?=.*\d)[A-Za-z\d]+$",
            "HTML5 Canvas尺寸": r"^\d+px$",
            "HTML id属性": r"id=\"[a-zA-Z_][\w\-]*\"",
            "标签内内容（提取HTML标签中的内容）": r"(?<=<[^>]+>)(.*?)(?=</[^>]+>)",
            "邮箱域名（例如gmail.com）": r"@([a-zA-Z0-9-]+\.[a-zA-Z0-9-]+)",
            "两位小数的浮动金额（正数，最多两位小数）": r"\b\d+(\.\d{1,2})?\b",
            "两位小数的负浮动金额（负数，最多两位小数）": r"-\d+(\.\d{1,2})?"
        }

        
        # 创建主体内容
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="🧪 正则表达式测试工具", content_widget=content_widget)
        # 初始化状态
        self.set_status("ℹ️ 请输入测试文本和正则表达式")
        
        self._init_examples()

    def _create_content_widget(self):
        """创建主内容区域"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 主要内容区域 - 使用分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧 - 测试文本输入
        left_group = QGroupBox("📝 测试文本")
        left_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        left_layout = QVBoxLayout(left_group)
        left_layout.setSpacing(10)
        
        self.input_text = QTextEdit()
        self.input_text.setObjectName("input_text")
        self.input_text.setPlaceholderText("请输入要测试的文本内容...")
        self.input_text.setMinimumHeight(200)
        self.input_text.setStyleSheet(TextEditStyles.get_standard_style("input_text"))
        left_layout.addWidget(self.input_text)
        
        splitter.addWidget(left_group)
        
        # 右侧 - 正则表达式设置
        right_group = QGroupBox("🧪 正则表达式")
        right_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        right_layout = QVBoxLayout(right_group)
        right_layout.setSpacing(15)
        
        # 常用正则示例选择
        example_group = QGroupBox("📚 常用示例")
        example_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        example_layout = QVBoxLayout(example_group)
        example_layout.setSpacing(10)
        
        self.regex_combobox = QComboBox()
        self.regex_combobox.setObjectName("regex_selector")
        self.regex_combobox.addItems(list(self.regex_examples.keys()))
        self.regex_combobox.setStyleSheet(ComboBoxStyles.get_enhanced_style("regex_selector"))
        self.regex_combobox.currentTextChanged.connect(self._on_regex_select)
        example_layout.addWidget(self.regex_combobox)
        
        right_layout.addWidget(example_group)
        
        # 正则表达式输入
        regex_input_group = QGroupBox("🔧 正则表达式")
        regex_input_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        regex_input_layout = QVBoxLayout(regex_input_group)
        regex_input_layout.setSpacing(10)
        
        self.regex_text = QTextEdit()
        self.regex_text.setObjectName("regex_text")
        self.regex_text.setPlaceholderText("请输入正则表达式...")
        self.regex_text.setMaximumHeight(100)
        self.regex_text.setStyleSheet(TextEditStyles.get_code_style("regex_text"))
        regex_input_layout.addWidget(self.regex_text)
        
        right_layout.addWidget(regex_input_group)
        
        # 测试按钮
        button_group = QGroupBox("⚡ 操作")
        button_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        button_layout = QHBoxLayout(button_group)
        button_layout.setSpacing(15)
        
        self.test_button = QPushButton("🔍 测试匹配")
        self.test_button.setStyleSheet(ButtonStyles.get_primary_style())
        self.test_button.clicked.connect(self._test_regex)
        button_layout.addWidget(self.test_button)
        
        self.clear_button = QPushButton("🧹 清空")
        self.clear_button.setStyleSheet(ButtonStyles.get_secondary_style())
        self.clear_button.clicked.connect(self._clear_all)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        right_layout.addWidget(button_group)
        
        # 结果显示
        self.result_label = QLabel("📊 准备就绪")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        right_layout.addWidget(self.result_label)
        
        # 匹配详情
        details_group = QGroupBox("📋 匹配详情")
        details_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        details_layout = QVBoxLayout(details_group)
        details_layout.setSpacing(10)
        
        self.details_text = QTextEdit()
        self.details_text.setObjectName("details_text")
        self.details_text.setMaximumHeight(300)
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet(TextEditStyles.get_output_style("details_text"))
        details_layout.addWidget(self.details_text)
        
        right_layout.addWidget(details_group)
        right_layout.setStretchFactor(details_group, 1)

        splitter.addWidget(right_group)
        splitter.setSizes([450, 400])
        
        layout.addWidget(splitter)
        layout.setStretchFactor(splitter, 1)

        return main_widget
    
    def _clear_all(self):
        """清空所有内容"""
        self.input_text.clear()
        self.regex_text.clear()
        self.details_text.clear()
        self.result_label.setText("📊 已清空所有内容")
        self.result_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        self.set_status("ℹ️ 已清空所有内容")
    
    def _init_examples(self):
        """初始化示例"""
        if self.regex_examples:
            first_key = list(self.regex_examples.keys())[0]
            self.regex_text.setPlainText(self.regex_examples[first_key])

    def _on_regex_select(self, text):
        """正则示例选择改变时的处理"""
        if text in self.regex_examples:
            self.regex_text.setPlainText(self.regex_examples[text])
        self._clear_highlights()

    def _clear_highlights(self):
        """清除高亮显示"""
        # 重置文本格式
        cursor = self.input_text.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextCharFormat()
        format.setBackground(QColor("white"))
        format.setForeground(QColor("black"))
        cursor.setCharFormat(format)

    def _test_regex(self):
        """测试正则表达式"""
        self._clear_highlights()

        pattern = self.regex_text.toPlainText().strip()
        text = self.input_text.toPlainText()

        if not pattern:
            QMessageBox.warning(self, "提示", "请输入正则表达式！")
            self._update_status("请输入正则表达式", "warning")
            return
            
        if not text.strip():
            QMessageBox.warning(self, "提示", "请输入测试文本！")
            self._update_status("请输入测试文本", "warning")
            return

        try:
            regex = re.compile(pattern)
        except re.error as e:
            QMessageBox.critical(self, "正则表达式错误", f"正则表达式语法错误:\n{str(e)}")
            self._update_status("正则表达式语法错误", "error")
            self.details_text.clear()
            return

        matches = list(regex.finditer(text))
        if matches:
            # 高亮匹配的文本
            self._highlight_matches(matches)
            
            # 显示结果
            self._update_status(f"匹配成功，共找到 {len(matches)} 个匹配项", "success")
            
            # 显示匹配详情
            details = []
            for i, match in enumerate(matches[:10]):  # 只显示前10个匹配
                details.append(f"匹配 {i+1}: '{match.group()}' (位置: {match.start()}-{match.end()})")
                if match.groups():
                    for j, group in enumerate(match.groups()):
                        details.append(f"  分组 {j+1}: '{group}'")
            
            if len(matches) > 10:
                details.append(f"... 还有 {len(matches) - 10} 个匹配项")
                
            self.details_text.setPlainText('\n'.join(details))
        else:
            self._update_status("未匹配到任何内容", "warning")
            self.details_text.clear()

    def _highlight_matches(self, matches):
        """高亮显示匹配的文本"""
        cursor = self.input_text.textCursor()
        format = QTextCharFormat()
        format.setBackground(QColor("#ffeb3b"))  # 黄色背景
        format.setForeground(QColor("#000000"))  # 黑色文字
        
        for match in matches:
            cursor.setPosition(match.start())
            cursor.setPosition(match.end(), QTextCursor.MoveMode.KeepAnchor)
            cursor.setCharFormat(format)

    def _update_status(self, message, status_type="normal"):
        """更新状态显示"""
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "normal": "ℹ️"
        }
        
        if status_type == "success":
            color = Colors.ONLINE_GREEN
        elif status_type == "error":
            color = "#ef4444"
        elif status_type == "warning":
            color = "#f59e0b"
        else:
            color = Colors.TEXT_PRIMARY
            
        icon = icons.get(status_type, icons["normal"])
        self.result_label.setText(f"📊 {message}")
        self.result_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
        self.set_status(f"{icon} {message}")


