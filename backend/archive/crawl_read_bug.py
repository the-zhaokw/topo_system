"""读取 schema.zip 中 dmBug 和 org 相关的 dataModel"""
import zipfile

z = zipfile.ZipFile('d:/topo_system/backend/schema.zip', 'r')

# 列出所有包含 bug 或 org 的文件
print("=== 包含 bug/org 的文件 ===")
for name in z.namelist():
    lower = name.lower()
    if 'bug' in lower or 'org' in lower or 'dmbug' in lower:
        print(f"  {name}")

# 读取 dmBug.dataModel.xml
print("\n\n=== dmBug.dataModel.xml ===")
try:
    content = z.read('devMng/dmBug.dataModel.xml').decode('utf-8', errors='replace')
    print(content)
except Exception as e:
    print(f"读取失败: {e}")
    # 尝试其他路径
    for name in z.namelist():
        if 'dmBug' in name and 'dataModel' in name:
            print(f"\n--- {name} ---")
            try:
                content = z.read(name).decode('utf-8', errors='replace')
                print(content)
            except Exception as e2:
                print(f"失败: {e2}")

# 读取 organization 相关
print("\n\n=== organization.dataModel.xml ===")
for name in z.namelist():
    if ('organization' in name.lower() or 'org.dataModel' in name.lower()) and 'dataModel' in name.lower():
        print(f"\n--- {name} ---")
        try:
            content = z.read(name).decode('utf-8', errors='replace')
            print(content[:5000])
        except Exception as e:
            print(f"失败: {e}")

# 列出所有 dataModel.xml 文件
print("\n\n=== 所有 dataModel.xml 文件 ===")
for name in z.namelist():
    if 'dataModel.xml' in name and not name.endswith('/'):
        print(f"  {name}")

z.close()
