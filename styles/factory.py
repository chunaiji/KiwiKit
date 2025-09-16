"""
样式化组件工厂 - 创建预设样式的 UI 组件
"""

from PySide6.QtWidgets import QComboBox, QPushButton, QLineEdit, QGroupBox, QTextEdit
from .widgets import ComboBoxStyles, ButtonStyles, LineEditStyles, GroupBoxStyles, TextEditStyles


class StyledWidgets:
    """样式化组件工厂类"""
    
    @staticmethod
    def create_enhanced_combo(items=None, current_index=0, object_name="enhanced_combo"):
        """
        创建增强样式的 ComboBox
        
        Args:
            items: 下拉选项列表
            current_index: 默认选中项索引
            object_name: 对象名称
            
        Returns:
            QComboBox: 配置好样式的 ComboBox
        """
        combo = QComboBox()
        combo.setObjectName(object_name)
        
        if items:
            combo.addItems(items)
            if 0 <= current_index < len(items):
                combo.setCurrentIndex(current_index)
        
        # 应用样式
        combo.setStyleSheet(ComboBoxStyles.get_enhanced_style(object_name))
        
        # 添加刷新样式的方法
        def refresh_styles():
            combo.setStyleSheet(ComboBoxStyles.get_enhanced_style(object_name))
        combo.refresh_styles = refresh_styles
        
        return combo

    @staticmethod
    def create_simple_combo(items=None, current_index=0, object_name="simple_combo"):
        """
        创建简洁样式的 ComboBox
        
        Args:
            items: 下拉选项列表
            current_index: 默认选中项索引  
            object_name: 对象名称
            
        Returns:
            QComboBox: 配置好样式的 ComboBox
        """
        combo = QComboBox()
        combo.setObjectName(object_name)
        
        if items:
            combo.addItems(items)
            if 0 <= current_index < len(items):
                combo.setCurrentIndex(current_index)
        
        # 应用样式
        combo.setStyleSheet(ComboBoxStyles.get_simple_style(object_name))
        return combo

    @staticmethod
    def create_primary_button(text, min_width=100):
        """
        创建主要样式按钮
        
        Args:
            text: 按钮文本
            min_width: 最小宽度
            
        Returns:
            QPushButton: 配置好样式的按钮
        """
        button = QPushButton(text)
        button.setMinimumWidth(min_width)
        button.setStyleSheet(ButtonStyles.get_primary_style())
        
        # 添加刷新样式的方法
        def refresh_styles():
            button.setStyleSheet(ButtonStyles.get_primary_style())
        button.refresh_styles = refresh_styles
        
        return button

    @staticmethod
    def create_secondary_button(text, min_width=100):
        """
        创建次要样式按钮
        
        Args:
            text: 按钮文本
            min_width: 最小宽度
            
        Returns:
            QPushButton: 配置好样式的按钮
        """
        button = QPushButton(text)
        button.setMinimumWidth(min_width)
        button.setStyleSheet(ButtonStyles.get_secondary_style())
        
        # 添加刷新样式的方法
        def refresh_styles():
            button.setStyleSheet(ButtonStyles.get_secondary_style())
        button.refresh_styles = refresh_styles
        
        return button

    @staticmethod
    def create_styled_line_edit(placeholder="", monospace=True):
        """
        创建样式化输入框
        
        Args:
            placeholder: 占位符文本
            monospace: 是否使用等宽字体
            
        Returns:
            QLineEdit: 配置好样式的输入框
        """
        line_edit = QLineEdit()
        if placeholder:
            line_edit.setPlaceholderText(placeholder)
        
        style = LineEditStyles.get_standard_style()
        if not monospace:
            # 移除等宽字体设置
            style = style.replace("font-family: 'Consolas', monospace;", "")
        
        line_edit.setStyleSheet(style)
        return line_edit

    @staticmethod
    def create_styled_group_box(title):
        """
        创建样式化分组框
        
        Args:
            title: 分组框标题
            
        Returns:
            QGroupBox: 配置好样式的分组框
        """
        group_box = QGroupBox(title)
        group_box.setStyleSheet(GroupBoxStyles.get_standard_style())
        return group_box

    @staticmethod
    def create_styled_text_edit(placeholder="", object_name="text_edit", style_type="standard"):
        """
        创建样式化文本编辑框
        
        Args:
            placeholder: 占位符文本
            object_name: 对象名称
            style_type: 样式类型 ("standard", "output", "code")
            
        Returns:
            QTextEdit: 配置好样式的文本编辑框
        """
        text_edit = QTextEdit()
        text_edit.setObjectName(object_name)
        
        if placeholder:
            text_edit.setPlaceholderText(placeholder)
        
        # 根据样式类型选择样式
        if style_type == "output":
            style = TextEditStyles.get_output_style(object_name)
            text_edit.setReadOnly(True)  # 输出样式默认只读
        elif style_type == "code":
            style = TextEditStyles.get_code_style(object_name)
        else:
            style = TextEditStyles.get_standard_style(object_name)
        
        text_edit.setStyleSheet(style)
        
        # 添加刷新样式的方法
        def refresh_styles():
            if style_type == "output":
                text_edit.setStyleSheet(TextEditStyles.get_output_style(object_name))
            elif style_type == "code":
                text_edit.setStyleSheet(TextEditStyles.get_code_style(object_name))
            else:
                text_edit.setStyleSheet(TextEditStyles.get_standard_style(object_name))
        text_edit.refresh_styles = refresh_styles
        
        return text_edit


# 便捷函数
def enhanced_combo(items=None, current_index=0, object_name="enhanced_combo"):
    """创建增强样式 ComboBox 的便捷函数"""
    return StyledWidgets.create_enhanced_combo(items, current_index, object_name)

def simple_combo(items=None, current_index=0, object_name="simple_combo"):
    """创建简洁样式 ComboBox 的便捷函数"""
    return StyledWidgets.create_simple_combo(items, current_index, object_name)

def primary_button(text, min_width=100):
    """创建主要按钮的便捷函数"""
    return StyledWidgets.create_primary_button(text, min_width)

def secondary_button(text, min_width=100):
    """创建次要按钮的便捷函数"""
    return StyledWidgets.create_secondary_button(text, min_width)

def styled_input(placeholder="", monospace=True):
    """创建样式化输入框的便捷函数"""
    return StyledWidgets.create_styled_line_edit(placeholder, monospace)

def styled_group(title):
    """创建样式化分组框的便捷函数"""
    return StyledWidgets.create_styled_group_box(title)

def styled_text_edit(placeholder="", object_name="text_edit", style_type="standard"):
    """创建样式化文本编辑框的便捷函数"""
    return StyledWidgets.create_styled_text_edit(placeholder, object_name, style_type)

def code_text_edit(placeholder="", object_name="code_edit"):
    """创建代码编辑器样式文本框的便捷函数"""
    return StyledWidgets.create_styled_text_edit(placeholder, object_name, "code")

def output_text_edit(placeholder="", object_name="text_output"):
    """创建输出样式文本框的便捷函数"""
    return StyledWidgets.create_styled_text_edit(placeholder, object_name, "output")
