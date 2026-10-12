"""通过 Java 反射和字符串搜索发现 AMF 服务和方法名"""
import requests as req
import struct
import re
import json
import time
from hashlib import md5
from Crypto.Cipher import DES
import zipfile

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
KEY = md5(b'hzytkjyxgs').digest()[:8]

# AMF0 编码辅助
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
    result = b'\x0A' + struct.pack('>I', len(items))
    for item in items:
        result += item
    return result

def enc_object(pairs):
    result = b'\x03'
    for key, val in pairs:
        result += enc_str(key) + val
    result += b'\x00\x00\x09'
    return result

def build_simple_amf(dest, op, args=None):
    if args is None:
        args = []
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
    body = enc_strict_array([enc_str(a) if isinstance(a, str) else enc_null() for a in args]) if args else enc_strict_array([])
    target = f"{dest}.{op}"
    tb = target.encode('utf-8')
    packet = b'\x00\x00\x00\x00\x00\x01'
    packet += struct.pack('>H', len(tb)) + tb
    packet += b'\x00\x00'
    packet += struct.pack('>I', len(body))
    packet += body
    return packet

def decode_response(data):
    """解码 AMF0 响应, 提取所有字符串和错误信息"""
    strings = []
    try:
        if len(data) < 6:
            return strings
        pos = 6
        headers_count = struct.unpack('>H', data[2:4])[0]
        bodies_count = struct.unpack('>H', data[4:6])[0]

        # 跳过 headers
        for _ in range(headers_count):
            if pos + 2 > len(data): break
            name_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2 + name_len + 1
            if pos < len(data):
                vt = data[pos]; pos += 1
                if vt == 0x02 and pos + 2 <= len(data):
                    slen = struct.unpack('>H', data[pos:pos+2])[0]
                    pos += 2 + slen
                elif vt == 0x00: pos += 8
                elif vt == 0x05: pass

        for _ in range(bodies_count):
            if pos + 2 > len(data): break
            target_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2 + target_len
            if pos + 2 > len(data): break
            resp_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2 + resp_len
            if pos + 4 > len(data): break
            body_len = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            body_data = data[pos:pos+body_len]
            pos += body_len

            # 提取所有字符串
            i = 0
            while i < len(body_data):
                # AMF0 string
                if body_data[i] == 0x02 and i + 2 < len(body_data):
                    slen = struct.unpack('>H', body_data[i+1:i+3])[0]
                    if i + 3 + slen <= len(body_data) and slen > 0:
                        s = body_data[i+3:i+3+slen].decode('utf-8', errors='replace')
                        if s.strip():
                            strings.append(s)
                    i += 3 + slen
                    continue
                # AMF0 long string
                elif body_data[i] == 0x0C and i + 4 < len(body_data):
                    slen = struct.unpack('>I', body_data[i+1:i+5])[0]
                    read_len = min(slen, 10000)
                    if i + 5 + read_len <= len(body_data):
                        s = body_data[i+5:i+5+read_len].decode('utf-8', errors='replace')
                        if s.strip():
                            strings.append(s[:500])
                    i += 5 + slen
                    continue
                # AMF3 string (0x06)
                elif body_data[i] == 0x06 and i + 1 < len(body_data):
                    b1 = body_data[i+1]
                    if b1 & 0x80 == 0:
                        slen = (b1 >> 1) & 0x7F
                        if slen > 0 and i + 2 + slen <= len(body_data):
                            s = body_data[i+2:i+2+slen].decode('utf-8', errors='replace')
                            if s.strip():
                                strings.append(s)
                        i += 2 + slen
                        continue
                    elif i + 2 < len(body_data):
                        b2 = body_data[i+2]
                        if b2 & 0x80 == 0:
                            slen = ((b1 & 0x7F) << 7 | (b2 >> 1)) & 0x3FFF
                            if slen > 0 and i + 3 + slen <= len(body_data):
                                s = body_data[i+3:i+3+slen].decode('utf-8', errors='replace')
                                if s.strip():
                                    strings.append(s)
                            i += 3 + slen
                            continue
                i += 1
    except:
        pass
    return strings

