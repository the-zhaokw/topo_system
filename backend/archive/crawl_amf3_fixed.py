"""修复 AMF3 编码并深入分析 AMF0 响应"""
import requests as req
import struct
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

# === AMF0 编码 ===
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
    return b'\x0A' + struct.pack('>I', len(items)) + b''.join(items)

def enc_object(pairs):
    result = b'\x03'
    for key, val in pairs:
        result += enc_str(key) + val
    result += b'\x00\x00\x09'
    return result

def build_amf0(dest, op, args=None):
    if args is None:
        args = []
    body_items = b''
    for arg in args:
        if isinstance(arg, str):
            body_items += enc_str(arg)
        elif isinstance(arg, (int, float)):
            body_items += enc_num(arg)
        elif arg is None:
            body_items += enc_null()
        elif isinstance(arg, bool):
            body_items += enc_bool(arg)
    body = enc_strict_array([enc_str(a) if isinstance(a, str) else enc_null() for a in args]) if args else enc_strict_array([])
    target = f"{dest}.{op}"
    tb = target.encode('utf-8')
    packet = b'\x00\x00\x00\x00\x00\x01' + struct.pack('>H', len(tb)) + tb + b'\x00\x00' + struct.pack('>I', len(body)) + body
    return packet

# === AMF3 编码 (修复版) ===
def amf3_u29(value):
    if value <= 0x7F:
        return bytes([value])
    elif value <= 0x3FFF:
        return bytes([(value >> 7) | 0x80, value & 0x7F])
    elif value <= 0x1FFFFF:
        return bytes([(value >> 14) | 0x80, (value >> 7) | 0x80, value & 0x7F])
    else:
        return bytes([(value >> 22) | 0x80, (value >> 15) | 0x80,
                      (value >> 8) | 0x80, value & 0xFF])

def amf3_str(s):
    b = s.encode('utf-8')
    length = (len(b) << 1) | 1
    return bytes([0x06]) + amf3_u29(length) + b

def amf3_null():
    return bytes([0x01])

def amf3_int(v):
    if 0 <= v <= 0x1FFFFFFF:
        return bytes([0x04]) + amf3_u29(v)
    return bytes([0x05]) + struct.pack('>d', float(v))

def amf3_double(v):
    return bytes([0x05]) + struct.pack('>d', float(v))

def amf3_array(items):
    """AMF3 数组 - 修复空字符串终止符"""
    count = (len(items) << 1) | 1
    result = bytes([0x09]) + amf3_u29(count)
    # 空字符串终止关联部分 (不带 marker, 只是 U29)
    result += bytes([0x01])
    for item in items:
        result += item
    return result

def amf3_typed_object(class_name, members):
    """AMF3 typed object"""
    name_bytes = class_name.encode('utf-8')
    name_len = (len(name_bytes) << 1) | 1

    member_names = list(members.keys())
    trait_count = len(member_names)
    traits_header = (trait_count << 4) | 3

    result = bytes([0x0A])
    result += amf3_u29(traits_header)
    result += amf3_u29(name_len) + name_bytes
    for name in member_names:
        mn = name.encode('utf-8')
        mn_len = (len(mn) << 1) | 1
        result += amf3_u29(mn_len) + mn
    for name in member_names:
        result += members[name]
    return result

def build_amf3_simple(dest, op, args=None):
    if args is None:
        args = []
    items = []
    for arg in args:
        if isinstance(arg, str):
            items.append(amf3_str(arg))
        elif isinstance(arg, int) and 0 <= arg <= 0x1FFFFFFF:
            items.append(amf3_int(arg))
        elif isinstance(arg, (int, float)):
            items.append(amf3_double(float(arg)))
        else:
            items.append(amf3_null())

    body = amf3_array(items)
    target = f"{dest}.{op}"
    tb = target.encode('utf-8')
    packet = b'\x00\x03\x00\x00\x00\x01' + struct.pack('>H', len(tb)) + tb + b'\x00\x00' + struct.pack('>I', len(body)) + body
    return packet

