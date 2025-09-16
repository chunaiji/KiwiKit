"""
扩展版 文件查找工具组件
功能（在原有基础上追加）：
- 搜索与匹配：支持正则测试（独立工具）、全文搜索、正则搜索、查找替换（对选中文本文件可批量替换并备份原文件）
- 文本处理：排序、去重、大小写转换（upper/lower/title）、统计（行数/词数/字符数）、导出处理结果

说明：把该文件放入你的工程中，并确保有 styles 模块或按需替换样式。依赖：PySide6
"""

import os
import fnmatch
import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QLabel, QTreeWidget, QTreeWidgetItem,
                               QFileDialog, QMessageBox, QProgressBar, QCheckBox,
                               QSplitter, QTextEdit, QGroupBox, QPushButton, QComboBox,
                               QRadioButton, QButtonGroup, QFrame)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from components.base_content import BaseContent
from styles.constants import Colors
from styles.widgets import (
    ButtonStyles, LineEditStyles, TextEditStyles, GroupBoxStyles,
    CheckBoxStyles, ProgressBarStyles
)


class FileSearchThread(QThread):
    """文件搜索线程"""
    file_found = Signal(str, str, int)  # file_path, relative_path, size
    search_finished = Signal(int)  # total_files_found
    progress_updated = Signal(int)  # processed_count

    def __init__(self, search_path, search_pattern, search_content="", case_sensitive=False, mode='filename'):
        super().__init__()
        self.search_path = search_path
        self.search_pattern = search_pattern
        self.search_content = search_content
        self.case_sensitive = case_sensitive
        self.mode = mode  # 'filename', 'fulltext', 'regex'
        self.stopped = False

    def run(self):
        found_count = 0
        processed_count = 0
        try:
            # 如果是正则模式，提前编译
            regex = None
            if self.mode == 'regex' and self.search_pattern:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                try:
                    regex = re.compile(self.search_pattern, flags=flags)
                except re.error:
                    regex = None

            for root, dirs, files in os.walk(self.search_path):
                if self.stopped:
                    break
                for file in files:
                    if self.stopped:
                        break
                    processed_count += 1
                    if processed_count % 10 == 0:
                        self.progress_updated.emit(processed_count)

                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.search_path)

                    try:
                        matched = False
                        # 模式匹配
                        if self.mode == 'filename':
                            pattern = self.search_pattern or '*'
                            name = file if self.case_sensitive else file.lower()
                            pat = pattern if self.case_sensitive else pattern.lower()
                            if fnmatch.fnmatch(name, pat):
                                matched = True
                        elif self.mode == 'regex' and regex:
                            # 检查文件名或相对路径
                            target = file if self.case_sensitive else file
                            if regex.search(target):
                                matched = True
                            else:
                                # 也尝试针对相对路径
                                if regex.search(relative_path):
                                    matched = True
                        elif self.mode == 'fulltext':
                            # 先判断是否文本文件，然后在内容中搜索字符串或正则
                            if self._is_text_file(file_path):
                                content = None
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                except Exception:
                                    content = None
                                if content is not None and self.search_pattern:
                                    if self.case_sensitive:
                                        if self.search_pattern in content:
                                            matched = True
                                    else:
                                        if self.search_pattern.lower() in content.lower():
                                            matched = True

                        if matched:
                            size = 0
                            try:
                                size = os.path.getsize(file_path)
                            except Exception:
                                size = 0
                            self.file_found.emit(file_path, relative_path, size)
                            found_count += 1
                    except (OSError, PermissionError):
                        continue
        except Exception:
            pass
        self.search_finished.emit(found_count)

    def _is_text_file(self, file_path):
        text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md', '.rst', '.ini', '.cfg', '.log', '.csv'}
        _, ext = os.path.splitext(file_path.lower())
        return ext in text_extensions

    def stop(self):
        self.stopped = True


