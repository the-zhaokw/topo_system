"""完整读取 schema.zip 中所有文件，重点找 dmBug 模型和服务配置"""
import zipfile
import re

z = zipfile.ZipFile('d:/topo_system/backend/schema.zip', 'r')

# 列出所有文件
print("=== 所有文件列表 ===")
for name in z.namelist():
    info = z.getinfo(name)
    print(f"  {name} ({info.file_size} bytes)")

# 查找 dmBug 相关文件
print("\n=== dmBug 相关文件 ===")
for name in z.namelist():
    if 'bug' in name.lower() or 'Bug' in name:
        print(f"  {name}")

# 读取 dmBug.dataModel.xml
print("\n=== dmBug.dataModel.xml ===")
for name in z.namelist():
    if 'dmBug' in name and 'dataModel' in name:
        content = z.read(name).decode('utf-8', errors='replace')
        print(content)
        break

# 查找服务配置文件
print("\n=== 服务配置文件 ===")
for name in z.namelist():
    lower = name.lower()
    if 'service' in lower or 'config' in lower or 'remoting' in lower or 'amf' in lower or 'messaging' in lower:
        print(f"  {name}")

# 读取可能的配置文件
print("\n=== 配置文件内容 ===")
for name in z.namelist():
    lower = name.lower()
    if 'service' in lower or 'config' in lower or 'remoting' in lower or 'proxy' in lower:
        try:
            content = z.read(name).decode('utf-8', errors='replace')
            print(f"\n--- {name} ---")
            print(content[:5000])
        except:
            pass

# 查找 organization/org 相关
print("\n=== org 相关文件 ===")
for name in z.namelist():
    if 'org' in name.lower() and 'organization' not in name.lower():
        print(f"  {name}")

# 读取 organization 相关文件
print("\n=== organization 相关文件 ===")
for name in z.namelist():
    if 'organization' in name.lower() or ('org' in name.lower() and name.endswith('.xml')):
        try:
            content = z.read(name).decode('utf-8', errors='replace')
            print(f"\n--- {name} ---")
            print(content[:5000])
        except:
            pass

# 查找 *.xml 中包含 destination 或 channel 的文件
print("\n=== 包含 destination/channel 定义的文件 ===")
for name in z.namelist():
    if name.endswith('.xml') or name.endswith('.properties'):
        try:
            content = z.read(name).decode('utf-8', errors='replace')
            if 'destination' in content.lower() or 'channel' in content.lower() or 'amf' in content.lower():
                print(f"\n--- {name} ---")
                print(content[:3000])
        except:
            pass

z.close()
