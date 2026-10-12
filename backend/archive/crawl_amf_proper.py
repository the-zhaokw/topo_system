"""
修正 AMF 请求格式，并完整解码 AMF3 响应。
之前的问题是请求包有重复的 header。
"""
import requests as req
import struct
import binascii
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

AMF_URL = 'http://172.18.36.5:8000/messagebroker/amf'

# ============================================
# AMF0 请求构建（修正版）
# ============================================
def build_amf0(dest, op, args=None):
    """构建正确的 AMF0 请求包"""
    if args is None:
        args = []

    # 构建参数数组 (AMF0 strict array)
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

    body_data = b'\x0A' + struct.pack('>I', len(args)) + body_items  # strict array

    # 目标 URI
    target = f"{dest}.{op}"
    tb = target.encode('utf-8')

    # 构建完整的 AMF0 包
    packet = b''
    packet += b'\x00\x00'  # version: AMF0
    packet += b'\x00\x00'  # header count: 0
    packet += b'\x00\x01'  # body count: 1

    # Body
    packet += struct.pack('>H', len(tb)) + tb  # target URI
    packet += struct.pack('>H', 0)               # response URI (empty)
    packet += struct.pack('>I', len(body_data)) + body_data  # body

    return packet

# ============================================
# AMF3 响应解码
# ============================================
class AMF3Decoder:
    def __init__(self, data, pos=0):
        self.data = data
        self.pos = pos
        self.strings = []
        self.objects = []
        self.traits = []

    def read_u29(self):
        """读取 U29 整数"""
        val = 0
        for i in range(4):
            if self.pos >= len(self.data):
                return val
            b = self.data[self.pos]
            self.pos += 1
            if i < 3:
                if (b & 0x80) == 0:
                    val = (val << 7) | (b & 0x7F)
                    return val
                else:
                    val = (val << 7) | (b & 0x7F)
            else:
                val = (val << 8) | b
        return val

    def read_string(self):
        """读取 AMF3 字符串"""
        ref = self.read_u29()
        if (ref & 1) == 0:
            idx = ref >> 1
            if idx < len(self.strings):
                return self.strings[idx]
            return ""
        length = ref >> 1
        s = self.data[self.pos:self.pos+length].decode('utf-8', errors='replace')
        self.pos += length
        if s:
            self.strings.append(s)
        return s

    def read_value(self):
        """读取 AMF3 值"""
        if self.pos >= len(self.data):
            return None
        marker = self.data[self.pos]
        self.pos += 1

        if marker == 0x00:  # undefined
            return None
        elif marker == 0x01:  # null
            return None
        elif marker == 0x02:  # false
            return False
        elif marker == 0x03:  # true
            return True
        elif marker == 0x04:  # integer
            val = self.read_u29()
            if val >= 0x10000000:
                val -= 0x20000000
            return val
        elif marker == 0x05:  # double
            if self.pos + 8 > len(self.data):
                return None
            val = struct.unpack('>d', self.data[self.pos:self.pos+8])[0]
            self.pos += 8
            return val
        elif marker == 0x06:  # string
            return self.read_string()
        elif marker == 0x07:  # XML
            return f"<XML>{self.read_string()}</XML>"
        elif marker == 0x08:  # date
            ref = self.read_u29()
            if (ref & 1) == 0:
                idx = ref >> 1
                return self.objects[idx] if idx < len(self.objects) else None
            if self.pos + 8 > len(self.data):
                return None
            ms = struct.unpack('>d', self.data[self.pos:self.pos+8])[0]
            self.pos += 8
            result = f"<date ms={ms}>"
            self.objects.append(result)
            return result
        elif marker == 0x09:  # array
            ref = self.read_u29()
            if (ref & 1) == 0:
                idx = ref >> 1
                return self.objects[idx] if idx < len(self.objects) else None
            count = ref >> 1
            # 关联部分
            result = {}
            while self.pos < len(self.data):
                key = self.read_string()
                if key == "":
                    break
                val = self.read_value()
                result[key] = val
            # 密集部分
            arr = []
            for _ in range(count):
                val = self.read_value()
                arr.append(val)
            if result:
                result['_array'] = arr
                self.objects.append(result)
                return result
            else:
                self.objects.append(arr)
                return arr
        elif marker == 0x0A:  # object
            ref = self.read_u29()
            if (ref & 1) == 0:
                idx = ref >> 1
                return self.objects[idx] if idx < len(self.objects) else None

            traits_val = ref >> 1
            if (traits_val & 1) == 0:
                # traits reference
                traits_idx = traits_val >> 1
                if traits_idx < len(self.traits):
                    prop_names, is_dynamic, is_externalizable, class_name = self.traits[traits_idx]
                else:
                    prop_names, is_dynamic, is_externalizable, class_name = [], False, False, "unknown"
            else:
                # new traits
                traits_val = traits_val >> 1
                is_externalizable = (traits_val & 1) == 1
                traits_val = traits_val >> 1
                is_dynamic = (traits_val & 1) == 1
                traits_val = traits_val >> 1
                num_sealed = traits_val
                class_name = self.read_string()
                prop_names = []
                for _ in range(num_sealed):
                    pname = self.read_string()
                    prop_names.append(pname)
                self.traits.append((prop_names, is_dynamic, is_externalizable, class_name))

            obj = {'__class__': class_name}
            self.objects.append(obj)

            # 读取 sealed members
            for pname in prop_names:
                val = self.read_value()
                obj[pname] = val

            # 读取 dynamic members
            if is_dynamic:
                while self.pos < len(self.data):
                    key = self.read_string()
                    if key == "":
                        break
                    val = self.read_value()
                    obj[key] = val

            # externalizable
            if is_externalizable:
                obj['__external_data__'] = self.read_value()

            return obj
        elif marker == 0x0B:  # XML doc
            return f"<XMLDoc>{self.read_string()}</XMLDoc>"
        elif marker == 0x0C:  # byte array
            ref = self.read_u29()
            if (ref & 1) == 0:
                idx = ref >> 1
                return self.objects[idx] if idx < len(self.objects) else None
            length = ref >> 1
            raw = self.data[self.pos:self.pos+length]
            self.pos += length
            self.objects.append(raw)
            return raw
        else:
            return f"<unknown AMF3 marker 0x{marker:02x} at pos {self.pos-1}>"

