import base64
import hashlib
import urllib.parse
import html
import json
import time
import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QTabWidget, QMessageBox, QLineEdit, QSpinBox, QDateTimeEdit,
    QPushButton, QComboBox, QGroupBox
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont

from components.base_content import BaseContent
from styles.constants import Colors
from styles.widgets import (
    ButtonStyles, ComboBoxStyles, TextEditStyles, 
    GroupBoxStyles, LineEditStyles, TabWidgetStyles, SpinBoxStyles
)
from styles.factory import StyledWidgets

# 可选依赖检查
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    from Crypto.Util.Padding import pad, unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    HAS_RSA = True
except ImportError:
    HAS_RSA = False

try:
    import jwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False


class EncodeDecodeWidget(BaseContent):
    def __init__(self):
        # 创建主体内容
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="🔐 编解码工具", content_widget=content_widget)
        # 初始化状态
        self.set_status("ℹ️ 请输入要处理的文本")

    def _create_content_widget(self):
        """创建主内容区域"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 输入区域
        input_group = QGroupBox("📝 输入文本")
        input_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        self.input_text = QTextEdit()
        self.input_text.setObjectName("encode_input")
        self.input_text.setPlaceholderText("请输入要处理的文本...")
        self.input_text.setStyleSheet(TextEditStyles.get_standard_style("encode_input"))
        input_layout.addWidget(self.input_text)

        layout.addWidget(input_group)

        # 操作区域
        operation_group = QGroupBox("⚙️ 操作设置")
        operation_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        operation_layout = QHBoxLayout(operation_group)
        operation_layout.setSpacing(15)

        # 编码类型选择
        self.type_combo = QComboBox()
        self.type_combo.setObjectName("type_selector")
        self.type_combo.addItems(["Base64", "URL", "HTML", "Hex"])
        self.type_combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("type_selector"))
        operation_layout.addWidget(self.type_combo)

        # 操作选择
        self.action_combo = QComboBox()
        self.action_combo.setObjectName("encode_selector")
        self.action_combo.addItems(["编码", "解码"])
        self.action_combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("encode_selector"))
        operation_layout.addWidget(self.action_combo)

        self.go_btn = QPushButton("🚀 执行")
        self.go_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.go_btn.clicked.connect(self.process_text)
        operation_layout.addWidget(self.go_btn)
        
        operation_layout.addStretch()
        layout.addWidget(operation_group)

        # 输出区域
        output_group = QGroupBox("📋 输出结果")
        output_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(10)

        self.output_text = QTextEdit()
        self.output_text.setObjectName("encode_output")
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(TextEditStyles.get_output_style("encode_output"))
        output_layout.addWidget(self.output_text)

        layout.addWidget(output_group)

        return main_widget

    def _update_status(self, message, status_type="normal"):
        """更新状态标签"""
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "normal": "ℹ️"
        }
        
        icon = icons.get(status_type, icons["normal"])
        self.set_status(f"{icon} {message}")

    def process_text(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "输入为空", "请输入文本内容！")
            self._update_status("请输入文本内容！", "warning")
            return

        encode_type = self.type_combo.currentText()
        action = self.action_combo.currentText()

        try:
            if encode_type == "Base64":
                if action == "编码":
                    encoded_bytes = base64.b64encode(text.encode("utf-8"))
                    result = encoded_bytes.decode("utf-8")
                else:
                    decoded_bytes = base64.b64decode(text)
                    result = decoded_bytes.decode("utf-8")
            elif encode_type == "URL":
                if action == "编码":
                    result = urllib.parse.quote(text)
                else:
                    result = urllib.parse.unquote(text)
            elif encode_type == "HTML":
                if action == "编码":
                    result = html.escape(text)
                else:
                    result = html.unescape(text)
            elif encode_type == "Hex":
                if action == "编码":
                    result = text.encode("utf-8").hex()
                else:
                    result = bytes.fromhex(text).decode("utf-8")
            else:
                result = "不支持的编码类型"
        except Exception as e:
            QMessageBox.critical(self, "处理失败", f"错误信息:\n{str(e)}")
            self._update_status("处理失败", "error")
            return

        self.output_text.setPlainText(result)
        self._update_status(f"{encode_type} {action}成功", "success")


class HashWidget(BaseContent):
    def __init__(self):
        # 创建主体内容
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="🔐 哈希加密", content_widget=content_widget)
        # 初始化状态
        self.set_status("ℹ️ 请输入要加密的文本")

    def _create_content_widget(self):
        """创建主内容区域"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 输入区域
        input_group = QGroupBox("📝 输入文本")
        input_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        self.input_text = QTextEdit()
        self.input_text.setObjectName("hash_input")
        self.input_text.setPlaceholderText("请输入要加密的文本...")
        self.input_text.setStyleSheet(TextEditStyles.get_standard_style("hash_input"))
        input_layout.addWidget(self.input_text)

        layout.addWidget(input_group)

        # 算法选择区域
        algorithm_group = QGroupBox("🔧 算法选择")
        algorithm_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        algorithm_layout = QHBoxLayout(algorithm_group)
        algorithm_layout.setSpacing(15)

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setObjectName("hash_selector")
        self.algorithm_combo.addItems(["MD5", "SHA-1", "SHA-256", "SHA-512"])
        self.algorithm_combo.setCurrentText("MD5")
        self.algorithm_combo.setStyleSheet(ComboBoxStyles.get_enhanced_style("hash_selector"))
        algorithm_layout.addWidget(self.algorithm_combo)

        self.hash_btn = QPushButton("🧮 计算哈希")
        self.hash_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.hash_btn.clicked.connect(self.compute_hash)
        algorithm_layout.addWidget(self.hash_btn)
        
        algorithm_layout.addStretch()
        layout.addWidget(algorithm_group)

        # 输出区域
        output_group = QGroupBox("📋 哈希结果")
        output_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(10)

        self.output_text = QTextEdit()
        self.output_text.setObjectName("hash_output")
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(TextEditStyles.get_output_style("hash_output"))
        output_layout.addWidget(self.output_text)

        layout.addWidget(output_group)

        return main_widget

    def compute_hash(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "输入为空", "请输入文本内容！")
            self._update_status("请输入文本内容！", "warning")
            return

        algorithm = self.algorithm_combo.currentText()
        try:
            if algorithm == "MD5":
                hash_result = hashlib.md5(text.encode("utf-8")).hexdigest()
            elif algorithm == "SHA-1":
                hash_result = hashlib.sha1(text.encode("utf-8")).hexdigest()
            elif algorithm == "SHA-256":
                hash_result = hashlib.sha256(text.encode("utf-8")).hexdigest()
            elif algorithm == "SHA-512":
                hash_result = hashlib.sha512(text.encode("utf-8")).hexdigest()
            else:
                hash_result = "不支持的算法"
                
            self.output_text.setPlainText(hash_result)
            self._update_status(f"{algorithm} 计算成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "计算失败", f"错误信息:\n{str(e)}")
            self._update_status("计算失败", "error")

    def _update_status(self, message, status_type="normal"):
        """更新状态标签"""
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "normal": "ℹ️"
        }
        
        icon = icons.get(status_type, icons["normal"])
        self.set_status(f"{icon} {message}")





