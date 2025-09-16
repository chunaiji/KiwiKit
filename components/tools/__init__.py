"""
Tools模块初始化文件
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from .json_formatter import JSONFormatter
from .file_search import FileSearchWidget
from .encode_decode import EncodeDecodeSuite
from .regex_formatter import RegexFormatterWidget
from .file_diff import FileDiffTool
from .code_formatter import CodeFormatterTool
from .color_picker import ColorPickerWidget

# 检查 base_converter.py 中是否有主要的转换器类
try:
    from .base_converter import BaseConverter
except ImportError:
    # 如果导入失败，创建一个占位符
    class BaseConverter(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)
            label = QLabel("进制转换工具加载失败")
            layout.addWidget(label)

# 导入图片转换工具
try:
    from .image_conver import ImageConverterWidget
except ImportError:
    # 如果导入失败，创建一个占位符
    class ImageConverterWidget(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)
            label = QLabel("图片转换工具需要安装 Pillow 库\n请运行: pip install Pillow")
            label.setWordWrap(True)
            layout.addWidget(label)

# 导入媒体下载工具
try:
    from .media_download import MediaDownloaderWidget
except ImportError:
    # 如果导入失败，创建一个占位符
    class MediaDownloaderWidget(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)
            label = QLabel("媒体下载工具加载失败")
            layout.addWidget(label)

# 导入二维码工具
try:
    from .qr_tool import QrToolWidget as QRToolWidget
except ImportError as e:
    print(f"⚠️  QR工具部分功能不可用: {e}")
    # 如果导入失败，创建一个占位符
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
    
    class QRToolWidget(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)
            label = QLabel("二维码工具需要安装依赖库\n请运行: pip install pillow qrcode[pil]")
            label.setWordWrap(True)
            label.setStyleSheet("color: orange; padding: 20px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;")
            layout.addWidget(label)

# 导入截屏工具
try:
    from .screen_shot import ScreenshotWidget
except ImportError as e:
    print(f"⚠️  截屏工具不可用: {e}")
    # 如果导入失败，创建一个占位符 (QWidget 已在上面导入)
    class ScreenshotWidget(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)
            label = QLabel("截屏工具加载失败\n某些依赖库可能缺失")
            label.setWordWrap(True)
            label.setStyleSheet("color: red; padding: 20px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px;")
            layout.addWidget(label)

__all__ = ['JSONFormatter', 'ImageConverterWidget', 'FileSearchWidget', 'EncodeDecodeSuite', 'RegexFormatterWidget', 'FileDiffTool', 'CodeFormatterTool', 'BaseConverter', 'ColorPickerWidget', 'MediaDownloaderWidget', 'QRToolWidget', 'ScreenshotWidget']
