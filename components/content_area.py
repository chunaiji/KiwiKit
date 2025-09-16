"""
主内容区域组件
"""

import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QStackedWidget, 
                               QTextEdit, QHBoxLayout, QPushButton, QFrame, QScrollArea)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from styles.generator import StyleGenerator
from components.tools import JSONFormatter, ImageConverterWidget, FileSearchWidget, EncodeDecodeSuite, RegexFormatterWidget, FileDiffTool, CodeFormatterTool, BaseConverter, ColorPickerWidget, MediaDownloaderWidget, QRToolWidget, ScreenshotWidget
from components.tools.dashboard import UsageDashboard
from components.tools.contact import ContactMeForm
from components.tools.about import AboutAppContent

# 导入日志系统
from utils.logger import info, error, warning, log_system_event, log_user_action

class ChatPage(QWidget):
    """聊天页面 - 微信风格"""
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 聊天头部 - 微信风格
        header = QWidget()
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Alice")
        title.setStyleSheet("font-size: 14px; font-weight: normal; color: #191919;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # 功能按钮
        for btn_text in ["📞", "📹", "👥"]:
            btn = QPushButton(btn_text)
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 14px;
                    color: #888888;
                }
                QPushButton:hover {
                    background: #f0f0f0;
                    border-radius: 4px;
                }
            """)
            header_layout.addWidget(btn)
        
        header.setStyleSheet("background: #f5f5f5; border-bottom: 1px solid #e7e7e7;")
        layout.addWidget(header)
        
        # 聊天区域
        chat_area = QTextEdit()
        chat_area.setReadOnly(True)
        chat_area.setHtml("""
        <div style="padding: 20px; font-family: 'Microsoft YaHei', sans-serif; line-height: 1.4;">
            <div style="text-align: center; color: #b2b2b2; margin: 20px 0; font-size: 12px;">
                ——— 今天 15:30 ———
            </div>
            
            <!-- 接收的消息 -->
            <div style="margin: 12px 0; display: flex; align-items: flex-start;">
                <div style="width: 40px; height: 40px; background: #07c160; border-radius: 6px; 
                           display: flex; align-items: center; justify-content: center; 
                           color: white; font-size: 16px; margin-right: 12px;">👩</div>
                <div style="max-width: 60%; background: #ffffff; padding: 8px 12px; 
                           border-radius: 8px; font-size: 14px; color: #191919; 
                           border: 1px solid #e7e7e7; word-wrap: break-word;">
                    你好，今天的会议准备得怎么样了？
                </div>
            </div>
            
            <!-- 发送的消息 -->
            <div style="margin: 12px 0; display: flex; align-items: flex-start; justify-content: flex-end;">
                <div style="max-width: 60%; background: #95ec69; padding: 8px 12px; 
                           border-radius: 8px; font-size: 14px; color: #191919; 
                           word-wrap: break-word; margin-right: 12px;">
                    准备得差不多了，PPT已经完成，需要再确认一下时间
                </div>
                <div style="width: 40px; height: 40px; background: #07c160; border-radius: 6px; 
                           display: flex; align-items: center; justify-content: center; 
                           color: white; font-size: 16px;">👤</div>
            </div>
            
            <!-- 接收的消息 -->
            <div style="margin: 12px 0; display: flex; align-items: flex-start;">
                <div style="width: 40px; height: 40px; background: #07c160; border-radius: 6px; 
                           display: flex; align-items: center; justify-content: center; 
                           color: white; font-size: 16px; margin-right: 12px;">👩</div>
                <div style="max-width: 60%; background: #ffffff; padding: 8px 12px; 
                           border-radius: 8px; font-size: 14px; color: #191919; 
                           border: 1px solid #e7e7e7; word-wrap: break-word;">
                    好的，下午2点在会议室A，记得带上项目资料
                </div>
            </div>
            
            <!-- 发送的消息 -->
            <div style="margin: 12px 0; display: flex; align-items: flex-start; justify-content: flex-end;">
                <div style="max-width: 60%; background: #95ec69; padding: 8px 12px; 
                           border-radius: 8px; font-size: 14px; color: #191919; 
                           word-wrap: break-word; margin-right: 12px;">
                    收到，我会准时到的 👍
                </div>
                <div style="width: 40px; height: 40px; background: #07c160; border-radius: 6px; 
                           display: flex; align-items: center; justify-content: center; 
                           color: white; font-size: 16px;">👤</div>
            </div>
        </div>
        """)
        chat_area.setStyleSheet("""
            QTextEdit {
                border: none;
                background: #f5f5f5;
                selection-background-color: #c7edff;
            }
        """)
        layout.addWidget(chat_area)
        
        # 输入区域 - 微信风格
        input_area = QWidget()
        input_area.setFixedHeight(54)
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(12, 8, 12, 8)
        input_layout.setSpacing(8)
        
        # 表情按钮
        emoji_btn = QPushButton("😊")
        emoji_btn.setFixedSize(32, 32)
        emoji_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                border-radius: 4px;
            }
        """)
        input_layout.addWidget(emoji_btn)
        
        # 输入框
        input_text = QTextEdit()
        input_text.setFixedHeight(38)
        input_text.setPlaceholderText("输入消息...")
        input_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e7e7e7;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                background: white;
                color: #191919;
            }
            QTextEdit:focus {
                border-color: #07c160;
            }
        """)
        input_layout.addWidget(input_text)
        
        # 发送按钮
        send_btn = QPushButton("发送")
        send_btn.setFixedSize(60, 32)
        send_btn.setStyleSheet("""
            QPushButton {
                background: #07c160;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #06ad56;
            }
            QPushButton:pressed {
                background: #059748;
            }
        """)
        input_layout.addWidget(send_btn)
        
        input_area.setStyleSheet("background: #ffffff; border-top: 1px solid #e7e7e7;")
        layout.addWidget(input_area)

class ContactDetailPage(QWidget):
    """联系人详情页面"""
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # 头像和基本信息
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setAlignment(Qt.AlignCenter)
        
        avatar = QLabel("👤")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(100, 100)
        avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                           stop:0 #667eea, stop:1 #764ba2);
                border-radius: 50px;
                color: white;
                font-size: 48px;
            }
        """)
        
        name = QLabel("Alice")
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("font-size: 24px; font-weight: bold; color: #1f2937; margin: 16px 0;")
        
        status = QLabel("在线")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("font-size: 14px; color: #22c55e;")
        
        header_layout.addWidget(avatar)
        header_layout.addWidget(name)
        header_layout.addWidget(status)
        
        layout.addWidget(header)
        
        # 操作按钮
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setAlignment(Qt.AlignCenter)
        actions_layout.setSpacing(16)
        
        for text, icon in [("发消息", "💬"), ("语音通话", "📞"), ("视频通话", "📹")]:
            btn = QPushButton(f"{icon}\n{text}")
            btn.setFixedSize(80, 80)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(59, 130, 246, 0.1);
                    border: none;
                    border-radius: 12px;
                    font-size: 12px;
                    color: #3b82f6;
                }
                QPushButton:hover {
                    background: rgba(59, 130, 246, 0.2);
                }
            """)
            actions_layout.addWidget(btn)
        
        layout.addWidget(actions)
        
        # 详细信息
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_items = [
            ("部门", "技术部"),
            ("职位", "高级工程师"),
            ("邮箱", "alice@company.com"),
            ("电话", "+86 138 0000 0000"),
            ("地址", "北京市朝阳区xxx大厦"),
        ]
        
        for label, value in info_items:
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(0, 8, 0, 8)
            
            label_widget = QLabel(label)
            label_widget.setFixedWidth(80)
            label_widget.setStyleSheet("color: #6b7280; font-size: 14px;")
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1f2937; font-size: 14px;")
            
            item_layout.addWidget(label_widget)
            item_layout.addWidget(value_widget)
            item_layout.addStretch()
            
            info_layout.addWidget(item)
        
        layout.addWidget(info_frame)
        layout.addStretch()

class DefaultPage(QWidget):
    """默认页面 - 微信风格"""
    def __init__(self, title="欢迎使用", description="请从左侧选择功能开始使用"):
        super().__init__()
        self.title = title
        self.description = description
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 图标
        icon = QLabel("📱")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("""
            font-size: 48px;
            color: #888888;
        """)
        
        # 标题
        title = QLabel(self.title)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: normal;
            color: #191919;
            margin: 12px 0;
        """)
        
        # 描述
        desc = QLabel(self.description)
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("""
            font-size: 14px;
            color: #888888;
            line-height: 1.5;
        """)
        
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()

