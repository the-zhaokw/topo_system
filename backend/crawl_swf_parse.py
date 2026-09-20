"""解析 draco_manager.swf 搜索 BlazeDS 配置"""
import requests as req
import re
import zlib
import struct

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

# 下载并解压 draco_manager.swf
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', timeout=60)
raw = r.content
print(f"SWF 原始大小: {len(raw)} bytes")

if raw[:3] == b'CWS':
    swf_data = zlib.decompress(raw[8:])
    print(f"SWF 解压后: {len(swf_data)} bytes")
elif raw[:3] == b'FWS':
    swf_data = raw[8:]
else:
    swf_data = raw

# === 1. 原始字节搜索 ===
print("\n=== 1. 原始字节搜索 ===")
search_patterns = [
    (b'messagebroker', 'messagebroker'),
    (b'channel-definition', 'channel-definition'),
    (b'channel_definition', 'channel_definition'),
    (b'<destination', '<destination'),
    (b'endpoint', 'endpoint'),
    (b'services-config', 'services-config'),
    (b'services_config', 'services_config'),
    (b'remoting-config', 'remoting-config'),
    (b'remoting_config', 'remoting_config'),
    (b'amf-channel', 'amf-channel'),
    (b'amfChannel', 'amfChannel'),
    (b'AMFChannel', 'AMFChannel'),
    (b'NetConnection', 'NetConnection'),
    (b'RemoteObject', 'RemoteObject'),
    (b'AsyncToken', 'AsyncToken'),
    (b'AbstractOperation', 'AbstractOperation'),
    (b'flex.messaging', 'flex.messaging'),
    (b'flex/messaging', 'flex/messaging'),
    (b'BlazeDS', 'BlazeDS'),
    (b'blazeds', 'blazeds'),
    (b'LCDS', 'LCDS'),
    (b'destination', 'destination'),
    (b'organizationService', 'organizationService'),
    (b'userService', 'userService'),
    (b'fileService', 'fileService'),
    (b'dracoModuleConfig', 'dracoModuleConfig'),
    (b'servicesConfig', 'servicesConfig'),
    (b'SERVICES_CONFIG', 'SERVICES_CONFIG'),
    (b'channelSet', 'channelSet'),
    (b'ChannelSet', 'ChannelSet'),
    (b'AMFChannel', 'AMFChannel'),
    (b'channelId', 'channelId'),
    (b'channelUrl', 'channelUrl'),
    (b'amfEndpoint', 'amfEndpoint'),
    (b'endpointUrl', 'endpointUrl'),
    (b'amfUrl', 'amfUrl'),
]

for pattern, name in search_patterns:
    positions = [m.start() for m in re.finditer(re.escape(pattern), swf_data)]
    if positions:
        print(f"\n  '{name}' 找到 {len(positions)} 处:")
        for pos in positions[:3]:
            # 显示上下文 (前后各 50 字节)
            start = max(0, pos - 30)
            end = min(len(swf_data), pos + len(pattern) + 70)
            context = swf_data[start:end]
            # 提取可打印字符
            printable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in context)
            print(f"    偏移 {pos}: {printable}")

# === 2. 搜索 SWF ABC (ActionScript Bytecode) ===
print("\n\n=== 2. 搜索 SWF 标签 ===")
# SWF 文件由标签组成, 每个标签有 tag_code 和 length
# DoABC 标签 (tag code 82) 包含 ActionScript 字节码
# DoInitAction 标签 (tag code 59) 包含初始化动作

pos = 0
# 跳过 SWF 头 (CWS/FWS + version + length + frame size + frame rate + frame count)
# 帧大小是位字段, 需要按位解析
# 简单起见, 搜索所有标签

def read_rect(data, pos):
    """读取 SWF Rect (位字段)"""
    if pos >= len(data):
        return pos
    # 读取 Nbits (5 bits)
    byte = data[pos]
    nbits = byte >> 3
    # Rect 占 5 + 4*nbits 位
    total_bits = 5 + 4 * nbits
    total_bytes = (total_bits + 7) // 8
    return pos + total_bytes

# 解析 SWF 头
sig = swf_data[:3]
version = swf_data[3]
file_length = struct.unpack('<I', swf_data[4:8])[0]
pos = 8

# 跳过帧大小 (Rect)
pos = read_rect(swf_data, pos)
# 跳过帧率 (2 bytes) 和帧数 (2 bytes)
pos += 4

print(f"SWF 头: {sig} 版本 {version} 长度 {file_length}")
print(f"标签开始位置: {pos}")

