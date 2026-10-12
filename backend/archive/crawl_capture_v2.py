"""使用 requests 登录后，将 cookies 转移到 Playwright 捕获 AMF 流量"""
import requests as req
import json
import time
import struct
from playwright.sync_api import sync_playwright

BASE_URL = 'http://172.18.36.5:8000/'
AMF_URL = 'http://172.18.36.5:8000/messagebroker/amf'

# === 1. 使用 requests 登录 ===
session = req.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})

r = session.get(BASE_URL, timeout=10)
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
resp = session.post(login_url, data={
    '_58_redirect': '', '_58_rememberMe': 'false',
    '_58_login': 'zhaokw', '_58_password': '`123qwer',
}, timeout=15, allow_redirects=True)
print(f"登录状态: {resp.status_code}")

# 获取 cookies
cookies = dict(session.cookies)
print(f"获取到 {len(cookies)} 个 cookies:")
for k, v in cookies.items():
    print(f"  {k}={v[:30]}...")

# === 2. 用 requests 直接发送 AMF 请求 ===
def build_amf0_remoting(dest, op, args=None):
    """构造 AMF0 RemotingMessage 请求"""
    if args is None:
        args = []

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

    def enc_strict_array(items_data):
        return b'\x0A' + struct.pack('>I', len(items_data)) + b''.join(items_data)

    def enc_object(pairs):
        result = b'\x03'
        for key, val in pairs:
            result += enc_str(key) + val
        result += b'\x00\x00\x09'
        return result

    # 构造 RemotingMessage 对象
    msg_id = f"msg_{int(time.time()*1000)}"
    remoting_msg = enc_object([
        ('correlationId', enc_str('')),
        ('clientId', enc_null()),
        ('destination', enc_str(dest)),
        ('messageId', enc_str(msg_id)),
        ('operation', enc_str(op)),
        ('source', enc_null()),
        ('timeToLive', enc_num(0)),
        ('timestamp', enc_num(0)),
        ('body', enc_strict_array([enc_str(a) if isinstance(a, str) else enc_null() for a in args])),
    ])

    # body = [RemotingMessage]
    body = enc_strict_array([remoting_msg])

    # 构造 AMF0 包
    packet = b'\x00\x00'  # version 0
    packet += b'\x00\x00'  # 0 headers
    packet += b'\x00\x01'  # 1 body

    # target URI
    target = f"{dest}.{op}"
    tb = target.encode('utf-8')
    packet += struct.pack('>H', len(tb)) + tb

    # response URI (empty)
    packet += b'\x00\x00'

    # body length
    packet += struct.pack('>I', len(body))
    packet += body

    return packet


def build_amf0_simple(dest, op, args=None):
    """构造简单 AMF0 请求 (直接调用, 非 RemotingMessage)"""
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

    body = b'\x0A' + struct.pack('>I', len(args)) + body_items

    target = f"{dest}.{op}"
    tb = target.encode('utf-8')

    packet = b'\x00\x00\x00\x00\x00\x01'  # version 0, 0 headers, 1 body
    packet += struct.pack('>H', len(tb)) + tb
    packet += b'\x00\x00'  # response URI
    packet += struct.pack('>I', len(body))
    packet += body

    return packet


