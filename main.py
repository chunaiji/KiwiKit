from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QIcon
from components.header import Header
from components.nav_primary import NavPrimary
from components.nav_secondary import NavSecondary
from components.content_area import ContentArea
from components.settings_dialog import SettingsDialog, theme_manager
from config import AppConfig
from styles.generator import StyleGenerator

# 初始化日志系统
from utils.logger import (
    GlobalLogger, info, error, warning, critical, 
    log_system_event, log_user_action, cleanup_old_logs
)

# 导入配置和工具
from config.app_config import (ORGANIZATION, APPLICATION_NAME, APPLICATION_VERSION, 
                              THEME, get_theme_config, reset_all_styles, apply_all_styles)
from config.nav_config import NAV_CONFIG
from utils.user_info import get_unique_identifier
from utils.background_api import background_api_manager

class MainWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            
            # 获取并记录设备唯一码
            try:
                unique_id = get_unique_identifier()
                info(f"应用程序启动 - {AppConfig.APP_NAME}")
                info(f"设备唯一码: {unique_id}")
                log_system_event("应用启动", f"版本: {AppConfig.APP_NAME}, 设备唯一码: {unique_id}")
            except Exception as e:
                warning(f"获取设备唯一码失败: {e}")
                info(f"应用程序启动 - {AppConfig.APP_NAME}")
                log_system_event("应用启动", f"版本: {AppConfig.APP_NAME}, 设备唯一码: 获取失败")
            
            self.setWindowTitle(AppConfig.APP_NAME)
            self.setMinimumSize(AppConfig.MIN_WINDOW_WIDTH, AppConfig.MIN_WINDOW_HEIGHT)

            main_widget = QWidget()
            main_layout = QVBoxLayout(main_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            # 头部
            # header = Header()
            # main_layout.addWidget(header)

            # 三栏布局
            body_layout = QHBoxLayout()
            body_layout.setContentsMargins(0, 0, 0, 0)
            body_layout.setSpacing(0)
            
            # 初始化各个组件并记录加载状态
            self._initialize_components()
            
        except Exception as e:
            error(f"主窗口初始化失败: {e}")
            log_system_event("窗口初始化失败", f"错误: {e}")
            raise
    
    def _initialize_components(self):
        """初始化主要组件并记录加载状态"""
        try:
            info("开始初始化主窗口组件")
            
            # 初始化主导航
            info("正在加载主导航组件...")
            self.nav_primary = NavPrimary()
            info("主导航组件加载完成")
            
            # 初始化副导航
            info("正在加载副导航组件...")
            self.nav_secondary = NavSecondary()
            info("副导航组件加载完成")
            
            # 初始化内容区域
            info("正在加载内容区域组件...")
            self.content_area = ContentArea()
            info("内容区域组件加载完成")
            
            # 完成布局设置
            self._setup_layout()
            
            # 连接信号
            self._connect_signals()
            
            # 初始化导航状态（显示首页）
            self._init_navigation()
            
            log_system_event("主窗口初始化完成", "所有组件加载成功")
            info("主窗口组件初始化完成")
            
            # 启动后台API服务
            self._start_background_services()
            
        except Exception as e:
            error(f"组件初始化失败: {e}")
            log_system_event("组件初始化失败", f"错误: {e}")
            raise
    
    def _setup_layout(self):
        """设置布局"""
        try:
            info("开始设置主窗口布局")
            
            main_widget = QWidget()
            main_layout = QVBoxLayout(main_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            body_layout = QHBoxLayout()
            body_layout.setContentsMargins(0, 0, 0, 0)
            body_layout.setSpacing(0)

            body_layout.addWidget(self.nav_primary, AppConfig.LAYOUT_RATIO[0])
            body_layout.addWidget(self.nav_secondary, AppConfig.LAYOUT_RATIO[1])
            body_layout.addWidget(self.content_area, AppConfig.LAYOUT_RATIO[2])
            main_layout.addLayout(body_layout)

            self.setCentralWidget(main_widget)
            
            info("主窗口布局设置完成")
            
        except Exception as e:
            error(f"布局设置失败: {e}")
            log_system_event("布局设置失败", f"错误: {e}")
            raise
    
    def _connect_signals(self):
        """连接组件间的信号"""
        try:
            info("开始连接组件信号")
            
            # 左侧导航变化 -> 中间导航更新
            self.nav_primary.nav_changed.connect(self.nav_secondary.load_nav_data)
            
            # 中间导航选择 -> 右侧内容更新
            self.nav_secondary.item_selected.connect(self.content_area.show_content_by_nav)
            
            # 工具选择 -> 右侧内容更新
            self.nav_secondary.tool_selected.connect(self.content_area.set_selected_tool)
            self.nav_secondary.tool_selected.connect(lambda tool_name: self.content_area.show_content_by_nav("tools", ""))
            
            # 用户头像点击
            self.nav_primary.user_clicked.connect(self._on_user_clicked)
            
            # 设置按钮点击
            self.nav_primary.settings_clicked.connect(self._on_settings_clicked)
            
            info("组件信号连接完成")
            
        except Exception as e:
            error(f"信号连接失败: {e}")
            log_system_event("信号连接失败", f"错误: {e}")
            raise
    
    def _init_navigation(self):
        """初始化导航状态 - 程序启动时自动跳转到首页"""
        try:
            info("初始化导航状态")
            
            # 触发默认导航（首页）
            self.nav_primary.nav_changed.emit("home")
            
            log_system_event("导航初始化完成", "默认选中首页")
            info("导航状态初始化完成")
            
        except Exception as e:
            error(f"导航初始化失败: {e}")
            log_system_event("导航初始化失败", f"错误: {e}")
    
    def _on_tool_selected(self, tool_name):
        """工具选择处理"""
        try:
            info(f"工具切换: {tool_name}")
            
            # 记录当前选中的工具
            self.content_area._current_selected_tool_name = tool_name
            
        except Exception as e:
            error(f"工具选择处理失败: {e}")
    
    def _on_user_clicked(self):
        """用户头像点击处理"""
        info("用户点击头像，显示用户信息菜单")
        # 这里可以显示用户信息弹窗或菜单
    
    def _on_settings_clicked(self):
        """设置按钮点击处理"""
        # 创建设置对话框
        current_theme = theme_manager.get_current_theme()
        settings_dialog = SettingsDialog(self, current_theme)
        
        # 连接主题切换信号
        settings_dialog.theme_changed.connect(self._on_theme_changed)
        
        # 显示对话框
        settings_dialog.exec()
    
    def _on_theme_changed(self, theme_name):
        """主题切换处理"""
        info(f"切换主题到: {theme_name}")
        
        # 切换主题
        theme_manager.switch_theme(theme_name)
        
        # 刷新整个界面
        self._refresh_ui()
    
    def _refresh_ui(self):
        """刷新界面样式"""
        try:
            # 重新加载所有组件的样式
            self.nav_primary.refresh_styles()
            self.nav_secondary.refresh_styles()
            self.content_area.refresh_styles()
            
            # 递归刷新所有子组件
            self._refresh_all_children(self)
            
            # 强制重绘整个窗口
            self.repaint()
            info("界面样式刷新完成")
        except Exception as e:
            error(f"刷新界面时出错: {e}")
    
    def _refresh_all_children(self, widget):
        """递归刷新所有子组件"""
        try:
            for child in widget.findChildren(QWidget):
                # 刷新有refresh_styles方法的组件
                if hasattr(child, 'refresh_styles'):
                    child.refresh_styles()
                # 强制重新应用样式表
                child.style().unpolish(child)
                child.style().polish(child)
        except Exception as e:
            error(f"刷新子组件时出错: {e}")
    
    def _start_background_services(self):
        """启动后台服务"""
        try:
            info("启动后台API服务")
            
            # 获取后台API服务
            api_service = background_api_manager.get_service()
            
            # 检查服务是否有效
            if api_service is None:
                error("后台API服务获取失败：服务为空")
                return
            
            # 连接信号，记录后台API结果
            if hasattr(api_service, 'api_success') and api_service.api_success is not None:
                api_service.api_success.connect(self._on_background_api_success)
            else:
                warning("api_success信号不可用")
                
            if hasattr(api_service, 'api_failed') and api_service.api_failed is not None:
                api_service.api_failed.connect(self._on_background_api_failed)
            else:
                warning("api_failed信号不可用")
                
            if hasattr(api_service, 'service_started') and api_service.service_started is not None:
                api_service.service_started.connect(lambda: info("后台API服务已启动"))
            else:
                warning("service_started信号不可用")
                
            if hasattr(api_service, 'service_stopped') and api_service.service_stopped is not None:
                api_service.service_stopped.connect(lambda: info("后台API服务已停止"))
            else:
                warning("service_stopped信号不可用")
            
            # 启动服务
            background_api_manager.start()
            
            log_system_event("后台服务启动", "后台API服务启动成功")
            
        except Exception as e:
            error(f"启动后台服务失败: {e}")
            log_system_event("后台服务启动失败", f"错误: {e}")
    
    def _on_background_api_success(self, api_name: str, data: dict):
        """后台API请求成功"""
        info(f"后台API请求成功: {api_name}")
        log_system_event("后台API成功", f"接口: {api_name}")
    
    def _on_background_api_failed(self, api_name: str, error: str):
        """后台API请求失败"""
        warning(f"后台API请求失败: {api_name} - {error}")
        log_system_event("后台API失败", f"接口: {api_name}, 错误: {error}")
    
    def closeEvent(self, event):
        """程序关闭事件"""
        try:
            info("程序准备关闭，停止后台服务")
            
            # 停止后台API服务
            background_api_manager.stop()
            
            # 记录程序关闭
            log_system_event("应用关闭", "用户主动关闭应用程序")
            
            event.accept()
            
        except Exception as e:
            error(f"程序关闭处理失败: {e}")
            event.accept()

if __name__ == "__main__":
    import sys
    import platform
    import os
    
    def main():
        """应用程序主函数"""
        # 设置全局异常处理
        GlobalLogger.setup_exception_handling()
        
        app = QApplication(sys.argv)
        
        # 获取并记录设备唯一码和系统信息
        try:
            unique_id = get_unique_identifier()
            system_info = f"系统: {platform.system()} {platform.release()}, Python: {platform.python_version()}"
            log_system_event("应用启动", f"{system_info}, 设备唯一码: {unique_id}")
            info(f"系统信息: {system_info}")
            info(f"设备唯一码: {unique_id}")
        except Exception as e:
            warning(f"获取设备信息失败: {e}")
            log_system_event("应用启动", f"系统: {platform.system()}, Python: {platform.python_version()}, 设备唯一码: 获取失败")
        
        # 应用图标
        try:
            app.setWindowIcon(QIcon("images/gongju.png"))
            info("应用图标加载成功")
        except Exception as e:
            warning(f"应用图标加载失败: {e}")
        
        # 全局样式
        try:
            app.setStyleSheet(StyleGenerator.get_global_style())
            info("全局样式加载成功")
        except Exception as e:
            error(f"全局样式加载失败: {e}")
            # 使用默认样式继续运行
        
        try:
            window = MainWindow()
            window.show()
            info("主窗口显示成功")
            
            # 运行应用
            exit_code = app.exec()
            log_system_event("应用退出", f"退出代码: {exit_code}")
            return exit_code
            
        except Exception as e:
            critical(f"应用程序启动失败: {e}")
            return 1
    
    # 启动应用程序
    sys.exit(main())


