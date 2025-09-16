"""
通用组件样式定义
"""


class ComboBoxStyles:
    """ComboBox 样式集合"""
    
    @staticmethod
    def get_enhanced_style(object_name="enhanced_combo"):
        """
        获取增强版 ComboBox 样式
        
        Args:
            object_name: 对象名称，用于样式选择器
            
        Returns:
            str: 完整的 QSS 样式字符串
        """
        from .constants import Colors  # 动态导入，确保获取最新的颜色
        return f"""
            QComboBox#{object_name} {{
                padding: 8px 12px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                color: {Colors.TEXT_PRIMARY};
                background-color: {Colors.BACKGROUND_LIGHT};
                min-width: 120px;
                min-height: 20px;
                padding-right: 30px;
                selection-background-color: {Colors.WECHAT_GREEN};
                selection-color: white;
            }}

            QComboBox#{object_name}:hover {{
                border-color: {Colors.WECHAT_GREEN};
                background-color: #f0f8f6;
                border-width: 2px;
            }}

            QComboBox#{object_name}:focus {{
                border-color: #06a050;
                background-color: #e8f3ea;
                outline: none;
                border-width: 2px;
            }}

            QComboBox#{object_name}:pressed {{
                background-color: #d4f3dc;
                border-color: #059940;
            }}

            QComboBox#{object_name}:disabled {{
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_SECONDARY};
                border-color: {Colors.BORDER_LIGHT};
            }}

            QComboBox#{object_name}::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 25px;
                border: none;
                border-left: 1px solid {Colors.BORDER_LIGHT};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background-color: transparent;
            }}

            QComboBox#{object_name}::drop-down:hover {{
                background-color: rgba(7, 193, 96, 0.1);
                border-left-color: {Colors.WECHAT_GREEN};
            }}

            QComboBox#{object_name}::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {Colors.TEXT_SECONDARY};
                margin-right: 3px;
            }}

            QComboBox#{object_name}::down-arrow:hover {{
                border-top-color: {Colors.WECHAT_GREEN};
            }}

            QComboBox#{object_name}::down-arrow:disabled {{
                border-top-color: {Colors.TEXT_SECONDARY};
            }}

            QComboBox#{object_name} QAbstractItemView {{
                border: 1px solid {Colors.WECHAT_GREEN};
                border-radius: 6px;
                background-color: {Colors.BACKGROUND_LIGHT};
                selection-background-color: {Colors.WECHAT_GREEN};
                selection-color: white;
                padding: 4px;
                outline: none;
                font-size: 13px;
                font-weight: 500;
                show-decoration-selected: 1;
            }}

            QComboBox#{object_name} QAbstractItemView::item {{
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                margin: 1px;
                min-height: 20px;
            }}

            QComboBox#{object_name} QAbstractItemView::item:hover {{
                background-color: rgba(7, 193, 96, 0.1);
                color: {Colors.TEXT_PRIMARY};
            }}

            QComboBox#{object_name} QAbstractItemView::item:selected {{
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                font-weight: bold;
            }}

            QComboBox#{object_name} QAbstractItemView::item:selected:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
                color: white;
            }}
        """

    @staticmethod
    def get_simple_style(object_name="simple_combo"):
        """
        获取简洁版 ComboBox 样式
        
        Args:
            object_name: 对象名称，用于样式选择器
            
        Returns:
            str: 简洁的 QSS 样式字符串
        """
        from .constants import Colors  # 动态导入，确保获取最新的颜色
        return f"""
            QComboBox#{object_name} {{
                padding: 6px 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                background-color: {Colors.BACKGROUND_TERTIARY};
                selection-background-color: {Colors.WECHAT_GREEN};
                min-width: 80px;
            }}
            
            QComboBox#{object_name}:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            
            QComboBox#{object_name}::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox#{object_name}::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {Colors.TEXT_SECONDARY};
                margin-right: 5px;
            }}
        """

    @staticmethod
    def apply_enhanced_style(combo_box, object_name="enhanced_combo"):
        """
        为 ComboBox 应用增强样式
        
        Args:
            combo_box: QComboBox 实例
            object_name: 对象名称
        """
        combo_box.setObjectName(object_name)
        combo_box.setStyleSheet(ComboBoxStyles.get_enhanced_style(object_name))

    @staticmethod
    def apply_simple_style(combo_box, object_name="simple_combo"):
        """
        为 ComboBox 应用简洁样式
        
        Args:
            combo_box: QComboBox 实例
            object_name: 对象名称
        """
        combo_box.setObjectName(object_name)
        combo_box.setStyleSheet(ComboBoxStyles.get_simple_style(object_name))


