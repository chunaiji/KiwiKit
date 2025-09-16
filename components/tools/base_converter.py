"""
进制转换工具组件
"""

import sys
import time
import math
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,QTextEdit,
    QMessageBox, QTabWidget, QGroupBox, QPushButton, QComboBox, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from styles.constants import Colors
from styles.widgets import (
    ComboBoxStyles, ButtonStyles, LineEditStyles, TextEditStyles, 
    GroupBoxStyles, TabWidgetStyles
)
from components.base_content import BaseContent


class BaseConverter(BaseContent):
    """多功能转换工具界面 - 包含进制、时间戳、单位等转换"""
    
    def __init__(self):
        # 创建主要内容组件
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="进制转换工具", content_widget=content_widget)

    def _create_content_widget(self):
        """创建主要内容区域组件"""
        from PySide6.QtWidgets import QWidget
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # 创建选项卡界面
        self.tabs = QTabWidget()
        TabWidgetStyles.apply_standard_style(self.tabs, "converter_tabs")
        
        # 添加各种转换工具
        self.tabs.addTab(self._create_base_converter(), "🔄 进制转换")
        self.tabs.addTab(TimestampConverter(), "⏰ 时间戳转换")
        self.tabs.addTab(UnitConverter(), "📏 单位换算")
        self.tabs.addTab(TemperatureConverter(), "🌡️ 温度转换")
        self.tabs.addTab(SpeedConverter(), "🏎️ 速度转换")
        self.tabs.addTab(AreaVolumeConverter(), "📐 面积/体积")
        self.tabs.addTab(AngleConverter(), "📏 角度转换")
        
        layout.addWidget(self.tabs)
        
        return content_widget

    def _create_base_converter(self):
        """创建进制转换界面"""
        from PySide6.QtWidgets import QWidget
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 输入区域
        input_group = QGroupBox("数值输入")
        input_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        input_layout = QVBoxLayout(input_group)
        
        # 输入行
        input_row = QHBoxLayout()
        input_label = QLabel("输入数值:")
        input_label.setMinimumWidth(80)
        
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("请输入要转换的数值...")
        self.input_edit.setStyleSheet(LineEditStyles.get_standard_style())
        
        base_label = QLabel("当前进制:")
        base_label.setMinimumWidth(80)
        
        self.input_base = QComboBox()
        self.input_base.addItems(["2 (二进制)", "8 (八进制)", "10 (十进制)", "16 (十六进制)"])
        self.input_base.setCurrentIndex(2)  # 默认十进制
        ComboBoxStyles.apply_enhanced_style(self.input_base, "input_base")
        
        input_row.addWidget(input_label)
        input_row.addWidget(self.input_edit)
        input_row.addWidget(base_label)
        input_row.addWidget(self.input_base)
        input_layout.addLayout(input_row)
        
        # 转换按钮
        btn_layout = QHBoxLayout()
        
        self.convert_btn = QPushButton("🔄 开始转换")
        self.convert_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.convert_btn.clicked.connect(self.convert)
        
        self.clear_btn = QPushButton("🧹 清空")
        self.clear_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.clear_btn.clicked.connect(self._clear_results)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.convert_btn)
        input_layout.addLayout(btn_layout)
        
        layout.addWidget(input_group)

        # 结果显示区域
        result_group = QGroupBox("转换结果")
        result_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        result_layout = QVBoxLayout(result_group)
        
        self.result_labels = {}
        bases = [
            (2, "二进制", "Binary"),
            (8, "八进制", "Octal"), 
            (10, "十进制", "Decimal"),
            (16, "十六进制", "Hexadecimal")
        ]
        
        for base, name, english in bases:
            row_layout = QHBoxLayout()
            name_label = QLabel(f"{name} ({english}):")
            name_label.setMinimumWidth(150)
            name_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
            
            result_label = QTextEdit("等待转换...")
            result_label.setObjectName(f"result_text_{base}")
            result_label.setStyleSheet(TextEditStyles.get_output_style(f"result_text_{base}"))
            
            self.result_labels[base] = result_label
            row_layout.addWidget(name_label)
            row_layout.addWidget(result_label)
            result_layout.addLayout(row_layout)
        
        layout.addWidget(result_group)
        
        return widget

    # 已删除_apply_styles方法的开始部分，现在使用全局样式
            # 删除的部分样式定义
            # 删除的样式结尾部分

    def _clear_results(self):
        """清空结果"""
        for base, label in self.result_labels.items():
            label.setText("等待转换...")
            # 重新应用输出样式
            label.setStyleSheet(TextEditStyles.get_output_style(f"result_text_{base}"))
        self.input_edit.clear()
        self._update_status("请输入数值并选择进制，然后点击转换", "normal")

    def convert(self):
        """执行进制转换"""
        value = self.input_edit.text().strip()
        if not value:
            QMessageBox.warning(self, "输入错误", "请输入要转换的数值！")
            self._update_status("请输入数值", "warning")
            return

        # 获取输入进制
        base_text = self.input_base.currentText()
        base = int(base_text.split()[0])  # 提取数字部分
        
        try:
            # 转换为十进制
            num = int(value, base)
            
            # 转换为各进制并显示
            self.result_labels[2].setText(bin(num))
            self.result_labels[8].setText(oct(num))
            self.result_labels[10].setText(str(num))
            self.result_labels[16].setText(hex(num).upper())
            
            # 更新结果标签样式为成功状态
            for base, label in self.result_labels.items():
                # 使用成功样式的 TextEdit
                success_style = f"""
                    QTextEdit#result_text_{base} {{
                        background-color: #f0f8ff;
                        border: 2px solid {Colors.WECHAT_GREEN};
                        border-radius: 6px;
                        padding: 10px;
                        font-family: 'Consolas', monospace;
                        font-size: 13px;
                        line-height: 1.4;
                        color: {Colors.TEXT_PRIMARY};
                        font-weight: bold;
                    }}
                """
                label.setStyleSheet(success_style)
            
            self._update_status(f"转换成功！原值: {value} ({base}进制) = {num} (10进制)", "success")
            
        except ValueError as e:
            QMessageBox.critical(self, "转换错误", f"输入的数值不符合 {base} 进制格式！\n错误信息: {str(e)}")
            self._update_status("转换失败：数值格式错误", "error")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"转换过程中发生错误: {str(e)}")
            self._update_status("转换失败", "error")

    def _update_status(self, message, status_type="normal"):
        """更新状态显示"""
        # 使用基类的状态更新方法
        if status_type == "success":
            message = f"✅ {message}"
        elif status_type == "warning":
            message = f"⚠️ {message}"
        elif status_type == "error":
            message = f"❌ {message}"
            
        self.set_status(message)


