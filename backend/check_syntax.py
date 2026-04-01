#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check syntax of enhanced_app.py
"""

import ast
import sys

def check_syntax(filename):
    """Check Python syntax of a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the source code
        ast.parse(source)
        print(f"✅ {filename} has valid syntax")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in {filename}:")
        print(f"   Line {e.lineno}: {e.msg}")
        print(f"   Text: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error checking {filename}: {e}")
        return False

if __name__ == "__main__":
    if check_syntax("enhanced_app.py"):
        print("Syntax check passed!")
    else:
        print("Syntax check failed!")
        sys.exit(1)