def send_amf(dest, op, args=None):
    packet = build_simple_amf(dest, op, args)
    try:
        resp = session.post(AMF_URL, data=packet,
                          headers={'Content-Type': 'application/x-amf'},
                          timeout=8)
        if resp.status_code == 200 and len(resp.content) > 10:
            return decode_response(resp.content)
    except:
        pass
    return []

# === 1. 枚举更多 AMF destinations ===
print("=== 1. 枚举 AMF destinations ===")

# 从已知包名 com.cloudtopo.draco 推断
# 已知: userService, organizationService
# 对应: UserRemoteService, OrganizationRemoteService (在 user.service 包下)

# 可能的模块名
modules = [
    'user', 'devMng', 'project', 'bug', 'task', 'test',
    'requirement', 'version', 'build', 'release', 'risk',
    'issue', 'report', 'meetingNotes', 'costs', 'budget',
    'baseline', 'review', 'specification', 'calendar',
    'portal', 'system', 'config', 'layout', 'message',
    'file', 'role', 'permission', 'auth', 'workLog',
    'dashboard', 'statistic', 'schedule', 'phase',
    'codeReview', 'docReview', 'testCase', 'testRun',
    'testSuite', 'dmBug', 'dmTask', 'dmRequirement',
    'dmVersion', 'dmBuild', 'dmRelease', 'dmRisk',
    'dmIssue', 'dmReport', 'dmMeetingNotes', 'dmCosts',
    'dmBudget', 'dmBaseline', 'dmReview', 'dmSpecification',
    'dmTestCase', 'dmTestRun', 'dmTestSuite', 'dmTestCaseRun',
    'dmPhase', 'dmCodeReview', 'dmDocReview',
]

# 可能的 entity 名 (与 RemoteService 对应)
entities = [
    'User', 'Role', 'Permission', 'Organization', 'Department',
    'Project', 'Bug', 'Task', 'TestCase', 'TestRun', 'TestSuite',
    'TestCaseRun', 'Requirement', 'Specification', 'Version',
    'Build', 'Release', 'Risk', 'Issue', 'Report',
    'MeetingNotes', 'Costs', 'Budget', 'Baseline', 'Review',
    'CodeReview', 'DocReview', 'Phase', 'WorkLog', 'WorkCalendar',
    'Layout', 'Message', 'File', 'Config', 'Dashboard',
    'dmBug', 'dmTask', 'dmRequirement', 'dmVersion',
    'dmBuild', 'dmRelease', 'dmRisk', 'dmIssue',
    'dmReport', 'dmMeetingNotes', 'dmCosts', 'dmBudget',
    'dmBaseline', 'dmReview', 'dmSpecification',
    'dmTestCase', 'dmTestRun', 'dmTestSuite',
    'dmTestCaseRun', 'dmPhase', 'dmCodeReview', 'dmDocReview',
    'project', 'projectFoundReview', 'projectFinishReview',
]

# destination 命名模式
patterns = [
    '{entity}Service',
    '{entityLower}Service',
    '{entity}RemoteService',
    '{entityLower}RemoteService',
    '{entity}ServiceImpl',
    '{entityLower}ServiceImpl',
]

found_dests = set()
# 先测试已知
for dest in ['userService', 'organizationService', 'fileService', 'roleService',
             'messageService', 'layoutService', 'workLogService']:
    result = send_amf(dest, 'toString')
    if result:
        for s in result:
            if 'cloudtopo' in s or 'com.' in s:
                print(f"  ✓ {dest} → {s}")
                found_dests.add(dest)
                break

# 测试新 destination
print("\n--- 测试新 destinations ---")
for entity in entities:
    for pattern in patterns:
        if entity in [e for e in entities if e.startswith('dm')]:
            # dmBug → dmBugService 或 dmbugService
            dest = pattern.format(entity=entity, entityLower=entity[0].lower() + entity[1:])
        else:
            dest = pattern.format(entity=entity, entityLower=entity[0].lower() + entity[1:])

        if dest in found_dests:
            continue

        result = send_amf(dest, 'toString')
        if result:
            for s in result:
                if 'cloudtopo' in s or 'com.' in s or 'Service' in s:
                    print(f"  ✓ {dest} → {s}")
                    found_dests.add(dest)
                    break
                elif 'No destination' not in s and 'Cannot invoke' not in s:
                    # 可能是有效响应
                    print(f"  ? {dest} → {s[:100]}")
                    found_dests.add(dest)
                    break