def decode_amf0_response(data):
    """解码 AMF0 响应"""
    result = {'raw_length': len(data)}
    try:
        if len(data) < 6:
            return result

        version = struct.unpack('>H', data[0:2])[0]
        headers_count = struct.unpack('>H', data[2:4])[0]
        bodies_count = struct.unpack('>H', data[4:6])[0]
        result['version'] = version
        result['headers'] = headers_count
        result['bodies'] = bodies_count

        pos = 6
        # 跳过 headers
        for _ in range(headers_count):
            if pos + 2 > len(data):
                break
            name_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2 + name_len + 1  # name + required bool
            # 跳过 value (简单处理)
            if pos < len(data):
                vt = data[pos]
                pos += 1
                if vt == 0x02:
                    if pos + 2 <= len(data):
                        slen = struct.unpack('>H', data[pos:pos+2])[0]
                        pos += 2 + slen
                elif vt == 0x00:
                    pos += 8
                elif vt == 0x05:
                    pass

        # 解析 bodies
        body_results = []
        for _ in range(bodies_count):
            if pos + 2 > len(data):
                break
            target_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            target_uri = data[pos:pos+target_len].decode('utf-8', errors='replace')
            pos += target_len

            if pos + 2 > len(data):
                break
            resp_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2 + resp_len

            if pos + 4 > len(data):
                break
            body_len = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            body_data = data[pos:pos+body_len]
            pos += body_len

            # 提取所有字符串
            strings = []
            # AMF0 string: 0x02 + 2byte length + data
            i = 0
            while i < len(body_data):
                if body_data[i] == 0x02 and i + 2 < len(body_data):
                    slen = struct.unpack('>H', body_data[i+1:i+3])[0]
                    if i + 3 + slen <= len(body_data) and slen > 0:
                        s = body_data[i+3:i+3+slen].decode('utf-8', errors='replace')
                        if s.strip():
                            strings.append(s)
                    i += 3 + slen
                    continue
                # AMF3 string: 0x06 + U29 length + data
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
                        slen = ((b1 & 0x7F) << 7 | (b2 >> 1)) & 0x3FFF
                        if slen > 0 and i + 3 + slen <= len(body_data):
                            s = body_data[i+3:i+3+slen].decode('utf-8', errors='replace')
                            if s.strip():
                                strings.append(s)
                        i += 3 + slen
                        continue
                # AMF0 long string: 0x0C + 4byte length + data
                elif body_data[i] == 0x0C and i + 4 < len(body_data):
                    slen = struct.unpack('>I', body_data[i+1:i+5])[0]
                    if slen > 0 and i + 5 + min(slen, 10000) <= len(body_data):
                        s = body_data[i+5:i+5+min(slen, 10000)].decode('utf-8', errors='replace')
                        if s.strip():
                            strings.append(s[:500])
                    i += 5 + slen
                    continue
                i += 1

            # 提取数字 (AMF0 number: 0x00 + 8 bytes)
            numbers = []
            i = 0
            while i < len(body_data) - 8:
                if body_data[i] == 0x00:
                    try:
                        n = struct.unpack('>d', body_data[i+1:i+9])[0]
                        if n != 0 and n == int(n) and 0 < n < 1000000:
                            numbers.append(int(n))
                    except:
                        pass
                i += 1

            body_results.append({
                'target': target_uri,
                'body_length': body_len,
                'strings': strings[:100],
                'numbers': numbers[:50],
            })

        result['body_details'] = body_results
    except Exception as e:
        result['error'] = str(e)

    return result


# === 3. 测试各种 AMF 请求 ===
print("\n=== 测试 AMF 请求 ===")

# 测试目标和方法
test_cases = [
    # (destination, operation, args, description)
    ('userService', 'toString', [], 'userService.toString'),
    ('organizationService', 'toString', [], 'orgService.toString'),

    # 基于数据模型的查询方法
    ('organizationService', 'getAll', [], 'org.getAll'),
    ('organizationService', 'findAll', [], 'org.findAll'),
    ('organizationService', 'getOrganizations', [], 'org.getOrganizations'),
    ('organizationService', 'getOrganizationTree', [], 'org.getTree'),
    ('organizationService', 'getOrgTree', [], 'org.getOrgTree'),
    ('organizationService', 'getTree', [], 'org.getTree'),

    # 项目相关
    ('projectService', 'getAll', [], 'project.getAll'),
    ('projectService', 'findAll', [], 'project.findAll'),
    ('projectService', 'getProjects', [], 'project.getProjects'),
    ('projectService', 'getByOrg', ['RTN'], 'project.getByOrg(RTN)'),
    ('projectService', 'findByOrg', ['RTN'], 'project.findByOrg(RTN)'),
    ('projectService', 'getByGroupId', ['RTN'], 'project.getByGroupId(RTN)'),

    # Bug 相关 - 关键!
    ('dmBugService', 'getAll', [], 'bug.getAll'),
    ('dmBugService', 'findAll', [], 'bug.findAll'),
    ('dmBugService', 'getBugs', [], 'bug.getBugs'),
    ('dmBugService', 'getByOrg', ['RTN'], 'bug.getByOrg(RTN)'),
    ('dmBugService', 'findByOrg', ['RTN'], 'bug.findByOrg(RTN)'),
    ('dmBugService', 'getByGroupId', ['RTN'], 'bug.getByGroupId(RTN)'),

    # 其他可能的 service 名
    ('bugService', 'getAll', [], 'bugService.getAll'),
    ('bugService', 'getByOrg', ['RTN'], 'bugService.getByOrg(RTN)'),
    ('devMngService', 'getBugs', [], 'devMng.getBugs'),
    ('devMngService', 'getBugByOrg', ['RTN'], 'devMng.getBugByOrg(RTN)'),

    # 用 RemotingMessage 格式
    ('organizationService', 'getOrganizationTree', [], 'org.getOrganizationTree'),
]

