"""发送 AMF 请求并输出原始响应字节，分析实际返回内容"""
import requests as req
import struct
import binascii

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
    packet += struct.pack('>I', len(body_array)) + body_array
    header = b'\x00\x00\x00\x00\x00\x01'
    return header + packet

def decode_amf0_response(data):
    """完整解码 AMF0 响应"""
    if len(data) < 8:
        return f"Too short: {binascii.hexlify(data).decode()}"
    version = struct.unpack('>H', data[0:2])[0]
    header_count = struct.unpack('>H', data[2:4])[0]
    pos = 4
    # 跳过 headers
    for _ in range(header_count):
        if pos + 2 > len(data):
            return "Header parse error"
        name_len = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        name = data[pos:pos+name_len].decode('utf-8', errors='replace')
        pos += name_len
        # mustUnderstand (1 byte) + length (4 bytes)
        pos += 1 + 4
        # skip value
        val, pos = decode_amf0_value(data, pos)

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
        resp_len = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        body_len = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        body_data = data[pos:pos+body_len]
        val, _ = decode_amf0_value(body_data, 0)
        results.append((target, val))
        pos += body_len

    return results

def decode_amf0_value(data, pos):
    if pos >= len(data):
        return None, pos
    marker = data[pos]
    pos += 1

    if marker == 0x00:  # number
        if pos + 8 > len(data):
            return None, pos
        val = struct.unpack('>d', data[pos:pos+8])[0]
        return val, pos + 8
    elif marker == 0x01:  # boolean
        return data[pos] == 1, pos + 1
    elif marker == 0x02:  # string
        if pos + 2 > len(data):
            return None, pos
        slen = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        s = data[pos:pos+slen].decode('utf-8', errors='replace')
        return s, pos + slen
    elif marker == 0x03:  # object
        obj = {}
        while pos + 2 < len(data):
            key_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            if key_len == 0:
                if pos < len(data) and data[pos] == 0x09:
                    pos += 1
                break
            key = data[pos:pos+key_len].decode('utf-8', errors='replace')
            pos += key_len
            val, pos = decode_amf0_value(data, pos)
            obj[key] = val
        return obj, pos
    elif marker == 0x05:  # null
        return None, pos
    elif marker == 0x06:  # undefined
        return "undefined", pos
    elif marker == 0x0A:  # strict array
        if pos + 4 > len(data):
            return [], pos
        count = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        arr = []
        for _ in range(count):
            val, pos = decode_amf0_value(data, pos)
            arr.append(val)
        return arr, pos
    elif marker == 0x07:  # long string
        if pos + 4 > len(data):
            return None, pos
        slen = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        s = data[pos:pos+slen].decode('utf-8', errors='replace')
        return s, pos + slen
    elif marker == 0x08:  # XML
        if pos + 4 > len(data):
            return None, pos
        slen = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        s = data[pos:pos+slen].decode('utf-8', errors='replace')
        return f"<XML>{s}</XML>", pos + slen
    elif marker == 0x0B:  # date
        if pos + 10 > len(data):
            return None, pos
        ms = struct.unpack('>d', data[pos:pos+8])[0]
        pos += 8 + 2  # skip timezone
        return f"<date ms={ms}>", pos
    elif marker == 0x0C:  # long string (AMF0)
        if pos + 4 > len(data):
            return None, pos
        slen = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        s = data[pos:pos+slen].decode('utf-8', errors='replace')
        return s, pos + slen
    elif marker == 0x10:  # typed object (AMF0)
        # class name
        if pos + 2 > len(data):
            return None, pos
        cname_len = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        cname = data[pos:pos+cname_len].decode('utf-8', errors='replace')
        pos += cname_len
        # sealed member count (not in AMF0, this is AMF3)
        # Actually in AMF0, typed object is followed by key-value pairs
        obj = {'__class__': cname}
        while pos + 2 < len(data):
            key_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            if key_len == 0:
                if pos < len(data) and data[pos] == 0x09:
                    pos += 1
                break
            key = data[pos:pos+key_len].decode('utf-8', errors='replace')
            pos += key_len
            val, pos = decode_amf0_value(data, pos)
            obj[key] = val
        return obj, pos
    elif marker == 0x11:  # AMF3 marker within AMF0
        # The entire rest is AMF3 format
        val, amf3_pos = decode_amf3_value(data, pos)
        return val, amf3_pos
    else:
        return f"<unknown marker 0x{marker:02x} at pos {pos-1}, remaining: {binascii.hexlify(data[pos:pos+30]).decode() if pos < len(data) else 'EOF'}>", pos

