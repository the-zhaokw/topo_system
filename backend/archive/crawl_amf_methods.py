"""解码 getClass 响应，并用大量常见 Java 方法名测试"""
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
    return resp.content, decode_response(resp.content)

# ============================================
# 1. 解码 getClass 响应 (原始 hex)
# ============================================
print("=== 1. 解码 getClass 响应 ===")

raw, result = send_amf('userService', 'getClass')
print(f"原始 hex ({len(raw)} bytes): {raw.hex()}")
print(f"解码结果: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")

# 也试 organizationService
raw2, result2 = send_amf('organizationService', 'getClass')
print(f"\norganizationService.getClass 原始 hex ({len(raw2)} bytes): {raw2.hex()}")
print(f"解码结果: {json.dumps(result2, indent=2, ensure_ascii=False, default=str)}")

# ============================================
# 2. 大量 Java 方法名测试
# ============================================
print("\n=== 2. 大量方法名测试 ===")

# 收集所有可能的方法名
method_names = set()

# Java Bean 方法名 (get/set/is + 属性名)
bean_properties = [
    'User', 'Role', 'Permission', 'Organization', 'Department',
    'Project', 'Bug', 'Task', 'TestCase', 'TestRun', 'TestSuite',
    'Requirement', 'Version', 'Build', 'Release', 'Risk', 'Issue',
    'Report', 'Meeting', 'Budget', 'Cost', 'Phase', 'Baseline',
    'Review', 'Code', 'Doc', 'Specification', 'Calendar',
    'Menu', 'Navigation', 'Tree', 'Grid', 'Form',
    'Config', 'Setting', 'Parameter', 'Option',
    'Session', 'Cache', 'Token', 'Ticket',
    'File', 'Attachment', 'Document',
    'Message', 'Notification', 'Email',
    'WorkLog', 'Log', 'Audit',
    'Home', 'Dashboard', 'Summary',
    'Statistics', 'Chart', 'Graph',
    'Entity', 'Model', 'Data', 'Record',
    'List', 'Array', 'Collection',
    'Page', 'Pagination',
    'Count', 'Total', 'Size',
    'Name', 'Id', 'Code', 'Type',
    'Status', 'Priority', 'Severity',
    'Category', 'Tag', 'Label',
    'Description', 'Content', 'Text',
    'Date', 'Time', 'Timestamp',
    'Creator', 'Modifier', 'Owner', 'Assignee',
    'Parent', 'Child', 'Children',
    'Root', 'Node', 'Leaf',
    'Start', 'End', 'Begin', 'Finish',
    'Current', 'Previous', 'Next',
    'Active', 'Inactive', 'Open', 'Close',
    'Published', 'Draft', 'Archived',
    'Public', 'Private', 'Protected',
    'Enabled', 'Disabled',
]

for prop in bean_properties:
    method_names.add(f'get{prop}')
    method_names.add(f'set{prop}')
    method_names.add(f'find{prop}')
    method_names.add(f'load{prop}')
    method_names.add(f'query{prop}')
    method_names.add(f'search{prop}')
    method_names.add(f'count{prop}')
    method_names.add(f'list{prop}')
    method_names.add(f'create{prop}')
    method_names.add(f'update{prop}')
    method_names.add(f'delete{prop}')
    method_names.add(f'save{prop}')
    method_names.add(f'remove{prop}')
    method_names.add(f'export{prop}')
    method_names.add(f'is{prop}')

# isXxx 格式
for prop in ['Active', 'Admin', 'Authenticated', 'Authorized', 'Available',
              'Closed', 'Complete', 'Deleted', 'Disabled', 'Editable',
              'Enabled', 'Expired', 'Finished', 'LoggedIn', 'Open',
              'Published', 'Ready', 'Running', 'Testing', 'Valid']:
    method_names.add(f'is{prop}')
    method_names.add(f'has{prop}')

