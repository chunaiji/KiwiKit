"""
应用程序配置
"""

# 应用程序基本信息
ORGANIZATION = "KiwiKit"
APPLICATION_NAME = "奇异工具包"
APPLICATION_VERSION = "1.0.0"

# 主题配置
THEME = "light"  # 默认主题

class AppConfig:
    """应用程序配置类"""
    
    # 应用信息
    APP_NAME = "奇异工具包"
    VERSION = "1.0.0"
    
    # 窗口设置
    MIN_WINDOW_WIDTH = 1200
    MIN_WINDOW_HEIGHT = 800
    DEFAULT_WINDOW_WIDTH = 1400
    DEFAULT_WINDOW_HEIGHT = 900
    
    # 组件尺寸
    NAV_PRIMARY_WIDTH = 80
    NAV_SECONDARY_WIDTH = 280
    HEADER_HEIGHT = 60
    
    # 布局比例 [左侧导航, 中间导航, 右侧内容]
    LAYOUT_RATIO = [0, 0, 1]  # 固定宽度的导航栏，内容区域自适应
    
    # API配置
    API_BASE_URL = "https://api.example.com"  # 请根据实际情况修改
    API_TIMEOUT = 30  # 超时时间（秒）
    API_RETRY_COUNT = 3  # 重试次数
    
    # 其他设置
    DEBUG = False


def get_theme_config():
    """获取当前主题配置"""
    return {
        "name": THEME,
        "colors": {
            "primary": "#007ACC",
            "secondary": "#6C757D", 
            "success": "#28A745",
            "warning": "#FFC107",
            "danger": "#DC3545",
            "background": "#FFFFFF" if THEME == "light" else "#2D2D30",
            "text": "#212529" if THEME == "light" else "#FFFFFF"
        }
    }


def reset_all_styles():
    """重置所有样式"""
    try:
        from styles.factory import StyledWidgets
        # 样式重置逻辑，不需要打印
        return True
    except Exception as e:
        # 可以记录到日志，但不打印
        return False


def apply_all_styles():
    """应用所有样式"""
    try:
        from styles.factory import StyledWidgets
        # 样式应用逻辑，不需要打印
        return True
    except Exception as e:
        # 可以记录到日志，但不打印
        return False
