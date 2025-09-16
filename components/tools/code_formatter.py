"""
代码格式化工具组件
"""

try:
    import jsbeautifier
    HAS_JSBEAUTIFIER = True
except ImportError:
    HAS_JSBEAUTIFIER = False

try:
    import cssbeautifier
    HAS_CSSBEAUTIFIER = True
except ImportError:
    HAS_CSSBEAUTIFIER = False

try:
    import html.parser
    import html
    from bs4 import BeautifulSoup
    HAS_HTML_BEAUTIFIER = True
except ImportError:
    HAS_HTML_BEAUTIFIER = False

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFileDialog, QComboBox, QSplitter, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from styles.constants import Colors
from styles.widgets import (
    ComboBoxStyles, ButtonStyles, TextEditStyles
)
from components.base_content import BaseContent
import os
import shutil
import tempfile
import subprocess
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTextEdit

EXTENSION_LANG_MAP = {
    '.html': 'HTML',
    '.htm': 'HTML',
    '.js': 'JavaScript',
    '.css': 'CSS',
    '.py': 'Python',
    '.java': 'Java',
    '.go': 'Go',
    '.rs': 'Rust',
    '.dart': 'Dart',
    '.ts': 'TypeScript',
    '.cs': 'NetCore',
    '.kt': 'Kotlin',
    '.swift': 'Swift',
}

class DraggableTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # 只接受文件拖入
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.setPlainText(content)

                    # 通过父组件调用自动语言识别
                    if hasattr(self.parent(), "_set_language_by_extension"):
                        self.parent()._set_language_by_extension(file_path)

                    if hasattr(self.parent(), "set_status"):
                        self.parent().set_status(f"✅ 已通过拖放加载文件：{os.path.basename(file_path)}")
                except Exception as e:
                    if hasattr(self.parent(), "set_status"):
                        self.parent().set_status(f"❌ 拖放文件读取失败: {str(e)}")
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

