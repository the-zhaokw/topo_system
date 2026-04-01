import requests
import json

# 基础URL
BASE_URL = 'http://localhost:5000'

print("开始测试用户认证和权限系统...\n")

def test_admin_login():
    """测试管理员登录"""
    print("1. 测试管理员登录...")
    auth_url = f"{BASE_URL}/api/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(auth_url, json=login_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("管理员登录成功")
        return response.json().get('access_token')
    else:
        print(f"管理员登录失败: {response.text}")
        return None

def test_create_developer_user(admin_token):
    """测试管理员创建开发者用户"""
    print("\n2. 测试创建开发者用户...")
    if not admin_token:
        print("跳过，管理员未登录")
        return None
    
    users_url = f"{BASE_URL}/api/users"
    headers = {'Authorization': f'Bearer {admin_token}'}
    user_data = {
        "username": "testdev",
        "email": "dev@test.com",
        "password": "dev123",
        "role": "developer"
    }
    
    response = requests.post(users_url, json=user_data, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {response.text}")
    
    if response.status_code == 201:
        print("开发者用户创建成功")
        return "testdev"
    else:
        print("开发者用户创建失败")
        return None

def test_developer_login(developer_username):
    """测试开发者登录"""
    print(f"\n3. 测试开发者 '{developer_username}' 登录...")
    if not developer_username:
        print("跳过，开发者用户未创建")
        return None
    
    auth_url = f"{BASE_URL}/api/auth/login"
    login_data = {
        "username": developer_username,
        "password": "dev123"
    }
    
    response = requests.post(auth_url, json=login_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("开发者登录成功")
        return response.json().get('access_token')
    else:
        print(f"开发者登录失败: {response.text}")
        return None

def test_permissions(admin_token, developer_token):
    """测试权限系统"""
    print("\n4. 测试权限系统...")
    
    # 测试管理员可以访问的资源
    if admin_token:
        print("\n4.1 测试管理员权限 (查看所有用户)...")
        users_url = f"{BASE_URL}/api/users"
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = requests.get(users_url, headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("管理员权限正常 - 可以查看所有用户")
        else:
            print(f"管理员权限异常: {response.text}")
    
    # 测试开发者权限 (应该无法访问某些管理员资源)
    if developer_token:
        print("\n4.2 测试开发者权限 (尝试查看所有用户)...")
        users_url = f"{BASE_URL}/api/users"
        headers = {'Authorization': f'Bearer {developer_token}'}
        response = requests.get(users_url, headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 403:
            print("开发者权限正常 - 无法访问管理员资源")
        else:
            print(f"开发者权限异常: {response.text}")
    
    # 测试普通用户可访问的资源 (如任务列表)
    if developer_token:
        print("\n4.3 测试开发者访问任务列表...")
        tasks_url = f"{BASE_URL}/api/v1/tasks"
        headers = {'Authorization': f'Bearer {developer_token}'}
        response = requests.get(tasks_url, headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("开发者可以正常访问任务列表")
        else:
            print(f"访问任务列表失败: {response.text}")

def test_user_registration():
    """测试用户注册功能"""
    print("\n5. 测试用户注册功能...")
    register_url = f"{BASE_URL}/api/auth/register"
    register_data = {
        "username": "newuser",
        "email": "new@test.com",
        "password": "newuser123"
    }
    
    response = requests.post(register_url, json=register_data)
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {response.text}")
    
    if response.status_code == 201:
        print("用户注册成功")
        return True
    else:
        print("用户注册失败或已存在")
        return False

def test_get_user_profile(token):
    """测试获取用户资料"""
    print("\n6. 测试获取用户资料...")
    if not token:
        print("跳过，没有有效的token")
        return
    
    profile_url = f"{BASE_URL}/api/auth/profile"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(profile_url, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("获取用户资料成功")
        user_data = response.json()
        print(f"用户名: {user_data.get('username')}")
        print(f"邮箱: {user_data.get('email')}")
        print(f"角色: {user_data.get('role')}")
    else:
        print(f"获取用户资料失败: {response.text}")

def main():
    try:
        # 1. 管理员登录
        admin_token = test_admin_login()
        
        # 2. 创建开发者用户
        developer_username = test_create_developer_user(admin_token)
        
        # 3. 开发者登录
        developer_token = test_developer_login(developer_username)
        
        # 4. 测试权限系统
        test_permissions(admin_token, developer_token)
        
        # 5. 测试用户注册
        test_user_registration()
        
        # 6. 测试获取用户资料
        test_get_user_profile(admin_token)
        
        print("\n用户认证和权限系统测试完成！")
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")

if __name__ == "__main__":
    main()