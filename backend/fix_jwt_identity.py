#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def fix_get_jwt_identity_issue():
    """修复项目中 get_jwt_identity() 调用错误的问题"""
    
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
            
            # 查找并修复 get_jwt_identity_func = get_jwt_identity 问题
            if 'get_jwt_identity_func = get_jwt_identity' in content:
                # 使用正则表达式进行更精确的替换
                pattern = r'get_jwt_identity_func = get_jwt_identity\(\)'
                replacement = 'get_jwt_identity_func = get_jwt_identity'
                new_content = re.sub(pattern, replacement, content)
                
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ 修复文件: {file_path}")
                    fixed_count += 1
                    
        except Exception as e:
            print(f"❌ 处理文件失败 {file_path}: {e}")
    
    print(f"\n总共修复了 {fixed_count} 个文件")
    return fixed_count

if __name__ == '__main__':
    fix_get_jwt_identity_issue()