# 解析 SWF 标签
tag_count = 0
abc_data_list = []
while pos < len(swf_data) - 2:
    # 读取标签头 (2 bytes, 可能扩展为 4 bytes)
    tag_header = struct.unpack('<H', swf_data[pos:pos+2])[0]
    tag_code = tag_header >> 6
    tag_length = tag_header & 0x3F
    pos += 2

    # 如果长度是 0x3F, 读取 4 字节完整长度
    if tag_length == 0x3F:
        if pos + 4 > len(swf_data):
            break
        tag_length = struct.unpack('<I', swf_data[pos:pos+4])[0]
        pos += 4

    tag_data = swf_data[pos:pos+tag_length]

    # 显示重要的标签
    tag_names = {
        82: 'DoABC',
        59: 'DoInitAction',
        14: 'DefineSounds',
        69: 'FileAttributes',
        86: 'DefineSceneAndFrameLabelData',
        9: 'SetBackgroundColor',
        1: 'ShowFrame',
        0: 'End',
        12: 'DoAction',
        56: 'ExportAssets',
        57: 'ImportAssets',
        83: 'DefineBinaryData',
        88: 'DefineFontName',
    }

    if tag_code in [82, 59, 12, 83]:
        tag_name = tag_names.get(tag_code, f'Tag{tag_code}')
        print(f"\n  标签 #{tag_count}: {tag_name} (code={tag_code}, length={tag_length})")
        if tag_code == 82:
            # DoABC: name (null-terminated string) + ABC data
            null_pos = tag_data.find(b'\x00')
            if null_pos > 0:
                abc_name = tag_data[:null_pos].decode('utf-8', errors='replace')
                abc_data = tag_data[null_pos+1:]
                print(f"    ABC 名称: {abc_name}")
                print(f"    ABC 数据大小: {len(abc_data)}")
                abc_data_list.append((abc_name, abc_data))

                # 在 ABC 数据中搜索服务配置
                for pattern, pname in [(b'messagebroker', 'messagebroker'),
                                       (b'destination', 'destination'),
                                       (b'organizationService', 'organizationService'),
                                       (b'userService', 'userService'),
                                       (b'channel', 'channel'),
                                       (b'amf', 'amf'),
                                       (b'endpoint', 'endpoint'),
                                       (b'services', 'services'),
                                       (b'config', 'config')]:
                    positions = [m.start() for m in re.finditer(re.escape(pattern), abc_data)]
                    if positions:
                        print(f"    '{pname}' 在 ABC 中找到 {len(positions)} 处")
                        for p in positions[:5]:
                            start = max(0, p - 20)
                            end = min(len(abc_data), p + len(pattern) + 40)
                            context = abc_data[start:end]
                            printable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in context)
                            print(f"      偏移 {p}: {printable}")

        elif tag_code == 12:
            # DoAction: 老式 ActionScript
            # 在数据中搜索字符串
            all_strs = [s.decode('ascii', errors='ignore')
                       for s in re.findall(rb'[\x20-\x7e]{4,}', tag_data)]
            config_strs = [s for s in all_strs if any(kw in s.lower() for kw in
                          ['service', 'destination', 'channel', 'amf', 'messagebroker', 'config'])]
            if config_strs:
                print(f"    ActionScript 中的配置字符串:")
                for s in sorted(set(config_strs))[:10]:
                    print(f"      {s}")

        elif tag_code == 83:
            # DefineBinaryData
            print(f"    二进制数据大小: {tag_length}")
            # 搜索配置
            for pattern, pname in [(b'messagebroker', 'messagebroker'),
                                   (b'destination', 'destination'),
                                   (b'organizationService', 'orgService'),
                                   (b'<channel', '<channel'),
                                   (b'<destination', '<destination'),
                                   (b'<?xml', '<?xml')]:
                positions = [m.start() for m in re.finditer(re.escape(pattern), tag_data)]
                if positions:
                    print(f"    '{pname}' 找到 {len(positions)} 处")
                    for p in positions[:3]:
                        start = max(0, p - 10)
                        end = min(len(tag_data), p + 100)
                        context = tag_data[start:end]
                        printable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in context)
                        print(f"      {printable}")

    pos += tag_length
    tag_count += 1

    if tag_code == 0:  # End tag
        break

print(f"\n总标签数: {tag_count}")
print(f"ABC 数据块数: {len(abc_data_list)}")

# === 3. 在所有 ABC 数据中搜索服务配置 ===
print("\n\n=== 3. 在 ABC 数据中搜索配置 ===")
all_abc = b''.join([data for _, data in abc_data_list])
print(f"总 ABC 数据大小: {len(all_abc)} bytes")

# 搜索所有可读字符串
all_strs = [s.decode('ascii', errors='ignore')
            for s in re.findall(rb'[\x20-\x7e]{4,}', all_abc)]
print(f"总字符串数: {len(all_strs)}")

# 搜索服务相关
svc_strs = sorted(set(s for s in all_strs if 'Service' in s and len(s) < 100))
print(f"\nService 相关 ({len(svc_strs)}):")
for s in svc_strs:
    print(f"  {s}")

# 搜索 message/amf/channel 相关
amf_strs = sorted(set(s for s in all_strs if
                      any(kw in s.lower() for kw in ['messagebroker', 'amf', 'channel', 'endpoint'])
                      and len(s) < 100))
print(f"\nAMF/Channel 相关 ({len(amf_strs)}):")
for s in amf_strs:
    print(f"  {s}")

# 搜索 destination 相关
dest_strs = sorted(set(s for s in all_strs if 'destination' in s.lower() and len(s) < 100))
print(f"\nDestination 相关 ({len(dest_strs)}):")
for s in dest_strs:
    print(f"  {s}")

# 搜索配置相关
cfg_strs = sorted(set(s for s in all_strs if
                      any(kw in s.lower() for kw in ['servicesconfig', 'services_config', 'channelset', 'loaderconfig'])
                      and len(s) < 100))
print(f"\nConfig 相关 ({len(cfg_strs)}):")
for s in cfg_strs:
    print(f"  {s}")
