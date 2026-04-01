import requests
import json

# 测试登录API
def test_login():
    url = 'http://localhost:5000/api/v1/auth/login'
    
    # 测试数据 - 使用常见的测试账号
    test_credentials = {
        'username': 'admin',  # 假设存在的管理员账号
        'password': 'admin123'  # 假设的密码
    }
    
    try:
        print("正在测试登录API...")
        response = requests.post(url, json=test_credentials)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 检查是否成功登录
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("登录测试成功! 获取到了访问令牌。")
                return True
            else:
                print("登录失败: 响应中没有访问令牌。")
                return False
        else:
            print(f"登录失败: 状态码 {response.status_code}")
            return False
    
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_login()