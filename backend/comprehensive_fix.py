#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def comprehensive_fix():
    """全面修复JWT身份验证相关问题"""
    
    # 获取所有Python文件
    python_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    fixed_count = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. 修复 get_jwt_identity_func = get_jwt_identity() 问题
            content = re.sub(r'get_jwt_identity_func = get_jwt_identity\(\)', 
                           'get_jwt_identity_func = get_jwt_identity', content)
            
            # 2. 修复直接调用 current_user_id = get_jwt_identity() 但缺少对应的 get_jwt_identity_func 定义的情况
            # 这种情况下，正确的调用应该是 current_user_id = get_jwt_identity_func()
            content = re.sub(r'(?<!\w)current_user_id = get_jwt_identity\(\)', 
                           'current_user_id = get_jwt_identity_func()', content)
            
            # 3. 修复其他直接调用 get_jwt_identity() 但可能导致问题的情况
            content = re.sub(r'(?<!func\s*=\s*)get_jwt_identity\(\)(?!\))', 
                           'get_jwt_identity_func()', content)
            
            # 4. 修复在需要 get_jwt_identity_func 的地方使用了 get_jwt_identity 的情况
            content = re.sub(r'(?<!\w)get_jwt_identity\(\)(?!\s*\))', 
                           'get_jwt_identity_func()', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 修复文件: {file_path}")
                fixed_count += 1
                
        except Exception as e:
            print(f"❌ 处理文件失败 {file_path}: {e}")
    
    print(f"\n总共修复了 {fixed_count} 个文件")
    return fixed_count

if __name__ == '__main__':
    comprehensive_fix()