"""
样式常量配置文件
定义了应用的所有样式常量，便于统一管理和修改
"""

# 颜色配置 - 微信风格
class Colors:
    # 微信主色调
    WECHAT_GREEN = "#07c160"
    WECHAT_GREEN_HOVER = "#06ad56"
    WECHAT_GREEN_PRESSED = "#059748"
    
    # 主要颜色
    PRIMARY = "#07c160"               # 主色调
    SECONDARY = "#f7f7f7"             # 次要颜色
    
    # 渐变颜色
    GRADIENT_PRIMARY = "#2e2e2e"      # 主渐变色
    GRADIENT_SECONDARY = "#ffffff"    # 次渐变色
    
    # 背景色 - 微信风格
    BACKGROUND_PRIMARY = "#f7f7f7"      # 微信主背景色
    BACKGROUND_SECONDARY = "#e0e0e0"    # 微信次要背景色
    BACKGROUND_TERTIARY = "#ffffff"     # 微信白色背景
    BACKGROUND_CHAT = "#f5f5f5"        # 微信聊天背景
    BACKGROUND_LIGHT = "#c8c8c8"       # 微信浅灰背景
    BACKGROUND_MEDIUM = "#e0e0e0"      # 微信中等背景
    BACKGROUND_WHITE = "#ffffff"       # 白色背景
    ROW_BG_LIGHT = "#ffffff"
    ROW_BG_ALT = "#f7f7f7"
    
    SEPARATOR_COLOR = "#e0e0e0"
    
    # 导航栏背景色
    NAV_PRIMARY_BG = "#393939"         # 微信左侧深灰色
    NAV_SECONDARY_BG = "#ffffff"       # 微信中间白色
    DARK_GRAY = "#2e2e2e"              # 深灰色（用于header等）
    
    # 文字颜色 - 微信风格
    TEXT_PRIMARY = "#191919"           # 微信主要文字色
    TEXT_SECONDARY = "#888888"         # 微信次要文字色
    TEXT_TERTIARY = "#b2b2b2"         # 微信辅助文字色
    TEXT_WHITE = "#ffffff"            # 白色文字
    TEXT_GREEN = "#576b95"            # 微信蓝色文字
    TEXT_HEADER = "#191919"           # 头部文字颜色
    
    # 边框颜色
    BORDER_LIGHT = "#e7e7e7"          # 微信浅边框
    BORDER_MEDIUM = "#d9d9d9"         # 微信中等边框
    BORDER_DARK = "#c0c0c0"           # 微信深边框
    
    # 聊天气泡颜色
    BUBBLE_RECEIVED = "#ffffff"        # 接收消息气泡（白色）
    BUBBLE_SENT = "#95ec69"           # 发送消息气泡（微信绿）
    
    # 状态颜色
    ONLINE_GREEN = "#07c160"          # 在线状态绿色
    OFFLINE_GRAY = "#b2b2b2"          # 离线状态灰色
    TEXT_SUCCESS = "#52c41a"          # 成功状态绿色
    TEXT_ERROR = "#ff4d4f"            # 错误状态红色
    
    # 悬浮和选中状态
    HOVER_GRAY = "#f0f0f0"           # 悬浮灰色
    SELECTED_BLUE = "#c7edff"        # 选中蓝色
    ACTIVE_GREEN = "#07c160"         # 激活绿色

# 尺寸配置 - 微信风格
class Sizes:
    # 字体大小 - 微信风格
    FONT_HEADER = "14px"              # 微信标题字体
    FONT_LARGE = "14px"               # 微信大字体
    FONT_MEDIUM = "13px"              # 微信中等字体
    FONT_NORMAL = "12px"              # 微信常规字体
    FONT_SMALL = "11px"               # 微信小字体
    
    # 边距 - 微信风格（更紧凑）
    MARGIN_TINY = "4px"
    MARGIN_SMALL = "8px"
    MARGIN_MEDIUM = "12px"
    MARGIN_LARGE = "16px"
    MARGIN_XL = "20px"
    MARGIN_XXL = "24px"               # 超大边距
    
    # 内边距
    PADDING_TINY = "4px"
    PADDING_SMALL = "8px"
    PADDING_MEDIUM = "12px"
    PADDING_LARGE = "16px"
    
    # 圆角 - 微信风格（更小的圆角）
    RADIUS_TINY = "2px"
    RADIUS_SMALL = "4px"
    RADIUS_MEDIUM = "6px"
    RADIUS_LARGE = "8px"
    
    # 组件尺寸 - 微信风格
    NAV_PRIMARY_WIDTH = "64px"        # 微信左侧导航宽度
    NAV_SECONDARY_WIDTH = "260px"     # 微信中间列表宽度
    HEADER_HEIGHT = "38px"            # 微信标题栏高度
    CHAT_INPUT_HEIGHT = "54px"        # 微信输入框高度
    
    # 最小宽度
    MIN_WIDTH_NAV_PRIMARY = "64px"    # 左侧导航最小宽度
    MIN_WIDTH_NAV_SECONDARY = "260px" # 中间导航最小宽度
    MIN_WIDTH_CONTENT = "400px"       # 内容区最小宽度
    
    # 头像尺寸
    AVATAR_SMALL = "20px"
    AVATAR_MEDIUM = "30px"
    AVATAR_LARGE = "40px"
    
    # 列表项高度
    LIST_ITEM_HEIGHT = "62px"         # 微信列表项高度
    NAV_ITEM_HEIGHT = "50px"          # 微信导航项高度

# 阴影配置
class Shadows:
    LIGHT = "0 2px 8px rgba(0,0,0,0.04)"
    MEDIUM = "0 2px 8px rgba(0,0,0,0.06)"
    HEAVY = "0 2px 12px rgba(0,0,0,0.04)"