print(f"\n找到 {len(found_dests)} 个有效 destinations: {sorted(found_dests)}")

# === 2. 在已知 destinations 上测试方法名 ===
print("\n\n=== 2. 测试方法名 ===")

# 通用 Java 方法
java_methods = [
    'toString', 'getClass', 'hashCode', 'getName', 'getClassName',
    'getMethods', 'getDeclaredMethods', 'getFields', 'getDeclaredFields',
]

# 业务方法前缀 + 实体名
method_prefixes = ['get', 'find', 'load', 'query', 'search', 'count', 'list',
                   'fetch', 'retrieve', 'select', 'read', 'lookup',
                   'getBy', 'findBy', 'queryBy', 'searchBy',
                   'getByOrg', 'findByOrg', 'getByGroupId', 'findByGroupId',
                   'getByProject', 'findByProject',
                   'getByOrgId', 'findByOrgId',
                   'getByOrganization', 'findByOrganization',
                   'getByGroup', 'findByGroup',
                   'getBugByOrg', 'getBugByProject',
                   'getBugsByOrg', 'getBugsByProject',
                   'getByProjectAndOrg',
]

# 数据访问方法 (基于查询模式)
query_methods = [
    'query', 'executeQuery', 'executeNamedQuery', 'runQuery',
    'getList', 'getData', 'getEntity', 'getEntities',
    'getModel', 'getModels', 'getEntityList',
    'getAll', 'findAll', 'loadAll', 'listAll',
    'getById', 'findById', 'loadById',
    'getCount', 'countAll', 'count',
    'getTree', 'getTreeData', 'getOrgTree',
    'getOrganization', 'getOrganizations',
    'getProject', 'getProjects',
    'getBug', 'getBugs',
    'getTask', 'getTasks',
    'getRequirement', 'getRequirements',
    'getVersion', 'getVersions',
    'getRelease', 'getReleases',
    'getRisk', 'getRisks',
    'getIssue', 'getIssues',
    'getReport', 'getReports',
    'getMember', 'getMembers', 'getUsers',
    'getRole', 'getRoles',
    'getPermission', 'getPermissions',
    'getWorkLog', 'getWorkLogs',
    'getLayout', 'getLayouts',
    'getMessage', 'getMessages',
    'getFile', 'getFiles',
    'getPhase', 'getPhases',
    'getBuild', 'getBuilds',
    'getBaseline', 'getBaselines',
    'getReview', 'getReviews',
    'getTestCase', 'getTestCases',
    'getTestRun', 'getTestRuns',
    'getTestSuite', 'getTestSuites',
    'getBudget', 'getBudgets',
    'getCosts', 'getCost',
    'getSpecification', 'getSpecifications',
    'getCalendar', 'getWorkCalendar',
    'getDashboard', 'getStatistics',
    'getStat', 'getStatData',
    'getNamedQueries', 'getQueries',
    'getNamedQuery', 'getQuery',
    'getNamedQueryList',
    'executeNamedQuery',
    'getNamedQueryNames',
    'getQueryNames',
    'getFilterFields',
    'getDisplayFields',
    'getModelNames', 'getEntityNames',
]

all_methods = set(java_methods + query_methods)
# 添加前缀 + 实体组合
for entity in ['Bug', 'Project', 'Organization', 'Task', 'User', 'Requirement',
               'Version', 'Build', 'Release', 'Risk', 'Issue', 'Report',
               'Member', 'Role', 'Permission', 'WorkLog', 'Layout',
               'Message', 'File', 'Phase', 'Baseline', 'Review',
               'TestCase', 'TestRun', 'TestSuite', 'Budget', 'Costs',
               'Specification', 'Calendar', 'Dashboard']:
    for prefix in ['get', 'find', 'load', 'query', 'search', 'count', 'list']:
        all_methods.add(f'{prefix}{entity}')
        all_methods.add(f'{prefix}{entity}s')
        all_methods.add(f'{prefix}{entity}ByOrg')
        all_methods.add(f'{prefix}{entity}sByOrg')
        all_methods.add(f'{prefix}{entity}ByGroupId')
        all_methods.add(f'{prefix}{entity}sByGroupId')
        all_methods.add(f'{prefix}{entity}ByProject')
        all_methods.add(f'{prefix}{entity}sByProject')
        all_methods.add(f'{prefix}{entity}ByOrganization')
        all_methods.add(f'{prefix}{entity}sByOrganization')

