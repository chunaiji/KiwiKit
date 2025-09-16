from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QPushButton, QSizePolicy
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt, QSize

from components.base_content import BaseContent
from styles.constants import Colors
from styles.widgets import GroupBoxStyles


class UsageDashboard(BaseContent):
    """常用项展示界面"""

    def __init__(self):
        # 主体内容
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="🧭 常用工具面板", content_widget=content_widget)

    def _create_content_widget(self):
        """创建主内容区域"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # 欢迎信息区域
        welcome_widget = self._create_welcome_section()
        main_layout.addWidget(welcome_widget)

        # 分组：文件处理工具
        file_group = self._create_group_box("📂 文件处理工具", [
            {"icon": "🔍", "title": "文件查找", "desc": "快速搜索本地文件，支持正则表达式和全文搜索"},
            {"icon": "📈", "title": "屏幕截屏", "desc": "截取当前屏幕内容"},
            {"icon": "🖼️", "title": "图片转换", "desc": "图片格式转换、压缩和简单编辑"},
            {"icon": "📦", "title": "媒体下载", "desc": "从网页提取并下载媒体文件"},
        ])
        main_layout.addWidget(file_group)

        # 分组：编程开发工具
        dev_group = self._create_group_box("🛠️ 编程开发工具", [
            {"icon": "📝", "title": "JSON格式化", "desc": "格式化、美化和验证JSON数据"},
            {"icon": "🔤", "title": "编码转换", "desc": "Base64、URL、进制转换等编码工具"},
            {"icon": "🎨", "title": "代码格式化", "desc": "代码美化和格式化工具"},
            {"icon": "🧮", "title": "正则工具", "desc": "正则表达式测试和匹配工具"},
        ])
        main_layout.addWidget(dev_group)

        # 分组：实用工具
        utility_group = self._create_group_box("⚡ 实用工具", [
            {"icon": "📊", "title": "二维码工具", "desc": "生成和识别二维码，支持多种样式"},
            {"icon": "🎨", "title": "颜色工具", "desc": "颜色选择器和调色板工具"},
            {"icon": "🔗", "title": "链接提取", "desc": "从文本中提取和验证URL链接"},
            {"icon": "📄", "title": "文本对比", "desc": "对比两个文本文件内容，高亮显示差异"}
        ])
        main_layout.addWidget(utility_group)

        return main_widget

    def _create_welcome_section(self):
        """创建欢迎信息区域"""
        welcome_widget = QWidget()
        welcome_widget.setFixedHeight(120)
        welcome_widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {Colors.WECHAT_GREEN}, stop: 1 #06ad50);
                border-radius: 12px;
                border: none;
            }}
        """)
        
        layout = QHBoxLayout(welcome_widget)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(20)

        # 左侧图标和文字
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)

        # 欢迎标题
        welcome_title = QLabel("🚀 欢迎使用微信工具箱")
        welcome_font = QFont()
        welcome_font.setPointSize(16)
        welcome_font.setBold(True)
        welcome_title.setFont(welcome_font)
        welcome_title.setStyleSheet("color: white;")

        # 描述文字
        welcome_desc = QLabel("集成多种实用工具，提升您的工作效率")
        welcome_desc.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 13px;")
        
        text_layout.addWidget(welcome_title)
        text_layout.addWidget(welcome_desc)
        text_layout.addStretch()

        layout.addWidget(text_container, 1)

        # 右侧装饰图标
        deco_label = QLabel("⚡🛠️✨")
        deco_font = QFont()
        deco_font.setPointSize(20)
        deco_label.setFont(deco_font)
        deco_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(deco_label)

        return welcome_widget

    def _create_group_box(self, title, items):
        """创建分组框和内容（三等分卡片布局）"""
        group = QGroupBox(title)
        group.setStyleSheet(GroupBoxStyles.get_standard_style())
        layout = QVBoxLayout(group)
        layout.setSpacing(5)

        row_layout = None
        for i, item in enumerate(items):
            # 每 4 个新建一行
            if i % 4 == 0:
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setSpacing(5)
                row_layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(row_widget)

            card = self._create_item_card(item)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row_layout.addWidget(card)

        # 补齐空位占位（保持每行四个，即使最后不满）
        if len(items) % 4 != 0:
            for _ in range(4 - len(items) % 4):
                spacer = QWidget()
                spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                row_layout.addWidget(spacer)

        return group



    def _create_item_card(self, item):
        """创建一个更加紧凑的功能卡片（emoji图标 + 标题 + 描述）"""
        card = QPushButton()
        card.setFlat(True)
        card.setFixedHeight(70)  # 更紧凑的卡片高度
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(10, 6, 10, 6)  # 更紧凑的内边距
        layout.setSpacing(8)  # 减少间隔

        # 卡片样式 - 添加卡片边框
        card.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BACKGROUND_SECONDARY};
                border: 2px solid {Colors.BORDER_LIGHT};  # 添加边框，并加粗
                border-radius: 6px;  # 更圆润的边角
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {Colors.BACKGROUND_TERTIARY};
                border: 2px solid {Colors.WECHAT_GREEN};  # 边框更简洁且颜色变化
            }}
            QPushButton:pressed {{
                background-color: {Colors.HOVER_GRAY};
            }}
        """)

        # 图标区域
        icon_label = QLabel(item["icon"])
        icon_font = QFont()
        icon_font.setPointSize(16)  # 更小的图标尺寸
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(36, 36)  # 缩小图标区域
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.BACKGROUND_LIGHT};
                border-radius: 18px;  # 圆形图标
                border: 1px solid {Colors.BORDER_LIGHT};
            }}
        """)
        layout.addWidget(icon_label)

        # 文本区域
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        title_label = QLabel(item["title"])
        title_font = QFont()
        title_font.setPointSize(11)  # 更小的标题字体
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")

        desc_label = QLabel(item["desc"])
        desc_label.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: 9px;  # 更小的描述字体
        """)
        desc_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        layout.addWidget(text_container, 1)

        # 点击事件
        card.clicked.connect(lambda: self._on_tool_clicked(item["title"]))

        return card





    def _on_tool_clicked(self, tool_name):
        """处理工具点击事件"""
        self.set_status(f"正在跳转到: {tool_name}")
        
        # 创建工具名称映射表（与导航配置和content_area.py中的tool_pages保持一致）
        tool_mapping = {
            "文件查找": "文件查找",
            "文本对比": "文本对比", 
            "图片转换": "图片转换",  # 对应content_area.py中的"图片转换"
            "媒体下载": "媒体下载",  # 对应content_area.py中的"媒体下载"
            "JSON格式化": "JSON格式化",
            "编码转换": "加密解密",  # 对应二级菜单中的"加密解密"
            "代码格式化": "代码格式化",
            "正则工具": "正则表达式",
            "二维码工具": "二维码工具",
            "颜色工具": "颜色选择器",
            "链接提取": "媒体下载",  # 暂时映射到媒体下载工具
            "屏幕截屏": "截屏工具"   # 暂时映射到屏幕截屏工具
        }
        
        # 获取实际的工具名称
        actual_tool_name = tool_mapping.get(tool_name, tool_name)
        
        # 向上查找主窗口并触发导航
        self._trigger_navigation_to_tool(actual_tool_name)
    
    def _trigger_navigation_to_tool(self, tool_name):
        """触发导航到指定工具"""
        # 向上查找主窗口
        widget = self
        while widget is not None:
            widget = widget.parent()
            if hasattr(widget, 'nav_primary') and hasattr(widget, 'nav_secondary'):
                # 找到主窗口，触发导航
                # 1. 切换到工具一级菜单
                widget.nav_primary._on_nav_clicked("tools")
                # 2. 让二级导航选择对应的工具
                widget.nav_secondary._select_tool_by_name(tool_name)
                break