def decode_amf_response(data):
    """解码 AMF 响应（支持 AMF0 和 AMF3）"""
    if len(data) < 6:
        return None

    version = struct.unpack('>H', data[0:2])[0]
    header_count = struct.unpack('>H', data[2:4])[0]
    pos = 4

    # 跳过 headers
    for _ in range(header_count):
        if pos + 2 > len(data):
            return None
        name_len = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        pos += name_len + 1 + 4  # name + mustUnderstand + length
        # skip value (simplified)
        if pos < len(data):
            if data[pos] in [0x05, 0x06]:  # null/undefined
                pos += 1
            elif data[pos] == 0x02:  # string
                pos += 1
                slen = struct.unpack('>H', data[pos:pos+2])[0]
                pos += 2 + slen
            elif data[pos] == 0x00:  # number
                pos += 1 + 8
            elif data[pos] == 0x03:  # object
                pos += 1
                while pos + 2 < len(data):
                    kl = struct.unpack('>H', data[pos:pos+2])[0]
                    pos += 2
                    if kl == 0:
                        pos += 1
                        break
                    pos += kl
                    # skip value (simplified - only handle common types)
                    if pos < len(data):
                        m = data[pos]
                        if m == 0x02:
                            pos += 1
                            sl = struct.unpack('>H', data[pos:pos+2])[0]
                            pos += 2 + sl
                        elif m == 0x00:
                            pos += 9
                        elif m in [0x05, 0x01]:
                            pos += 1
                        else:
                            pos += 1

    body_count = struct.unpack('>H', data[pos:pos+2])[0]
    pos += 2

    results = []
    for _ in range(body_count):
        if pos + 2 > len(data):
            break
        target_len = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        target = data[pos:pos+target_len].decode('utf-8', errors='replace')
        pos += target_len
        if pos + 2 > len(data):
            break
        resp_len = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        if pos + 4 > len(data):
            break
        body_len = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4

        if body_len == 0xFFFFFFFF:
            # 未知长度，读取到末尾
            body_data = data[pos:]
        else:
            body_data = data[pos:pos+body_len]
            pos += body_len

        # 解码 body value
        if len(body_data) > 0:
            marker = body_data[0]
            if marker == 0x11:  # AMF3 marker in AMF0
                decoder = AMF3Decoder(body_data, 1)
                val = decoder.read_value()
            else:
                # AMF0 value
                val = decode_amf0_value(body_data, 0)[0]
            results.append((target, val))

    return results

