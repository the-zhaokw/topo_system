"""根据 schema ZIP 中的查询名测试 AMF 方法"""
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
    decoder.read_u16()  # version
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
    resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf'}, timeout=10)
    return decode_response(resp.content)

def test(dest, op, args=None):
    try:
        result = send_amf(dest, op, args)
        if isinstance(result, dict):
            msg = str(result.get('message', ''))
            if 'No destination' in msg:
                return 'NO_DEST'
            elif 'Cannot invoke method' in msg:
                return 'NO_METHOD'
            else:
                return f'OTHER: {msg[:200]}'
        elif isinstance(result, list):
            return f'DATA: Array({len(result)})'
        elif result is None:
            return 'NULL'
        else:
            return f'DATA: {str(result)[:200]}'
    except Exception as e:
        return f'ERR: {e}'

# ============================================
# 1. 在已知 destination 上用 XML 中的 query 名作为方法名
# ============================================
print("=== 1. 在已知 destination 上用 XML query 名作为方法名 ===")

query_names = [
    'all', 'todo', 'toAssign', 'allOpen', 'ownerByMe',
    'meAsOwner', 'planning', 'testing', 'allOpened', 'allPublished',
    'composedByMe', 'organizedByMe', 'participatedByMe', 'allAboutMe',
    'allRegistered', 'allAsOwner', 'confirm', 'toDo',
    'createEntity', 'queryEntity', 'loadEntity', 'updateEntity', 'deleteEntity',
    'getEntity', 'findEntity', 'saveEntity',
    'query', 'get', 'find', 'load', 'create', 'update', 'delete', 'save',
    'list', 'data', 'info', 'tree', 'menu', 'home', 'init',
    'getProject', 'getProjects', 'getProjectList', 'getProjectData',
    'getBug', 'getBugs', 'getBugList', 'getBugData',
    'getTask', 'getTasks', 'getTaskList', 'getTaskData',
    'getTestCase', 'getTestCases', 'getTestCaseList',
    'getTestRun', 'getTestRuns', 'getTestRunList',
    'getDmBug', 'getDmTask', 'getDmTestCase',
    'getRequirement', 'getRequirements',
    'getOrganization', 'getOrganizations', 'getOrg', 'getOrgs',
    'getDepartment', 'getDepartments',
    'getUser', 'getUsers', 'getUserList', 'getCurrentUser', 'getLoginUser',
    'getRole', 'getRoles', 'getRoleList',
    'getPermission', 'getPermissions',
    'getMenu', 'getMenuTree', 'getNavigation', 'getNavTree',
    'getLayout', 'getLayouts', 'getTemplate',
    'getMessage', 'getMessages',
    'getWorkLog', 'getWorkLogs', 'getWorkLogList',
    'getHomePage', 'getHomeData', 'getTopoData', 'getDracoData',
    'getNav', 'getNavPanel', 'getWorkPanel', 'getQueryPanel',
    'getDataModel', 'getModelConfig', 'getSchema', 'getModuleConfig',
    'getVersion', 'getSystemInfo', 'getSystemConfig',
    'getStatistics', 'getSummary', 'getDashboard',
    'export', 'exportData', 'exportExcel',
    'login', 'authenticate', 'validate',
    'ping', 'echo', 'test',
    'getAll', 'findAll', 'loadAll', 'findById', 'getById',
    'count', 'getCount', 'countAll', 'search', 'filter',
    'getStatView', 'getNamedQuery', 'executeQuery', 'runQuery',
    'namedQuery', 'getEntityList', 'getEntityData', 'getEntityById',
    'getByProject', 'getByOrg', 'getByOrganization',
    'getBugByProject', 'getBugByOrg', 'getBugByOrganization',
    'getBugsByProject', 'getBugsByOrg', 'getBugsByOrganization',
    'getProjectBug', 'getProjectBugs', 'getProjectBugList',
    'getOrgBug', 'getOrgBugs', 'getOrgBugList',
    'getOrganizationBug', 'getOrganizationBugs',
    'getRTN', 'getRTNBugs', 'getRTNOrg',
    'loadData', 'loadList', 'loadEntity', 'loadModel',
    'fetch', 'fetchData', 'fetchList',
    'getEntityPage', 'getPage', 'getPaged',
    'getListByPage', 'getWithPagination',
]

known_dests = ['userService', 'fileService', 'roleService', 'messageService', 'layoutService', 'workLogService']

for dest in known_dests:
    print(f"\n--- {dest} ---")
    found_any = False
    for method in query_names:
        result = test(dest, method)
        if result not in ['NO_METHOD', 'NO_DEST', 'NULL']:
            print(f"  ✓✓✓ {dest}.{method}: {result}")
            found_any = True
    if not found_any:
        # 也试带参数
        for method in ['query', 'get', 'find', 'load', 'list', 'search', 'getEntity', 'queryEntity']:
            for arg in ['project', 'dmBug', 'dmTask', 'all', 'todo', '1', 'RTN']:
                result = test(dest, method, [arg])
                if result not in ['NO_METHOD', 'NO_DEST', 'NULL']:
                    print(f"  ✓✓✓ {dest}.{method}('{arg}'): {result}")
                    found_any = True
        if not found_any:
            print(f"  (未找到有效方法)")

