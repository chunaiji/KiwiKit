"""
QR Code Generator & Reader Widget
- Features:
  1. 生成二维码（多种风格，支持中心 logo）
  2. 识别本地图片中的二维码并显示内容
  3. 批量生成：粘贴多条文本（逗号/换行/空格分隔），分别生成二维码图片

依赖：
    pip install pillow qrcode[pil] pyzbar PySide6

注意：pyzbar 需要系统安装 zbar（Linux/macOS/Windows 有对应安装包）。
"""

import os
import io
from PIL import Image, ImageDraw, ImageOps
import qrcode
from qrcode.constants import ERROR_CORRECT_H

# 尝试导入 pyzbar，如果失败则禁用相关功能
try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except ImportError:
    print("⚠️  pyzbar 不可用，二维码识别功能将被禁用")
    PYZBAR_AVAILABLE = False
    decode = None

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QMessageBox, QTextEdit, QComboBox, QSpinBox, QSlider,
    QFrame, QApplication, QColorDialog, QGroupBox, QCheckBox
)
from PySide6.QtGui import QPixmap, QImage, QFont, QColor
from PySide6.QtCore import Qt

from components.base_content import BaseContent
from components.base_bootstrap import Container, Row, Col, Spacer
from styles.constants import Colors
from styles.widgets import (
    ButtonStyles, LineEditStyles, GroupBoxStyles, ComboBoxStyles,
    TextEditStyles, SliderStyles, CheckBoxStyles, SpinBoxStyles
)
from utils.logger import get_logger, log_errors, log_performance, log_user_action, error, info, warning


def pil2qimage(img: Image.Image) -> QImage:
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    if img.mode == "RGB":
        data = img.tobytes("raw", "RGB")
        qimage = QImage(data, img.width, img.height, QImage.Format_RGB888)
    else:
        data = img.tobytes("raw", "RGBA")
        qimage = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
    return qimage


# ----------------- QR 图像生成器 -----------------

