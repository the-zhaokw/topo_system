"""获取 BlazeDS 配置 + 深入分析 SWF 中的服务调用"""
import requests
import re
import zlib
import json

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

# 1. 登录
print("=== 1. 登录 ===")
r = s.get('http://172.18.36.5:8000/', timeout=10)
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
r2 = s.post(login_url, data={
    '_58_redirect': '', '_58_rememberMe': 'false',
    '_58_login': 'zhaokw', '_58_password': '`123qwer',
}, timeout=15, allow_redirects=True)
print(f"登录: {r2.status_code}, URL: {r2.url}")

# 2. 获取 cache-config.xml
print("\n=== 2. cache-config.xml ===")
r = s.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/cache-config.xml', timeout=10)
print(f"Status: {r.status_code}, Length: {len(r.text)}")
if r.status_code == 200:
    print(r.text[:3000])

# 3. 获取 BlazeDS 配置文件
print("\n=== 3. BlazeDS 配置 ===")
config_paths = [
    '/WEB-INF/flex/services-config.xml',
    '/WEB-INF/flex/remoting-config.xml',
    '/WEB-INF/flex/messaging-config.xml',
    '/WEB-INF/flex/proxy-config.xml',
    '/WEB-INF/flex/data-management-config.xml',
    '/html/portlet/ext/draco/WEB-INF/flex/services-config.xml',
    '/html/portlet/ext/draco/WEB-INF/flex/remoting-config.xml',
    '/html/WEB-INF/flex/services-config.xml',
    '/WEB-INF/services-config.xml',
    '/WEB-INF/remoting-config.xml',
]
for path in config_paths:
    try:
        r = s.get(f'http://172.18.36.5:8000{path}', timeout=5)
        if r.status_code == 200 and len(r.text) > 50:
            print(f"  ✅ {path} -> {r.status_code} (len={len(r.text)})")
            print(f"    {r.text[:500]}")
    except:
        pass

# 4. messagebroker/http 响应
print("\n=== 4. messagebroker/http 响应 ===")
r = s.post('http://172.18.36.5:8000/messagebroker/http',
    data=b'',
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    timeout=10)
print(f"Status: {r.status_code}")
print(f"Headers: {dict(r.headers)}")
print(f"Body: {r.text[:500]}")

# 5. 深入分析 SWF - 查找服务相关字符串
print("\n=== 5. SWF 深度分析 ===")
r = s.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', timeout=30)
swf_data = r.content
decompressed = swf_data[:8] + zlib.decompress(swf_data[8:])
all_strings = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]

# 查找 com.loader 相关的所有类名
loader_strings = [s for s in all_strings if 'com.loader' in s.lower() or 'draco' in s.lower()]
print(f"com.loader 相关 ({len(loader_strings)}):")
for s in sorted(set(loader_strings))[:40]:
    print(f"  {s}")

# 查找可能的方法名（驼峰命名）
method_pattern = re.compile(r'^[a-z][a-zA-Z0-9]{3,30}$')
method_strings = [s for s in all_strings if method_pattern.match(s) and any(kw in s.lower() for kw in ['get', 'set', 'find', 'list', 'create', 'update', 'delete', 'save', 'load', 'fetch', 'query', 'search', 'count', 'add', 'remove'])]
print(f"\n方法名字符串 ({len(method_strings)}):")
for s in sorted(set(method_strings))[:50]:
    print(f"  {s}")

# 查找 transmitfile 和其他端点
endpoint_strings = [s for s in all_strings if 'transmit' in s.lower() or 'messagebroker' in s.lower() or 'destination' in s.lower() or 'channel' in s.lower()]
print(f"\n端点字符串 ({len(endpoint_strings)}):")
for s in sorted(set(endpoint_strings)):
    print(f"  {s}")

# 查找 XML 配置
xml_strings = [s for s in all_strings if s.startswith('<') or 'xmlns' in s or 'xml version' in s]
print(f"\nXML 字符串 ({len(xml_strings)}):")
for s in sorted(set(xml_strings))[:20]:
    print(f"  {s[:200]}")

# 查找所有包含 _destination 或 _channel 的变量
var_strings = [s for s in all_strings if '_destination' in s or '_channel' in s or 'destination' in s.lower() and len(s) < 50]
print(f"\nDestination/Channel 变量 ({len(var_strings)}):")
for s in sorted(set(var_strings))[:30]:
    print(f"  {s}")

# 6. 尝试 transmitfile 端点
print("\n=== 6. transmitfile 端点测试 ===")
transmit_paths = [
    '/transmitfile?cmd=download',
    '/transmitfile?cmd=upload',
    '/transmitfile?cmd=delete',
    '/html/portlet/ext/draco/transmitfile?cmd=download',
    '/transmitfile',
]
for path in transmit_paths:
    try:
        r = s.get(f'http://172.18.36.5:8000{path}', timeout=5)
        ct = r.headers.get('content-type', '')
        print(f"  GET {path} -> {r.status_code} (type={ct[:30]}, len={len(r.content)})")
        if r.status_code == 200 and len(r.text) < 500:
            print(f"    Body: {r.text[:300]}")
    except Exception as e:
        print(f"  {path} -> Error: {str(e)[:60]}")

# 7. 查找 SWF 中加载的其他 SWF 模块
print("\n=== 7. SWF 模块引用 ===")
swf_refs = [s for s in all_strings if '.swf' in s.lower()]
print(f"SWF 引用 ({len(swf_refs)}):")
for s in sorted(set(swf_refs)):
    print(f"  {s}")

# 查找模块路径
module_strings = [s for s in all_strings if 'module' in s.lower() and len(s) < 100]
print(f"\n模块引用 ({len(module_strings)}):")
for s in sorted(set(module_strings))[:20]:
    print(f"  {s}")

# 8. 尝试通过 AMF 发送简单的 ping 请求
print("\n=== 8. AMF ping 测试 ===")
# 构建一个简单的 AMF0 请求
# AMF0 format: 0x00 (version) + 0x00 0x00 (headers count) + 0x00 0x01 (bodies count)
# Body: target string + response string + value
def build_amf_string(s):
    """AMF0 长字符串"""
    s_bytes = s.encode('utf-8')
    return len(s_bytes).to_bytes(4, 'big') + s_bytes  # actually AMF0 uses 2-byte for short strings

# 尝试 AMF3
amf_data = b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'
r = s.post('http://172.18.36.5:8000/messagebroker/amf',
    data=amf_data,
    headers={'Content-Type': 'application/x-amf'},
    timeout=10)
print(f"AMF response status: {r.status_code}")
print(f"AMF response length: {len(r.content)}")
print(f"AMF response headers: {dict(r.headers)}")
if r.content:
    print(f"AMF response hex: {r.content[:100].hex()}")
    # 尝试解析 AMF 响应
    resp_strs = re.findall(rb'[\x20-\x7e]{4,}', r.content)
    if resp_strs:
        print(f"AMF response strings: {[s.decode('ascii', errors='ignore') for s in resp_strs[:20]]}")
