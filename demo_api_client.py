"""
API客户端快速使用指南
"""

from utils.api_client import ApiHelper, ApiResponse


def quick_start_demo():
    """快速开始演示"""
    print("🚀 API客户端快速使用指南")
    print("=" * 50)
    
    # 1. 基础配置
    print("1️⃣ 设置API基础信息")
    ApiHelper.set_base_url("https://jsonplaceholder.typicode.com")
    ApiHelper.set_auth_token("your_token_here")
    print("   ✅ 基础URL和认证令牌已设置")
    
    # 2. 定义回调函数
    def handle_response(response: ApiResponse):
        print(f"   📡 收到响应: 状态码={response.status_code}, 成功={response.success}")
        if response.is_success():
            data = response.get_data()
            if isinstance(data, list):
                print(f"   📝 获取到 {len(data)} 条数据")
            elif isinstance(data, dict):
                print(f"   📝 数据字段: {list(data.keys())[:5]}...")
        else:
            print(f"   ❌ 错误信息: {response.message}")
    
    # 3. 发送各种类型的请求
    print("\n2️⃣ 发送API请求")
    
    # GET请求 - 获取文章列表
    print("   🔍 GET请求 - 获取文章列表")
    ApiHelper.get(
        endpoint="/posts", 
        params={"_limit": 5},
        callback=handle_response
    )
    
    # POST请求 - 创建新文章
    print("   ➕ POST请求 - 创建新文章")
    ApiHelper.post(
        endpoint="/posts",
        data={
            "title": "测试文章",
            "body": "这是一篇测试文章的内容",
            "userId": 1
        },
        callback=handle_response
    )
    
    # PUT请求 - 更新文章
    print("   🔄 PUT请求 - 更新文章")
    ApiHelper.put(
        endpoint="/posts/1",
        data={
            "id": 1,
            "title": "更新的文章标题",
            "body": "更新的文章内容",
            "userId": 1
        },
        callback=handle_response
    )
    
    # DELETE请求 - 删除文章
    print("   🗑️ DELETE请求 - 删除文章")
    ApiHelper.delete(
        endpoint="/posts/1",
        callback=handle_response
    )
    
    print("\n3️⃣ 请求已发送，等待响应...")
    print("💡 提示：这是异步请求，响应将通过回调函数处理")
    
    return ApiHelper.get_client()


# 常用API封装示例
class UserApi:
    """用户相关API封装"""
    
    @staticmethod
    def get_user_profile(user_id: int, callback=None):
        """获取用户信息"""
        return ApiHelper.get(f"/users/{user_id}", callback=callback)
    
    @staticmethod
    def update_user_profile(user_id: int, data: dict, callback=None):
        """更新用户信息"""
        return ApiHelper.put(f"/users/{user_id}", data=data, callback=callback)
    
    @staticmethod
    def create_user(user_data: dict, callback=None):
        """创建用户"""
        return ApiHelper.post("/users", data=user_data, callback=callback)
    
    @staticmethod
    def delete_user(user_id: int, callback=None):
        """删除用户"""
        return ApiHelper.delete(f"/users/{user_id}", callback=callback)
    
    @staticmethod
    def get_user_posts(user_id: int, callback=None):
        """获取用户的文章"""
        return ApiHelper.get("/posts", params={"userId": user_id}, callback=callback)


class PostApi:
    """文章相关API封装"""
    
    @staticmethod
    def get_posts(page: int = 1, limit: int = 10, callback=None):
        """获取文章列表"""
        return ApiHelper.get(
            "/posts",
            params={"_page": page, "_limit": limit},
            callback=callback
        )
    
    @staticmethod
    def get_post_detail(post_id: int, callback=None):
        """获取文章详情"""
        return ApiHelper.get(f"/posts/{post_id}", callback=callback)
    
    @staticmethod
    def create_post(title: str, content: str, user_id: int, callback=None):
        """创建文章"""
        return ApiHelper.post(
            "/posts",
            data={"title": title, "body": content, "userId": user_id},
            callback=callback
        )
    
    @staticmethod
    def update_post(post_id: int, title: str = None, content: str = None, callback=None):
        """更新文章"""
        data = {}
        if title:
            data["title"] = title
        if content:
            data["body"] = content
        
        return ApiHelper.put(f"/posts/{post_id}", data=data, callback=callback)
    
    @staticmethod
    def delete_post(post_id: int, callback=None):
        """删除文章"""
        return ApiHelper.delete(f"/posts/{post_id}", callback=callback)
    
    @staticmethod
    def get_post_comments(post_id: int, callback=None):
        """获取文章评论"""
        return ApiHelper.get(f"/posts/{post_id}/comments", callback=callback)


def business_api_examples():
    """业务API使用示例"""
    print("\n🏢 业务API使用示例")
    print("=" * 50)
    
    def print_response(response: ApiResponse):
        if response.is_success():
            print(f"✅ 请求成功: {response.status_code}")
        else:
            print(f"❌ 请求失败: {response.message}")
    
    # 用户API示例
    print("👤 用户API使用：")
    UserApi.get_user_profile(1, callback=print_response)
    UserApi.create_user({
        "name": "张三",
        "username": "zhangsan",
        "email": "zhangsan@example.com"
    }, callback=print_response)
    
    # 文章API示例
    print("\n📝 文章API使用：")
    PostApi.get_posts(page=1, limit=5, callback=print_response)
    PostApi.create_post(
        title="API客户端使用指南",
        content="这是一份详细的API客户端使用指南",
        user_id=1,
        callback=print_response
    )


if __name__ == "__main__":
    # 运行演示
    client = quick_start_demo()
    
    # 业务API示例
    business_api_examples()
    
    print(f"\n📊 当前活跃请求数: {client.get_active_request_count()}")
    print("\n💡 使用提示：")
    print("1. 修改config/app_config.py中的API_BASE_URL设置真实的API地址")
    print("2. 使用ApiHelper.set_auth_token()设置认证令牌")
    print("3. 根据需要创建专门的API类来封装业务逻辑")
    print("4. 所有请求都是异步的，通过回调函数处理响应")