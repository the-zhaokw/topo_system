"""深入分析 draco_manager.swf 中的 AMF 配置和 RemoteObject 设置"""
import zipfile
import re
import zlib
import struct

# 读取之前保存的 draco_manager_decoded.bin
with open('d:/topo_system/backend/draco_manager_decoded.bin', 'rb') as f:
    swf_data = f.read()

print(f"draco_manager.swf 解码后大小: {len(swf_data)} bytes")

# 提取所有字符串
all_strs = [s.decode('utf-8', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{3,}', swf_data)]
print(f"字符串数: {len(all_strs)}")

# 1. 搜索 XML 片段
print("\n=== 1. 搜索 XML 配置片段 ===")
xml_patterns = re.findall(rb'<[^>]+(?:channel|destination|service|endpoint|amf|messagebroker|remote)[^>]*>', swf_data, re.I)
for match in xml_patterns[:20]:
    print(f"  {match.decode('ascii', errors='ignore')[:200]}")

# 2. 搜索所有看起来像 URL 的字符串
print("\n=== 2. 搜索 URL ===")
urls = sorted(set(s for s in all_strs if 'http' in s.lower() or s.startswith('/') or 'messagebroker' in s.lower()))
for s in urls:
    if len(s) < 200:
        print(f"  {s}")

# 3. 搜索 RemoteObject 相关配置
print("\n=== 3. RemoteObject / Channel 配置 ===")
for s in sorted(set(all_strs)):
    sl = s.lower()
    if any(kw in sl for kw in ['remote', 'channel', 'endpoint', 'destination',
                                'messagebroker', 'amfchannel', 'streamingamf',
                                'polling', 'netconnection', 'request',
                                'flex.messaging', 'remoting',
                                'services-config', 'channelset',
                                'amfchannel', 'streamingamfchannel',
                                'secureamfchannel']):
        if len(s) < 200:
            print(f"  {s}")

# 4. 搜索 service 名 (在 AS3 中通常以 "Service" 结尾)
print("\n=== 4. Service 相关字符串 ===")
service_strs = sorted(set(s for s in all_strs if ('Service' in s or 'service' in s) and len(s) < 100))
for s in service_strs:
    print(f"  {s}")

# 5. 搜索方法名 (get/find/load/query 开头)
print("\n=== 5. 可能的方法名 ===")
method_strs = sorted(set(s for s in all_strs if re.match(r'^[a-z][a-zA-Z]{3,50}$', s) and
                         any(kw in s.lower() for kw in ['get', 'find', 'load', 'query', 'search',
                                                         'fetch', 'count', 'list', 'save', 'create',
                                                         'delete', 'update', 'add', 'remove',
                                                         'export', 'import', 'check', 'verify',
                                                         'validate', 'login', 'authenticate'])))
for s in method_strs[:80]:
    print(f"  {s}")

# 6. 搜索 com. 开头的包名/类名
print("\n=== 6. AS3 包名/类名 ===")
class_strs = sorted(set(s for s in all_strs if re.match(r'^[a-z]+\.[a-zA-Z]', s) and len(s) < 80))
for s in class_strs:
    print(f"  {s}")

# 7. 搜索 BlazeDS 相关类名
print("\n=== 7. BlazeDS/Flex 相关类名 ===")
blaze_strs = sorted(set(s for s in all_strs if 'flex' in s.lower() or 'messaging' in s.lower() or 'remoting' in s.lower()))
for s in blaze_strs:
    if len(s) < 100:
        print(f"  {s}")

# 8. 搜索缓存配置
print("\n=== 8. 缓存/模块配置 ===")
cache_strs = sorted(set(s for s in all_strs if 'cache' in s.lower() or 'module' in s.lower() or 'config' in s.lower()))
for s in cache_strs[:40]:
    if len(s) < 100:
        print(f"  {s}")

# 9. 搜索关键配置字符串
print("\n=== 9. 关键配置 ===")
key_strs = sorted(set(s for s in all_strs if any(kw in s for kw in
    ['DEFAULT_', 'CONFIG_', 'AMF_', 'REMOTE_', 'SERVICE_',
     'DESTINATION', 'CHANNEL', 'ENDPOINT',
     'GATEWAY_URL', 'CONTEXT_ROOT', 'MESSAGEBROKER'])))
for s in key_strs:
    if len(s) < 200:
        print(f"  {s}")

# 10. 搜索 DRACO 常量
print("\n=== 10. DRACO 常量 ===")
draco_strs = sorted(set(s for s in all_strs if 'DRACO' in s or 'draco' in s))
for s in draco_strs:
    if len(s) < 200:
        print(f"  {s}")

# 11. 搜索 transmitfile 和附件相关
print("\n=== 11. transmitfile/attachment ===")
transmit_strs = sorted(set(s for s in all_strs if 'transmit' in s.lower() or 'attachment' in s.lower() or 'upload' in s.lower() or 'download' in s.lower()))
for s in transmit_strs:
    if len(s) < 200:
        print(f"  {s}")

# 12. 尝试在 SWF 中搜索 DoABC tag 的内容
# SWF 中 DoABC (tag type 82) 包含 ActionScript bytecode
print("\n=== 12. 搜索 ABC bytecode 中的类名 ===")
# 搜索 ABC header: 0x00 0x02 (minor version) 0x00 0x10 (major version 16)
# 或者直接搜索 flex.messaging
flex_patterns = re.findall(rb'flex\.messaging\.[\x20-\x7e]{5,100}', swf_data)
for p in flex_patterns[:20]:
    print(f"  {p.decode('ascii', errors='ignore')}")

# 13. 搜索所有 PascalCase 字符串 (可能是方法名或属性名)
print("\n=== 13. PascalCase 字符串 ===")
pascal_strs = sorted(set(s for s in all_strs if re.match(r'^[A-Z][a-zA-Z]{3,30}$', s)))
for s in pascal_strs[:50]:
    print(f"  {s}")
