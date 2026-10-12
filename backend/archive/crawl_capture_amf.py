"""
尝试多种方式发现 AMF 服务调用方式：
1. 尝试访问 BlazeDS 配置文件
2. 使用 fileService 读取配置
3. 尝试通用数据访问方法
"""
import requests as req
import struct
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

# ============================================
# 1. 尝试访问 BlazeDS 配置文件
# ============================================
print("\n=== 1. 尝试访问配置文件 ===")
config_paths = [
    '/WEB-INF/flex/remoting-config.xml',
    '/WEB-INF/flex/services-config.xml',
    '/WEB-INF/flex/proxy-config.xml',
    '/WEB-INF/web.xml',
    '/WEB-INF/flex/data-management-config.xml',
    '/flex/remoting-config.xml',
    '/flex/services-config.xml',
    '/remoting-config.xml',
    '/services-config.xml',
    '/html/client/topo/WEB-INF/flex/remoting-config.xml',
    '/html/client/topo/WEB-INF/web.xml',
    '/html/WEB-INF/flex/remoting-config.xml',
    '/html/WEB-INF/web.xml',
]

for path in config_paths:
    url = f'http://172.18.36.5:8000{path}'
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.text) > 50:
            print(f"  ✓ {path}: {resp.status_code} ({len(resp.text)} bytes)")
            print(f"    {resp.text[:500]}")
        elif resp.status_code != 404:
            print(f"  {path}: {resp.status_code}")
    except:
        pass

# ============================================
# 2. 尝试在 fileService 上调用方法读取文件
# ============================================
print("\n=== 2. fileService 方法测试 ===")
AMF_URL = 'http://172.18.36.5:8000/messagebroker/amf'

def build_amf(dest, op, args=None):
    if args is None:
        args = []
    body_items = b''
    for arg in args:
        if isinstance(arg, str):
            b = arg.encode('utf-8')
            body_items += b'\x02' + struct.pack('>H', len(b)) + b
        elif isinstance(arg, (int, float)):
            body_items += b'\x00' + struct.pack('>d', float(arg))
        elif isinstance(arg, bool):
            body_items += b'\x01' + (b'\x01' if arg else b'\x00')
        elif arg is None:
            body_items += b'\x05'
        else:
            body_items += b'\x05'
    body_array = b'\x0A' + struct.pack('>I', len(args)) + body_items
    target = f"{dest}.{op}"
    packet = b'\x00\x00\x00\x00\x00\x01'
    tb = target.encode('utf-8')
    packet += struct.pack('>H', len(tb)) + tb
    packet += struct.pack('>H', 0)
    packet += struct.pack('>I', len(body_array)) + body_array
    header = b'\x00\x00\x00\x00\x00\x01'
    return header + packet

def decode_response(data):
    """简化解码 AMF0 响应"""
    if len(data) < 6:
        return None
    # 跳过 headers
    version = struct.unpack('>H', data[0:2])[0]
    header_count = struct.unpack('>H', data[2:4])[0]
    pos = 4
    for _ in range(header_count):
        if pos + 6 > len(data):
            return None
        name_len = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2 + name_len + 4
        # skip value
        if pos < len(data) and data[pos] == 0x05:
            pos += 1
    # bodies
    body_count = struct.unpack('>H', data[pos:pos+2])[0]
    pos += 2
    for _ in range(body_count):
        if pos + 4 > len(data):
            return None
        target_len = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        target = data[pos:pos+target_len].decode('utf-8', errors='replace')
        pos += target_len
        resp_len = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        body_len = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        body_data = data[pos:pos+body_len]
        # 尝试解码 body
        return decode_amf_value(body_data, 0)[0]
    return None