def decode_u29(data, pos):
    """解码 AMF3 U29 整数"""
    if pos >= len(data):
        return 0, pos
    b = data[pos]
    if (b & 0x80) == 0:
        return b >> 1, pos + 1
    elif (b & 0xC0) == 0x80:
        if pos + 1 >= len(data):
            return 0, pos
        val = ((b & 0x3F) << 7) | (data[pos+1] >> 1)
        return val, pos + 2
    elif (b & 0xE0) == 0xC0:
        if pos + 2 >= len(data):
            return 0, pos
        val = ((b & 0x1F) << 14) | (data[pos+1] << 6) | (data[pos+2] >> 1)
        return val, pos + 3
    elif (b & 0xF0) == 0xE0:
        if pos + 3 >= len(data):
            return 0, pos
        val = ((b & 0x0F) << 22) | (data[pos+1] << 14) | (data[pos+2] << 6) | (data[pos+3] >> 1)
        return val, pos + 4
    return 0, pos

# AMF3 字符串/引用表
amf3_string_table = []
amf3_object_table = []

def decode_amf3_value(data, pos, reset_tables=True):
    """解码 AMF3 值"""
    if reset_tables:
        global amf3_string_table, amf3_object_table
        amf3_string_table = []
        amf3_object_table = []

    return _decode_amf3_value(data, pos)

def _decode_amf3_value(data, pos):
    if pos >= len(data):
        return None, pos
    marker = data[pos]
    pos += 1

    if marker == 0x00:  # undefined
        return None, pos
    elif marker == 0x01:  # null
        return None, pos
    elif marker == 0x02:  # false
        return False, pos
    elif marker == 0x03:  # true
        return True, pos
    elif marker == 0x04:  # integer
        val, pos = decode_u29(data, pos)
        if val & 0x10000000:  # sign extend
            val -= 0x20000000
        return val, pos
    elif marker == 0x05:  # double
        if pos + 8 > len(data):
            return None, pos
        val = struct.unpack('>d', data[pos:pos+8])[0]
        return val, pos + 8
    elif marker == 0x06:  # string
        return _decode_amf3_string(data, pos)
    elif marker == 0x07:  # XML
        val, pos = _decode_amf3_string(data, pos)
        return f"<XML>{val}</XML>", pos
    elif marker == 0x08:  # date
        ref, pos = decode_u29(data, pos)
        if (ref & 1) == 0:  # reference
            idx = ref >> 1
            if idx < len(amf3_object_table):
                return amf3_object_table[idx], pos
            return None, pos
        # new date
        if pos + 8 > len(data):
            return None, pos
        ms = struct.unpack('>d', data[pos:pos+8])[0]
        amf3_object_table.append(f"<date ms={ms}>")
        return f"<date ms={ms}>", pos + 8
    elif marker == 0x09:  # array
        ref, pos = decode_u29(data, pos)
        if (ref & 1) == 0:  # reference
            idx = ref >> 1
            if idx < len(amf3_object_table):
                return amf3_object_table[idx], pos
            return None, pos
        # new array
        count = ref >> 1
        # First, associative part (key-value pairs until empty string)
        result = {}
        # Read associative keys
        while pos < len(data):
            key, pos = _decode_amf3_string(data, pos)
            if key == "":  # end of associative part
                break
            val, pos = _decode_amf3_value(data, pos)
            result[key] = val
        # Then dense elements
        arr = []
        for i in range(count):
            val, pos = _decode_amf3_value(data, pos)
            arr.append(val)
        if result:
            result['_array'] = arr
            amf3_object_table.append(result)
            return result, pos
        else:
            amf3_object_table.append(arr)
            return arr, pos
    elif marker == 0x0A:  # object
        ref, pos = decode_u29(data, pos)
        if (ref & 1) == 0:  # reference
            idx = ref >> 1
            if idx < len(amf3_object_table):
                return amf3_object_table[idx], pos
            return None, pos
        # New object
        traits_ref = ref >> 1
        if (traits_ref & 1) == 0:  # traits reference
            # traits are already in table... but we don't track traits separately
            # Just read sealed members
            obj = {}
        else:
            # New traits
            traits_ref = traits_ref >> 1
            # externalizable?
            is_externalizable = (traits_ref & 1) == 1
            traits_ref = traits_ref >> 1
            is_dynamic = (traits_ref & 1) == 1
            traits_ref = traits_ref >> 1
            num_sealed = traits_ref
            # class name
            class_name, pos = _decode_amf3_string(data, pos)
            # property names
            prop_names = []
            for _ in range(num_sealed):
                pname, pos = _decode_amf3_string(data, pos)
                prop_names.append(pname)
            obj = {'__class__': class_name}

        amf3_object_table.append(obj)

        # Read sealed members
        for pname in prop_names:
            val, pos = _decode_amf3_value(data, pos)
            obj[pname] = val

        # Read dynamic members
        if is_dynamic:
            while pos < len(data):
                key, pos = _decode_amf3_string(data, pos)
                if key == "":
                    break
                val, pos = _decode_amf3_value(data, pos)
                obj[key] = val

        # If externalizable, read external data
        if is_externalizable:
            # For Flex ActionResult, typically has message body
            external, pos = _decode_amf3_value(data, pos)
            obj['__external__'] = external

        return obj, pos
    elif marker == 0x0B:  # XML (document)
        val, pos = _decode_amf3_string(data, pos)
        return f"<XMLDoc>{val}</XMLDoc>", pos
    elif marker == 0x0C:  # byte array
        ref, pos = decode_u29(data, pos)
        if (ref & 1) == 0:  # reference
            idx = ref >> 1
            if idx < len(amf3_object_table):
                return amf3_object_table[idx], pos
            return None, pos
        length = ref >> 1
        raw = data[pos:pos+length]
        amf3_object_table.append(raw)
        return raw, pos + length
    else:
        return f"<unknown AMF3 marker 0x{marker:02x} at pos {pos-1}>", pos