class TimestampConverter(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 时间戳转日期组
        ts_group = QGroupBox("时间戳 → 日期")
        ts_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        ts_layout = QVBoxLayout(ts_group)
        
        ts_input_layout = QHBoxLayout()
        ts_input_layout.addWidget(QLabel("时间戳:"))
        
        self.ts_input = QLineEdit()
        self.ts_input.setPlaceholderText("请输入时间戳...")
        self.ts_input.setStyleSheet(LineEditStyles.get_standard_style())
        ts_input_layout.addWidget(self.ts_input)
        
        self.ts_unit = QComboBox()
        self.ts_unit.addItems(["秒", "毫秒"])
        ComboBoxStyles.apply_enhanced_style(self.ts_unit, "ts_unit_combo")
        ts_input_layout.addWidget(QLabel("单位:"))
        ts_input_layout.addWidget(self.ts_unit)
        
        ts_btn = QPushButton("🔄 转换为日期")
        ts_btn.setStyleSheet(ButtonStyles.get_primary_style())
        ts_btn.clicked.connect(self.ts_to_date)
        ts_input_layout.addWidget(ts_btn)
        
        ts_layout.addLayout(ts_input_layout)
        
        self.date_output = QTextEdit("等待转换...")
        self.date_output.setObjectName("date_output")
        self.date_output.setStyleSheet(TextEditStyles.get_output_style("date_output"))
        ts_layout.addWidget(self.date_output)
        layout.addWidget(ts_group)

        # 日期转时间戳组
        dt_group = QGroupBox("日期 → 时间戳")
        dt_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        dt_layout = QVBoxLayout(dt_group)
        
        dt_input_layout = QHBoxLayout()
        dt_input_layout.addWidget(QLabel("日期时间:"))
        
        self.dt_input = QLineEdit()
        self.dt_input.setPlaceholderText("格式: 2024-01-01 12:00:00")
        self.dt_input.setStyleSheet(LineEditStyles.get_standard_style())
        dt_input_layout.addWidget(self.dt_input)
        
        dt_btn = QPushButton("🔄 转换为时间戳")
        dt_btn.setStyleSheet(ButtonStyles.get_primary_style())
        dt_btn.clicked.connect(self.date_to_ts)
        dt_input_layout.addWidget(dt_btn)
        
        dt_layout.addLayout(dt_input_layout)
        
        self.ts_output = QTextEdit("等待转换...")
        self.ts_output.setObjectName("ts_output")
        self.ts_output.setStyleSheet(TextEditStyles.get_output_style("ts_output"))
        dt_layout.addWidget(self.ts_output)
        layout.addWidget(dt_group)

    def _apply_converter_styles(self):
        """应用转换器样式"""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
            }}
            QLineEdit:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox {{
                padding: 6px 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                background-color: {Colors.BACKGROUND_TERTIARY};
                selection-background-color: {Colors.WECHAT_GREEN};
                min-width: 80px;
            }}
            QComboBox:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {Colors.TEXT_SECONDARY};
                margin-right: 5px;
            }}
            QPushButton {{
                padding: 8px 16px;
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.WECHAT_GREEN_PRESSED};
            }}
        """)

    def ts_to_date(self):
        try:
            if not self.ts_input.text().strip():
                QMessageBox.warning(self, "输入错误", "请输入时间戳！")
                return
                
            ts = float(self.ts_input.text())
            if self.ts_unit.currentText() == "毫秒":
                ts /= 1000
            dt = datetime.fromtimestamp(ts)
            result = f"📅 {dt.strftime('%Y-%m-%d %H:%M:%S')}"
            self.date_output.setText(result)
            # 应用成功状态样式
            success_style = f"""
                QTextEdit#date_output {{
                    background-color: #f0f8ff;
                    border: 2px solid {Colors.WECHAT_GREEN};
                    border-radius: 6px;
                    padding: 10px;
                    font-family: 'Consolas', monospace;
                    font-size: 13px;
                    line-height: 1.4;
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: bold;
                }}
            """
            self.date_output.setStyleSheet(success_style)
        except ValueError:
            QMessageBox.critical(self, "输入错误", "请输入有效的数字格式！")
        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换失败: {str(e)}")

    def date_to_ts(self):
        try:
            if not self.dt_input.text().strip():
                QMessageBox.warning(self, "输入错误", "请输入日期时间！")
                return
                
            dt = datetime.strptime(self.dt_input.text(), "%Y-%m-%d %H:%M:%S")
            ts = int(dt.timestamp())
            result = f"🕐 {ts} 秒 / {ts * 1000} 毫秒"
            self.ts_output.setText(result)
            # 应用成功状态样式
            success_style = f"""
                QTextEdit#ts_output {{
                    background-color: #f0f8ff;
                    border: 2px solid {Colors.WECHAT_GREEN};
                    border-radius: 6px;
                    padding: 10px;
                    font-family: 'Consolas', monospace;
                    font-size: 13px;
                    line-height: 1.4;
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: bold;
                }}
            """
            self.ts_output.setStyleSheet(success_style)
        except ValueError:
            QMessageBox.critical(self, "格式错误", "请按照 YYYY-MM-DD HH:MM:SS 格式输入！\n例如: 2024-01-01 12:00:00")
        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换失败: {str(e)}")


class UnitConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.unit_types = {
            "长度": {"m": 1, "cm": 100, "mm": 1000, "km": 0.001, "in": 39.37, "ft": 3.28, "yd": 1.094},
            "质量": {"kg": 1, "g": 1000, "lb": 2.2046, "oz": 35.274, "t": 0.001},
            "面积": {"m²": 1, "cm²": 10000, "km²": 0.000001, "ft²": 10.764, "亩": 0.0015},
            "体积": {"m³": 1, "L": 1000, "mL": 1000000, "ft³": 35.315, "gal": 264.17}
        }
        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 类型选择组
        type_group = QGroupBox("单位类型")
        type_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        type_layout = QHBoxLayout(type_group)
        type_layout.addWidget(QLabel("类型:"))
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(list(self.unit_types.keys()))
        ComboBoxStyles.apply_enhanced_style(self.type_combo, "type_combo")
        self.type_combo.currentTextChanged.connect(self.update_units)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        layout.addWidget(type_group)

        # 转换输入组
        convert_group = QGroupBox("单位转换")
        convert_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        convert_layout = QVBoxLayout(convert_group)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("数值:"))
        
        self.from_value = QLineEdit()
        self.from_value.setPlaceholderText("请输入要转换的数值...")
        self.from_value.setStyleSheet(LineEditStyles.get_standard_style())
        input_layout.addWidget(self.from_value)
        convert_layout.addLayout(input_layout)
        
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("从:"))
        
        self.from_unit = QComboBox()
        ComboBoxStyles.apply_enhanced_style(self.from_unit, "from_unit_combo")
        unit_layout.addWidget(self.from_unit)
        
        arrow_label = QLabel("→")
        arrow_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.WECHAT_GREEN};")
        unit_layout.addWidget(arrow_label)
        
        unit_layout.addWidget(QLabel("到:"))
        self.to_unit = QComboBox()
        ComboBoxStyles.apply_enhanced_style(self.to_unit, "to_unit_combo")
        unit_layout.addWidget(self.to_unit)
        convert_layout.addLayout(unit_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn = QPushButton("🔄 开始转换")
        btn.setStyleSheet(ButtonStyles.get_primary_style())
        btn.clicked.connect(self.convert)
        btn_layout.addWidget(btn)
        convert_layout.addLayout(btn_layout)
        
        layout.addWidget(convert_group)

        # 结果显示
        result_group = QGroupBox("转换结果")
        result_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        result_layout = QVBoxLayout(result_group)
        
        self.result = QTextEdit("等待转换...")
        self.result.setObjectName("unit_result")
        self.result.setStyleSheet(TextEditStyles.get_output_style("unit_result"))
        result_layout.addWidget(self.result)
        layout.addWidget(result_group)
        
        self.update_units()

    def _apply_converter_styles(self):
        """应用转换器样式"""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
            }}
            QLineEdit:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox {{
                padding: 6px 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                background-color: {Colors.BACKGROUND_TERTIARY};
                selection-background-color: {Colors.WECHAT_GREEN};
                min-width: 80px;
            }}
            QComboBox:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {Colors.TEXT_SECONDARY};
                margin-right: 5px;
            }}
            QPushButton {{
                padding: 8px 16px;
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.WECHAT_GREEN_PRESSED};
            }}
        """)

    def update_units(self):
        """更新单位选项"""
        units = self.unit_types[self.type_combo.currentText()]
        self.from_unit.clear()
        self.to_unit.clear()
        self.from_unit.addItems(units.keys())
        self.to_unit.addItems(units.keys())
        # 重置结果显示
        self.result.setText("等待转换...")
        self.result.setStyleSheet(TextEditStyles.get_output_style("unit_result"))

    def convert(self):
        """执行单位转换"""
        try:
            if not self.from_value.text().strip():
                QMessageBox.warning(self, "输入错误", "请输入要转换的数值！")
                return
                
            val = float(self.from_value.text())
            units = self.unit_types[self.type_combo.currentText()]
            from_unit = self.from_unit.currentText()
            to_unit = self.to_unit.currentText()
            
            # 转换计算
            base = val / units[from_unit]
            result = base * units[to_unit]
            
            # 显示结果
            result_text = f"📐 {val} {from_unit} = {result:.6f} {to_unit}"
            self.result.setText(result_text)
            # 应用成功状态样式
            success_style = f"""
                QTextEdit#unit_result {{
                    background-color: #f0f8ff;
                    border: 2px solid {Colors.WECHAT_GREEN};
                    border-radius: 6px;
                    padding: 10px;
                    font-family: 'Consolas', monospace;
                    font-size: 14px;
                    line-height: 1.4;
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: bold;
                }}
            """
            self.result.setStyleSheet(success_style)
            
        except ValueError:
            QMessageBox.critical(self, "输入错误", "请输入有效的数字格式！")
        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换失败: {str(e)}")


