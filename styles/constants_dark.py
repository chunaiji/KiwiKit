"""
深色风格样式常量配置
适用于夜间模式，统一管理深色UI风格
"""

class Colors:
    # 主色调（保持一致）
    WECHAT_GREEN = "#07c160"
    WECHAT_GREEN_HOVER = "#06ad56"
    WECHAT_GREEN_PRESSED = "#059748"

    # 背景色 - 深色风格
    BACKGROUND_PRIMARY = "#1f1f1f"        # 主背景（深黑灰）
    BACKGROUND_SECONDARY = "#2a2a2a"      # 次背景（偏黑）
    BACKGROUND_TERTIARY = "#333333"       # 内容区背景
    BACKGROUND_CHAT = "#1c1c1c"           # 聊天区域背景
    BACKGROUND_LIGHT = "#3a3a3a"          # 浅背景块（hover 或卡片）

    # 行背景交替色（用于列表条纹）
    ROW_BG_LIGHT = "#2a2a2a"
    ROW_BG_ALT = "#242424"

    # hover / 选中状态
    HOVER_GRAY = "#3c3c3c"
    SELECTED_BLUE = "#385470"            # 选中蓝（偏灰蓝）
    ACTIVE_GREEN = "#07c160"             # 激活绿色

    # 分隔线
    SEPARATOR_COLOR = "#444444"

    # 导航栏背景色
    NAV_PRIMARY_BG = "#121212"           # 左侧导航（微信风格深黑）
    NAV_SECONDARY_BG = "#1e1e1e"         # 中间面板（聊天/联系人区域）
    DARK_GRAY = "#2e2e2e"                # 用于 Header/标题

    # 文字颜色 - 深色友好
    TEXT_PRIMARY = "#ffffff"             # 主文字：白
    TEXT_SECONDARY = "#aaaaaa"           # 次文字：浅灰
    TEXT_TERTIARY = "#777777"            # 辅助文字：更灰
    TEXT_WHITE = "#ffffff"               # 白文字
    TEXT_GREEN = "#8de9c3"               # 微信绿文字（浅绿）

    # 边框颜色（用作按钮/模块边界）
    BORDER_LIGHT = "#3a3a3a"
    BORDER_MEDIUM = "#555555"

    # 聊天气泡颜色（保持对比度）
    BUBBLE_RECEIVED = "#2e2e2e"          # 接收气泡深灰
    BUBBLE_SENT = "#058f5a"              # 发送气泡暗绿

    # 在线/离线状态
    ONLINE_GREEN = "#07c160"
    OFFLINE_GRAY = "#666666"

class Sizes:
    # 复用原来的即可，无需修改
    FONT_HEADER = "14px"
    FONT_LARGE = "14px"
    FONT_MEDIUM = "13px"
    FONT_NORMAL = "12px"
    FONT_SMALL = "11px"

    MARGIN_TINY = "4px"
    MARGIN_SMALL = "8px"
    MARGIN_MEDIUM = "12px"
    MARGIN_LARGE = "16px"
    MARGIN_XL = "20px"

    PADDING_TINY = "4px"
    PADDING_SMALL = "8px"
    PADDING_MEDIUM = "12px"
    PADDING_LARGE = "16px"

    RADIUS_TINY = "2px"
    RADIUS_SMALL = "4px"
    RADIUS_MEDIUM = "6px"
    RADIUS_LARGE = "8px"

    NAV_PRIMARY_WIDTH = "64px"
    NAV_SECONDARY_WIDTH = "260px"
    HEADER_HEIGHT = "38px"
    CHAT_INPUT_HEIGHT = "54px"

    AVATAR_SMALL = "20px"
    AVATAR_MEDIUM = "30px"
    AVATAR_LARGE = "40px"

    LIST_ITEM_HEIGHT = "62px"
    NAV_ITEM_HEIGHT = "50px"

class Shadows:
    LIGHT = "0 2px 8px rgba(0,0,0,0.5)"
    MEDIUM = "0 2px 8px rgba(0,0,0,0.6)"
    HEAVY = "0 2px 12px rgba(0,0,0,0.7)"
