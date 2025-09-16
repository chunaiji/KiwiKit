"""
图片加载工具
"""

from PySide6.QtCore import QObject, Signal, QThread, QTimer, Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtWidgets import QLabel
from utils.http_client import HttpClient, HttpResponse


class ImageLoader(QObject):
    """网络图片加载器"""
    
    # 信号定义
    image_loaded = Signal(QPixmap)
    load_failed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.http_client = HttpClient()
        self.http_client.request_finished.connect(self._on_response)
        self.http_client.request_error.connect(self._on_error)
    
    def load_image(self, url: str) -> None:
        """加载网络图片"""
        self.http_client.get(url)
    
    def _on_response(self, response: HttpResponse) -> None:
        """处理响应"""
        if response.status_code == 200:
            pixmap = QPixmap()
            if pixmap.loadFromData(response.data):
                self.image_loaded.emit(pixmap)
            else:
                self.load_failed.emit("Failed to parse image data")
        else:
            self.load_failed.emit(f"HTTP {response.status_code}")
    
    def _on_error(self, error: str) -> None:
        """处理错误"""
        self.load_failed.emit(error)


class RoundImageLabel(QLabel):
    """圆形图片标签"""
    
    def __init__(self, size: int = 40):
        super().__init__()
        self.image_size = size
        self.setFixedSize(size, size)
        self.original_pixmap = None
        self.image_loader = ImageLoader()
        self.image_loader.image_loaded.connect(self._on_image_loaded)
        self.image_loader.load_failed.connect(self._on_load_failed)
        
        # 默认样式
        self.setStyleSheet(f"""
            QLabel {{
                background: #07c160;
                border-radius: {size//2}px;
                color: white;
                font-size: {size//2}px;
                font-weight: bold;
                border: 2px solid #ffffff;
            }}
        """)
        self.setText("👤")
        self.setAlignment(Qt.AlignCenter)
    
    def load_from_url(self, url: str) -> None:
        """从URL加载图片"""
        self.image_loader.load_image(url)
    
    def _on_image_loaded(self, pixmap: QPixmap) -> None:
        """图片加载成功"""
        self.original_pixmap = pixmap
        self._update_round_image()
    
    def _on_load_failed(self, error: str) -> None:
        """图片加载失败"""
        print(f"Image load failed: {error}")
        # 保持默认头像
    
    def _update_round_image(self) -> None:
        """更新圆形图片"""
        if not self.original_pixmap:
            return
        
        # 创建圆形遮罩
        size = self.image_size
        round_pixmap = QPixmap(size, size)
        round_pixmap.fill(Qt.transparent)
        
        painter = QPainter(round_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆形路径
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        
        # 绘制缩放后的图片
        scaled_pixmap = self.original_pixmap.scaled(
            size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )
        
        # 居中绘制
        x = (size - scaled_pixmap.width()) // 2
        y = (size - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()
        
        # 设置圆形图片
        self.setPixmap(round_pixmap)
        self.setStyleSheet(f"""
            QLabel {{
                border-radius: {size//2}px;
                border: 2px solid #ffffff;
            }}
        """)
