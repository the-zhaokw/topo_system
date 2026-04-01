#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys

base_url = 'http://localhost:5000/api/v1'

def test_project_creation():
    print("=== 项目创建功能测试 ===")
    
    # 1. 登录admin账户
    print("\n1. 登录admin账户...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }

    try:
        response = requests.post(f'{base_url}/auth/login', json=login_data)
        print(f'登录响应状态码: {response.status_code}')
        
        if response.status_code != 200:
            print(f'❌ 登录失败: {response.text}')
            return False
            
        login_result = response.json()
        print(f'✅ 登录成功')

        token = login_result['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 2. 创建测试项目
        print("\n2. 创建测试项目...")
        project_data = {
            'name': '测试项目 - 功能验证',
            'code': 'TEST_PROJ_001',
            'description': '这是一个用于测试项目创建功能的测试项目',
            'priority': 'high',
            'technology_stack': 'Python, Flask, Vue.js',
            'budget': 50000,
            'progress': 0
        }
        
        response = requests.post(f'{base_url}/projects', json=project_data, headers=headers)
        print(f'创建项目响应状态码: {response.status_code}')
        
        if response.status_code == 201:
            create_result = response.json()
            print(f'✅ 项目创建成功')
            print(f'   项目ID: {create_result["project"]["id"]}')
            print(f'   项目名称: {create_result["project"]["name"]}')
            
            # 安全地获取项目代码，如果不存在则使用默认值
            project_code = create_result.get('project', {}).get('code', 'N/A')
            print(f'   项目代码: {project_code}')
            
            project_id = create_result['project']['id']
            
            # 3. 验证项目是否成功写入数据库
            print("\n3. 验证项目是否成功写入数据库...")
            response = requests.get(f'{base_url}/projects/{project_id}', headers=headers)
            print(f'获取项目详情响应状态码: {response.status_code}')
            
            if response.status_code == 200:
                project_detail = response.json()
                print(f'✅ 数据库验证成功')
                
                # 安全地获取项目详情字段
                project_data = project_detail.get('project', {})
                print(f'   项目名称: {project_data.get("name", "N/A")}')
                print(f'   项目代码: {project_data.get("code", "N/A")}')
                print(f'   项目状态: {project_data.get("status", "N/A")}')
                print(f'   项目进度: {project_data.get("progress", "N/A")}%')
                
                # 4. 验证项目是否在项目列表中
                print("\n4. 验证项目是否在项目列表中...")
                response = requests.get(f'{base_url}/projects', headers=headers)
                print(f'获取项目列表响应状态码: {response.status_code}')
                
                if response.status_code == 200:
                    projects_result = response.json()
                    project_in_list = any(p['id'] == project_id for p in projects_result['projects'])
                    
                    if project_in_list:
                        print(f'✅ 项目在列表中验证成功')
                        print(f'   项目总数: {len(projects_result["projects"])}')
                        
                        # 5. 测试重复项目代码验证
                        print("\n5. 测试重复项目代码验证...")
                        duplicate_project_data = {
                            'name': '重复项目测试',
                            'code': 'TEST_PROJ_001',  # 使用相同的项目代码
                            'description': '测试重复项目代码验证'
                        }
                        
                        response = requests.post(f'{base_url}/projects', json=duplicate_project_data, headers=headers)
                        print(f'重复项目创建响应状态码: {response.status_code}')
                        
                        if response.status_code == 400:
                            print(f'✅ 重复项目代码验证成功')
                            print(f'   错误信息: {response.json()["error"]}')
                        else:
                            print(f'❌ 重复项目代码验证失败')
                            return False
                        
                        # 6. 测试必填字段验证
                        print("\n6. 测试必填字段验证...")
                        invalid_project_data = {
                            'name': '',  # 空名称
                            'code': ''   # 空代码
                        }
                        
                        response = requests.post(f'{base_url}/projects', json=invalid_project_data, headers=headers)
                        print(f'无效项目创建响应状态码: {response.status_code}')
                        
                        if response.status_code == 400:
                            print(f'✅ 必填字段验证成功')
                            print(f'   错误信息: {response.json()["error"]}')
                        else:
                            print(f'❌ 必填字段验证失败')
                            return False
                        
                        print("\n🎉 项目创建功能测试全部通过！")
                        return True
                    else:
                        print(f'❌ 项目不在列表中')
                        return False
                else:
                    print(f'❌ 获取项目列表失败: {response.text}')
                    return False
            else:
                print(f'❌ 数据库验证失败: {response.text}')
                return False
        else:
            print(f'❌ 项目创建失败: {response.text}')
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_project_creation()
    sys.exit(0 if success else 1)