def _decode_amf3_string(data, pos):
    global amf3_string_table
    ref, pos = decode_u29(data, pos)
    if (ref & 1) == 0:  # reference
        idx = ref >> 1
        if idx < len(amf3_string_table):
            return amf3_string_table[idx], pos
        return "", pos
    length = ref >> 1
    s = data[pos:pos+length].decode('utf-8', errors='replace')
    if s:
        amf3_string_table.append(s)
    return s, pos + length

def send_and_decode(dest, op, args=None, label=None):
    """发送 AMF 请求并解码响应"""
    if args is None:
        args = []
    if label:
        print(f"\n--- {label} ---")
    amf_data = build_amf(dest, op, args)
    resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf'}, timeout=15)

    print(f"  响应大小: {len(resp.content)} bytes")
    print(f"  响应前 100 字节: {binascii.hexlify(resp.content[:100]).decode()}")

    try:
        result = decode_amf0_response(resp.content)
        if isinstance(result, list):
            for target, val in result:
                print(f"  Target: {target}")
                print(f"  Value: {val}")
                if isinstance(val, dict):
                    for k, v in val.items():
                        print(f"    {k}: {v}")
                elif isinstance(val, str):
                    print(f"  String: {val[:500]}")
                elif isinstance(val, list):
                    print(f"  Array ({len(val)} items):")
                    for i, item in enumerate(val[:5]):
                        print(f"    [{i}]: {item}")
                    if len(val) > 5:
                        print(f"    ... ({len(val)-5} more)")
        else:
            print(f"  Result: {result}")
        return result
    except Exception as e:
        print(f"  解码错误: {e}")
        # 输出原始 hex
        print(f"  原始数据: {binascii.hexlify(resp.content[:200]).decode()}")
        return None

# 测试关键方法
print("\n=== 1. organizationService.toString ===")
send_and_decode('organizationService', 'toString')

print("\n=== 2. organizationService.getClass ===")
send_and_decode('organizationService', 'getClass')

print("\n=== 3. organizationService.getAll ===")
send_and_decode('organizationService', 'getAll')

print("\n=== 4. organizationService.getOrganization(['RTN']) ===")
send_and_decode('organizationService', 'getOrganization', ['RTN'])

print("\n=== 5. organizationService.getProjects(['RTN']) ===")
send_and_decode('organizationService', 'getProjects', ['RTN'])

print("\n=== 6. organizationService.getBugs(['RTN']) ===")
send_and_decode('organizationService', 'getBugs', ['RTN'])

print("\n=== 7. organizationService.query(['dmBug', 'all']) ===")
send_and_decode('organizationService', 'query', ['dmBug', 'all'])

print("\n=== 8. organizationService.getChildren() ===")
send_and_decode('organizationService', 'getChildren')

print("\n=== 9. organizationService.getTree() ===")
send_and_decode('organizationService', 'getTree')

print("\n=== 10. organizationService.getOrganizationTree() ===")
send_and_decode('organizationService', 'getOrganizationTree')

print("\n完成")
