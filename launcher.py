#!/usr/bin/env python3
"""
无控制台窗口启动器
解决多个console窗口闪现问题
"""

import os
import sys

def main():
    """主入口 - 无控制台启动"""
    
    # 设置环境变量禁用调试输出
    os.environ['KIWIKIT_DEBUG'] = 'False'
    os.environ['PYTHONUNBUFFERED'] = '0'
    
    # 重定向标准输出到空设备，避免控制台输出
    if os.name == 'nt':  # Windows
        try:
            import sys
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
        except:
            pass
    
    try:
        # 直接导入并执行main.py的内容
        import main
        
    except Exception as e:
        # 静默处理错误，写入日志文件
        try:
            import traceback
            from pathlib import Path
            from datetime import datetime
            
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            error_msg = f"[{datetime.now()}] 启动错误: {e}\\n{traceback.format_exc()}\\n\\n"
            
            with open(log_dir / "startup_error.log", "a", encoding="utf-8") as f:
                f.write(error_msg)
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()