"""发现 AMF destination 和方法名 - 基于 userService 已知有效"""
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

# AMF0 编码
def enc_str(s):
    b = s.encode('utf-8')
    return b'\x02' + struct.pack('>H', len(b)) + b

def enc_num(n):
    return b'\x00' + struct.pack('>d', float(n))

def enc_null():
    return b'\x05'

def enc_str_arg(arg):
    if isinstance(arg, str):
        return enc_str(arg)
    elif isinstance(arg, (int, float)):
        return enc_num(arg)
    elif arg is None:
        return enc_null()
    return enc_null()

def build_amf0_legacy(destination, operation, args=None):
    if args is None:
        args = []
    body_items = b''
    for arg in args:
        body_items += enc_str_arg(arg)
    body_array = b'\x0A' + struct.pack('>I', len(args)) + body_items
    target = f"{destination}.{operation}"
    packet = b'\x00\x00\x00\x00\x00\x01'  # version 0, headers 0, bodies 1
    tb = target.encode('utf-8')
    packet += struct.pack('>H', len(tb)) + tb
    packet += struct.pack('>H', 0)
    packet += struct.pack('>I', len(body_array))
    packet += body_array
    return packet

# AMF0 解码
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
        decoder.read_string()
        decoder.read_u8()
        decoder.read_u32()
        decoder.read_value()
    body_count = decoder.read_u16()
    for _ in range(body_count):
        decoder.read_string()
        decoder.read_string()
        decoder.read_u32()
        return decoder.read_value()
    return None

def send_amf(dest, op, args=None):
    amf_data = build_amf0_legacy(dest, op, args)
    resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf', 'Accept': 'application/x-amf'}, timeout=10)
    return decode_response(resp.content)

# ============================================
# 1. 测试 userService 的方法名
# ============================================
print("\n=== 测试 userService 的方法名 ===")

user_methods = [
    # 基础方法
    'get', 'find', 'list', 'load', 'save', 'create', 'delete', 'update',
    # get 变体
    'getUser', 'getUsers', 'getUserList', 'getAllUsers',
    'getUserById', 'getUserByName', 'getUserByNameAndPassword',
    'findById', 'findByName', 'findAll', 'findAllUsers',
    'getCurrentUser', 'getLoginUser', 'getLoginInfo',
    'getInfo', 'getProfile', 'getMenu', 'getPermission',
    'getRole', 'getRoles', 'getRoleList', 'getAllRoles',
    'getProject', 'getProjects', 'getProjectList', 'getAllProjects',
    'getModule', 'getModules', 'getModuleList',
    'getTestCase', 'getTestCases', 'getTestCaseList',
    'getTestPlan', 'getTestPlans', 'getTestPlanList',
    'getTestRun', 'getTestRuns', 'getTestRunList',
    'getDefect', 'getDefects', 'getDefectList',
    'getBug', 'getBugs', 'getBugList',
    'getReport', 'getReports', 'getReportList',
    'getStatistics', 'getSummary', 'getDashboard',
    'getEnv', 'getEnvironment', 'getEnvironments',
    'getBuild', 'getBuilds', 'getBuildList',
    'getTask', 'getTasks', 'getTaskList',
    'getRequirement', 'getRequirements', 'getRequirementList',
    'getScenario', 'getScenarios', 'getScenarioList',
    'getTestStep', 'getTestSteps', 'getTestStepList',
    'getTestSuite', 'getTestSuites', 'getTestSuiteList',
    'getExecution', 'getExecutions', 'getExecutionList',
    'getOption', 'getOptions', 'getConfig', 'getConfiguration',
    'getCategory', 'getCategories', 'getPriority', 'getStatus',
    'getSeverity', 'getVersion', 'getVersions', 'getField',
    'getTree', 'getTreeData', 'getMenuTree', 'getModuleTree',
    'getById', 'getByIds', 'getByProject', 'getByModule',
    'count', 'getCount', 'countAll',
    'search', 'searchUser', 'queryUser', 'filterUser',
    'login', 'authenticate', 'logout', 'checkLogin',
    'validate', 'checkPermission', 'hasPermission',
    'getPage', 'getPaged', 'getListByPage',
    # 复合名
    'getUserProjects', 'getUserInfo', 'getUserRole',
    'getProjectInfo', 'getProjectTree', 'getProjectData',
    'getTestPlanData', 'getTestCaseData', 'getDefectData',
    'getBugData', 'getRunData', 'getReportData',
    # 中文拼音相关
    'getYonghu', 'getYonghuList', 'getXiangmu', 'getXiangmuList',
    # 极简
    'all', 'list', 'data', 'tree', 'info', 'menu',
    'home', 'index', 'main', 'default', 'init',
    'getDracoData', 'getTopoData', 'getTopoInfo',
    'loadUser', 'loadUsers', 'loadData', 'loadAll',
    'fetch', 'fetchUser', 'fetchUsers',
    'query', 'queryAll', 'queryList',
    # transmitfile 相关
    'transmitFile', 'downloadFile', 'uploadFile',
    'deleteFile', 'getAttachment', 'getAttachments',
    # 数据导出
    'export', 'exportData', 'exportExcel', 'exportReport',
    'importData', 'importExcel',
]

