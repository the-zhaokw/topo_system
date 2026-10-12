"""解密 schema.def 为 ZIP 文件并提取内容"""
import requests as req
import struct
import re
import zipfile
import io
from hashlib import md5
from Crypto.Cipher import DES

session = req.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})

# 登录
r = session.get('http://172.18.36.5:8000/', timeout=10)
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
session.post(login_url, data={
    '_58_redirect': '', '_58_rememberMe': 'false',
    '_58_login': 'zhaokw', '_58_password': '`123qwer',
}, timeout=15, allow_redirects=True)
print("登录完成")

# 下载 schema.def
r = session.get('http://172.18.36.5:8000/html/client/schema.def', timeout=30)
schema_raw = r.content
print(f"schema.def 原始大小: {len(schema_raw)} bytes")

# DES 解密
KEY = md5(b'hzytkjyxgs').digest()[:8]
cipher = DES.new(KEY, DES.MODE_ECB)
padded_len = (len(schema_raw) // 8) * 8
schema_dec = cipher.decrypt(schema_raw[:padded_len]) + schema_raw[padded_len:]
print(f"解密后大小: {len(schema_dec)} bytes")
print(f"解密头: {schema_dec[:4]}")

# 检查是否是 ZIP
if schema_dec[:2] == b'PK':
    print("=> ZIP 文件确认!")
    # 保存 ZIP 文件
    zip_path = 'd:/topo_system/backend/schema.zip'
    with open(zip_path, 'wb') as f:
        f.write(schema_dec)
    print(f"已保存到 {zip_path}")

    # 打开 ZIP 并列出文件
    z = zipfile.ZipFile(zip_path, 'r')
    file_list = z.namelist()
    print(f"\nZIP 文件列表 ({len(file_list)} 个):")
    for name in file_list:
        info = z.getinfo(name)
        print(f"  {name} ({info.file_size} bytes)")

    # 提取所有 XML 文件
    print("\n\n=== 提取 dataModel.xml 文件 ===")
    for name in file_list:
        if 'dataModel.xml' in name and not name.endswith('/'):
            try:
                content = z.read(name).decode('utf-8', errors='replace')
                print(f"\n--- {name} ---")
                print(content[:3000])
            except Exception as e:
                print(f"\n--- {name} (错误: {e}) ---")

    # 提取 dataManageUI XML
    print("\n\n=== 提取 dataManageUI.xml 文件 ===")
    for name in file_list:
        if 'dataManageUI' in name and not name.endswith('/'):
            try:
                content = z.read(name).decode('utf-8', errors='replace')
                print(f"\n--- {name} ---")
                print(content[:3000])
            except Exception as e:
                print(f"\n--- {name} (错误: {e}) ---")

    # 提取 layout.xml
    print("\n\n=== 提取 layout.xml ===")
    for name in file_list:
        if name == 'layout.xml':
            content = z.read(name).decode('utf-8', errors='replace')
            print(f"--- {name} ---")
            print(content[:5000])

    # 提取 .dot 文件 (layout definitions)
    print("\n\n=== 提取 .dot 文件 (前几个) ===")
    dot_files = [f for f in file_list if f.endswith('.dot') and 'zh_CN' in f][:3]
    for name in dot_files:
        try:
            content = z.read(name).decode('utf-8', errors='replace')
            print(f"\n--- {name} ---")
            print(content[:2000])
        except Exception as e:
            print(f"\n--- {name} (错误: {e}) ---")

    z.close()

# 同时从 draco_module.swf 解密数据中搜索方法名
print("\n\n=== 从 draco_module.swf 解密数据中搜索方法名 ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf', timeout=60)
mod_raw = r.content
cipher2 = DES.new(KEY, DES.MODE_ECB)
padded_len2 = (len(mod_raw) // 8) * 8
mod_dec = cipher2.decrypt(mod_raw[:padded_len2]) + mod_raw[padded_len2:]

all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', mod_dec)]
print(f"总字符串数: {len(all_strs)}")

# 搜索 service 相关字符串
service_strs = sorted(set(s for s in all_strs if 'service' in s.lower() or 'Service' in s))
print(f"\n=== Service 相关 ({len(service_strs)}) ===")
for s in service_strs:
    if len(s) < 100:
        print(f"  {s}")

# 搜索 RemoteObject 调用
remote_strs = sorted(set(s for s in all_strs if 'Remote' in s or 'remote' in s.lower()))
print(f"\n=== Remote 相关 ({len(remote_strs)}) ===")
for s in remote_strs:
    if len(s) < 100:
        print(f"  {s}")

# 搜索 get/find/load 方法名
method_strs = sorted(set(s for s in all_strs if re.match(r'^[a-z][a-zA-Z]{4,50}$', s) and
                         any(kw in s.lower() for kw in ['get', 'find', 'load', 'query', 'search',
                                                         'fetch', 'count', 'list', 'all'])))
print(f"\n=== 方法名候选 ({len(method_strs)}) ===")
for s in method_strs[:100]:
    print(f"  {s}")

# 搜索 destination 相关
dest_strs = sorted(set(s for s in all_strs if 'destination' in s.lower() or 'Destination' in s))
print(f"\n=== Destination 相关 ({len(dest_strs)}) ===")
for s in dest_strs:
    if len(s) < 100:
        print(f"  {s}")

# 搜索 messagebroker/amf 相关
amf_strs = sorted(set(s for s in all_strs if 'amf' in s.lower() or 'messagebroker' in s.lower() or 'channel' in s.lower()))
print(f"\n=== AMF 相关 ({len(amf_strs)}) ===")
for s in amf_strs:
    if len(s) < 100:
        print(f"  {s}")

# 搜索 com.loader 相关
loader_strs = sorted(set(s for s in all_strs if 'com.loader' in s or 'com.draco' in s))
print(f"\n=== com.loader/draco 相关 ({len(loader_strs)}) ===")
for s in loader_strs[:50]:
    print(f"  {s}")
