# 样式化组件使用指南

## 概述

本项目提供了一套统一的 UI 组件样式系统，包含 ComboBox、Button、LineEdit、GroupBox 等常用组件的预设样式。

## 快速开始

### 1. 导入样式组件

```python
# 导入便捷函数
from styles import enhanced_combo, simple_combo, primary_button, secondary_button, styled_input, styled_group

# 或者导入工厂类
from styles import StyledWidgets

# 或者导入样式类
from styles import ComboBoxStyles, ButtonStyles, LineEditStyles, GroupBoxStyles
```

### 2. 使用便捷函数创建组件

```python
# 创建增强样式的 ComboBox
combo = enhanced_combo(
    items=["选项1", "选项2", "选项3"],
    current_index=0,
    object_name="my_combo"
)

# 创建主要按钮
btn = primary_button("确认", min_width=120)

# 创建输入框
input_field = styled_input("请输入内容...", monospace=True)

# 创建分组框
group = styled_group("设置选项")
```

### 3. 使用工厂类创建组件

```python
# 创建组件
combo = StyledWidgets.create_enhanced_combo(["选项1", "选项2"])
button = StyledWidgets.create_primary_button("提交")
line_edit = StyledWidgets.create_styled_line_edit("占位符文本")
group_box = StyledWidgets.create_styled_group_box("标题")
```

### 4. 直接应用样式到现有组件

```python
from PySide6.QtWidgets import QComboBox

# 创建标准组件
combo = QComboBox()
combo.addItems(["选项1", "选项2", "选项3"])

# 应用增强样式
ComboBoxStyles.apply_enhanced_style(combo, "enhanced_combo")

# 或者直接设置样式
combo.setObjectName("enhanced_combo")
combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("enhanced_combo"))
```

## 组件样式类型

### ComboBox 样式

1. **增强样式** (`enhanced_combo`)
   - 圆角边框，悬停效果
   - 自定义下拉箭头
   - 美化的下拉列表
   - 焦点状态突出显示

2. **简洁样式** (`simple_combo`)
   - 基础样式，占用空间小
   - 适合紧凑布局

### Button 样式

1. **主要按钮** (`primary_button`)
   - 微信绿主题色
   - 悬停和按下效果
   - 适合主要操作

2. **次要按钮** (`secondary_button`)
   - 浅色主题
   - 边框样式
   - 适合辅助操作

### LineEdit 样式

1. **标准样式** (`styled_input`)
   - 圆角边框
   - 焦点突出效果
   - 可选等宽字体

### GroupBox 样式

1. **标准样式** (`styled_group`)
   - 圆角边框
   - 统一的标题样式
   - 适合内容分组

## 自定义样式

### 修改现有样式

```python
# 获取基础样式
base_style = ComboBoxStyles.get_enhanced_style("my_combo")

# 添加自定义样式
custom_style = base_style + """
    QComboBox#my_combo {
        background-color: #f0f0f0;
    }
"""

combo.setStyleSheet(custom_style)
```

### 创建新的样式类

```python
from styles.widgets import ComboBoxStyles
from styles.constants import Colors

class CustomComboBoxStyles(ComboBoxStyles):
    @staticmethod
    def get_dark_style(object_name="dark_combo"):
        return f"""
            QComboBox#{object_name} {{
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
            }}
        """
```

## 最佳实践

1. **统一命名**：使用描述性的 `object_name`
2. **样式复用**：优先使用预设样式
3. **性能考虑**：避免重复设置相同样式
4. **主题一致性**：保持整个应用的视觉统一

## 示例：完整的表单

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from styles import enhanced_combo, primary_button, secondary_button, styled_input, styled_group

class MyForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 输入组
        input_group = styled_group("基本信息")
        input_layout = QVBoxLayout(input_group)
        
        # 姓名输入
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("姓名:"))
        name_input = styled_input("请输入姓名", monospace=False)
        name_layout.addWidget(name_input)
        input_layout.addLayout(name_layout)
        
        # 类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("类型:"))
        type_combo = enhanced_combo(
            items=["类型1", "类型2", "类型3"],
            object_name="type_selector"
        )
        type_layout.addWidget(type_combo)
        input_layout.addLayout(type_layout)
        
        layout.addWidget(input_group)
        
        # 按钮组
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = secondary_button("取消")
        submit_btn = primary_button("提交")
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(submit_btn)
        
        layout.addLayout(btn_layout)
```

这个样式系统提供了统一、美观、易用的 UI 组件，可以大大提高开发效率和界面一致性。
