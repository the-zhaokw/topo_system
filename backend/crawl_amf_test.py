"""获取cache-config.xml并手动构造AMF0请求"""
import requests as req
import re
import struct
import zlib
import uuid
import time
import json

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

# 1. 获取 cache-config.xml
print("\n=== cache-config.xml ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/cache-config.xml', timeout=10)
print(f"状态码: {r.status_code}")
if r.status_code == 200:
    print(r.text[:3000])

# 2. 解密并分析 draco_module.swf (提取 service 名)
print("\n\n=== 解密 draco_module.swf ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf', timeout=60)
mod_data = r.content
print(f"原始大小: {len(mod_data)} bytes")

from hashlib import md5
from Crypto.Cipher import DES

KEY = md5(b'hzytkjyxgs').digest()[:8]
cipher = DES.new(KEY, DES.MODE_ECB)
padded_len = (len(mod_data) // 8) * 8
decrypted = cipher.decrypt(mod_data[:padded_len]) + mod_data[padded_len:]
print(f"解密后: {len(decrypted)} bytes, header: {decrypted[:8]}")

# 容错解压
best_result = b''
for wbits in [15, -15, 31, 47]:
    try:
        dec_obj = zlib.decompressobj(wbits=wbits if wbits > 0 or wbits == -15 else 15)
        result = dec_obj.decompress(decrypted[8:])
        try:
            result += dec_obj.flush()
        except:
            pass
        if len(result) > len(best_result):
            best_result = result
            print(f"  wbits={wbits}: 解压 {len(result)} bytes")
    except zlib.error as e:
        try:
            dec_obj = zlib.decompressobj(wbits=wbits if wbits > 0 or wbits == -15 else 15)
            result = dec_obj.decompress(decrypted[8:], 100*1024*1024)
            if len(result) > len(best_result):
                best_result = result
                print(f"  wbits={wbits} (partial): 解压 {len(result)} bytes")
        except:
            pass

print(f"最佳解压结果: {len(best_result)} bytes")

if len(best_result) > 100:
    # 保存
    with open('d:/topo_system/backend/draco_module_partial.bin', 'wb') as f:
        f.write(best_result)

    all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', best_result)]
    print(f"字符串总数: {len(all_strs)}")

    # 搜索所有看起来像 destination 名的字符串
    # 在 BlazeDS 中，destination 通常是 PascalCase 名字，如 "testCaseService"
    # 且会出现在 RemoteObject 的 destination 属性中
    # 或者以 "Service" 结尾

    # 搜索 com.xxx.service 或 com.xxx.delegate
    service_classes = set()
    for s in all_strs:
        if re.match(r'^[a-z]+\.[a-zA-Z]', s) and len(s) < 80:
            sl = s.lower()
            if any(kw in sl for kw in ['service', 'delegate', 'remote', 'proxy', 'facade', 'rpc']):
                service_classes.add(s)
    print(f"\n=== 服务相关类名 ({len(service_classes)}) ===")
    for s in sorted(service_classes):
        print(f"  {s}")

    # 搜索 BlazeDS destination 名
    # 这些通常是 camelCase 或 PascalCase，不以 com. 开头
    dest_candidates = set()
    for s in all_strs:
        if re.match(r'^[a-z][a-zA-Z]+Service$', s):
            dest_candidates.add(s)
        elif re.match(r'^[a-z][a-zA-Z]+Delegate$', s):
            dest_candidates.add(s)
        elif re.match(r'^[a-z][a-zA-Z]+RemoteObject$', s):
            dest_candidates.add(s)
    print(f"\n=== Destination 候选 ({len(dest_candidates)}) ===")
    for s in sorted(dest_candidates):
        print(f"  {s}")

    # 搜索所有可能的方法名 (get/find/load/save/create/delete/update + 业务词)
    method_names = set()
    for s in all_strs:
        if re.match(r'^[a-z][a-zA-Z0-9]{4,60}$', s):
            sl = s.lower()
            if any(kw in sl for kw in ['get', 'find', 'load', 'save', 'create', 'delete', 'update',
                                         'query', 'search', 'list', 'export', 'import',
                                         'add', 'remove', 'modify', 'batch', 'all']):
                if not any(skip in sl for skip in ['effect', 'style', 'manager', 'event', 'error',
                                                          'binding', 'animation', 'transition', 'cursor',
                                                          'focus', 'drag', 'tooltip', 'validator',
                                                          'formatter', 'skin', 'layout', 'container',
                                                          'button', 'label', 'text', 'list', 'grid',
                                                          'chart', 'series', 'stroke', 'fill',
                                                          'default', 'class', 'instance', 'factory',
                                                          'header', 'footer', 'navigator']):
                    method_names.add(s)
    print(f"\n=== 方法名候选 ({len(method_names)}) ===")
    for s in sorted(method_names)[:80]:
        print(f"  {s}")

    # 搜索 transmitfile
    transmit = [s for s in all_strs if 'transmit' in s.lower() or 'attachment' in s.lower()]
    print(f"\n=== transmitfile 相关 ===")
    for s in sorted(set(transmit)):
        print(f"  {s}")

# 3. 手动构造 AMF0 请求
print("\n\n=== 手动构造 AMF0 请求测试 ===")

def write_amf_string(data, s):
    """写入 AMF0 UTF8 字符串"""
    encoded = s.encode('utf-8')
    data += struct.pack('>H', len(encoded))
    data += encoded
    return data

def write_amf_long_string(data, s):
    """写入 AMF0 long string"""
    encoded = s.encode('utf-8')
    data += b'\x0C'  # long string type
    data += struct.pack('>I', len(encoded))
    data += encoded
    return data

def write_amf_number(data, n):
    """写入 AMF0 number"""
    data += b'\x00'  # number type
    data += struct.pack('>d', n)
    return data

def write_amf_string_val(data, s):
    """写入 AMF0 string value"""
    data += b'\x02'  # string type
    encoded = s.encode('utf-8')
    data += struct.pack('>H', len(encoded))
    data += encoded
    return data

def write_amf_null(data):
    data += b'\x05'  # null
    return data

def write_amf_bool(data, b):
    data += b'\x01'  # bool type
    data += b'\x01' if b else b'\x00'
    return data

def write_amf_strict_array(data, items):
    """写入 AMF0 strict array"""
    data += b'\x0A'  # array type
    data += struct.pack('>I', len(items))
    for item in items:
        data += item
    return data

def write_amf_object(data, fields):
    """写入 AMF0 object"""
    data += b'\x03'  # object type
    for key, value in fields:
        # key is always a string
        encoded = key.encode('utf-8')
        data += struct.pack('>H', len(encoded))
        data += encoded
        data += value
    # end marker
    data += b'\x00\x00\x09'
    return data

def build_remoting_message(destination, operation, args=None):
    """构造 BlazeDS RemotingMessage 的 AMF0 编码"""
    msg_id = str(uuid.uuid4()).replace('-', '')  # 简单的 UUID
    msg_id = msg_id[:8] + '-' + msg_id[8:12] + '-' + msg_id[12:16] + '-' + msg_id[16:20] + '-' + msg_id[20:]

    # 构建 body 参数数组
    if args is None:
        args = []

    body_items = []
    for arg in args:
        if isinstance(arg, str):
            body_items.append(b'\x02' + struct.pack('>H', len(arg.encode('utf-8'))) + arg.encode('utf-8'))
        elif isinstance(arg, (int, float)):
            body_items.append(b'\x00' + struct.pack('>d', float(arg)))
        elif isinstance(arg, bool):
            body_items.append(b'\x01' + (b'\x01' if arg else b'\x00'))
        elif arg is None:
            body_items.append(b'\x05')
        else:
            body_items.append(b'\x05')

    body_data = b'\x0A' + struct.pack('>I', len(body_items))
    for item in body_items:
        body_data += item

    # RemotingMessage fields
    fields = [
        ('source', b'\x05'),  # null
        ('operation', b'\x02' + struct.pack('>H', len(operation.encode('utf-8'))) + operation.encode('utf-8')),
        ('destination', b'\x02' + struct.pack('>H', len(destination.encode('utf-8'))) + destination.encode('utf-8')),
        ('messageId', b'\x02' + struct.pack('>H', len(msg_id.encode('utf-8'))) + msg_id.encode('utf-8')),
        ('timestamp', b'\x00' + struct.pack('>d', 0.0)),
        ('timeToLive', b'\x00' + struct.pack('>d', 0.0)),
        ('body', body_data),
        ('clientId', b'\x05'),  # null
    ]

    # AS3 flex.messaging.messages.RemotingMessage
    # 先写 className，再写字段
    obj_data = b'\x03'  # object type
    # className for typed object (ABCStr): externalizable=true
    # 实际上 BlazeDS 用的是 typed object
    # 让我们用简单对象试试

    for key, value in fields:
        encoded = key.encode('utf-8')
        obj_data += struct.pack('>H', len(encoded))
        obj_data += encoded
        obj_data += value
    obj_data += b'\x00\x00\x09'  # end marker

    return obj_data

def build_amf0_request(destination, operation, args=None):
    """构造完整的 AMF0 HTTP 请求体"""
    # AMF0 packet
    packet = b'\x00\x00'  # version: AMF0
    # No headers
    packet += b'\x00\x00'  # header count = 0
    # One body
    packet += b'\x00\x01'  # body count = 1

    # Body target URI: "null" for BlazeDS
    target = b'null'
    packet += struct.pack('>H', len(target))
    packet += target

    # Response URI: empty
    packet += struct.pack('>H', 0)

    # Content: the RemotingMessage as AMF0 value
    msg = build_remoting_message(destination, operation, args)
    packet += msg

    return packet

# 测试不同的 destination/operation 组合
# 基于常见的测试管理系统的命名模式
test_destinations = [
    'testPlanService',
    'testCaseService',
    'testRunService',
    'testSuiteService',
    'testStepService',
    'defectService',
    'bugService',
    'projectService',
    'moduleService',
    'requirementService',
    'scenarioService',
    'environmentService',
    'buildService',
    'userService',
    'executionService',
    'reportService',
    'statisticsService',
    'topoService',
    'dracoService',
    'homeService',
    'dashboardService',
    'taskService',
]

test_operations = [
    'getAll',
    'getList',
    'findAll',
    'findAllProject',
    'getProjectList',
    'getProjects',
    'getById',
    'loadAll',
]

# 先测试 AMF 端点是否响应
print("测试 AMF 端点...")
for dest in test_destinations[:5]:
    for op in ['getAll', 'getList', 'findAll']:
        amf_data = build_amf0_request(dest, op)
        try:
            resp = session.post(
                'http://172.18.36.5:8000/messagebroker/amf',
                data=amf_data,
                headers={
                    'Content-Type': 'application/x-amf',
                    'Accept': 'application/x-amf',
                },
                timeout=10
            )
            body = resp.content
            print(f"\n  {dest}.{op}(): {resp.status_code}, {len(body)} bytes")
            # 简单分析响应
            if len(body) > 0:
                # 检查响应头
                ct = resp.headers.get('content-type', '')
                print(f"    Content-Type: {ct}")
                # 提取字符串
                strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{5,}', body)]
                if strs:
                    print(f"    Strings: {strs[:10]}")
                else:
                    print(f"    Hex: {body[:50].hex()}")
        except Exception as e:
            print(f"  {dest}.{op}(): 错误: {e}")