def build_amf3_remoting(dest, op, args=None):
    if args is None:
        args = []
    import time
    msg_id = f"msg_{int(time.time()*1000)}"

    members = {}
    members['correlationId'] = amf3_null()
    members['destination'] = amf3_str(dest)
    members['messageId'] = amf3_str(msg_id)
    members['operation'] = amf3_str(op)
    members['source'] = amf3_null()
    members['timeToLive'] = amf3_int(0)
    members['timestamp'] = amf3_int(0)
    members['clientId'] = amf3_null()
    members['body'] = amf3_array([amf3_str(a) if isinstance(a, str) else amf3_null() for a in args])

    remoting_msg = amf3_typed_object('flex.messaging.messages.RemotingMessage', members)
    body = amf3_array([remoting_msg])
    target = f"{dest}.{op}"
    tb = target.encode('utf-8')
    packet = b'\x00\x03\x00\x00\x00\x01' + struct.pack('>H', len(tb)) + tb + b'\x00\x00' + struct.pack('>I', len(body)) + body
    return packet

# === 深度解码 AMF 响应 ===
class AMF0Decoder:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.strings = []
        self.numbers = []
        self.objects = []
        self.arrays = []

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
        s = self.data[self.pos:self.pos+min(length, 50000)].decode('utf-8', errors='replace')
        self.pos += length; return s

    def read_value(self):
        if self.pos >= len(self.data):
            return None
        type_marker = self.read_u8()
        if type_marker == 0x00:
            v = self.read_double()
            self.numbers.append(v)
            return v
        elif type_marker == 0x01:
            return self.read_u8() != 0
        elif type_marker == 0x02:
            s = self.read_string()
            if s.strip():
                self.strings.append(s)
            return s
        elif type_marker == 0x03:
            obj = {}
            while self.pos < len(self.data):
                key = self.read_string()
                if len(key) == 0:
                    nb = self.read_u8()
                    if nb == 0x09:
                        break
                    else:
                        self.pos -= 1
                        continue
                val = self.read_value()
                obj[key] = val
            self.objects.append(obj)
            return obj
        elif type_marker == 0x05:
            return None
        elif type_marker == 0x06:
            return f"undefined"
        elif type_marker == 0x07:
            return f"reference({self.read_u16()})"
        elif type_marker == 0x08:
            count = self.read_u32()
            arr = []
            for _ in range(count):
                arr.append(self.read_value())
            self.arrays.append(arr)
            return arr
        elif type_marker == 0x0A:
            count = self.read_u32()
            arr = []
            for _ in range(count):
                arr.append(self.read_value())
            self.arrays.append(arr)
            return arr
        elif type_marker == 0x0B:
            date = self.read_double()
            self.numbers.append(date)
            return f"date({date})"
        elif type_marker == 0x0C:
            s = self.read_long_string()
            if s.strip():
                self.strings.append(s[:500])
            return s
        elif type_marker == 0x0D:
            # unsupported
            length = self.read_u32()
            self.pos += length
            return f"unsupported({length})"
        elif type_marker == 0x0F:
            # XML
            length = self.read_u32()
            s = self.data[self.pos:self.pos+min(length, 10000)].decode('utf-8', errors='replace')
            self.pos += length
            if s.strip():
                self.strings.append(f"[XML]{s[:500]}")
            return s
        elif type_marker == 0x10:
            # typed object
            class_name = self.read_string()
            obj = {}
            # read sealed members count
            sealed_count = self.read_u16()
            for _ in range(sealed_count):
                key = self.read_string()
                val = self.read_value()
                obj[key] = val
            # read dynamic members
            while self.pos < len(self.data):
                key = self.read_string()
                if len(key) == 0:
                    nb = self.read_u8()
                    if nb == 0x09:
                        break
                    else:
                        self.pos -= 1
                        continue
                val = self.read_value()
                obj[key] = val
            if class_name.strip():
                self.strings.append(f"[Class:{class_name}]")
            self.objects.append(obj)
            return obj
        elif type_marker == 0x11:
            # AMF3 marker
            return self.read_amf3_value()
        else:
            return f"unknown({type_marker})"

    def read_amf3_value(self):
        if self.pos >= len(self.data):
            return None
        marker = self.read_u8()
        if marker == 0x01:
            return None
        elif marker == 0x02:
            return False
        elif marker == 0x03:
            return True
        elif marker == 0x04:
            return self.read_amf3_u29()
        elif marker == 0x05:
            v = self.read_double()
            return v
        elif marker == 0x06:
            s = self.read_amf3_string()
            if s.strip():
                self.strings.append(f"[AMF3]{s}")
            return s
        elif marker == 0x09:
            count = self.read_amf3_u29()
            is_ref = (count & 1) == 0
            dense_count = count >> 1
            if not is_ref and dense_count == 0:
                pass
            # Read associative part
            arr = []
            while self.pos < len(self.data):
                key = self.read_amf3_string()
                if len(key) == 0:
                    break
                val = self.read_amf3_value()
                arr.append((key, val))
            # Read dense part
            for _ in range(dense_count):
                arr.append(self.read_amf3_value())
            return arr
        elif marker == 0x0A:
            # typed object
            header = self.read_amf3_u29()
            is_ref = (header & 1) == 0
            is_trait_ref = (header & 3) == 1
            if is_ref:
                return f"ref({header >> 1})"
            if is_trait_ref:
                header >>= 2
            traits_header = header >> 2
            has_externalizable = (traits_header & 1) != 0
            has_dynamic = (traits_header & 2) != 0
            member_count = traits_header >> 2

            if not is_trait_ref:
                class_name = self.read_amf3_string()
                if class_name.strip():
                    self.strings.append(f"[AMF3Class:{class_name}]")
                member_names = []
                for _ in range(member_count):
                    mn = self.read_amf3_string()
                    member_names.append(mn)

            obj = {}
            for mn in member_names:
                obj[mn] = self.read_amf3_value()
            return obj
        else:
            return f"amf3_marker({marker})"

    def read_amf3_u29(self):
        result = 0
        for i in range(3):
            if self.pos >= len(self.data):
                return result
            b = self.read_u8()
            result = (result << 7) | (b & 0x7F)
            if (b & 0x80) == 0:
                # Check if this is the 4th byte
                if i < 2:
                    return result
                else:
                    result = (result << 8) | self.read_u8()
                    return result
        if self.pos < len(self.data):
            b = self.read_u8()
            result = (result << 8) | b
        return result

    def read_amf3_string(self):
        header = self.read_amf3_u29()
        is_ref = (header & 1) == 0
        if is_ref:
            return f"str_ref({header >> 1})"
        length = header >> 1
        s = self.data[self.pos:self.pos+length].decode('utf-8', errors='replace')
        self.pos += length
        return s

    def decode(self):
        if len(self.data) < 6:
            return {"error": "too short"}
        version = struct.unpack('>H', self.data[0:2])[0]
        headers_count = struct.unpack('>H', self.data[2:4])[0]
        bodies_count = struct.unpack('>H', self.data[4:6])[0]

        self.pos = 6
        # Skip headers
        for _ in range(headers_count):
            name_len = self.read_u16()
            self.pos += name_len
            self.pos += 1  # required bool
            self.read_value()  # value

        # Parse bodies
        bodies = []
        for _ in range(bodies_count):
            target_len = self.read_u16()
            target_uri = self.data[self.pos:self.pos+target_len].decode('utf-8', errors='replace')
            self.pos += target_len

            resp_len = self.read_u16()
            self.pos += resp_len

            body_len = self.read_u32()
            body_start = self.pos
            value = self.read_value()
            body_end = self.pos

            bodies.append({
                'target': target_uri,
                'value': str(value)[:500] if value is not None else None,
                'body_start': body_start,
                'body_end': body_end,
            })

        return {
            'version': version,
            'bodies': bodies,
            'strings': self.strings,
            'numbers': self.numbers,
            'objects_count': len(self.objects),
            'arrays_count': len(self.arrays),
        }


