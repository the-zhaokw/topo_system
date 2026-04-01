#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Bug导出功能修复
"""

import requests
import json

def test_bug_export():
    """测试Bug导出功能"""
    
    # 登录获取token
    login_url = 'http://localhost:5000/api/auth/login'
    login_data = {'username': 'admin', 'password': 'admin123'}
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print('✅ 登录成功')
            
            # 测试Bug导出功能
            headers = {'Authorization': f'Bearer {token}'}
            
            print('\\n📊 测试Bug导出功能:')
            export_url = 'http://localhost:5000/api/bugs/export?format=csv'
            response = requests.get(export_url, headers=headers)
            print(f'状态码: {response.status_code}')
            if response.status_code == 200:
                print('✅ Bug CSV导出成功')
                print(f'文件大小: {len(response.content)} bytes')
                content_type = response.headers.get('Content-Type', '未知')
                print(f'内容类型: {content_type}')
            else:
                print(f'❌ Bug CSV导出失败: {response.text}')
            
            # 测试Excel导出
            print('\\n📊 测试Bug Excel导出:')
            export_url = 'http://localhost:5000/api/bugs/export?format=excel'
            response = requests.get(export_url, headers=headers)
            print(f'状态码: {response.status_code}')
            if response.status_code == 200:
                print('✅ Bug Excel导出成功')
                print(f'文件大小: {len(response.content)} bytes')
            else:
                print(f'❌ Bug Excel导出失败: {response.text}')
        else:
            print('❌ 登录失败')
            
    except Exception as e:
        print(f'❌ 测试异常: {e}')

if __name__ == "__main__":
    test_bug_export()