# 通用方法名
general_methods = [
    'get', 'set', 'find', 'load', 'save', 'create', 'update', 'delete',
    'remove', 'query', 'search', 'list', 'count', 'export', 'import',
    'getAll', 'findAll', 'loadAll', 'getById', 'findById',
    'getByName', 'findByName', 'getByCode', 'findByCode',
    'getByProject', 'findByProject', 'getByOrg', 'findByOrg',
    'getByOrganization', 'findByOrganization',
    'getByUser', 'findByUser', 'getByOwner', 'findByOwner',
    'getEntity', 'findEntity', 'loadEntity', 'saveEntity',
    'createEntity', 'updateEntity', 'deleteEntity', 'queryEntity',
    'getEntityList', 'findEntityList', 'loadEntityList',
    'getEntityById', 'findEntityById', 'getEntityByName',
    'getEntityPage', 'getEntityByQuery', 'getEntityCount',
    'getNamedQuery', 'executeNamedQuery', 'runNamedQuery',
    'getNamedQueryResult', 'getNamedQueryResults',
    'getEntityByNamedQuery', 'queryByNamedQuery',
    'getByNamedQuery', 'findNamedQuery',
    'getModel', 'getModelData', 'getModelConfig', 'getModelInfo',
    'getSchema', 'getDefinition', 'getDefinitionList',
    'getModule', 'getModuleData', 'getModuleConfig', 'getModuleInfo',
    'getModuleList', 'getModuleTree',
    'getHomePage', 'getHomeData', 'getHomeInfo',
    'getTopoData', 'getDracoData', 'getDracoInfo',
    'getNav', 'getNavTree', 'getNavigation', 'getNavData',
    'getWorkPanel', 'getQueryPanel', 'getNavPanel',
    'getMenu', 'getMenuTree', 'getMenuData',
    'getLayout', 'getLayouts', 'getTemplate', 'getTemplates',
    'getRole', 'getRoles', 'getRoleList',
    'getPermission', 'getPermissions', 'getPermissionList',
    'getOrganization', 'getOrganizations', 'getOrgList',
    'getDepartment', 'getDepartments', 'getDeptList',
    'getTeam', 'getTeams', 'getGroup', 'getGroups',
    'getUser', 'getUsers', 'getUserList', 'getUserInfo',
    'getCurrentUser', 'getLoginUser', 'getLoginInfo',
    'getProject', 'getProjects', 'getProjectList', 'getProjectInfo',
    'getBug', 'getBugs', 'getBugList', 'getBugInfo', 'getBugData',
    'getTask', 'getTasks', 'getTaskList', 'getTaskInfo',
    'getTestCase', 'getTestCases', 'getTestCaseList',
    'getTestRun', 'getTestRuns', 'getTestRunList',
    'getTestSuite', 'getTestSuites', 'getTestSuiteList',
    'getRequirement', 'getRequirements', 'getRequirementList',
    'getVersion', 'getVersions', 'getVersionList',
    'getBuild', 'getBuilds', 'getBuildList',
    'getRelease', 'getReleases', 'getReleaseList',
    'getRisk', 'getRisks', 'getRiskList',
    'getIssue', 'getIssues', 'getIssueList',
    'getReport', 'getReports', 'getReportList',
    'getMeetingNotes', 'getMeetingNotesList',
    'getBudget', 'getBudgets', 'getBudgetList',
    'getCost', 'getCosts', 'getCostList',
    'getPhase', 'getPhases', 'getPhaseList',
    'getBaseline', 'getBaselines', 'getBaselineList',
    'getReview', 'getReviews', 'getReviewList',
    'getSpecification', 'getSpecifications',
    'getCalendar', 'getCalendars', 'getWorkCalendar',
    'getStatistics', 'getStats', 'getStatData',
    'getDashboard', 'getSummary', 'getOverview',
    'getChart', 'getChartData', 'getChartData',
    'getAttachment', 'getAttachments', 'getAttachmentList',
    'getComment', 'getComments', 'getCommentList',
    'getLog', 'getLogs', 'getLogList',
    'getWorkLog', 'getWorkLogs', 'getWorkLogList',
    'getMessage', 'getMessages', 'getMessageList',
    'getNotification', 'getNotifications',
    'getEmail', 'getEmails',
    'getConfig', 'getConfiguration', 'getSystemConfig',
    'getSetting', 'getSettings', 'getSystemSetting',
    'getParameter', 'getParameters', 'getParam',
    'getOption', 'getOptions', 'getOptionsList',
    'getSession', 'getSessions', 'getSessionInfo',
    'getCache', 'getCaches', 'getCacheData',
    'getToken', 'getTicket',
    'getVersion', 'getSystemVersion', 'getSystemInfo',
    'getServerInfo', 'getServerVersion',
    'getDracoVersion', 'getTopoVersion',
    'getByProjectId', 'findByProjectId',
    'getBugByProject', 'getBugsByProject',
    'getBugByOrg', 'getBugsByOrg',
    'getByOrganizationId', 'findByOrganizationId',
    'getTaskByProject', 'getTasksByProject',
    'getTestCaseByProject', 'getTestCasesByProject',
    'getTestRunByProject', 'getTestRunsByProject',
    # 登录认证
    'login', 'logout', 'authenticate', 'validate', 'checkLogin',
    'checkPermission', 'hasPermission', 'isAuthorized',
    # 其他
    'ping', 'echo', 'test', 'hello', 'version',
    'help', 'info', 'status', 'health', 'check',
    'describe', 'describeMethods', 'listMethods', 'getMethods',
    'invoke', 'execute', 'process', 'handle',
    'doQuery', 'doFind', 'doGet', 'doList', 'doExecute',
    'fetch', 'fetchData', 'fetchList', 'fetchEntity',
    'page', 'pageQuery', 'pageList',
    'tree', 'getTree', 'getTreeData', 'getTreeList', 'getTreeNode',
    'loadData', 'loadList', 'loadAll', 'loadById',
    'getData', 'getDataList', 'getDataById',
    'queryData', 'queryList', 'queryById',
    'findData', 'findList', 'findById',
    'saveData', 'saveList',
    'createData', 'createList',
    'updateData', 'updateList',
    'deleteData', 'deleteList',
    'removeData', 'removeList',
    'exportData', 'exportList', 'exportExcel', 'exportReport', 'exportCSV',
    'importData', 'importList', 'importExcel', 'importCSV',
    'download', 'upload', 'downloadFile', 'uploadFile',
    'transmit', 'transmitFile',
    'add', 'addAll', 'addItem', 'addEntity',
    'remove', 'removeAll', 'removeItem', 'removeEntity',
    'exist', 'exists', 'contains',
    'refresh', 'reload', 'clear', 'reset', 'flush',
    'init', 'initialize', 'setup', 'configure',
    'start', 'stop', 'restart',
    'open', 'close',
    'begin', 'commit', 'rollback',
    'subscribe', 'unsubscribe',
    'publish', 'notify', 'notifyAll',
    # 拼音命名
    'huoqu', 'chaxun', 'jiazai', 'baocun', 'xinzeng', 'shanchu', 'xiugai',
    'xiangmu', 'quexian', 'renwu', 'yonghu', 'juese', 'quanxian',
    'zuzhi', 'bumen', 'caidan', 'daohang', 'shuju', 'shiti',
]