class JWTWidget(BaseContent):
    def __init__(self):
        # 创建主体内容
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="🔑 JWT 编解码", content_widget=content_widget)
        # 初始化状态
        status_msg = "ℹ️ 请输入JWT Token" if HAS_JWT else "❌ 未安装 PyJWT 库"
        self.set_status(status_msg)

    def _create_content_widget(self):
        """创建主内容区域"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # JWT Token 输入区域
        token_group = QGroupBox("🎫 JWT Token")
        token_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        token_layout = QVBoxLayout(token_group)
        token_layout.setSpacing(10)

        self.token_text = QTextEdit()
        self.token_text.setObjectName("jwt_input")
        self.token_text.setPlaceholderText("请输入JWT Token...")
        self.token_text.setMaximumHeight(120)
        self.token_text.setStyleSheet(TextEditStyles.get_standard_style("jwt_input"))
        token_layout.addWidget(self.token_text)

        layout.addWidget(token_group)

        # 密钥输入区域
        key_group = QGroupBox("🔐 密钥设置")
        key_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        key_layout = QVBoxLayout(key_group)
        key_layout.setSpacing(10)

        self.key_input = QLineEdit()
        self.key_input.setObjectName("jwt_key")
        self.key_input.setPlaceholderText("请输入密钥 (用于编码)...")
        self.key_input.setStyleSheet(LineEditStyles.get_standard_style())
        key_layout.addWidget(self.key_input)

        layout.addWidget(key_group)

        # 按钮区域
        button_group = QGroupBox("⚡ 操作")
        button_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        button_layout = QHBoxLayout(button_group)
        button_layout.setSpacing(15)
        
        self.decode_btn = QPushButton("🔓 解码 JWT")
        self.decode_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.decode_btn.clicked.connect(self.decode_jwt)
        button_layout.addWidget(self.decode_btn)

        self.encode_btn = QPushButton("🔒 编码 JWT")
        self.encode_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.encode_btn.clicked.connect(self.encode_jwt)
        button_layout.addWidget(self.encode_btn)
        
        button_layout.addStretch()
        layout.addWidget(button_group)

        # 输出区域
        output_group = QGroupBox("📋 解码结果")
        output_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(10)

        self.output_text = QTextEdit()
        self.output_text.setObjectName("jwt_output")
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(TextEditStyles.get_output_style("jwt_output"))
        output_layout.addWidget(self.output_text)

        layout.addWidget(output_group)

        return main_widget

    def decode_jwt(self):
        token = self.token_text.toPlainText().strip()
        if not token:
            QMessageBox.warning(self, "输入为空", "请输入JWT Token！")
            self._update_status("请输入JWT Token！", "warning")
            return

        if not HAS_JWT:
            QMessageBox.warning(self, "库缺失", "请安装 PyJWT 库: pip install PyJWT")
            self._update_status("请安装 PyJWT 库", "error")
            return

        try:
            # 不验证签名的解码
            decoded = jwt.decode(token, options={"verify_signature": False})
            formatted_output = json.dumps(decoded, indent=2, ensure_ascii=False)
            self.output_text.setPlainText(formatted_output)
            self._update_status("解码成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "解码失败", f"错误信息:\n{str(e)}")
            self._update_status("解码失败", "error")

    def encode_jwt(self):
        payload_text = self.output_text.toPlainText().strip()
        key = self.key_input.text().strip()
        
        if not payload_text or not key:
            QMessageBox.warning(self, "输入不完整", "请输入payload和密钥！")
            self._update_status("请输入payload和密钥！", "warning")
            return

        if not HAS_JWT:
            QMessageBox.warning(self, "库缺失", "请安装 PyJWT 库: pip install PyJWT")
            self._update_status("请安装 PyJWT 库", "error")
            return

        try:
            payload = json.loads(payload_text)
            token = jwt.encode(payload, key, algorithm="HS256")
            self.token_text.setPlainText(token)
            self._update_status("编码成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "编码失败", f"错误信息:\n{str(e)}")
            self._update_status("编码失败", "error")

    def _update_status(self, message, status_type="normal"):
        """更新状态标签"""
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "normal": "ℹ️"
        }
        
        icon = icons.get(status_type, icons["normal"])
        self.set_status(f"{icon} {message}")


class CryptoWidget(BaseContent):
    def __init__(self):
        # 创建主体内容
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="🔐 对称/非对称加密", content_widget=content_widget)
        # 初始化状态
        status_msg = "ℹ️ 请选择加密类型" if (HAS_CRYPTO and HAS_RSA) else "❌ 需要安装 pycryptodome 库"
        self.set_status(status_msg)

    def _create_content_widget(self):
        """创建主内容区域"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 加密类型选择区域
        type_group = QGroupBox("🔧 加密类型选择")
        type_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        type_layout = QHBoxLayout(type_group)
        type_layout.setSpacing(15)

        self.crypto_type = QComboBox()
        self.crypto_type.setObjectName("crypto_selector")
        self.crypto_type.addItems(["AES", "RSA"])
        self.crypto_type.setStyleSheet(ComboBoxStyles.get_enhanced_style("crypto_selector"))
        self.crypto_type.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.crypto_type)
        type_layout.addStretch()

        layout.addWidget(type_group)

        # AES 密钥输入区域
        self.aes_key_group = QGroupBox("🔑 AES 密钥设置")
        self.aes_key_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        aes_key_layout = QVBoxLayout(self.aes_key_group)
        aes_key_layout.setSpacing(10)

        self.key_input = QLineEdit()
        self.key_input.setObjectName("crypto_key")
        self.key_input.setPlaceholderText("请输入AES密钥 (16/24/32字符)...")
        self.key_input.setStyleSheet(LineEditStyles.get_standard_style())
        aes_key_layout.addWidget(self.key_input)

        layout.addWidget(self.aes_key_group)

        # RSA 密钥输入区域（初始隐藏）
        self.rsa_key_group = QGroupBox("🔐 RSA 密钥设置")
        self.rsa_key_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        self.rsa_key_group.hide()
        rsa_key_layout = QVBoxLayout(self.rsa_key_group)
        rsa_key_layout.setSpacing(10)

        # 公钥输入
        pub_key_label = QLabel("📄 公钥 (PEM格式):")
        pub_key_label.setStyleSheet(f"font-weight: bold; color: {Colors.TEXT_PRIMARY};")
        rsa_key_layout.addWidget(pub_key_label)

        self.pub_key_input = QTextEdit()
        self.pub_key_input.setObjectName("rsa_pub_key")
        self.pub_key_input.setPlaceholderText("请输入RSA公钥...")
        self.pub_key_input.setMaximumHeight(120)
        self.pub_key_input.setStyleSheet(TextEditStyles.get_standard_style("rsa_pub_key"))
        rsa_key_layout.addWidget(self.pub_key_input)

        # 私钥输入
        priv_key_label = QLabel("🔓 私钥 (PEM格式):")
        priv_key_label.setStyleSheet(f"font-weight: bold; color: {Colors.TEXT_PRIMARY};")
        rsa_key_layout.addWidget(priv_key_label)

        self.priv_key_input = QTextEdit()
        self.priv_key_input.setObjectName("rsa_priv_key")
        self.priv_key_input.setPlaceholderText("请输入RSA私钥...")
        self.priv_key_input.setMaximumHeight(120)
        self.priv_key_input.setStyleSheet(TextEditStyles.get_standard_style("rsa_priv_key"))
        rsa_key_layout.addWidget(self.priv_key_input)

        # RSA密钥生成按钮
        self.generate_keys_btn = QPushButton("🔧 生成RSA密钥对")
        self.generate_keys_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.generate_keys_btn.clicked.connect(self.generate_rsa_keys)
        rsa_key_layout.addWidget(self.generate_keys_btn)

        layout.addWidget(self.rsa_key_group)

        # 文本输入区域
        input_group = QGroupBox("📝 明文/密文输入")
        input_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        self.text_input = QTextEdit()
        self.text_input.setObjectName("crypto_input")
        self.text_input.setPlaceholderText("请输入要加密或解密的文本...")
        self.text_input.setStyleSheet(TextEditStyles.get_standard_style("crypto_input"))
        input_layout.addWidget(self.text_input)

        layout.addWidget(input_group)

        # 按钮操作区域
        button_group = QGroupBox("⚡ 操作")
        button_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        button_layout = QHBoxLayout(button_group)
        button_layout.setSpacing(15)
        
        self.encrypt_btn = QPushButton("🔒 加密")
        self.encrypt_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.encrypt_btn.clicked.connect(self.encrypt_text)
        button_layout.addWidget(self.encrypt_btn)

        self.decrypt_btn = QPushButton("🔓 解密")
        self.decrypt_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.decrypt_btn.clicked.connect(self.decrypt_text)
        button_layout.addWidget(self.decrypt_btn)
        
        button_layout.addStretch()
        layout.addWidget(button_group)

        # 输出结果区域
        output_group = QGroupBox("📋 输出结果")
        output_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(10)

        self.output_text = QTextEdit()
        self.output_text.setObjectName("crypto_output")
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(TextEditStyles.get_output_style("crypto_output"))
        output_layout.addWidget(self.output_text)

        layout.addWidget(output_group)

        return main_widget

    def on_type_changed(self):
        crypto_type = self.crypto_type.currentText()
        if crypto_type == "AES":
            # 显示AES相关控件
            self.aes_key_group.show()
            # 隐藏RSA相关控件
            self.rsa_key_group.hide()
            
            self.encrypt_btn.setText("🔒 AES 加密")
            self.decrypt_btn.setText("🔓 AES 解密")
        elif crypto_type == "RSA":
            # 隐藏AES相关控件
            self.aes_key_group.hide()
            # 显示RSA相关控件
            self.rsa_key_group.show()
            
            self.encrypt_btn.setText("🔒 RSA 加密")
            self.decrypt_btn.setText("🔓 RSA 解密")

    def generate_rsa_keys(self):
        if not HAS_RSA:
            QMessageBox.warning(self, "库缺失", "请安装 pycryptodome 库: pip install pycryptodome")
            self._update_status("请安装 pycryptodome 库", "error")
            return

        try:
            key = RSA.generate(2048)
            private_key = key.export_key().decode('utf-8')
            public_key = key.publickey().export_key().decode('utf-8')
            
            self.priv_key_input.setPlainText(private_key)
            self.pub_key_input.setPlainText(public_key)
            self._update_status("密钥生成成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "密钥生成失败", f"错误信息:\n{str(e)}")
            self._update_status("密钥生成失败", "error")

    def encrypt_text(self):
        crypto_type = self.crypto_type.currentText()
        text = self.text_input.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self, "输入为空", "请输入要加密的文本！")
            self._update_status("请输入要加密的文本！", "warning")
            return

        if crypto_type == "AES":
            self._encrypt_aes(text)
        elif crypto_type == "RSA":
            self._encrypt_rsa(text)

    def decrypt_text(self):
        crypto_type = self.crypto_type.currentText()
        text = self.text_input.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self, "输入为空", "请输入要解密的文本！")
            self._update_status("请输入要解密的文本！", "warning")
            return

        if crypto_type == "AES":
            self._decrypt_aes(text)
        elif crypto_type == "RSA":
            self._decrypt_rsa(text)

    def _encrypt_aes(self, text):
        key = self.key_input.text().strip()
        
        if not key:
            QMessageBox.warning(self, "输入不完整", "请输入AES密钥！")
            self._update_status("请输入AES密钥！", "warning")
            return

        if not HAS_CRYPTO:
            QMessageBox.warning(self, "库缺失", "请安装 pycryptodome 库: pip install pycryptodome")
            self._update_status("请安装 pycryptodome 库", "error")
            return

        try:
            # 确保密钥长度正确
            key_bytes = key.encode('utf-8')
            if len(key_bytes) not in [16, 24, 32]:
                # 填充或截断到32字节
                key_bytes = key_bytes[:32].ljust(32, b'\0')
            
            cipher = AES.new(key_bytes, AES.MODE_CBC)
            padded_text = pad(text.encode('utf-8'), AES.block_size)
            encrypted = cipher.encrypt(padded_text)
            
            # 将IV和密文组合，然后base64编码
            result = base64.b64encode(cipher.iv + encrypted).decode('utf-8')
            self.output_text.setPlainText(result)
            self._update_status("AES加密成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "加密失败", f"错误信息:\n{str(e)}")
            self._update_status("AES加密失败", "error")

    def _decrypt_aes(self, encrypted_text):
        key = self.key_input.text().strip()
        
        if not key:
            QMessageBox.warning(self, "输入不完整", "请输入AES密钥！")
            self._update_status("请输入AES密钥！", "warning")
            return

        if not HAS_CRYPTO:
            QMessageBox.warning(self, "库缺失", "请安装 pycryptodome 库: pip install pycryptodome")
            self._update_status("请安装 pycryptodome 库", "error")
            return

        try:
            # 确保密钥长度正确
            key_bytes = key.encode('utf-8')
            if len(key_bytes) not in [16, 24, 32]:
                key_bytes = key_bytes[:32].ljust(32, b'\0')
            
            # base64解码
            encrypted_data = base64.b64decode(encrypted_text)
            
            # 提取IV和密文
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
            
            result = decrypted.decode('utf-8')
            self.output_text.setPlainText(result)
            self._update_status("AES解密成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "解密失败", f"错误信息:\n{str(e)}")
            self._update_status("AES解密失败", "error")

    def _encrypt_rsa(self, text):
        pub_key_text = self.pub_key_input.toPlainText().strip()
        
        if not pub_key_text:
            QMessageBox.warning(self, "输入不完整", "请输入RSA公钥！")
            self._update_status("请输入RSA公钥！", "warning")
            return

        if not HAS_RSA:
            QMessageBox.warning(self, "库缺失", "请安装 pycryptodome 库: pip install pycryptodome")
            self._update_status("请安装 pycryptodome 库", "error")
            return

        try:
            key = RSA.import_key(pub_key_text)
            cipher = PKCS1_OAEP.new(key)
            encrypted = cipher.encrypt(text.encode('utf-8'))
            result = base64.b64encode(encrypted).decode('utf-8')
            
            self.output_text.setPlainText(result)
            self._update_status("RSA加密成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "加密失败", f"错误信息:\n{str(e)}")
            self._update_status("RSA加密失败", "error")

    def _decrypt_rsa(self, encrypted_text):
        priv_key_text = self.priv_key_input.toPlainText().strip()
        
        if not priv_key_text:
            QMessageBox.warning(self, "输入不完整", "请输入RSA私钥！")
            self._update_status("请输入RSA私钥！", "warning")
            return

        if not HAS_RSA:
            QMessageBox.warning(self, "库缺失", "请安装 pycryptodome 库: pip install pycryptodome")
            self._update_status("请安装 pycryptodome 库", "error")
            return

        try:
            key = RSA.import_key(priv_key_text)
            cipher = PKCS1_OAEP.new(key)
            encrypted_data = base64.b64decode(encrypted_text)
            decrypted = cipher.decrypt(encrypted_data)
            result = decrypted.decode('utf-8')
            
            self.output_text.setPlainText(result)
            self._update_status("RSA解密成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "解密失败", f"错误信息:\n{str(e)}")
            self._update_status("RSA解密失败", "error")

    def _update_status(self, message, status_type="normal"):
        """更新状态标签"""
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "normal": "ℹ️"
        }
        
        icon = icons.get(status_type, icons["normal"])
        self.set_status(f"{icon} {message}")





class TimestampWidget(BaseContent):
    def __init__(self):
        # 创建主体内容
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="🕒 时间戳转换", content_widget=content_widget)
        # 初始化状态
        self.set_status("ℹ️ 准备转换时间戳和日期")

    def _create_content_widget(self):
        """创建主内容区域"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 时间戳输入区域
        timestamp_group = QGroupBox("🔢 时间戳输入")
        timestamp_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        timestamp_layout = QHBoxLayout(timestamp_group)
        timestamp_layout.setSpacing(15)
        
        self.timestamp_input = QLineEdit()
        self.timestamp_input.setObjectName("timestamp_input")
        self.timestamp_input.setPlaceholderText("请输入时间戳...")
        self.timestamp_input.setStyleSheet(LineEditStyles.get_standard_style())
        timestamp_layout.addWidget(self.timestamp_input)

        self.current_time_btn = QPushButton("📅 当前时间")
        self.current_time_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.current_time_btn.clicked.connect(self.set_current_timestamp)
        timestamp_layout.addWidget(self.current_time_btn)
        timestamp_layout.addStretch()

        layout.addWidget(timestamp_group)

        # 日期时间选择区域
        datetime_group = QGroupBox("📆 日期时间选择")
        datetime_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        datetime_layout = QVBoxLayout(datetime_group)
        datetime_layout.setSpacing(10)

        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setObjectName("datetime_input")
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.datetime_edit.setStyleSheet(f"""
            QDateTimeEdit {{
                background-color: {Colors.BACKGROUND_LIGHT};
                border: 2px solid {Colors.BORDER_LIGHT};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }}
            QDateTimeEdit:focus {{
                border-color: {Colors.WECHAT_GREEN};
            }}
        """)
        datetime_layout.addWidget(self.datetime_edit)

        layout.addWidget(datetime_group)

        # 转换按钮区域
        button_group = QGroupBox("⚡ 转换操作")
        button_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        button_layout = QHBoxLayout(button_group)
        button_layout.setSpacing(15)
        
        self.to_datetime_btn = QPushButton("📅 时间戳→日期")
        self.to_datetime_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.to_datetime_btn.clicked.connect(self.timestamp_to_datetime)
        button_layout.addWidget(self.to_datetime_btn)

        self.to_timestamp_btn = QPushButton("🔢 日期→时间戳")
        self.to_timestamp_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.to_timestamp_btn.clicked.connect(self.datetime_to_timestamp)
        button_layout.addWidget(self.to_timestamp_btn)
        
        button_layout.addStretch()
        layout.addWidget(button_group)

        # 输出结果区域
        output_group = QGroupBox("📋 转换结果")
        output_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(10)

        self.output_text = QTextEdit()
        self.output_text.setObjectName("timestamp_output")
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(150)
        self.output_text.setStyleSheet(TextEditStyles.get_output_style("timestamp_output"))
        output_layout.addWidget(self.output_text)

        layout.addWidget(output_group)

        return main_widget

    def set_current_timestamp(self):
        current_timestamp = int(time.time())
        self.timestamp_input.setText(str(current_timestamp))
        self._update_status("已设置当前时间戳", "success")

    def timestamp_to_datetime(self):
        timestamp_str = self.timestamp_input.text().strip()
        if not timestamp_str:
            QMessageBox.warning(self, "输入为空", "请输入时间戳！")
            self._update_status("请输入时间戳！", "warning")
            return

        try:
            timestamp = int(timestamp_str)
            # 处理毫秒时间戳
            if len(timestamp_str) == 13:
                timestamp = timestamp / 1000
            
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            result_lines = [
                f"时间戳: {timestamp_str}",
                f"本地时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}",
                f"UTC时间: {datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}",
                f"ISO格式: {dt.isoformat()}",
                f"星期: {dt.strftime('%A')}",
                f"年份第几天: {dt.timetuple().tm_yday}"
            ]
            
            self.output_text.setPlainText('\n'.join(result_lines))
            self.datetime_edit.setDateTime(QDateTime.fromSecsSinceEpoch(int(timestamp)))
            self._update_status("转换成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "转换失败", f"错误信息:\n{str(e)}")
            self._update_status("转换失败", "error")

    def datetime_to_timestamp(self):
        try:
            dt = self.datetime_edit.dateTime().toPython()
            timestamp = int(dt.timestamp())
            
            result_lines = [
                f"日期时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}",
                f"时间戳(秒): {timestamp}",
                f"时间戳(毫秒): {timestamp * 1000}",
                f"ISO格式: {dt.isoformat()}",
                f"星期: {dt.strftime('%A')}",
                f"UTC时间: {dt.utctimetuple()}"
            ]
            
            self.output_text.setPlainText('\n'.join(result_lines))
            self.timestamp_input.setText(str(timestamp))
            self._update_status("转换成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "转换失败", f"错误信息:\n{str(e)}")
            self._update_status("转换失败", "error")

    def _update_status(self, message, status_type="normal"):
        """更新状态标签"""
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "normal": "ℹ️"
        }
        
        icon = icons.get(status_type, icons["normal"])
        self.set_status(f"{icon} {message}")


class EncodeDecodeSuite(BaseContent):
    def __init__(self):
        # 创建主体内容
        content_widget = self._create_content_widget()
        # 初始化基类
        super().__init__(title="🔐 编解码工具套件", content_widget=content_widget)
        # 初始化状态
        self.set_status("ℹ️ 选择相应的工具标签页开始使用")

    def _create_content_widget(self):
        """创建主内容区域"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("main_tabs")
        self.tabs.setStyleSheet(TabWidgetStyles.get_standard_style("main_tabs"))

        # 整合后的标签页
        self.tabs.addTab(EncodeDecodeWidget(), "🔐 编解码")
        self.tabs.addTab(HashWidget(), "🔐 哈希加密")
        self.tabs.addTab(JWTWidget(), "🔑 JWT")
        self.tabs.addTab(CryptoWidget(), "🔒 对称/非对称")
        self.tabs.addTab(TimestampWidget(), "🕒 时间戳")

        layout.addWidget(self.tabs)

        return main_widget
    
    def refresh_styles(self):
        """刷新样式 - 支持主题切换"""
        self.tabs.setStyleSheet(TabWidgetStyles.get_standard_style("main_tabs"))


