#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务详情格式导出测试脚本
按照用户提供的任务详情格式测试CSV导出功能
"""

import requests
import json
import csv
import io
from datetime import datetime

# 配置
BASE_URL = 'http://localhost:5000'
LOGIN_URL = f'{BASE_URL}/api/auth/login'

# 测试用户凭据
TEST_USER = {
    'username': 'admin',
    'password': 'admin123'
}

def login():
    """登录获取JWT令牌"""
    print("🔐 登录系统...")
    
    response = requests.post(LOGIN_URL, json=TEST_USER)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        if token:
            print("✅ 登录成功")
            return token
        else:
            print("❌ 登录失败: 未获取到token")
            return None
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return None

def test_task_details_export(token):
    """测试任务详情格式导出功能"""
    print("\n📋 测试任务详情格式导出功能")
    
    # 调用任务详情导出API
    export_url = f'{BASE_URL}/api/activities/export/csv'
    response = requests.get(export_url, headers={'Authorization': f'Bearer {token}'})
    
    print(f"导出状态码: {response.status_code}")
    
    if response.status_code == 200:
        # 保存CSV文件
        filename = f'task_details_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ 任务详情文件已保存: {filename}")
        
        # 解析并显示CSV内容
        print("\n📊 任务详情数据预览:")
        
        # 处理BOM并解码
        content = response.content.decode('utf-8-sig')
        reader = csv.reader(io.StringIO(content))
        
        # 显示头部信息
        headers = next(reader)  # 第一行：任务详情,状态,优先级,基本信息
        print(f"📝 表头: {headers}")
        
        # 显示字段标题
        field_headers = next(reader)  # 第二行：具体字段标题
        print(f"📋 字段标题: {field_headers}")
        
        # 显示前5条数据记录
        print("\n📈 数据记录预览:")
        for i, row in enumerate(reader):
            if i >= 5:  # 只显示前5条
                break
            if len(row) >= 3:  # 确保有足够的数据
                print(f"{i+1}. 标题: {row[0]}, 状态: {row[1]}, 优先级: {row[2]}, 创建者: {row[3]}")
        
        # 显示文件统计信息
        content_lines = content.strip().split('\n')
        print(f"\n📊 文件统计:")
        print(f"   总行数: {len(content_lines)}")
        print(f"   数据记录数: {len(content_lines) - 2}")  # 减去表头和字段标题行
        
        return True
    else:
        print(f"❌ 导出失败: {response.text}")
        return False

def main():
    """主函数"""
    print("🚀 开始任务详情格式导出测试")
    print("=" * 50)
    
    # 登录获取token
    token = login()
    if not token:
        print("❌ 无法继续测试，登录失败")
        return
    
    # 测试任务详情导出
    success = test_task_details_export(token)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 任务详情格式导出测试完成")
    else:
        print("❌ 任务详情格式导出测试失败")

if __name__ == '__main__':
    main()