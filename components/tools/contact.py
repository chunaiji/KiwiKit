"""
联系我（用户反馈）组件
"""

import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
from components.base_content import BaseContent
from styles.constants import Colors
from styles.widgets import ButtonStyles, GroupBoxStyles, TextEditStyles, LineEditStyles
from utils.background_api import background_api_manager
from utils.api_client import ApiResponse
from utils.logger import get_logger


class ContactMeForm(BaseContent):
    """联系我 / 用户反馈表单"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.api_service = background_api_manager.get_service()
        
        # 确保API服务已启动
        if not background_api_manager.is_running():
            background_api_manager.start()
        
        content_widget = self._create_content_widget()
        super().__init__(title="📬 联系我们", content_widget=content_widget)

    def _create_content_widget(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # 📩 信息输入区域
        form_group = QGroupBox("📩 反馈信息")
        form_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        form_layout = QVBoxLayout(form_group)

        # 姓名
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入您的姓名（最长50字符）")
        self.name_input.setMaxLength(50)
        self.name_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.name_input.textChanged.connect(self._update_name_counter)
        form_layout.addWidget(self._create_labeled_widget("👤 姓名", self.name_input, max_length=50))

        # 联系方式
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("请输入您的联系方式（最长50字符）")
        self.email_input.setMaxLength(50)
        self.email_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.email_input.textChanged.connect(self._update_contact_counter)
        form_layout.addWidget(self._create_labeled_widget("📧 联系方式", self.email_input, max_length=50))

        # 内容
        self.message_input = QTextEdit()
        self.message_input.setObjectName("message_input")
        self.message_input.setPlaceholderText("请输入您的反馈、建议或需求（最长500字符）\n如内容较多，建议分两次提交...")
        self.message_input.setStyleSheet(TextEditStyles.get_standard_style("message_input"))
        self.message_input.textChanged.connect(self._update_message_counter)
        self.message_input.setMinimumHeight(400)  # 设置最小高度
        form_layout.addWidget(self._create_labeled_widget("📝 内容", self.message_input, max_length=500), 1)


        main_layout.addWidget(form_group)

        # 操作按钮区域
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 10, 0, 0)

        self.clear_btn = QPushButton("🧹 清空内容")
        self.clear_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.clear_btn.clicked.connect(self._clear_form)

        self.submit_btn = QPushButton("📨 提交反馈")
        self.submit_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.submit_btn.clicked.connect(self._submit_form)

        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.submit_btn)

        main_layout.addWidget(button_widget)

        return main_widget

    def _create_labeled_widget(self, label_text, widget, max_length=None):
        """创建带标签的表单行"""
        from PySide6.QtWidgets import QHBoxLayout
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签行：包含标签和字符计数器
        label_container = QWidget()
        label_layout = QHBoxLayout(label_container)
        label_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
        label_layout.addWidget(label)
        
        if max_length:
            # 添加字符计数器
            counter_label = QLabel(f"0/{max_length}")
            counter_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
            counter_label.setObjectName(f"counter_{id(widget)}")
            label_layout.addStretch()
            label_layout.addWidget(counter_label)
            
            # 存储计数器引用
            if hasattr(widget, 'setMaxLength'):  # QLineEdit
                widget.counter_label = counter_label
            else:  # QTextEdit
                widget.counter_label = counter_label
                widget.max_length = max_length
        
        layout.addWidget(label_container)
        layout.addWidget(widget)
        return container

    def _update_name_counter(self):
        """更新姓名字符计数器"""
        text = self.name_input.text()
        if hasattr(self.name_input, 'counter_label'):
            self.name_input.counter_label.setText(f"{len(text)}/50")
            # 根据长度设置颜色
            if len(text) >= 45:
                color = "#ef4444"  # 接近限制时显示红色
            elif len(text) >= 35:
                color = "#f59e0b"  # 接近限制时显示橙色
            else:
                color = Colors.TEXT_SECONDARY
            self.name_input.counter_label.setStyleSheet(f"color: {color}; font-size: 12px;")

    def _update_contact_counter(self):
        """更新联系方式字符计数器"""
        text = self.email_input.text()
        if hasattr(self.email_input, 'counter_label'):
            self.email_input.counter_label.setText(f"{len(text)}/50")
            # 根据长度设置颜色
            if len(text) >= 45:
                color = "#ef4444"  # 接近限制时显示红色
            elif len(text) >= 35:
                color = "#f59e0b"  # 接近限制时显示橙色
            else:
                color = Colors.TEXT_SECONDARY
            self.email_input.counter_label.setStyleSheet(f"color: {color}; font-size: 12px;")

    def _update_message_counter(self):
        """更新消息内容字符计数器并限制长度"""
        text = self.message_input.toPlainText()
        
        # 限制TextEdit长度
        if len(text) > 500:
            # 如果超出限制，截断文本
            cursor = self.message_input.textCursor()
            cursor.setPosition(500)
            cursor.movePosition(cursor.End, cursor.KeepAnchor)
            cursor.removeSelectedText()
            text = text[:500]
            # 显示提示
            self.set_status("内容已达到500字符上限，建议分两次提交")
        
        if hasattr(self.message_input, 'counter_label'):
            self.message_input.counter_label.setText(f"{len(text)}/500")
            # 根据长度设置颜色
            if len(text) >= 450:
                color = "#ef4444"  # 接近限制时显示红色
            elif len(text) >= 350:
                color = "#f59e0b"  # 接近限制时显示橙色
            else:
                color = Colors.TEXT_SECONDARY
            self.message_input.counter_label.setStyleSheet(f"color: {color}; font-size: 12px;")

    def _clear_form(self):
        """清空表单内容"""
        self.name_input.clear()
        self.email_input.clear()
        self.message_input.clear()
        self._update_name_counter()
        self._update_contact_counter()
        self._update_message_counter()
        self.set_status("已清空所有输入")

    def _submit_form(self):
        """提交表单到API接口"""
        name = self.name_input.text().strip()
        contact = self.email_input.text().strip()
        message = self.message_input.toPlainText().strip()

        # 表单验证
        if not name or not contact or not message:
            QMessageBox.warning(self, "表单不完整", "请填写所有字段后再提交。")
            return
            
        # 长度验证
        if len(name) > 50:
            QMessageBox.warning(self, "姓名过长", "姓名不能超过50个字符，请缩短后重试。")
            return
            
        if len(contact) > 50:
            QMessageBox.warning(self, "联系方式过长", "联系方式不能超过50个字符，请缩短后重试。")
            return
            
        if len(message) > 500:
            QMessageBox.warning(self, "内容过长", "反馈内容不能超过500个字符。\n建议将内容分为两次提交，或精简表述。")
            return

        # 禁用提交按钮防止重复提交
        self.submit_btn.setEnabled(False)
        self.submit_btn.setText("📤 提交中...")
        self.set_status("正在提交反馈信息...")

        try:
            # 准备API请求数据
            # 限制MemberId长度，避免太长导致错误
            member_id_raw = f"{name}-{contact}"
            if len(member_id_raw) > 50:  # 限制长度
                member_id = member_id_raw[:50]
            else:
                member_id = member_id_raw
            
            # 组合用户信息作为CodeContent，避免换行符问题
            code_content = f"用户:{name} 联系方式:{contact} 内容:{message}"
            # 限制内容长度
            if len(code_content) > 500:
                code_content = code_content[:500] + "..."
            
            # 使用数字BatchNo，参考成功的后台请求格式
            import time
            batch_no = str(int(time.time()))  # 使用时间戳作为BatchNo
            

            # 调用后台API服务的手动插入方法
            success = self.api_service.manual_insert_code(
                member_id=member_id,
                code_content=code_content,
                batch_no='contact',
                callback=self._handle_submit_response
            )

            if not success:
                self._reset_submit_button()
                self.set_status("提交失败：API服务不可用")
                QMessageBox.critical(self, "提交失败", "API服务暂时不可用，请稍后重试。")

        except Exception as e:
            self.logger.error(f"提交表单时发生异常: {e}")
            self._reset_submit_button()
            self.set_status("提交失败：系统异常")
            QMessageBox.critical(self, "系统错误", f"提交时发生异常：{str(e)}")

    def _handle_submit_response(self, response: ApiResponse):
        """处理API响应"""
        try:
            self._reset_submit_button()
            
            # 添加响应状态码检查和详细日志
            # print("\n" + "="*60)
            # print("📡 API响应处理")
            # print("="*60)
            # print(f"🌐 响应状态: {'成功' if response.is_success() else '失败'}")
            # print(f"📊 状态码: {getattr(response, 'status_code', '未知')}")
            # print(f"💬 响应消息: {response.message}")
            # print("="*60)
            
            if response.is_success():
                # 获取响应数据
                data = response.get_data({})
                
                # 检查业务状态码
                if isinstance(data, dict):
                    business_code = data.get('code')
                    message = data.get('message', '提交成功')
                    
                    # print(f"🔢 业务代码: {business_code}")
                    # print(f"📝 业务消息: {message}")
                    
                    if business_code == 200:
                        # self.logger.info("联系我们表单提交成功")
                        self.set_status("反馈已成功提交！我们已收到您的信息。")
                        QMessageBox.information(
                            self, 
                            "提交成功", 
                            f"感谢您的反馈！\n\n{message}\n\n我们将尽快处理您的反馈。"
                        )
                        self._clear_form()
                    else:
                        error_msg = f"提交失败：{message} (业务代码: {business_code})"
                        self.logger.warning(error_msg)
                        self.set_status(error_msg)
                        QMessageBox.warning(self, "提交失败", error_msg)
                else:
                    # 如果没有业务状态码，认为HTTP成功即为成功
                    self.logger.info("联系我们表单提交成功（无业务状态码）")
                    self.set_status("反馈已成功提交！")
                    QMessageBox.information(self, "提交成功", "感谢您的反馈！我们将尽快处理。")
                    self._clear_form()
            else:
                # HTTP请求失败 - 根据状态码提供不同的用户提示
                status_code = getattr(response, 'status_code', 0)
                error_msg = f"网络请求失败：{response.message}"
                
                if status_code == 502:
                    # 502 Bad Gateway - 服务器临时问题
                    user_msg = "服务器暂时繁忙，请稍后重试。\n\n这通常是临时性问题，几分钟后再次尝试即可。"
                    title = "服务器繁忙"
                elif status_code == 500:
                    # 500 Internal Server Error
                    user_msg = "服务器内部错误，请联系技术支持。"
                    title = "服务器错误"
                elif status_code == 0:
                    # 网络连接问题
                    user_msg = "网络连接失败，请检查网络连接后重试。"
                    title = "网络错误"
                else:
                    # 其他HTTP错误
                    user_msg = f"提交失败，请稍后重试。\n\n错误详情：{response.message}"
                    title = "网络错误"
                
                self.logger.error(error_msg)
                self.set_status(f"提交失败 (状态码: {status_code})")
                QMessageBox.critical(self, title, user_msg)
                
        except Exception as e:
            self.logger.error(f"处理提交响应时发生异常: {e}")
            self.set_status("处理响应时发生异常")
            QMessageBox.critical(self, "系统错误", f"处理响应时发生异常：{str(e)}")

    def _reset_submit_button(self):
        """重置提交按钮状态"""
        self.submit_btn.setEnabled(True)
        self.submit_btn.setText("📨 提交反馈")
