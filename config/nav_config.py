"""
导航配置文件 - 统一管理一级和二级导航数据
"""

# 导航总配置
NAV_CONFIG = {
    "primary": {},  # 将在下面填充
    "secondary": {}  # 将在下面填充
}

# 一级导航配置
NAV_PRIMARY_ITEMS = [
    {"icon": "💬", "text": "首页", "key": "home", "img": "images/tab-home.png"},
    {"icon": "🛠️", "text": "工具", "key": "tools", "img": "images/gongju.png"}
]

# 二级导航配置
NAV_SECONDARY_DATA = {
    "home": {
        "title": "首页",
        "show_header": False,
        "items": [
            {"name": "首页", "icon": "⚡", "description": "常用工具集合"},
            {"name": "最近使用", "icon": "🕒", "description": "最近访问的功能"},
            {"name": "联系我们", "icon": "❓", "description": "把需要开发的功能告诉我"},
            {"name": "关于软件", "icon": "⭐", "description": "我的收藏工具"},
         
        ]
    },

    "tools": {
        "title": "常用工具",
        "show_header": True,
        "items": [
            {
                "name": "文本处理",
                "icon": "📝",
                "description": "处理和分析文本",
                "children": [
                    {"name": "JSON格式化", "icon": "📋", "description": "美化和验证JSON"},
                    {"name": "文本对比", "icon": "📄", "description": "文本对比工具"},
                    {"name": "文件查找", "icon": "📂", "description": "文件内容查找"}
                ]
            },
            {
                "name": "编码转换",
                "icon": "🔤",
                "description": "各种编码和进制转换",
                "children": [
                    {"name": "加密解密", "icon": "🔐", "description": "编码/解码工具"},
                    {"name": "进制转换", "icon": "🔢", "description": "进制转换工具"},
                    {"name": "正则表达式", "icon": "🧪", "description": "正则表达式测试"}
                ]
            },
            {
                "name": "代码工具",
                "icon": "💻",
                "description": "开发辅助工具",
                "children": [
                    {"name": "代码格式化", "icon": "✨", "description": "代码美化格式化"},
                    {"name": "颜色选择器", "icon": "🎨", "description": "颜色代码转换"}
                ]
            },
            {
                "name": "媒体工具",
                "icon": "📥",
                "description": "音视频下载与提取",
                "children": [
                     {"name": "图片转换", "icon": "🖼️", "description": "图片格式转换、压缩"},
                    {"name": "截屏工具", "icon": "📸", "description": "截图与标注"},
                    {"name": "媒体下载", "icon": "📥", "description": "下载网页中的音视频"}
                ]
            },
            {
                "name": "二维码工具",
                "icon": "📱",
                "description": "二维码生成与识别",
                "children": [
                    {"name": "二维码工具", "icon": "📱", "description": "二维码生成与识别"}
                ]
            }
        ]
    }
}


def get_nav_primary_items():
    """获取一级导航配置"""
    return NAV_PRIMARY_ITEMS

def get_nav_secondary_data(nav_key):
    """获取指定导航键的二级数据"""
    return NAV_SECONDARY_DATA.get(nav_key, NAV_SECONDARY_DATA["home"])

def get_all_nav_keys():
    """获取所有导航键"""
    return [item["key"] for item in NAV_PRIMARY_ITEMS]


# 填充 NAV_CONFIG
NAV_CONFIG["primary"] = NAV_PRIMARY_ITEMS
NAV_CONFIG["secondary"] = NAV_SECONDARY_DATA
