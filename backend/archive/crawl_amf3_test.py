"""尝试 AMF3 格式和不同 destination 名称"""
import requests as req
import struct
import io
import time

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

# === AMF3 编码 ===
class AMF3Encoder:
    def __init__(self):
        self.strings = []
        self.objects = []
        self.traits = []

    def encode_u29(self, value):
        """编码 U29 整数"""
        if value <= 0x7F:
            return bytes([value])
        elif value <= 0x3FFF:
            return bytes([(value >> 7) | 0x80, value & 0x7F])
        elif value <= 0x1FFFFF:
            return bytes([(value >> 14) | 0x80, (value >> 7) | 0x80, value & 0x7F])
        else:
            return bytes([(value >> 22) | 0x80, (value >> 15) | 0x80,
                         (value >> 8) | 0x80, value & 0xFF])

    def encode_string(self, s):
        """编码 AMF3 字符串"""
        b = s.encode('utf-8')
        length = len(b)
        # 长度左移1位, 最低位置1表示不是引用
        encoded_len = (length << 1) | 1
        return bytes([0x06]) + self.encode_u29(encoded_len) + b

    def encode_null(self):
        return bytes([0x01])

    def encode_bool_true(self):
        return bytes([0x03])

    def encode_bool_false(self):
        return bytes([0x02])

    def encode_integer(self, value):
        """编码 AMF3 整数"""
        if value >= 0 and value <= 0x1FFFFFFF:
            return bytes([0x04]) + self.encode_u29(value)
        else:
            return bytes([0x05]) + struct.pack('>d', float(value))

    def encode_double(self, value):
        return bytes([0x05]) + struct.pack('>d', float(value))

    def encode_array(self, items):
        """编码 AMF3 数组"""
        encoded_items = b''
        for item in items:
            encoded_items += item
        # 数组长度左移4位, 最低位(引用位)设为1
        count = (len(items) << 1) | 1  # 密集部分长度, 低位置1表示非引用
        return bytes([0x09]) + self.encode_u29(count) + b'' + encoded_items

    def encode_typed_object(self, class_name, members):
        """编码 AMF3 typed object"""
        # 外化对象: type marker 0x0A (instance)
        # 外化标记: (traits_ref << 2) | 1 = 表示这是一个外化对象(无成员信息)
        # 实际上对于 Flex RemotingMessage, 通常用 ASObject (关联数组)

        # 简单方案: 用关联数组 (类型 marker 0x08 = ECMA Array)
        # 或者直接用匿名对象 (类型 marker 0x0A + traits)

        # 用 typed object
        name_bytes = class_name.encode('utf-8')
        name_len = (len(name_bytes) << 1) | 1  # 非引用

        # traits: (count << 4) | 3 = 非 traits 引用, 有成员, 是外化的
        member_names = list(members.keys())
        trait_count = len(member_names)
        traits_header = (trait_count << 4) | 3  # 非 traits 引用, 不是外化的, 有成员

        result = bytes([0x0A])  # instance marker
        result += self.encode_u29(traits_header)  # traits
        result += self.encode_u29(name_len) + name_bytes  # class name
        for name in member_names:
            # 成员名
            mn = name.encode('utf-8')
            mn_len = (len(mn) << 1) | 1
            result += self.encode_u29(mn_len) + mn
        for name in member_names:
            result += members[name]
        return result

    def encode_ecma_array(self, pairs):
        """编码 AMF3 ECMA Array"""
        result = bytes([0x08])  # ECMA array marker
        count = (len(pairs) << 1) | 1  # 非引用
        result += self.encode_u29(count)
        for key, val in pairs:
            # key
            kb = key.encode('utf-8')
            kl = (len(kb) << 1) | 1
            result += self.encode_u29(kl) + kb
            # value
            result += val
        # 空字符串结束
        result += bytes([0x01])  # 空字符串 (length=0<<1|1=1, encoded as 0x01)
        return result


def build_amf3_remoting(destination, operation, args=None):
    """构造 AMF3 RemotingMessage 请求"""
    if args is None:
        args = []

    enc = AMF3Encoder()
    msg_id = f"msg_{int(time.time()*1000)}"

    # RemotingMessage 的成员
    members = {
        'correlationId': enc.encode_null(),
        'destination': enc.encode_string(destination),
        'messageId': enc.encode_string(msg_id),
        'operation': enc.encode_string(operation),
        'source': enc.encode_null(),
        'timeToLive': enc.encode_integer(0),
        'timestamp': enc.encode_integer(0),
        'clientId': enc.encode_null(),
        'body': enc.encode_array([enc.encode_string(a) if isinstance(a, str) else enc.encode_null() for a in args]),
    }

    # 构造 RemotingMessage 作为 typed object
    # Flex 会使用 flex.messaging.messages.RemotingMessage
    remoting_msg = enc.encode_typed_object('flex.messaging.messages.RemotingMessage', members)

    # 构造 body = [RemotingMessage]
    body = enc.encode_array([remoting_msg])

    # 构造 AMF 包 (version 3)
    packet = b'\x00\x03'  # version 3 (AMF3)
    packet += b'\x00\x00'  # 0 headers
    packet += b'\x00\x01'  # 1 body

    # target URI (空字符串 - 在 RemotingMessage 模式下)
    # 实际上 BlazeDS 会使用 target URI 来路由
    target = f"{destination}.{operation}"
    tb = target.encode('utf-8')
    packet += struct.pack('>H', len(tb)) + tb

    # response URI
    packet += struct.pack('>H', 0)

    # body length
    packet += struct.pack('>I', len(body))
    packet += body

    return packet


