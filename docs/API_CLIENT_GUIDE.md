# API客户端使用指南

## 概述

API客户端是一个基于PySide6/Qt的异步HTTP请求封装工具，提供了简单易用的接口来处理各种API请求。

## 主要特性

- ✅ **统一的接口封装** - 支持GET、POST、PUT、DELETE、PATCH等HTTP方法
- ✅ **异步请求处理** - 基于Qt信号槽机制，不阻塞UI线程
- ✅ **全局配置管理** - 统一管理API基础URL、认证令牌等
- ✅ **自动设备识别** - 自动添加设备唯一码到请求头
- ✅ **详细日志记录** - 完整的请求/响应日志
- ✅ **错误处理** - 统一的错误处理和回调机制
- ✅ **请求管理** - 支持请求取消、超时控制等

## 快速开始

### 1. 基础配置

在 `config/app_config.py` 中配置API基础信息：

```python
class AppConfig:
    # API配置
    API_BASE_URL = "https://your-api-domain.com"  # 修改为你的API域名
    API_TIMEOUT = 30  # 超时时间（秒）
    API_RETRY_COUNT = 3  # 重试次数
```

### 2. 简单使用

```python
from utils.api_client import ApiHelper

# 设置认证令牌（可选）
ApiHelper.set_auth_token("your_jwt_token_here")

# 定义响应处理函数
def handle_response(response):
    if response.is_success():
        print(f"请求成功: {response.data}")
    else:
        print(f"请求失败: {response.message}")

# GET请求
ApiHelper.get("/api/users", params={"page": 1}, callback=handle_response)

# POST请求
ApiHelper.post("/api/users", data={"name": "张三", "email": "test@example.com"}, callback=handle_response)

# PUT请求
ApiHelper.put("/api/users/123", data={"name": "李四"}, callback=handle_response)

# DELETE请求
ApiHelper.delete("/api/users/123", callback=handle_response)
```

### 3. 高级使用

```python
from utils.api_client import ApiClient

# 创建专用客户端（针对不同服务）
client = ApiClient("https://another-api.com")
client.set_auth_token("different_token")

# 自定义请求头
custom_headers = {
    "X-Custom-Header": "custom_value",
    "Accept-Language": "zh-CN"
}

client.get("/api/data", headers=custom_headers, callback=handle_response)

# 请求管理
request_id = client.get("/api/long-running-task")
# ... 可以稍后取消
client.cancel_request(request_id)
```

## 业务API封装示例

推荐为不同的业务模块创建专门的API类：

```python
class UserApi:
    """用户相关API"""
    
    @staticmethod
    def get_profile(user_id, callback=None):
        return ApiHelper.get(f"/api/users/{user_id}", callback=callback)
    
    @staticmethod
    def update_profile(user_id, data, callback=None):
        return ApiHelper.put(f"/api/users/{user_id}", data=data, callback=callback)
    
    @staticmethod
    def create_user(user_data, callback=None):
        return ApiHelper.post("/api/users", data=user_data, callback=callback)


class PostApi:
    """文章相关API"""
    
    @staticmethod
    def get_posts(page=1, limit=10, callback=None):
        return ApiHelper.get("/api/posts", 
                           params={"page": page, "limit": limit}, 
                           callback=callback)
    
    @staticmethod
    def create_post(title, content, callback=None):
        return ApiHelper.post("/api/posts", 
                            data={"title": title, "content": content}, 
                            callback=callback)
```

## 响应处理

### ApiResponse 对象

所有API请求的响应都封装为 `ApiResponse` 对象：

```python
def handle_api_response(response):
    # 检查请求是否成功
    if response.is_success():
        # 获取响应数据
        data = response.get_data()  # 返回解析后的数据
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"数据: {data}")
    else:
        # 处理错误
        print(f"错误: {response.message}")
        print(f"状态码: {response.status_code}")
        
        # 根据状态码处理特定错误
        if response.status_code == 401:
            print("认证失败，需要重新登录")
        elif response.status_code == 404:
            print("资源不存在")
        elif response.status_code >= 500:
            print("服务器错误")
```

### 信号处理

也可以通过信号来处理响应：

```python
from utils.api_client import ApiClient

client = ApiClient()

# 连接信号
client.request_finished.connect(lambda req_id, response: print(f"请求完成: {req_id}"))
client.request_failed.connect(lambda req_id, error: print(f"请求失败: {req_id}, {error}"))

# 发送请求
request_id = client.get("/api/data")
```

## 配置选项

### 全局配置

在 `config/app_config.py` 中可以配置：

- `API_BASE_URL`: API基础域名
- `API_TIMEOUT`: 请求超时时间（秒）
- `API_RETRY_COUNT`: 重试次数

### 运行时配置

```python
# 更改基础URL
ApiHelper.set_base_url("https://new-api.com")

# 设置认证令牌
ApiHelper.set_auth_token("new_token")

# 获取客户端实例进行更多配置
client = ApiHelper.get_client()
client.timeout = 60  # 设置超时时间
```

## 常见用法模式

### 1. 列表页面数据加载

```python
def load_user_list(self, page=1):
    def handle_users(response):
        if response.is_success():
            users = response.get_data([])
            self.update_user_table(users)
        else:
            self.show_error_message(f"加载失败: {response.message}")
    
    ApiHelper.get("/api/users", params={"page": page, "limit": 20}, callback=handle_users)
```

### 2. 表单提交

```python
def submit_user_form(self, form_data):
    def handle_submit(response):
        if response.is_success():
            self.show_success_message("用户创建成功")
            self.close_form_dialog()
        else:
            self.show_error_message(f"提交失败: {response.message}")
    
    ApiHelper.post("/api/users", data=form_data, callback=handle_submit)
```

### 3. 文件上传（待实现）

```python
# 文件上传功能正在开发中
# client.upload_file("/api/upload", file_path="image.jpg", callback=handle_upload)
```

## 注意事项

1. **异步特性**: 所有请求都是异步的，不会阻塞UI线程
2. **回调函数**: 使用回调函数处理响应，避免在UI线程中进行网络请求
3. **错误处理**: 始终检查 `response.is_success()` 来判断请求是否成功
4. **设备唯一码**: 会自动在请求头中添加设备唯一码 `X-Device-ID`
5. **日志记录**: 所有请求和响应都会记录到日志文件中

## 调试技巧

1. 查看日志文件了解请求详情
2. 使用 `client.get_active_request_count()` 查看活跃请求数
3. 在开发时可以设置较短的超时时间来快速发现问题

## 示例运行

运行 `demo_api_client.py` 查看完整的使用示例：

```bash
python demo_api_client.py
```

这将展示各种API使用模式和最佳实践。