method_names.update(general_methods)

known_dests = ['userService', 'fileService', 'roleService', 'messageService',
               'layoutService', 'workLogService', 'organizationService']

valid_methods = {}
for dest in known_dests:
    print(f"\n--- {dest} ---")
    found = False
    for method in sorted(method_names):
        try:
            amf_data = build_amf(dest, method)
            resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf'}, timeout=8)
            result = decode_response(resp.content)

            if isinstance(result, dict):
                msg = str(result.get('message', ''))
                if 'No destination' in msg or 'Cannot invoke method' in msg:
                    continue  # 跳过错误
                else:
                    print(f"  ✓✓✓ {dest}.{method}: {msg[:200]}")
                    valid_methods[f"{dest}.{method}"] = msg
                    found = True
            elif isinstance(result, list):
                print(f"  ✓✓✓ {dest}.{method}: Array({len(result)})")
                if len(result) > 0:
                    print(f"    First: {str(result[0])[:200]}")
                valid_methods[f"{dest}.{method}"] = f"Array({len(result)})"
                found = True
            elif result is not None and not isinstance(result, str):
                print(f"  ✓✓✓ {dest}.{method}: {str(result)[:200]}")
                valid_methods[f"{dest}.{method}"] = str(result)
                found = True
            elif isinstance(result, str) and not result.startswith('__'):
                print(f"  ✓✓✓ {dest}.{method}: {result[:200]}")
                valid_methods[f"{dest}.{method}"] = result
                found = True
        except Exception as e:
            pass

    if not found:
        print(f"  (未找到有效方法)")

print(f"\n\n=== 结果汇总 ===")
print(f"找到 {len(valid_methods)} 个有效方法:")
for key, value in sorted(valid_methods.items()):
    print(f"  {key}: {value[:200]}")
