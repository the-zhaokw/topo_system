#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for data export functionality
"""

import requests
import json
import sys

def test_export():
    """Test the statistics data export API"""
    
    # Login to get token
    # 使用正确的API路径，适配蓝图嵌套注册
    login_url = "http://127.0.0.1:5000/api/v1/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Login to get token
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ Login successful. Token: {token[:20]}...")
            
            # 使用正确的导出API端点和POST方法
            export_url = "http://127.0.0.1:5000/api/v1/statistics/export"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # 测试任务数据导出
            print("\n📊 Testing tasks data export...")
            tasks_export_data = {
                "export_type": "tasks"
            }
            
            task_response = requests.post(
                export_url,
                headers=headers,
                json=tasks_export_data
            )
            print(f"Tasks Export Status: {task_response.status_code}")
            
            if task_response.status_code == 200:
                task_data = task_response.json()
                print(f"✅ Tasks export successful")
                print(f"📊 Total records: {task_data.get('record_count', 0)}")
                
                # 保存任务导出数据到JSON文件
                with open('exported_tasks.json', 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)
                print("✅ Task data saved to exported_tasks.json")
            else:
                print(f"❌ Tasks export failed: {task_response.text}")
            
            # 测试缺陷数据导出
            print("\n📊 Testing bugs data export...")
            bugs_export_data = {
                "export_type": "bugs"
            }
            
            bug_response = requests.post(
                export_url,
                headers=headers,
                json=bugs_export_data
            )
            print(f"Bugs Export Status: {bug_response.status_code}")
            
            if bug_response.status_code == 200:
                bug_data = bug_response.json()
                print(f"✅ Bugs export successful")
                print(f"📊 Total records: {bug_data.get('record_count', 0)}")
                
                # 保存缺陷导出数据到JSON文件
                with open('exported_bugs.json', 'w', encoding='utf-8') as f:
                    json.dump(bug_data, f, ensure_ascii=False, indent=2)
                print("✅ Bug data saved to exported_bugs.json")
            else:
                print(f"❌ Bugs export failed: {bug_response.text}")
            
            # 测试项目数据导出
            print("\n📊 Testing projects data export...")
            projects_export_data = {
                "export_type": "projects"
            }
            
            project_response = requests.post(
                export_url,
                headers=headers,
                json=projects_export_data
            )
            print(f"Projects Export Status: {project_response.status_code}")
            
            if project_response.status_code == 200:
                project_data = project_response.json()
                print(f"✅ Projects export successful")
                print(f"📊 Total records: {project_data.get('record_count', 0)}")
                
                # 保存项目导出数据到JSON文件
                with open('exported_projects.json', 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, ensure_ascii=False, indent=2)
                print("✅ Project data saved to exported_projects.json")
            else:
                print(f"❌ Projects export failed: {project_response.text}")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing activities export functionality...")
    test_export()