class CodeFormatterTool(BaseContent):
    """单页面：代码格式化工具"""

    def __init__(self):
        # 创建主要内容组件
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="代码格式化", content_widget=content_widget)
        self._apply_styles()

    def _create_content_widget(self):
        """创建主要内容区域组件"""
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 第二行：语言选择 + 安装依赖 + 格式化按钮
        tool_layout = QHBoxLayout()

        lang_label = QLabel("语言类型：")
        lang_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        tool_layout.addWidget(lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "HTML", "JavaScript", "CSS",
            "Python", "Java", "Go", "Rust", "Dart",
            "TypeScript", "NetCore", "Kotlin", "Swift"
        ])
        ComboBoxStyles.apply_enhanced_style(self.lang_combo, "language_selector")
        tool_layout.addWidget(self.lang_combo)

        tool_layout.addStretch()


 # 顶部：文件按钮 + 描述
        header_layout = QHBoxLayout()
        self.file_btn = QPushButton("📂 打开文件")
        self.file_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.file_btn.clicked.connect(self._open_file)
        header_layout.addWidget(self.file_btn)

        header_layout.addStretch()
        tool_layout.addLayout(header_layout)



        self.format_btn = QPushButton("🎯 美化格式")
        self.format_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.format_btn.clicked.connect(self._format_code)
        tool_layout.addWidget(self.format_btn)
        layout.addLayout(tool_layout)

        # 中间区域：输入输出左右平铺
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)

        # 左侧输入框
        self.code_input = DraggableTextEdit()
        self.code_input.setPlaceholderText("请粘贴原始代码或拖放文件到这里...")
        self.code_input.setObjectName("code_input")
        self.code_input.setStyleSheet(TextEditStyles.get_standard_style("code_input"))


        # 右侧输出框
        self.code_output = QTextEdit()
        self.code_output.setReadOnly(True)
        self.code_output.setPlaceholderText("格式化后的代码将在此显示")
        self.code_output.setObjectName("code_output")
        self.code_output.setStyleSheet(TextEditStyles.get_output_style("code_output"))

        splitter.addWidget(self._wrap_with_label("原始代码", self.code_input))
        splitter.addWidget(self._wrap_with_label("格式化结果", self.code_output))
        splitter.setSizes([1, 1])  # 初始平分宽度

        layout.addWidget(splitter, 1)

        return content_widget


    def _apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BACKGROUND_CHAT};
                color: {Colors.TEXT_PRIMARY};
            }}
           
            QComboBox {{
                padding: 4px 8px;
                font-size: 13px;
            }}
            QPushButton {{
                padding: 8px 16px;
                font-size: 13px;
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #06a050;
            }}
            QPushButton:pressed {{
                background-color: #059940;
            }}
            QTextEdit {{
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 5px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                background-color: #fefefe;
                padding: 8px;
            }}
            QTextEdit:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QLabel#status_label {{
                font-size: 12px;
                color: {Colors.TEXT_SECONDARY};
            }}
        """)

    def _wrap_with_label(self, title: str, widget: QTextEdit) -> QWidget:
        """将 QTextEdit 与标题包装为一个垂直面板"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        label = QLabel(title)
        label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
        layout.addWidget(label)
        layout.addWidget(widget)

        return container


    def _set_language_by_extension(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        lang = EXTENSION_LANG_MAP.get(ext)
        if lang:
            index = self.lang_combo.findText(lang)
            if index != -1:
                self.lang_combo.setCurrentIndex(index)


    def _open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择要格式化的代码文件",
            os.path.expanduser("~"),
            "代码文件 (*.py *.js *.html *.css *.java *.go *.rs *.dart *.ts *.swift *.kt);;所有文件 (*)"
        )

        if not file_path:
            return  # 用户取消选择

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.code_input.setPlainText(content)
                self._set_language_by_extension(file_path)  # 自动识别语言
                self.set_status(f"✅ 已加载文件：{os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "读取文件失败", f"无法读取文件内容：{str(e)}")
            self.set_status("❌ 文件读取失败")



    def _format_code(self):
        code = self.code_input.toPlainText()
        if not code.strip():
            self.set_status("请输入代码后再执行格式化")
            return

        lang = self.lang_combo.currentText().lower()
        result = ""

        try:
            if lang == "javascript":
                if not HAS_JSBEAUTIFIER:
                    QMessageBox.warning(self, "缺少依赖", "请先安装 jsbeautifier：pip install jsbeautifier")
                    return
                opts = jsbeautifier.default_options()
                result = jsbeautifier.beautify(code, opts)
                
            elif lang == "css":
                if not HAS_CSSBEAUTIFIER:
                    QMessageBox.warning(self, "缺少依赖", "请先安装 cssbeautifier：pip install cssbeautifier")
                    return
                opts = cssbeautifier.default_options()
                result = cssbeautifier.beautify(code, opts)
                
            elif lang == "html":
                if not HAS_HTML_BEAUTIFIER:
                    QMessageBox.warning(self, "缺少依赖", "请先安装 beautifulsoup4：pip install beautifulsoup4")
                    return
                try:
                    # 使用 BeautifulSoup 格式化 HTML
                    soup = BeautifulSoup(code, 'html.parser')
                    result = soup.prettify()
                except Exception as e:
                    raise RuntimeError(f"HTML 格式化失败: {str(e)}")

            elif lang == "python":
                result = self._format_with_black(code)

            elif lang == "java":
                result = self._format_with_google_java_format(code)

            elif lang == "go":
                result = self._format_with_cli_tool(code, "gofmt", args=["-s"])

            elif lang == "rust":
                result = self._format_with_cli_tool(code, "rustfmt")

            elif lang == "dart":
                result = self._format_with_cli_tool(code, "dart", args=["format", "--output", "show"])
            
            elif lang == "typescript":
                result = self._format_with_cli_tool(code, "prettier", args=["--parser", "typescript"])

            elif lang == "netcore":
                result = self._format_with_dotnet_format(code)

            elif lang == "kotlin":
                result = self._format_with_cli_tool(code, "ktlint", args=["--format", "--stdin"])

            elif lang == "swift":
                result = self._format_with_cli_tool(code, "swift-format", args=["format", "-"])



            else:
                QMessageBox.information(self, "暂不支持", f"暂未实现对 {lang.upper()} 的格式化")
                return

            self.code_output.setPlainText(result)
            self.set_status("✅ 格式化成功")
        except Exception as e:
            self.set_status(f"❌ 格式化失败: {str(e)}")
            QMessageBox.critical(self, "格式化错误", str(e))

    def _format_with_dotnet_format(self, code: str) -> str:
        if shutil.which("dotnet-format") is None:
            raise RuntimeError("未找到 dotnet-format，请先通过 dotnet 工具安装：dotnet tool install -g dotnet-format")

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "Test.cs")
            proj_path = os.path.join(temp_dir, "Test.csproj")

            # 创建 .cs 文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)

            # 创建一个最小的 C# 项目文件
            with open(proj_path, "w", encoding="utf-8") as f:
                f.write("""
    <Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <OutputType>Exe</OutputType>
        <TargetFramework>net6.0</TargetFramework>
    </PropertyGroup>
    </Project>
    """)

            # 调用 dotnet format - 使用 CREATE_NO_WINDOW 避免控制台窗口
            import os
            CREATE_NO_WINDOW = 0x08000000
            result = subprocess.run(
                ["dotnet-format", proj_path, "--include", file_path, "--verify-no-changes", "--folder"],
                capture_output=True, text=True,
                creationflags=CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            if result.returncode not in (0, 2):  # 0 = 成功，2 = 有格式化更改
                raise RuntimeError(result.stderr.strip())

            # 读取格式化后的文件
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

                
    def _format_with_black(self, code: str) -> str:
        try:
            import black
            return black.format_str(code, mode=black.FileMode())
        except ImportError:
            raise RuntimeError("请先安装 black：pip install black")

    def _format_with_google_java_format(self, code: str) -> str:
        java_formatter_path = shutil.which("google-java-format")
        if not java_formatter_path:
            raise RuntimeError("请安装 google-java-format 并添加到系统路径")

        return self._format_with_cli_tool(code, java_formatter_path)

    def _format_with_cli_tool(self, code: str, command: str, args: list = None) -> str:
        if shutil.which(command) is None:
            raise RuntimeError(f"未找到命令 {command}，请先安装并加入系统路径")

        args = args or []

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".tmp") as f:
            f.write(code)
            temp_path = f.name

        try:
            # 使用 CREATE_NO_WINDOW 避免控制台窗口
            import os
            CREATE_NO_WINDOW = 0x08000000
            full_cmd = [command] + args + [temp_path]
            result = subprocess.run(full_cmd, capture_output=True, text=True,
                                  creationflags=CREATE_NO_WINDOW if os.name == 'nt' else 0)

            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip())

            # 读取回格式化结果
            if os.path.exists(temp_path):
                with open(temp_path, "r", encoding="utf-8") as f:
                    formatted = f.read()
                return formatted
            else:
                return result.stdout.strip()
        finally:
            os.unlink(temp_path)
            
    def _install_dependencies(self):
        """安装代码格式化所需的依赖"""
        try:
            import subprocess
            import sys
            
            self.set_status("正在安装必要依赖...")
            
            # 创建包含依赖列表的命令
            cmd = [
                sys.executable, "-m", "pip", "install",
                "jsbeautifier", "cssbeautifier", "beautifulsoup4", "black", "--upgrade"
            ]
            
            # 显示一个提示对话框
            reply = QMessageBox.question(
                self,
                "安装依赖",
                "这将安装以下包:\n- jsbeautifier (JavaScript格式化)\n- cssbeautifier (CSS格式化)\n"
                "- beautifulsoup4 (HTML格式化)\n- black (Python格式化)\n\n是否继续?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 在后台运行安装命令 - 确保无控制台窗口
                import os
                CREATE_NO_WINDOW = 0x08000000
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    stdin=subprocess.DEVNULL,
                    creationflags=CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    QMessageBox.information(self, "安装成功", "所有依赖已成功安装！")
                    self.set_status("✅ 依赖已安装，请重启程序以应用更改")
                    
                    # 刷新模块导入状态
                    global HAS_JSBEAUTIFIER, HAS_CSSBEAUTIFIER, HAS_HTML_BEAUTIFIER
                    try:
                        import jsbeautifier
                        HAS_JSBEAUTIFIER = True
                    except ImportError:
                        HAS_JSBEAUTIFIER = False
                    
                    try:
                        import cssbeautifier
                        HAS_CSSBEAUTIFIER = True
                    except ImportError:
                        HAS_CSSBEAUTIFIER = False
                    
                    try:
                        from bs4 import BeautifulSoup
                        HAS_HTML_BEAUTIFIER = True
                    except ImportError:
                        HAS_HTML_BEAUTIFIER = False
                        
                else:
                    error_msg = f"安装失败：{stderr}"
                    QMessageBox.critical(self, "安装失败", error_msg)
                    self.set_status("❌ 依赖安装失败")
                    
        except Exception as e:
            QMessageBox.critical(self, "安装错误", f"安装依赖时出错：{str(e)}")
            self.set_status(f"❌ 安装依赖时出错: {str(e)}")
