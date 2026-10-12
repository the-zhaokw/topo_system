#!/usr/bin/env python3
"""
检查Flask应用路由是否正确注册
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_app import app, register_api_blueprints

# 注册API蓝图
register_api_blueprints()

print("=" * 60)
print("已注册的URL路由:")
print("=" * 60)

# 获取所有路由
routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        'endpoint': rule.endpoint,
        'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
        'path': rule.rule
    })

# 按路径排序
routes.sort(key=lambda x: x['path'])

# 打印所有路由
for route in routes:
    print(f"{route['path']:<50} {route['methods']:<20} {route['endpoint']}")

print("=" * 60)

# 检查 /api/system/time 路由是否存在
time_route_exists = any('/api/system/time' in r['path'] for r in routes)
if time_route_exists:
    print("✓ /api/system/time 路由已正确注册")
else:
    print("✗ /api/system/time 路由未找到")
    print("\n查找包含 'time' 的路由:")
    for r in routes:
        if 'time' in r['path']:
            print(f"  - {r['path']}")

print("=" * 60)
