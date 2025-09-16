import json
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTextEdit,
    QSplitter, QFrame, QMessageBox, QPushButton, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QPalette
from styles.constants import Colors
from styles.widgets import TextEditStyles, ButtonStyles, ComboBoxStyles
from components.base_content import BaseContent
import re
from typing import Any

class JSONFormatter(BaseContent):
    """JSON格式化工具界面"""

    def __init__(self):
        # 创建主要内容组件
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="JSON 格式化工具", content_widget=content_widget)
        self._setup_styles()

    def _create_content_widget(self):
        """创建主要内容区域组件"""
        from PySide6.QtWidgets import QWidget, QLabel
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 主内容区域
        splitter = QSplitter(Qt.Horizontal)
        # 左侧输入区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        input_label = QLabel("输入 JSON:")
        input_label.setObjectName("section_label")
        left_layout.addWidget(input_label)

        self.input_text = QTextEdit()
        self.input_text.setObjectName("json_input")
        self.input_text.setPlaceholderText('请输入JSON，例如:\n{\n  "name": "张三",\n  "age": 25\n}')
        self.input_text.setStyleSheet(TextEditStyles.get_standard_style("json_input"))
        self.input_text.setMinimumHeight(400)  # 设置最小高度
        self.input_text.textChanged.connect(self._on_input_changed)
        left_layout.addWidget(self.input_text, 1)  # 添加拉伸因子，让它占用更多空间

        # 右侧输出区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        output_label = QLabel("输出结果:")
        output_label.setObjectName("section_label")
        right_layout.addWidget(output_label)

        self.output_text = QTextEdit()
        self.output_text.setObjectName("json_output")
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("格式化后的结果将在此处显示...")
        self.output_text.setStyleSheet(TextEditStyles.get_output_style("json_output"))
        self.output_text.setMinimumHeight(400)  # 设置最小高度
        right_layout.addWidget(self.output_text, 1)  # 添加拉伸因子，让它占用更多空间

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([1, 1])

        layout.addWidget(splitter, 1)  # 直接给splitter添加拉伸因子，让它占据主要空间
        
        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.format_btn = QPushButton("格式化")
        self.format_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.format_btn.clicked.connect(self._format_json)

        self.minify_btn = QPushButton("压缩")
        self.minify_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.minify_btn.clicked.connect(self._minify_json)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.clear_btn.clicked.connect(self._clear_all)

        self.validate_btn = QPushButton("验证")
        self.validate_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.validate_btn.clicked.connect(self._validate_json)

        self.language_selector = QComboBox()
        self.language_selector.setObjectName("language_selector")
        self.language_selector.addItems(["Java", "NetCore", "Python", "TypeScript", "Go", "Kotlin", "Swift", "Dart", "Rust"])
        self.language_selector.setStyleSheet(ComboBoxStyles.get_enhanced_style("language_selector"))

        self.entity_btn = QPushButton("转换成实体")
        self.entity_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.entity_btn.clicked.connect(self._convert_to_entity)



        button_layout.addWidget(self.format_btn)
        button_layout.addWidget(self.minify_btn)
        button_layout.addWidget(self.validate_btn)
        button_layout.addWidget(self.language_selector)
        button_layout.addWidget(self.entity_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

        # 延迟验证
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._auto_validate)
        
        return content_widget

    def _setup_styles(self):
        """设置样式 - 只定义组件特有的样式，通用样式已直接应用到控件"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BACKGROUND_CHAT};
                color: {Colors.TEXT_PRIMARY};
            }}

            QSplitter::handle {{
                background-color: {Colors.BORDER_LIGHT};
                width: 2px;
            }}

            QSplitter::handle:hover {{
                background-color: {Colors.WECHAT_GREEN};
            }}
        """)

    def _on_input_changed(self):
        self.validation_timer.stop()
        self.validation_timer.start(1000)

    def _auto_validate(self):
        text = self.input_text.toPlainText().strip()
        # 输入改变时清除高亮
        self._clear_highlights()
        
        if text:
            try:
                json.loads(text)
                self._update_status("✅ JSON格式正确", "success")
            except json.JSONDecodeError as e:
                self._update_status(f"❌ JSON格式错误: {str(e)}", "error")
        else:
            self._update_status("准备就绪", "normal")
    
    def _convert_to_entity(self):
        input_text = self.input_text.toPlainText().strip()

        if not input_text:
            self._show_message("请先输入JSON数据", "warning")
            return

        # 清除之前的高亮
        self._clear_highlights()

        try:
            parsed_json = json.loads(input_text)
        except json.JSONDecodeError as e:
            # 高亮显示错误位置
            self._highlight_json_error(e, input_text)
            self._show_message(f"JSON格式错误：{str(e)}", "error")
            self._update_status(f"❌ 转换失败: {str(e)}", "error")
            return

        language = self.language_selector.currentText()

        if language == "Java":
            entity_code = self._generate_java_entity(parsed_json)
        elif language == "NetCore":
            entity_code = self._generate_csharp_entity(parsed_json)
        elif language == "Python":
            entity_code = self._generate_python_class(parsed_json)
        elif language == "TypeScript":
            entity_code = self._generate_typescript_interface(parsed_json)
        elif language == "Go":
            entity_code = self._generate_go_struct(parsed_json)
        elif language == "Kotlin":
            entity_code = self._generate_kotlin_data_class(parsed_json)
        elif language == "Swift":
            entity_code = self._generate_swift_struct(parsed_json)
        elif language == "Dart":
            entity_code = self._generate_dart_class(parsed_json)
        elif language == "Rust":
            entity_code = self._generate_rust_struct(parsed_json)
        else:
            entity_code = "// 不支持的语言"

        self.output_text.setPlainText(entity_code)
        self._update_status(f"✅ 成功转换为 {language} 实体", "success")

    
    def _generate_java_entity(self, json_obj, class_name="MyEntity"):
        lines = []
        nested_classes = []

        def parse_dict(obj, cls_name):
            fields = []
            for key, value in obj.items():
                safe_key = self._safe_field_name(key)
                type_str, nested = self._infer_java_type(value, safe_key)
                fields.append(f"    private {type_str} {safe_key};")
                if nested:
                    nested_classes.append(nested)
            class_def = [f"public class {cls_name} " + "{"] + fields + ["}"]
            return "\n".join(class_def)

        entity_code = parse_dict(json_obj, class_name)
        all_classes = nested_classes + [entity_code]
        return "\n\n".join(reversed(all_classes))

    def _safe_field_name(self, name):
        # 将非法字符转为下划线
        return re.sub(r'\W|^(?=\d)', '_', name)

    def _to_pascal_case(self, s):
        parts = re.split(r'[_\-\s]+', s)
        return ''.join(word.capitalize() for word in parts)

    def _to_camel_case(self, s):
        parts = re.split(r'[_\-\s]+', s)
        return parts[0].capitalize() + ''.join(word.capitalize() for word in parts[1:])

    def _safe_field_name_pascal(self, name):
        parts = re.split(r'[\W_]+', name)
        return ''.join(p.capitalize() for p in parts if p)

    def _class_name_from_key(self, key):
        return ''.join(x.capitalize() for x in re.split(r'[\W_]+', key))


    def _generate_csharp_entity(self, json_obj, class_name="MyEntity"):
        lines = []
        nested_classes = []

        def parse_dict(obj, cls_name):
            fields = []
            for key, value in obj.items():
                safe_key = self._safe_field_name_pascal(key)
                type_str, nested = self._infer_csharp_type(value, safe_key)
                fields.append(f"    public {type_str} {safe_key} {{ get; set; }}")
                if nested:
                    nested_classes.append(nested)
            class_def = [f"public class {cls_name} " + "{"] + fields + ["}"]
            return "\n".join(class_def)

        entity_code = parse_dict(json_obj, class_name)
        all_classes = nested_classes + [entity_code]
        return "\n\n".join(reversed(all_classes))

    def _generate_python_class(self, json_obj, class_name="MyEntity"):
        lines = [f"class {class_name}:"]
        if not json_obj:
            lines.append("    pass")
            return "\n".join(lines)
        for key, value in json_obj.items():
            py_type = self._get_python_type(value)
            safe_key = self._safe_field_name(key)
            lines.append(f"    {safe_key}: {py_type}")
        return "\n".join(lines)

    def _get_python_type(self, value):
        if isinstance(value, str):
            return "str"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        else:
            return "Any"

    def _generate_dart_class(self, json_obj, class_name="MyEntity"):
        lines = [f"class {class_name} " + "{"]
        for key, value in json_obj.items():
            dart_type = self._get_dart_type(value)
            safe_key = self._safe_field_name(key)
            lines.append(f"  final {dart_type} {safe_key};")
        lines.append("")
        lines.append(f"  {class_name}({{")
        for key in json_obj.keys():
            safe_key = self._safe_field_name(key)
            lines.append(f"    required this.{safe_key},")
        lines.append("  });")
        lines.append("}")
        return "\n".join(lines)

    def _get_dart_type(self, value):
        if isinstance(value, str):
            return "String"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "double"
        elif isinstance(value, list):
            return "List<dynamic>"
        elif isinstance(value, dict):
            return "Map<String, dynamic>"
        else:
            return "dynamic"


    def _generate_rust_struct(self, json_obj, struct_name="MyEntity"):
        lines = [f"#[derive(Debug, Serialize, Deserialize)]", f"pub struct {struct_name} " + "{"]
        for key, value in json_obj.items():
            rust_type = self._get_rust_type(value)
            safe_key = self._safe_field_name(key)
            lines.append(f"    pub {safe_key}: {rust_type},")
        lines.append("}")
        return "\n".join(lines)

    def _get_rust_type(self, value):
        if isinstance(value, str):
            return "String"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "i64"
        elif isinstance(value, float):
            return "f64"
        elif isinstance(value, list):
            return "Vec<Value>"  # Value 需引入 serde_json::Value
        elif isinstance(value, dict):
            return "HashMap<String, Value>"
        else:
            return "Value"


    def _infer_java_type(self, value, field_name):
        if isinstance(value, str):
            return "String", None
        elif isinstance(value, bool):
            return "boolean", None
        elif isinstance(value, int):
            return "int", None
        elif isinstance(value, float):
            return "double", None
        elif isinstance(value, list):
            if not value:
                return "List<Object>", None
            element_type, nested = self._infer_java_type(value[0], field_name)
            return f"List<{element_type}>", nested
        elif isinstance(value, dict):
            class_name = self._class_name_from_key(field_name)
            nested_class = self._generate_java_entity(value, class_name)
            return class_name, nested_class
        else:
            return "Object", None

    def _infer_csharp_type(self, value, field_name):
        if isinstance(value, str):
            return "string", None
        elif isinstance(value, bool):
            return "bool", None
        elif isinstance(value, int):
            return "int", None
        elif isinstance(value, float):
            return "double", None
        elif isinstance(value, list):
            if not value:
                return "List<object>", None
            element_type, nested = self._infer_csharp_type(value[0], field_name)
            return f"List<{element_type}>", nested
        elif isinstance(value, dict):
            class_name = self._class_name_from_key(field_name)
            nested_class = self._generate_csharp_entity(value, class_name)
            return class_name, nested_class
        else:
            return "object", None

    def _generate_typescript_interface(self, json_obj, interface_name="MyEntity"):
        lines = [f"interface {interface_name} " + "{"]
        for key, value in json_obj.items():
            ts_type = self._get_typescript_type(value)
            safe_key = self._safe_field_name(key)
            lines.append(f"  {safe_key}: {ts_type};")
        lines.append("}")
        return "\n".join(lines)

    def _get_typescript_type(self, value):
        if isinstance(value, str):
            return "string"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int) or isinstance(value, float):
            return "number"
        elif isinstance(value, list):
            return "any[]"
        elif isinstance(value, dict):
            return "object"
        else:
            return "any"

    def _generate_go_struct(self, json_obj, struct_name="MyEntity"):
        lines = [f"type {struct_name} struct " + "{"]
        for key, value in json_obj.items():
            go_type = self._get_go_type(value)
            camel_key = self._to_camel_case(key)
            lines.append(f"    {camel_key} {go_type} `json:\"{key}\"`")
        lines.append("}")
        return "\n".join(lines)

    def _get_go_type(self, value):
        if isinstance(value, str):
            return "string"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float64"
        elif isinstance(value, list):
            return "[]interface{}"
        elif isinstance(value, dict):
            return "map[string]interface{}"
        else:
            return "interface{}"

    def _generate_kotlin_data_class(self, json_obj, class_name="MyEntity"):
        lines = [f"data class {class_name}("]
        props = []
        for key, value in json_obj.items():
            kotlin_type = self._get_kotlin_type(value)
            safe_key = self._safe_field_name(key)
            props.append(f"    val {safe_key}: {kotlin_type}")
        lines.append(",\n".join(props))
        lines.append(")")
        return "\n".join(lines)

    def _get_kotlin_type(self, value):
        if isinstance(value, str):
            return "String"
        elif isinstance(value, bool):
            return "Boolean"
        elif isinstance(value, int):
            return "Int"
        elif isinstance(value, float):
            return "Double"
        elif isinstance(value, list):
            return "List<Any>"
        elif isinstance(value, dict):
            return "Map<String, Any>"
        else:
            return "Any"

    def _generate_swift_struct(self, json_obj, struct_name="MyEntity"):
        lines = [f"struct {struct_name} " + "{"]
        for key, value in json_obj.items():
            swift_type = self._get_swift_type(value)
            safe_key = self._safe_field_name(key)
            lines.append(f"    var {safe_key}: {swift_type}")
        lines.append("}")
        return "\n".join(lines)

    def _get_swift_type(self, value):
        if isinstance(value, str):
            return "String"
        elif isinstance(value, bool):
            return "Bool"
        elif isinstance(value, int):
            return "Int"
        elif isinstance(value, float):
            return "Double"
        elif isinstance(value, list):
            return "[Any]"
        elif isinstance(value, dict):
            return "[String: Any]"
        else:
            return "Any"


    def _get_csharp_type(self, value):
        if isinstance(value, str):
            return "string"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "double"
        elif isinstance(value, list):
            return "List<object>"
        elif isinstance(value, dict):
            return "object"
        else:
            return "object"


    def _format_json(self):
        input_text = self.input_text.toPlainText().strip()

        if not input_text:
            self._show_message("请先输入JSON数据", "warning")
            return

        # 清除之前的高亮
        self._clear_highlights()

        try:
            parsed_json = json.loads(input_text)
            formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False, sort_keys=True)
            self.output_text.setPlainText(formatted_json)
            self._update_status("✅ JSON格式化成功", "success")

        except json.JSONDecodeError as e:
            # 高亮显示错误位置
            self._highlight_json_error(e, input_text)
            self._show_message(f"JSON格式错误：{str(e)}", "error")
            self._update_status(f"❌ 格式化失败: {str(e)}", "error")

    def _minify_json(self):
        input_text = self.input_text.toPlainText().strip()

        if not input_text:
            self._show_message("请先输入JSON数据", "warning")
            return

        # 清除之前的高亮
        self._clear_highlights()

        try:
            parsed_json = json.loads(input_text)
            minified_json = json.dumps(parsed_json, separators=(',', ':'), ensure_ascii=False)
            self.output_text.setPlainText(minified_json)
            self._update_status("✅ JSON压缩成功", "success")

        except json.JSONDecodeError as e:
            # 高亮显示错误位置
            self._highlight_json_error(e, input_text)
            self._show_message(f"JSON格式错误：{str(e)}", "error")
            self._update_status(f"❌ 压缩失败: {str(e)}", "error")

    def _validate_json(self):
        input_text = self.input_text.toPlainText().strip()

        if not input_text:
            self._show_message("请先输入JSON数据", "warning")
            return

        # 清除之前的高亮
        self._clear_highlights()

        try:
            parsed_json = json.loads(input_text)
            json_info = self._analyze_json(parsed_json)
            self.output_text.setPlainText(json_info)
            self._update_status("✅ JSON验证通过", "success")

        except json.JSONDecodeError as e:
            print(f"JSON验证失败: {str(e)}")  # 调试信息
            
            # 先添加一个强制高亮测试
            self._force_highlight_test()
            
            # 然后进行正常的错误高亮
            self._highlight_json_error(e, input_text)
            
            error_info = f"JSON格式错误：\n\n{str(e)}\n\n请检查以下常见问题：\n• 是否缺少引号\n• 是否有多余的逗号\n• 括号是否匹配\n• 字符串是否正确转义"
            self.output_text.setPlainText(error_info)
            self._update_status(f"❌ JSON验证失败: {str(e)}", "error")

    def _force_highlight_test(self):
        """强制高亮测试 - 确保高亮功能工作"""
        text = self.input_text.toPlainText()
        if not text:
            return
            
        cursor = self.input_text.textCursor()
        
        # 强制高亮前10个字符
        cursor.setPosition(0)
        cursor.setPosition(min(10, len(text)), QTextCursor.KeepAnchor)
        
        # 使用非常明显的格式
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("red"))
        # highlight_format.setForeground(QColor("white"))
        highlight_format.setFontWeight(900)  # 超粗
        highlight_format.setFontPointSize(16)  # 大字体
        
        cursor.setCharFormat(highlight_format)
        cursor.clearSelection()
        
        # 强制刷新
        self.input_text.update()
        self.input_text.repaint()
        
        print("强制高亮测试已执行")  # 调试信息

    def _clear_highlights(self):
        """清除输入框中的所有高亮"""
        cursor = self.input_text.textCursor()
        cursor.select(QTextCursor.Document)
        
        # 创建默认格式
        default_format = QTextCharFormat()
        # default_format.setBackground(QColor("white"))  # 明确设置背景色
        default_format.setForeground(QColor("#2d3748"))  # 默认文字颜色
        default_format.setFontWeight(400)  # 正常字重
        
        cursor.setCharFormat(default_format)
        cursor.clearSelection()
        
        # 刷新显示
        self.input_text.update()

    def _highlight_json_error(self, error, text):
        """高亮显示JSON错误位置"""
        try:
            # 从错误信息中提取位置信息
            error_msg = str(error)
            print(f"JSON错误信息: {error_msg}")  # 调试信息
            
            highlighted = False
            
            # 尝试从错误信息中提取行号和列号
            line_col_match = re.search(r'line (\d+) column (\d+)', error_msg)
            if line_col_match:
                line_num = int(line_col_match.group(1))
                col_num = int(line_col_match.group(2))
                print(f"找到错误位置: 行{line_num}, 列{col_num}")  # 调试信息
                
                # 转换为字符位置
                lines = text.split('\n')
                char_pos = 0
                for i in range(line_num - 1):
                    if i < len(lines):
                        char_pos += len(lines[i]) + 1  # +1 for newline
                char_pos += col_num - 1
                
                print(f"字符位置: {char_pos}")  # 调试信息
                # 高亮错误位置及周围几个字符
                self._highlight_position(char_pos, max(1, min(5, len(text) - char_pos)), 
                                       QColor("#ff4444"), QColor("#ffe6e6"))
                highlighted = True
                
            # 尝试从错误信息中提取字符位置
            elif 'char' in error_msg.lower():
                char_match = re.search(r'char (\d+)', error_msg)
                if char_match:
                    char_pos = int(char_match.group(1))
                    print(f"找到字符位置: {char_pos}")  # 调试信息
                    self._highlight_position(char_pos, max(1, min(5, len(text) - char_pos)), 
                                           QColor("#ff4444"), QColor("#ffe6e6"))
                    highlighted = True
            
            # 如果无法确定具体位置，尝试高亮常见错误模式
            if not highlighted:
                print("使用通用错误模式高亮")  # 调试信息
                self._highlight_common_errors(text, error_msg)
                
        except Exception as e:
            print(f"高亮错误时出现异常: {e}")
            # 至少高亮第一个字符作为fallback
            if text:
                self._highlight_position(0, 1, QColor("#ff4444"), QColor("#ffe6e6"))

    def _highlight_position(self, start_pos, length, text_color, bg_color):
        """在指定位置高亮文本"""
        if start_pos < 0 or start_pos >= len(self.input_text.toPlainText()):
            return
            
        cursor = self.input_text.textCursor()
        
        # 确保位置和长度有效
        text_length = len(self.input_text.toPlainText())
        if start_pos + length > text_length:
            length = text_length - start_pos
            
        cursor.setPosition(start_pos)
        cursor.setPosition(start_pos + length, QTextCursor.KeepAnchor)
        
        # 设置高亮格式 - 使用更明显的颜色
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 200, 200))  # 明显的红色背景
        highlight_format.setForeground(QColor(180, 0, 0))     # 深红色文字
        highlight_format.setFontWeight(700)  # 加粗
        highlight_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)  # 波浪下划线
        highlight_format.setUnderlineColor(QColor(255, 0, 0))  # 红色下划线
        
        cursor.setCharFormat(highlight_format)
        
        # 将光标移动到错误位置并显示
        cursor.setPosition(start_pos)
        self.input_text.setTextCursor(cursor)
        self.input_text.ensureCursorVisible()  # 确保错误位置可见
        
        # 强制刷新显示
        self.input_text.update()

    def _highlight_common_errors(self, text, error_msg):
        """高亮常见的JSON错误模式"""
        cursor = self.input_text.textCursor()
        found_error = False
        
        # 错误格式设置 - 使用更明显的颜色
        error_format = QTextCharFormat()
        error_format.setBackground(QColor(255, 200, 200))  # 明显的红色背景
        error_format.setForeground(QColor(180, 0, 0))      # 深红色文字
        error_format.setFontWeight(700)
        error_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        error_format.setUnderlineColor(QColor(255, 0, 0))
        
        warning_format = QTextCharFormat()
        warning_format.setBackground(QColor(255, 255, 200))  # 明显的黄色背景
        warning_format.setForeground(QColor(180, 120, 0))    # 橙色文字
        warning_format.setFontWeight(700)
        
        # 检查常见错误模式
        error_patterns = [
            (r'[,\]\}]\s*[,\]\}]', "多余的逗号"),      # 多余逗号
            (r'[{\[]\s*,', "开头的逗号"),              # 开头逗号
            (r'(?<!")(\w+)(?=\s*:)', "未加引号的键"),   # 未加引号的键
            (r"'([^']*)'(?=\s*:)", "单引号键名"),       # 单引号键名
            (r':\s*([^",\[\{\s\d\-][^,\]\}]*?)(?=[,\]\}])', "未加引号的字符串值"),  # 未加引号的值
            (r'[{\[,]\s*[}\]]', "空结构错误"),          # 空对象/数组后直接逗号
            (r'(?<!\\)"[^"]*\n[^"]*"', "跨行字符串"),   # 跨行字符串
        ]
        
        print(f"开始检查错误模式...")  # 调试信息
        
        for pattern, error_type in error_patterns:
            matches = list(re.finditer(pattern, text))
            print(f"模式 '{error_type}' 找到 {len(matches)} 个匹配")  # 调试信息
            
            for match in matches:
                start_pos = match.start()
                end_pos = match.end()
                print(f"高亮位置: {start_pos}-{end_pos}, 内容: '{text[start_pos:end_pos]}'")  # 调试信息
                
                cursor.setPosition(start_pos)
                cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
                cursor.setCharFormat(error_format if "逗号" in error_type else warning_format)
                found_error = True
        
        if found_error:
            # 刷新显示
            self.input_text.update()
            # 移动光标到第一个错误位置
            cursor.setPosition(0)
            self.input_text.setTextCursor(cursor)
        else:
            print("未找到匹配的错误模式，高亮整个文本开头")  # 调试信息
            # 如果找不到具体错误，高亮前几个字符
            if text:
                cursor.setPosition(0)
                cursor.setPosition(min(10, len(text)), QTextCursor.KeepAnchor)
                cursor.setCharFormat(error_format)

    def _analyze_json(self, json_obj):
        info_lines = ["JSON验证通过 ✅\n"]

        def count_elements(obj, path="root"):
            if isinstance(obj, dict):
                info_lines.append(f"📁 {path}: 对象 ({len(obj)} 个属性)")
                for key, value in obj.items():
                    count_elements(value, f"{path}.{key}")
            elif isinstance(obj, list):
                info_lines.append(f"📋 {path}: 数组 ({len(obj)} 个元素)")
                for i, item in enumerate(obj):
                    count_elements(item, f"{path}[{i}]")
            elif isinstance(obj, str):
                info_lines.append(f"📝 {path}: 字符串 (长度: {len(obj)})")
            elif isinstance(obj, (int, float)):
                info_lines.append(f"🔢 {path}: 数字 ({obj})")
            elif isinstance(obj, bool):
                info_lines.append(f"✅ {path}: 布尔值 ({obj})")
            elif obj is None:
                info_lines.append(f"❌ {path}: null")

        count_elements(json_obj)

        json_str = json.dumps(json_obj, ensure_ascii=False)
        info_lines.extend([
            "\n" + "=" * 50,
            "📊 统计信息:",
            f"• 字符总数: {len(json_str)}",
            f"• 压缩后大小: {len(json.dumps(json_obj, separators=(',', ':'), ensure_ascii=False))} 字符",
            f"• 数据类型: {type(json_obj).__name__}"
        ])

        return "\n".join(info_lines)

    def _clear_all(self):
        self.input_text.clear()
        self.output_text.clear()
        self._update_status("已清空所有内容", "normal")

    def _update_status(self, message, status_type="normal"):
        # 使用基类的状态更新方法
        self.set_status(message)
        
        # 根据状态类型设置不同的颜色样式
        if status_type == "success":
            color = "#10b981"
        elif status_type == "error":
            color = "#ef4444"
        elif status_type == "warning":
            color = "#f59e0b"
        else:
            color = Colors.TEXT_SECONDARY

        # 更新状态标签的样式以反映不同的状态
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f5f5f5;
            }}
        """)

    def _show_message(self, message, msg_type="info"):
        msg_box = QMessageBox()

        if msg_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("错误")
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("警告")
        else:
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("提示")

        msg_box.setText(message)
        msg_box.exec()
    
    def refresh_styles(self):
        """刷新样式 - 支持主题切换"""
        self._setup_styles()
