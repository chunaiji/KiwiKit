from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from components.base_content import BaseContent
from styles.constants import Colors
from styles.widgets import ButtonStyles


class AboutAppContent(BaseContent):
    """关于本软件"""

    def __init__(self):
        content_widget = self._create_content_widget()
        super().__init__(title="ℹ️ 关于本软件", content_widget=content_widget)

    def _create_content_widget(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 软件标题
        title_label = QLabel("🛠 工具集软件（Toolkit App）")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333333;")
        layout.addWidget(title_label)

        # 版本信息
        version_label = QLabel("版本号：v1.0.0")
        version_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(version_label)

        # 软件简介
        description = QLabel("这是一款集成了多种常用Windows工具的软件，旨在帮助不同人群（开发者、设计师、学生等）提高工作效率。功能包括编码转换、正则测试、进制转换、截图、计算器等，旨在让你的日常任务更加便捷。")
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px;")
        layout.addWidget(description)

        # 软件特点
        features_label = QLabel("软件特点：\n- 多功能工具集\n- 简洁易用的用户界面\n- 支持快捷键操作\n- 适用于开发者、设计师、学生等多种用户")
        features_label.setWordWrap(True)
        features_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px;")
        layout.addWidget(features_label)

        # 分隔线
        layout.addSpacing(10)

        # 作者信息
        author_label = QLabel("作者：Your Name / Team")
        author_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px;")
        layout.addWidget(author_label)

        # 联系方式（可超链接）
        contact_label = QLabel('<a href="mailto:cnj008@126.com">📧 邮箱联系:cnj008@126.com</a> | '
                               '<a href="https://github.com/your-repo">🔗 GitHub</a> | '
                               '<a href="">🐦 微信:chunj008</a>')
        contact_label.setOpenExternalLinks(True)
        contact_label.setStyleSheet(f"color: {Colors.WECHAT_GREEN}; font-size: 14px;")
        layout.addWidget(contact_label)

        # 版权信息
        copyright_label = QLabel("© 2025 Your Name. 保留所有权利。")
        copyright_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(copyright_label)

        # 软件更新日志
        changelog_label = QLabel("更新日志：\n- v1.0.0: 初始版本发布\n- 预计未来版本将加入更多实用功能。")
        changelog_label.setWordWrap(True)
        changelog_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px;")
        layout.addWidget(changelog_label)

        # 添加图片区域
        image_layout = QHBoxLayout()

        # 图片1：软件 logo
        self.image_label1 = QLabel()
        pixmap1 = QPixmap("path_to_your_image_1.png")
        self.image_label1.setPixmap(pixmap1.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        self.image_label1.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(self.image_label1)

        # 图片2：软件功能展示图
        self.image_label2 = QLabel()
        pixmap2 = QPixmap("path_to_your_image_2.png")
        self.image_label2.setPixmap(pixmap2.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        self.image_label2.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(self.image_label2)

        layout.addLayout(image_layout)

        return main_widget