class TemperatureConverter(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 输入组
        input_group = QGroupBox("温度输入")
        input_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        input_layout = QVBoxLayout(input_group)
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("温度值:"))
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("请输入温度数值...")
        self.input.setStyleSheet(LineEditStyles.get_standard_style())
        temp_layout.addWidget(self.input)
        
        temp_layout.addWidget(QLabel("单位:"))
        self.unit = QComboBox()
        self.unit.addItems(["°C (摄氏度)", "°F (华氏度)", "K (开尔文)"])
        ComboBoxStyles.apply_enhanced_style(self.unit, "temp_unit_combo")
        temp_layout.addWidget(self.unit)
        input_layout.addLayout(temp_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn = QPushButton("🌡️ 开始转换")
        btn.setStyleSheet(ButtonStyles.get_primary_style())
        btn.clicked.connect(self.convert)
        btn_layout.addWidget(btn)
        input_layout.addLayout(btn_layout)
        
        layout.addWidget(input_group)

        # 结果显示
        result_group = QGroupBox("转换结果")
        result_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        result_layout = QVBoxLayout(result_group)
        
        self.result = QTextEdit("等待转换...")
        self.result.setObjectName("temp_result")
        self.result.setStyleSheet(TextEditStyles.get_output_style("temp_result"))
        result_layout.addWidget(self.result)
        layout.addWidget(result_group)

    def _apply_converter_styles(self):
        """应用转换器样式"""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
            }}
            QLineEdit:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox {{
                padding: 6px 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                background-color: {Colors.BACKGROUND_TERTIARY};
                selection-background-color: {Colors.WECHAT_GREEN};
                min-width: 120px;
            }}
            QComboBox:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {Colors.TEXT_SECONDARY};
                margin-right: 5px;
            }}
            QPushButton {{
                padding: 8px 16px;
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.WECHAT_GREEN_PRESSED};
            }}
        """)

    def convert(self):
        """执行温度转换"""
        try:
            if not self.input.text().strip():
                QMessageBox.warning(self, "输入错误", "请输入温度数值！")
                return
                
            val = float(self.input.text())
            unit_text = self.unit.currentText()
            
            # 解析输入单位
            if "°C" in unit_text:
                input_unit = "C"
                c, f, k = val, val * 9 / 5 + 32, val + 273.15
            elif "°F" in unit_text:
                input_unit = "F"
                c = (val - 32) * 5 / 9
                f, k = val, c + 273.15
            elif "K" in unit_text:
                input_unit = "K"
                c = val - 273.15
                f, k = c * 9 / 5 + 32, val
            
            # 检查物理有效性
            if k < 0:
                QMessageBox.warning(self, "物理错误", "温度不能低于绝对零度 (-273.15°C / -459.67°F / 0K)！")
                return
            
            # 显示结果
            result_text = f"""🌡️ 温度转换结果:
            
