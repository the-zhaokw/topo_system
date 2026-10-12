"""解码 AMF0 响应，提取错误信息，找出正确的 destination 名"""
import requests as req
import struct
import re
import zlib
import uuid

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
# AMF0 解码器
# ============================================

class AMF0Decoder:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read_u8(self):
        v = self.data[self.pos]
        self.pos += 1
        return v

    def read_u16(self):
        v = struct.unpack('>H', self.data[self.pos:self.pos+2])[0]
        self.pos += 2
        return v

    def read_u32(self):
        v = struct.unpack('>I', self.data[self.pos:self.pos+4])[0]
        self.pos += 4
        return v

    def read_double(self):
        v = struct.unpack('>d', self.data[self.pos:self.pos+8])[0]
        self.pos += 8
        return v

    def read_string(self):
        length = self.read_u16()
        s = self.data[self.pos:self.pos+length].decode('utf-8', errors='replace')
        self.pos += length
        return s

    def read_long_string(self):
        length = self.read_u32()
        s = self.data[self.pos:self.pos+length].decode('utf-8', errors='replace')
        self.pos += length
        return s

    def read_value(self):
        type_marker = self.read_u8()
        if type_marker == 0x00:  # number
            return self.read_double()
        elif type_marker == 0x01:  # boolean
            return self.read_u8() != 0
        elif type_marker == 0x02:  # string
            return self.read_string()
        elif type_marker == 0x03:  # object
            obj = {}
            while True:
                key = self.read_string()
                if len(key) == 0:
                    next_byte = self.read_u8()
                    if next_byte == 0x09:  # end marker
                        break
                    else:
                        self.pos -= 1
                        continue
                val = self.read_value()
                obj[key] = val
            return obj
        elif type_marker == 0x05:  # null
            return None
        elif type_marker == 0x06:  # undefined
            return None
        elif type_marker == 0x08:  # mixed array (ecma array)
            count = self.read_u32()
            obj = {}
            for _ in range(count):
                key = self.read_string()
                val = self.read_value()
                obj[key] = val
            # 读到 end marker
            while True:
                key = self.read_string()
                if len(key) == 0:
                    next_byte = self.read_u8()
                    if next_byte == 0x09:
                        break
                    else:
                        self.pos -= 1
                        continue
                val = self.read_value()
                obj[key] = val
            return obj
        elif type_marker == 0x09:  # end marker
            return '__END__'
        elif type_marker == 0x0A:  # strict array
            count = self.read_u32()
            arr = []
            for _ in range(count):
                arr.append(self.read_value())
            return arr
        elif type_marker == 0x0B:  # date
            return self.read_double()
        elif type_marker == 0x0C:  # long string
            return self.read_long_string()
        elif type_marker == 0x0D:  # unsupported
            return '__UNSUPPORTED__'
        elif type_marker == 0x10:  # typed object (AMF0)
            class_name = self.read_string()
            obj = {}
            while True:
                key = self.read_string()
                if len(key) == 0:
                    next_byte = self.read_u8()
                    if next_byte == 0x09:
                        break
                    else:
                        self.pos -= 1
                        continue
                val = self.read_value()
                obj[key] = val
            obj['__class_name__'] = class_name
            return obj
        else:
            print(f"  未知类型标记: 0x{type_marker:02x} at pos {self.pos-1}")
            return f'__UNKNOWN_0x{type_marker:02x}__'

def decode_amf0_response(data):
    """解码 AMF0 响应"""
    decoder = AMF0Decoder(data)
    version = decoder.read_u16()
    print(f"AMF 版本: 0x{version:04x}")

    # Headers
    header_count = decoder.read_u16()
    print(f"Headers: {header_count}")
    for i in range(header_count):
        name = decoder.read_string()
        must_understand = decoder.read_u8()
        length = decoder.read_u32()
        value = decoder.read_value()
        print(f"  Header {name}: {value}")

    # Bodies
    body_count = decoder.read_u16()
    print(f"Bodies: {body_count}")
    for i in range(body_count):
        target = decoder.read_string()
        response = decoder.read_string()
        length = decoder.read_u32()
        value = decoder.read_value()
        print(f"  Body target={target}, response={response}")
        print(f"  Value: {value}")
        return value

