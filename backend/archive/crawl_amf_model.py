"""用模型名作为 destination，查询名作为方法名测试 AMF"""
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

AMF_URL = 'http://172.18.36.5:8000/messagebroker/amf'

def enc_str(s):
    b = s.encode('utf-8')
    return b'\x02' + struct.pack('>H', len(b)) + b

def enc_num(n):
    return b'\x00' + struct.pack('>d', float(n))

def enc_null():
    return b'\x05'

def enc_bool(b):
    return b'\x01' + (b'\x01' if b else b'\x00')

def enc_strict_array(items):
    data = b'\x0A' + struct.pack('>I', len(items))
    for item in items:
        if isinstance(item, str):
            data += enc_str(item)
        elif isinstance(item, (int, float)):
            data += enc_num(item)
        elif isinstance(item, bool):
            data += enc_bool(item)
        elif item is None:
            data += enc_null()
        else:
            data += enc_null()
    return data

def enc_object(fields):
    data = b'\x03'
    for key, value in fields:
        kb = key.encode('utf-8')
        data += struct.pack('>H', len(kb)) + kb
        data += value
    data += b'\x00\x00\x09'
    return data

def build_amf(dest, op, args=None):
    if args is None:
        args = []
    body_array = enc_strict_array(args)
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
    version = decoder.read_u16()
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
    resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf', 'Accept': 'application/x-amf'}, timeout=15)
    return decode_response(resp.content)

def check_result(dest, op, args=None):
    try:
        result = send_amf(dest, op, args)
        if isinstance(result, dict):
            msg = str(result.get('message', ''))
            code = str(result.get('code', ''))
            if 'No destination' in msg:
                return 'no_dest', msg
            elif 'Cannot invoke method' in msg:
                return 'no_method', msg
            else:
                return 'other_error', msg
        elif isinstance(result, list):
            return 'data', f"Array({len(result)} items)"
        elif result is None:
            return 'null', 'null'
        else:
            return 'data', str(result)[:300]
    except Exception as e:
        return 'exception', str(e)

# ============================================
# 1. 测试模型名作为 destination
# ============================================
print("=== 1. 测试模型名作为 destination ===")

models = [
    'project', 'dmTask', 'dmBug', 'dmRequirement', 'dmTestSuite',
    'dmTestCase', 'dmTestRun', 'dmTestCaseRun', 'dmVersion', 'dmBuild',
    'dmRelease', 'dmRisk', 'dmIssue', 'dmDocReview', 'dmCodeReview',
    'dmReport', 'dmProjectReport', 'dmMeetingNotes', 'dmBudget',
    'dmCosts', 'dmPhase', 'dmBaseline', 'dmReview',
    'dmRequirementFolder', 'dmSpecification', 'dmTaskDependency',
    'dmVersionPhase', 'workCalendar',
    'projectFinishReview', 'projectFoundReview',
]

for model in models:
    status, msg = check_result(model, 'all')
    if status != 'no_dest':
        print(f"  ✓ {model}.all: [{status}] {msg[:200]}")

# ============================================
# 2. 测试通用方法名 (在已知有效的 destination 上)
# ============================================
print("\n=== 2. 测试通用方法名 (在已知 destination 上) ===")

# 基于XML中发现的action和query名
generic_methods = [
    # 基础CRUD
    'query', 'find', 'get', 'load', 'save', 'create', 'delete', 'update',
    'count', 'search', 'list', 'all',
    # 基于XML action名
    'createEntity', 'queryEntity', 'loadEntity', 'updateEntity', 'deleteEntity',
    'queryModel', 'loadModel', 'getModel', 'findModel',
    'queryData', 'loadData', 'getData', 'findData',
    # 基于XML query名
    'getNamedQuery', 'executeQuery', 'runQuery', 'namedQuery',
    # 批量操作
    'findAll', 'getAll', 'getList', 'getById', 'findById',
    'getEntity', 'findEntity', 'loadEntity',
    # 数据操作
    'getEntityList', 'getEntityData', 'getEntityById',
    'getProjectList', 'getProjectData', 'getProjectById',
    'getBugList', 'getBugData', 'getBugById',
    'getTaskList', 'getTaskData', 'getTaskById',
    'getTestCaseList', 'getTestCaseData',
    'getTestRunList', 'getTestRunData',
    # 导出
    'export', 'exportData', 'exportExcel', 'exportReport',
    # 用户相关
    'getCurrentUser', 'getLoginUser', 'getLoginInfo',
    'getUserInfo', 'getUserProjects', 'getUserRole',
    'getPermission', 'getMenu', 'getMenuTree',
    'getRole', 'getRoles', 'getRoleList',
    'getDepartment', 'getDepartments',
    # 文件相关
    'upload', 'download', 'getAttachment', 'getAttachments',
    'transmitFile', 'transmitfile',
    # 布局相关
    'getLayout', 'getLayouts', 'getTemplate',
    # 消息相关
    'getMessage', 'getMessages', 'send', 'receive',
    # 系统相关
    'getSystemInfo', 'getSystemConfig', 'getVersion',
    # 统计
    'getStatistics', 'getSummary', 'getDashboard',
    'statView', 'getStatView',
    # AMF特定
    'ping', 'echo', 'test',
    # 拼音命名
    'chaxun', 'huoqu', 'jiazai', 'baocun', 'xinzeng', 'shanchu', 'xiugai',
    # 其他
    'login', 'authenticate', 'validate', 'checkPermission',
    'getNavTree', 'getNav', 'getTree', 'getTreeNode',
    'getWorkPanel', 'getQueryPanel', 'getNavPanel',
    'getDataModel', 'getModelConfig', 'getSchema',
    'getModuleConfig', 'getModuleInfo',
    'getHomePage', 'getHomeData', 'getTopoData',
    'getDracoData', 'getDracoInfo',
    'getConfig', 'getSettings', 'getProperties',
    'getProjects', 'getTasks', 'getBugs', 'getRequirements',
    'getTestCases', 'getTestRuns', 'getTestSuites',
    'getTestSteps', 'getExecutions', 'getEnvironments',
    'getBuilds', 'getReleases', 'getReports',
    'getUsers', 'getRoles', 'getPermissions',
    'getDepartments', 'getTeams', 'getGroups',
    'getCategories', 'getPriorities', 'getSeverities',
    'getStatuses', 'getVersions', 'getFields',
    'getOptions', 'getSettings', 'getParameters',
]

