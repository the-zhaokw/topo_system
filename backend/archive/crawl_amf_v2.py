"""修复 AMF0 RemotingMessage 编码 - 使用 typed object 格式"""
import requests as req
import struct
import re
import uuid
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
# AMF0 编码器
# ============================================

def enc_str(s):
    """编码 AMF0 string value"""
    b = s.encode('utf-8')
    return b'\x02' + struct.pack('>H', len(b)) + b

def enc_long_str(s):
    """编码 AMF0 long string value"""
    b = s.encode('utf-8')
    return b'\x0C' + struct.pack('>I', len(b)) + b

def enc_num(n):
    """编码 AMF0 number"""
    return b'\x00' + struct.pack('>d', float(n))

def enc_null():
    return b'\x05'

def enc_bool(b):
    return b'\x01' + (b'\x01' if b else b'\x00')

def enc_strict_array(items_data):
    """编码 AMF0 strict array - items_data 是已编码的 items bytes"""
    return b'\x0A' + struct.pack('>I', len(items_data)) + items_data

def enc_typed_object(class_name, fields):
    """编码 AMF0 typed object (type 0x10)"""
    data = b'\x10'  # typed object marker
    data += struct.pack('>H', len(class_name.encode('utf-8')))
    data += class_name.encode('utf-8')
    for key, value in fields:
        kb = key.encode('utf-8')
        data += struct.pack('>H', len(kb))
        data += kb
        data += value
    data += b'\x00\x00\x09'  # end marker
    return data

def enc_object(fields):
    """编码 AMF0 simple object (type 0x03)"""
    data = b'\x03'
    for key, value in fields:
        kb = key.encode('utf-8')
        data += struct.pack('>H', len(kb))
        data += kb
        data += value
    data += b'\x00\x00\x09'
    return data

# ============================================
# AMF0 解码器 (同前)
# ============================================

class AMF0Decoder:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read_u8(self):
        v = self.data[self.pos]; self.pos += 1; return v

    def read_u16(self):
        v = struct.unpack('>H', self.data[self.pos:self.pos+2])[0]; self.pos += 2; return v

    def read_u32(self):
        v = struct.unpack('>I', self.data[self.pos:self.pos+4])[0]; self.pos += 4; return v

    def read_double(self):
        v = struct.unpack('>d', self.data[self.pos:self.pos+8])[0]; self.pos += 8; return v

    def read_string(self):
        length = self.read_u16()
        s = self.data[self.pos:self.pos+length].decode('utf-8', errors='replace')
        self.pos += length; return s

    def read_long_string(self):
        length = self.read_u32()
        s = self.data[self.pos:self.pos+length].decode('utf-8', errors='replace')
        self.pos += length; return s

    def read_value(self):
        type_marker = self.read_u8()
        if type_marker == 0x00: return self.read_double()
        elif type_marker == 0x01: return self.read_u8() != 0
        elif type_marker == 0x02: return self.read_string()
        elif type_marker == 0x03:
            obj = {}
            while True:
                key = self.read_string()
                if len(key) == 0:
                    next_byte = self.read_u8()
                    if next_byte == 0x09: break
                    else: self.pos -= 1; continue
                val = self.read_value(); obj[key] = val
            return obj
        elif type_marker == 0x05: return None
        elif type_marker == 0x06: return None
        elif type_marker == 0x08:
            count = self.read_u32(); obj = {}
            for _ in range(count):
                key = self.read_string(); val = self.read_value(); obj[key] = val
            while True:
                key = self.read_string()
                if len(key) == 0:
                    next_byte = self.read_u8()
                    if next_byte == 0x09: break
                    else: self.pos -= 1; continue
                val = self.read_value(); obj[key] = val
            return obj
        elif type_marker == 0x09: return '__END__'
        elif type_marker == 0x0A:
            count = self.read_u32(); arr = []
            for _ in range(count): arr.append(self.read_value())
            return arr
        elif type_marker == 0x0B: return self.read_double()
        elif type_marker == 0x0C: return self.read_long_string()
        elif type_marker == 0x10:
            class_name = self.read_string()
            obj = {}
            while True:
                key = self.read_string()
                if len(key) == 0:
                    next_byte = self.read_u8()
                    if next_byte == 0x09: break
                    else: self.pos -= 1; continue
                val = self.read_value(); obj[key] = val
            obj['__class_name__'] = class_name
            return obj
        else:
            return f'__UNKNOWN_0x{type_marker:02x}__'