class ContentArea(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 使用堆叠窗口管理不同页面
        self.stacked_widget = QStackedWidget()
        
        # 添加各种页面
        self.pages = {}
        self._initialize_pages()
        
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        
        # 显示默认页面
        self.stacked_widget.setCurrentWidget(self.pages["default"])
        
        layout.addWidget(self.stacked_widget)
    
    def _initialize_pages(self):
        """初始化所有页面，包含错误处理"""
        info("开始初始化所有页面组件")
        
        page_configs = {
            "default": lambda: DefaultPage("欢迎使用", "请从左侧选择功能开始使用"),
            "首页": lambda: UsageDashboard(),
            "dashboard": lambda: UsageDashboard(),
            "chat": lambda: ChatPage(),
            "contact_detail": lambda: ContactDetailPage(),
            "contact_me": lambda: ContactMeForm(),
            "about": lambda: AboutAppContent(),
            "groups_page": lambda: DefaultPage("群组管理", "查看和管理您的群组"),
            "apps_page": lambda: DefaultPage("应用中心", "发现更多实用应用"),
            "files_page": lambda: DefaultPage("文件管理", "管理您的文件和文档"),
            "settings_page": lambda: DefaultPage("设置", "个性化您的应用体验"),
            # 工具页面
            "json_formatter": lambda: JSONFormatter(),
            "image_converter": lambda: ImageConverterWidget(),
            "file_search": lambda: FileSearchWidget(),
            "encode_decode": lambda: EncodeDecodeSuite(),
            "regex_formatter": lambda: RegexFormatterWidget(),
            "file_diff": lambda: FileDiffTool(),
            "code_formatter": lambda: CodeFormatterTool(),
            "base_converter": lambda: BaseConverter(),
            "color_picker": lambda: ColorPickerWidget(),
            "media_download": lambda: MediaDownloaderWidget(),
            "qr_tool": lambda: QRToolWidget(),
            "screenshot": lambda: ScreenshotWidget(),
        }
        
        total_pages = len(page_configs)
        loaded_successfully = 0
        failed_pages = []
        
        for page_key, page_creator in page_configs.items():
            try:
                info(f"正在加载页面: {page_key} ({loaded_successfully + 1}/{total_pages})")
                start_time = time.time()
                
                self.pages[page_key] = page_creator()
                
                load_time = time.time() - start_time
                info(f"页面加载成功: {page_key} (耗时: {load_time:.3f}秒)")
                loaded_successfully += 1
                
            except ImportError as e:
                error(f"页面加载失败 - 缺少依赖库: {page_key} - {e}")
                log_system_event("页面加载失败", f"{page_key}: 缺少依赖 {e}")
                failed_pages.append((page_key, f"依赖缺失: {e}"))
                
                # 创建错误页面替代
                self.pages[page_key] = DefaultPage(
                    f"加载失败: {page_key}", 
                    f"缺少必要的依赖库: {e}\n\n请检查依赖安装情况"
                )
                
            except Exception as e:
                error(f"页面加载失败 - 未知错误: {page_key} - {e}")
                log_system_event("页面加载失败", f"{page_key}: 未知错误 {e}")
                failed_pages.append((page_key, f"加载错误: {e}"))
                
                # 创建错误页面替代
                self.pages[page_key] = DefaultPage(
                    f"加载失败: {page_key}", 
                    f"页面初始化出错: {e}\n\n请查看日志获取详细信息"
                )
        
        # 记录加载统计信息
        failed_count = len(failed_pages)
        success_rate = (loaded_successfully / total_pages) * 100
        
        info(f"页面加载统计: 成功 {loaded_successfully}/{total_pages} ({success_rate:.1f}%)")
        
        if failed_count > 0:
            warning(f"有 {failed_count} 个页面加载失败:")
            for page_key, error_msg in failed_pages:
                warning(f"  - {page_key}: {error_msg}")
            log_system_event("页面加载警告", f"{failed_count}个页面加载失败")
        else:
            log_system_event("页面加载完成", f"所有{total_pages}个页面加载成功")
            
        info("页面初始化完成")
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QWidget {
                background: #f5f5f5;
            }
        """)
    
    def show_page(self, page_key):
        """显示指定页面"""
        if page_key in self.pages:
            log_user_action("页面切换", f"切换到页面: {page_key}")
            info(f"显示页面: {page_key}")
            self.stacked_widget.setCurrentWidget(self.pages[page_key])
        else:
            warning(f"页面不存在: {page_key}")
            log_system_event("页面访问失败", f"尝试访问不存在的页面: {page_key}")
            # 回退到默认页面
            self.stacked_widget.setCurrentWidget(self.pages["default"])
    
    def show_chat_page(self, contact_name=None):
        """显示聊天页面"""
        self.show_page("chat")
    
    def show_contact_detail(self, contact_name=None):
        """显示联系人详情"""
        self.show_page("contact_detail")
    
    def show_content_by_nav(self, group_key, item_key):
        """根据导航选择显示对应内容"""
        
        # 特殊处理首页点击
        current_tool = getattr(self, '_current_selected_tool_name', None)
        if current_tool == "首页":
            self.show_page("首页")
            return
        
        # 通过工具名称映射到具体页面
        tool_pages = {
            "JSON格式化": "json_formatter",
            "图片转换": "image_converter",
            "文件查找": "file_search",
            "加密解密": "encode_decode",
            "正则表达式": "regex_formatter",
            "文本对比": "file_diff",
            "代码格式化": "code_formatter",
            "进制转换": "base_converter",
            "颜色选择器": "color_picker",
            "媒体下载": "media_download",
            "二维码工具": "qr_tool",
            "截屏工具": "screenshot",
            "联系我们": "contact_me",  # 联系我页面
            "关于软件": "about",  # 关于软件页面
            "Base64编解码": "apps_page",  # 暂时指向默认页面
            "URL编解码": "apps_page",
            "MD5加密": "apps_page",
            "时间戳转换": "apps_page",
            "单位换算": "apps_page",
            "正则测试": "apps_page"
        }
        
        # 检查是否是工具页面（通过检查当前选中的项目名称）
        current_tool = getattr(self, '_current_selected_tool_name', None)
        if current_tool and current_tool in tool_pages:
            self.show_page(tool_pages[current_tool])
            return
        
        # 根据导航键显示默认内容
        self._show_default_content_for_nav(group_key)
    
    def _show_default_content_for_nav(self, nav_key):
        """为指定导航键显示默认内容"""
        if nav_key == "home":
            # 首页显示dashboard
            self.show_page("首页")
        elif nav_key == "tools":
            # 工具页面默认显示第一个工具（已通过信号处理）
            # 如果没有工具选中，显示默认页面
            if not hasattr(self, '_current_selected_tool_name'):
                self.show_page("default")
        else:
            # 其他页面的路由逻辑
            if nav_key == "messages":
                self.show_chat_page()
            elif nav_key == "contacts":
                self.show_contact_detail()
            elif nav_key == "favorites":
                self.show_page("files_page")
            elif nav_key == "groups":
                self.show_page("groups_page")
            elif nav_key == "apps":
                self.show_page("apps_page")
            elif nav_key == "mobile":
                self.show_page("apps_page")
            elif nav_key == "files":
                self.show_page("files_page")
            else:
                self.show_page("default")
    
    def set_selected_tool(self, tool_name):
        """设置当前选中的工具名称"""
        self._current_selected_tool_name = tool_name
    
    def refresh_styles(self):
        """刷新样式 - 支持主题切换"""
        from styles.constants import Colors
        # 重新设置主背景样式
        self.setStyleSheet(f"""
            QWidget {{
                background: {Colors.BACKGROUND_PRIMARY};
            }}
        """)
        
        # 刷新所有页面的样式
        for page in self.pages.values():
            if hasattr(page, 'refresh_styles'):
                page.refresh_styles()