# ============================================
# 构造 AMF0 请求
# ============================================

def build_amf0_request(destination, operation, args=None):
    """构造完整的 AMF0 HTTP 请求体"""
    if args is None:
        args = []

    msg_id = str(uuid.uuid4())
    timestamp = 0.0

    # body 参数数组
    body_content = b'\x0A' + struct.pack('>I', len(args))
    for arg in args:
        if isinstance(arg, str):
            encoded = arg.encode('utf-8')
            body_content += b'\x02' + struct.pack('>H', len(encoded)) + encoded
        elif isinstance(arg, (int, float)):
            body_content += b'\x00' + struct.pack('>d', float(arg))
        elif isinstance(arg, bool):
            body_content += b'\x01' + (b'\x01' if arg else b'\x00')
        elif arg is None:
            body_content += b'\x05'
        else:
            body_content += b'\x05'

    # RemotingMessage object
    def str_val(s):
        encoded = s.encode('utf-8')
        return b'\x02' + struct.pack('>H', len(encoded)) + encoded

    def num_val(n):
        return b'\x00' + struct.pack('>d', float(n))

    def null_val():
        return b'\x05'

    fields = [
        (b'source', null_val()),
        (b'operation', str_val(operation)),
        (b'destination', str_val(destination)),
        (b'messageId', str_val(msg_id)),
        (b'timestamp', num_val(timestamp)),
        (b'timeToLive', num_val(0.0)),
        (b'body', body_content),
        (b'clientId', null_val()),
    ]

    msg_obj = b'\x03'  # object type
    for key, value in fields:
        msg_obj += struct.pack('>H', len(key))
        msg_obj += key
        msg_obj += value
    msg_obj += b'\x00\x00\x09'  # end marker

    # AMF0 packet
    packet = b'\x00\x00'  # version AMF0
    packet += b'\x00\x00'  # header count = 0
    packet += b'\x00\x01'  # body count = 1

    # Body
    target = b'null'
    packet += struct.pack('>H', len(target))
    packet += target
    packet += struct.pack('>H', 0)  # response URI empty
    packet += struct.pack('>I', len(msg_obj))  # content length
    packet += msg_obj

    return packet

# ============================================
# 测试 AMF 请求
# ============================================

print("\n=== 解码 AMF 错误响应 ===")

# 发送一个测试请求并解码完整响应
dest = 'testPlanService'
op = 'getAll'
amf_data = build_amf0_request(dest, op)
resp = session.post(
    'http://172.18.36.5:8000/messagebroker/amf',
    data=amf_data,
    headers={'Content-Type': 'application/x-amf', 'Accept': 'application/x-amf'},
    timeout=10
)

print(f"\n请求: {dest}.{op}()")
print(f"响应: {resp.status_code}, {len(resp.content)} bytes")
print(f"Content-Type: {resp.headers.get('content-type', '')}")

# 解码响应
print("\n解码 AMF 响应:")
try:
    result = decode_amf0_response(resp.content)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
except Exception as e:
    print(f"解码错误: {e}")
    print(f"原始 hex: {resp.content[:100].hex()}")
    # 手动提取字符串
    strs = re.findall(rb'[\x20-\x7e]{4,}', resp.content)
    print(f"所有字符串:")
    for s in strs:
        print(f"  {s.decode('ascii', errors='ignore')}")

# ============================================
# 尝试更多 destination 名
# ============================================

print("\n\n=== 尝试更多 destination 名 ===")