method_results = {}
for dest in sorted(found_dests):
    print(f"\n--- {dest} ---")
    found = False
    for method in sorted(all_methods):
        if method in ['toString', 'getClass']:
            continue  # 已经测试过
        result = send_amf(dest, method)
        if result:
            # 检查是否是错误
            is_error = False
            for s in result:
                if 'Cannot invoke method' in s or 'Method' in s and 'not found' in s:
                    is_error = True
                    break
                if 'No destination' in s:
                    is_error = True
                    break

            if not is_error:
                print(f"  ✓✓✓ {dest}.{method}: {result[:5]}")
                method_results[f"{dest}.{method}"] = result[:20]
                found = True
    if not found:
        print(f"  (无有效方法)")

# === 3. 从 SWF 中搜索方法名 ===
print("\n\n=== 3. 从 SWF 中搜索方法名 ===")
swf_urls = [
    '/html/portlet/ext/draco/modules/draco_module.swf',
    '/html/portlet/ext/draco/modules/draco_drmng.swf',
    '/html/portlet/ext/draco/modules/draco_test.swf',
    '/html/portlet/ext/draco/modules/draco_report.swf',
    '/html/portlet/ext/draco/modules/draco_baseline.swf',
    '/html/portlet/ext/draco/modules/draco_version.swf',
    '/html/portlet/ext/draco/modules/draco_cost.swf',
    '/html/portlet/ext/draco/modules/draco_risk.swf',
    '/html/portlet/ext/draco/modules/draco_layout.swf',
    '/html/portlet/ext/draco/modules/draco_user.swf',
    '/html/portlet/ext/draco/modules/draco_organization.swf',
    '/html/portlet/ext/draco/modules/draco_project.swf',
]

for swf_url in swf_urls:
    url = f'http://172.18.36.5:8000{swf_url}'
    try:
        r = session.get(url, timeout=15)
        if r.status_code == 200 and len(r.content) > 100:
            # 解密
            cipher = DES.new(KEY, DES.MODE_ECB)
            padded_len = (len(r.content) // 8) * 8
            decrypted = cipher.decrypt(r.content[:padded_len]) + r.content[padded_len:]

            # 提取字符串
            all_strs = [s.decode('ascii', errors='ignore')
                       for s in re.findall(rb'[\x20-\x7e]{4,}', decrypted)]

            # 搜索 Service 相关
            svc_strs = [s for s in all_strs if 'Service' in s and len(s) < 100]
            if svc_strs:
                print(f"\n--- {swf_url} ({len(r.content)} bytes, {len(all_strs)} strings) ---")
                for s in sorted(set(svc_strs))[:30]:
                    print(f"  Service: {s}")

            # 搜索 destination 相关 (RemoteObject.destination)
            dest_strs = [s for s in all_strs if 'destination' in s.lower() and len(s) < 100]
            for s in sorted(set(dest_strs))[:10]:
                print(f"  Dest: {s}")

            # 搜索 get/find 方法
            method_strs = [s for s in all_strs
                          if re.match(r'^[a-z][a-zA-Z]{4,50}$', s) and
                          any(kw in s.lower() for kw in ['get', 'find', 'load', 'query', 'search', 'count', 'list', 'fetch'])]
            if method_strs:
                for s in sorted(set(method_strs))[:30]:
                    print(f"  Method: {s}")

            # 搜索 messagebroker/amf/Remote 相关
            amf_strs = [s for s in all_strs if 'messagebroker' in s.lower() or
                        'Remote' in s or 'remote' in s.lower() or
                        'Channel' in s or 'channel' in s.lower()]
            for s in sorted(set(amf_strs))[:10]:
                print(f"  AMF: {s}")
    except Exception as e:
        pass

# === 4. 保存结果 ===
print(f"\n\n=== 找到 {len(method_results)} 个有效方法 ===")
with open('d:/topo_system/backend/amf_methods_found.json', 'w', encoding='utf-8') as f:
    json.dump({
        'destinations': sorted(found_dests),
        'methods': method_results,
    }, f, ensure_ascii=False, indent=2)
print("结果已保存到 amf_methods_found.json")