# === 1. 测试 AMF3 (修复版) ===
print("=== 1. 测试 AMF3 (修复版) ===")
for dest in ['userService', 'organizationService']:
    for method in ['toString', 'getClass']:
        # AMF3 simple
        packet = build_amf3_simple(dest, method)
        resp = session.post(AMF_URL, data=packet, headers={'Content-Type': 'application/x-amf'}, timeout=10)
        decoder = AMF0Decoder(resp.content)
        result = decoder.decode()
        print(f"\n  {dest}.{method} (AMF3 simple):")
        print(f"    响应大小: {len(resp.content)} bytes")
        print(f"    Strings: {result.get('strings', [])[:5]}")
        print(f"    Bodies: {[(b['target'], b['value'][:100] if b['value'] else None) for b in result.get('bodies', [])]}")

        # AMF3 remoting
        packet = build_amf3_remoting(dest, method)
        resp = session.post(AMF_URL, data=packet, headers={'Content-Type': 'application/x-amf'}, timeout=10)
        decoder = AMF0Decoder(resp.content)
        result = decoder.decode()
        print(f"\n  {dest}.{method} (AMF3 remoting):")
        print(f"    响应大小: {len(resp.content)} bytes")
        print(f"    Strings: {result.get('strings', [])[:5]}")
        print(f"    Bodies: {[(b['target'], b['value'][:100] if b['value'] else None) for b in result.get('bodies', [])]}")