class ButtonStyles:
    """按钮样式集合"""
    
    @staticmethod
    def get_primary_style():
        """获取主要按钮样式"""
        from .constants import Colors  # 动态导入，确保获取最新的颜色
        return f"""
            QPushButton {{
                padding: 8px 16px;
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.WECHAT_GREEN_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_SECONDARY};
            }}
        """

    @staticmethod
    def get_secondary_style():
        """获取次要按钮样式"""
        from .constants import Colors  # 动态导入，确保获取最新的颜色
        return f"""
            QPushButton {{
                padding: 8px 16px;
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {Colors.HOVER_GRAY};
                border-color: {Colors.WECHAT_GREEN};
            }}
            QPushButton:pressed {{
                background-color: {Colors.BORDER_LIGHT};
            }}
        """


class LineEditStyles:
    """输入框样式集合"""
    
    @staticmethod
    def get_standard_style():
        """获取标准输入框样式"""
        from .constants import Colors  # 动态导入，确保获取最新的颜色
        return f"""
            QLineEdit {{
                padding: 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {Colors.WECHAT_GREEN};
                border-width: 2px;
            }}
            QLineEdit:disabled {{
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_SECONDARY};
            }}
        """


class TextEditStyles:
    """文本编辑框样式集合"""
    
    @staticmethod
    def get_standard_style(object_name="text_edit"):
        """获取标准 QTextEdit 样式"""
        from .constants import Colors  # 动态导入，确保获取最新的颜色
        return f"""
            QTextEdit#{object_name} {{
                background-color: {Colors.BACKGROUND_LIGHT};
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                line-height: 1.4;
                color: {Colors.TEXT_PRIMARY};
            }}

            QTextEdit#{object_name}:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}

            QTextEdit#{object_name}:disabled {{
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_SECONDARY};
                border-color: {Colors.BORDER_LIGHT};
            }}
        """
    
    @staticmethod
    def get_output_style(object_name="text_output"):
        """获取输出文本框样式（只读）"""
        from .constants import Colors  # 动态导入，确保获取最新的颜色
        return f"""
            QTextEdit#{object_name} {{
                background-color: #f8f9fa;
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                line-height: 1.4;
                color: #2d3748;
            }}

            QTextEdit#{object_name}:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
        """
    
    @staticmethod
    def get_code_style(object_name="code_edit"):
        """获取代码编辑器样式"""
        from .constants import Colors  # 动态导入，确保获取最新的颜色
        return f"""
            QTextEdit#{object_name} {{
                background-color: #282c34;
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 6px;
                padding: 12px;
                font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                line-height: 1.5;
                color: #abb2bf;
            }}

            QTextEdit#{object_name}:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
        """


