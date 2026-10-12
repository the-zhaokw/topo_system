"""读取 schema.zip 中的关键 XML 文件"""
import zipfile
import re

z = zipfile.ZipFile('d:/topo_system/backend/schema.zip', 'r')

# 1. 读取 devMng.xml (主模块配置)
print("=== devMng.xml ===")
try:
    content = z.read('devMng/devMng.xml').decode('utf-8', errors='replace')
    print(content[:5000])
except:
    pass

# 2. 读取 devMng.dataManageUI.xml
print("\n\n=== devMng.dataManageUI.xml ===")
try:
    content = z.read('devMng/devMng.dataManageUI.xml').decode('utf-8', errors='replace')
    print(content[:8000])
except:
    pass

# 3. 读取 project.dataModel.xml
print("\n\n=== project.dataModel.xml ===")
try:
    content = z.read('devMng/project.dataModel.xml').decode('utf-8', errors='replace')
    print(content)
except:
    pass

# 4. 读取 layout.xml
print("\n\n=== layout.xml ===")
try:
    content = z.read('layout.xml').decode('utf-8', errors='replace')
    print(content[:5000])
except:
    pass

z.close()
