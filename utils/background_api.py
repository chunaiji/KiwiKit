"""
后台API请求服务
程序启动时自动进行后台API请求，用户无感知
"""

import json
import time
import threading
from typing import Dict, Any, Optional, Callable
from PySide6.QtCore import QObject, Signal, QTimer, QThread

from utils.api_client import ApiClient, ApiResponse
from utils.logger import get_logger
from utils.user_info import get_unique_identifier
from config.app_config import AppConfig


class BackgroundApiService(QObject):
    """后台API服务"""
    
    # 信号定义
    api_success = Signal(str, dict)  # API请求成功
    api_failed = Signal(str, str)   # API请求失败
    service_started = Signal()      # 服务启动
    service_stopped = Signal()      # 服务停止
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        
        # API配置
        self.api_base_url = "https://ambertu.com"
        self.api_client = None  # 延迟初始化，在主线程中创建
        
        # 服务状态
        self.is_running = False
        self.startup_timer = QTimer()
        self.startup_timer.setSingleShot(True)
        self.startup_timer.timeout.connect(self._perform_startup_requests)
        
        # 请求配置
        self.startup_delay = 3000  # 启动延迟3秒
        self.request_timeout = 10  # 请求超时10秒
        
        self.logger.info("后台API服务初始化完成")
    
    def _ensure_api_client(self):
        """确保API客户端在主线程中创建"""
        if self.api_client is None:
            self.api_client = ApiClient(self.api_base_url)
            self.logger.info("在主线程中创建API客户端")
    
    def start_service(self):
        """启动后台API服务"""
        if self.is_running:
            self.logger.warning("后台API服务已在运行中")
            return
        
        self.is_running = True
        self.logger.info(f"启动后台API服务，{self.startup_delay/1000}秒后开始请求")
        
        # 确保在主线程中初始化API客户端
        self._ensure_api_client()
        
        # 延迟启动，让主程序完全加载完成
        self.startup_timer.start(self.startup_delay)
        self.service_started.emit()
    
    def stop_service(self):
        """停止后台API服务"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.startup_timer.stop()
        self.api_client.cancel_all_requests()
        
        # self.logger.info("后台API服务已停止")
        self.service_stopped.emit()
    
    def _perform_startup_requests(self):
        """执行启动时的API请求"""
        if not self.is_running:
            return
        
        # self.logger.info("开始执行后台API请求")
        
        # 直接在主线程中执行API请求（Qt网络组件必须在主线程中使用）
        self._background_api_calls()
    
    def _background_api_calls(self):
        """后台API调用（在主线程中执行）"""
        try:
            # 请求1：插入代码接口
            self._insert_code_request()
            
            # 可以在这里添加更多启动时需要的API请求
            # self._other_startup_request()
            
        except Exception as e:
            self.logger.error(f"后台API请求发生异常: {e}")
    
    def _insert_code_request(self):
        """插入代码API请求"""
        try:
            # 确保API客户端在主线程中创建
            self._ensure_api_client()
            
            # self.logger.info("发送插入代码请求")
            
            # 构造请求数据
            device_id = get_unique_identifier()
            request_data = {
                "MemberId": device_id[:8],  # 使用设备ID的前8位作为MemberId
                "CodeContent": device_id,   # 使用完整设备ID作为CodeContent
                "BatchNo": "info",  # 使用固定值作为BatchNo
                "MerchantId": "8f86b406180a4303a87108eaeab7f351",
                "TenantId": "e25d142b7cc34b8d9818145671030354",
                "IsDeleted": True  
            }
            
            # 设置请求头 - 使用更简洁但标准的请求头
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Cache-Control": "no-cache"
            }
            
            # 发送POST请求
            self.api_client.post(
                endpoint="/gateway/sso_multiple/api/Code/InsertCode",
                data=request_data,
                headers=headers,
                callback=self._handle_insert_code_response
            )
            
            # 记录日志
            # self.logger.info(f"插入代码请求已发送，数据: {json.dumps(request_data, ensure_ascii=False)}")
            
            # 同时打印到控制台
            # print(f"🚀 后台API请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            # print(f"⏰ 请求时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            # print(f"🔗 请求URL: https://ambertu.com/gateway/sso_multiple/api/Code/InsertCode")
            # print("⏳ 等待服务器响应...")
            
        except Exception as e:
            self.logger.error(f"构造插入代码请求失败: {e}")
            # print(f"💥 API请求构造失败: {e}")
            self.api_failed.emit("insert_code", str(e))
    
    def _handle_insert_code_response(self, response: ApiResponse):
        """处理插入代码响应"""
        try:
            # print(f"🔄 收到API响应: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if response.is_success():
                self.logger.info(f"插入代码请求成功: 状态码={response.status_code}")
                
                # 解析响应数据
                data = response.get_data({})
                # self.logger.info(f"响应数据: {json.dumps(data, ensure_ascii=False) if isinstance(data, dict) else str(data)}")
                
                # 打印HTTP响应状态
                # print(f"🌐 HTTP响应: 状态码={response.status_code}")
                
                # 解析并打印业务响应数据
                if isinstance(data, dict):
                    # print(f"📄 返回数据:")
                    # print(json.dumps(data, ensure_ascii=False, indent=2))
                    
                    # 检查业务状态码
                    business_code = data.get('code')
                    message = data.get('message', '无消息')
                    
                    if business_code == 200:
                        print(f"✅ 业务处理成功: {message}")
                    else:
                        print(f"⚠️ 业务处理异常: code={business_code}, message={message}")
                else:
                    print(f"📄 响应数据: {str(data)}")
                
                # 发送成功信号
                self.api_success.emit("insert_code", data if isinstance(data, dict) else {"response": data})
                
            else:
                error_msg = f"插入代码请求失败: {response.message} (状态码: {response.status_code})"
                # self.logger.warning(error_msg)
                
                # # 打印详细的失败信息
                # print(f"❌ HTTP请求失败: 状态码={response.status_code}")
                # print(f"💔 错误信息: {response.message}")
                
                # 尝试解析错误响应数据
                try:
                    error_data = response.get_data({})
                    if error_data:
                        print(f"📄 错误详情:")
                        print(json.dumps(error_data, ensure_ascii=False, indent=2) if isinstance(error_data, dict) else str(error_data))
                except Exception as parse_error:
                    print(f"🔍 无法解析错误响应: {parse_error}")
                
                # 记录响应详情用于调试
                if hasattr(response, 'data') and response.data:
                    try:
                        error_detail = response.data if isinstance(response.data, str) else str(response.data)
                        self.logger.debug(f"错误详情: {error_detail}")
                    except:
                        pass
                
                # 发送失败信号
                self.api_failed.emit("insert_code", error_msg)
                
        except Exception as e:
            error_msg = f"处理插入代码响应时发生异常: {e}"
            self.logger.error(error_msg)
            print(f"💥 响应处理异常: {error_msg}")
            self.api_failed.emit("insert_code", error_msg)
    
    def manual_insert_code(self, member_id: str = None, code_content: str = None, 
                          batch_no: str = None, is_deleted: bool = False, callback: Callable = None):
        """手动触发插入代码请求"""
        try:
            # self.logger.info("手动触发插入代码请求")
            
            # 构造请求数据
            device_id = get_unique_identifier()
            request_data = {
                "MemberId": member_id or device_id[:8],
                "CodeContent": code_content or device_id,
                "BatchNo": batch_no or str(int(time.time())),
                "MerchantId": "8f86b406180a4303a87108eaeab7f351",
                "TenantId": "e25d142b7cc34b8d9818145671030354",
                "IsDeleted": True
            }
            
            # 发送请求 - 使用和后台请求相同的headers
            def handle_response(response: ApiResponse):
                self._handle_insert_code_response(response)
                if callback:
                    callback(response)
            
            # 使用和后台请求相同的headers配置
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Client-Version": "1.0.0",
                "X-Device-ID": get_unique_identifier(),
                "Cache-Control": "no-cache"
            }
            
            self.api_client.post(
                endpoint="/gateway/sso_multiple/api/Code/InsertCode",
                data=request_data,
                headers=headers,
                callback=handle_response
            )
            
            return True
            
        except Exception as e:
            # self.logger.error(f"手动插入代码请求失败: {e}")
            if callback:
                error_response = ApiResponse(False, message=str(e))
                callback(error_response)
            return False
    
    def add_custom_background_request(self, endpoint: str, data: Dict[str, Any], 
                                    callback: Callable = None, delay: int = 0):
        """添加自定义后台请求"""
        def delayed_request():
            if delay > 0:
                time.sleep(delay)
            
            self.api_client.post(
                endpoint=endpoint,
                data=data,
                callback=callback or self._default_response_handler
            )
        
        # 在后台线程中执行
        thread = threading.Thread(target=delayed_request, daemon=True)
        thread.start()
        
        # self.logger.info(f"已添加自定义后台请求: {endpoint}")
    
    def _default_response_handler(self, response: ApiResponse):
        """默认响应处理器"""
        if response.is_success():
            self.logger.info(f"自定义请求成功: {response.status_code}")
        else:
            self.logger.warning(f"自定义请求失败: {response.message}")


class BackgroundApiManager:
    """后台API管理器 - 单例模式"""
    
    _instance = None
    _service = None
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if BackgroundApiManager._service is None:
            BackgroundApiManager._service = BackgroundApiService()
    
    def get_service(self) -> BackgroundApiService:
        """获取后台API服务"""
        return BackgroundApiManager._service
    
    def start(self):
        """启动服务"""
        self._service.start_service()
    
    def stop(self):
        """停止服务"""
        self._service.stop_service()
    
    def is_running(self) -> bool:
        """检查服务是否运行中"""
        return self._service.is_running


# 全局实例
background_api_manager = BackgroundApiManager()