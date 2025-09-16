"""
网络请求工具类
"""

import json
import asyncio
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, QThread, QUrl, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class HttpResponse:
    """HTTP响应封装"""
    def __init__(self, status_code: int, data: bytes, headers: Dict[str, str] = None):
        self.status_code = status_code
        self.data = data
        self.headers = headers or {}
    
    def json(self) -> Dict[str, Any]:
        """解析JSON响应"""
        try:
            return json.loads(self.data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
    
    def text(self) -> str:
        """获取文本响应"""
        try:
            return self.data.decode('utf-8')
        except UnicodeDecodeError:
            return self.data.decode('utf-8', errors='ignore')


class HttpClient(QObject):
    """网络请求客户端 - 基于Qt Network"""
    
    # 信号定义
    request_finished = Signal(HttpResponse)
    request_error = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.manager = QNetworkAccessManager()
        self.default_headers = {
            'User-Agent': 'WeChat-Desktop-App/1.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
    
    def get(self, url: str, headers: Dict[str, str] = None, timeout: int = 30) -> None:
        """发送GET请求"""
        self._send_request('GET', url, headers=headers, timeout=timeout)
    
    def post(self, url: str, data: Dict[str, Any] = None, json_data: Dict[str, Any] = None, 
             headers: Dict[str, str] = None, timeout: int = 30) -> None:
        """发送POST请求"""
        post_data = None
        request_headers = headers or {}
        
        if json_data:
            post_data = json.dumps(json_data).encode('utf-8')
            request_headers['Content-Type'] = 'application/json'
        elif data:
            post_data = self._encode_form_data(data)
            request_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        self._send_request('POST', url, data=post_data, headers=request_headers, timeout=timeout)
    
    def put(self, url: str, data: Dict[str, Any] = None, json_data: Dict[str, Any] = None,
            headers: Dict[str, str] = None, timeout: int = 30) -> None:
        """发送PUT请求"""
        put_data = None
        request_headers = headers or {}
        
        if json_data:
            put_data = json.dumps(json_data).encode('utf-8')
            request_headers['Content-Type'] = 'application/json'
        elif data:
            put_data = self._encode_form_data(data)
            request_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        self._send_request('PUT', url, data=put_data, headers=request_headers, timeout=timeout)
    
    def delete(self, url: str, headers: Dict[str, str] = None, timeout: int = 30) -> None:
        """发送DELETE请求"""
        self._send_request('DELETE', url, headers=headers, timeout=timeout)
    
    def _send_request(self, method: str, url: str, data: bytes = None, 
                     headers: Dict[str, str] = None, timeout: int = 30) -> None:
        """发送HTTP请求"""
        request = QNetworkRequest(QUrl(url))
        
        # 设置默认头部
        merged_headers = {**self.default_headers}
        if headers:
            merged_headers.update(headers)
        
        for key, value in merged_headers.items():
            request.setRawHeader(key.encode(), value.encode())
        
        # 设置超时
        request.setTransferTimeout(timeout * 1000)  # Qt使用毫秒
        
        # 发送请求
        if method == 'GET':
            reply = self.manager.get(request)
        elif method == 'POST':
            reply = self.manager.post(request, data or QByteArray())
        elif method == 'PUT':
            reply = self.manager.put(request, data or QByteArray())
        elif method == 'DELETE':
            reply = self.manager.deleteResource(request)
        else:
            self.request_error.emit(f"Unsupported HTTP method: {method}")
            return
        
        # 连接信号
        reply.finished.connect(lambda: self._handle_response(reply))
        reply.errorOccurred.connect(lambda error: self._handle_error(reply, error))
    
    def _handle_response(self, reply: QNetworkReply) -> None:
        """处理响应"""
        try:
            status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            data = reply.readAll().data()
            
            # 获取响应头
            headers = {}
            for header in reply.rawHeaderList():
                key = header.data().decode()
                value = reply.rawHeader(header).data().decode()
                headers[key] = value
            
            response = HttpResponse(status_code, data, headers)
            self.request_finished.emit(response)
            
        except Exception as e:
            self.request_error.emit(f"Response parsing error: {str(e)}")
        finally:
            reply.deleteLater()
    
    def _handle_error(self, reply: QNetworkReply, error: QNetworkReply.NetworkError) -> None:
        """处理错误"""
        error_string = reply.errorString()
        self.request_error.emit(f"Network error: {error_string}")
        reply.deleteLater()
    
    def _encode_form_data(self, data: Dict[str, Any]) -> bytes:
        """编码表单数据"""
        from urllib.parse import urlencode
        return urlencode(data).encode('utf-8')


class SimpleHttpClient:
    """简单的同步HTTP客户端（用于简单场景）"""
    
    @staticmethod
    def get_sync(url: str, headers: Dict[str, str] = None, timeout: int = 30) -> HttpResponse:
        """同步GET请求"""
        import urllib.request
        import urllib.error
        
        try:
            req = urllib.request.Request(url)
            
            # 设置头部
            default_headers = {
                'User-Agent': 'WeChat-Desktop-App/1.0',
                'Accept': 'application/json, text/plain, */*'
            }
            if headers:
                default_headers.update(headers)
            
            for key, value in default_headers.items():
                req.add_header(key, value)
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return HttpResponse(
                    status_code=response.getcode(),
                    data=response.read(),
                    headers=dict(response.headers)
                )
                
        except urllib.error.HTTPError as e:
            return HttpResponse(
                status_code=e.code,
                data=e.read(),
                headers=dict(e.headers)
            )
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")


# 全局实例
http_client = HttpClient()
