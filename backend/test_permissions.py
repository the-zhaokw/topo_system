import requests
import json

# 测试服务器地址
BASE_URL = "http://127.0.0.1:5000"

def test_admin_permissions():
    print("=== 测试Admin权限 ===")
    
    # 1. 管理员登录
    print("1. 管理员登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            if token:
                print(f"✅ 登录成功，token: {token[:20]}...")
            else:
                print(f"❌ 登录响应中没有token: {result}")
                return
            
            # 设置请求头
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # 2. 测试获取当前用户信息
            print("\n2. 测试获取当前用户信息...")
            response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ 获取用户信息成功")
                print(f"   用户名: {user_info.get('username')}")
                print(f"   角色: {user_info.get('role')}")
                print(f"   权限: {user_info.get('permissions', [])}")
            else:
                print(f"❌ 获取用户信息失败: {response.status_code} - {response.text}")
            
            # 3. 测试获取用户列表（需要view_all权限）
            print("\n3. 测试获取用户列表...")
            response = requests.get(f"{BASE_URL}/api/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                print(f"✅ 获取用户列表成功，共{len(users)}个用户")
                for user in users[:3]:  # 只显示前3个用户
                    print(f"   - {user.get('username')} ({user.get('role')})")
            else:
                print(f"❌ 获取用户列表失败: {response.status_code} - {response.text}")
            
            # 4. 测试获取特定用户详情
            print("\n4. 测试获取用户详情...")
            response = requests.get(f"{BASE_URL}/api/users/2", headers=headers)  # 获取ID为2的用户
            if response.status_code == 200:
                user_detail = response.json()
                print(f"✅ 获取用户详情成功: {user_detail.get('username')}")
            else:
                print(f"❌ 获取用户详情失败: {response.status_code} - {response.text}")
                
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

def test_guest_permissions():
    print("\n=== 测试Guest权限 ===")
    
    # 1. 访客登录
    print("1. 访客登录...")
    login_data = {
        "username": "guest",
        "password": "guest123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            print(f"✅ 登录成功，token: {token[:20]}...")
            
            # 设置请求头
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # 2. 测试获取当前用户信息
            print("\n2. 测试获取当前用户信息...")
            response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ 获取用户信息成功")
                print(f"   用户名: {user_info.get('username')}")
                print(f"   角色: {user_info.get('role')}")
                print(f"   权限: {user_info.get('permissions', [])}")
            else:
                print(f"❌ 获取用户信息失败: {response.status_code} - {response.text}")
            
            # 3. 测试获取用户列表（guest应该没有权限）
            print("\n3. 测试获取用户列表（guest权限不足）...")
            response = requests.get(f"{BASE_URL}/api/users", headers=headers)
            if response.status_code == 403:
                print(f"✅ 权限检查正确：guest用户无法访问用户列表")
            else:
                print(f"⚠️ 权限检查异常: {response.status_code} - {response.text}")
                
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    print("开始测试权限系统...")
    test_admin_permissions()
    test_guest_permissions()
    print("\n=== 测试完成 ===")