def decode_amf_value(data, pos):
    if pos >= len(data):
        return None, pos
    marker = data[pos]
    pos += 1

    if marker == 0x00:  # number
        val = struct.unpack('>d', data[pos:pos+8])[0]
        return val, pos + 8
    elif marker == 0x01:  # boolean
        return data[pos] == 1, pos + 1
    elif marker == 0x02:  # string
        slen = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        s = data[pos:pos+slen].decode('utf-8', errors='replace')
        return s, pos + slen
    elif marker == 0x03:  # object
        obj = {}
        while pos < len(data):
            key_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            if key_len == 0 and data[pos] == 0x09:  # end marker
                pos += 1
                break
            key = data[pos:pos+key_len].decode('utf-8', errors='replace')
            pos += key_len
            val, pos = decode_amf_value(data, pos)
            obj[key] = val
        return obj, pos
    elif marker == 0x05:  # null
        return None, pos
    elif marker == 0x06:  # undefined
        return None, pos
    elif marker == 0x0A:  # array
        count = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        arr = []
        for _ in range(count):
            val, pos = decode_amf_value(data, pos)
            arr.append(val)
        return arr, pos
    elif marker == 0x07:  # long string
        slen = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        s = data[pos:pos+slen].decode('utf-8', errors='replace')
        return s, pos + slen
    elif marker == 0x0C:  # AMF3 string - might appear in mixed mode
        # Try to skip AMF3 data
        return f"<AMF3 data at pos {pos}>", pos
    elif marker == 0x11:  # AMF3
        # Skip AMF3 - just return raw
        return f"<AMF3 data>", pos
    else:
        return f"<unknown marker 0x{marker:02x} at pos {pos-1}>", pos

def send_amf(dest, op, args=None):
    """发送 AMF 请求并返回解码结果"""
    if args is None:
        args = []
    amf_data = build_amf(dest, op, args)
    resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf'}, timeout=10)
    return decode_response(resp.content)

# 测试 fileService 的各种方法
file_methods = [
    'toString', 'getClass', 'notify',
    'getFiles', 'listFiles', 'readFile', 'getFile',
    'load', 'loadAll', 'getAll',
    'getSchema', 'getConfig', 'getConfiguration',
    'getData', 'query', 'queryData',
    'getModel', 'getDataModel', 'getEntity',
    'getProject', 'getBug', 'getDmBug',
    'findBug', 'findDmBug', 'queryBug',
    'getOrganization', 'getOrg',
    'loadFile', 'openFile', 'fetchFile',
]

for method in file_methods:
    try:
        result = send_amf('fileService', method)
        if result is not None:
            result_str = str(result)[:300]
            if 'Cannot invoke' not in result_str and 'No destination' not in result_str:
                print(f"  ✓✓✓ fileService.{method}: {result_str}")
            else:
                print(f"  ✗ fileService.{method}: {result_str[:100]}")
    except Exception as e:
        print(f"  ✗ fileService.{method}: Error {e}")

# ============================================
# 3. 测试 organizationService 的方法
# ============================================
print("\n=== 3. organizationService 方法测试 ===")
org_methods = [
    'toString', 'getClass', 'notify',
    'getOrganization', 'getOrg', 'getAll', 'findAll', 'loadAll',
    'getOrganizationTree', 'getOrgTree', 'getTree',
    'getProjects', 'getProject', 'findProject', 'queryProject',
    'getBugs', 'getBug', 'findBug', 'queryBug',
    'getDmBug', 'findDmBug', 'queryDmBug',
    'getByOrg', 'findByOrg', 'getByOrganization',
    'getBugByOrg', 'getBugsByOrg', 'getBugByOrganization',
    'getProjectByOrg', 'getProjectsByOrg',
    'getChildren', 'getChild', 'getSubOrg', 'getSubOrganizations',
    'getProjectList', 'getBugList',
    'getRTN', 'getByRTN', 'getRTNProjects', 'getRTNBugs',
    'query', 'queryData', 'queryEntity',
    'load', 'loadEntity', 'loadData',
    'getData', 'getEntity', 'getEntities',
    'getProjectData', 'getBugData',
]

