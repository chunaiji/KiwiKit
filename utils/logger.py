"""
全局日志系统
支持按日期分类保存日志，包含错误、信息、警告等级别
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class GlobalLogger:
    """全局日志管理器"""
    
    _instance: Optional['GlobalLogger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.logger = None
        self.log_dir = None
        self._initialized = True
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志配置"""
        # 获取当前日期作为文件夹名
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 创建按日期分层的日志目录：logs/2025-09-11/
        self.log_dir = Path("logs") / today
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建主logger
        self.logger = logging.getLogger('KiwiKit')
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if self.logger.handlers:
            return
        
        # 创建格式化器
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器 - 在生产环境中完全禁用
        # 检查多个条件确保生产环境不会有控制台输出
        debug_mode = (
            os.getenv('KIWIKIT_DEBUG', 'False').lower() == 'true' or 
            '--debug' in sys.argv or
            os.getenv('PYTHONDEBUG', '') != '' or
            hasattr(sys, 'gettrace') and sys.gettrace() is not None  # 检查调试器
        )
        
        # 额外检查：如果设置了完全静默模式，强制禁用控制台
        no_console = (
            os.getenv('KIWIKIT_NO_CONSOLE', 'False').lower() == 'true' or
            not hasattr(sys.stdout, 'isatty') or  # 没有真实的终端
            (hasattr(sys.stdout, 'isatty') and not sys.stdout.isatty())  # 输出被重定向
        )
        
        if debug_mode and not no_console:
            try:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
            except Exception:
                # 如果控制台处理器创建失败，静默忽略
                pass
        
        # 文件处理器 - 按日期分文件
        self._setup_file_handlers(formatter)
        
        # 设置异常钩子
        self._setup_exception_hook()
    
    def _setup_file_handlers(self, formatter):
        """设置文件处理器"""
        # 由于日志已经按日期分文件夹，文件名不需要再包含日期
        # 所有日志文件
        all_log_file = self.log_dir / "all.log"
        all_handler = RotatingFileHandler(
            all_log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        all_handler.setLevel(logging.DEBUG)
        all_handler.setFormatter(formatter)
        self.logger.addHandler(all_handler)
        
        # 错误日志文件
        error_log_file = self.log_dir / "error.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # 警告日志文件
        warning_log_file = self.log_dir / "warning.log"
        warning_handler = RotatingFileHandler(
            warning_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        warning_handler.setLevel(logging.WARNING)
        warning_handler.setFormatter(formatter)
        self.logger.addHandler(warning_handler)
    
    def _setup_exception_hook(self):
        """设置全局异常捕获"""
        def exception_handler(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # 允许正常的键盘中断
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # 记录未捕获的异常到文件
            try:
                self.logger.critical(
                    "未捕获的异常",
                    exc_info=(exc_type, exc_value, exc_traceback)
                )
            except Exception:
                # 如果日志记录失败，完全静默
                pass
            
            # 在生产环境中不显示异常到控制台
            if os.getenv('KIWIKIT_NO_CONSOLE', 'False').lower() == 'true':
                # 完全静默，不调用原始异常处理器
                pass
            else:
                # 仅在开发环境显示异常
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = exception_handler
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """获取日志器实例"""
        if name:
            return logging.getLogger(f'KiwiKit.{name}')
        return self.logger
    
    def debug(self, message: str, *args, **kwargs):
        """调试日志"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """信息日志"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """警告日志"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """错误日志"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """异常日志（自动包含traceback）"""
        self.logger.exception(message, *args, **kwargs)
    
    def log_function_call(self, func_name: str, *args, **kwargs):
        """记录函数调用"""
        self.debug(f"调用函数: {func_name} - args: {args}, kwargs: {kwargs}")
    
    def log_user_action(self, action: str, details: str = ""):
        """记录用户操作"""
        self.info(f"用户操作: {action} - {details}")
    
    def log_system_event(self, event: str, details: str = ""):
        """记录系统事件"""
        self.info(f"系统事件: {event} - {details}")
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """清理旧日志文件"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    self.info(f"已删除旧日志文件: {log_file.name}")
        except Exception as e:
            self.error(f"清理旧日志文件时出错: {e}")
    
    @classmethod
    def setup_exception_handling(cls):
        """设置全局异常处理"""
        instance = cls()
        instance._setup_exception_hook()


# 创建全局日志实例
_global_logger = GlobalLogger()

# 导出常用函数
def get_logger(name: str = None) -> logging.Logger:
    """获取日志器实例"""
    return _global_logger.get_logger(name)

def debug(message: str, *args, **kwargs):
    """调试日志"""
    _global_logger.debug(message, *args, **kwargs)

def info(message: str, *args, **kwargs):
    """信息日志"""
    _global_logger.info(message, *args, **kwargs)

def warning(message: str, *args, **kwargs):
    """警告日志"""
    _global_logger.warning(message, *args, **kwargs)

def error(message: str, *args, **kwargs):
    """错误日志"""
    _global_logger.error(message, *args, **kwargs)

def critical(message: str, *args, **kwargs):
    """严重错误日志"""
    _global_logger.critical(message, *args, **kwargs)

def exception(message: str, *args, **kwargs):
    """异常日志（自动包含traceback）"""
    _global_logger.exception(message, *args, **kwargs)

def log_function_call(func_name: str, *args, **kwargs):
    """记录函数调用"""
    _global_logger.log_function_call(func_name, *args, **kwargs)

def log_user_action(action: str, details: str = ""):
    """记录用户操作"""
    _global_logger.log_user_action(action, details)

def log_system_event(event: str, details: str = ""):
    """记录系统事件"""
    _global_logger.log_system_event(event, details)

def cleanup_old_logs(days_to_keep: int = 30):
    """清理旧日志文件"""
    _global_logger.cleanup_old_logs(days_to_keep)


# 装饰器工具
def log_errors(func):
    """错误日志装饰器"""
    def wrapper(*args, **kwargs):
        try:
            log_function_call(f"{func.__module__}.{func.__name__}", *args, **kwargs)
            return func(*args, **kwargs)
        except Exception as e:
            exception(f"函数 {func.__name__} 执行出错: {e}")
            raise
    return wrapper

def log_performance(func):
    """性能日志装饰器"""
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            info(f"函数 {func.__name__} 执行耗时: {end_time - start_time:.4f}秒")
            return result
        except Exception as e:
            end_time = time.time()
            error(f"函数 {func.__name__} 执行失败 (耗时: {end_time - start_time:.4f}秒): {e}")
            raise
    return wrapper
