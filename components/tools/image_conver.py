import os
from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFileDialog, QLineEdit, QMessageBox, QSplitter,
    QPushButton, QComboBox, QCheckBox, QSlider, QSpinBox,
    QGroupBox, QFormLayout, QFrame
)
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtCore import Qt
from styles.constants import Colors
from styles.widgets import (
    ButtonStyles, ComboBoxStyles, LineEditStyles, 
    GroupBoxStyles, TextEditStyles, SliderStyles, CheckBoxStyles, SpinBoxStyles
)
from components.base_content import BaseContent

# ========== 工具函数 ==========
def make_slider_with_label(min_val, max_val, default_val, suffix='%'):
    layout = QHBoxLayout()
    slider = QSlider(Qt.Horizontal)
    slider.setRange(min_val, max_val)
    slider.setValue(default_val)
    slider.setObjectName(f"slider_{min_val}_{max_val}")
    slider.setStyleSheet(SliderStyles.get_standard_style(f"slider_{min_val}_{max_val}"))
    label = QLabel(f"{default_val}{suffix}")
    label.setFixedWidth(40)
    layout.addWidget(slider)
    layout.addWidget(label)
    return layout, slider, label
    
    # ========== 主界面类 ==========
class ImageConverterWidget(BaseContent):
    def __init__(self):
        self.image = None
        self.image_path = None
        self.converted_image = None
        
        # 翻转状态变量
        self.flip_horizontal = False
        self.flip_vertical = False
        
        # 创建主要内容组件
        content_widget = self._create_content_widget()
        
        # 初始化基类
        super().__init__(title="图片处理工具", content_widget=content_widget)
        self.setAcceptDrops(True)

    def _create_content_widget(self):
        """创建主要内容区域组件"""
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 顶部按钮
        top_layout = QHBoxLayout()
        
        self.load_button = QPushButton("📂 加载图片")
        self.load_button.setMinimumWidth(110)
        self.load_button.setStyleSheet(ButtonStyles.get_secondary_style())
        self.load_button.clicked.connect(self._load_image)
        top_layout.addWidget(self.load_button)

        self.save_button = QPushButton("💾 保存图片")
        self.save_button.setMinimumWidth(110)
        self.save_button.setStyleSheet(ButtonStyles.get_primary_style())
        self.save_button.clicked.connect(self._save_image)
        self.save_button.setEnabled(False)
        top_layout.addWidget(self.save_button)

        self.save_slices_button = QPushButton("保存切片")
        self.save_slices_button.setMinimumWidth(110)
        self.save_slices_button.setStyleSheet(ButtonStyles.get_secondary_style())
        self.save_slices_button.clicked.connect(self._save_slices)
        self.save_slices_button.setEnabled(False)
        top_layout.addWidget(self.save_slices_button)

        self.convert_button = QPushButton("⚙️ 应用并预览")
        self.convert_button.setMinimumWidth(110)
        self.convert_button.setStyleSheet(ButtonStyles.get_primary_style())
        self.convert_button.clicked.connect(self.apply_preview)
        self.convert_button.setEnabled(False)
        top_layout.addWidget(self.convert_button)

        layout.addLayout(top_layout)

        # 参数区域
        params_frame = QFrame()
        params_layout = QHBoxLayout(params_frame)
        params_layout.setSpacing(12)

        # ====== 左列：尺寸 & 格式 ======
        basic_group = QGroupBox("基本设置")
        basic_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        bg_layout = QFormLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPEG", "PNG", "WEBP", "BMP", "TIFF"])
        self.format_combo.setObjectName("format_combo")
        self.format_combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("format_combo"))
        bg_layout.addRow(QLabel("格式:"), self.format_combo)

        self.keep_aspect = QCheckBox("保持比例")
        self.keep_aspect.setObjectName("keep_aspect")
        self.keep_aspect.setStyleSheet(CheckBoxStyles.get_standard_style("keep_aspect"))
        self.keep_aspect.setChecked(True)
        bg_layout.addRow(self.keep_aspect)

        wh_layout = QHBoxLayout()
        self.width_input = QLineEdit()
        self.width_input.setObjectName("width_input")
        self.width_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.width_input.setFixedWidth(80)
        
        self.height_input = QLineEdit()
        self.height_input.setObjectName("height_input")
        self.height_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.height_input.setFixedWidth(80)
        
        wh_layout.addWidget(QLabel("W:"))
        wh_layout.addWidget(self.width_input)
        wh_layout.addWidget(QLabel("H:"))
        wh_layout.addWidget(self.height_input)
        bg_layout.addRow(QLabel("尺寸:"), wh_layout)

        # 用 Slider 替代 Scale SpinBox
        scale_layout = QVBoxLayout()
        self.scale_slider_layout, self.scale_slider, self.scale_label = make_slider_with_label(10, 800, 100)
        self.scale_slider.valueChanged.connect(lambda val: self.scale_label.setText(f"{val}%"))
        self.scale_slider.valueChanged.connect(self._on_size_changed)
        scale_layout.addWidget(QLabel("缩放比例:"))
        scale_layout.addLayout(self.scale_slider_layout)
        bg_layout.addRow(scale_layout)

        basic_group.setLayout(bg_layout)
        params_layout.addWidget(basic_group)

        # ====== 中列：圆角 & 切割 ======
        middle_group = QGroupBox("圆角 & 切割")
        middle_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        mg_layout = QFormLayout()

        rc_layout = QHBoxLayout()
        self.corner_spin = QSpinBox()
        self.corner_spin.setRange(0, 500)
        self.corner_spin.setValue(0)
        self.corner_spin.setObjectName("corner_spin")
        self.corner_spin.setStyleSheet(SpinBoxStyles.get_enhanced_style("corner_spin"))
        self.corner_spin.valueChanged.connect(lambda: self._small_apply())  # 添加实时更新
        rc_layout.addWidget(QLabel("半径:"))
        rc_layout.addWidget(self.corner_spin)
        mg_layout.addRow(QLabel("圆角:"), rc_layout)

        self.slice_combo = QComboBox()
        self.slice_combo.addItems(["不切割", "1x2 (2)", "2x2 (4)", "3x3 (9)", "4x4 (16)"])
        self.slice_combo.setObjectName("slice_combo")
        self.slice_combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("slice_combo"))
        mg_layout.addRow(QLabel("切割:"), self.slice_combo)

        middle_group.setLayout(mg_layout)
        params_layout.addWidget(middle_group)

        # ====== 右列：RGB 调整 ======
        rgb_group = QGroupBox("RGB 调整")
        rgb_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        rg_layout = QFormLayout()

        # 替换 R/G/B 缩放为 Slider
        self.r_slider_layout, self.r_slider, self.r_label = make_slider_with_label(0, 300, 100)
        self.g_slider_layout, self.g_slider, self.g_label = make_slider_with_label(0, 300, 100)
        self.b_slider_layout, self.b_slider, self.b_label = make_slider_with_label(0, 300, 100)

        self.r_slider.valueChanged.connect(lambda val: self.r_label.setText(f"{val}%"))
        self.g_slider.valueChanged.connect(lambda val: self.g_label.setText(f"{val}%"))
        self.b_slider.valueChanged.connect(lambda val: self.b_label.setText(f"{val}%"))

        self.r_slider.valueChanged.connect(lambda: self._small_apply())
        self.g_slider.valueChanged.connect(lambda: self._small_apply())
        self.b_slider.valueChanged.connect(lambda: self._small_apply())

        rg_layout.addRow(QLabel("R 缩放:"), self.r_slider_layout)
        rg_layout.addRow(QLabel("G 缩放:"), self.g_slider_layout)
        rg_layout.addRow(QLabel("B 缩放:"), self.b_slider_layout)

        self.r_offset = QSpinBox()
        self.r_offset.setRange(-255, 255)
        self.r_offset.setValue(0)
        self.r_offset.setObjectName("r_offset")
        self.r_offset.setStyleSheet(SpinBoxStyles.get_enhanced_style("r_offset"))
        
        self.g_offset = QSpinBox()
        self.g_offset.setRange(-255, 255)
        self.g_offset.setValue(0)
        self.g_offset.setObjectName("g_offset")
        self.g_offset.setStyleSheet(SpinBoxStyles.get_enhanced_style("g_offset"))
        
        self.b_offset = QSpinBox()
        self.b_offset.setRange(-255, 255)
        self.b_offset.setValue(0)
        self.b_offset.setObjectName("b_offset")
        self.b_offset.setStyleSheet(SpinBoxStyles.get_enhanced_style("b_offset"))

        self.r_offset.valueChanged.connect(lambda: self._small_apply())
        self.g_offset.valueChanged.connect(lambda: self._small_apply())
        self.b_offset.valueChanged.connect(lambda: self._small_apply())

        rg_layout.addRow(QLabel("R 偏移:"), self.r_offset)
        rg_layout.addRow(QLabel("G 偏移:"), self.g_offset)
        rg_layout.addRow(QLabel("B 偏移:"), self.b_offset)

        rgb_group.setLayout(rg_layout)
        params_layout.addWidget(rgb_group)

        layout.addWidget(params_frame)

        # ========== 高级功能区域 ==========
        advanced_frame = QFrame()
        advanced_layout = QHBoxLayout(advanced_frame)
        advanced_layout.setSpacing(12)

        # ====== 左列：滤镜和效果 ======
        filter_group = QGroupBox("🎨 滤镜和效果")
        filter_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        filter_layout = QFormLayout()

        # 滤镜选择
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "无滤镜", "模糊", "锐化", "边缘检测", "浮雕", 
            "查找边缘", "平滑", "平滑更多", "轮廓"
        ])
        self.filter_combo.setObjectName("filter_combo")
        self.filter_combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("filter_combo"))
        self.filter_combo.currentTextChanged.connect(lambda: self._small_apply())
        filter_layout.addRow(QLabel("滤镜:"), self.filter_combo)

        # 色调调整
        self.hue_slider_layout, self.hue_slider, self.hue_label = make_slider_with_label(-180, 180, 0, '°')
        self.hue_slider.valueChanged.connect(lambda val: self.hue_label.setText(f"{val}°"))
        self.hue_slider.valueChanged.connect(lambda: self._small_apply())
        filter_layout.addRow(QLabel("色调:"), self.hue_slider_layout)

        # 饱和度调整
        self.saturation_slider_layout, self.saturation_slider, self.saturation_label = make_slider_with_label(0, 200, 100, '%')
        self.saturation_slider.valueChanged.connect(lambda val: self.saturation_label.setText(f"{val}%"))
        self.saturation_slider.valueChanged.connect(lambda: self._small_apply())
        filter_layout.addRow(QLabel("饱和度:"), self.saturation_slider_layout)

        # 亮度调整
        self.brightness_slider_layout, self.brightness_slider, self.brightness_label = make_slider_with_label(0, 200, 100, '%')
        self.brightness_slider.valueChanged.connect(lambda val: self.brightness_label.setText(f"{val}%"))
        self.brightness_slider.valueChanged.connect(lambda: self._small_apply())
        filter_layout.addRow(QLabel("亮度:"), self.brightness_slider_layout)

        filter_group.setLayout(filter_layout)
        advanced_layout.addWidget(filter_group)

        # ====== 中列：变换操作 ======
        transform_group = QGroupBox("🔄 变换操作")
        transform_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        transform_layout = QFormLayout()

        # 旋转角度
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(-360, 360)
        self.rotation_spin.setValue(0)
        self.rotation_spin.setSuffix("°")
        self.rotation_spin.setObjectName("rotation_spin")
        self.rotation_spin.setStyleSheet(SpinBoxStyles.get_enhanced_style("rotation_spin"))
        self.rotation_spin.valueChanged.connect(lambda: self._small_apply())
        transform_layout.addRow(QLabel("旋转角度:"), self.rotation_spin)

        # 翻转按钮
        flip_layout = QHBoxLayout()
        self.flip_h_btn = QPushButton("水平翻转")
        self.flip_h_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.flip_h_btn.clicked.connect(self._flip_horizontal)
        
        self.flip_v_btn = QPushButton("垂直翻转")
        self.flip_v_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.flip_v_btn.clicked.connect(self._flip_vertical)
        
        flip_layout.addWidget(self.flip_h_btn)
        flip_layout.addWidget(self.flip_v_btn)
        transform_layout.addRow(QLabel("翻转:"), flip_layout)

        # 裁剪模式
        self.crop_combo = QComboBox()
        self.crop_combo.addItems(["不裁剪", "智能裁剪", "中心裁剪", "手动裁剪"])
        self.crop_combo.setObjectName("crop_combo")
        self.crop_combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("crop_combo"))
        self.crop_combo.currentTextChanged.connect(lambda: self._small_apply())
        transform_layout.addRow(QLabel("裁剪:"), self.crop_combo)

        transform_group.setLayout(transform_layout)
        advanced_layout.addWidget(transform_group)

        # ====== 右列：水印设置 ======
        watermark_group = QGroupBox("💧 文字水印")
        watermark_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        watermark_layout = QFormLayout()

        # 水印文字
        self.watermark_text = QLineEdit()
        self.watermark_text.setObjectName("watermark_text")
        self.watermark_text.setStyleSheet(LineEditStyles.get_standard_style())
        self.watermark_text.setPlaceholderText("输入水印文字...")
        self.watermark_text.textChanged.connect(lambda: self._small_apply())
        watermark_layout.addRow(QLabel("文字:"), self.watermark_text)

        # 水印位置
        self.watermark_position = QComboBox()
        self.watermark_position.addItems([
            "右下角", "右上角", "左下角", "左上角", "中心"
        ])
        self.watermark_position.setObjectName("watermark_position")
        self.watermark_position.setStyleSheet(ComboBoxStyles.get_enhanced_style("watermark_position"))
        self.watermark_position.currentTextChanged.connect(lambda: self._small_apply())
        watermark_layout.addRow(QLabel("位置:"), self.watermark_position)

        # 水印大小
        self.watermark_size = QSpinBox()
        self.watermark_size.setRange(10, 200)
        self.watermark_size.setValue(24)
        self.watermark_size.setSuffix("px")
        self.watermark_size.setObjectName("watermark_size")
        self.watermark_size.setStyleSheet(SpinBoxStyles.get_enhanced_style("watermark_size"))
        self.watermark_size.valueChanged.connect(lambda: self._small_apply())
        watermark_layout.addRow(QLabel("大小:"), self.watermark_size)

        # 水印透明度
        self.watermark_opacity_layout, self.watermark_opacity, self.watermark_opacity_label = make_slider_with_label(10, 100, 80, '%')
        self.watermark_opacity.valueChanged.connect(lambda val: self.watermark_opacity_label.setText(f"{val}%"))
        self.watermark_opacity.valueChanged.connect(lambda: self._small_apply())
        watermark_layout.addRow(QLabel("透明度:"), self.watermark_opacity_layout)

        watermark_group.setLayout(watermark_layout)
        advanced_layout.addWidget(watermark_group)

        layout.addWidget(advanced_frame)

        # 预览区域 - 左右分割显示原图和处理后的图片
        preview_split = QSplitter(Qt.Horizontal)
        preview_split.setHandleWidth(8)
        
        # 左侧原图预览区域
        original_preview_group = QGroupBox("📷 原图预览")
        original_preview_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        original_layout = QVBoxLayout(original_preview_group)
        
        self.original_preview_label = QLabel()
        self.original_preview_label.setMinimumSize(300, 300)
        self.original_preview_label.setAlignment(Qt.AlignCenter)
        self.original_preview_label.setStyleSheet(f"""
            QLabel {{
                background-color: white; 
                border: 2px solid {Colors.BORDER_LIGHT}; 
                border-radius: 8px;
                padding: 15px;
                color: {Colors.TEXT_SECONDARY};
                font-size: 14px;
            }}
        """)
        self.original_preview_label.setText("📂 点击【加载图片】查看原图")
        original_layout.addWidget(self.original_preview_label, alignment=Qt.AlignCenter)
        
        # 右侧处理后预览区域
        processed_preview_group = QGroupBox("🎨 处理预览")
        processed_preview_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        processed_layout = QVBoxLayout(processed_preview_group)
        
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
        self.preview_label.setText("⚙️点击【应用并预览】查看处理结果")
        processed_layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)
        
        # 添加到分割器
        preview_split.addWidget(original_preview_group)
        preview_split.addWidget(processed_preview_group)
        preview_split.setSizes([400, 400])  # 设置初始大小比例
        
        layout.addWidget(preview_split)
        
        # 状态标签已由BaseContent类处理
        return content_widget

    def _pil2qimage(self, im):
        if im.mode == "RGB":
            r, g, b = im.split()
            im = Image.merge("RGB", (b, g, r))
            data = im.tobytes()
            qimage = QImage(data, im.width, im.height, QImage.Format_RGB888)
            return qimage

        elif im.mode == "RGBA":
            r, g, b, a = im.split()
            im = Image.merge("RGBA", (b, g, r, a))
            data = im.tobytes()
            qimage = QImage(data, im.width, im.height, QImage.Format_RGBA8888)
            return qimage

        else:
            # 其它格式转换为RGBA再处理
            im = im.convert("RGBA")
            return self._pil2qimage(im)

    # 删除 _apply_styles 方法，因为我们现在使用了全局样式

    # ========== 业务逻辑 ==========
    def _load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff)")
        if not path:
            return
        self.image = Image.open(path).convert("RGBA")
        self.image_path = path
        self.converted_image = self.image.copy()
        
        # 更新原图预览
        self._update_original_preview()
        # 更新处理后预览
        self._update_preview()
        
        self.save_button.setEnabled(True)
        self.convert_button.setEnabled(True)
        self.save_slices_button.setEnabled(True)
        self.width_input.setText(str(self.image.width))
        self.height_input.setText(str(self.image.height))
        self.set_status("✅ 图片加载成功，可以开始处理")

    def _save_image(self):
        if not self.converted_image:
            return
        format = self.format_combo.currentText().upper()
        path, _ = QFileDialog.getSaveFileName(self, "保存图片", f"output.{format.lower()}", f"{format} files (*.{format.lower()})")
        if path:
            # 处理RGBA图像保存为JPEG的情况
            img_to_save = self.converted_image.copy()
            if format == "JPEG" and img_to_save.mode == "RGBA":
                # 创建白色背景并合成图像
                background = Image.new("RGB", img_to_save.size, (255, 255, 255))
                background.paste(img_to_save, mask=img_to_save.split()[-1])  # 使用alpha通道作为mask
                img_to_save = background
            elif format == "JPEG" and img_to_save.mode not in ["RGB", "L"]:
                # 转换其他模式为RGB
                img_to_save = img_to_save.convert("RGB")
            
            img_to_save.save(path, format=format, quality=95 if format == "JPEG" else None)
            QMessageBox.information(self, "保存成功", f"图片已保存到:\n{path}")

    def _save_slices(self):
        if not self.converted_image:
            QMessageBox.warning(self, "错误", "请先点击“应用并预览”按钮")
            return

        text = self.slice_combo.currentText()
        mapping = {
            "1x2 (2)": (1, 2),
            "2x2 (4)": (2, 2),
            "3x3 (9)": (3, 3),
            "4x4 (16)": (4, 4),
        }
        if text not in mapping:
            QMessageBox.warning(self, "错误", "请选择一个有效的切割方式")
            return

        rows, cols = mapping[text]
        img = self.converted_image.copy()
        w, h = img.size
        slice_w = w // cols
        slice_h = h // rows

        folder = QFileDialog.getExistingDirectory(self, "选择保存文件夹")
        if not folder:
            return

        count = 0
        for r in range(rows):
            for c in range(cols):
                box = (c * slice_w, r * slice_h, (c + 1) * slice_w, (r + 1) * slice_h)
                part = img.crop(box)
                fname = os.path.join(folder, f"slice_{r}_{c}.jpg")
                if part.mode == "RGBA":
                    background = Image.new("RGB", part.size, (255, 255, 255))
                    background.paste(part, mask=part.split()[-1])
                    part = background
                part.save(fname, format="JPEG", quality=95)
                count += 1

        self.set_status(f"✅ 成功保存 {count} 张切片")
        QMessageBox.information(self, "完成", f"已保存 {count} 张切片到:\n{folder}")



    def _on_size_changed(self):
        if not self.image:
            return
        if self.scale_slider.value() != 100:
            s = self.scale_slider.value() / 100.0
            self.width_input.setText(str(int(self.image.width * s)))
            self.height_input.setText(str(int(self.image.height * s)))

    def _flip_horizontal(self):
        """水平翻转图片 - 不影响原图"""
        self.flip_horizontal = not self.flip_horizontal
        
        # 更新按钮文本显示状态
        if self.flip_horizontal:
            self.flip_h_btn.setText("✓ 水平翻转")
            self.flip_h_btn.setStyleSheet(ButtonStyles.get_primary_style())
        else:
            self.flip_h_btn.setText("水平翻转")
            self.flip_h_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        
        self._small_apply()
        status = "已启用" if self.flip_horizontal else "已取消"
        self.set_status(f"✅ 水平翻转{status}")

    def _flip_vertical(self):
        """垂直翻转图片 - 不影响原图"""
        self.flip_vertical = not self.flip_vertical
        
        # 更新按钮文本显示状态
        if self.flip_vertical:
            self.flip_v_btn.setText("✓ 垂直翻转")
            self.flip_v_btn.setStyleSheet(ButtonStyles.get_primary_style())
        else:
            self.flip_v_btn.setText("垂直翻转")
            self.flip_v_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        
        self._small_apply()
        status = "已启用" if self.flip_vertical else "已取消"
        self.set_status(f"✅ 垂直翻转{status}")

    def apply_preview(self):
        if not self.image:
            return
        img = self.image.copy()

        # 1. 缩放
        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
            img = img.resize((width, height), Image.LANCZOS)
        except Exception:
            QMessageBox.warning(self, "尺寸错误", "请输入有效的宽度和高度")
            return

        # 2. 应用裁剪
        img = self._apply_cropping(img)
        
        # 3. 应用翻转
        img = self._apply_flips(img)
        
        # 4. 应用旋转
        img = self._apply_rotation(img)
        
        # 5. 应用滤镜效果
        img = self._apply_filters(img)
        
        # 6. 应用色调、饱和度、亮度调整
        img = self._apply_color_adjustments(img)

        # 7. 圆角
        radius = self.corner_spin.value()
        if radius > 0:
            img = self._add_rounded_corners(img, radius)

        # 8. RGB 调整
        img = self._apply_rgb_adjust(img)

        # 9. 应用水印（最后添加）
        img = self._apply_watermark(img)

        self.converted_image = img
        self._update_preview()

    def _add_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        w, h = img.size
        radius = min(radius, w // 2, h // 2)
        rounded = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (w, h)], radius=radius, fill=255)
        rounded.paste(img, (0, 0), mask=mask)
        return rounded

    def _apply_rgb_adjust(self, img: Image.Image) -> Image.Image:
        r_mul = self.r_slider.value() / 100.0
        g_mul = self.g_slider.value() / 100.0
        b_mul = self.b_slider.value() / 100.0
        r_off = self.r_offset.value()
        g_off = self.g_offset.value()
        b_off = self.b_offset.value()

        def make_table(mul, off):
            table = []
            for i in range(256):
                v = int(i * mul + off)
                v = max(0, min(255, v))
                table.append(v)
            return table

        r_table = make_table(r_mul, r_off)
        g_table = make_table(g_mul, g_off)
        b_table = make_table(b_mul, b_off)

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")

        channels = img.split()
        r = channels[0].point(r_table)
        g = channels[1].point(g_table)
        b = channels[2].point(b_table)
        if img.mode == "RGBA":
            a = channels[3]
            img = Image.merge("RGBA", (r, g, b, a))
        else:
            img = Image.merge("RGB", (r, g, b))

        return img

    def _apply_filters(self, img: Image.Image) -> Image.Image:
        """应用滤镜效果"""
        filter_name = self.filter_combo.currentText()
        
        if filter_name == "模糊":
            img = img.filter(ImageFilter.BLUR)
        elif filter_name == "锐化":
            img = img.filter(ImageFilter.SHARPEN)
        elif filter_name == "边缘检测":
            img = img.filter(ImageFilter.FIND_EDGES)
        elif filter_name == "浮雕":
            img = img.filter(ImageFilter.EMBOSS)
        elif filter_name == "查找边缘":
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_name == "平滑":
            img = img.filter(ImageFilter.SMOOTH)
        elif filter_name == "平滑更多":
            img = img.filter(ImageFilter.SMOOTH_MORE)
        elif filter_name == "轮廓":
            img = img.filter(ImageFilter.CONTOUR)
        
        return img

    def _apply_color_adjustments(self, img: Image.Image) -> Image.Image:
        """应用色调、饱和度、亮度调整"""
        # 亮度调整
        brightness_factor = self.brightness_slider.value() / 100.0
        if brightness_factor != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness_factor)
        
        # 色调调整（简化版本，通过调整HSV实现）
        hue_shift = self.hue_slider.value()
        if hue_shift != 0:
            # 将RGB转换为HSV，调整色调，再转回RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # 简化的色调调整实现
            img = self._adjust_hue(img, hue_shift)
        
        # 饱和度调整
        saturation_factor = self.saturation_slider.value() / 100.0
        if saturation_factor != 1.0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(saturation_factor)
        
        return img

    def _adjust_hue(self, img: Image.Image, hue_shift: int) -> Image.Image:
        """调整图像色调"""
        import colorsys
        
        # 将图像转换为numpy数组进行处理
        pixels = img.load()
        width, height = img.size
        
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y][:3]
                # 转换到HSV
                h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                # 调整色调
                h = (h + hue_shift/360.0) % 1.0
                # 转换回RGB
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                if img.mode == 'RGBA':
                    pixels[x, y] = (int(r*255), int(g*255), int(b*255), pixels[x, y][3])
                else:
                    pixels[x, y] = (int(r*255), int(g*255), int(b*255))
        
        return img

    def _apply_flips(self, img: Image.Image) -> Image.Image:
        """应用翻转效果"""
        if self.flip_horizontal:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if self.flip_vertical:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        return img

    def _apply_rotation(self, img: Image.Image) -> Image.Image:
        """应用旋转"""
        angle = self.rotation_spin.value()
        if angle != 0:
            img = img.rotate(angle, expand=True, fillcolor=(255, 255, 255, 0))
        return img

    def _apply_cropping(self, img: Image.Image) -> Image.Image:
        """应用裁剪"""
        crop_mode = self.crop_combo.currentText()
        
        if crop_mode == "智能裁剪":
            # 自动检测主要内容区域并裁剪
            img = self._smart_crop(img)
        elif crop_mode == "中心裁剪":
            # 裁剪为正方形，保持中心
            img = self._center_crop(img)
        
        return img

    def _smart_crop(self, img: Image.Image) -> Image.Image:
        """智能裁剪 - 去除边缘的空白区域"""
        # 转换为灰度图进行边缘检测
        gray = img.convert('L')
        
        # 使用边缘检测找到内容边界
        edges = gray.filter(ImageFilter.FIND_EDGES)
        
        # 找到非零像素的边界框
        bbox = edges.getbbox()
        if bbox:
            # 添加一些边距
            margin = 10
            left = max(0, bbox[0] - margin)
            top = max(0, bbox[1] - margin)
            right = min(img.width, bbox[2] + margin)
            bottom = min(img.height, bbox[3] + margin)
            
            img = img.crop((left, top, right, bottom))
        
        return img

    def _center_crop(self, img: Image.Image) -> Image.Image:
        """中心裁剪为正方形"""
        width, height = img.size
        size = min(width, height)
        
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        return img.crop((left, top, right, bottom))

    def _apply_watermark(self, img: Image.Image) -> Image.Image:
        """添加文字水印"""
        watermark_text = self.watermark_text.text().strip()
        if not watermark_text:
            return img
        
        # 保存原始模式
        original_mode = img.mode
        
        # 确保图片是RGBA模式以支持透明度
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 创建水印图层
        watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # 尝试加载系统字体
        font_size = self.watermark_size.value()
        try:
            # Windows系统字体
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # 备用字体
                font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", font_size)
            except:
                # 使用默认字体
                font = ImageFont.load_default()
        
        # 获取文字尺寸
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        position = self.watermark_position.currentText()
        margin = 20
        
        if position == "右下角":
            x = img.width - text_width - margin
            y = img.height - text_height - margin
        elif position == "右上角":
            x = img.width - text_width - margin
            y = margin
        elif position == "左下角":
            x = margin
            y = img.height - text_height - margin
        elif position == "左上角":
            x = margin
            y = margin
        else:  # 中心
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
        
        # 计算透明度
        opacity = int(255 * self.watermark_opacity.value() / 100)
        
        # 绘制水印（白色文字，带透明度）
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, opacity))
        
        # 合成水印
        result = Image.alpha_composite(img, watermark)
        
        # 如果原始图片不是RGBA模式，转换回原始模式
        if original_mode != 'RGBA':
            if original_mode == 'RGB':
                # 创建白色背景合成
                background = Image.new('RGB', result.size, (255, 255, 255))
                background.paste(result, mask=result.split()[-1])  # 使用alpha通道作为mask
                result = background
            else:
                result = result.convert(original_mode)
        
        return result

    def _update_original_preview(self):
        """更新原图预览"""
        if not self.image:
            return
        qimage = self._pil2qimage(self.image)
        pixmap = QPixmap.fromImage(qimage)
        # 获取预览标签的可用尺寸（减去边距和边框）
        margins = self.original_preview_label.contentsMargins()
        available_width = self.original_preview_label.width() - margins.left() - margins.right() - 30  # 额外减去边框和内边距
        available_height = self.original_preview_label.height() - margins.top() - margins.bottom() - 30
        # 适应预览框大小，保持宽高比
        scaled_pixmap = pixmap.scaled(
            available_width, available_height,
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.original_preview_label.setPixmap(scaled_pixmap)

    def _update_preview(self):
        """更新处理后预览"""
        if not self.converted_image:
            return
        qimage = self._pil2qimage(self.converted_image)
        pixmap = QPixmap.fromImage(qimage)
        # 获取预览标签的可用尺寸（减去边距和边框）
        margins = self.preview_label.contentsMargins()
        available_width = self.preview_label.width() - margins.left() - margins.right() - 30  # 额外减去边框和内边距
        available_height = self.preview_label.height() - margins.top() - margins.bottom() - 30
        # 适应预览框大小，保持宽高比
        scaled_pixmap = pixmap.scaled(
            available_width, available_height,
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)
        self.set_status("✅ 应用完成，预览已更新。可以保存。")

    def _small_apply(self):
        """实时预览所有效果"""
        if not self.image:
            return
            
        img = self.image.copy()
        
        # 1. 首先应用尺寸调整（如果有设置的话）
        try:
            width_text = self.width_input.text().strip()
            height_text = self.height_input.text().strip()
            if width_text and height_text:
                width = int(width_text)
                height = int(height_text)
                img = img.resize((width, height), Image.LANCZOS)
        except (ValueError, AttributeError):
            # 如果尺寸输入无效，使用原始尺寸
            pass
        
        # 2. 应用裁剪
        img = self._apply_cropping(img)
        
        # 3. 应用翻转
        img = self._apply_flips(img)
        
        # 4. 应用旋转
        img = self._apply_rotation(img)
        
        # 5. 应用滤镜效果
        img = self._apply_filters(img)
        
        # 6. 应用色调、饱和度、亮度调整
        img = self._apply_color_adjustments(img)
        
        # 7. 应用圆角效果
        radius = self.corner_spin.value()
        if radius > 0:
            img = self._add_rounded_corners(img, radius)
        
        # 8. 应用RGB调整
        img = self._apply_rgb_adjust(img)
        
        # 9. 应用水印（最后添加）
        img = self._apply_watermark(img)
        
        self.converted_image = img
        self._update_preview()
