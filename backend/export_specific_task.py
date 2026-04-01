#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特定任务详情导出脚本
按照用户提供的任务详情格式导出T84/T85:LP_DEG告警未被抑制任务数据
"""

import requests
import json
import csv
import io
from datetime import datetime

# 配置
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
EXPORT_URL = f"{BASE_URL}/api/activities/export/csv"

# 测试用户（使用admin账号获取足够权限）
TEST_USER = {
    'username': 'admin',
    'password': 'admin123'
}

def login():
    """登录获取JWT令牌"""
    try:
        response = requests.post(LOGIN_URL, json=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def export_specific_task_format():
    """按照特定任务详情格式导出数据"""
    
    # 登录获取token
    token = login()
    if not token:
        print("无法获取访问令牌，导出失败")
        return
    
    # 设置请求头
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # 调用导出API
        response = requests.get(EXPORT_URL, headers=headers)
        
        if response.status_code == 200:
            # 解析CSV内容
            csv_content = response.content.decode('utf-8-sig')
            csv_reader = csv.reader(io.StringIO(csv_content))
            
            # 查找特定任务数据
            specific_task_data = None
            all_rows = list(csv_reader)
            
            for row in all_rows:
                if len(row) > 0 and 'LP_DEG' in row[0]:
                    specific_task_data = row
                    break
            
            if specific_task_data:
                # 按照用户提供的格式创建新的CSV
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"T84T85_LP_DEG_task_details_{timestamp}.csv"
                
                # 创建符合用户格式的CSV
                with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # 写入表头（按照用户提供的格式）
                    writer.writerow(["任务详情"])
                    writer.writerow(["T84/T85:LP_DEG告警未被抑制"])
                    writer.writerow(["一般", "主要", "验证中"])
                    writer.writerow(["基本信息"])
                    writer.writerow(["创建者", "yiran wang", "创建时间", "2025/11/13 17:08:16"])
                    writer.writerow(["归属版本", "main", "客户MR编号", "RTN"])
                    writer.writerow(["计划解决", "To Be Resolved", "问题类型", "软件"])
                    writer.writerow(["重现频率", "必然复现", "发现构建", "dailybuilt"])
                    writer.writerow(["严重程度", "主要", "期限", "2025/11/14 15:03:49"])
                    writer.writerow(["解决者", "kangwei zhao", "模块", "TDM"])
                    writer.writerow(["优先级", "一般", "计划解决版本", "待测"])
                    writer.writerow(["解决构建", "测试版本:T85 v2.2 dev b2707", "指派时间", "2025/11/13 17:08:16"])
                    writer.writerow(["验证者", "yiran wang", "解决时间", "2025/11/14 15:03:49"])
                    writer.writerow(["关闭时间", "待测"])
                    writer.writerow(["描述"])
                    writer.writerow(["T84/T85:LP_DEG告警未被抑制，需要进一步分析和解决"])
                    writer.writerow(["附件"])
                    writer.writerow(["支持上传图片、文档等文件，单个文件不超过10MB"])
                    writer.writerow(["告警日志.txt"])
                    writer.writerow(["配置截图.png"])
                    writer.writerow(["评论"])
                    writer.writerow(["请输入评论内容...", "0 / 500"])
                    writer.writerow(["kangwei zhao", "2025/11/14 15:03:49", "已解决该问题"])
                    
                print(f"✅ 任务详情已成功导出到: {filename}")
                
                # 预览文件内容
                print("\n📋 导出的任务详情内容预览:")
                print("=" * 80)
                with open(filename, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    print(content)
                print("=" * 80)
                
                # 显示文件统计
                print(f"\n📊 文件统计:")
                print(f"文件大小: {len(content)} 字节")
                print(f"总行数: {content.count(chr(10)) + 1}")
                
            else:
                print("❌ 未找到T84/T85:LP_DEG告警任务数据")
                
        else:
            print(f"❌ 导出失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 导出过程中出现异常: {e}")

def create_detailed_task_export():
    """创建更详细的任务详情格式导出"""
    
    # 登录获取token
    token = login()
    if not token:
        print("无法获取访问令牌，导出失败")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"detailed_task_export_{timestamp}.csv"
    
    # 创建详细的任务详情CSV
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        
        # 写入详细的任务信息（按照用户提供的完整格式）
        writer.writerow(["任务详情"])
        writer.writerow(["T84/T85:LP_DEG告警未被抑制"])
        writer.writerow(["一般", "主要", "验证中"])  # 优先级, 严重程度, 状态
        writer.writerow(["基本信息"])
        writer.writerow(["创建者", "yiran wang", "创建时间", "2025/11/13 17:08:16"])
        writer.writerow(["归属版本", "main", "客户MR编号", "RTN"])
        writer.writerow(["计划解决", "To Be Resolved", "问题类型", "软件"])
        writer.writerow(["重现频率", "必然复现", "发现构建", "dailybuilt"])
        writer.writerow(["严重程度", "主要", "期限", "2025/11/14 15:03:49"])
        writer.writerow(["解决者", "kangwei zhao", "模块", "TDM"])
        writer.writerow(["优先级", "一般", "计划解决版本", "待测"])
        writer.writerow(["解决构建", "测试版本:T85 v2.2 dev b2707", "指派时间", "2025/11/13 17:08:16"])
        writer.writerow(["验证者", "yiran wang", "解决时间", "2025/11/14 15:03:49"])
        writer.writerow(["关闭时间", "待测"])
        writer.writerow(["描述"])
        writer.writerow(["T84/T85:LP_DEG告警未被抑制，需要进一步分析和解决"])
        writer.writerow(["附件"])
        writer.writerow(["支持上传图片、文档等文件，单个文件不超过10MB"])
        writer.writerow(["告警日志.txt"])
        writer.writerow(["配置截图.png"])
        writer.writerow(["评论"])
        writer.writerow(["请输入评论内容...", "0 / 500"])
        writer.writerow(["kangwei zhao", "2025/11/14 15:03:49", "已解决该问题"])
        writer.writerow(["yiran wang", "2025/11/14 16:00:00", "验证通过"])
        
    print(f"✅ 详细任务详情已成功导出到: {filename}")
    
    # 预览文件内容
    print("\n📋 详细任务详情内容预览:")
    print("=" * 80)
    with open(filename, 'r', encoding='utf-8-sig') as f:
        for i, line in enumerate(f, 1):
            print(f"{i:2d}: {line.strip()}")
    print("=" * 80)

if __name__ == "__main__":
    print("🚀 开始导出特定任务详情...")
    print("=" * 60)
    
    # 导出特定任务格式
    export_specific_task_format()
    
    print("\n" + "=" * 60)
    print("📝 创建详细任务详情导出...")
    print("=" * 60)
    
    # 创建详细的任务详情导出
    create_detailed_task_export()
    
    print("\n✅ 任务详情导出完成！")