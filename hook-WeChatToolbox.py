"""
PyInstaller hook for WeChatToolbox application
确保所有必要的 PySide6 模块被正确包含
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

# 收集 PySide6 的所有子模块
datas, binaries, hiddenimports = collect_all('PySide6')

# 添加额外的隐式导入
hiddenimports += [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'PySide6.QtOpenGL',
    'PySide6.QtSvg',
    'PySide6.QtSql',
    'PySide6.QtPrintSupport',
]

# 收集应用程序模块
app_modules = [
    'components',
    'styles', 
    'utils',
    'config',
]

for module in app_modules:
    try:
        hiddenimports += collect_submodules(module)
    except Exception:
        pass  # 忽略收集错误

print(f"Hook: 收集到 {len(hiddenimports)} 个隐式导入")
print(f"Hook: 收集到 {len(datas)} 个数据文件")
print(f"Hook: 收集到 {len(binaries)} 个二进制文件")