def build_amf3_simple(destination, operation, args=None):
    """构造简单 AMF3 请求 (直接调用, 非 RemotingMessage)"""
    if args is None:
        args = []

    enc = AMF3Encoder()

    # body = [args...]
    items = []
    for arg in args:
        if isinstance(arg, str):
            items.append(enc.encode_string(arg))
        elif isinstance(arg, (int, float)):
            items.append(enc.encode_integer(int(arg)) if isinstance(arg, int) and 0 <= arg <= 0x1FFFFFFF else enc.encode_double(float(arg)))
        else:
            items.append(enc.encode_null())

    body = enc.encode_array(items)

    target = f"{destination}.{operation}"
    tb = target.encode('utf-8')

    packet = b'\x00\x03'  # version 3
    packet += b'\x00\x00'  # 0 headers
    packet += b'\x00\x01'  # 1 body
    packet += struct.pack('>H', len(tb)) + tb
    packet += struct.pack('>H', 0)  # response URI
    packet += struct.pack('>I', len(body))
    packet += body

    return packet


def decode_response(data):
    """解码 AMF 响应, 提取所有字符串"""
    strings = []
    try:
        if len(data) < 6:
            return strings
        version = struct.unpack('>H', data[0:2])[0]
        headers_count = struct.unpack('>H', data[2:4])[0]
        bodies_count = struct.unpack('>H', data[4:6])[0]
        pos = 6

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

            # 提取所有字符串 (AMF0 和 AMF3)
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
                # AMF3 string
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
                        elif i + 3 < len(body_data):
                            b3 = body_data[i+3]
                            if b3 & 0x80 == 0:
                                slen = ((b1 & 0x7F) << 14 | (b2 & 0x7F) << 7 | (b3 >> 1)) & 0x1FFFFF
                                if slen > 0 and i + 4 + slen <= len(body_data):
                                    s = body_data[i+4:i+4+slen].decode('utf-8', errors='replace')
                                    if s.strip():
                                        strings.append(s)
                                i += 4 + slen
                                continue
                i += 1
    except:
        pass
    return strings


def send_amf0(dest, op, args=None):
    """发送 AMF0 简单请求"""
    if args is None:
        args = []
    body_items = b''
    for arg in args:
        if isinstance(arg, str):
            b = arg.encode('utf-8')
            body_items += b'\x02' + struct.pack('>H', len(b)) + b
        elif isinstance(arg, (int, float)):
            body_items += b'\x00' + struct.pack('>d', float(arg))
        elif arg is None:
            body_items += b'\x05'
    body = b'\x0A' + struct.pack('>I', len(args)) + body_items
    target = f"{dest}.{op}"
    tb = target.encode('utf-8')
    packet = b'\x00\x00\x00\x00\x00\x01' + struct.pack('>H', len(tb)) + tb + b'\x00\x00' + struct.pack('>I', len(body)) + body
    resp = session.post(AMF_URL, data=packet, headers={'Content-Type': 'application/x-amf'}, timeout=10)
    if resp.status_code == 200 and len(resp.content) > 10:
        return decode_response(resp.content)
    return []


def send_amf3_simple(dest, op, args=None):
    """发送 AMF3 简单请求"""
    packet = build_amf3_simple(dest, op, args)
    resp = session.post(AMF_URL, data=packet, headers={'Content-Type': 'application/x-amf'}, timeout=10)
    if resp.status_code == 200 and len(resp.content) > 10:
        return decode_response(resp.content)
    return []


def send_amf3_remoting(dest, op, args=None):
    """发送 AMF3 RemotingMessage 请求"""
    packet = build_amf3_remoting(dest, op, args)
    resp = session.post(AMF_URL, data=packet, headers={'Content-Type': 'application/x-amf'}, timeout=10)
    if resp.status_code == 200 and len(resp.content) > 10:
        return decode_response(resp.content)
    return []


# === 1. 测试已知 destinations (AMF3 格式) ===
print("=== 1. 测试已知 destinations (AMF3) ===")
known_dests = ['userService', 'organizationService', 'fileService', 'roleService',
               'messageService', 'layoutService', 'workLogService']

for dest in known_dests:
    for format_name, send_func in [('AMF0', send_amf0), ('AMF3simple', send_amf3_simple), ('AMF3remoting', send_amf3_remoting)]:
        result = send_func(dest, 'toString')
        if result:
            for s in result:
                if 'cloudtopo' in s or 'com.' in s:
                    print(f"  {dest}.{format_name}.toString: {s}")
                    break