for method in org_methods:
    try:
        result = send_amf('organizationService', method)
        if result is not None:
            result_str = str(result)[:300]
            if 'Cannot invoke' not in result_str and 'No destination' not in result_str:
                print(f"  ✓✓✓ organizationService.{method}: {result_str}")
            else:
                print(f"  ✗ organizationService.{method}: {result_str[:100]}")
    except Exception as e:
        print(f"  ✗ organizationService.{method}: Error {e}")

# ============================================
# 4. 测试 workLogService 的方法
# ============================================
print("\n=== 4. workLogService 方法测试 ===")
worklog_methods = [
    'toString', 'getClass', 'notify',
    'getAll', 'findAll', 'loadAll',
    'getWorkLog', 'getWorkLogs',
    'getBug', 'getBugs', 'findBug', 'findBugs',
    'getProject', 'getProjects', 'findProject',
    'query', 'queryData', 'queryEntity',
    'getData', 'getEntity', 'getEntities',
    'getByOrg', 'findByOrg',
    'getBugByOrg', 'getBugsByOrg',
]

for method in worklog_methods:
    try:
        result = send_amf('workLogService', method)
        if result is not None:
            result_str = str(result)[:300]
            if 'Cannot invoke' not in result_str and 'No destination' not in result_str:
                print(f"  ✓✓✓ workLogService.{method}: {result_str}")
            else:
                print(f"  ✗ workLogService.{method}: {result_str[:100]}")
    except Exception as e:
        print(f"  ✗ workLogService.{method}: Error {e}")

# ============================================
# 5. 尝试带参数的方法调用
# ============================================
print("\n=== 5. 带参数的方法调用 ===")
# 尝试 organizationService 带字符串参数
param_methods = [
    ('organizationService', 'getOrganization', ['RTN']),
    ('organizationService', 'getOrg', ['RTN']),
    ('organizationService', 'getByName', ['RTN']),
    ('organizationService', 'findByName', ['RTN']),
    ('organizationService', 'getByOrg', ['RTN']),
    ('organizationService', 'getProjects', ['RTN']),
    ('organizationService', 'getProject', ['RTN']),
    ('organizationService', 'getBugs', ['RTN']),
    ('organizationService', 'getBug', ['RTN']),
    ('organizationService', 'getByOrg', ['RTN']),
    ('organizationService', 'getProjectByOrg', ['RTN']),
    ('organizationService', 'getBugByOrg', ['RTN']),
    ('organizationService', 'getBugsByOrg', ['RTN']),
    ('organizationService', 'getProjectByOrganization', ['RTN']),
    ('organizationService', 'getBugByOrganization', ['RTN']),
    ('organizationService', 'getBugsByOrganization', ['RTN']),
    ('organizationService', 'getProjectList', ['RTN']),
    ('organizationService', 'getBugList', ['RTN']),
    ('organizationService', 'query', ['RTN']),
    ('organizationService', 'query', ['dmBug']),
    ('organizationService', 'query', ['dmBug', 'all']),
    ('organizationService', 'query', ['dmBug', 'all', 'RTN']),
    ('organizationService', 'query', ['project', 'all']),
    ('organizationService', 'getData', ['dmBug']),
    ('organizationService', 'getData', ['dmBug', 'all']),
    ('organizationService', 'getEntity', ['dmBug']),
    ('organizationService', 'getEntity', ['dmBug', 'all']),
    ('organizationService', 'load', ['dmBug']),
    ('organizationService', 'load', ['dmBug', 'all']),
    # 尝试 IPRAN 作为参数
    ('organizationService', 'getProjects', ['IPRAN']),
    ('organizationService', 'getBugs', ['IPRAN']),
    ('organizationService', 'getProject', ['IPRAN']),
    ('organizationService', 'getBug', ['IPRAN']),
]

for dest, method, args in param_methods:
    try:
        result = send_amf(dest, method, args)
        if result is not None:
            result_str = str(result)[:300]
            if 'Cannot invoke' not in result_str and 'No destination' not in result_str:
                print(f"  ✓✓✓ {dest}.{method}({args}): {result_str}")
    except Exception as e:
        pass

print("\n完成")