摄氏度 (°C): {c:.2f}
华氏度 (°F): {f:.2f}
开尔文 (K): {k:.2f}

输入: {val:.2f} {unit_text.split()[0]}"""
            
            self.result.setText(result_text)
            self.result.setStyleSheet(f"""
                QLabel {{
                    padding: 12px;
                    border: 1px solid {Colors.WECHAT_GREEN};
                    border-radius: 4px;
                    background-color: #f0f8ff;
                    font-family: 'Consolas', monospace;
                    font-size: 14px;
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: bold;
                    line-height: 1.5;
                }}
            """)
            
        except ValueError:
            QMessageBox.critical(self, "输入错误", "请输入有效的数字格式！")
        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换失败: {str(e)}")


class SpeedConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.units = {"m/s (米/秒)": 1, "km/h (千米/时)": 3.6, "mph (英里/时)": 2.23694, "knot (节)": 1.94384, "ft/s (英尺/秒)": 3.28084}
        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 输入组
        input_group = QGroupBox("速度输入")
        input_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        input_layout = QVBoxLayout(input_group)
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("速度值:"))
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("请输入速度数值...")
        self.input.setObjectName("speed_input")
        self.input.setStyleSheet(LineEditStyles.get_standard_style())
        speed_layout.addWidget(self.input)
        
        speed_layout.addWidget(QLabel("单位:"))
        self.from_unit = QComboBox()
        self.from_unit.addItems(list(self.units.keys()))
        self.from_unit.setObjectName("speed_unit_combo")
        self.from_unit.setStyleSheet(ComboBoxStyles.get_enhanced_style("speed_unit_combo"))
        speed_layout.addWidget(self.from_unit)
        input_layout.addLayout(speed_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn = QPushButton("🏎️ 开始转换")
        btn.setStyleSheet(ButtonStyles.get_primary_style())
        btn.setMinimumWidth(120)
        btn.clicked.connect(self.convert)
        btn_layout.addWidget(btn)
        input_layout.addLayout(btn_layout)
        
        layout.addWidget(input_group)

        # 结果显示
        result_group = QGroupBox("转换结果")
        result_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        result_layout = QVBoxLayout(result_group)
        
        self.result = QTextEdit("等待转换...")
        self.result.setObjectName("speed_result")
        self.result.setStyleSheet(TextEditStyles.get_output_style("speed_result"))
        result_layout.addWidget(self.result)
        layout.addWidget(result_group)

    def _apply_converter_styles(self):
        """应用转换器样式"""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
            }}
            QLineEdit:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox {{
                padding: 6px 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                background-color: {Colors.BACKGROUND_TERTIARY};
                selection-background-color: {Colors.WECHAT_GREEN};
                min-width: 120px;
            }}
            QComboBox:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {Colors.TEXT_SECONDARY};
                margin-right: 5px;
            }}
            QPushButton {{
                padding: 8px 16px;
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.WECHAT_GREEN_PRESSED};
            }}
        """)

    def convert(self):
        """执行速度转换"""
        try:
            if not self.input.text().strip():
                QMessageBox.warning(self, "输入错误", "请输入速度数值！")
                return
                
            input_val = float(self.input.text())
            from_unit_text = self.from_unit.currentText()
            
            # 转换为基准单位 (m/s)
            base_val = input_val / self.units[from_unit_text]
            
            # 转换为所有单位
            results = []
            for unit_text, factor in self.units.items():
                converted_val = base_val * factor
                unit_name = unit_text.split(' (')[0]
                results.append(f"{unit_name}: {converted_val:.4f}")
            
            result_text = f"🏎️ 速度转换结果:\n输入: {input_val} {from_unit_text.split(' (')[0]}\n\n" + "\n".join(results)
            
            self.result.setText(result_text)
            self.result.setStyleSheet(f"""
                QLabel {{
                    padding: 12px;
                    border: 1px solid {Colors.WECHAT_GREEN};
                    border-radius: 4px;
                    background-color: #f0f8ff;
                    font-family: 'Consolas', monospace;
                    font-size: 13px;
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: bold;
                    line-height: 1.6;
                }}
            """)
            
        except ValueError:
            QMessageBox.critical(self, "输入错误", "请输入有效的数字格式！")
        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换失败: {str(e)}")


class AreaVolumeConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.area_units = {"m² (平方米)": 1, "cm² (平方厘米)": 10000, "km² (平方千米)": 0.000001, "亩": 0.0015, "ft² (平方英尺)": 10.7639, "in² (平方英寸)": 1550}
        self.volume_units = {"m³ (立方米)": 1, "L (升)": 1000, "mL (毫升)": 1000000, "ft³ (立方英尺)": 35.315, "gal (加仑)": 264.17, "in³ (立方英寸)": 61024}
        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 输入组
        input_group = QGroupBox("面积/体积输入")
        input_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        input_layout = QVBoxLayout(input_group)
        
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("数值:"))
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("请输入要转换的数值...")
        self.input.setObjectName("area_volume_input")
        self.input.setStyleSheet(LineEditStyles.get_standard_style())
        value_layout.addWidget(self.input)
        input_layout.addLayout(value_layout)
        
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("单位:"))
        all_units = list(self.area_units.keys()) + list(self.volume_units.keys())
        
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(all_units)
        self.unit_combo.setObjectName("area_volume_combo")
        self.unit_combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("area_volume_combo"))
        unit_layout.addWidget(self.unit_combo)
        input_layout.addLayout(unit_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn = QPushButton("📐 开始转换")
        btn.setStyleSheet(ButtonStyles.get_primary_style())
        btn.setMinimumWidth(120)
        btn.clicked.connect(self.convert)
        btn_layout.addWidget(btn)
        input_layout.addLayout(btn_layout)
        
        layout.addWidget(input_group)

        # 结果显示
        result_group = QGroupBox("转换结果")
        result_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        result_layout = QVBoxLayout(result_group)
        
        self.result = QTextEdit("等待转换...")
        self.result.setObjectName("area_volume_result")
        self.result.setStyleSheet(TextEditStyles.get_output_style("area_volume_result"))
        result_layout.addWidget(self.result)
        layout.addWidget(result_group)

    def _apply_converter_styles(self):
        """应用转换器样式"""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
            }}
            QLineEdit:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox {{
                padding: 6px 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                background-color: {Colors.BACKGROUND_TERTIARY};
                selection-background-color: {Colors.WECHAT_GREEN};
                min-width: 150px;
            }}
            QComboBox:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {Colors.TEXT_SECONDARY};
                margin-right: 5px;
            }}
            QPushButton {{
                padding: 8px 16px;
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.WECHAT_GREEN_PRESSED};
            }}
        """)

    def convert(self):
        """执行面积/体积转换"""
        try:
            if not self.input.text().strip():
                QMessageBox.warning(self, "输入错误", "请输入要转换的数值！")
                return
                
            val = float(self.input.text())
            unit_text = self.unit_combo.currentText()
            
            if unit_text in self.area_units:
                # 面积转换
                base_val = val / self.area_units[unit_text]
                results = []
                for unit, factor in self.area_units.items():
                    converted_val = base_val * factor
                    unit_name = unit.split(' (')[0]
                    results.append(f"{unit_name}: {converted_val:.6f}")
                result_text = f"📐 面积转换结果:\n输入: {val} {unit_text.split(' (')[0]}\n\n" + "\n".join(results)
            else:
                # 体积转换
                base_val = val / self.volume_units[unit_text]
                results = []
                for unit, factor in self.volume_units.items():
                    converted_val = base_val * factor
                    unit_name = unit.split(' (')[0]
                    results.append(f"{unit_name}: {converted_val:.6f}")
                result_text = f"📦 体积转换结果:\n输入: {val} {unit_text.split(' (')[0]}\n\n" + "\n".join(results)
            
            self.result.setText(result_text)
            self.result.setStyleSheet(f"""
                QLabel {{
                    padding: 12px;
                    border: 1px solid {Colors.WECHAT_GREEN};
                    border-radius: 4px;
                    background-color: #f0f8ff;
                    font-family: 'Consolas', monospace;
                    font-size: 13px;
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: bold;
                    line-height: 1.6;
                }}
            """)
            
        except ValueError:
            QMessageBox.critical(self, "输入错误", "请输入有效的数字格式！")
        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换失败: {str(e)}")


class AngleConverter(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 输入组
        input_group = QGroupBox("角度输入")
        input_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        input_layout = QVBoxLayout(input_group)
        
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("角度值:"))
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("请输入角度数值...")
        self.input.setObjectName("angle_input")
        self.input.setStyleSheet(LineEditStyles.get_standard_style())
        angle_layout.addWidget(self.input)
        
        angle_layout.addWidget(QLabel("单位:"))
        
        self.unit = QComboBox()
        self.unit.addItems(["度 (Degree)", "弧度 (Radian)", "百分度 (Gradian)"])
        self.unit.setObjectName("angle_unit_combo")
        self.unit.setStyleSheet(ComboBoxStyles.get_enhanced_style("angle_unit_combo"))
        angle_layout.addWidget(self.unit)
        input_layout.addLayout(angle_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn = QPushButton("📐 开始转换")
        btn.setStyleSheet(ButtonStyles.get_primary_style())
        btn.setMinimumWidth(120)
        btn.clicked.connect(self.convert)
        btn_layout.addWidget(btn)
        input_layout.addLayout(btn_layout)
        
        layout.addWidget(input_group)

        # 结果显示
        result_group = QGroupBox("转换结果")
        result_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        result_layout = QVBoxLayout(result_group)
        
        self.result = QTextEdit("等待转换...")
        self.result.setObjectName("angle_result")
        self.result.setStyleSheet(TextEditStyles.get_output_style("angle_result"))
        result_layout.addWidget(self.result)
        layout.addWidget(result_group)

    def _apply_converter_styles(self):
        """应用转换器样式"""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
            }}
            QLineEdit:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox {{
                padding: 6px 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 13px;
                background-color: {Colors.BACKGROUND_TERTIARY};
                selection-background-color: {Colors.WECHAT_GREEN};
                min-width: 120px;
            }}
            QComboBox:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {Colors.TEXT_SECONDARY};
                margin-right: 5px;
            }}
            QPushButton {{
                padding: 8px 16px;
                background-color: {Colors.WECHAT_GREEN};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {Colors.WECHAT_GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.WECHAT_GREEN_PRESSED};
            }}
        """)

    def convert(self):
        """执行角度转换"""
        try:
            if not self.input.text().strip():
                QMessageBox.warning(self, "输入错误", "请输入角度数值！")
                return
                
            val = float(self.input.text())
            unit_text = self.unit.currentText()
            
            if "度" in unit_text:
                # 输入是度
                deg = val
                rad = math.radians(val)
                grad = val * (10 / 9)
            elif "弧度" in unit_text:
                # 输入是弧度
                rad = val
                deg = math.degrees(val)
                grad = deg * (10 / 9)
            elif "百分度" in unit_text:
                # 输入是百分度
                grad = val
                deg = val * (9 / 10)
                rad = math.radians(deg)
            
            result_text = f"""📐 角度转换结果:
                输入: {val} {unit_text.split(' (')[0]}

                度 (Degree): {deg:.4f}°
                弧度 (Radian): {rad:.6f} rad
                百分度 (Gradian): {grad:.4f} gon"""
            
            self.result.setText(result_text)
            self.result.setStyleSheet(f"""
                QLabel {{
                    padding: 12px;
                    border: 1px solid {Colors.WECHAT_GREEN};
                    border-radius: 4px;
                    background-color: #f0f8ff;
                    font-family: 'Consolas', monospace;
                    font-size: 14px;
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: bold;
                    line-height: 1.5;
                }}
            """)
            
        except ValueError:
            QMessageBox.critical(self, "输入错误", "请输入有效的数字格式！")
        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换失败: {str(e)}")
    
    def refresh_styles(self):
        """刷新样式 - 支持主题切换"""
        # 由于这个组件使用了样式化工厂函数，主题切换时会自动更新
        # 但为了完整性，我们可以在这里添加任何特定的样式刷新逻辑
        pass