# === 2. 深度分析 AMF0 响应 ===
print("\n\n=== 2. 深度分析 AMF0 响应 ===")
for dest, method in [
    ('organizationService', 'toString'),
    ('organizationService', 'getClass'),
    ('userService', 'toString'),
    ('userService', 'getClass'),
    ('organizationService', 'getAll'),
    ('organizationService', 'getGroups'),
]:
    packet = build_amf0(dest, method)
    resp = session.post(AMF_URL, data=packet, headers={'Content-Type': 'application/x-amf'}, timeout=10)
    decoder = AMF0Decoder(resp.content)
    result = decoder.decode()
    print(f"\n  {dest}.{method} (AMF0):")
    print(f"    响应大小: {len(resp.content)} bytes")
    print(f"    Version: {result.get('version')}")
    print(f"    Bodies: {len(result.get('bodies', []))}")
    for b in result.get('bodies', []):
        print(f"      Target: {b['target']}")
        print(f"      Value: {str(b['value'])[:200] if b['value'] else 'None'}")
    print(f"    Strings: {result.get('strings', [])[:10]}")
    print(f"    Numbers: {result.get('numbers', [])[:10]}")
    print(f"    Objects: {result.get('objects_count')}")
    print(f"    Arrays: {result.get('arrays_count')}")

    # 保存原始响应
    fname = f'd:/topo_system/backend/amf_response_{dest}_{method}.bin'
    with open(fname, 'wb') as f:
        f.write(resp.content)

# === 3. 使用 AMF3 remoting 测试 organizationService 方法 ===
print("\n\n=== 3. 测试 organizationService 方法 (AMF3 remoting) ===")
for method in ['toString', 'getClass', 'getGroups', 'getOrganizations',
               'getOrganizationTree', 'getByCode']:
    packet = build_amf3_remoting('organizationService', method, ['RTN'])
    resp = session.post(AMF_URL, data=packet, headers={'Content-Type': 'application/x-amf'}, timeout=10)
    decoder = AMF0Decoder(resp.content)
    result = decoder.decode()
    strings = result.get('strings', [])
    is_error = any('Cannot invoke' in s or 'No destination' in s or 'Unexpected' in s for s in strings)
    has_data = len(strings) > 0 and not is_error
    if has_data:
        print(f"\n  ✓ organizationService.{method} (AMF3 remoting): {len(resp.content)} bytes")
        for s in strings[:10]:
            print(f"    {s[:200]}")
    elif is_error:
        err = ' '.join(strings[:2])
        print(f"  ✗ organizationService.{method}: {err[:100]}")
