"""
API接口请求封装工具
"""

import json
import time
from typing import Dict, Any, Optional, Union, Callable
from urllib.parse import urljoin, urlencode
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QSslConfiguration

from config.app_config import AppConfig
from utils.logger import get_logger
from utils.user_info import get_unique_identifier


class ApiResponse:
    """API响应封装"""
    def __init__(self, success: bool, data: Any = None, message: str = "", 
                 status_code: int = 200, headers: Dict[str, str] = None):
        self.success = success
        self.data = data
        self.message = message
        self.status_code = status_code
        self.headers = headers or {}
        self.timestamp = time.time()
    
    def is_success(self) -> bool:
        """是否请求成功"""
        return self.success and 200 <= self.status_code < 300
    
    def get_data(self, default=None) -> Any:
        """获取数据，如果失败返回默认值"""
        return self.data if self.success else default
    
    def __str__(self):
        return f"ApiResponse(success={self.success}, status={self.status_code}, message='{self.message}')"


class ApiClient(QObject):
    """API客户端 - 统一的接口请求封装"""
    
    # 信号定义
    request_started = Signal(str)  # 请求开始
    request_finished = Signal(str, ApiResponse)  # 请求完成
    request_failed = Signal(str, str)  # 请求失败
    
    def __init__(self, base_url: str = None):
        super().__init__()
        self.logger = get_logger(__name__)
        
        # 配置
        self.base_url = base_url or AppConfig.API_BASE_URL
        self.timeout = AppConfig.API_TIMEOUT
        self.retry_count = AppConfig.API_RETRY_COUNT
        
        # 网络管理器
        self.manager = QNetworkAccessManager()
        self._setup_ssl()
        
        # 默认请求头
        self.default_headers = {
            'User-Agent': f'{AppConfig.APP_NAME}/{AppConfig.VERSION}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Client-Version': AppConfig.VERSION,
            'X-Device-ID': get_unique_identifier(),
        }
        
        # 请求追踪
        self._active_requests = {}
        
        self.logger.info(f"API客户端初始化完成，基础URL: {self.base_url}")
    
    def _setup_ssl(self):
        """设置SSL配置"""
        try:
            from PySide6.QtNetwork import QSslSocket
            ssl_config = QSslConfiguration.defaultConfiguration()
            # 使用正确的SSL验证模式，禁用验证
            ssl_config.setPeerVerifyMode(QSslSocket.PeerVerifyMode.VerifyNone)
            QSslConfiguration.setDefaultConfiguration(ssl_config)
            self.logger.info("SSL配置成功：已禁用证书验证")
        except Exception as e:
            # SSL配置失败不是致命错误，记录警告但继续运行
            self.logger.debug(f"SSL配置跳过: {e}")
    
    def set_auth_token(self, token: str):
        """设置认证令牌"""
        self.default_headers['Authorization'] = f'Bearer {token}'
        self.logger.info("API认证令牌已设置")
    
    def set_base_url(self, url: str):
        """设置基础URL"""
        self.base_url = url
        self.logger.info(f"API基础URL更新为: {url}")
    
    def get(self, endpoint: str, params: Dict[str, Any] = None, 
            headers: Dict[str, str] = None, callback: Callable = None) -> str:
        """GET请求"""
        url = self._build_url(endpoint, params)
        return self._request('GET', url, headers=headers, callback=callback)
    
    def post(self, endpoint: str, data: Dict[str, Any] = None, 
             headers: Dict[str, str] = None, callback: Callable = None) -> str:
        """POST请求"""
        url = self._build_url(endpoint)
        return self._request('POST', url, data=data, headers=headers, callback=callback)
    
    def put(self, endpoint: str, data: Dict[str, Any] = None,
            headers: Dict[str, str] = None, callback: Callable = None) -> str:
        """PUT请求"""
        url = self._build_url(endpoint)
        return self._request('PUT', url, data=data, headers=headers, callback=callback)
    
    def delete(self, endpoint: str, headers: Dict[str, str] = None, 
               callback: Callable = None) -> str:
        """DELETE请求"""
        url = self._build_url(endpoint)
        return self._request('DELETE', url, headers=headers, callback=callback)
    
    def patch(self, endpoint: str, data: Dict[str, Any] = None,
              headers: Dict[str, str] = None, callback: Callable = None) -> str:
        """PATCH请求"""
        url = self._build_url(endpoint)
        return self._request('PATCH', url, data=data, headers=headers, callback=callback)
    
    def upload_file(self, endpoint: str, file_path: str, field_name: str = 'file',
                   additional_data: Dict[str, str] = None, callback: Callable = None) -> str:
        """文件上传"""
        # TODO: 实现文件上传功能
        self.logger.warning("文件上传功能待实现")
        return ""
    
    def _build_url(self, endpoint: str, params: Dict[str, Any] = None) -> str:
        """构建完整URL"""
        # 处理endpoint
        if endpoint.startswith('http'):
            url = endpoint
        else:
            endpoint = endpoint.lstrip('/')
            url = urljoin(self.base_url.rstrip('/') + '/', endpoint)
        
        # 添加查询参数
        if params:
            query_string = urlencode(params)
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}{query_string}"
        
        return url
    
    def _request(self, method: str, url: str, data: Dict[str, Any] = None,
                headers: Dict[str, str] = None, callback: Callable = None) -> str:
        """发送HTTP请求"""
        request_id = f"{method}_{url}_{int(time.time() * 1000)}"
        
        try:
            # self.logger.info(f"发送API请求: {method} {url}")
            self.request_started.emit(request_id)
            
            # 创建请求
            request = QNetworkRequest()
            request.setUrl(url)
            
            # 设置HTTP版本和属性
            try:
                from PySide6.QtNetwork import QNetworkRequest as QNR
                # 只设置安全的属性
                request.setAttribute(QNR.Attribute.HttpPipeliningAllowedAttribute, True)
                # 跳过可能不存在的属性
            except AttributeError as e:
                self.logger.debug(f"跳过不支持的网络属性: {e}")
            
            # 设置请求头
            merged_headers = {**self.default_headers}
            if headers:
                merged_headers.update(headers)
            
            # 调试：打印请求详细信息
            # print(f"\n🔍 详细请求信息:")
            # print(f"📍 完整URL: {url}")
            # print(f"🔧 HTTP方法: {method}")
            # print(f"📋 请求头:")
            # for key, value in merged_headers.items():
            #     print(f"   {key}: {value}")
            # if data:
            #     print(f"📦 请求数据: {json.dumps(data, ensure_ascii=False, indent=2) if isinstance(data, dict) else str(data)}")
            # print("─" * 50)
            
            for key, value in merged_headers.items():
                request.setRawHeader(key.encode(), str(value).encode())
            
            # 设置超时
            request.setTransferTimeout(self.timeout * 1000)
            
            # 准备请求数据
            request_data = None
            if data and method in ['POST', 'PUT', 'PATCH']:
                if isinstance(data, dict):
                    request_data = json.dumps(data).encode('utf-8')
                else:
                    request_data = str(data).encode('utf-8')
            
            # 发送请求
            if method == 'GET':
                reply = self.manager.get(request)
            elif method == 'POST':
                reply = self.manager.post(request, request_data or b'')
            elif method == 'PUT':
                reply = self.manager.put(request, request_data or b'')
            elif method == 'DELETE':
                reply = self.manager.deleteResource(request)
            elif method == 'PATCH':
                reply = self.manager.sendCustomRequest(request, b'PATCH', request_data or b'')
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            # 保存请求信息
            self._active_requests[request_id] = {
                'method': method,
                'url': url,
                'start_time': time.time(),
                'callback': callback,
                'reply': reply
            }
            
            # 连接信号
            reply.finished.connect(lambda: self._handle_response(request_id))
            reply.errorOccurred.connect(lambda error: self._handle_error(request_id, error))
            
            return request_id
            
        except Exception as e:
            # self.logger.error(f"发送请求失败: {e}")
            error_response = ApiResponse(False, message=str(e))
            self.request_finished.emit(request_id, error_response)
            if callback:
                callback(error_response)
            return request_id
    
    def _handle_response(self, request_id: str):
        """处理响应"""
        if request_id not in self._active_requests:
            return
        
        request_info = self._active_requests[request_id]
        reply = request_info['reply']
        
        try:
            # 获取响应数据
            status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) or 0
            raw_data = reply.readAll().data()
            
            # 获取响应头
            headers = {}
            for header_name in reply.rawHeaderList():
                key = header_name.data().decode()
                value = reply.rawHeader(key).data().decode()
                headers[key] = value
            
            # 解析响应数据
            response_data = None
            error_message = ""
            
            try:
                if raw_data:
                    text_data = raw_data.decode('utf-8')
                    response_data = json.loads(text_data) if text_data.strip() else {}
                else:
                    response_data = {}
            except json.JSONDecodeError:
                response_data = raw_data.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                response_data = str(raw_data)
                error_message = "响应数据编码错误"
            
            # 判断请求是否成功
            success = 200 <= status_code < 300
            
            # 提取错误信息
            if not success and isinstance(response_data, dict):
                error_message = response_data.get('message') or response_data.get('error') or f"HTTP {status_code}"
            
            # 创建响应对象
            api_response = ApiResponse(
                success=success,
                data=response_data,
                message=error_message,
                status_code=status_code,
                headers=headers
            )
            
            # 记录日志
            duration = time.time() - request_info['start_time']
            # self.logger.info(f"API响应: {request_info['method']} {request_info['url']} - "
            #                f"状态码: {status_code}, 耗时: {duration:.3f}秒")
            
            # 发送信号
            self.request_finished.emit(request_id, api_response)
            
            # 执行回调
            if request_info.get('callback'):
                request_info['callback'](api_response)
            
        except Exception as e:
            # self.logger.error(f"处理响应失败: {e}")
            error_response = ApiResponse(False, message=f"响应处理错误: {str(e)}")
            self.request_finished.emit(request_id, error_response)
            
            if request_info.get('callback'):
                request_info['callback'](error_response)
        
        finally:
            # 清理
            reply.deleteLater()
            del self._active_requests[request_id]
    
    def _handle_error(self, request_id: str, error: QNetworkReply.NetworkError):
        """处理网络错误"""
        if request_id not in self._active_requests:
            return
        
        request_info = self._active_requests[request_id]
        reply = request_info['reply']
        
        error_string = reply.errorString()
        
        # self.logger.error(f"API请求失败: {request_info['method']} {request_info['url']} - {error_string}")
        
        # 同时打印网络错误到控制台
        # print(f"🚫 网络请求错误: {error_string}")
        # print(f"🔗 请求地址: {request_info['url']}")
        # print(f"📊 错误代码: {error}")
        
        # 创建错误响应
        error_response = ApiResponse(
            success=False,
            message=error_string,
            status_code=reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) or 0
        )
        
        # 发送信号
        self.request_failed.emit(request_id, error_string)
        self.request_finished.emit(request_id, error_response)
        
        # 执行回调
        if request_info.get('callback'):
            request_info['callback'](error_response)
        
        # 清理
        reply.deleteLater()
        if request_id in self._active_requests:
            del self._active_requests[request_id]
    
    def cancel_request(self, request_id: str):
        """取消请求"""
        if request_id in self._active_requests:
            reply = self._active_requests[request_id]['reply']
            reply.abort()
            del self._active_requests[request_id]
            self.logger.info(f"已取消请求: {request_id}")
    
    def cancel_all_requests(self):
        """取消所有请求"""
        for request_id in list(self._active_requests.keys()):
            self.cancel_request(request_id)
    
    def get_active_request_count(self) -> int:
        """获取活跃请求数量"""
        return len(self._active_requests)