@log_performance
@log_errors
def generate_qr_image(data: str, size: int = 800, fg_color="#000000", bg_color="#ffffff",
                      style: str = "Standard", logo_path: str = None, logo_scale: float = 0.2) -> Image.Image:
    """生成二维码图片，返回 PIL.Image。
    style: "Standard", "Rounded", "ColorBlocks", "EyeLess", "WithLogo"（WithLogo 只是额外 paste）
    """
    # 使用 qrcode 生成 matrix
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()  # 2D list of bool

    module_count = len(matrix)
    # 计算单模块像素大小
    border = 4
    box = max(1, int(size / (module_count + 2 * border)))
    img_size = box * (module_count + 2 * border)

    # 初始空白背景
    img = Image.new("RGBA", (img_size, img_size), bg_color)
    draw = ImageDraw.Draw(img)

    # 绘制不同风格
    if style in ("Standard", "WithLogo", "ColorBlocks", "EyeLess"):
        # 标准方块绘制
        for r in range(module_count):
            for c in range(module_count):
                if matrix[r][c]:
                    x = (c + border) * box
                    y = (r + border) * box
                    if style == "EyeLess":
                        # 绘制无外眼风格：缩小角落的 finder patterns to look "eye-less" by filling normally but we'll remove typical eyes? simple approach: draw inner modules only
                        draw.rectangle([x, y, x + box - 1, y + box - 1], fill=fg_color)
                    else:
                        draw.rectangle([x, y, x + box - 1, y + box - 1], fill=fg_color)
    elif style == "Rounded":
        # 绘制圆角模块（circle modules）
        radius = box // 2
        for r in range(module_count):
            for c in range(module_count):
                if matrix[r][c]:
                    cx = (c + border) * box + box // 2
                    cy = (r + border) * box + box // 2
                    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=fg_color)
    else:
        # fallback standard
        for r in range(module_count):
            for c in range(module_count):
                if matrix[r][c]:
                    x = (c + border) * box
                    y = (r + border) * box
                    draw.rectangle([x, y, x + box - 1, y + box - 1], fill=fg_color)

    # 如果需要特殊色块风格，可以在后面做局部处理（这里基础实现）

    # 可选：嵌入 logo
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # logo 最大占比
            max_logo_w = int(img_size * logo_scale)
            max_logo_h = int(img_size * logo_scale)
            logo.thumbnail((max_logo_w, max_logo_h), Image.ANTIALIAS)
            # 在中心粘贴，并在 logo 背后加白色圆角底以提高可见性
            lx, ly = logo.size
            center = ((img_size - lx) // 2, (img_size - ly) // 2)
            # optional white background with rounded rect
            pad = int(min(lx, ly) * 0.15)
            bg_w = lx + pad * 2
            bg_h = ly + pad * 2
            bg_img = Image.new("RGBA", (bg_w, bg_h), (255, 255, 255, 230))
            # rounded mask
            mask = Image.new("L", (bg_w, bg_h), 0)
            mdraw = ImageDraw.Draw(mask)
            mdraw.rounded_rectangle([(0, 0), (bg_w, bg_h)], radius=int(min(bg_w, bg_h) * 0.2), fill=255)
            bg_pos = (center[0] - pad, center[1] - pad)
            img.paste(bg_img, bg_pos, mask=mask)
            img.paste(logo, center, mask=logo)
        except Exception:
            pass

    # 转换为 RGBA 完成
    return img


# ----------------- QR 识别 -----------------

@log_errors
def decode_qr_from_path(path: str):
    """
    从图片路径识别二维码
    返回识别到的文本列表，如果出错返回错误信息列表
    """
    try:
        logger = get_logger('QrTool')
        logger.info(f"🔍 开始识别二维码图片: {path}")
        
        # 检查 pyzbar 是否可用
        if not PYZBAR_AVAILABLE:
            error_msg = "ERROR: pyzbar 库不可用，无法识别二维码。请在开发环境中安装 pyzbar。"
            logger.error(f"❌ {error_msg}")
            return [error_msg]
        
        # 检查文件是否存在
        if not os.path.exists(path):
            error_msg = f"ERROR: 文件不存在: {path}"
            logger.error(f"❌ {error_msg}")
            return [error_msg]
        
        logger.info(f"📁 图片文件存在，准备打开...")
        
        # 使用PIL打开图片
        im = Image.open(path).convert("RGBA")
        logger.info(f"✅ PIL 成功打开图片，尺寸: {im.size}")
        
        # 使用pyzbar解码
        logger.info(f"🔄 开始使用 pyzbar 解码二维码...")
        results = decode(im)
        logger.info(f"📊 pyzbar 解码结果数量: {len(results)}")
        
        if not results:
            info_msg = "未在图片中找到二维码"
            logger.info(f"ℹ️ {info_msg}")
            return [info_msg]
        
        # 提取解码的文本
        texts = []
        for i, r in enumerate(results):
            logger.info(f"🔤 处理第 {i+1} 个二维码结果...")
            try:
                text = r.data.decode('utf-8')
                texts.append(text)
                logger.info(f"✅ UTF-8 解码成功: {text[:50]}...")
            except UnicodeDecodeError:
                logger.warning(f"⚠️ UTF-8 解码失败，尝试 GBK...")
                # 如果UTF-8解码失败，尝试其他编码
                try:
                    text = r.data.decode('gbk')
                    texts.append(text)
                    logger.info(f"✅ GBK 解码成功: {text[:50]}...")
                except:
                    fallback_text = f"识别到二维码但解码失败: {r.data}"
                    texts.append(fallback_text)
                    logger.warning(f"⚠️ 所有编码都失败: {fallback_text}")
        
        logger.info(f"🎉 二维码识别完成，共识别到 {len(texts)} 个内容")
        return texts
        
    except ImportError as e:
        error_msg = f"ERROR: 缺少依赖库 - {e}. 请安装: pip install pyzbar"
        logger.error(f"❌ 依赖库导入失败: {error_msg}")
        return [error_msg]
    except Exception as e:
        return [f"ERROR: 识别失败 - {e}"]


# ----------------- GUI Widget -----------------
class QrToolWidget(BaseContent):
    def __init__(self):
        try:
            info("🔄 开始初始化二维码工具组件...")
            info(f"🐍 当前Python版本和环境信息")
            info(f"📍 QR工具初始化位置: {__file__}")
            
            self.loaded_image_path = None
            self.latest_generated_image = None
            self.output_folder = None
            self.logger = get_logger('QrTool')
            
            # 检查依赖库
            info("🔍 开始检查二维码工具依赖库...")
            self._check_dependencies()
            info("✅ 二维码工具依赖库检查完成")
            
            # 创建主要内容组件
            info("🎨 开始创建二维码工具界面组件...")
            content_widget = self._create_content_widget()
            info("✅ 二维码工具界面组件创建完成")
            
            # 初始化基类
            info("🏗️ 开始初始化BaseContent基类...")
            super().__init__(title="二维码生成与识别", content_widget=content_widget)
            info("✅ 二维码工具组件完全初始化成功")
            
        except ImportError as e:
            error(f"❌ 二维码工具初始化失败 - 缺少依赖库: {e}")
            error(f"📋 依赖库详细信息: {str(e)}")
            log_system_event("模块加载失败", f"QR工具缺少依赖: {e}")
            raise
        except Exception as e:
            error(f"❌ 二维码工具初始化失败 - 未知错误: {e}")
            error(f"📋 错误详细信息: {str(e)}")
            log_system_event("模块加载失败", f"QR工具初始化异常: {e}")
            raise
    
    def _check_dependencies(self):
        """检查必要的依赖库"""
        try:
            info("🔍 检查 qrcode 模块...")
            import qrcode
            info(f"✅ qrcode 模块导入成功")
            
            info("🔍 检查 PIL (Pillow) 模块...")
            import PIL
            info(f"✅ PIL 模块导入成功，版本: {PIL.__version__}")
            
            if PYZBAR_AVAILABLE:
                info("🔍 检查 pyzbar 模块...")
                import pyzbar
                info(f"✅ pyzbar 模块导入成功")
                
                info("🔍 检查 pyzbar.pyzbar.decode 函数...")
                # decode 已在模块顶部导入或设置为 None
                info(f"✅ pyzbar decode 函数导入成功")
                
                info("🎉 二维码工具所有依赖库检查通过！")
            else:
                info("⚠️  pyzbar 不可用，二维码识别功能将被禁用")
                info("🎉 二维码生成功能可以正常使用！")
            
        except ImportError as e:
            error(f"❌ 二维码工具依赖库检查失败: {e}")
            error(f"📋 失败的模块: {e.name if hasattr(e, 'name') else '未知'}")
            error(f"📋 错误详情: {str(e)}")
            # 只要求必要的依赖，pyzbar 是可选的
            raise ImportError(f"缺少必要的依赖库: {e}. 请安装: pip install pillow qrcode[pil]")

    def _create_content_widget(self):
        """创建主要内容区域组件 - 使用Bootstrap风格的网格布局"""

        # 🔍 二维码识别组件
        recognize_group = QGroupBox("🔍 二维码识别")
        recognize_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        recognize_layout = QVBoxLayout(recognize_group)

        if PYZBAR_AVAILABLE:
            self.load_img_btn = QPushButton("📂 选择图片识别")
            self.load_img_btn.setMinimumWidth(140)
            self.load_img_btn.setStyleSheet(ButtonStyles.get_secondary_style())
            self.load_img_btn.clicked.connect(self._choose_image_for_decode)

            self.decode_btn = QPushButton("🔍 识别二维码")
            self.decode_btn.setMinimumWidth(120)
            self.decode_btn.setStyleSheet(ButtonStyles.get_primary_style())
            self.decode_btn.clicked.connect(self._decode_image)
            self.decode_btn.setEnabled(False)
        else:
            # pyzbar 不可用时显示提示
            self.load_img_btn = QPushButton("⚠️  二维码识别不可用")
            self.load_img_btn.setMinimumWidth(140)
            self.load_img_btn.setStyleSheet("QPushButton { background-color: #f59e0b; color: white; padding: 8px; border-radius: 4px; }")
            self.load_img_btn.setEnabled(False)
            self.load_img_btn.setToolTip("需要安装 pyzbar 库才能使用二维码识别功能")

            self.decode_btn = QPushButton("❌ 功能不可用")
            self.decode_btn.setMinimumWidth(120)
            self.decode_btn.setStyleSheet("QPushButton { background-color: #ef4444; color: white; padding: 8px; border-radius: 4px; }")
            self.decode_btn.setEnabled(False)

        self.decode_result = QLineEdit()
        self.decode_result.setObjectName("decode_result")
        self.decode_result.setStyleSheet(LineEditStyles.get_standard_style())
        self.decode_result.setPlaceholderText("识别结果显示在这里")
        self.decode_result.setReadOnly(True)

        # Row 1: 识别操作行 (Bootstrap col-3 + col-3 + col-6)
        recognize_row = Row(
            Col(self.load_img_btn, span=3),
            Col(self.decode_btn, span=3),
            Col(self.decode_result, span=6),
            spacing=15
        )
        recognize_layout.addLayout(recognize_row)

        # ⚙️ 生成设置组件
        gen_group = QGroupBox("⚙️ 二维码生成设置")
        gen_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        gen_layout = QVBoxLayout(gen_group)

        # 文本输入组件（60%宽度）
        self.data_input = QLineEdit()
        self.data_input.setObjectName("data_input")
        self.data_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.data_input.setPlaceholderText("请输入要生成的文本（单条），例如：https://example.com")

        # 样式和尺寸设置组件（40%宽度）
        style_widget = QWidget()
        style_layout = QHBoxLayout(style_widget)
        style_layout.setContentsMargins(0, 0, 0, 0)
        style_layout.addWidget(QLabel("风格:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Standard", "Rounded", "ColorBlocks", "EyeLess", "WithLogo"])
        self.style_combo.setObjectName("style_combo")
        self.style_combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("style_combo"))
        style_layout.addWidget(self.style_combo)
        style_layout.addSpacing(15)
        style_layout.addWidget(QLabel("尺寸:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(128, 2000)
        self.size_spin.setValue(800)
        self.size_spin.setFixedWidth(80)
        self.size_spin.setObjectName("size_spin")
        self.size_spin.setStyleSheet(SpinBoxStyles.get_enhanced_style("size_spin"))
        style_layout.addWidget(self.size_spin)
        # 不添加stretch，让控件紧凑排列

        # Row 2: 文本输入和样式设置同行 (Bootstrap col-7 + col-5)
        text_and_style_row = Row(
            Col(self.data_input, span=7),         # 文本输入占约60%宽度
            Col(style_widget, span=5),            # 样式设置占约40%宽度
            spacing=15
        )
        gen_layout.addLayout(text_and_style_row)

        # 🎨 高级设置组件
        advanced_group = QGroupBox("🎨 高级设置")
        advanced_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        advanced_layout = QVBoxLayout(advanced_group)

        # Logo设置组件
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setObjectName("logo_path_input")
        self.logo_path_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.logo_path_input.setPlaceholderText("可选：中心 logo 路径")
        self.logo_btn = QPushButton("📂 选择Logo")
        self.logo_btn.setFixedWidth(100)
        self.logo_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.logo_btn.clicked.connect(self._choose_logo)
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(60, 60)
        self.logo_preview.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0; border-radius: 4px;")
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setText("预览")
        logo_layout.addWidget(self.logo_path_input)
        logo_layout.addWidget(self.logo_btn)
        logo_layout.addWidget(self.logo_preview)

        # 颜色设置组件
        color_widget = QWidget()
        color_layout = QHBoxLayout(color_widget)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.addWidget(QLabel("前景色:"))
        self.fg_input = QLineEdit("#000000")
        self.fg_input.setObjectName("fg_input")
        self.fg_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.fg_input.setFixedWidth(80)
        self.fg_color_preview = QLabel()
        self.fg_color_preview.setFixedSize(25, 25)
        self.fg_color_preview.setCursor(Qt.PointingHandCursor)
        self.fg_color_preview.setStyleSheet("border: 1px solid #ccc; background: #000000; border-radius: 4px;")
        color_layout.addWidget(self.fg_input)
        color_layout.addWidget(self.fg_color_preview)
        color_layout.addSpacing(20)
        color_layout.addWidget(QLabel("背景色:"))
        self.bg_input = QLineEdit("#FFFFFF")
        self.bg_input.setObjectName("bg_input")
        self.bg_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.bg_input.setFixedWidth(80)
        self.bg_color_preview = QLabel()
        self.bg_color_preview.setFixedSize(25, 25)
        self.bg_color_preview.setCursor(Qt.PointingHandCursor)
        self.bg_color_preview.setStyleSheet("border: 1px solid #ccc; background: #FFFFFF; border-radius: 4px;")
        color_layout.addWidget(self.bg_input)
        color_layout.addWidget(self.bg_color_preview)
        color_layout.addStretch()

        # Logo比例设置组件（60%宽度）
        scale_widget = QWidget()
        scale_layout = QHBoxLayout(scale_widget)
        scale_layout.setContentsMargins(0, 0, 0, 0)
        scale_layout.addWidget(QLabel("Logo 占比:"))
        self.logo_scale = QSlider(Qt.Horizontal)
        self.logo_scale.setObjectName("logo_scale")
        self.logo_scale.setStyleSheet(SliderStyles.get_standard_style("logo_scale"))
        self.logo_scale.setRange(5, 50)
        self.logo_scale.setValue(20)
        scale_layout.addWidget(self.logo_scale)
        scale_layout.addStretch()

        # 操作按钮组件（40%宽度）
        advanced_buttons_widget = QWidget()
        advanced_buttons_layout = QHBoxLayout(advanced_buttons_widget)
        advanced_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.generate_btn = QPushButton("⚡ 生成并预览")
        self.generate_btn.setFixedHeight(36)
        self.generate_btn.setMinimumWidth(110)
        self.generate_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.generate_btn.clicked.connect(self._generate_preview)

        self.save_generated_btn = QPushButton("💾 保存二维码")
        self.save_generated_btn.setFixedHeight(36)
        self.save_generated_btn.setMinimumWidth(110)
        self.save_generated_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.save_generated_btn.clicked.connect(self._save_generated)
        self.save_generated_btn.setEnabled(False)
        
        advanced_buttons_layout.addWidget(self.generate_btn)
        advanced_buttons_layout.addWidget(self.save_generated_btn)
        # 不添加stretch，让按钮紧凑排列

        # Row 4: Logo设置行 (Bootstrap col-12)
        logo_row = Row(
            Col(logo_widget, span=12),
            spacing=15
        )
        advanced_layout.addLayout(logo_row)
        
        # Row 5: 颜色设置行 (Bootstrap col-12)
        color_row = Row(
            Col(color_widget, span=12),
            spacing=15
        )
        advanced_layout.addLayout(color_row)
        
        # Row 6: Logo比例设置和操作按钮同行 (Bootstrap col-7 + col-5)
        scale_and_buttons_row = Row(
            Col(scale_widget, span=7),                    # Logo比例占约60%宽度
            Col(advanced_buttons_widget, span=5),         # 操作按钮占约40%宽度
            spacing=15
        )
        advanced_layout.addLayout(scale_and_buttons_row)



        # 📦 批量生成组件
        batch_group = QGroupBox("📦 批量生成")
        batch_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        batch_layout = QVBoxLayout(batch_group)

        batch_label = QLabel("📝 输入多条文本（支持逗号、换行或空格分隔）:")
        batch_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        batch_layout.addWidget(batch_label)

        self.batch_input = QTextEdit()
        self.batch_input.setObjectName("batch_input")
        self.batch_input.setStyleSheet(TextEditStyles.get_standard_style("batch_input"))
        self.batch_input.setMinimumHeight(120)
        self.batch_input.setPlaceholderText("示例：\nhttps://example1.com\nhttps://example2.com\n或用逗号分隔...")
        batch_layout.addWidget(self.batch_input)

        # 批量操作按钮组件（40%宽度）
        batch_btn_widget = QWidget()
        batch_btn_layout = QHBoxLayout(batch_btn_widget)
        batch_btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.batch_gen_btn = QPushButton("🚀 批量生成")
        self.batch_gen_btn.setMinimumWidth(110)
        self.batch_gen_btn.setFixedHeight(36)
        self.batch_gen_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.batch_gen_btn.clicked.connect(self._batch_generate)
        self.batch_gen_btn.setEnabled(False)  # 初始状态不可用，需要先选择文件夹
        
        self.batch_folder_btn = QPushButton("📁 选择文件夹")
        self.batch_folder_btn.setMinimumWidth(110)
        self.batch_folder_btn.setFixedHeight(36)
        self.batch_folder_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.batch_folder_btn.clicked.connect(self._choose_output_folder)
        
        batch_btn_layout.addWidget(self.batch_gen_btn)
        batch_btn_layout.addWidget(self.batch_folder_btn)
        # 不添加stretch，让按钮紧凑排列

        # 文件夹显示框（60%宽度）
        self.output_folder_display = QLineEdit()
        self.output_folder_display.setObjectName("output_folder_display")
        self.output_folder_display.setStyleSheet(LineEditStyles.get_standard_style())
        self.output_folder_display.setReadOnly(True)
        self.output_folder_display.setPlaceholderText("选择输出文件夹...")

        # 批量操作控制行 (Bootstrap col-5 + col-7)
        batch_controls_row = Row(
            Col(batch_btn_widget, span=5),           # 按钮组占约40%宽度
            Col(self.output_folder_display, span=7), # 文件夹显示占约60%宽度
            spacing=15
        )
        batch_layout.addLayout(batch_controls_row)

        # 👁️ 预览组件
        preview_group = QGroupBox("👁️ 二维码预览")
        preview_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(f"""
            QLabel {{
                background-color: white; 
                border: 2px solid {Colors.BORDER_LIGHT}; 
                border-radius: 8px;
                padding: 15px;
                color: {Colors.TEXT_SECONDARY};
                font-size: 14px;
            }}
        """)
        self.preview_label.setText("🖼️ 点击生成预览二维码")
        preview_layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        # 使用Bootstrap容器组织所有内容
        content_widget = Container(
            Row(Col(recognize_group, span=12), spacing=15),           # 识别区域
            Row(Col(gen_group, span=12), spacing=15),                 # 生成设置区域
            Row(Col(advanced_group, span=12), spacing=15),            # 高级设置区域（包含操作按钮）
            Row(
                Col(batch_group, span=6),                             # 批量生成区域
                Col(preview_group, span=6),                           # 预览区域
                spacing=20
            ),
            spacing=20,
            margins=(15, 15, 15, 15)
        )
        
        # 设置颜色选择器事件
        self.fg_color_preview.mousePressEvent = lambda e: self._pick_color(self.fg_input, self.fg_color_preview)
        self.bg_color_preview.mousePressEvent = lambda e: self._pick_color(self.bg_input, self.bg_color_preview)
        
        # 状态标签已由BaseContent类处理
        return content_widget
    




    # ---------- handlers ----------
    def _choose_image_for_decode(self):
        if not PYZBAR_AVAILABLE:
            self._show_msg("二维码识别功能不可用，需要安装 pyzbar 库", "warning")
            return
            
        log_user_action("选择图片进行二维码识别")
        p, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tiff)")
        if p:
            self.loaded_image_path = p
            if PYZBAR_AVAILABLE:
                self.decode_btn.setEnabled(True)
            self.status_label.setText(f"已选择: {os.path.basename(p)}")
            info(f"用户选择了图片文件: {p}")

            # 将选择的图片显示在预览框中
            try:
                img = Image.open(p)
                img.thumbnail((300, 300))  # 缩放到适合预览
                qimg = pil2qimage(img)
                pix = QPixmap.fromImage(qimg).scaled(
                    self.preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(pix)
                info("图片预览加载成功")
            except Exception as e:
                error(f"图片预览加载失败: {e}")
                self._show_msg(f"图片加载失败: {e}")
        else:
            info("用户取消了图片选择")


    def _pick_color(self, line_edit: QLineEdit, preview_label: QLabel):
        current_color = line_edit.text().strip()
        print(f"Before pick: {current_color}")
        initial = QColor(current_color) if QColor(current_color).isValid() else QColor("#000000")

        color = QColorDialog.getColor(initial, self, "选择颜色")
        if color.isValid():
            hex_color = color.name()
            print(f"Picked color: {hex_color}")
            line_edit.setText(hex_color)
            print(f"After setText: {line_edit.text()}")
            preview_label.setStyleSheet(f"border: 1px solid #ccc; background: {hex_color};")
            if self.latest_generated_image:
                self._generate_preview()


    def _decode_image(self):
        if not PYZBAR_AVAILABLE:
            self._show_msg("二维码识别功能不可用，需要安装 pyzbar 库", "warning")
            return
            
        if not self.loaded_image_path:
            warning("尝试识别二维码但未选择图片")
            return
        
        log_user_action("开始识别二维码", f"文件: {self.loaded_image_path}")
        info(f"开始识别二维码: {self.loaded_image_path}")
        
        texts = decode_qr_from_path(self.loaded_image_path)
        if texts:
            result_text = "; ".join(texts)
            self.decode_result.setText(result_text)
            self.status_label.setText("识别完成")
            info(f"二维码识别成功，结果: {result_text}")
            log_user_action("二维码识别成功", f"识别到 {len(texts)} 个二维码")
        else:
            self.decode_result.setText("")
            self.status_label.setText("未识别到二维码或出错")
            warning(f"二维码识别失败或未找到二维码: {self.loaded_image_path}")

    def _update_color_preview(self, line_edit: QLineEdit, preview_label: QLabel):
        color = line_edit.text().strip()
        print(f"Updating color preview for {line_edit.objectName()} with color: {color}")  # <- 加调试
        if color.startswith("#") and len(color) in (4, 7):  # e.g. #FFF or #FFFFFF
            preview_label.setStyleSheet(f"border: 1px solid #ccc; background: {color};")




    def _choose_logo(self):
        p, _ = QFileDialog.getOpenFileName(self, "选择 logo 图片 (可选)", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tiff)")
        if p:
            self.logo_path_input.setText(p)
            try:
                img = Image.open(p)
                img.thumbnail((80, 80))
                qimg = pil2qimage(img)
                pix = QPixmap.fromImage(qimg)
                self.logo_preview.setPixmap(pix)
            except Exception as e:
                self._show_msg(f"Logo 预览失败: {e}")
            # 新增：上传 logo 后立即刷新二维码预览（如果已输入内容）
            if self.data_input.text().strip():
                self._generate_preview()



    @log_errors
    def _generate_preview(self):
        import os

        # 获取输入数据并校验
        data = self.data_input.text().strip()
        if not data:
            warning("尝试生成二维码但未输入内容")
            self._show_msg("请先输入要生成的内容（单条）")
            return

        log_user_action("生成二维码预览", f"内容长度: {len(data)}")
        info(f"开始生成二维码预览: {data[:50]}...")

        # 获取用户选择的样式和 logo 参数
        style = self.style_combo.currentText()

        fg = self.fg_input.text().strip() or "#000000"
        bg = self.bg_input.text().strip() or "#FFFFFF"

        logo = self.logo_path_input.text().strip() or None
        logo_exists = os.path.exists(logo) if logo else False
        logo_scale = self.logo_scale.value() / 100.0

        try:
            # 生成高质量预览图，使用动态尺寸以适应布局
            available_width = max(self.preview_label.width(), 350)
            available_height = max(self.preview_label.height(), 350)
            preview_size = min(available_width - 40, available_height - 40)  # 留出充足边距
            preview_size = max(preview_size, 250)  # 确保最小尺寸

            info(f"生成二维码参数 - 尺寸: {preview_size}, 样式: {style}, 前景色: {fg}, 背景色: {bg}")

            img = generate_qr_image(
                data,
                size=preview_size,
                fg_color=fg,
                bg_color=bg,
                style=style,
                logo_path=logo if logo_exists else None,
                logo_scale=logo_scale
            )

            # 保存当前预览图片（注意：保存时可用高分辨率重新生成）
            self.latest_generated_image = img

            # 显示在预览框中，确保完整显示
            qimg = pil2qimage(img)
            # 直接使用生成的尺寸，无需再次缩放
            pix = QPixmap.fromImage(qimg)
            self.preview_label.setPixmap(pix)

            self.save_generated_btn.setEnabled(True)
            self.status_label.setText("生成成功，预览已更新")
            
            info("二维码生成成功")
            log_user_action("二维码生成成功", f"样式: {style}, 尺寸: {preview_size}")

        except Exception as e:
            error(f"二维码生成失败: {e}")
            self._show_msg(f"生成失败: {e}")
            print(f"生成二维码异常: {e}")





    def _save_generated(self):
        if not self.latest_generated_image:
            self._show_msg("没有可保存的生成图片")
            return
        p, _ = QFileDialog.getSaveFileName(self, "保存二维码", "qrcode.png", "PNG files (*.png);;JPEG files (*.jpg *.jpeg)")
        if p:
            try:
                # 若保存为 JPEG 丢失 alpha，需要转换
                ext = os.path.splitext(p)[1].lower()
                img = self.latest_generated_image
                if ext in ('.jpg', '.jpeg'):
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[-1])
                    bg.save(p, quality=95)
                else:
                    img.save(p)
                self.status_label.setText(f"已保存: {p}")
            except Exception as e:
                self._show_msg(f"保存失败: {e}")

    def _choose_output_folder(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if d:
            self.output_folder = d
            self.output_folder_display.setText(d)
            # 选择文件夹后启用批量生成按钮
            self.batch_gen_btn.setEnabled(True)
            self.status_label.setText(f"输出文件夹已设置: {os.path.basename(d)}")
            log_user_action("设置批量生成输出文件夹", f"路径: {d}")
        else:
            # 取消选择时保持当前状态
            if not self.output_folder:
                self.batch_gen_btn.setEnabled(False)

    @log_errors
    @log_performance
    def _batch_generate(self):
        raw = self.batch_input.toPlainText().strip()
        if not raw:
            warning("尝试批量生成但未输入数据")
            self._show_msg("请先输入要批量生成的数据（多个条目）")
            return
        if not self.output_folder:
            warning("尝试批量生成但未选择输出文件夹")
            self._show_msg("请先选择输出文件夹")
            return
        
        log_user_action("开始批量生成二维码", f"输出文件夹: {self.output_folder}")
        info(f"开始批量生成二维码，输出到: {self.output_folder}")
        
        # split by comma, newline or whitespace
        parts = [p.strip() for p in raw.replace(',', '\n').split() if p.strip()]
        if not parts:
            warning("批量生成：未解析到任何有效项")
            self._show_msg("未解析到任何有效项")
            return
        
        info(f"解析到 {len(parts)} 个待生成项目")
        
        style = self.style_combo.currentText()
        size = int(self.size_spin.value())
        fg = self.fg_input.text().strip() or "#000000"
        bg = self.bg_input.text().strip() or "#FFFFFF"
        logo = self.logo_path_input.text().strip() or None
        logo_scale = self.logo_scale.value() / 100.0

        count = 0
        errors = []
        for i, item in enumerate(parts):
            try:
                img = generate_qr_image(item, size=size, fg_color=fg, bg_color=bg, style=style, logo_path=logo, logo_scale=logo_scale)
                # safe filename from item
                safe = ''.join(c for c in item if c.isalnum() or c in ('-', '_'))
                if not safe:
                    safe = f"item_{count}"
                fname = os.path.join(self.output_folder, f"{safe}.png")
                img.save(fname)
                count += 1
                info(f"批量生成进度: {i+1}/{len(parts)} - 已保存: {fname}")
            except Exception as e:
                error(f"批量生成第 {i+1} 项失败: {item} - {e}")
                errors.append((item, str(e)))
        
        success_msg = f"已生成 {count} 张二维码。" + (" 部分失败。" if errors else "")
        self._show_msg(success_msg)
        if errors:
            # 简单显示第一个错误
            error_msg = f"部分项失败示例: {errors[0][0]} -> {errors[0][1]}"
            self._show_msg(error_msg)
            error(f"批量生成部分失败，共 {len(errors)} 项失败")
        
        self.status_label.setText(f"批量生成完成: {count} 张，输出: {self.output_folder}")
        info(f"批量生成完成：成功 {count} 个，失败 {len(errors)} 个")
        log_user_action("批量生成完成", f"成功: {count}, 失败: {len(errors)}")

    def _show_msg(self, text):
        QMessageBox.information(self, "信息", text)

