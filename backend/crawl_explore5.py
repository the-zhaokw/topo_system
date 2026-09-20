"""登录成功后探测后端 API + 解压 SWF 提取字符串"""
import requests
import re
import zlib
import json

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

# 1. 登录
print("=== 1. 登录 ===")
r = s.get('http://172.18.36.5:8000/', timeout=10)
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
r2 = s.post(login_url, data={
    '_58_redirect': '',
    '_58_rememberMe': 'false',
    '_58_login': 'zhaokw',
    '_58_password': '`123qwer',
}, timeout=15, allow_redirects=True)
print(f"登录状态: {r2.status_code}, URL: {r2.url}")
if 'topo' in r2.url.lower():
    print("✅ 登录成功！已重定向到 Topo 页面")
else:
    print(f"登录后页面: {r2.url}")

# 2. 探测 AMF/BlazeDS 端点
print("\n=== 2. 探测 AMF/BlazeDS 端点 ===")
amf_paths = [
    '/messagebroker/amf',
    '/messagebroker/amfsecure',
    '/messagebroker/http',
    '/messagebroker/polling',
    '/html/messagebroker/amf',
    '/html/portlet/ext/draco/messagebroker/amf',
    '/draco/messagebroker/amf',
    '/lc/messagebroker/amf',
    '/flex2/messagebroker/amf',
    '/blazeds/messagebroker/amf',
    '/spring/messagebroker/amf',
    '/gateway',
    '/amf gateway',
    '/html/portlet/ext/draco/gateway',
]
for path in amf_paths:
    try:
        r = s.post(f'http://172.18.36.5:8000{path}',
            data=b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00',
            headers={'Content-Type': 'application/x-amf'},
            timeout=5)
        ct = r.headers.get('content-type', '')
        print(f"  {path} -> {r.status_code} (type={ct[:30]}, len={len(r.content)})")
        if r.status_code == 200 and 'amf' in ct.lower():
            print(f"    ✅ AMF 端点找到！")
    except Exception as e:
        print(f"  {path} -> Error: {str(e)[:60]}")

# 3. 探测 Liferay 服务端点
print("\n=== 3. Liferay 服务端点 ===")
service_paths = [
    '/c/portal/json',
    '/c/portal/jsonp',
    '/c/json',
    '/api/secure/json',
    '/api/jsonws',
    '/api/jsonws/invoke',
    '/tunnel/json',
    '/tunnel/secure/json',
    '/c/portal/layout',
    '/c/portal/session',
    '/c/portal/user',
    '/html/portlet/ext/draco/spring/json',
    '/html/portlet/ext/draco/dwr/json',
    '/html/portlet/ext/draco/ajax',
]
for path in service_paths:
    try:
        r = s.get(f'http://172.18.36.5:8000{path}', timeout=5)
        ct = r.headers.get('content-type', '')
        info = f"{r.status_code} (type={ct[:30]}, len={len(r.text)})"
        if r.status_code == 200 and 'json' in ct.lower():
            try:
                data = r.json()
                info += f" JSON keys: {list(data.keys())[:5] if isinstance(data, dict) else type(data)}"
            except:
                info += f" Body[:200]: {r.text[:200]}"
        elif r.status_code == 200 and len(r.text) < 200:
            info += f" Body: {r.text[:200]}"
        print(f"  {path} -> {info}")
    except Exception as e:
        print(f"  {path} -> Error: {str(e)[:60]}")

# 4. 下载并解压 SWF
print("\n=== 4. 下载并解压 SWF ===")
r = s.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', timeout=30)
swf_data = r.content
print(f"SWF size: {len(swf_data)} bytes")

# 检查 SWF 头
if swf_data[:3] == b'FWS':
    print("SWF 格式: 未压缩 (FWS)")
    decompressed = swf_data
elif swf_data[:3] == b'CWS':
    print("SWF 格式: ZLIB 压缩 (CWS)")
    # 解压（跳过前 8 字节头部）
    try:
        decompressed = swf_data[:8] + zlib.decompress(swf_data[8:])
        print(f"解压后大小: {len(decompressed)} bytes")
    except Exception as e:
        print(f"解压失败: {e}")
        decompressed = swf_data
