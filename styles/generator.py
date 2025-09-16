"""
样式生成器
基于样式常量生成具体的样式字符串
"""

from .constants import Colors, Sizes, Shadows

class StyleGenerator:
    @staticmethod
    def header_style():
        """头部样式"""
        return f"""
            background: {Colors.BACKGROUND_PRIMARY}; 
            border-bottom: 1px solid {Colors.BORDER_LIGHT}; 
            height: {Sizes.HEADER_HEIGHT};
        """
    
    @staticmethod
    def header_label_style():
        """头部标签样式"""
        return f"""
            font-size: {Sizes.FONT_HEADER}; 
            font-weight: bold; 
            color: {Colors.TEXT_HEADER};
        """
    
    @staticmethod
    def nav_primary_style():
        """左侧导航栏样式"""
        return f"""
            background: {Colors.BACKGROUND_PRIMARY}; 
            border-right: 1px solid {Colors.BORDER_LIGHT}; 
            min-width: {Sizes.MIN_WIDTH_NAV_PRIMARY};
        """
    
    @staticmethod
    def nav_primary_avatar_style():
        """左侧导航栏头像样式"""
        return f"""
            background: {Colors.PRIMARY}; 
            border-radius: {Sizes.RADIUS_LARGE}; 
            margin: {Sizes.MARGIN_LARGE}; 
            padding: {Sizes.PADDING_LARGE}; 
            font-size: {Sizes.FONT_MEDIUM};
        """
    
    @staticmethod
    def nav_primary_item_style():
        """左侧导航栏项目样式"""
        return f"""
            margin: {Sizes.MARGIN_SMALL}; 
            font-size: {Sizes.FONT_NORMAL}; 
            color: {Colors.TEXT_SECONDARY}; 
            border-radius: {Sizes.RADIUS_SMALL}; 
            padding: {Sizes.PADDING_SMALL} 0; 
            background: {Colors.SECONDARY};
        """
    
    @staticmethod
    def nav_primary_settings_style():
        """左侧导航栏设置样式"""
        return f"""
            margin: {Sizes.MARGIN_SMALL}; 
            font-size: {Sizes.FONT_SMALL}; 
            color: {Colors.TEXT_TERTIARY}; 
            border-radius: {Sizes.RADIUS_SMALL}; 
            padding: {Sizes.PADDING_SMALL} 0; 
            background: {Colors.SECONDARY};
        """
    
    @staticmethod
    def nav_secondary_style():
        """中间导航栏样式"""
        return f"""
            background: {Colors.NAV_SECONDARY_BG}; 
            border-right: 1px solid {Colors.BORDER_LIGHT}; 
            min-width: {Sizes.MIN_WIDTH_NAV_SECONDARY};
        """
    
    @staticmethod
    def nav_secondary_item_style():
        """中间导航栏项目样式"""
        return f"""
            margin: {Sizes.MARGIN_MEDIUM}; 
            font-size: {Sizes.FONT_NORMAL}; 
            color: {Colors.TEXT_SECONDARY}; 
            border-radius: {Sizes.RADIUS_SMALL}; 
            padding: {Sizes.PADDING_SMALL} 0; 
            background: {Colors.SECONDARY};
        """
    
    @staticmethod
    def nav_secondary_group_style():
        """中间导航栏分组样式"""
        return f"""
            margin: {Sizes.MARGIN_MEDIUM}; 
            font-size: {Sizes.FONT_SMALL}; 
            color: {Colors.TEXT_TERTIARY}; 
            border-radius: {Sizes.RADIUS_SMALL}; 
            padding: {Sizes.PADDING_SMALL} 0; 
            background: {Colors.SECONDARY};
        """
    
    @staticmethod
    def content_area_style():
        """主内容区域样式"""
        return f"""
            background: {Colors.BACKGROUND_WHITE}; 
            min-width: {Sizes.MIN_WIDTH_CONTENT}; 
            border-top-right-radius: {Sizes.RADIUS_LARGE}; 
            border-bottom-right-radius: {Sizes.RADIUS_LARGE};
        """
    
    @staticmethod
    def content_label_style():
        """主内容区域标签样式"""
        return f"""
            margin: {Sizes.MARGIN_XXL}; 
            font-size: {Sizes.FONT_LARGE}; 
            color: {Colors.TEXT_PRIMARY}; 
            border-radius: {Sizes.RADIUS_MEDIUM}; 
            background: {Colors.BACKGROUND_SECONDARY};
        """
    
    @staticmethod
    def get_global_style():
        """获取全局应用样式"""
        return f"""
            QMainWindow {{
                background: {Colors.BACKGROUND_PRIMARY};
                color: {Colors.TEXT_PRIMARY};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            
            QWidget {{
                background: {Colors.BACKGROUND_PRIMARY};
                color: {Colors.TEXT_PRIMARY};
            }}
            
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {Colors.BACKGROUND_LIGHT};
                width: 8px;
                border-radius: 4px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {Colors.BORDER_MEDIUM};
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {Colors.BORDER_DARK};
            }}
        """
