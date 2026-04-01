import requests
import json

# 测试登录获取token
login_url = "http://localhost:5000/api/auth/login"
login_data = {
    "username": "admin",
    "password": "admin123"
}

try:
    # 登录获取token
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"登录成功，token: {token[:20]}...")
        
        # 测试项目API
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        projects_url = "http://localhost:5000/api/projects"
        response = requests.get(projects_url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"项目API调用成功，返回数据: {result}")
            if isinstance(result, list):
                print(f"返回项目数量: {len(result)}")
                for project in result:
                    print(f"项目ID: {project['id']}, 名称: {project['name']}, 状态: {project['status']}")
            else:
                print(f"返回数据类型: {type(result)}")
        else:
            print(f"项目API调用失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
    else:
        print(f"登录失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        
except Exception as e:
    print(f"测试过程中出现错误: {str(e)}")