# 便捷函数
class ApiHelper:
    """API辅助函数"""
    
    _client = None
    
    @classmethod
    def get_client(cls) -> ApiClient:
        """获取全局API客户端实例"""
        if cls._client is None:
            cls._client = ApiClient()
        return cls._client
    
    @classmethod
    def get(cls, endpoint: str, params: Dict[str, Any] = None, 
            callback: Callable = None) -> str:
        """快捷GET请求"""
        return cls.get_client().get(endpoint, params, callback=callback)
    
    @classmethod
    def post(cls, endpoint: str, data: Dict[str, Any] = None, 
             callback: Callable = None) -> str:
        """快捷POST请求"""
        return cls.get_client().post(endpoint, data, callback=callback)
    
    @classmethod
    def put(cls, endpoint: str, data: Dict[str, Any] = None, 
            callback: Callable = None) -> str:
        """快捷PUT请求"""
        return cls.get_client().put(endpoint, data, callback=callback)
    
    @classmethod
    def delete(cls, endpoint: str, callback: Callable = None) -> str:
        """快捷DELETE请求"""
        return cls.get_client().delete(endpoint, callback=callback)
    
    @classmethod
    def set_auth_token(cls, token: str):
        """设置全局认证令牌"""
        cls.get_client().set_auth_token(token)
    
    @classmethod
    def set_base_url(cls, url: str):
        """设置全局基础URL"""
        cls.get_client().set_base_url(url)


# 全局实例（兼容旧代码）
api_client = ApiClient()