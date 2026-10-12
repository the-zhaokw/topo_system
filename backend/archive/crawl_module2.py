"""分析 draco_module.swf 文件格式 + 用 PyAMF 尝试 AMF 调用"""
import requests as req
import re
import zlib
import struct

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

# 2. 重新下载并分析模块文件头
print("\n=== 2. 分析模块文件格式 ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf', timeout=60)
module_data = r.content
print(f"Size: {len(module_data)} bytes")
print(f"Content-Type: {r.headers.get('content-type', 'N/A')}")
print(f"First 32 bytes hex: {module_data[:32].hex()}")
print(f"First 32 bytes: {module_data[:32]}")

# 检查是否是 CWS 但前3字节被替换
# 标准 CWS: 43 57 53 XX XX (version) XX XX XX XX (file size)  then zlib data
# 我们的数据: 6a 9d 2a ...
# 如果把前3字节替换为 CWS:
test = b'CWS' + module_data[3:]
print(f"\n替换前3字节为 CWS 后的前 16 bytes: {test[:16].hex()}")
# 尝试解压
try:
    decompressed = test[:8] + zlib.decompress(test[8:])
    print(f"✅ CWS 替换后解压成功! Size: {len(decompressed)} bytes")
    all_strings = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]
    print(f"字符串数: {len(all_strings)}")

    # 查找关键信息
    # com.loader 类
    loader_classes = [s for s in all_strings if 'com.loader' in s]
    print(f"\ncom.loader 类 ({len(loader_classes)}):")
    for s in sorted(set(loader_classes))[:50]:
        print(f"  {s}")

    # 查找 destination 名称
    # 在 BlazeDS 中, destination 通常在 RemoteObject 声明中
    remote_patterns = [s for s in all_strings if any(kw in s.lower() for kw in ['destination', 'remoteobject', 'source', 'endpoint'])]
    print(f"\nRemote 相关 ({len(remote_patterns)}):")
    for s in sorted(set(remote_patterns))[:30]:
        print(f"  {s}")

    # 查找方法名
    methods = set()
    for s in all_strings:
        if re.match(r'^[a-z][a-zA-Z0-9]{4,50}$', s):
            sl = s.lower()
            if any(kw in sl for kw in ['gettest', 'findtest', 'getproject', 'findproject', 'getplan', 'findplan',
                                         'getcase', 'findcase', 'getdefect', 'finddefect', 'getbug', 'findbug',
                                         'getmodule', 'findmodule', 'getrequirement', 'findrequirement',
                                         'getrun', 'findrun', 'getscenario', 'findscenario',
                                         'getenvironment', 'findenvironment', 'getbuild', 'findbuild',
                                         'getall', 'findall', 'getlist', 'findlist',
                                         'createtest', 'createproject', 'createplan', 'createcase',
                                         'createdefect', 'updatetest', 'updateproject', 'updateplan',
                                         'savetest', 'saveproject', 'deletetest', 'deleteproject',
                                         'loadtest', 'loadproject', 'loadplan', 'loadmodule',
                                         'querytest', 'queryproject', 'searchtest', 'searchproject',
                                         'getuser', 'finduser', 'gettask', 'findtask',
                                         'getexecution', 'findexecution', 'getresult', 'findresult']):
                methods.add(s)

    print(f"\n业务方法名 ({len(methods)}):")
    for s in sorted(methods):
        print(f"  {s}")

    # 查找所有 URL/端点
    url_strings = [s for s in all_strings if s.startswith('http://') or s.startswith('https://') or s.startswith('/')]
    url_strings = [s for s in url_strings if len(s) > 5 and len(s) < 200 and not s.startswith('//')]
    print(f"\nURL/路径 ({len(url_strings)}):")
    for s in sorted(set(url_strings))[:40]:
        print(f"  {s}")

    # 查找 transmitfile
    transmit = [s for s in all_strings if 'transmit' in s.lower()]
    print(f"\ntransmitfile 相关:")
    for s in sorted(set(transmit)):
        print(f"  {s}")

    # 查找 .do .action 端点
    do_endpoints = set()
    for s in all_strings:
        if ('.do' in s or '.action' in s or '.jsp' in s) and len(s) < 200:
            do_endpoints.add(s)
    print(f"\n.do/.action/.jsp 端点 ({len(do_endpoints)}):")
    for s in sorted(do_endpoints):
        print(f"  {s}")

    # 查找 BlazeDS destination 名称
    # 通常是在 services-config.xml 中定义的
    # 但也可以在 AS3 代码中硬编码
    # 查找看起来像 destination 名的字符串（短小、驼峰命名）
    possible_destinations = set()
    for s in all_strings:
        if re.match(r'^[a-z][a-zA-Z]+Service$', s) or re.match(r'^[a-z][a-zA-Z]+Service\b', s):
            possible_destinations.add(s)
        if 'Service' in s and len(s) < 50 and not '.' in s and not ' ' in s:
            possible_destinations.add(s)

    print(f"\n可能的 Destination 名 ({len(possible_destinations)}):")
    for s in sorted(possible_destinations):
        print(f"  {s}")