# 可能的命名模式: DracoProject, dracoProject, topoProject, projectService, Project 等
more_dests = [
    # 大写开头
    'Project', 'TestCase', 'TestPlan', 'TestRun', 'Defect', 'Bug',
    'Module', 'Requirement', 'Scenario', 'User', 'Task', 'Report',
    'TestStep', 'TestSuite', 'Execution', 'Environment', 'Build',
    # 小写开头
    'project', 'testCase', 'testPlan', 'testRun', 'defect', 'bug',
    'module', 'requirement', 'scenario', 'user', 'task', 'report',
    # Service 后缀
    'projectService', 'testCaseService', 'testPlanService',
    'testRunService', 'defectService', 'bugService',
    'moduleService', 'requirementService', 'scenarioService',
    'userService', 'taskService', 'reportService',
    # 大写 Service 后缀
    'ProjectService', 'TestCaseService', 'TestPlanService',
    'TestRunService', 'DefectService', 'BugService',
    # 其他常见命名
    'topoService', 'topoProject', 'dracoService', 'dracoProject',
    'homeService', 'dashboardService', 'statisticsService',
    'testService', 'caseService', 'planService', 'runService',
    'RemoteService', 'RemoteObject', 'RemoteObjectService',
    'FlexService', 'CommonService', 'BaseService',
    'TestManageService', 'TestManage', 'TMService',
    'projectManagerService', 'projectManager',
    'defectManagerService', 'defectManager',
    'testcaseManagerService', 'testcaseManager',
    'testplanManagerService', 'testplanManager',
    'testrunManagerService', 'testrunManager',
    # 极简命名
    'ps', 'ts', 'tc', 'tp', 'tr', 'df', 'bg', 'md', 'rq',
    # 其他
    'IfaceFlexService', 'IFlexService', 'FlexServiceImpl',
    'Service', 'service', 'ServiceBean', 'serviceBean',
    'remoteService', 'remoteObject',
    'dracoTestCaseService', 'dracoTestPlanService',
    'dracoDefectService', 'dracoProjectService',
    'dracoUserService', 'dracoModuleService',
    'dracoTestRunService', 'dracoTestStepService',
    'dracoTestSuiteService', 'dracoExecutionService',
    'dracoEnvironmentService', 'dracoBuildService',
    'dracoReportService', 'dracoTaskService',
    'dracoScenarioService', 'dracoRequirementService',
]

tested = set()
for dest in more_dests:
    if dest in tested:
        continue
    tested.add(dest)

    for op in ['getAll', 'getList', 'findAll', 'loadAll', 'getProjects', 'getProjectList']:
        amf_data = build_amf0_request(dest, op)
        try:
            resp = session.post(
                'http://172.18.36.5:8000/messagebroker/amf',
                data=amf_data,
                headers={'Content-Type': 'application/x-amf', 'Accept': 'application/x-amf'},
                timeout=8
            )
            body = resp.content
            # 解码响应看是否为错误
            decoder = AMF0Decoder(body)
            version = decoder.read_u16()
            header_count = decoder.read_u16()
            # skip headers
            for _ in range(header_count):
                decoder.read_string()  # name
                decoder.read_u8()  # must_understand
                decoder.read_u32()  # length
                decoder.read_value()  # value
            body_count = decoder.read_u16()
            target_uri = decoder.read_string()
            response_uri = decoder.read_string()
            content_length = decoder.read_u32()
            value = decoder.read_value()

            # 检查是否为错误
            is_error = False
            error_msg = ''
            if isinstance(value, dict):
                class_name = value.get('__class_name__', '')
                if 'ErrorMessage' in class_name or 'Fault' in class_name:
                    is_error = True
                    error_msg = str(value.get('faultString', ''))
                    fault_detail = str(value.get('faultDetail', ''))
                    if fault_detail:
                        error_msg += f" | Detail: {fault_detail[:200]}"
                elif value is not None and not is_error:
                    print(f"\n  ✓ {dest}.{op}(): 成功!")
                    print(f"    {value}")

            if is_error:
                # 只在错误信息不同时才打印
                if 'No destination' not in str(error_msg) and 'not found' not in str(error_msg).lower():
                    print(f"\n  {dest}.{op}(): 特殊错误: {error_msg[:200]}")
                elif len(tested) <= 5:  # 前几个打印详细信息
                    print(f"  {dest}.{op}(): {error_msg[:150]}")

            break  # 只测一个操作
        except Exception as e:
            print(f"  {dest}: 解码失败: {e}")
            break

# ============================================
# 也尝试 schema.def 文件
# ============================================
print("\n\n=== 获取 schema.def ===")
r = session.get('http://172.18.36.5:8000/html/client/schema.def', timeout=30)
print(f"状态: {r.status_code}, 大小: {len(r.content)} bytes")
if r.status_code == 200:
    print(f"Header: {r.content[:20]}")
    # 可能是加密的
    all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', r.content)]
    print(f"字符串数: {len(all_strs)}")
    for s in sorted(set(all_strs))[:50]:
        print(f"  {s}")
