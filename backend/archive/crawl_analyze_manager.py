"""下载并分析 draco_manager.swf - 这是主应用 SWF"""
import requests as req
import re
import zlib
import struct
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

# === 1. 下载 draco_manager.swf ===
print("\n=== 1. 下载 draco_manager.swf ===")
url = 'http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf'
r = session.get(url, timeout=60)
raw = r.content
print(f"原始大小: {len(raw)} bytes")
print(f"前16字节: {raw[:16].hex()}")

# 检查是否是标准 SWF (FWS 或 CWS)
if raw[:3] in [b'FWS', b'CWS', b'ZWS']:
    print("=> 标准 SWF 文件!")
    # 如果是 CWS (压缩), 解压
    if raw[:3] == b'CWS':
        print("  CWS 压缩格式, 解压中...")
        try:
            decompressed = zlib.decompress(raw[8:])
            print(f"  解压后: {len(decompressed)} bytes")
            swf_data = decompressed
        except:
            swf_data = raw[8:]
            print(f"  解压失败, 使用原始数据")
    elif raw[:3] == b'ZWS':
        print("  ZWS 格式")
        swf_data = raw
    else:
        swf_data = raw
        print("  FWS 未压缩格式")

    # 提取所有可读字符串
    all_strs = [s.decode('ascii', errors='ignore')
                for s in re.findall(rb'[\x20-\x7e]{4,}', swf_data)]
    print(f"\n  总字符串数: {len(all_strs)}")

    # 搜索 Service 相关
    svc_strs = sorted(set(s for s in all_strs if 'Service' in s and len(s) < 100))
    print(f"\n=== Service 相关 ({len(svc_strs)}) ===")
    for s in svc_strs:
        print(f"  {s}")

    # 搜索 destination 相关
    dest_strs = sorted(set(s for s in all_strs if 'destination' in s.lower() and len(s) < 100))
    print(f"\n=== Destination 相关 ({len(dest_strs)}) ===")
    for s in dest_strs:
        print(f"  {s}")

    # 搜索 RemoteObject / channel 相关
    remote_strs = sorted(set(s for s in all_strs
                           if ('Remote' in s or 'remote' in s.lower() or
                               'Channel' in s or 'channel' in s.lower() or
                               'messagebroker' in s.lower() or 'amf' in s.lower())
                           and len(s) < 100))
    print(f"\n=== Remote/Channel/AMF 相关 ({len(remote_strs)}) ===")
    for s in remote_strs:
        print(f"  {s}")

    # 搜索 get/find/load/query 方法名
    method_strs = sorted(set(s for s in all_strs
                            if re.match(r'^[a-z][a-zA-Z]{4,60}$', s) and
                            any(kw in s.lower() for kw in
                                ['get', 'find', 'load', 'query', 'search',
                                 'count', 'list', 'fetch', 'retrieve', 'create',
                                 'update', 'delete', 'save', 'execute'])))
    print(f"\n=== 方法名候选 ({len(method_strs)}) ===")
    for s in method_strs:
        print(f"  {s}")

    # 搜索 bug/project/org 相关字符串
    domain_strs = sorted(set(s for s in all_strs
                            if any(kw in s.lower() for kw in
                                ['bug', 'project', 'org', 'rtn', 'ipran', 'task',
                                 'requirement', 'version', 'build', 'release',
                                 'risk', 'issue', 'test', 'phase', 'baseline'])))
    print(f"\n=== 领域相关 ({len(domain_strs)}) ===")
    for s in domain_strs[:50]:
        print(f"  {s}")

    # 搜索 com.cloudtopo 相关
    pkg_strs = sorted(set(s for s in all_strs if 'com.cloudtopo' in s or 'cloudtopo' in s))
    print(f"\n=== 包路径 ({len(pkg_strs)}) ===")
    for s in pkg_strs[:30]:
        print(f"  {s}")

