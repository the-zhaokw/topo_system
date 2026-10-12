"""解密并深度分析 draco_module.swf，查找 AMF 服务名和方法名"""
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

# === 1. 下载并解密 draco_module.swf ===
print("\n=== 1. 下载并解密 draco_module.swf ===")
url = 'http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf'
r = session.get(url, timeout=120)
raw = r.content
print(f"原始大小: {len(raw)} bytes")
print(f"前16字节: {raw[:16].hex()}")

# DES-ECB 解密
KEY = md5(b'hzytkjyxgs').digest()[:8]
cipher = DES.new(KEY, DES.MODE_ECB)
padded_len = (len(raw) // 8) * 8
decrypted = cipher.decrypt(raw[:padded_len]) + raw[padded_len:]
print(f"解密后大小: {len(decrypted)} bytes")
print(f"解密后前16字节: {decrypted[:16].hex()}")

# 检查是否是标准 SWF
header = decrypted[:3]
print(f"SWF 头: {header}")

if header == b'CWS':
    print("=> CWS 压缩格式")
    # 尝试解压
    best_data = b''
    for wbits in [15, -15, 31, 47]:
        try:
            dec_obj = zlib.decompressobj(wbits=wbits)
            result = dec_obj.decompress(decrypted[8:])
            try:
                result += dec_obj.flush()
            except:
                pass
            if len(result) > len(best_data):
                best_data = result
                print(f"  wbits={wbits}: 解压 {len(result)} bytes")
        except zlib.error as e:
            try:
                dec_obj = zlib.decompressobj(wbits=wbits)
                result = dec_obj.decompress(decrypted[8:], 200*1024*1024)
                if len(result) > len(best_data):
                    best_data = result
                    print(f"  wbits={wbits} (partial): 解压 {len(result)} bytes, error: {str(e)[:50]}")
            except:
                pass

    if best_data:
        swf_data = best_data
        print(f"\n使用最佳解压结果: {len(swf_data)} bytes")
    else:
        swf_data = decrypted[8:]
        print(f"\n解压失败, 使用解密后原始数据: {len(swf_data)} bytes")

elif header == b'FWS':
    print("=> FWS 未压缩格式")
    swf_data = decrypted[8:]

else:
    print(f"=> 未知格式: {header}")
    # 可能不是标准 SWF, 直接使用解密后的数据
    swf_data = decrypted

# === 2. 提取所有可读字符串 ===
print(f"\n=== 2. 提取字符串 (从 {len(swf_data)} bytes 数据) ===")
all_strs = [s.decode('ascii', errors='ignore')
            for s in re.findall(rb'[\x20-\x7e]{4,}', swf_data)]
print(f"总字符串数: {len(all_strs)}")

# 保存所有字符串
with open('d:/topo_system/backend/module_strings.txt', 'w', encoding='utf-8') as f:
    for s in all_strs:
        f.write(s + '\n')
print("所有字符串已保存到 module_strings.txt")

# === 3. 搜索 Service 相关 ===
svc_strs = sorted(set(s for s in all_strs if 'Service' in s and len(s) < 150))
print(f"\n=== Service 相关 ({len(svc_strs)}) ===")
for s in svc_strs:
    print(f"  {s}")

# === 4. 搜索 destination 相关 ===
dest_strs = sorted(set(s for s in all_strs if 'destination' in s.lower() and len(s) < 150))
print(f"\n=== Destination 相关 ({len(dest_strs)}) ===")
for s in dest_strs:
    print(f"  {s}")

# === 5. 搜索 Remote/Channel/AMF 相关 ===
remote_strs = sorted(set(s for s in all_strs
                         if ('RemoteObject' in s or 'Remote' in s or
                             'channel' in s.lower() or 'Channel' in s or
                             'messagebroker' in s.lower() or 'amf' in s.lower() or
                             'BlazeDS' in s or 'blazeds' in s.lower())
                         and len(s) < 150))
print(f"\n=== Remote/Channel/AMF 相关 ({len(remote_strs)}) ===")
for s in remote_strs:
    print(f"  {s}")

# === 6. 搜索方法名 (get/find/query/create/update/delete) ===
method_strs = sorted(set(s for s in all_strs
                         if re.match(r'^[a-z][a-zA-Z]{4,60}$', s) and
                         any(kw in s.lower() for kw in
                             ['get', 'find', 'load', 'query', 'search',
                              'count', 'list', 'fetch', 'retrieve',
                              'create', 'update', 'delete', 'save',
                              'execute', 'export', 'import'])))
print(f"\n=== 方法名候选 ({len(method_strs)}) ===")
for s in method_strs[:200]:
    print(f"  {s}")

# === 7. 搜索 bug/project/org/rtn/ipran 相关 ===
domain_strs = sorted(set(s for s in all_strs
                         if any(kw in s.lower() for kw in
                             ['bug', 'project', 'org', 'rtn', 'ipran',
                              'task', 'requirement', 'version', 'build',
                              'release', 'risk', 'issue', 'test', 'phase',
                              'baseline', 'dmbug', 'dmproject', 'dmtask'])))
print(f"\n=== 领域相关 ({len(domain_strs)}) ===")
for s in domain_strs[:80]:
    print(f"  {s}")

# === 8. 搜索 com.cloudtopo 包路径 ===
pkg_strs = sorted(set(s for s in all_strs if 'com.cloudtopo' in s or 'com.loader' in s or 'cloudtopo' in s))
print(f"\n=== 包路径 ({len(pkg_strs)}) ===")
for s in pkg_strs[:50]:
    print(f"  {s}")

# === 9. 搜索 RemoteObject 调用模式 ===
# Flex 中 RemoteObject 调用: new RemoteObject(destination), operation = getOperation(methodName)
ro_strs = sorted(set(s for s in all_strs
                     if ('RemoteObject' in s or 'getOperation' in s or
                         'AsyncToken' in s or 'AbstractOperation' in s or
                         'invoke' in s.lower() and 'operation' in s.lower())
                     and len(s) < 150))
print(f"\n=== RemoteObject 调用相关 ({len(ro_strs)}) ===")
for s in ro_strs:
    print(f"  {s}")

# === 10. 搜索 BlazeDS 配置 XML ===
print(f"\n=== 10. 搜索 XML 配置 ===")
# 搜索 services-config
xml_configs = re.findall(rb'<services-config.*?</services-config>', swf_data, re.DOTALL)
print(f"services-config: {len(xml_configs)}")

# 搜索 destination 定义
xml_dests = re.findall(rb'<destination[^>]*>.*?</destination>', swf_data, re.DOTALL)
print(f"destination 定义: {len(xml_dests)}")

# 搜索 channel 定义
xml_channels = re.findall(rb'<channel-definition[^>]*>.*?</channel-definition>', swf_data, re.DOTALL)
print(f"channel-definition: {len(xml_channels)}")

# 搜索 <source> 标签 (BlazeDS destination 的 source 属性)
source_matches = re.findall(rb'<source>([^<]+)</source>', swf_data)
print(f"<source> 标签: {len(source_matches)}")
for s in source_matches:
    print(f"  {s.decode('utf-8', errors='replace')}")

# === 11. 从解密后的原始数据中也搜索 (未解压部分) ===
print(f"\n=== 11. 从解密后原始数据搜索 ===")
raw_strs = [s.decode('ascii', errors='ignore')
            for s in re.findall(rb'[\x20-\x7e]{4,}', decrypted)]
print(f"解密后原始数据字符串数: {len(raw_strs)}")

svc_raw = sorted(set(s for s in raw_strs if 'Service' in s and len(s) < 100))
print(f"Service 相关 (原始): {len(svc_raw)}")
for s in svc_raw:
    print(f"  {s}")

dest_raw = sorted(set(s for s in raw_strs if 'destination' in s.lower() and len(s) < 100))
print(f"\nDestination 相关 (原始): {len(dest_raw)}")
for s in dest_raw:
    print(f"  {s}")

remote_raw = sorted(set(s for s in raw_strs
                        if ('RemoteObject' in s or 'messagebroker' in s.lower() or
                            'amf' in s.lower())
                        and len(s) < 100))
print(f"\nRemote/AMF 相关 (原始): {len(remote_raw)}")
for s in remote_raw:
    print(f"  {s}")

# 方法名
method_raw = sorted(set(s for s in raw_strs
                        if re.match(r'^[a-z][a-zA-Z]{4,60}$', s) and
                        any(kw in s.lower() for kw in
                            ['get', 'find', 'load', 'query', 'search',
                             'create', 'update', 'delete', 'save',
                             'execute', 'export'])))
print(f"\n方法名候选 (原始): {len(method_raw)}")
for s in method_raw[:100]:
    print(f"  {s}")

# 领域相关
domain_raw = sorted(set(s for s in raw_strs
                        if any(kw in s.lower() for kw in
                            ['bug', 'project', 'org', 'rtn', 'ipran',
                             'dmbug', 'dmproject'])))
print(f"\n领域相关 (原始): {len(domain_raw)}")
for s in domain_raw[:50]:
    print(f"  {s}")
