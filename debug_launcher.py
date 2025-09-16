"""
调试启动器 - 保留错误输出
"""

import sys
import os
from pathlib import Path

# 设置环境变量但不完全静默
os.environ['KIWIKIT_NO_CONSOLE'] = 'false'  # 允许错误输出
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 导入并启动主应用
if __name__ == "__main__":
    try:
        # 导入主模块
        from main import main
        main()
    except Exception as e:
        # 显示错误信息用于调试
        import traceback
        print(f"启动失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        input("按回车键退出...")
