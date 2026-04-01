#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统完整性测试脚本
测试所有功能模块，确保系统稳定运行
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

def login():
    """登录获取访问令牌"""
    try:
        response = requests.post(LOGIN_URL, json=TEST_USER)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ 登录成功，令牌: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_api_endpoints(token):
    """测试所有API端点"""
    endpoints = [
        ("GET", "/api/v1/bugs", "Bug列表"),
        ("GET", "/api/v1/projects", "项目列表"),
        ("GET", "/api/v1/users", "用户列表"),
        ("GET", "/api/v1/activities", "活动记录"),
        ("GET", "/api/v1/comments", "评论列表"),
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers)
            
            if response.status_code in [200, 201]:
                print(f"✅ {description} API测试通过")
            elif response.status_code == 404:
                print(f"⚠️ {description} API端点不存在")
            else:
                print(f"❌ {description} API测试失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description} API测试异常: {e}")

def test_export_functions(token):
    """测试导出功能"""
    export_endpoints = [
        ("/api/bugs/export?format=csv", "Bug数据CSV导出"),
        ("/api/bugs/export?format=excel", "Bug数据Excel导出"),
        ("/api/activities/export/csv", "活动记录CSV导出"),
        ("/api/activities/export/xlsx", "活动记录Excel导出"),
        ("/api/users/export/csv", "用户数据CSV导出"),
        ("/api/users/export/xlsx", "用户数据Excel导出"),
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for endpoint, description in export_endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # 检查响应内容类型
                content_type = response.headers.get('Content-Type', '')
                content_length = len(response.content)
                
                if 'csv' in content_type or 'excel' in content_type:
                    print(f"✅ {description}测试通过 (大小: {content_length} bytes)")
                else:
                    print(f"⚠️ {description}响应类型异常: {content_type}")
            else:
                print(f"❌ {description}测试失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}测试异常: {e}")

def test_database_connection():
    """测试数据库连接"""
    try:
        import sqlite3
        # 检查多个可能的数据库文件位置
        db_paths = [
            "instance/topo_system.db",
            "instance/enhanced_bug_system.db",
            "enhanced_topo_system.db"
        ]
        
        db_found = False
        for db_path in db_paths:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 检查表是否存在
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                if tables:  # 只在有表的情况下检查
                    print(f"✅ 数据库连接正常 ({db_path})，包含 {len(tables)} 个表")
                    
                    # 检查关键表
                    required_tables = ['user', 'project', 'bug', 'activity', 'comment']
                    existing_tables = [table[0] for table in tables]
                    
                    for table in required_tables:
                        if table in existing_tables:
                            print(f"✅ 表 {table} 存在")
                        else:
                            print(f"❌ 表 {table} 缺失")
                    
                    conn.close()
                    db_found = True
                    break
                else:
                    print(f"⚠️ 数据库文件存在但无表: {db_path}")
                    conn.close()
        
        if not db_found:
            print("❌ 没有找到包含表的数据库文件")
            
    except Exception as e:
        print(f"❌ 数据库连接测试异常: {e}")

def test_file_uploads():
    """测试文件上传目录"""
    upload_dirs = [
        "uploads",
        "uploads/bugs",
        "uploads/projects",
        "uploads/users"
    ]
    
    for dir_path in upload_dirs:
        if os.path.exists(dir_path):
            print(f"✅ 上传目录 {dir_path} 存在")
        else:
            print(f"❌ 上传目录 {dir_path} 缺失")

def test_database_backup():
    """测试数据库备份功能"""
    try:
        import sys
        import os
        
        # 添加当前目录到Python路径
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # 导入备份模块
        import backup_database
        
        # 执行备份
        result = backup_database.backup_database()
        
        if result:
            print("✅ 数据库备份测试通过")
        else:
            print("❌ 数据库备份测试失败")
            
    except Exception as e:
        print(f"❌ 数据库备份测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始系统完整性测试...\n")
    
    # 测试数据库连接
    print("📊 测试数据库连接...")
    test_database_connection()
    print()
    
    # 测试文件上传目录
    print("📁 测试文件上传目录...")
    test_file_uploads()
    print()
    
    # 登录获取令牌
    print("🔐 测试用户登录...")
    token = login()
    print()
    
    if not token:
        print("❌ 无法获取访问令牌，终止测试")
        return
    
    # 测试API端点
    print("🌐 测试API端点...")
    test_api_endpoints(token)
    print()
    
    # 测试导出功能
    print("📤 测试导出功能...")
    test_export_functions(token)
    print()
    
    # 测试数据库备份
    print("💾 测试数据库备份...")
    test_database_backup()
    print()
    
    print("🎉 系统测试完成！")

if __name__ == "__main__":
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        sys.exit(1)