else:
    # 可能是加密的
    print("=> 不是标准 SWF, 可能加密")
    print(f"  前8字节: {raw[:8].hex()}")

    # 尝试 DES 解密
    KEY = md5(b'hzytkjyxgs').digest()[:8]
    cipher = DES.new(KEY, DES.MODE_ECB)
    padded_len = (len(raw) // 8) * 8
    decrypted = cipher.decrypt(raw[:padded_len]) + raw[padded_len:]
    print(f"  DES解密后前16字节: {decrypted[:16].hex()}")

    if decrypted[:3] in [b'FWS', b'CWS', b'ZWS']:
        print("  => 解密后是标准 SWF!")
        if decrypted[:3] == b'CWS':
            try:
                swf_data = zlib.decompress(decrypted[8:])
                print(f"  解压后: {len(swf_data)} bytes")
            except:
                swf_data = decrypted[8:]
        else:
            swf_data = decrypted

        all_strs = [s.decode('ascii', errors='ignore')
                    for s in re.findall(rb'[\x20-\x7e]{4,}', swf_data)]
        print(f"  总字符串数: {len(all_strs)}")

        svc_strs = sorted(set(s for s in all_strs if 'Service' in s and len(s) < 100))
        print(f"\n=== Service 相关 ({len(svc_strs)}) ===")
        for s in svc_strs:
            print(f"  {s}")

        dest_strs = sorted(set(s for s in all_strs if 'destination' in s.lower() and len(s) < 100))
        print(f"\n=== Destination 相关 ({len(dest_strs)}) ===")
        for s in dest_strs:
            print(f"  {s}")

        remote_strs = sorted(set(s for s in all_strs
                               if ('Remote' in s or 'channel' in s.lower() or
                                   'messagebroker' in s.lower() or 'amf' in s.lower())
                               and len(s) < 100))
        print(f"\n=== Remote/AMF 相关 ({len(remote_strs)}) ===")
        for s in remote_strs:
            print(f"  {s}")

        method_strs = sorted(set(s for s in all_strs
                                if re.match(r'^[a-z][a-zA-Z]{4,60}$', s) and
                                any(kw in s.lower() for kw in
                                    ['get', 'find', 'load', 'query', 'search',
                                     'count', 'list', 'fetch', 'create',
                                     'update', 'delete', 'save', 'execute'])))
        print(f"\n=== 方法名候选 ({len(method_strs)}) ===")
        for s in method_strs:
            print(f"  {s}")

        domain_strs = sorted(set(s for s in all_strs
                                if any(kw in s.lower() for kw in
                                    ['bug', 'project', 'org', 'rtn', 'ipran', 'task'])))
        print(f"\n=== 领域相关 ({len(domain_strs)}) ===")
        for s in domain_strs[:50]:
            print(f"  {s}")

        pkg_strs = sorted(set(s for s in all_strs if 'com.cloudtopo' in s or 'cloudtopo' in s))
        print(f"\n=== 包路径 ({len(pkg_strs)}) ===")
        for s in pkg_strs[:30]:
            print(f"  {s}")

# === 2. 也下载 resources 目录下的其他文件 ===
print("\n\n=== 2. 检查 resources 目录 ===")
resource_files = [
    '/html/portlet/ext/draco/resources/draco_manager.swf',
    '/html/portlet/ext/draco/resources/crossdomain.xml',
    '/html/portlet/ext/draco/resources/services-config.xml',
    '/html/portlet/ext/draco/resources/remoting-config.xml',
    '/html/portlet/ext/draco/resources/config.xml',
    '/html/portlet/ext/draco/resources/channel-config.xml',
    '/html/portlet/ext/draco/resources/framework.swc',
    '/html/portlet/ext/draco/resources/rpclibs.swc',
    '/html/portlet/ext/draco/resources/draco_framework.swf',
    '/html/portlet/ext/draco/resources/draco_lib.swf',
    '/html/portlet/ext/draco/resources/draco_drmng.swf',
    '/html/portlet/ext/draco/resources/draco_user.swf',
    '/html/portlet/ext/draco/resources/draco_project.swf',
    '/html/portlet/ext/draco/resources/draco_bug.swf',
    '/html/portlet/ext/draco/resources/draco_devMng.swf',
]

for f in resource_files:
    try:
        resp = session.get(f'http://172.18.36.5:8000{f}', timeout=10)
        if resp.status_code == 200:
            print(f"  OK {f}: {len(resp.content)} bytes ({resp.headers.get('content-type', '')})")
    except:
        pass
