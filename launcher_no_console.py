"""
无控制台启动器
确保应用程序以无控制台模式启动
"""

import sys
import os
from pathlib import Path

# 立即禁用控制台输出
if hasattr(sys, '_getframe'):
    try:
        # 尝试隐藏控制台窗口
        import ctypes
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        
        # 获取控制台窗口句柄
        console_window = kernel32.GetConsoleWindow()
        if console_window:
            # 隐藏控制台窗口
            user32.ShowWindow(console_window, 0)  # SW_HIDE
    except:
        pass  # 忽略任何错误

# 设置环境变量确保完全静默模式
os.environ['KIWIKIT_NO_CONSOLE'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 重定向所有输出到空设备
try:
    import io
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
except:
    pass

# 导入并启动主应用
if __name__ == "__main__":
    try:
        # 导入主模块
        from main import main
        main()
    except Exception:
        # 完全静默，不显示任何错误
        pass
