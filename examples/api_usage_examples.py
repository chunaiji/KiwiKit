"""
API客户端使用示例
"""

from utils.api_client import ApiClient, ApiHelper, ApiResponse
from utils.logger import get_logger

logger = get_logger(__name__)


def example_callback(response: ApiResponse):
    """示例回调函数"""
    if response.is_success():
        logger.info(f"请求成功: {response.data}")
    else:
        logger.error(f"请求失败: {response.message}")


def api_usage_examples():
    """API使用示例"""
    
    # 方法1：使用全局实例（推荐）
    print("=== 使用ApiHelper（推荐方式） ===")
    
    # 设置认证令牌
    ApiHelper.set_auth_token("your_token_here")
    
    # GET请求 - 获取用户信息
    request_id = ApiHelper.get(
        endpoint="/api/user/profile",
        params={"user_id": 123},
        callback=example_callback
    )
    print(f"发送GET请求，ID: {request_id}")
    
    # POST请求 - 创建用户
    request_id = ApiHelper.post(
        endpoint="/api/user/create",
        data={
            "username": "test_user",
            "email": "test@example.com",
            "age": 25
        },
        callback=example_callback
    )
    print(f"发送POST请求，ID: {request_id}")
    
    # PUT请求 - 更新用户信息
    request_id = ApiHelper.put(
        endpoint="/api/user/123",
        data={
            "username": "updated_user",
            "email": "updated@example.com"
        },
        callback=example_callback
    )
    print(f"发送PUT请求，ID: {request_id}")
    
    # DELETE请求 - 删除用户
    request_id = ApiHelper.delete(
        endpoint="/api/user/123",
        callback=example_callback
    )
    print(f"发送DELETE请求，ID: {request_id}")
    
    print("\n=== 使用独立实例 ===")
    
    # 方法2：使用独立实例
    client = ApiClient("https://api.another-service.com")
    client.set_auth_token("another_token")
    
    # 连接信号
    client.request_finished.connect(
        lambda req_id, response: print(f"请求完成: {req_id}, 成功: {response.success}")
    )
    client.request_failed.connect(
        lambda req_id, error: print(f"请求失败: {req_id}, 错误: {error}")
    )
    
    # 发送请求
    request_id = client.get("/api/data", {"page": 1, "limit": 10})
    print(f"发送GET请求到另一个服务，ID: {request_id}")


def api_response_handling_examples():
    """API响应处理示例"""
    
    def handle_user_list(response: ApiResponse):
        """处理用户列表响应"""
        if response.is_success():
            users = response.get_data([])  # 默认返回空列表
            print(f"获取到 {len(users)} 个用户")
            
            for user in users:
                print(f"- 用户: {user.get('name', 'Unknown')}")
        else:
            print(f"获取用户列表失败: {response.message}")
    
    def handle_user_create(response: ApiResponse):
        """处理用户创建响应"""
        if response.is_success():
            user_data = response.get_data({})
            user_id = user_data.get('id')
            print(f"用户创建成功，ID: {user_id}")
        else:
            print(f"用户创建失败: {response.message}")
            
            # 处理特定错误
            if response.status_code == 400:
                print("请检查输入数据格式")
            elif response.status_code == 401:
                print("认证失败，请检查令牌")
            elif response.status_code == 500:
                print("服务器内部错误")
    
    # 发送请求
    ApiHelper.get("/api/users", callback=handle_user_list)
    
    ApiHelper.post(
        "/api/users",
        data={"name": "新用户", "email": "new@example.com"},
        callback=handle_user_create
    )


def advanced_api_usage():
    """高级API使用示例"""
    
    # 创建专用客户端
    client = ApiClient()
    
    # 自定义请求头
    custom_headers = {
        "X-Custom-Header": "custom_value",
        "Accept-Language": "zh-CN"
    }
    
    # 带自定义头部的请求
    client.get(
        "/api/custom-endpoint",
        headers=custom_headers,
        callback=lambda r: print(f"自定义请求结果: {r.success}")
    )
    
    # 批量请求管理
    request_ids = []
    
    # 发送多个请求
    for i in range(5):
        req_id = client.get(f"/api/data/{i}")
        request_ids.append(req_id)
    
    print(f"发送了 {len(request_ids)} 个请求")
    print(f"当前活跃请求数: {client.get_active_request_count()}")
    
    # 取消部分请求
    if request_ids:
        client.cancel_request(request_ids[0])
        print(f"已取消请求: {request_ids[0]}")
    
    # 在需要时取消所有请求
    # client.cancel_all_requests()


if __name__ == "__main__":
    print("API客户端使用示例")
    print("=" * 50)
    
    # 基础使用示例
    api_usage_examples()
    
    # 响应处理示例
    print("\n" + "=" * 50)
    api_response_handling_examples()
    
    # 高级使用示例
    print("\n" + "=" * 50)
    advanced_api_usage()