for method in user_methods:
    try:
        result = send_amf('userService', method)
        if isinstance(result, dict):
            msg = str(result.get('message', ''))
            code = str(result.get('code', ''))
            if 'Cannot invoke method' not in msg:
                print(f"\n  ✓✓✓ userService.{method}: {msg[:300]}")
                # 打印完整结果
                print(f"    完整: {json.dumps(result, indent=2, ensure_ascii=False, default=str)[:500]}")
    except Exception as e:
        print(f"  userService.{method}: 错误: {e}")

# ============================================
# 2. 更全面的 destination 测试
# ============================================
print("\n\n=== 全面测试 destination ===")

# 基于 userService 有效，推测其他可能用类似的命名
more_dests = [
    # xxxService 格式
    'userService', 'projectService', 'testCaseService', 'testPlanService',
    'testRunService', 'defectService', 'bugService', 'moduleService',
    'requirementService', 'scenarioService', 'taskService', 'reportService',
    'testStepService', 'testSuiteService', 'executionService',
    'environmentService', 'buildService', 'attachmentService',
    'fileService', 'commentService', 'logService', 'auditService',
    'permissionService', 'roleService', 'departmentService',
    'teamService', 'groupService', 'configService', 'systemService',
    'dashboardService', 'statisticsService', 'chartService',
    'planService', 'caseService', 'runService', 'stepService',
    'suiteService', 'categoryService', 'priorityService',
    'severityService', 'statusService', 'versionService',
    'labelService', 'tagService', 'searchService',
    'notifyService', 'notificationService', 'messageService',
    'emailService', 'smsService', 'scheduleService',
    'cacheService', 'syncService', 'dataService',
    'testService', 'qaService', 'testManageService',
    'testCaseManagerService', 'testPlanManagerService',
    'testRunManagerService', 'defectManagerService',
    'projectManagerService', 'userManagerService',
    'testStepManagerService', 'testSuiteManagerService',
    'executionManagerService', 'requirementManagerService',
    'scenarioManagerService', 'moduleManagerService',
    'taskManagerService', 'reportManagerService',
    'environmentManagerService', 'buildManagerService',
    'attachmentManagerService', 'commentManagerService',
    'topoService', 'dracoService', 'homeService',
    'portalService', 'pageService', 'layoutService',
    'menuService', 'navigationService', 'sidebarService',
    'filterService', 'sortService', 'exportService',
    'importService', 'printService', 'historyService',
    'versionControlService', 'changeService',
    'relationService', 'dependencyService', 'linkService',
    'referenceService', 'treeService', 'gridService',
    'formService', 'dialogService', 'windowService',
    'tabService', 'panelService', 'cardService',
    'workflowService', 'processService', 'flowService',
    'approvalService', 'reviewService', 'confirmService',
    # 单词格式
    'user', 'project', 'testCase', 'testPlan', 'testRun',
    'defect', 'bug', 'module', 'requirement', 'scenario',
    'task', 'report', 'testStep', 'testSuite', 'execution',
    'environment', 'build', 'attachment', 'file', 'comment',
    'log', 'audit', 'permission', 'role', 'department',
    'team', 'group', 'config', 'system', 'dashboard',
    'statistics', 'chart', 'plan', 'case', 'run',
    'step', 'suite', 'category', 'priority', 'severity',
    'status', 'version', 'label', 'tag', 'search',
    'notify', 'notification', 'message', 'email', 'schedule',
    'cache', 'sync', 'data', 'test', 'qa',
    'topo', 'draco', 'home', 'portal', 'page',
    'menu', 'navigation', 'filter', 'sort', 'export',
    'print', 'history', 'relation', 'dependency', 'tree',
    'grid', 'form', 'dialog', 'window', 'tab',
    'panel', 'card', 'workflow', 'process', 'approval',
    'review', 'confirm',
    # 下划线格式
    'user_service', 'project_service', 'test_case_service',
    'test_plan_service', 'test_run_service', 'defect_service',
    # 其他可能
    'flexService', 'amfService', 'remotingService',
    'messageService', 'brokerService', 'channelService',
    'endpointService', 'gatewayService', 'servletService',
    'remoteObjectService', 'remoteService',
    'dataService', 'dataSourceService', 'queryService',
    'crudService', 'repositoryService', 'daoService',
    'mapperService', 'entityService', 'modelService',
    'voService', 'dtoService', 'boService',
    'facadeService', 'delegateService', 'proxyService',
    'interceptorService', 'filterService', 'handlerService',
    'controllerService', 'actionService',
]