except Exception as e:
    print(f"CWS 替换解压失败: {e}")

    # 尝试 FWS 替换
    test2 = b'FWS' + module_data[3:]
    print(f"\n尝试 FWS: 前 16 bytes: {test2[:16].hex()}")

    # 尝试直接 ZLIB 解压（跳过前8字节）
    try:
        decompressed2 = zlib.decompress(module_data[8:])
        print(f"✅ 直接 ZLIB 解压成功! Size: {len(decompressed2)} bytes")
    except Exception as e2:
        print(f"直接 ZLIB 解压失败: {e2}")

    # 尝试跳过不同长度的头部
    for skip in [0, 3, 4, 5, 6, 7, 8, 10, 12, 16]:
        try:
            d = zlib.decompress(module_data[skip:])
            print(f"✅ 跳过 {skip} 字节后 ZLIB 解压成功! Size: {len(d)} bytes")
            break
        except:
            pass

    # 检查是否是 LZMA
    try:
        import lzma
        d = lzma.decompress(module_data)
        print(f"✅ LZMA 解压成功! Size: {len(d)} bytes")
    except:
        pass

    # 检查是否是 GZIP
    try:
        import gzip
        d = gzip.decompress(module_data)
        print(f"✅ GZIP 解压成功! Size: {len(d)} bytes")
    except:
        pass

# 3. 检查 transmitfile 端点
print("\n=== 3. transmitfile 端点 ===")
for cmd in ['download', 'upload', 'delete', 'list', 'export']:
    try:
        r = session.get(f'http://172.18.36.5:8000/transmitfile?cmd={cmd}', timeout=5)
        ct = r.headers.get('content-type', '')
        print(f"  cmd={cmd} -> {r.status_code} (type={ct[:30]}, len={len(r.content)})")
        if r.status_code == 200 and len(r.text) < 500:
            print(f"    Body: {r.text[:300]}")
    except Exception as e:
        print(f"  cmd={cmd} -> Error: {str(e)[:60]}")

# 也尝试 POST
for cmd in ['download', 'list', 'export']:
    try:
        r = session.post(f'http://172.18.36.5:8000/transmitfile?cmd={cmd}', data={}, timeout=5)
        ct = r.headers.get('content-type', '')
        print(f"  POST cmd={cmd} -> {r.status_code} (type={ct[:30]}, len={len(r.content)})")
    except Exception as e:
        print(f"  POST cmd={cmd} -> Error: {str(e)[:60]}")

# 4. 尝试 Liferay 的 JSON 服务
print("\n=== 4. Liferay JSON 服务 ===")
# Liferay 5/6 的 JSON 服务入口
json_paths = [
    '/c/portal/json?__callback=jsonpCallback&serviceClassName=com.liferay.portal.service.UserLocalServiceUtil&serviceMethodName=getUserIdByScreenName&serviceParameters=[screenName]',
    '/tunnel/secure/json?serviceClassName=com.liferay.portal.service.UserLocalServiceUtil&serviceMethodName=getUserIdByScreenName&serviceParameters=[screenName]&screenName=zhaokw',
]
for path in json_paths:
    try:
        r = session.get(f'http://172.18.36.5:8000{path}', timeout=5)
        print(f"  {path[:80]}... -> {r.status_code} (len={len(r.text)})")
        if r.status_code == 200:
            print(f"    Body: {r.text[:300]}")
    except Exception as e:
        print(f"  Error: {str(e)[:60]}")