# === 2. 测试新 destination 名称 (不带 Service 后缀) ===
print("\n=== 2. 测试新 destination 名称 ===")
new_dests = [
    'dmBug', 'dmTask', 'dmRequirement', 'dmVersion', 'dmBuild',
    'dmRelease', 'dmRisk', 'dmIssue', 'dmReport', 'dmMeetingNotes',
    'dmCosts', 'dmBudget', 'dmBaseline', 'dmReview', 'dmSpecification',
    'dmTestCase', 'dmTestRun', 'dmTestSuite', 'dmTestCaseRun',
    'dmPhase', 'dmCodeReview', 'dmDocReview',
    'project', 'bug', 'task', 'requirement', 'version',
    'build', 'release', 'risk', 'issue', 'report',
    'projectService', 'bugService', 'taskService',
    'devMng', 'devMngService', 'devService',
    'dataService', 'entityService', 'modelService',
    'dmService', 'dmDataService', 'dmEntityService',
    'applicationService', 'appService',
    'portalService', 'portal',
    'statService', 'stat',
    'exportService', 'export',
    'queryService', 'query',
]

for dest in new_dests:
    # 用 AMF0 测试
    result = send_amf0(dest, 'toString')
    if result:
        is_real = False
        for s in result:
            if 'No destination' in s or 'Cannot invoke' in s:
                break
            if 'cloudtopo' in s or 'com.' in s or 'Service' in s:
                print(f"  OK {dest} (AMF0): {s}")
                is_real = True
                break
        if not is_real and result:
            # 可能是其他响应
            first = result[0]
            if first and 'No destination' not in first and 'Cannot invoke' not in first:
                print(f"  ? {dest} (AMF0): {first[:100]}")

    # 也用 AMF3 测试
    result3 = send_amf3_simple(dest, 'toString')
    if result3:
        is_real = False
        for s in result3:
            if 'No destination' in s or 'Cannot invoke' in s:
                break
            if 'cloudtopo' in s or 'com.' in s or 'Service' in s:
                print(f"  OK {dest} (AMF3): {s}")
                is_real = True
                break

# === 3. 在 organizationService 上测试更多方法 (AMF3) ===
print("\n=== 3. 测试 organizationService 方法 (AMF3) ===")
org_methods = [
    'toString', 'getClass',
    # 组织树
    'getOrganizationTree', 'getOrgTree', 'getTree',
    'getOrganizations', 'getOrganization',
    'getRootOrganizations', 'getRoots',
    'getSubOrganizations', 'getChildren',
    'getOrganizationById', 'getById',
    # 获取关联数据
    'getProjects', 'getProject',
    'getBugs', 'getBug',
    'getTasks', 'getTask',
    'getUsers', 'getUser',
    'getMembers', 'getMember',
    'getRequirements', 'getRequirement',
    # 通用方法
    'getAll', 'findAll', 'list', 'getList',
    'get', 'find', 'load', 'query',
    'getEntity', 'getEntities',
    'getData', 'getModel', 'getModels',
    'getNamedQueries', 'getQueries',
    'executeQuery', 'runQuery',
    'getHome', 'getHomePage',
    'getOrgHomePage', 'getOrgHomePageUrl',
    # 可能的云拓扑特有方法
    'getOrg', 'getOrgs', 'getGroup', 'getGroups',
    'getGroupById', 'getGroupByName',
    'getByName', 'findByCode', 'getByCode',
    'getByType', 'findByType',
    'getByPath', 'findByPath',
]

for method in org_methods:
    if method in ['toString']:
        continue
    # AMF0
    result = send_amf0('organizationService', method)
    if result:
        is_error = any('Cannot invoke' in s or 'No destination' in s for s in result)
        if not is_error:
            print(f"  OK organizationService.{method} (AMF0): {result[:5]}")

    # AMF3
    result3 = send_amf3_simple('organizationService', method)
    if result3:
        is_error = any('Cannot invoke' in s or 'No destination' in s for s in result3)
        if not is_error:
            print(f"  OK organizationService.{method} (AMF3): {result3[:5]}")

# === 4. 在所有已知 service 上测试 getClass 和 getMethods ===
print("\n=== 4. 测试 getClass ===")
for dest in known_dests:
    for format_name, send_func in [('AMF0', send_amf0), ('AMF3', send_amf3_simple)]:
        result = send_func(dest, 'getClass')
        if result:
            is_error = any('Cannot invoke' in s for s in result)
            if not is_error:
                print(f"  {dest}.getClass ({format_name}): {result[:5]}")

        # 也试试 getName
        result = send_func(dest, 'getName')
        if result:
            is_error = any('Cannot invoke' in s for s in result)
            if not is_error:
                print(f"  {dest}.getName ({format_name}): {result[:5]}")

        # 也试试 getOrgHomePageUrl
        result = send_func(dest, 'getOrgHomePageUrl')
        if result:
            is_error = any('Cannot invoke' in s for s in result)
            if not is_error:
                print(f"  {dest}.getOrgHomePageUrl ({format_name}): {result[:5]}")