valid_dests = []
for dest in more_dests:
    try:
        result = send_amf(dest, 'getAll')
        if isinstance(result, dict):
            msg = str(result.get('message', ''))
            if 'No destination' not in msg:
                print(f"  ✓ {dest}: {msg[:200]}")
                valid_dests.append(dest)
    except Exception as e:
        pass

print(f"\n有效的 destination: {valid_dests}")

# ============================================
# 3. 如果找到有效 destination，测试方法名
# ============================================
if valid_dests:
    print(f"\n\n=== 测试有效 destination 的方法名 ===")
    for dest in valid_dests:
        print(f"\n--- {dest} ---")
        methods_to_test = [
            'getAll', 'getList', 'findAll', 'loadAll', 'get', 'find', 'list',
            'getById', 'findById', 'getByName', 'findByName',
            'getProject', 'getProjects', 'getProjectList', 'getAllProjects',
            'getTestCase', 'getTestCases', 'getTestCaseList',
            'getTestPlan', 'getTestPlans', 'getTestPlanList',
            'getTestRun', 'getTestRuns', 'getTestRunList',
            'getDefect', 'getDefects', 'getDefectList',
            'getBug', 'getBugs', 'getBugList',
            'getModule', 'getModules', 'getModuleList',
            'getRequirement', 'getRequirements', 'getRequirementList',
            'getScenario', 'getScenarios', 'getScenarioList',
            'getTask', 'getTasks', 'getTaskList',
            'getReport', 'getReports', 'getReportList',
            'getTestStep', 'getTestSteps', 'getTestStepList',
            'getTestSuite', 'getTestSuites', 'getTestSuiteList',
            'getExecution', 'getExecutions', 'getExecutionList',
            'getEnvironment', 'getEnvironments', 'getEnvironmentList',
            'getBuild', 'getBuilds', 'getBuildList',
            'getAttachment', 'getAttachments', 'getAttachmentList',
            'getComment', 'getComments', 'getCommentList',
            'getLog', 'getLogs', 'getLogList',
            'getUser', 'getUsers', 'getUserList',
            'getRole', 'getRoles', 'getRoleList',
            'getPermission', 'getPermissions', 'getPermissionList',
            'getDepartment', 'getDepartments', 'getDepartmentList',
            'getCategory', 'getCategories', 'getCategoryList',
            'getPriority', 'getPriorities', 'getPriorityList',
            'getSeverity', 'getSeverities', 'getSeverityList',
            'getStatus', 'getStatuses', 'getStatusList',
            'getVersion', 'getVersions', 'getVersionList',
            'getConfig', 'getConfiguration', 'getSystemConfig',
            'getMenu', 'getMenuTree', 'getNavigation',
            'getTree', 'getTreeData', 'getTreeList',
            'getInfo', 'getDetail', 'getSummary',
            'getStatistics', 'getDashboard', 'getChartData',
            'getOption', 'getOptions', 'getField',
            'getById', 'getByIds', 'getByProjectId',
            'count', 'getCount', 'countAll',
            'search', 'query', 'filter',
            'export', 'import', 'download', 'upload',
            'create', 'update', 'delete', 'save',
            'login', 'authenticate', 'logout',
            'getTopoData', 'getDracoData',
            'getTestPlanData', 'getTestCaseData', 'getDefectData',
            'getProjectData', 'getRunData', 'getReportData',
            'getUserData', 'getModuleData', 'getTaskData',
            'getPage', 'getPaged', 'getListByPage',
            'getByPage', 'getWithPagination',
            'all', 'data', 'tree', 'info', 'menu', 'home',
            'index', 'main', 'default', 'init',
            'load', 'loadData', 'loadList', 'loadAll',
            'fetch', 'fetchList',
        ]
        for method in methods_to_test:
            try:
                result = send_amf(dest, method)
                if isinstance(result, dict):
                    msg = str(result.get('message', ''))
                    if 'Cannot invoke method' not in msg:
                        print(f"\n  ✓✓✓ {dest}.{method}: {msg[:300]}")
                        print(f"    {json.dumps(result, indent=2, ensure_ascii=False, default=str)[:500]}")
            except Exception as e:
                pass
