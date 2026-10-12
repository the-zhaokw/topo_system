"""下载 draco_module.swf 和 schema.def，分析服务调用"""
import requests as req
import re
import zlib

session = req.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
})

# 1. 登录
print("=== 1. 登录 ===")
r = session.get('http://172.18.36.5:8000/', timeout=10)
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
r2 = session.post(login_url, data={
    '_58_redirect': '', '_58_rememberMe': 'false',
    '_58_login': 'zhaokw', '_58_password': '`123qwer',
}, timeout=15, allow_redirects=True)
print(f"登录: {r2.status_code}, URL: {r2.url}")

# 2. 下载 draco_module.swf
print("\n=== 2. 下载 draco_module.swf ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf', timeout=60)
module_data = r.content
print(f"Status: {r.status_code}, Size: {len(module_data)} bytes")

# 解压
if module_data[:3] == b'CWS':
    decompressed = module_data[:8] + zlib.decompress(module_data[8:])
    print(f"解压后: {len(decompressed)} bytes")
elif module_data[:3] == b'FWS':
    decompressed = module_data
    print(f"未压缩: {len(decompressed)} bytes")
else:
    print(f"格式: {module_data[:3]}")
    decompressed = module_data

# 提取所有字符串
all_strings = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]
print(f"字符串总数: {len(all_strings)}")

# 3. 查找 AMF destination 和方法名
print("\n=== 3. AMF 服务分析 ===")

# 查找 RemoteObject 相关
remote_strings = [s for s in all_strings if any(kw in s.lower() for kw in ['remoteobject', 'remote_object', 'destination', 'source', 'endpoint'])]
print(f"RemoteObject 相关 ({len(remote_strings)}):")
for s in sorted(set(remote_strings))[:30]:
    print(f"  {s}")

# 查找 com.loader 中的服务类
service_classes = [s for s in all_strings if 'com.loader' in s and ('service' in s.lower() or 'remote' in s.lower() or 'delegate' in s.lower() or 'proxy' in s.lower() or 'facade' in s.lower() or 'model' in s.lower() or 'controller' in s.lower())]
print(f"\n服务类 ({len(service_classes)}):")
for s in sorted(set(service_classes))[:40]:
    print(f"  {s}")

# 查找所有 com.loader 类
all_loader = [s for s in all_strings if 'com.loader' in s]
print(f"\n所有 com.loader 类 ({len(all_loader)}):")
for s in sorted(set(all_loader)):
    print(f"  {s}")

# 4. 查找方法名（含 get/find/list/create/update/delete/save/load 等动词）
method_names = set()
for s in all_strings:
    if re.match(r'^[a-z][a-zA-Z0-9]{4,40}$', s):
        s_lower = s.lower()
        if any(kw in s_lower for kw in ['getall', 'findall', 'getlist', 'findlist', 'gettest', 'findtest', 'getproject', 'findproject', 'getplan', 'findplan', 'getcase', 'findcase', 'getbug', 'findbug', 'getdefect', 'createdefect', 'savetest', 'loadtest']):
            method_names.add(s)

print(f"\n业务方法名 ({len(method_names)}):")
for s in sorted(method_names):
    print(f"  {s}")

# 5. 更广泛的方法名搜索
biz_methods = set()
for s in all_strings:
    if re.match(r'^[a-z][a-zA-Z0-9]{5,50}$', s):
        s_lower = s.lower()
        if any(kw in s_lower for kw in ['testcase', 'testplan', 'testrun', 'defect', 'project', 'module', 'requirement', 'scenario', 'environment', 'build']):
            biz_methods.add(s)

print(f"\n业务方法名（宽搜索）({len(biz_methods)}):")
for s in sorted(biz_methods):
    print(f"  {s}")

# 6. 查找 HTTPService / WebService URL
print("\n=== 6. HTTP/Web Service URL ===")
http_urls = [s for s in all_strings if s.startswith('http://') or s.startswith('https://')]
print(f"HTTP URL ({len(http_urls)}):")
for s in sorted(set(http_urls))[:20]:
    print(f"  {s}")

# 查找 .do 或 .action 或 .jsp 端点
endpoints = set()
for s in all_strings:
    if any(ext in s for ext in ['.do', '.action', '.jsp']) and len(s) < 200:
        endpoints.add(s)
    if '/transmitfile' in s:
        endpoints.add(s)
    if '/messagebroker' in s:
        endpoints.add(s)

print(f"\n端点 ({len(endpoints)}):")
for s in sorted(endpoints):
    print(f"  {s}")

# 7. 下载 schema.def
print("\n=== 7. 下载 schema.def ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/schema.def', timeout=30)
print(f"Status: {r.status_code}, Size: {len(r.content)} bytes")
if r.status_code == 200:
    # 尝试解析
    content = r.content
    if content[:3] == b'CWS':
        schema_decompressed = content[:8] + zlib.decompress(content[8:])
        print(f"Schema 是 SWF 格式，解压后: {len(schema_decompressed)} bytes")
    elif content[:2] == b'\x1f\x8b':
        import gzip
        schema_decompressed = gzip.decompress(content)
        print(f"Schema 是 GZIP 格式，解压后: {len(schema_decompressed)} bytes")
    else:
        schema_decompressed = content
        print(f"Schema 原始格式，前 50 字节: {content[:50].hex()}")

    # 提取 schema 中的字符串
    schema_strings = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', schema_decompressed)]
    print(f"Schema 字符串数: {len(schema_strings)}")
    # 打印前 100 个字符串
    for s in schema_strings[:100]:
        print(f"  {s[:200]}")

# 8. 测试 AMF 端点
print("\n=== 8. AMF 端点测试 ===")
# 发送空 AMF3 请求
r = session.post('http://172.18.36.5:8000/messagebroker/amf',
    data=b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x04null\x00\x00\x00\x00',
    headers={'Content-Type': 'application/x-amf'},
    timeout=10)
print(f"AMF ping: {r.status_code}, len={len(r.content)}")
if r.content:
    print(f"Hex: {r.content[:200].hex()}")
    resp_strings = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', r.content)]
    print(f"Response strings: {resp_strings[:10]}")
