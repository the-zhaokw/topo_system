#!/usr/bin/env python3
"""
启动后端服务并测试路由
"""
import sys
import os
import subprocess
import time
import requests

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("启动后端服务...")
print("=" * 60)

# 启动后端服务
process = subprocess.Popen(
    [sys.executable, 'run_app.py'],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# 等待服务启动
time.sleep(5)

# 读取启动输出
output = ""
while True:
    line = process.stdout.readline()
    if not line:
        break
    output += line
    print(line, end='')
    if "Running on" in line:
        break

print("\n" + "=" * 60)
print("测试 API 端点...")
print("=" * 60)

# 测试各个端点
endpoints = [
    'http://localhost:5000/api/system/time',
    'http://localhost:5000/api/auth/login',
    'http://localhost:5000/api/health',
]

for url in endpoints:
    try:
        r = requests.get(url, timeout=5)
        print(f"{url}: {r.status_code}")
        if r.status_code == 200:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"{url}: Error - {e}")

print("=" * 60)
print("停止后端服务...")
process.terminate()
process.wait()
print("完成!")