# ============================================
# 2. 模型名 + query 名组合 (destination.operation)
# ============================================
print("\n=== 2. 模型名 + query 名组合 ===")

models = ['project', 'dmBug', 'dmTask', 'dmTestCase', 'dmTestRun', 'dmTestSuite',
          'dmRequirement', 'dmVersion', 'dmBuild', 'dmRelease', 'dmRisk', 'dmIssue',
          'dmReport', 'dmProjectReport', 'dmMeetingNotes', 'dmBudget', 'dmCosts',
          'dmCodeReview', 'dmDocReview', 'dmReview', 'dmBaseline', 'dmPhase',
          'dmSpecification', 'dmRequirementFolder', 'dmTestCaseRun',
          'dmTaskDependency', 'dmVersionPhase', 'workCalendar',
          'projectFinishReview', 'projectFoundReview']

queries = ['all', 'todo', 'toAssign', 'allOpen', 'ownerByMe', 'meAsOwner',
           'planning', 'testing', 'allOpened', 'allPublished', 'allRegistered',
           'allAsOwner', 'confirm', 'toDo', 'composedByMe', 'organizedByMe',
           'participatedByMe', 'allAboutMe', 'createEntity', 'queryEntity',
           'loadEntity', 'get', 'find', 'load', 'list', 'data', 'tree',
           'getEntity', 'query', 'getAll', 'findAll', 'getProject', 'getBug',
           'getTask', 'getTestCase', 'getTestRun', 'getRequirement']

for model in models:
    for query in queries:
        result = test(model, query)
        if result not in ['NO_DEST', 'NO_METHOD', 'NULL']:
            print(f"  ✓✓✓ {model}.{query}: {result}")

# ============================================
# 3. 模型名 + "Service" 后缀 + 方法名
# ============================================
print("\n=== 3. 模型名+Service 后缀 ===")
model_services = [m + 'Service' for m in models] + [m.lower() + 'Service' for m in models]

for dest in model_services:
    result = test(dest, 'getAll')
    if result != 'NO_DEST':
        print(f"  ✓ {dest}: {result}")
        # 找到有效 destination 后测试更多方法
        for method in ['all', 'todo', 'getBug', 'getProject', 'getEntity', 'query', 'get']:
            result2 = test(dest, method)
            if result2 not in ['NO_METHOD', 'NO_DEST']:
                print(f"    {dest}.{method}: {result2}")

# ============================================
# 4. 尝试 BlazeDS 特定方法名
# ============================================
print("\n=== 4. BlazeDS 特定方法名 ===")

blaze_methods = [
    # BlazeDS 服务器管理
    'getFlexClient', 'setFlexClient',
    'subscribe', 'unsubscribe', 'poll',
    'push', 'send', 'publish',
    # 常见 Java 方法名
    'doQuery', 'doFind', 'doGet', 'doList',
    'execute', 'invoke', 'process', 'handle',
    'getData', 'getItems', 'getRecords',
    'fetchData', 'fetchItems', 'fetchRecords',
    # 事务相关
    'begin', 'commit', 'rollback',
    # 通用
    'getModule', 'getModuleData', 'getModuleConfig',
    'getModuleInfo', 'getModuleList',
    'getModel', 'getModelData', 'getModelConfig',
    'getModelInfo', 'getModelList',
    'getSchema', 'getDefinition', 'getDefinitionList',
    'getEntity', 'getEntities', 'getEntityList',
    'findEntity', 'findEntities',
    'loadEntity', 'loadEntities',
    'queryEntity', 'queryEntities',
    'saveEntity', 'createEntity', 'updateEntity', 'deleteEntity',
    'getEntityById', 'findEntityById',
    'getEntityByQuery', 'queryByNamedQuery',
    'getByNamedQuery', 'executeNamedQuery',
    'namedQuery', 'getNamedQuery',
    'getNamedQueryResult', 'getNamedQueryResults',
]

for dest in known_dests:
    for method in blaze_methods:
        result = test(dest, method)
        if result not in ['NO_METHOD', 'NO_DEST']:
            print(f"  ✓✓✓ {dest}.{method}: {result}")

# ============================================
# 5. 尝试发送空方法名
# ============================================
print("\n=== 5. 尝试空/特殊方法名 ===")

special_methods = ['', ' ', '_', '__init__', '__str__', 'toString',
                   'getClass', 'hashCode', 'equals', 'clone',
                   'notify', 'notifyAll', 'wait',
                   'getClass', 'main', 'run']

for dest in known_dests[:2]:
    for method in special_methods:
        result = test(dest, method)
        if result not in ['NO_METHOD', 'NO_DEST', 'NULL']:
            print(f"  {dest}.{repr(method)}: {result}")