for dest in ['userService', 'fileService', 'roleService', 'messageService', 'layoutService']:
    found = False
    for method in generic_methods:
        status, msg = check_result(dest, method)
        if status not in ['no_method', 'no_dest', 'exception', 'null']:
            print(f"\n  ✓✓✓ {dest}.{method}: [{status}] {msg[:300]}")
            found = True
        elif status == 'no_method' and not found:
            # 只在方法被识别但无法调用时打印
            pass
    if not found:
        print(f"  {dest}: 未找到有效方法名")

# ============================================
# 3. 在已知destination上用参数测试
# ============================================
print("\n=== 3. 用参数测试方法 ===")

# 也许方法需要参数 (如模型名)
for dest in ['userService', 'fileService', 'roleService', 'messageService', 'layoutService']:
    for method in ['query', 'find', 'get', 'load', 'search', 'list']:
        # 带参数测试
        for arg in ['project', 'all', 'todo', 'dmBug', 'dmTask', 'getProject', '1']:
            status, msg = check_result(dest, method, [arg])
            if status not in ['no_method', 'no_dest', 'exception']:
                print(f"  {dest}.{method}('{arg}'): [{status}] {msg[:200]}")

# ============================================
# 4. 测试更多 destination 候选
# ============================================
print("\n=== 4. 测试更多 destination 候选 ===")

more_dests = [
    'dataService', 'entityService', 'modelService', 'crudService',
    'devMngService', 'devMng', 'projectService',
    'dmBugService', 'dmTaskService', 'dmTestCaseService',
    'dmTestRunService', 'dmRequirementService',
    'homeService', 'navService', 'workPanelService',
    'queryService', 'searchService', 'filterService',
    'treeService', 'gridService', 'formService',
    'attachmentService', 'commentService',
    'permissionService', 'departmentService',
    'teamService', 'groupService',
    'statisticsService', 'chartService',
    'scheduleService', 'calendarService',
    'historyService', 'versionService',
    'logService', 'auditService',
    'configService', 'systemService',
    'dashboardService', 'reportService',
    'taskService', 'planService',
    'testService', 'caseService',
    'runService', 'stepService',
    'suiteService', 'executionService',
    'defectService', 'bugService',
    'moduleService', 'requirementService',
    'scenarioService', 'environmentService',
    'buildService', 'releaseService',
    'riskService', 'issueService',
    'reviewService', 'baselineService',
    'phaseService', 'versionService',
    'specificationService', 'folderService',
    'costService', 'budgetService',
    'workCalendarService', 'workLogService',
    'meetingNotesService', 'projectReportService',
    'codeReviewService', 'docReviewService',
    'topoDataService', 'topoEntityService',
    'topoModelService', 'topoCrudService',
    'dracoDataService', 'dracoEntityService',
    'dracoModelService', 'dracoCrudService',
    'flexDataService', 'flexEntityService',
    'remoteDataService', 'remoteEntityService',
    'baseDataService', 'baseEntityService',
    'commonService', 'baseService',
    'remoteService', 'flexService',
    'amfService', 'remotingService',
    'brokerService', 'gatewayService',
    'servletService', 'endpointService',
    'repositoryService', 'daoService',
    'mapperService', 'entityManagerService',
    'sessionService', 'transactionService',
]

for dest in more_dests:
    status, msg = check_result(dest, 'getAll')
    if status != 'no_dest':
        print(f"  ✓ {dest}: [{status}] {msg[:200]}")
