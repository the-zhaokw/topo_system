import requests
import json

base_url = "http://localhost:5000/api/v1/api/v1"  # 由于蓝图嵌套注册导致的路径问题
auth_url = "http://localhost:5000/api/v1"

def test_task_api():
    """测试任务管理API功能"""
    print("开始测试任务管理API功能...")
    
    # 0. 登录获取JWT Token
    print("\n0. 登录获取认证Token...")
    token = None
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{auth_url}/auth/login", json=login_data)
        print(f"状态码: {response.status_code}")
        try:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            if data.get('success') and data.get('data', {}).get('access_token'):
                token = data['data']['access_token']
                print("登录成功，已获取Token")
            elif data.get('access_token'):
                # 兼容其他可能的响应格式
                token = data['access_token']
                print("登录成功，已获取Token")
        except json.JSONDecodeError:
            print(f"响应不是JSON格式: {response.text}")
    except Exception as e:
        print(f"登录失败: {str(e)}")
    
    if not token:
        print("\n未获取到认证Token，无法继续测试API")
        return
    
    # 设置请求头，包含JWT Token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 1. 首先尝试获取任务列表
    print("\n1. 获取任务列表...")
    try:
        # 确保使用正确的API端点路径
        response = requests.get(f"{base_url}/tasks", headers=headers)
        print(f"状态码: {response.status_code}")
        try:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError:
            print(f"响应不是JSON格式: {response.text}")
    except Exception as e:
        print(f"获取任务列表失败: {str(e)}")
    
    # 2. 创建新任务
    print("\n2. 创建新任务...")
    try:
        new_task = {
            "title": "测试任务API",
            "description": "这是一个用于测试API的任务",
            "status": "todo",
            "priority": "medium",
            # creator_id会自动从token中获取，不需要手动指定
            "assignee_id": 3,
            "project_id": 4
        }
        # 确保使用正确的API端点路径
        response = requests.post(f"{base_url}/tasks", json=new_task, headers=headers)
        print(f"状态码: {response.status_code}")
        try:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            task_id = data.get('id') if isinstance(data, dict) else None
        except json.JSONDecodeError:
            print(f"响应不是JSON格式: {response.text}")
            task_id = None
    except Exception as e:
        print(f"创建任务失败: {str(e)}")
        task_id = None
    
    # 3. 如果任务创建成功，测试获取单个任务
    if task_id:
        print(f"\n3. 获取任务ID {task_id} 的详细信息...")
        try:
            response = requests.get(f"{base_url}/tasks/{task_id}", headers=headers)
            print(f"状态码: {response.status_code}")
            try:
                data = response.json()
                print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            except json.JSONDecodeError:
                print(f"响应不是JSON格式: {response.text}")
        except Exception as e:
            print(f"获取任务详情失败: {str(e)}")
        
        # 4. 更新任务
        print(f"\n4. 更新任务ID {task_id}...")
        try:
            update_data = {
                "status": "进行中",
                "priority": "高",
                "description": "已更新的任务描述"
            }
            response = requests.put(f"{base_url}/tasks/{task_id}", json=update_data, headers=headers)
            print(f"状态码: {response.status_code}")
            try:
                data = response.json()
                print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            except json.JSONDecodeError:
                print(f"响应不是JSON格式: {response.text}")
        except Exception as e:
            print(f"更新任务失败: {str(e)}")
        
        # 5. 删除任务（可选，根据测试需求决定是否执行）
        print(f"\n5. 删除任务ID {task_id}...")
        try:
            response = requests.delete(f"{base_url}/tasks/{task_id}", headers=headers)
            print(f"状态码: {response.status_code}")
            try:
                data = response.json()
                print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            except json.JSONDecodeError:
                print(f"响应不是JSON格式: {response.text}")
        except Exception as e:
            print(f"删除任务失败: {str(e)}")
    
    print("\n任务管理API测试完成！")

if __name__ == "__main__":
    test_task_api()