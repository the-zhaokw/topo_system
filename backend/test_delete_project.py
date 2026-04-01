#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

base_url = 'http://localhost:5000/api/v1'

def test_delete_project():
    # 登录admin账户
    print('1. 登录admin账户...')
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }

    response = requests.post(f'{base_url}/auth/login', json=login_data)
    print(f'登录响应: {response.status_code}')
    
    if response.status_code != 200:
        print(f'登录失败: {response.text}')
        return
        
    login_result = response.json()
    print(f'登录结果: {json.dumps(login_result, indent=2, ensure_ascii=False)}')

    token = login_result['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 获取项目列表
    print('\n2. 获取项目列表...')
    response = requests.get(f'{base_url}/projects', headers=headers)
    print(f'获取项目列表响应: {response.status_code}')
    
    if response.status_code != 200:
        print(f'获取项目列表失败: {response.text}')
        return
        
    projects_result = response.json()
    print(f'共有 {len(projects_result["projects"])} 个项目')
    
    # 显示前3个项目的详细信息
    for i, project in enumerate(projects_result['projects'][:3]):
        print(f'  项目 {i+1}: ID={project["id"]}, 名称={project["name"]}, owner_id={project["owner_id"]}')
        
    # 尝试删除admin创建的项目
    admin_projects = [p for p in projects_result['projects'] if p.get('owner_id') == 1]
    print(f'\n3. admin创建的项目数量: {len(admin_projects)}')
    
    if admin_projects:
        project_to_delete = admin_projects[0]
        print(f'4. 尝试删除项目: ID={project_to_delete["id"]}, 名称={project_to_delete["name"]}')
        
        response = requests.delete(f'{base_url}/projects/{project_to_delete["id"]}', headers=headers)
        print(f'删除项目响应: {response.status_code}')
        print(f'删除响应内容: {response.text}')
        
        if response.status_code == 200:
            print('\n✅ 删除项目成功！')
        else:
            print('\n❌ 删除项目失败')
    else:
        print('4. 没有找到admin创建的项目')

if __name__ == '__main__':
    test_delete_project()