class FileSearchWidget(BaseContent):
    """文件查找工具界面（扩展）"""

    def __init__(self):
        self.search_thread = None
        
        # 创建主要内容组件
        content_widget = self._create_content_widget()
        
        # 初始化基类
        super().__init__(title="文件查找与文本处理", content_widget=content_widget)

    def _create_content_widget(self):
        """创建主要内容区域组件 - 使用全局样式"""
        
        # 主容器
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 🔍 搜索设置组件
        search_group = QGroupBox("🔍 搜索设置")
        search_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        search_layout = QVBoxLayout(search_group)

        folder_layout = QHBoxLayout()
        folder_label = QLabel("搜索目录:")
        folder_label.setMinimumWidth(80)
        self.path_entry = QLineEdit()
        self.path_entry.setPlaceholderText("请选择要搜索的文件夹...")
        self.path_entry.setStyleSheet(LineEditStyles.get_standard_style())
        
        self.browse_button = QPushButton("📁 浏览")
        self.browse_button.setStyleSheet(ButtonStyles.get_secondary_style())
        self.browse_button.clicked.connect(self._select_folder)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.path_entry)
        folder_layout.addWidget(self.browse_button)
        search_layout.addLayout(folder_layout)

        # 搜索模式（文件名 / 正则 / 全文）
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("搜索模式:"))
        self.mode_group = QButtonGroup()
        
        self.rb_filename = QRadioButton("📄 文件名")
        self.rb_regex = QRadioButton("🔤 正则")
        self.rb_fulltext = QRadioButton("📖 全文")
        self.rb_filename.setChecked(True)
        
        # 应用复选框样式到单选按钮
        for rb in [self.rb_filename, self.rb_regex, self.rb_fulltext]:
            rb.setStyleSheet(CheckBoxStyles.get_standard_style())
        
        self.mode_group.addButton(self.rb_filename)
        self.mode_group.addButton(self.rb_regex)
        self.mode_group.addButton(self.rb_fulltext)
        
        mode_layout.addWidget(self.rb_filename)
        mode_layout.addWidget(self.rb_regex)
        mode_layout.addWidget(self.rb_fulltext)
        mode_layout.addStretch()
        search_layout.addLayout(mode_layout)

        pattern_layout = QHBoxLayout()
        pattern_label = QLabel("模式 / 内容:")
        pattern_label.setMinimumWidth(80)
        self.pattern_entry = QLineEdit()
        self.pattern_entry.setPlaceholderText("文件名模式或正则或全文搜索文本")
        self.pattern_entry.setText("*.*")
        self.pattern_entry.setStyleSheet(LineEditStyles.get_standard_style())
        pattern_layout.addWidget(pattern_label)
        pattern_layout.addWidget(self.pattern_entry)
        search_layout.addLayout(pattern_layout)

        # 🧪 正则测试小工具
        regex_tool_layout = QHBoxLayout()
        self.regex_test_input = QLineEdit()
        self.regex_test_input.setPlaceholderText("正则测试：在这里输入示例文本")
        self.regex_test_input.setStyleSheet(LineEditStyles.get_standard_style())
        
        self.regex_pattern_input = QLineEdit()
        self.regex_pattern_input.setPlaceholderText("正则表达式（示例: \\d{4}|error.*）")
        self.regex_pattern_input.setStyleSheet(LineEditStyles.get_standard_style())
        
        self.regex_test_btn = QPushButton("🧪 正则测试")
        self.regex_test_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.regex_test_btn.clicked.connect(self._regex_test)
        
        regex_tool_layout.addWidget(QLabel("示例文本:"))
        regex_tool_layout.addWidget(self.regex_test_input)
        regex_tool_layout.addWidget(QLabel("模式:"))
        regex_tool_layout.addWidget(self.regex_pattern_input)
        regex_tool_layout.addWidget(self.regex_test_btn)
        search_layout.addLayout(regex_tool_layout)

        # 📝 内容搜索选项
        content_layout = QHBoxLayout()
        self.content_entry = QLineEdit()
        self.content_entry.setPlaceholderText("（可选）在文件内容中搜索的文本/正则")
        self.content_entry.setStyleSheet(LineEditStyles.get_standard_style())
        
        self.case_sensitive_cb = QCheckBox("🔤 区分大小写")
        self.case_sensitive_cb.setStyleSheet(CheckBoxStyles.get_standard_style())
        
        content_layout.addWidget(QLabel("内容:"))
        content_layout.addWidget(self.content_entry)
        content_layout.addWidget(self.case_sensitive_cb)
        search_layout.addLayout(content_layout)

        # ⚡ 操作按钮
        options_layout = QHBoxLayout()
        self.search_button = QPushButton("🔍 开始搜索")
        self.search_button.setStyleSheet(ButtonStyles.get_primary_style())
        self.search_button.clicked.connect(self._start_search)
        
        self.stop_button = QPushButton("⏹ 停止搜索")
        self.stop_button.setStyleSheet(ButtonStyles.get_secondary_style())
        self.stop_button.clicked.connect(self._stop_search)
        self.stop_button.setEnabled(False)
        
        self.clear_button = QPushButton("🧹 清空结果")
        self.clear_button.setStyleSheet(ButtonStyles.get_secondary_style())
        self.clear_button.clicked.connect(self._clear_results)
        
        options_layout.addStretch()
        options_layout.addWidget(self.clear_button)
        options_layout.addWidget(self.search_button)
        options_layout.addWidget(self.stop_button)
        search_layout.addLayout(options_layout)

        layout.addWidget(search_group)

        # 📊 中间分割：结果 & 处理工具
        splitter = QSplitter(Qt.Vertical)

        # 📋 结果显示区域
        result_frame = QFrame()
        rlayout = QVBoxLayout(result_frame)
        
        # 结果树组件
        result_group = QGroupBox("📋 搜索结果")
        result_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        result_tree_layout = QVBoxLayout(result_group)
        
        self.result_tree = QTreeWidget()
        self.result_tree.setHeaderLabels(["文件名", "相对路径", "大小"])
        self.result_tree.setAlternatingRowColors(True)
        self.result_tree.itemClicked.connect(self._preview_file)
        self.result_tree.itemSelectionChanged.connect(self._on_selection_changed)
        result_tree_layout.addWidget(self.result_tree)
        rlayout.addWidget(result_group)

        # 👁️ 文件预览组件
        preview_group = QGroupBox("👁️ 文件预览 / 文本聚合")
        preview_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        pv_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(False)
        self.preview_text.setMaximumHeight(220)
        self.preview_text.setObjectName("preview_text")
        self.preview_text.setStyleSheet(TextEditStyles.get_standard_style("preview_text"))
        pv_layout.addWidget(self.preview_text)

        # 预览工具按钮
        pv_tool_layout = QHBoxLayout()
        self.aggregate_btn = QPushButton("📝 聚合选中文本到预览")
        self.aggregate_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.aggregate_btn.clicked.connect(self._aggregate_selected_to_preview)
        
        self.reload_btn = QPushButton("🔄 重新加载选中文件")
        self.reload_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.reload_btn.clicked.connect(self._preview_selected_file)
        
        pv_tool_layout.addWidget(self.aggregate_btn)
        pv_tool_layout.addWidget(self.reload_btn)
        pv_tool_layout.addStretch()
        pv_layout.addLayout(pv_tool_layout)

        rlayout.addWidget(preview_group)
        splitter.addWidget(result_frame)

        # 🛠️ 文本处理面板
        text_tool_group = QGroupBox("🛠️ 文本处理与查找替换")
        text_tool_group.setStyleSheet(GroupBoxStyles.get_standard_style())
        tt_layout = QVBoxLayout(text_tool_group)

        # 🔍 查找替换行
        fr_layout = QHBoxLayout()
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("查找（支持正则，勾选右侧正则开关）")
        self.find_input.setStyleSheet(LineEditStyles.get_standard_style())
        
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("替换为（留空表示删除）")
        self.replace_input.setStyleSheet(LineEditStyles.get_standard_style())
        
        self.fr_regex_cb = QCheckBox("🔤 正则")
        self.fr_regex_cb.setStyleSheet(CheckBoxStyles.get_standard_style())
        
        self.fr_case_cb = QCheckBox("🔤 区分大小写")
        self.fr_case_cb.setStyleSheet(CheckBoxStyles.get_standard_style())
        
        self.replace_btn = QPushButton("🔄 替换并保存到选中文件（备份原文件 .bak）")
        self.replace_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.replace_btn.clicked.connect(self._replace_in_files)
        
        fr_layout.addWidget(QLabel("查找:"))
        fr_layout.addWidget(self.find_input)
        fr_layout.addWidget(QLabel("替换:"))
        fr_layout.addWidget(self.replace_input)
        fr_layout.addWidget(self.fr_regex_cb)
        fr_layout.addWidget(self.fr_case_cb)
        fr_layout.addWidget(self.replace_btn)
        tt_layout.addLayout(fr_layout)

        # ⚙️ 文本处理操作：排序、去重、大小写转换、统计、导出
        tp_layout = QHBoxLayout()
        
        self.sort_btn = QPushButton("📊 排序 (asc)")
        self.sort_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.sort_btn.clicked.connect(self._sort_preview)
        
        self.uniq_btn = QPushButton("🔄 去重")
        self.uniq_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.uniq_btn.clicked.connect(self._uniq_preview)
        
        self.upper_btn = QPushButton("🔤 大写")
        self.upper_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.upper_btn.clicked.connect(lambda: self._case_convert('upper'))
        
        self.lower_btn = QPushButton("🔡 小写")
        self.lower_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.lower_btn.clicked.connect(lambda: self._case_convert('lower'))
        
        self.title_btn = QPushButton("🔠 首字母大写")
        self.title_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.title_btn.clicked.connect(lambda: self._case_convert('title'))
        
        self.stats_btn = QPushButton("📈 统计")
        self.stats_btn.setStyleSheet(ButtonStyles.get_secondary_style())
        self.stats_btn.clicked.connect(self._stats_preview)
        
        self.export_btn = QPushButton("💾 导出为文件")
        self.export_btn.setStyleSheet(ButtonStyles.get_primary_style())
        self.export_btn.clicked.connect(self._export_preview_to_file)
        
        tp_layout.addWidget(self.sort_btn)
        tp_layout.addWidget(self.uniq_btn)
        tp_layout.addWidget(self.upper_btn)
        tp_layout.addWidget(self.lower_btn)
        tp_layout.addWidget(self.title_btn)
        tp_layout.addWidget(self.stats_btn)
        tp_layout.addWidget(self.export_btn)
        tt_layout.addLayout(tp_layout)

        splitter.addWidget(text_tool_group)
        splitter.setSizes([400, 200])
        layout.addWidget(splitter)

        # 📊 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(ProgressBarStyles.get_standard_style())
        layout.addWidget(self.progress_bar)

        # 状态标签已由BaseContent类处理
        return main_widget



    # -------------- 搜索逻辑 --------------
    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择搜索目录")
        if folder:
            self.path_entry.setText(folder)

    def _start_search(self):
        search_path = self.path_entry.text().strip()
        pattern = self.pattern_entry.text().strip()
        content = self.content_entry.text().strip()
        case_sensitive = self.case_sensitive_cb.isChecked()
        mode = 'filename'
        if self.rb_regex.isChecked():
            mode = 'regex'
        elif self.rb_fulltext.isChecked():
            mode = 'fulltext'

        if not search_path or not os.path.exists(search_path):
            QMessageBox.warning(self, "警告", "请选择有效的搜索目录")
            return
        if not pattern:
            pattern = '*.*'

        self.result_tree.clear(); self.preview_text.clear()
        self.search_button.setEnabled(False); self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True); self.progress_bar.setRange(0, 0)
        self.set_status("搜索中...")

        self.search_thread = FileSearchThread(search_path, pattern, content, case_sensitive, mode)
        self.search_thread.file_found.connect(self._add_result)
        self.search_thread.search_finished.connect(self._search_finished)
        self.search_thread.progress_updated.connect(self._update_progress)
        self.search_thread.start()

    def _stop_search(self):
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.stop(); self.search_thread.wait()
        self._search_finished(self.result_tree.topLevelItemCount())

    def _clear_results(self):
        self.result_tree.clear(); self.preview_text.clear(); self.set_status("已清空结果")

    def _add_result(self, file_path, relative_path, file_size):
        item = QTreeWidgetItem(self.result_tree)
        item.setText(0, os.path.basename(file_path)); item.setText(1, relative_path); item.setText(2, self._format_size(file_size))
        item.setData(0, Qt.UserRole, file_path)

    def _search_finished(self, total_found):
        self.search_button.setEnabled(True); self.stop_button.setEnabled(False); self.progress_bar.setVisible(False)
        self.set_status(f"搜索完成，找到 {total_found} 个文件")
        if self.search_thread:
            self.search_thread.deleteLater(); self.search_thread = None

    def _update_progress(self, processed):
        self.set_status(f"已处理 {processed} 个文件...")

    # -------------- 预览与聚合 --------------
    def _preview_file(self, item):
        path = item.data(0, Qt.UserRole)
        if not path or not os.path.exists(path):
            return
        try:
            if self._is_text_file(path):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(20000)
                self.preview_text.setPlainText(content)
            else:
                self.preview_text.setPlainText(f"[二进制文件] {os.path.basename(path)}")
        except Exception as e:
            self.preview_text.setPlainText(f"无法预览: {e}")

    def _on_selection_changed(self):
        # 当选择改变时启用相关按钮（如果需要）
        selected = self.result_tree.selectedItems()
        self.aggregate_btn.setEnabled(len(selected) > 0)
        self.reload_btn.setEnabled(len(selected) == 1)

    def _aggregate_selected_to_preview(self):
        items = self.result_tree.selectedItems()
        if not items:
            QMessageBox.information(self, "提示", "请先选择要聚合的文件行")
            return
        lines = []
        for it in items:
            path = it.data(0, Qt.UserRole)
            if path and os.path.exists(path) and self._is_text_file(path):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines.append(f.read())
                except Exception:
                    continue
        self.preview_text.setPlainText('\n\n--- 文件分隔 ---\n\n'.join(lines))
        self.set_status(f"已聚合 {len(lines)} 个文件到预览区")

    def _preview_selected_file(self):
        items = self.result_tree.selectedItems()
        if len(items) != 1:
            QMessageBox.information(self, "提示", "请选择单个文件以重新加载内容")
            return
        self._preview_file(items[0])

    # -------------- 文本处理工具 --------------
    def _regex_test(self):
        pattern = self.regex_pattern_input.text() or ''
        sample = self.regex_test_input.text() or ''
        if not pattern:
            QMessageBox.information(self, "正则测试", "请输入正则表达式")
            return
        try:
            prog = re.compile(pattern)
            matches = prog.findall(sample)
            QMessageBox.information(self, "正则测试结果", f"匹配数: {len(matches)}\n示例匹配: {matches[:10]}")
        except re.error as e:
            QMessageBox.warning(self, "正则错误", f"正则表达式错误: {e}")

    def _replace_in_files(self):
        find = self.find_input.text()
        replace = self.replace_input.text()
        use_regex = self.fr_regex_cb.isChecked()
        case_sensitive = self.fr_case_cb.isChecked()
        items = self.result_tree.selectedItems()
        if not find:
            QMessageBox.information(self, "提示", "请输入要查找的内容")
            return
        if not items:
            QMessageBox.information(self, "提示", "请先选择要操作的文件（仅文本文件）")
            return
        # 执行替换并备份
        failures = []
        modified = 0
        for it in items:
            path = it.data(0, Qt.UserRole)
            if not path or not os.path.exists(path) or not self._is_text_file(path):
                continue
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                new_content = content
                if use_regex:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    try:
                        new_content = re.sub(find, replace, content, flags=flags)
                    except re.error as e:
                        failures.append((path, str(e)))
                        continue
                else:
                    if case_sensitive:
                        new_content = content.replace(find, replace)
                    else:
                        # 不区分大小写的替换：使用 re with re.IGNORECASE but preserve case is complex; we do simple approach
                        pattern = re.compile(re.escape(find), re.IGNORECASE)
                        new_content = pattern.sub(replace, content)
                if new_content != content:
                    # 备份
                    bak = path + '.bak'
                    try:
                        if not os.path.exists(bak):
                            with open(bak, 'w', encoding='utf-8', errors='ignore') as bf:
                                bf.write(content)
                    except Exception:
                        pass
                    with open(path, 'w', encoding='utf-8', errors='ignore') as f:
                        f.write(new_content)
                    modified += 1
            except Exception as e:
                failures.append((path, str(e)))
        QMessageBox.information(self, "替换完成", f"已修改 {modified} 个文件。失败: {len(failures)} 个。")
        self.set_status(f"替换完成：修改 {modified} 个文件")

    def _sort_preview(self):
        text = self.preview_text.toPlainText()
        if not text:
            return
        lines = text.splitlines()
        lines.sort()
        self.preview_text.setPlainText('\n'.join(lines))
        self.set_status('已排序（升序）')

    def _uniq_preview(self):
        text = self.preview_text.toPlainText()
        if not text:
            return
        lines = text.splitlines()
        seen = set(); out = []
        for l in lines:
            if l not in seen:
                seen.add(l); out.append(l)
        self.preview_text.setPlainText('\n'.join(out))
        self.set_status('已去重')

    def _case_convert(self, mode='upper'):
        text = self.preview_text.toPlainText();
        if not text:
            return
        if mode == 'upper':
            self.preview_text.setPlainText(text.upper())
            self.set_status('已转换为大写')
        elif mode == 'lower':
            self.preview_text.setPlainText(text.lower())
            self.set_status('已转换为小写')
        elif mode == 'title':
            self.preview_text.setPlainText(text.title())
            self.set_status('已转换为首字母大写')

    def _stats_preview(self):
        text = self.preview_text.toPlainText()
        if text is None:
            return
        lines = text.splitlines(); line_count = len(lines)
        word_count = sum(len(l.split()) for l in lines)
        char_count = len(text)
        QMessageBox.information(self, "统计结果", f"行数: {line_count}\n词数: {word_count}\n字符数: {char_count}")

    def _export_preview_to_file(self):
        text = self.preview_text.toPlainText()
        if not text:
            QMessageBox.information(self, "导出", "预览区为空，无内容可导出")
            return
        p, _ = QFileDialog.getSaveFileName(self, "导出为文本文件", "export.txt", "Text files (*.txt);;All Files (*)")
        if p:
            try:
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "导出", f"已导出: {p}")
                self.set_status(f"已导出到 {p}")
            except Exception as e:
                QMessageBox.warning(self, "导出失败", str(e))

    # -------------- 辅助方法 --------------
    def _is_text_file(self, file_path):
        text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md', '.rst', '.ini', '.cfg', '.log', '.csv'}
        _, ext = os.path.splitext(file_path.lower())
        return ext in text_extensions

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

