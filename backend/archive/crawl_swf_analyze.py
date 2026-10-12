"""下载并分析 SWF 文件，提取 AMF destination 和方法名"""
import requests as req
import re
import struct
import zlib

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

# 1. 下载 draco_manager.swf (主SWF)
print("\n=== 下载 draco_manager.swf ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', timeout=60)
manager_data = r.content
print(f"draco_manager.swf: {len(manager_data)} bytes, header: {manager_data[:8]}")

# 检查是否加密
if manager_data[:3] == b'CWS' or manager_data[:3] == b'FWS':
    print("  标准SWF格式")
    # 解压SWF (CWS = 压缩, FWS = 未压缩)
    if manager_data[:3] == b'CWS':
        try:
            # SWF压缩格式: CWS + version(1byte) + length(4bytes) + zlib compressed data
            swf_version = manager_data[3]
            swf_length = struct.unpack('<I', manager_data[4:8])[0]
            decompressed = zlib.decompress(manager_data[8:])
            full_swf = b'FWS' + manager_data[3:8] + decompressed
            print(f"  解压成功: {len(full_swf)} bytes")
            # 保存解压后的 SWF
            with open('d:/topo_system/backend/draco_manager_decoded.bin', 'wb') as f:
                f.write(full_swf)
            # 提取字符串
            all_strs = [s.decode('utf-8', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', full_swf)]
            print(f"  字符串数: {len(all_strs)}")

            # 找 destination/service 相关
            amf_strs = [s for s in all_strs if any(kw in s.lower() for kw in ['destination', 'amf', 'messagebroker', 'channel', 'endpoint', 'service'])]
            print(f"\n  === AMF相关字符串 ===")
            for s in sorted(set(amf_strs)):
                print(f"    {s}")

            # 找 RemoteObject / 模块加载相关
            remote_strs = [s for s in all_strs if any(kw in s.lower() for kw in ['remote', 'draco', 'module', 'topo'])]
            print(f"\n  === 模块/远程相关 ===")
            for s in sorted(set(remote_strs))[:30]:
                print(f"    {s}")

            # 找所有 URL
            urls = [s for s in all_strs if (s.startswith('http://') or s.startswith('/')) and len(s) > 5 and len(s) < 200]
            print(f"\n  === URL/路径 ===")
            for s in sorted(set(urls))[:30]:
                print(f"    {s}")

            # 找类名和方法名 (AS3格式 com.xxx.yyy)
            as3_classes = [s for s in all_strs if re.match(r'^[a-z]+\.[a-zA-Z]', s) and len(s) < 80]
            print(f"\n  === AS3 类名 ({len(as3_classes)}) ===")
            for s in sorted(set(as3_classes))[:50]:
                print(f"    {s}")

        except Exception as e:
            print(f"  解压失败: {e}")
            # 直接搜索原始数据中的字符串
            all_strs = [s.decode('utf-8', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', manager_data)]
            print(f"  原始数据字符串数: {len(all_strs)}")
            for s in sorted(set(all_strs))[:50]:
                print(f"    {s}")
else:
    print(f"  非标准SWF，可能是加密文件")
    # 尝试 DES 解密
    from hashlib import md5
    try:
        from Crypto.Cipher import DES
        KEY = md5(b'hzytkjyxgs').digest()[:8]
        cipher = DES.new(KEY, DES.MODE_ECB)
        padded_len = (len(manager_data) // 8) * 8
        decrypted = cipher.decrypt(manager_data[:padded_len]) + manager_data[padded_len:]
        print(f"  解密后: {len(decrypted)} bytes, header: {decrypted[:8]}")

        # 尝试解压
        for wbits in [15, -15, 31, 47]:
            try:
                dec_obj = zlib.decompressobj(wbits=wbits if wbits > 0 or wbits == -15 else 15)
                result = dec_obj.decompress(decrypted[8:])
                try:
                    result += dec_obj.flush()
                except:
                    pass
                if len(result) > 100:
                    print(f"  wbits={wbits}: 解压 {len(result)} bytes")
                    full_swf = b'FWS' + decrypted[3:8] + result
                    all_strs = [s.decode('utf-8', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', full_swf)]
                    print(f"  字符串数: {len(all_strs)}")
                    for s in sorted(set(all_strs))[:100]:
                        print(f"    {s}")
                    break
            except zlib.error:
                pass
    except ImportError:
        print("  PyCryptodome not installed")

# 2. 尝试获取 BlazeDS 配置文件
print("\n=== 尝试获取 BlazeDS 配置文件 ===")
config_paths = [
    '/WEB-INF/flex/services-config.xml',
    '/WEB-INF/flex/remoting-config.xml',
    '/html/WEB-INF/flex/services-config.xml',
    '/html/WEB-INF/flex/remoting-config.xml',
    '/html/client/topo/WEB-INF/flex/services-config.xml',
    '/flex/services-config.xml',
    '/services-config.xml',
]
for path in config_paths:
    url = f'http://172.18.36.5:8000{path}'
    r = session.get(url, timeout=5)
    print(f"  {path}: {r.status_code}")
    if r.status_code == 200 and len(r.text) > 50:
        print(f"    内容前300字符: {r.text[:300]}")

# 3. 尝试访问其他 SWF 文件
print("\n=== 列出可能的 SWF 文件 ===")
swf_paths = [
    '/html/portlet/ext/draco/resources/draco_manager.swf',
    '/html/portlet/ext/draco/modules/draco_module.swf',
    '/html/portlet/ext/draco/resources/draco.swf',
    '/html/portlet/ext/draco/draco.swf',
    '/html/portlet/ext/draco/main.swf',
    '/html/portlet/ext/draco/resources/draco_module.swf',
]
for path in swf_paths:
    url = f'http://172.18.36.5:8000{path}'
    r = session.head(url, timeout=5)
    print(f"  {path}: {r.status_code}, Content-Length: {r.headers.get('content-length', '?')}")