elif swf_data[:3] == b'ZWS':
    print("SWF 格式: LZMA 压缩 (ZWS)")
    try:
        import lzma
        decompressed = swf_data[:8] + lzma.decompress(swf_data[12:])
        print(f"解压后大小: {len(decompressed)} bytes")
    except Exception as e:
        print(f"解压失败: {e}")
        decompressed = swf_data
else:
    print(f"未知格式: {swf_data[:3]}")
    decompressed = swf_data

# 提取所有字符串
strings = re.findall(rb'[\x20-\x7e]{4,}', decompressed)
all_strings = [s.decode('ascii', errors='ignore') for s in strings]
print(f"提取字符串总数: {len(all_strings)}")

# 分类输出
# URL 路径
url_strings = [s for s in all_strings if '/' in s and len(s) > 5 and len(s) < 200]
print(f"\n路径字符串 ({len(url_strings)}):")
for s in sorted(set(url_strings)):
    if not s.startswith('//') and not s.startswith('/*') and 'http' in s.lower() or s.startswith('/'):
        print(f"  {s}")

# Java 类名
java_strings = [s for s in all_strings if any(kw in s for kw in ['com.', 'org.', 'cn.', 'java.', 'flex.', 'mx.']) and len(s) > 8]
print(f"\nJava 类名字符串 ({len(java_strings)}):")
for s in sorted(set(java_strings))[:30]:
    print(f"  {s}")

# 服务/方法名
service_strings = [s for s in all_strings if any(kw in s for kw in ['Service', 'service', 'Remote', 'remote', 'Destination', 'destination', 'Channel', 'channel', 'Endpoint', 'endpoint'])]
print(f"\n服务相关字符串 ({len(service_strings)}):")
for s in sorted(set(service_strings))[:30]:
    print(f"  {s}")

# AMF/BlazeDS 相关
amf_strings = [s for s in all_strings if any(kw in s.lower() for kw in ['amf', 'blaze', 'message', 'remoting', 'flex', 'gateway'])]
print(f"\nAMF 相关字符串 ({len(amf_strings)}):")
for s in sorted(set(amf_strings))[:30]:
    print(f"  {s}")

# 测试相关
test_strings = [s for s in all_strings if any(kw in s.lower() for kw in ['test', 'case', 'plan', 'project', 'bug', 'defect', 'run', 'suite', 'scenario'])]
print(f"\n测试相关字符串 ({len(test_strings)}):")
for s in sorted(set(test_strings))[:30]:
    print(f"  {s}")

# 5. 探查其他 SWF 文件
print("\n=== 5. 查找其他 SWF 文件 ===")
# 检查 resources 目录下的其他文件
resource_files = ['draco.swf', 'main.swf', 'topo.swf', 'app.swf', 'config.xml',
                  'services-config.xml', 'remoting-config.xml', 'data-management-config.xml',
                  'proxy-config.xml', 'messaging-config.xml']
for f in resource_files:
    try:
        r = s.get(f'http://172.18.36.5:8000/html/portlet/ext/draco/resources/{f}', timeout=5)
        if r.status_code == 200:
            print(f"  ✅ {f} found! Size: {len(r.content)}")
            if f.endswith('.xml'):
                print(f"    Content: {r.text[:500]}")
    except:
        pass

# 检查 SWF 中的资源引用
swf_refs = [s for s in all_strings if s.endswith('.swf') or s.endswith('.xml') or s.endswith('.json')]
print(f"\nSWF 中的资源引用:")
for s in sorted(set(swf_refs)):
    print(f"  {s}")

# 6. 查找 Liferay 6 custom portlet 端点
print("\n=== 6. Liferay 自定义端点 ===")
custom_paths = [
    '/html/portlet/ext/draco/view.jsp',
    '/html/portlet/ext/draco/init.jsp',
    '/html/portlet/ext/draco/action.jsp',
    '/html/portlet/ext/draco/find_test_case.jsp',
    '/html/portlet/ext/draco/test_case.jsp',
    '/html/portlet/ext/draco/resource_serve.jsp',
]
for path in custom_paths:
    try:
        r = s.get(f'http://172.18.36.5:8000{path}', timeout=5)
        print(f"  {path} -> {r.status_code} (len={len(r.text)})")
        if r.status_code == 200 and len(r.text) < 500:
            print(f"    Body: {r.text[:300]}")
    except Exception as e:
        print(f"  {path} -> Error: {str(e)[:60]}")
