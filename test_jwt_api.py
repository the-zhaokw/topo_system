#!/usr/bin/env python3
"""
测试JWT修复后的API端点
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:5000/api/v1"

def get_valid_jwt_token():
    """获取有效的JWT令牌"""
    # 首先尝试登录获取有效令牌
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"登录失败: {response.status_code}")
            print(f"响应: {response.text}")
            return None
    except Exception as e:
        print(f"登录请求异常: {e}")
        return None

def test_statistics_api(token):
    """测试统计API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 测试dashboard端点
    print("测试 /statistics/dashboard 端点...")
    try:
        response = requests.get(f"{BASE_URL}/statistics/dashboard", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ dashboard端点测试成功")
            print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ dashboard端点测试失败: {response.text}")
    except Exception as e:
        print(f"❌ dashboard端点请求异常: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试tasks端点
    print("测试 /statistics/tasks 端点...")
    try:
        response = requests.get(f"{BASE_URL}/statistics/tasks", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ tasks端点测试成功")
            print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ tasks端点测试失败: {response.text}")
    except Exception as e:
        print(f"❌ tasks端点请求异常: {e}")

if __name__ == "__main__":
    print("开始测试JWT修复后的API端点...")
    
    # 获取有效JWT令牌
    token = get_valid_jwt_token()
    if not token:
        print("❌ 无法获取有效的JWT令牌，测试终止")
        exit(1)
    
    print(f"✅ 获取到有效JWT令牌: {token[:50]}...")
    
    # 测试统计API
    test_statistics_api(token)