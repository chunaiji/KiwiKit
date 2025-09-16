import os
import re
import requests
from urllib.parse import urlparse
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QCheckBox, QProgressBar,
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QImage, QFont
from styles.constants import Colors
from styles.widgets import (
    ButtonStyles, LineEditStyles, GroupBoxStyles, CheckBoxStyles,
    ProgressBarStyles
)
from components.base_content import BaseContent
from components.base_bootstrap import Col, Row, Container, Spacer


MEDIA_EXTENSIONS = ['.mp4', '.mp3', '.wav', '.avi', '.mkv', '.flv', '.mov', '.webm']
EXT_VIDEO = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.webm']
EXT_AUDIO = ['.mp3', '.wav', '.aac', '.ogg', '.flac']
EXT_IMAGE = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']



# ============ 提取媒体链接线程 ============ #
class MediaExtractThread(QThread):
    media_found = Signal(list)  # list of media URLs
    error_occurred = Signal(str)

    def __init__(self, page_url, extensions):
        super().__init__()
        self.page_url = page_url
        self.extensions = extensions

    def run(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.get(self.page_url, headers=headers, timeout=15)
            resp.raise_for_status()  # 抛出HTTP错误
            
            html = resp.text
            
            # 使用更全面的正则表达式来查找媒体链接
            # 包括相对路径和绝对路径
            absolute_links = re.findall(r'https?://[^\s\'"<>]+', html)
            relative_links = re.findall(r'(?:src|href)=["\']([^"\']+)', html)
            
            all_links = absolute_links.copy()
            
            # 处理相对路径
            from urllib.parse import urljoin
            base_url = self.page_url
            for link in relative_links:
                if not link.startswith(('http://', 'https://', '//')):
                    full_url = urljoin(base_url, link)
                    all_links.append(full_url)
                elif link.startswith('//'):
                    # 协议相对URL
                    protocol = 'https:' if base_url.startswith('https:') else 'http:'
                    all_links.append(protocol + link)
            
            # 过滤媒体文件
            media_links = list({
                url for url in all_links 
                if any(url.lower().endswith(ext) for ext in self.extensions) or
                   any(ext[1:] in url.lower() for ext in self.extensions)  # 处理没有明确扩展名的情况
            })
            
            self.media_found.emit(media_links)
            
        except requests.exceptions.Timeout:
            self.error_occurred.emit("网页访问超时")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("网络连接失败，请检查网络设置")
        except requests.exceptions.HTTPError as e:
            self.error_occurred.emit(f"HTTP错误 {e.response.status_code}: {e.response.reason}")
        except Exception as e:
            self.error_occurred.emit(f"解析网页时出错: {str(e)}")


# ============ 下载线程 ============ #
class MediaDownloadThread(QThread):
    progress_updated = Signal(str, int)  # url, downloaded bytes
    download_finished = Signal(str)
    error_occurred = Signal(str, str)
    status_updated = Signal(str, str)  # url, status message

    def __init__(self, url, save_path, timeout=30, max_retries=3):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.timeout = timeout
        self.max_retries = max_retries
        self._stopped = False

    def run(self):
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries and not self._stopped:
            try:
                if retry_count > 0:
                    self.status_updated.emit(self.url, f"重试中 ({retry_count}/{self.max_retries})")
                else:
                    self.status_updated.emit(self.url, "连接中...")
                
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                
                # 检查是否支持断点续传
                if os.path.exists(self.save_path):
                    existing = os.path.getsize(self.save_path)
                    headers['Range'] = f'bytes={existing}-'
                else:
                    existing = 0

                # 发起请求，设置超时
                with requests.get(self.url, headers=headers, stream=True, timeout=self.timeout) as r:
                    r.raise_for_status()
                    
                    # 获取文件总大小
                    total_size = existing
                    if 'content-length' in r.headers:
                        total_size += int(r.headers['content-length'])
                    
                    self.status_updated.emit(self.url, f"下载中... (0%)")
                    
                    mode = 'ab' if existing > 0 else 'wb'
                    with open(self.save_path, mode) as f:
                        downloaded = existing
                        for chunk in r.iter_content(chunk_size=8192):
                            if self._stopped:
                                return
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                # 计算进度百分比
                                if total_size > 0:
                                    progress = int((downloaded / total_size) * 100)
                                    self.status_updated.emit(self.url, f"下载中... ({progress}%)")
                                
                                self.progress_updated.emit(self.url, downloaded)
                
                if not self._stopped:
                    self.download_finished.emit(self.url)
                return
                
            except requests.exceptions.Timeout:
                last_error = f"连接超时 ({self.timeout}秒)"
                retry_count += 1
            except requests.exceptions.ConnectionError:
                last_error = "网络连接错误"
                retry_count += 1
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    last_error = "文件不存在 (404)"
                    break  # 404错误不重试
                elif e.response.status_code == 403:
                    last_error = "访问被拒绝 (403)"
                    break  # 403错误不重试
                else:
                    last_error = f"HTTP错误: {e.response.status_code}"
                    retry_count += 1
            except Exception as e:
                last_error = f"未知错误: {str(e)}"
                retry_count += 1
            
            if retry_count <= self.max_retries and not self._stopped:
                # 等待一段时间后重试
                import time
                time.sleep(min(retry_count * 2, 10))  # 递增等待时间，最多10秒
        
        # 所有重试都失败了
        if not self._stopped:
            self.error_occurred.emit(self.url, last_error or "下载失败")

    def stop(self):
        self._stopped = True


# ============ 主界面 ============ #
class MediaDownloaderWidget(BaseContent):
    def __init__(self):
        self.extract_thread = None
        self.download_threads = []
        
        # 创建主要内容组件
        content_widget = self._create_content_widget()
        
        # 初始化基类
        super().__init__(title="媒体下载工具", content_widget=content_widget)

    def _create_content_widget(self):
        """创建主要内容区域组件 - 使用Bootstrap风格的网格布局"""
        
        # 🔗 URL输入组件
        url_group = QGroupBox("🌐 网页地址")
        url_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        url_group_layout = QVBoxLayout(url_group)
        
        self.url_input = QLineEdit()
        self.url_input.setObjectName("url_input")
        self.url_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.url_input.setPlaceholderText("请输入网页地址 (支持 http:// 或 https://)...")
        
        self.extract_button = QPushButton("🔍 提取媒体链接")
        self.extract_button.setMinimumWidth(140)
        self.extract_button.setStyleSheet(ButtonStyles.get_primary_style())
        self.extract_button.clicked.connect(self._start_extract)
        
        # Row 1: URL输入行 (Bootstrap col-9 + col-3)
        url_row = Row(
            Col(self.url_input, span=9),
            Col(self.extract_button, span=3, alignment=Qt.AlignCenter),
            spacing=15
        )
        url_group_layout.addLayout(url_row)

        # 下载配置组件
        settings_group = QGroupBox("⚙️ 下载配置")
        settings_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        settings_layout = QVBoxLayout(settings_group)

        # 超时设置组件
        timeout_widget = QWidget()
        timeout_layout = QHBoxLayout(timeout_widget)
        timeout_layout.setContentsMargins(0, 0, 0, 0)
        timeout_layout.addWidget(QLabel("超时时间:"))
        self.timeout_input = QLineEdit()
        self.timeout_input.setObjectName("timeout_input")
        self.timeout_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.timeout_input.setText("30")
        self.timeout_input.setFixedWidth(80)
        self.timeout_input.setPlaceholderText("30")
        timeout_layout.addWidget(self.timeout_input)
        timeout_layout.addWidget(QLabel("秒"))
        timeout_layout.addStretch()

        # 重试次数设置组件
        retry_widget = QWidget()
        retry_layout = QHBoxLayout(retry_widget)
        retry_layout.setContentsMargins(0, 0, 0, 0)
        retry_layout.addWidget(QLabel("重试次数:"))
        self.retry_input = QLineEdit()
        self.retry_input.setObjectName("retry_input")
        self.retry_input.setStyleSheet(LineEditStyles.get_standard_style())
        self.retry_input.setText("3")
        self.retry_input.setFixedWidth(80)
        self.retry_input.setPlaceholderText("3")
        retry_layout.addWidget(self.retry_input)
        retry_layout.addWidget(QLabel("次"))
        retry_layout.addStretch()

        # 保存路径设置组件
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.addWidget(QLabel("保存路径:"))
        self.path_entry = QLineEdit()
        self.path_entry.setObjectName("path_entry")
        self.path_entry.setStyleSheet(LineEditStyles.get_standard_style())
        self.path_entry.setPlaceholderText("选择文件保存目录...")
        self.browse_button = QPushButton("📂 浏览")
        self.browse_button.setMinimumWidth(80)
        self.browse_button.setStyleSheet(ButtonStyles.get_secondary_style())
        self.browse_button.clicked.connect(self._select_folder)
        path_layout.addWidget(self.path_entry)
        path_layout.addWidget(self.browse_button)

        # Row 3: 配置设置行 (Bootstrap col-6 + col-6)
        settings_row = Row(
            Col(timeout_widget, span=6),
            Col(retry_widget, span=6),
            spacing=20
        )
        settings_layout.addLayout(settings_row)

        self.video_cb = QCheckBox("🎥 视频文件")
        self.video_cb.setObjectName("video_checkbox")
        self.video_cb.setStyleSheet(CheckBoxStyles.get_standard_style("video_checkbox"))
        self.video_cb.setChecked(True)
        
        self.audio_cb = QCheckBox("🎵 音频文件")
        self.audio_cb.setObjectName("audio_checkbox")
        self.audio_cb.setStyleSheet(CheckBoxStyles.get_standard_style("audio_checkbox"))
        self.audio_cb.setChecked(True)
        
        self.image_cb = QCheckBox("🖼️ 图片文件")
        self.image_cb.setObjectName("image_checkbox")
        self.image_cb.setStyleSheet(CheckBoxStyles.get_standard_style("image_checkbox"))
        self.image_cb.setChecked(True)

        # Row 2: 媒体类型选择行 (Bootstrap col-4 + col-4 + col-4)
        media_type_row = Row(
            Col(self.video_cb, span=4),
            Col(self.audio_cb, span=4),
            Col(self.image_cb, span=4),
            spacing=15
        )
        settings_layout.addLayout(media_type_row)
        
        # Row 4: 保存路径行 (Bootstrap col-12)
        path_row = Row(
            Col(path_widget, span=12),
            spacing=15
        )
        settings_layout.addLayout(path_row)



        # 媒体文件列表组件
        list_group = QGroupBox("� 发现的媒体文件")
        list_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        list_layout = QVBoxLayout(list_group)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["📄 媒体文件URL", "📊 下载状态"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(False)
        
        # 应用Bootstrap风格的树形控件样式
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: 6px;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: {Colors.WECHAT_GREEN};
                font-size: 13px;
                gridline-color: #e9ecef;
            }}
            QTreeWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
                min-height: 25px;
            }}
            QTreeWidget::item:selected {{
                background-color: {Colors.WECHAT_GREEN};
                color: white;
            }}
            QTreeWidget::item:hover {{
                background-color: #e8f3ea;
            }}
            QHeaderView::section {{
                background-color: {Colors.BACKGROUND_SECONDARY};
                padding: 8px;
                border: 1px solid {Colors.BORDER_LIGHT};
                font-weight: bold;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        list_layout.addWidget(self.tree)

        # 操作控制组件

        control_group = QGroupBox("🎛️ 操作控制")
        control_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        control_layout = QVBoxLayout(control_group)
        
        self.clear_button = QPushButton("🧹 清空列表")
        self.clear_button.setMinimumWidth(100)
        self.clear_button.setStyleSheet(ButtonStyles.get_secondary_style())
        self.clear_button.clicked.connect(self._clear_all)
        
        self.stop_button = QPushButton("⏹️ 停止下载")
        self.stop_button.setMinimumWidth(100)
        self.stop_button.setStyleSheet(ButtonStyles.get_secondary_style())
        self.stop_button.clicked.connect(self._stop_all)
        self.stop_button.setEnabled(False)
        
        self.download_button = QPushButton("⬇️ 开始下载")
        self.download_button.setMinimumWidth(120)
        self.download_button.setStyleSheet(ButtonStyles.get_primary_style())
        self.download_button.clicked.connect(self._start_download)

        # Row 5: 控制按钮行 (Bootstrap col-3 + col-6 + col-3)
        control_row = Row(
            Col(self.clear_button, span=3),
            Spacer(span=6),  # 空白占位
            Col(self.stop_button, span=2),
            Col(self.download_button, span=1),
            spacing=10
        )
        control_layout.addLayout(control_row)

        # 下载进度组件
        progress_group = QGroupBox("📊 下载进度")
        progress_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress = QProgressBar()
        self.progress.setObjectName("download_progress")
        try:
            self.progress.setStyleSheet(ProgressBarStyles.get_standard_style("download_progress"))
        except AttributeError:
            # 如果没有ProgressBarStyles，使用基础样式
            self.progress.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {Colors.BORDER_LIGHT};
                    border-radius: 6px;
                    background-color: {Colors.BACKGROUND_LIGHT};
                    text-align: center;
                    font-size: 13px;
                    color: {Colors.TEXT_PRIMARY};
                    height: 25px;
                }}
                QProgressBar::chunk {{
                    background-color: {Colors.WECHAT_GREEN};
                    border-radius: 6px;
                }}
            """)
        
        progress_layout.addWidget(self.progress)

        # 使用Bootstrap容器组织所有内容
        content_widget = Container(
            Row(Col(url_group, span=12), spacing=15),                    # URL输入行
            Row(Col(settings_group, span=12), spacing=15),               # 配置设置行
            Row(Col(list_group, span=12), spacing=15),                   # 文件列表行
            Row(Col(control_group, span=12), spacing=15),                # 控制按钮行
            Row(Col(progress_group, span=12), spacing=15),               # 进度条行
            spacing=20,
            margins=(15, 15, 15, 15)
        )
        
        # 状态标签已由BaseContent类处理
        return content_widget

    def _get_selected_extensions(self):
        exts = []
        if self.video_cb.isChecked():
            exts += ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.webm']
        if self.audio_cb.isChecked():
            exts += ['.mp3', '.wav', '.aac', '.ogg', '.flac']
        if self.image_cb.isChecked():
            exts += ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return exts


    # 删除 _apply_styles 方法，现在使用全局样式和BaseContent

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if folder:
            self.path_entry.setText(folder)

    def _start_extract(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "警告", "请输入有效的网址")
            return
        
        # 简单的URL格式验证
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "警告", "请输入完整的网址（以http://或https://开头）")
            return
            
        extensions = self._get_selected_extensions()
        if not extensions:
            QMessageBox.warning(self, "警告", "请至少选择一个媒体类型")
            return
        
        self.tree.clear()
        self.progress.setValue(0)
        self.extract_button.setEnabled(False)
        self.set_status("🔍 正在分析网页并提取媒体链接...")
        
        self.extract_thread = MediaExtractThread(url, extensions)
        self.extract_thread.media_found.connect(self._populate_results)
        self.extract_thread.error_occurred.connect(self._extract_failed)
        self.extract_thread.start()

    def _extract_failed(self, error):
        self.extract_button.setEnabled(True)
        self.set_status(f"❌ 提取失败: {error}")
        
        # 更友好的错误提示
        if "timeout" in error.lower():
            QMessageBox.critical(self, "网络超时", "网页访问超时，请检查网络连接或稍后重试")
        elif "403" in error:
            QMessageBox.critical(self, "访问被拒绝", "网站拒绝访问，可能需要登录或该网站不允许爬取")
        elif "404" in error:
            QMessageBox.critical(self, "页面不存在", "指定的网页不存在，请检查网址是否正确")
        else:
            QMessageBox.critical(self, "提取失败", f"无法提取媒体链接:\n{error}")

    def _populate_results(self, urls):
        self.extract_button.setEnabled(True)
        
        if not urls:
            self.set_status("⚠️ 未找到任何媒体文件")
            QMessageBox.information(self, "提示", "在指定网页中未找到任何媒体文件\n\n请确认：\n1. 网页中确实包含媒体文件\n2. 已选择正确的媒体类型\n3. 媒体文件URL是直接链接")
            return
        
        self.set_status(f"✅ 提取完成，共找到 {len(urls)} 个媒体资源")
        
        for url in urls:
            item = QTreeWidgetItem([url, "📋 待下载"])
            item.setCheckState(0, Qt.Checked)
            self.tree.addTopLevelItem(item)
        
        # 自动展开列表以显示内容
        self.tree.expandAll()
        
        # 如果找到文件，给用户一个友好的提示
        if len(urls) > 0:
            QMessageBox.information(self, "提取成功", f"成功找到 {len(urls)} 个媒体文件！\n\n请选择保存目录，然后点击'开始下载'。")

    def _start_download(self):
        save_dir = self.path_entry.text().strip()
        if not os.path.exists(save_dir):
            QMessageBox.warning(self, "警告", "请选择有效的保存目录")
            return

        # 获取用户设置
        try:
            timeout = int(self.timeout_input.text() or "30")
            if timeout <= 0:
                timeout = 30
        except ValueError:
            timeout = 30

        try:
            max_retries = int(self.retry_input.text() or "3")
            if max_retries < 0:
                max_retries = 3
        except ValueError:
            max_retries = 3

        # 检查是否有选中的项目
        selected_count = 0
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                selected_count += 1

        if selected_count == 0:
            QMessageBox.information(self, "提示", "请至少选择一个文件进行下载")
            return

        self.download_threads.clear()
        self.progress.setRange(0, selected_count)
        self.progress.setValue(0)

        # 禁用下载按钮，启用停止按钮
        self.download_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                url = item.text(0)
                filename = os.path.basename(urlparse(url).path)
                
                # 如果URL没有文件名，生成一个
                if not filename or '.' not in filename:
                    import hashlib
                    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                    # 根据URL猜测文件类型
                    if any(ext in url.lower() for ext in ['.mp4', '.avi', '.mkv']):
                        filename = f"video_{url_hash}.mp4"
                    elif any(ext in url.lower() for ext in ['.mp3', '.wav', '.aac']):
                        filename = f"audio_{url_hash}.mp3"
                    else:
                        filename = f"media_{url_hash}.bin"
                
                save_path = os.path.join(save_dir, filename)

                thread = MediaDownloadThread(url, save_path, timeout, max_retries)
                thread.progress_updated.connect(lambda u, p: self._update_progress(u, p))
                thread.download_finished.connect(lambda u: self._mark_done(u))
                thread.error_occurred.connect(lambda u, e: self._mark_error(u, e))
                thread.status_updated.connect(lambda u, s: self._update_status(u, s))
                thread.start()
                self.download_threads.append(thread)

    def _mark_done(self, url):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.text(0) == url:
                item.setText(1, "✅ 完成")
                break
        
        self.progress.setValue(self.progress.value() + 1)
        filename = os.path.basename(urlparse(url).path) or "文件"
        self.set_status(f"✅ 完成下载: {filename}")
        
        # 检查是否所有下载都完成了
        self._check_all_downloads_complete()

    def _mark_error(self, url, error):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.text(0) == url:
                item.setText(1, f"❌ {error}")
                break
        
        self.progress.setValue(self.progress.value() + 1)
        filename = os.path.basename(urlparse(url).path) or "未知文件"
        self.set_status(f"❌ 下载失败: {filename} - {error}")
        
        # 检查是否所有下载都完成了
        self._check_all_downloads_complete()

    def _update_status(self, url, status):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.text(0) == url:
                item.setText(1, status)
                break

    def _update_progress(self, url, downloaded_bytes):
        # 可以在这里添加更详细的进度显示逻辑
        filename = os.path.basename(urlparse(url).path) or "文件"
        size_mb = downloaded_bytes / (1024 * 1024)
        self.set_status(f"⬇️ 正在下载 {filename}: {size_mb:.1f} MB")

    def _check_all_downloads_complete(self):
        """检查所有下载是否完成"""
        if self.progress.value() >= self.progress.maximum():
            self.download_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            # 统计下载结果
            completed = error = 0
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)
                status = item.text(1)
                if "✅" in status:
                    completed += 1
                elif "❌" in status:
                    error += 1
            
            if error == 0:
                self.set_status(f"🎉 下载完成! 成功下载 {completed} 个文件")
                QMessageBox.information(self, "完成", f"所有文件下载完成! 共 {completed} 个文件")
            else:
                self.set_status(f"⚠️ 下载完成! 成功: {completed}, 失败: {error}")
                QMessageBox.warning(self, "完成", f"下载完成! 成功: {completed}, 失败: {error}")

    def _stop_all(self):
        for thread in self.download_threads:
            thread.stop()
        
        # 重新启用下载按钮
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.set_status("⏹️ 已停止所有下载任务")
        
        # 更新未完成项目的状态
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            status = item.text(1)
            if "下载中" in status or "连接中" in status or "重试中" in status:
                item.setText(1, "⏹️ 已停止")

    def _clear_all(self):
        # 停止所有下载
        for thread in self.download_threads:
            thread.stop()
        
        self.tree.clear()
        self.progress.setValue(0)
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.set_status("🧹 已清空文件列表，可以重新开始")