def decode_amf0_value(data, pos):
    """简化的 AMF0 值解码"""
    if pos >= len(data):
        return None, pos
    marker = data[pos]
    pos += 1

    if marker == 0x00:
        if pos + 8 > len(data):
            return None, pos
        return struct.unpack('>d', data[pos:pos+8])[0], pos + 8
    elif marker == 0x01:
        return data[pos] == 1, pos + 1
    elif marker == 0x02:
        slen = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        return data[pos:pos+slen].decode('utf-8', errors='replace'), pos + slen
    elif marker == 0x05:
        return None, pos
    elif marker == 0x0A:
        count = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        arr = []
        for _ in range(count):
            val, pos = decode_amf0_value(data, pos)
            arr.append(val)
        return arr, pos
    elif marker == 0x11:
        decoder = AMF3Decoder(data, pos)
        val = decoder.read_value()
        return val, decoder.pos
    elif marker == 0x03:
        obj = {}
        while pos + 2 < len(data):
            kl = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            if kl == 0 and pos < len(data) and data[pos] == 0x09:
                pos += 1
                break
            key = data[pos:pos+kl].decode('utf-8', errors='replace')
            pos += kl
            val, pos = decode_amf0_value(data, pos)
            obj[key] = val
        return obj, pos
    else:
        return f"<AMF0 marker 0x{marker:02x}>", pos

def send_amf(dest, op, args=None):
    """发送 AMF 请求并返回解码结果"""
    if args is None:
        args = []
    amf_data = build_amf0(dest, op, args)
    resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf'}, timeout=15)
    results = decode_amf_response(resp.content)
    return results

def print_result(dest, op, args=None):
    """发送请求并打印结果"""
    print(f"\n--- {dest}.{op}({args or []}) ---")
    try:
        results = send_amf(dest, op, args)
        if results:
            for target, val in results:
                print(f"  Target: {target}")
                if isinstance(val, dict):
                    cls = val.get('__class__', '')
                    print(f"  Class: {cls}")
                    for k, v in val.items():
                        if k != '__class__':
                            vstr = str(v)
                            if len(vstr) > 200:
                                vstr = vstr[:200] + "..."
                            print(f"    {k}: {vstr}")
                elif isinstance(val, str):
                    print(f"  Value: {val[:500]}")
                elif isinstance(val, list):
                    print(f"  Array ({len(val)} items):")
                    for i, item in enumerate(val[:3]):
                        print(f"    [{i}]: {item}")
                    if len(val) > 3:
                        print(f"    ... ({len(val)-3} more)")
                else:
                    print(f"  Value: {val}")
        else:
            print("  No results decoded")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

# ============================================
# 测试修正后的请求
# ============================================
print("\n=== 1. organizationService.toString ===")
print_result('organizationService', 'toString')

print("\n=== 2. organizationService.getClass ===")
print_result('organizationService', 'getClass')

print("\n=== 3. userService.toString ===")
print_result('userService', 'toString')

print("\n=== 4. organizationService.getChildren ===")
print_result('organizationService', 'getChildren')

print("\n=== 5. organizationService.getAll ===")
print_result('organizationService', 'getAll')

print("\n=== 6. organizationService.getOrganization(['RTN']) ===")
print_result('organizationService', 'getOrganization', ['RTN'])

print("\n=== 7. organizationService.query(['dmBug', 'all']) ===")
print_result('organizationService', 'query', ['dmBug', 'all'])

print("\n=== 8. userService.getUser ===")
print_result('userService', 'getUser')

print("\n=== 9. userService.getCurrentUser ===")
print_result('userService', 'getCurrentUser')

print("\n=== 10. layoutService.toString ===")
print_result('layoutService', 'toString')

print("\n完成")
