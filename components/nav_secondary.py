"""
中间二级导航栏组件
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, 
                               QPushButton, QScrollArea, QListWidget, QListWidgetItem, 
                               QHBoxLayout, QLineEdit)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from styles.generator import StyleGenerator
from PySide6.QtWidgets import QSizePolicy
from styles.constants import Colors
from config.nav_config import get_nav_secondary_data

# 导入日志系统
from utils.logger import info, error, warning, log_system_event, log_user_action

class ContactItem(QWidget):
    """联系人项目组件 - 微信风格，支持条纹背景、hover、高亮、展开子项"""
    
    clicked = Signal(str, str)  # (group_key, item_key)

    def __init__(self, group_key, item_key, item_data, level=0, index=0, parent=None):
        super().__init__(parent)
        self.group_key = group_key
        self.item_key = item_key
        self.item_data = item_data
        self.level = level
        self.index = index
        self.child_widgets = []
        self.is_expanded = False
        self.is_selected = False  # 添加选中状态

        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover)

        self._setup_ui()

    def _setup_ui(self):
        # 主 layout（垂直方向：内容 + 分隔线）
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 条目容器
        container = QWidget()
        container_layout = QHBoxLayout(container)
        # 设置左对齐的边距
        left_margin = 10 + (self.level * 15)  # 基础边距加上层级缩进
        container_layout.setContentsMargins(left_margin, 0, 10, 0)
        container_layout.setSpacing(4)  # 图标和文字间的小间距

        # 展开/折叠图标（只对有子项的一级项目显示）
        if self.level == 0 and "children" in self.item_data:
            self.expand_icon = QLabel("▶")
            self.expand_icon.setStyleSheet("""
                font-size: 12px;
                color: #666666;
                background: transparent;  /* 🧪 临时调试背景色 */
                padding: 0px;
                margin: 0px;
                font-weight: bold;
            """)
            self.expand_icon.setFixedWidth(16)  # 给图标固定一个小宽度
            self.expand_icon.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            container_layout.addWidget(self.expand_icon)
        else:
            # placeholder = QLabel()  # 空白占位，保持对齐
            # placeholder.setFixedWidth(1)
            # container_layout.addWidget(placeholder)
            pass

        # # 图标
        # if 'icon' in self.item_data:
        #     icon_label = QLabel(self.item_data['icon'])
        #     icon_label.setStyleSheet("""
        #         font-size: 16px;
        #         background: transparent;
        #     """)
        #     icon_label.setFixedSize(20, 20)
        #     container_layout.addWidget(icon_label)

        # 信息区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(0, 4, 0, 4)

        # 名称
        name_label = QLabel(self.item_data['name'])
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        name_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        name_label.setStyleSheet(f"""
            font-size: {'15px' if self.level == 0 else '13px'};
            color: #191919;
            background: transparent;
        """)
        info_layout.addWidget(name_label)

        # 描述（如果有）
        if 'description' in self.item_data:
            desc_label = QLabel(self.item_data['description'])
            desc_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            desc_label.setStyleSheet("""
                font-size: 11px;
                color: #888888;
                background: transparent;
            """)
            info_layout.addWidget(desc_label)

        container_layout.addLayout(info_layout)  # 直接添加，不设置stretch因子

        # 时间或其他信息
        # if 'time' in self.item_data:
        #     time_label = QLabel(self.item_data['time'])
        #     time_label.setStyleSheet("""
        #         font-size: 11px;
        #         color: #999999;
        #         background: transparent;
        #     """)
        #     container_layout.addWidget(time_label)

        # 设置背景色（条纹）
        # bg_color = Colors.BACKGROUND_CHAT if self.index % 2 else Colors.BACKGROUND_SECONDARY
        bg_color = Colors.BACKGROUND_SECONDARY
        container.setStyleSheet(f"background-color: {bg_color};")

        # 添加容器到主布局
        main_layout.addWidget(container)

        # 添加底部分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet(f"""
            color: {Colors.BACKGROUND_LIGHT};
            background-color: {Colors.BACKGROUND_LIGHT};
            margin-right: 12px;
        """)
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)

        self.setLayout(main_layout)
        self.setFixedHeight(48 if self.level == 0 else 40)

    def enterEvent(self, event):
        """鼠标进入时高亮"""
        if not self.is_selected:  # 只有非选中状态才显示hover效果
            self.setStyleSheet(f"""
                ContactItem {{
                    background-color: {Colors.HOVER_GRAY};
                    border: none;
                }}
            """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """恢复样式"""
        if not self.is_selected:  # 只有非选中状态才恢复默认样式
            self._update_style()  # 使用统一的样式更新方法
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """点击事件：一级项目展开/折叠子项"""
        if event.button() == Qt.LeftButton:
            if self.level == 0 and "children" in self.item_data:
                self.is_expanded = not self.is_expanded
                self.toggle_children()
                # 更新展开图标
                if hasattr(self, 'expand_icon'):
                    self.expand_icon.setText("▼" if self.is_expanded else "▶")
            self.clicked.emit(self.group_key, self.item_key)

    def toggle_children(self):
        """展开或隐藏子项"""
        for child in self.child_widgets:
            child.setVisible(self.is_expanded)
    
    def set_selected(self, selected):
        """设置选中状态"""
        self.is_selected = selected
        self._update_style()
    
    def _update_style(self):
        """更新样式"""
        if self.is_selected:
            # 选中状态样式
            self.setStyleSheet(f"""
                ContactItem {{
                    background-color: {Colors.SELECTED_BLUE};
                    border-left: 3px solid {Colors.WECHAT_GREEN};
                    border-right: none;
                    border-top: none;
                    border-bottom: none;
                }}
            """)
        else:
            # 默认状态样式
            bg_color = Colors.BACKGROUND_SECONDARY
            self.setStyleSheet(f"""
                ContactItem {{
                    background-color: {bg_color};
                    border: none;
                }}
            """)

    def add_child(self, child_widget):
        """添加子项目"""
        self.child_widgets.append(child_widget)
        child_widget.setVisible(self.is_expanded)
    
    def refresh_styles(self):
        """刷新样式 - 支持主题切换"""
        # 重新导入当前主题的颜色常量
        from styles.constants import Colors
        
        # 重新设置整个组件，重新调用_setup_ui会有问题，所以手动更新关键样式
        bg_color = Colors.BACKGROUND_SECONDARY
        
        # 更新容器背景色
        container = self.findChild(QWidget)  # 找到第一个子QWidget（容器）
        if container:
            container.setStyleSheet(f"background-color: {bg_color};")
        
        # 更新分隔线样式
        separator = self.findChild(QFrame)
        if separator:
            separator.setStyleSheet(f"""
                color: {Colors.BACKGROUND_LIGHT};
                background-color: {Colors.BACKGROUND_LIGHT};
                margin-right: 12px;
            """)
        
        # 更新名称标签样式
        for label in self.findChildren(QLabel):
            if "▶" not in label.text() and "▼" not in label.text():  # 不是展开图标
                label.setStyleSheet(f"""
                    font-size: {'14px' if self.level == 0 else '13px'};
                    color: {Colors.TEXT_PRIMARY};
                    background: transparent;
                """)
        
        # 刷新子项样式
        for child in self.child_widgets:
            if hasattr(child, 'refresh_styles'):
                child.refresh_styles()


class SearchBar(QWidget):
    """搜索栏组件 - 微信风格"""
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)  # 减小边距
        layout.setSpacing(8)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索")
        self.search_input.setFixedHeight(28)  # 高度固定
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {Colors.BACKGROUND_TERTIARY};
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                color: #191919;
            }}
            QLineEdit:focus {{
                background: #eeeeee;
                border: 1px solid #07c160;
            }}
        """)

        # 允许搜索框根据父布局伸缩
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 添加搜索框到布局
        layout.addWidget(self.search_input)
    
    def refresh_styles(self):
        """刷新样式 - 支持主题切换"""
        from styles.constants import Colors
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {Colors.BACKGROUND_TERTIARY};
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                background: {Colors.HOVER_GRAY};
                border: 1px solid {Colors.WECHAT_GREEN};
            }}
        """)

class NavSecondary(QWidget):
    """二级导航栏组件"""
    item_selected = Signal(str, str)  # group_key, item_key
    tool_selected = Signal(str)  # tool_name
    
    def __init__(self):
        try:
            super().__init__()
            info("开始初始化副导航组件")
            
            self.current_nav = "home"  # 默认选中首页
            self.current_selected_item = None  # 跟踪当前选中的项目
            self._setup_ui()
            self._apply_styles()
            self._load_default_data()
            
            log_system_event("副导航组件初始化完成", f"默认选中: {self.current_nav}")
            info("副导航组件初始化完成")
            
        except Exception as e:
            error(f"副导航组件初始化失败: {e}")
            log_system_event("副导航初始化失败", f"错误: {e}")
            raise
    
    def _setup_ui(self):
        """设置UI布局 - 微信风格"""
        layout = QVBoxLayout(self)
        
        # 搜索栏
        self.search_bar = SearchBar()
        layout.addWidget(self.search_bar)
        
        # 联系人列表滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 4px;
            }
            QScrollBar::handle:vertical {
                background: #d9d9d9;
                border-radius: 2px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #bfbfbf;
            }
        """)
        
        # 内容容器
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.content_container)
        layout.addWidget(scroll_area)
    
    def _apply_styles(self):
        """应用样式 - 微信白色风格"""
        # 重新导入当前主题的颜色常量
        from styles.constants import Colors
        self.setStyleSheet(f"""
            QWidget {{
                background: {Colors.NAV_SECONDARY_BG};
                border-right: 1px solid {Colors.BORDER_LIGHT};
                min-width: 280px;
                max-width: 280px;
            }}
        """)
    
    def _load_default_data(self):
        """加载默认数据"""
        self.load_nav_data("home")
    
    def load_nav_data(self, nav_key):
        """根据一级导航加载对应的数据 - 支持两层结构"""
        self.current_nav = nav_key
        
        # 清除现有内容
        self._clear_content()
        
        # 根据导航类型加载不同数据
        nav_data = self._get_nav_data(nav_key)
        
        # 添加标题（如果需要显示）
        # if nav_data.get("show_header", False):
        #     group_header = GroupHeader(nav_data["title"], level=0)
        #     self.content_layout.addWidget(group_header)
        
        # 添加项目
        item_index = 0  # 用于条纹背景
        for item_data in nav_data["items"]:
            # 为数组中的每个项目生成唯一key
            item_key = f"item_{item_index}"
            
            # 创建一级项目
            item_widget = ContactItem(nav_key, item_key, item_data, level=0, index=item_index)
            item_widget.clicked.connect(lambda gk, ik, data=item_data: self._on_item_clicked(gk, ik, data))
            self.content_layout.addWidget(item_widget)
            item_index += 1
            
            # 添加二级项目（如果有children数组）
            if "children" in item_data and isinstance(item_data["children"], list):
                for child_index, child_data in enumerate(item_data["children"]):
                    child_key = f"child_{item_index}_{child_index}"
                    child_widget = ContactItem(nav_key, child_key, child_data, level=1, index=item_index)
                    child_widget.clicked.connect(lambda gk, ik, data=child_data: self._on_item_clicked(gk, ik, data))
                    item_widget.add_child(child_widget)  # 将子项添加到父项
                    self.content_layout.addWidget(child_widget)
                    item_index += 1
        
        # 添加弹性空间
        self.content_layout.addStretch()
        
        # 自动选择第一个可用的项目
        self._auto_select_first_item(nav_data)
    
    def _clear_content(self):
        """清除内容"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _auto_select_first_item(self, nav_data):
        """自动选择第一个可用的项目"""
        if not nav_data or not nav_data.get("items"):
            return
        
        first_item = nav_data["items"][0]
        
        # 如果第一个项目有子项，选择第一个子项
        if "children" in first_item and isinstance(first_item["children"], list) and first_item["children"]:
            first_child = first_item["children"][0]
            self._trigger_item_selection(self.current_nav, "child_1_0", first_child)
        else:
            # 否则选择第一个项目本身
            self._trigger_item_selection(self.current_nav, "item_0", first_item)
    
    def _trigger_item_selection(self, group_key, item_key, item_data):
        """触发项目选择（用于程序化选择）"""
        # 清除之前的选中状态
        if self.current_selected_item:
            self.current_selected_item.set_selected(False)
        
        # 找到并设置新的选中项目
        target_widget = self._find_item_widget(group_key, item_key, item_data)
        if target_widget:
            target_widget.set_selected(True)
            self.current_selected_item = target_widget
        
        # 发射通用的项目选择信号
        self.item_selected.emit(group_key, item_key)
        
        # 如果是工具项目，发射专门的工具选择信号
        if 'name' in item_data:
            tool_name = item_data['name']
            self.tool_selected.emit(tool_name)

    def _on_item_clicked(self, group_key, item_key, item_data):
        """处理项目点击事件"""
        self._trigger_item_selection(group_key, item_key, item_data)
    
    def _get_nav_data(self, nav_key):
        """获取导航数据 - 使用配置文件"""
        return get_nav_secondary_data(nav_key)
    
    def refresh_styles(self):
        """刷新样式 - 支持主题切换"""
        # 重新导入当前主题的颜色常量
        from styles.constants import Colors
        # 重新应用主组件样式
        self._apply_styles()
        
        # 刷新搜索栏样式
        if hasattr(self, 'search_bar'):
            self.search_bar.refresh_styles()
    
    def _select_tool_by_name(self, tool_name):
        """根据工具名称选择对应的导航项"""
        # 查找所有ContactItem组件
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'item_data') and isinstance(widget.item_data, dict):
                    # 检查是否是目标工具
                    if widget.item_data.get('name') == tool_name:
                        # 如果是子项（level=1），需要先展开父项
                        if widget.level == 1:
                            # 查找对应的父项并展开
                            parent_widget = self._find_parent_widget(widget)
                            if parent_widget and not parent_widget.is_expanded:
                                parent_widget.is_expanded = True
                                parent_widget.toggle_children()
                                # 更新展开图标
                                if hasattr(parent_widget, 'expand_icon'):
                                    parent_widget.expand_icon.setText("▼")
                        
                        # 直接触发选择逻辑
                        self._trigger_item_selection(widget.group_key, widget.item_key, widget.item_data)
                        return True
        
        return False
    
    def _find_parent_widget(self, child_widget):
        """查找子项的父项组件"""
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if (hasattr(widget, 'level') and widget.level == 0 and 
                    hasattr(widget, 'child_widgets') and child_widget in widget.child_widgets):
                    return widget
        return None
    
    def _find_item_widget(self, group_key, item_key, item_data):
        """根据group_key, item_key和item_data查找对应的widget"""
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if (hasattr(widget, 'group_key') and hasattr(widget, 'item_key') and 
                    hasattr(widget, 'item_data') and
                    widget.group_key == group_key and widget.item_key == item_key):
                    return widget
        return None
        
        # 刷新所有联系人项目样式
        if hasattr(self, 'content_container'):
            # 递归刷新所有子组件
            self._refresh_child_widgets(self.content_container)
    
    def _refresh_child_widgets(self, parent_widget):
        """递归刷新所有子组件的样式"""
        for child in parent_widget.findChildren(QWidget):
            if hasattr(child, 'refresh_styles'):
                child.refresh_styles()