valid_results = []
for dest, op, args, desc in test_cases:
    # 用简单格式
    packet = build_amf0_simple(dest, op, args)
    try:
        resp = session.post(AMF_URL, data=packet,
                          headers={'Content-Type': 'application/x-amf'},
                          timeout=10)
        if resp.status_code == 200 and len(resp.content) > 10:
            decoded = decode_amf0_response(resp.content)
            body_details = decoded.get('body_details', [])

            # 检查是否有错误
            has_error = False
            all_strings = []
            for bd in body_details:
                strs = bd.get('strings', [])
                all_strings.extend(strs)
                for s in strs:
                    if 'No destination' in s or 'Cannot invoke' in s or 'not found' in s.lower() or 'error' in s.lower():
                        has_error = True

            if not has_error and all_strings:
                print(f"\n✓ {desc}: {len(resp.content)} bytes, {len(all_strings)} strings")
                # 显示前20个字符串
                for s in all_strings[:20]:
                    print(f"  {s[:200]}")
                valid_results.append({
                    'desc': desc,
                    'destination': dest,
                    'operation': op,
                    'args': args,
                    'size': len(resp.content),
                    'strings': all_strings[:50],
                    'decoded': decoded,
                })
            elif has_error:
                err_msg = ' '.join(all_strings[:3])
                print(f"  ✗ {desc}: {err_msg[:100]}")
            else:
                print(f"  - {desc}: {len(resp.content)} bytes (无字符串)")
        else:
            print(f"  ✗ {desc}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  ✗ {desc}: 异常 {e}")

# === 4. 测试 RemotingMessage 格式 ===
print("\n\n=== 测试 RemotingMessage 格式 ===")
for dest, op, args, desc in [
    ('organizationService', 'getAll', [], 'RM org.getAll'),
    ('organizationService', 'getTree', [], 'RM org.getTree'),
    ('dmBugService', 'getAll', [], 'RM bug.getAll'),
    ('projectService', 'getAll', [], 'RM project.getAll'),
]:
    packet = build_amf0_remoting(dest, op, args)
    try:
        resp = session.post(AMF_URL, data=packet,
                          headers={'Content-Type': 'application/x-amf'},
                          timeout=10)
        if resp.status_code == 200 and len(resp.content) > 10:
            decoded = decode_amf0_response(resp.content)
            body_details = decoded.get('body_details', [])
            all_strings = []
            for bd in body_details:
                all_strings.extend(bd.get('strings', []))

            if all_strings:
                print(f"\n✓ {desc}: {len(resp.content)} bytes")
                for s in all_strings[:30]:
                    if len(s) > 5:
                        print(f"  {s[:200]}")
                valid_results.append({
                    'desc': desc,
                    'destination': dest,
                    'operation': op,
                    'args': args,
                    'size': len(resp.content),
                    'strings': all_strings[:50],
                })
            else:
                print(f"  - {desc}: {len(resp.content)} bytes (无字符串)")
    except Exception as e:
        print(f"  ✗ {desc}: {e}")

# === 5. 保存结果 ===
print(f"\n\n=== 找到 {len(valid_results)} 个有效结果 ===")
with open('d:/topo_system/backend/amf_results.json', 'w', encoding='utf-8') as f:
    json.dump(valid_results, f, ensure_ascii=False, indent=2)
print("结果已保存到 amf_results.json")