class GroupBoxStyles:
    """分组框样式集合"""
    
    @staticmethod
    def get_standard_style():
        """获取标准分组框样式"""
        from .constants import Colors  # 动态导入，确保获取最新的颜色
        return f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """

class CheckBoxStyles:
    """复选框样式集合"""

    @staticmethod
    def get_standard_style(object_name="standard_checkbox"):
        from .constants import Colors
        return f"""
            QCheckBox#{object_name} {{
                spacing: 8px;
                font-size: 13px;
                color: {Colors.TEXT_PRIMARY};
            }}

            QCheckBox#{object_name}::indicator {{
                width: 18px;
                height: 18px;
                border: 1.5px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                background: {Colors.BACKGROUND_LIGHT};
            }}

            QCheckBox#{object_name}::indicator:hover {{
                border-color: {Colors.WECHAT_GREEN};
                background: #e8f3ea;
            }}

            QCheckBox#{object_name}::indicator:checked {{
                background-color: {Colors.WECHAT_GREEN};
                border-color: {Colors.WECHAT_GREEN};
                /* 移除SVG图标引用，使用纯色背景表示选中状态 */
            }}

            QCheckBox#{object_name}::indicator:checked:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
                border-color: {Colors.WECHAT_GREEN_HOVER};
            }}

            QCheckBox#{object_name}:disabled {{
                color: {Colors.TEXT_SECONDARY};
            }}

            QCheckBox#{object_name}::indicator:disabled {{
                border-color: {Colors.BORDER_LIGHT};
                background: {Colors.BACKGROUND_SECONDARY};
            }}
        """

    @staticmethod
    def apply_standard_style(checkbox, object_name="standard_checkbox"):
        checkbox.setObjectName(object_name)
        checkbox.setStyleSheet(CheckBoxStyles.get_standard_style(object_name))



class RadioButtonStyles:
    """单选按钮样式集合"""

    @staticmethod
    def get_standard_style(object_name="standard_radiobutton"):
        """获取标准单选按钮样式"""
        from .constants import Colors
        return f"""
            QRadioButton#{object_name} {{
                spacing: 8px;
                font-size: 13px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QRadioButton#{object_name}::indicator {{
                width: 18px;
                height: 18px;
                border: 1.5px solid {Colors.BORDER_LIGHT};
                border-radius: 9px;
                background: {Colors.BACKGROUND_LIGHT};
            }}
            QRadioButton#{object_name}::indicator:hover {{
                border-color: {Colors.WECHAT_GREEN};
                background: #e8f3ea;
            }}
            QRadioButton#{object_name}::indicator:checked {{
                background-color: {Colors.WECHAT_GREEN};
                border-color: {Colors.WECHAT_GREEN};
            }}
            QRadioButton#{object_name}::indicator:checked:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
                border-color: {Colors.WECHAT_GREEN_HOVER};
            }}
            QRadioButton#{object_name}:disabled {{
                color: {Colors.TEXT_SECONDARY};
            }}
            QRadioButton#{object_name}::indicator:disabled {{
                border-color: {Colors.BORDER_LIGHT};
                background: {Colors.BACKGROUND_SECONDARY};
            }}
        """

    @staticmethod
    def apply_standard_style(radiobutton, object_name="standard_radiobutton"):
        radiobutton.setObjectName(object_name)
        radiobutton.setStyleSheet(RadioButtonStyles.get_standard_style(object_name))


class SliderStyles:
    """滑块样式集合"""

    @staticmethod
    def get_standard_style(object_name="horizontal_slider"):
        """获取水平滑块样式"""
        from .constants import Colors
        return f"""
            QSlider#{object_name} {{
                min-height: 20px;
            }}

            QSlider#{object_name}::groove:horizontal {{
                border: 1px solid {Colors.BORDER_LIGHT};
                height: 6px;
                background: {Colors.BACKGROUND_LIGHT};
                border-radius: 3px;
            }}

            QSlider#{object_name}::handle:horizontal {{
                background: {Colors.WECHAT_GREEN};
                border: 1px solid {Colors.WECHAT_GREEN_HOVER};
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }}

            QSlider#{object_name}::handle:horizontal:hover {{
                background: {Colors.WECHAT_GREEN_HOVER};
                border: 1px solid {Colors.WECHAT_GREEN};
            }}

            QSlider#{object_name}:disabled {{
                background: {Colors.BACKGROUND_SECONDARY};
            }}
        """

    @staticmethod
    def apply_horizontal_style(slider, object_name="horizontal_slider"):
        slider.setObjectName(object_name)
        slider.setStyleSheet(SliderStyles.get_standard_style(object_name))


class ProgressBarStyles:
    """进度条样式集合"""

    @staticmethod
    def get_standard_style(object_name="progress_bar"):
        """获取标准进度条样式"""
        from .constants import Colors
        return f"""
            QProgressBar#{object_name} {{
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 6px;
                background-color: {Colors.BACKGROUND_LIGHT};
                text-align: center;
                font-size: 13px;
                color: {Colors.TEXT_PRIMARY};
            }}

            QProgressBar#{object_name}::chunk {{
                background-color: {Colors.WECHAT_GREEN};
                border-radius: 6px;
            }}

            QProgressBar#{object_name}:disabled {{
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_SECONDARY};
            }}
        """

    @staticmethod
    def apply_standard_style(progress_bar, object_name="progress_bar"):
        progress_bar.setObjectName(object_name)
        progress_bar.setStyleSheet(ProgressBarStyles.get_standard_style(object_name))


class TabWidgetStyles:
    """标签页控件样式集合"""

    @staticmethod
    def get_standard_style(object_name="tab_widget"):
        """获取标准 QTabWidget 样式"""
        from .constants import Colors
        return f"""
            QTabWidget#{object_name} {{
                font-size: 13px;
                color: {Colors.TEXT_PRIMARY};
            }}

            QTabBar#{object_name}::tab {{
                background: {Colors.BACKGROUND_LIGHT};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-bottom: none;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }}

            QTabBar#{object_name}::tab:selected {{
                background: {Colors.WECHAT_GREEN};
                color: white;
                font-weight: bold;
            }}

            QTabBar#{object_name}::tab:hover {{
                background: {Colors.WECHAT_GREEN_HOVER};
                color: white;
            }}

            QTabBar#{object_name}::tab:disabled {{
                color: {Colors.TEXT_SECONDARY};
            }}

            QTabWidget#{object_name}::pane {{
                border: 1px solid {Colors.BORDER_LIGHT};
                top: -1px;
                border-radius: 6px;
                background: {Colors.BACKGROUND_LIGHT};
            }}
        """

    @staticmethod
    def apply_standard_style(tab_widget, object_name="tab_widget"):
        tab_widget.setObjectName(object_name)
        tab_widget.setStyleSheet(TabWidgetStyles.get_standard_style(object_name))

class WindowStyles:
    """窗口及整体界面样式集合"""

    @staticmethod
    def get_main_window_style():
        """
        获取主窗口的统一样式，包含背景色、字体等基础设置
        """
        from .constants import Colors
        return f"""
            QWidget {{
                background-color: {Colors.BACKGROUND_LIGHT};
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                color: {Colors.TEXT_PRIMARY};
            }}

            /* 设置全局按钮的默认样式 */
            QPushButton {{
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
            }}

            /* 输入框统一样式 */
            QLineEdit, QTextEdit {{
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 6px;
                padding: 8px;
            }}

            /* 滚动条基础样式 */
            QScrollBar:vertical {{
                border: none;
                background: {Colors.BACKGROUND_SECONDARY};
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical {{
                background: {Colors.WECHAT_GREEN};
                min-height: 20px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {Colors.WECHAT_GREEN_HOVER};
            }}

            /* 标签和标题颜色统一 */
            QLabel, QGroupBox {{
                color: {Colors.TEXT_PRIMARY};
            }}
        """

    @staticmethod
    def apply_main_window_style(widget):
        """
        为窗口或顶层控件应用主窗口样式

        Args:
            widget: QMainWindow 或 QWidget 实例
        """
        widget.setStyleSheet(WindowStyles.get_main_window_style())


class QWidgetStyles:
    """QWidget 及其子控件的统一样式封装"""

    @staticmethod
    def get_default_style():
        """
        获取基础 QWidget 样式，适合大多数面板或窗口
        """
        from .constants import Colors
        return f"""
            QWidget {{
                background-color: {Colors.BACKGROUND_LIGHT};
                color: {Colors.TEXT_PRIMARY};
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                border-radius: 8px;
            }}

            /* QLabel 样式 */
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
            }}

            /* QPushButton 统一样式 */
            QPushButton {{
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
            }}

            QPushButton:pressed {{
                background-color: {Colors.WECHAT_GREEN_PRESSED};
            }}

            QPushButton:disabled {{
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_SECONDARY};
            }}

            /* 输入框样式 */
            QLineEdit, QTextEdit {{
                background-color: white;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 6px;
                padding: 6px 8px;
                font-family: "Consolas", monospace;
            }}

            QLineEdit:focus, QTextEdit:focus {{
                border-color: {Colors.WECHAT_GREEN};
                border-width: 2px;
            }}

            /* 滚动条样式 */
            QScrollBar:vertical {{
                background: {Colors.BACKGROUND_SECONDARY};
                width: 10px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical {{
                background: {Colors.WECHAT_GREEN};
                border-radius: 4px;
                min-height: 20px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {Colors.WECHAT_GREEN_HOVER};
            }}
        """

    @staticmethod
    def apply_default_style(widget):
        """
        应用默认 QWidget 样式
        
        Args:
            widget: QWidget 或其子类实例
        """
        widget.setStyleSheet(QWidgetStyles.get_default_style())


class LayoutAndDialogStyles:
    """布局和消息框公共封装"""

    @staticmethod
    def create_vbox_layout(parent=None, margin=0, spacing=5):
        """
        创建带默认边距和间距的垂直布局
        
        Args:
            parent: 父控件
            margin: 边距
            spacing: 控件间距
            
        Returns:
            QVBoxLayout 实例
        """
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(spacing)
        return layout

    @staticmethod
    def create_hbox_layout(parent=None, margin=0, spacing=5):
        """
        创建带默认边距和间距的水平布局
        
        Args:
            parent: 父控件
            margin: 边距
            spacing: 控件间距
            
        Returns:
            QHBoxLayout 实例
        """
        from PySide6.QtWidgets import QHBoxLayout
        layout = QHBoxLayout(parent)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(spacing)
        return layout

    @staticmethod
    def create_splitter(orientation=None, parent=None, handle_width=6):
        """
        创建带默认handle宽度的分割控件
        
        Args:
            orientation: Qt.Horizontal 或 Qt.Vertical
            parent: 父控件
            handle_width: 分割条宽度
            
        Returns:
            QSplitter 实例
        """
        from PySide6.QtWidgets import QSplitter
        from PySide6.QtCore import Qt
        if orientation is None:
            orientation = Qt.Horizontal
        splitter = QSplitter(orientation, parent)
        splitter.setHandleWidth(handle_width)
        return splitter

    class MessageBox:
        """消息框统一封装"""

        @staticmethod
        def info(parent, title, message):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(parent, title, message)

        @staticmethod
        def warning(parent, title, message):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(parent, title, message)

        @staticmethod
        def error(parent, title, message):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(parent, title, message)

# ScrollViewStyles.py
class ScrollViewStyles:
    """ScrollView 样式集合"""

    @staticmethod
    def get_hidden_scrollbar_style():
        """隐藏滚动条的样式"""
        return """
            QScrollBar:vertical, QScrollBar:horizontal {
                background: transparent;
                width: 0px;
                height: 0px;
            }
        """

    @staticmethod
    def get_custom_scrollbar_style(track_color="#f0f0f0", thumb_color="#06a050", radius=3):
        """自定义滚动条样式"""
        return f"""
            QScrollBar:vertical {{
                background: {track_color};
                width: 8px;
                margin: 2px 0;
                border-radius: {radius}px;
            }}

            QScrollBar::handle:vertical {{
                background: {thumb_color};
                min-height: 20px;
                border-radius: {radius}px;
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QScrollBar:horizontal {{
                background: {track_color};
                height: 8px;
                margin: 0 2px;
                border-radius: {radius}px;
            }}

            QScrollBar::handle:horizontal {{
                background: {thumb_color};
                min-width: 20px;
                border-radius: {radius}px;
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
            }}
        """

    @staticmethod
    def apply_hidden_style(scroll_view):
        scroll_view.setStyleSheet(ScrollViewStyles.get_hidden_scrollbar_style())

    @staticmethod
    def apply_custom_style(scroll_view, track_color="#f0f0f0", thumb_color="#06a050", radius=3):
        scroll_view.setStyleSheet(
            ScrollViewStyles.get_custom_scrollbar_style(track_color, thumb_color, radius)
        )


# MessageBoxStyles.py

class MessageBoxStyles:
    """统一 QMessageBox 样式的静态类"""

    @staticmethod
    def get_base_style():
        from .constants import Colors
        return f"""
            QMessageBox {{
                background-color: {Colors.BACKGROUND_LIGHT};
                font-size: 14px;
                color: {Colors.TEXT_PRIMARY};
            }}

            QMessageBox QLabel {{
                font-size: 14px;
                font-weight: 500;
                padding: 10px;
            }}

            QMessageBox QPushButton {{
                padding: 6px 14px;
                border-radius: 5px;
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                min-width: 80px;
            }}

            QMessageBox QPushButton:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
            }}

            QMessageBox QPushButton:pressed {{
                background-color: {Colors.WECHAT_GREEN_ACTIVE};
            }}
        """

    @staticmethod
    def get_success_style():
        from .constants import Colors
        return f"""
            QMessageBox {{
                background-color: #f6ffed;
                border: 1px solid #b7eb8f;
            }}

            QMessageBox QLabel {{
                color: #389e0d;
                font-weight: bold;
                font-size: 14px;
            }}

            QMessageBox QPushButton {{
                background-color: #52c41a;
                color: white;
                border-radius: 5px;
                padding: 6px 14px;
            }}

            QMessageBox QPushButton:hover {{
                background-color: #73d13d;
            }}
        """

    @staticmethod
    def get_error_style():
        return """
            QMessageBox {
                background-color: #fff1f0;
                border: 1px solid #ffa39e;
            }

            QMessageBox QLabel {
                color: #cf1322;
                font-weight: bold;
                font-size: 14px;
            }

            QMessageBox QPushButton {
                background-color: #ff4d4f;
                color: white;
                border-radius: 5px;
                padding: 6px 14px;
            }

            QMessageBox QPushButton:hover {
                background-color: #ff7875;
            }
        """

    @staticmethod
    def apply_style(message_box):
        message_box.setStyleSheet(MessageBoxStyles.get_base_style())

    @staticmethod
    def apply_success_style(message_box):
        message_box.setStyleSheet(MessageBoxStyles.get_success_style())

    @staticmethod
    def apply_error_style(message_box):
        message_box.setStyleSheet(MessageBoxStyles.get_error_style())

class SpinBoxStyles:
    """QSpinBox 样式集合"""
    
    @staticmethod
    def get_enhanced_style(object_name="enhanced_spinbox"):
        """
        获取增强版 QSpinBox 样式
        
        Args:
            object_name: 对象名称，用于样式选择器
            
        Returns:
            str: 完整的 QSS 样式字符串
        """
        from .constants import Colors  # 动态导入，确保获取最新的颜色
        return f"""
            QSpinBox#{object_name} {{
                padding: 8px 12px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                color: {Colors.TEXT_PRIMARY};
                background-color: {Colors.BACKGROUND_LIGHT};
                min-width: 120px;
                min-height: 20px;
                padding-right: 30px;
                selection-background-color: {Colors.WECHAT_GREEN};
                selection-color: white;
            }}

            QSpinBox#{object_name}:hover {{
                border-color: {Colors.WECHAT_GREEN};
                background-color: #f0f8f6;
                border-width: 2px;
            }}

            QSpinBox#{object_name}:focus {{
                border-color: #06a050;
                background-color: #e8f3ea;
                outline: none;
                border-width: 2px;
            }}

            QSpinBox#{object_name}:pressed {{
                background-color: #d4f3dc;
                border-color: #059940;
            }}

            QSpinBox#{object_name}:disabled {{
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_SECONDARY};
                border-color: {Colors.BORDER_LIGHT};
            }}

            QSpinBox#{object_name}::up-button {{
                border: none;
                background-color: transparent;
                width: 16px;
                height: 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}

            QSpinBox#{object_name}::up-button:hover {{
                background-color: rgba(7, 193, 96, 0.1);
                border-color: {Colors.WECHAT_GREEN};
            }}

            QSpinBox#{object_name}::up-button:pressed {{
                background-color: #d4f3dc;
                border-color: #059940;
            }}

            QSpinBox#{object_name}::down-button {{
                border: none;
                background-color: transparent;
                width: 16px;
                height: 16px;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
            }}

            QSpinBox#{object_name}::down-button:hover {{
                background-color: rgba(7, 193, 96, 0.1);
                border-color: {Colors.WECHAT_GREEN};
            }}

            QSpinBox#{object_name}::down-button:pressed {{
                background-color: #d4f3dc;
                border-color: #059940;
            }}

            QSpinBox#{object_name} QAbstractSpinBox {{
                border: none;
                background-color: transparent;
                padding: 0 4px;
                font-size: 13px;
                font-weight: 500;
                color: {Colors.TEXT_PRIMARY};
                selection-background-color: {Colors.WECHAT_GREEN};
                selection-color: white;
            }}
            
            QSpinBox#{object_name} QAbstractSpinBox:focus {{
                outline: none;
                border-color: {Colors.WECHAT_GREEN};
            }}
        """