def decode_amf0_response(data):
    decoder = AMF0Decoder(data)
    version = decoder.read_u16()
    header_count = decoder.read_u16()
    for _ in range(header_count):
        decoder.read_string()  # name
        decoder.read_u8()  # must_understand
        decoder.read_u32()  # length
        decoder.read_value()  # value
    body_count = decoder.read_u16()
    result = None
    for _ in range(body_count):
        target = decoder.read_string()
        response = decoder.read_string()
        content_length = decoder.read_u32()
        value = decoder.read_value()
        result = value
    return result

# ============================================
# 方法1: 使用 typed RemotingMessage
# ============================================

def build_amf0_typed_remoting(destination, operation, args=None):
    """使用 typed object (0x10) 构造 RemotingMessage"""
    if args is None:
        args = []

    msg_id = str(uuid.uuid4())

    # body 参数数组
    body_items = b''
    for arg in args:
        if isinstance(arg, str):
            body_items += enc_str(arg)
        elif isinstance(arg, (int, float)):
            body_items += enc_num(arg)
        elif isinstance(arg, bool):
            body_items += enc_bool(arg)
        elif arg is None:
            body_items += enc_null()
        else:
            body_items += enc_null()

    body_array = b'\x0A' + struct.pack('>I', len(args)) + body_items

    # RemotingMessage as typed object
    fields = [
        ('source', enc_null()),
        ('operation', enc_str(operation)),
        ('destination', enc_str(destination)),
        ('messageId', enc_str(msg_id)),
        ('timestamp', enc_num(0.0)),
        ('timeToLive', enc_num(0.0)),
        ('body', body_array),
        ('clientId', enc_null()),
    ]

    msg = enc_typed_object('flex.messaging.messages.RemotingMessage', fields)

    # AMF0 packet
    packet = b'\x00\x00'  # version AMF0
    packet += b'\x00\x00'  # header count = 0
    packet += b'\x00\x01'  # body count = 1
    # Body
    packet += struct.pack('>H', 4) + b'null'  # target URI
    packet += struct.pack('>H', 0)  # response URI
    packet += struct.pack('>I', len(msg))  # content length
    packet += msg

    return packet

# ============================================
# 方法2: 老式 AMF0 格式 (target URI = destination.operation)
# ============================================

def build_amf0_legacy(destination, operation, args=None):
    """老式 AMF0 格式: target URI = destination.operation"""
    if args is None:
        args = []

    # body 参数数组
    body_items = b''
    for arg in args:
        if isinstance(arg, str):
            body_items += enc_str(arg)
        elif isinstance(arg, (int, float)):
            body_items += enc_num(arg)
        elif arg is None:
            body_items += enc_null()
        else:
            body_items += enc_null()

    body_array = b'\x0A' + struct.pack('>I', len(args)) + body_items

    # target URI = destination.operation
    target = f"{destination}.{operation}"

    # AMF0 packet
    packet = b'\x00\x00'  # version AMF0
    packet += b'\x00\x00'  # header count = 0
    packet += b'\x00\x01'  # body count = 1
    # Body
    target_bytes = target.encode('utf-8')
    packet += struct.pack('>H', len(target_bytes)) + target_bytes  # target URI
    packet += struct.pack('>H', 0)  # response URI
    packet += struct.pack('>I', len(body_array))  # content length
    packet += body_array

    return packet

# ============================================
# 方法3: AMF3 格式
# ============================================

def build_amf3_remoting(destination, operation, args=None):
    """AMF3 格式的 RemotingMessage"""
    # AMF3 packet with version 0x0003
    # Body is a RemotingMessage in AMF3 format
    # 这比较复杂，先跳过
    pass

# ============================================
# 测试
# ============================================

AMF_URL = 'http://172.18.36.5:8000/messagebroker/amf'

print("\n=== 方法1: Typed RemotingMessage ===")
dest = 'testPlanService'
op = 'getAll'
amf_data = build_amf0_typed_remoting(dest, op)
print(f"请求大小: {len(amf_data)} bytes")
print(f"请求 hex: {amf_data[:50].hex()}")

resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf', 'Accept': 'application/x-amf'}, timeout=10)
print(f"响应: {resp.status_code}, {len(resp.content)} bytes")
result = decode_amf0_response(resp.content)
print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")

print("\n=== 方法2: Legacy AMF0 (target=dest.op) ===")
amf_data = build_amf0_legacy(dest, op)
print(f"请求大小: {len(amf_data)} bytes")
print(f"请求 hex: {amf_data[:50].hex()}")

resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf', 'Accept': 'application/x-amf'}, timeout=10)
print(f"响应: {resp.status_code}, {len(resp.content)} bytes")
result = decode_amf0_response(resp.content)
print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")

# ============================================
# 用方法2（legacy格式）测试更多 destination
# ============================================

print("\n\n=== 用 legacy 格式测试更多 destination ===")

dests_to_test = [
    'Project', 'TestCase', 'TestPlan', 'TestRun', 'Defect', 'Bug',
    'Module', 'Requirement', 'Scenario', 'User', 'Task', 'Report',
    'TestStep', 'TestSuite', 'Execution', 'Environment', 'Build',
    'project', 'testCase', 'testPlan', 'testRun', 'defect', 'bug',
    'module', 'requirement', 'scenario', 'user', 'task', 'report',
    'projectService', 'testCaseService', 'testPlanService',
    'testRunService', 'defectService', 'bugService',
    'moduleService', 'requirementService', 'scenarioService',
    'userService', 'taskService', 'reportService',
    'ProjectService', 'TestCaseService', 'TestPlanService',
    'TestRunService', 'DefectService', 'BugService',
    'dracoProjectService', 'dracoTestCaseService',
    'dracoTestPlanService', 'dracoTestRunService',
    'dracoDefectService', 'dracoUserService',
    'dracoModuleService', 'dracoReportService',
    'dracoTaskService', 'dracoScenarioService',
    'dracoRequirementService', 'dracoTestStepService',
    'dracoTestSuiteService', 'dracoExecutionService',
    'dracoEnvironmentService', 'dracoBuildService',
    'topoService', 'dracoService', 'homeService',
    'dashboardService', 'statisticsService',
    'remoteService', 'flexService', 'commonService',
    'baseService', 'testManageService',
    'projectManager', 'defectManager', 'testcaseManager',
    'testplanManager', 'testrunManager',
]

# 用 legacy 格式测试
for dest in dests_to_test:
    amf_data = build_amf0_legacy(dest, 'getAll')
    try:
        resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf', 'Accept': 'application/x-amf'}, timeout=8)
        result = decode_amf0_response(resp.content)

        msg = ''
        if isinstance(result, dict):
            msg = str(result.get('message', ''))
            if result.get('__class_name__'):
                msg += f" [class={result['__class_name__']}]"

        # 只在不是 "No destination" 错误时打印
        if 'No destination' not in msg and 'not registered' not in msg:
            print(f"\n  ✓✓✓ {dest}.getAll: {msg[:300]}")
        else:
            # 检查 destination 是否被服务器识别
            if dest in msg:
                print(f"  {dest}: 被识别但错误: {msg[:200]}")
    except Exception as e:
        print(f"  {dest}: 错误: {e}")

# 也用 typed RemotingMessage 测试
print("\n\n=== 用 typed RemotingMessage 格式测试 ===")
for dest in dests_to_test[:30]:
    amf_data = build_amf0_typed_remoting(dest, 'getAll')
    try:
        resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf', 'Accept': 'application/x-amf'}, timeout=8)
        result = decode_amf0_response(resp.content)

        msg = ''
        if isinstance(result, dict):
            msg = str(result.get('message', ''))
            if result.get('__class_name__'):
                msg += f" [class={result['__class_name__']}]"

        if 'No destination' not in msg and 'not registered' not in msg:
            print(f"\n  ✓✓✓ {dest}.getAll: {msg[:300]}")
        else:
            if dest in msg:
                print(f"  {dest}: 被识别但错误: {msg[:200]}")
    except Exception as e:
        print(f"  {dest}: 错误: {e}")
