"""尝试 AMF3 格式和 Liferay JSON API"""
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

# ============================================
# 1. 测试 Liferay JSON API
# ============================================
print("\n=== 1. 测试 Liferay JSON API ===")

liferay_endpoints = [
    '/api/jsonws/',
    '/api/jsonws/invoke',
    '/api/secure/jsonws/',
    '/jsonws/',
    '/api/json',
    '/jsonrpc',
]

for endpoint in liferay_endpoints:
    url = f'http://172.18.36.5:8000{endpoint}'
    try:
        resp = session.get(url, timeout=5)
        print(f"  GET {endpoint}: {resp.status_code}")
        if resp.status_code == 200 and len(resp.text) > 50:
            print(f"    Body: {resp.text[:300]}")
    except:
        print(f"  GET {endpoint}: 超时")

# 测试 invoke
for endpoint in ['/api/jsonws/invoke', '/api/secure/jsonws/invoke']:
    url = f'http://172.18.36.5:8000{endpoint}'
    try:
        resp = session.post(url, data='{}', headers={'Content-Type': 'application/json'}, timeout=5)
        print(f"  POST {endpoint}: {resp.status_code}")
        if resp.status_code in [200, 400, 401, 403]:
            print(f"    Body: {resp.text[:300]}")
    except:
        pass

# ============================================
# 2. 尝试 AMF3 格式
# ============================================
print("\n=== 2. 尝试 AMF3 格式 ===")

def build_amf3_request(destination, operation, args=None):
    """构造 AMF3 格式的请求"""
    if args is None:
        args = []

    # AMF3 编码函数
    def amf3_string(s):
        """AMF3 string 编码 - 使用 U29 编码"""
        data = b'\x06'  # string type marker
        b = s.encode('utf-8')
        length = len(b)
        # U29: if length <= 0x7F, 1 byte; if <= 0x3FFF, 2 bytes; if <= 0x1FFFFF, 3 bytes
        # The last bit is set to indicate this is a string reference, not an integer
        length = (length << 1) | 1  # set lowest bit to 1 (not a reference)
        if length <= 0x7F:
            data += bytes([length])
        elif length <= 0x3FFF:
            data += bytes([(length >> 7) | 0x80, length & 0x7F])
        elif length <= 0x1FFFFF:
            data += bytes([(length >> 14) | 0x80, (length >> 7) | 0x80, length & 0x7F])
        else:
            data += bytes([(length >> 22) | 0x80, (length >> 15) | 0x80, (length >> 8) | 0x80, length & 0xFF])
        data += b
        return data

    def amf3_integer(n):
        """AMF3 integer encoding"""
        if n < 0:
            # Negative numbers are 4 bytes in AMF3
            data = b'\x04'  # integer type marker
            data += struct.pack('>I', n & 0x1FFFFFFF | 0x20000000)
            return data
        elif n <= 0x7F:
            return b'\x04' + bytes([n << 1 | 1])  # Actually AMF3 integer is different
        # Let me simplify - just use double for numbers
        return amf3_double(float(n))

    def amf3_double(n):
        """AMF3 double encoding"""
        return b'\x05' + struct.pack('>d', float(n))

    def amf3_null():
        return b'\x01'  # null

    def amf3_false():
        return b'\x02'  # false

    def amf3_true():
        return b'\x03'  # true

    def amf3_array(items):
        """AMF3 array encoding"""
        data = b'\x09'  # array type marker
        count = len(items)
        # U29 with count: (count << 1) | 0 (no associative part)
        count_enc = (count << 1) | 0
        if count_enc <= 0x7F:
            data += bytes([count_enc])
        elif count_enc <= 0x3FFF:
            data += bytes([(count_enc >> 7) | 0x80, count_enc & 0x7F])
        elif count_enc <= 0x1FFFFF:
            data += bytes([(count_enc >> 14) | 0x80, (count_enc >> 7) | 0x80, count_enc & 0x7F])
        else:
            data += bytes([(count_enc >> 22) | 0x80, (count_enc >> 15) | 0x80, (count_enc >> 8) | 0x80, count_enc & 0xFF])
        # Empty associative part marker (end of associative)
        # If no associative part, the count encoding has lowest bit = 0
        # And no empty string marker needed
        for item in items:
            if isinstance(item, str):
                data += amf3_string(item)
            elif isinstance(item, (int, float)):
                data += amf3_double(item)
            elif item is None:
                data += amf3_null()
            elif isinstance(item, bool):
                data += amf3_true() if item else amf3_false()
            else:
                data += amf3_null()
        return data

    def amf3_object(fields, class_name=''):
        """AMF3 object encoding (anonymous or typed)"""
        data = b'\x0A'  # object type marker
        # Traits: (traits_ref << 2) | 0b11 (0b11 = 0x03 means new traits, not a reference)
        # U29Traits: (0 << 2) | 3 = 3
        traits = 0x03  # new traits, not externalizable, not dynamic
        data += bytes([traits])
        # Class name (empty string for anonymous, or actual class name)
        data += amf3_string(class_name)[1:]  # remove type marker, just the U29 + string
        # Wait, the class name is encoded as a regular AMF3 string but without the type marker
        # Actually in AMF3 object encoding, after the traits flag, the class name is a U29 length + string
        # Let me reconsider...

        # Actually, for AMF3 typed object:
        # 1. Type marker: 0x0A
        # 2. U29Traits: (class_name_is_not_empty << 1) | (is_dynamic << 1) | (is_externalizable << 1) | is_new_traits
        # Actually this is complex. Let me just use a simple anonymous object.

        # For anonymous object:
        # Type marker: 0x0A
        # U29Traits: 0x03 (new traits, not externalizable, not dynamic, sealed)
        # Class name: empty string (U29 length 0x01 = length 0, no reference)
        # Sealed member count: U29 (count)
        # Member names: list of strings
        # Member values: list of values
        # Or for dynamic object:
        # U29Traits: 0x07 (new traits, dynamic, not externalizable)

        # Let me use dynamic object (traits = 0x07)
        data = b'\x0A'  # object type marker
        data += bytes([0x07])  # traits: new, dynamic, not externalizable
        # Class name (empty = anonymous)
        data += bytes([0x01])  # empty string (U29: 0 = length 0, shifted left 1 = 0, | 1 = 1)
        # Sealed member count: 0
        data += bytes([0x01])  # 0 members (U29: 0 << 1 | 1 = 1... wait this is wrong)
        # Actually: sealed member count is a U29 where the value is count << 1 | 0
        # No wait, the traits encoding is different:
        # U29Traits: the value is (traits << 1) | new_traits_flag
        # For new traits (new_traits_flag = 1): (traits_value << 1) | 1
        # traits_value includes: is_dynamic (1 bit), is_externalizable (1 bit), sealed_count (29 bits)
        # For dynamic object with 0 sealed members: traits_value = (1 << 1) | 0 = 2 (dynamic=1, externalizable=0)
        # But then shifted: (2 << 1) | 1 = 5 = 0x05
        # Hmm, this is getting complicated. Let me just use AMF0 format instead.

        return None  # Give up on AMF3 for now

    # AMF3 packet: version 0x0003, headers, bodies
    # Body: target URI, response URI, content (AMF3 encoded)
    msg_id = str(uuid.uuid4())

    # Try with AMF0 body but AMF3 packet version
    # Sometimes BlazeDS accepts AMF0 body with version 3

    # Build body as AMF0 (simple object with destination and operation)
    def enc_str(s):
        b = s.encode('utf-8')
        return b'\x02' + struct.pack('>H', len(b)) + b

    def enc_num(n):
        return b'\x00' + struct.pack('>d', float(n))

    def enc_null():
        return b'\x05'

    # Body array
    body_items = b''
    for arg in (args or []):
        if isinstance(arg, str):
            body_items += enc_str(arg)
        elif isinstance(arg, (int, float)):
            body_items += enc_num(arg)
        elif arg is None:
            body_items += enc_null()
        else:
            body_items += enc_null()

    body_array = b'\x0A' + struct.pack('>I', len(args or [])) + body_items

    # RemotingMessage as AMF0 object
    fields = [
        (b'source', enc_null()),
        (b'operation', enc_str(operation)),
        (b'destination', enc_str(destination)),
        (b'messageId', enc_str(msg_id)),
        (b'timestamp', enc_num(0.0)),
        (b'timeToLive', enc_num(0.0)),
        (b'body', body_array),
        (b'clientId', enc_null()),
    ]

    msg = b'\x03'  # AMF0 object type
    for key, value in fields:
        msg += struct.pack('>H', len(key)) + key + value
    msg += b'\x00\x00\x09'

    # Packet with version 0x0003 (AMF3) but AMF0 body
    packet = b'\x00\x03'  # version AMF3
    packet += b'\x00\x00'  # header count = 0
    packet += b'\x00\x01'  # body count = 1
    packet += struct.pack('>H', 4) + b'null'  # target URI
    packet += struct.pack('>H', 0)  # response URI
    packet += struct.pack('>I', len(msg))
    packet += msg

    return packet

AMF_URL = 'http://172.18.36.5:8000/messagebroker/amf'

# AMF3 version packet with AMF0 body
print("=== AMF3 version packet ===")
amf_data = build_amf3_request('userService', 'getAll')
resp = session.post(AMF_URL, data=amf_data, headers={'Content-Type': 'application/x-amf'}, timeout=10)
print(f"响应: {resp.status_code}, {len(resp.content)} bytes")
strs = re.findall(rb'[\x20-\x7e]{5,}', resp.content)
for s in strs[:20]:
    print(f"  {s.decode('ascii', errors='ignore')}")

# ============================================
# 3. 尝试用 AMF3 RemotingMessage (typed object)
# ============================================
print("\n=== 3. 尝试 AMF0 typed RemotingMessage ===")

def enc_str(s):
    b = s.encode('utf-8')
    return b'\x02' + struct.pack('>H', len(b)) + b

def enc_num(n):
    return b'\x00' + struct.pack('>d', float(n))

def enc_null():
    return b'\x05'

def enc_typed_obj(class_name, fields):
    """AMF0 typed object (0x10)"""
    data = b'\x10'
    cb = class_name.encode('utf-8')
    data += struct.pack('>H', len(cb)) + cb
    for key, value in fields:
        kb = key.encode('utf-8')
        data += struct.pack('>H', len(kb)) + kb
        data += value
    data += b'\x00\x00\x09'
    return data

# Try with flex.messaging.messages.RemotingMessage typed object
msg_id = str(uuid.uuid4())
body_array = b'\x0A' + struct.pack('>I', 0)  # empty array

fields = [
    (b'source', enc_null()),
    (b'operation', enc_str('getAll')),
    (b'destination', enc_str('userService')),
    (b'messageId', enc_str(msg_id)),
    (b'timestamp', enc_num(0.0)),
    (b'timeToLive', enc_num(0.0)),
    (b'body', body_array),
    (b'clientId', enc_null()),
]

msg = enc_typed_obj('flex.messaging.messages.RemotingMessage', fields)

# AMF0 packet with typed object
packet = b'\x00\x00'  # AMF0 version
packet += b'\x00\x00'  # no headers
packet += b'\x00\x01'  # 1 body
packet += struct.pack('>H', 4) + b'null'  # target
packet += struct.pack('>H', 0)  # response
packet += struct.pack('>I', len(msg))
packet += msg

resp = session.post(AMF_URL, data=packet, headers={'Content-Type': 'application/x-amf'}, timeout=10)
print(f"AMF0 typed RemotingMessage: {resp.status_code}, {len(resp.content)} bytes")
strs = re.findall(rb'[\x20-\x7e]{5,}', resp.content)
for s in strs[:20]:
    print(f"  {s.decode('ascii', errors='ignore')}")

# ============================================
# 4. 尝试 AMF3 RemotingMessage
# ============================================
print("\n=== 4. 尝试 AMF3 RemotingMessage ===")

# AMF3 RemotingMessage format:
# 1. AMF0 header: 0x11 (AMF3 marker) followed by AMF3 data
# 2. AMF3 data: typed object with class name "flex.messaging.messages.RemotingMessage"

# Let me try: version 0x0003, body content starts with 0x11 (AMF3 marker)
# then AMF3 encoded typed object

def amf3_u29(n):
    """Encode U29 integer"""
    if n <= 0x7F:
        return bytes([n])
    elif n <= 0x3FFF:
        return bytes([(n >> 7) | 0x80, n & 0x7F])
    elif n <= 0x1FFFFF:
        return bytes([(n >> 14) | 0x80, (n >> 7) | 0x80, n & 0x7F])
    else:
        return bytes([(n >> 22) | 0x80, (n >> 15) | 0x80, (n >> 8) | 0x80, n & 0xFF])

def amf3_string_val(s):
    """Encode AMF3 string (U29 length | 1 + string bytes)"""
    b = s.encode('utf-8')
    length = len(b)
    # String U29: (length << 1) | 1 (not a reference)
    return amf3_u29((length << 1) | 1) + b

def amf3_str(s):
    """AMF3 string value"""
    return b'\x06' + amf3_string_val(s)

def amf3_double(n):
    return b'\x05' + struct.pack('>d', float(n))

def amf3_null():
    return b'\x01'

def amf3_false():
    return b'\x02'

def amf3_true():
    return b'\x03'

def amf3_int(n):
    if 0 <= n <= 0x1FFFFFFF:
        return b'\x04' + amf3_u29(n)
    else:
        return amf3_double(float(n))

def amf3_array(items):
    """AMF3 array (dense)"""
    count = len(items)
    # U29 value: (count << 1) | 0 (no associative)
    u29 = amf3_u29((count << 1) | 0)
    data = b'\x09' + u29
    # If no associative part, we need to mark the end
    # For dense-only array: the U29 with lowest bit 0 means dense
    # But we still need an empty string to end the associative part if bit is 0
    # Wait, if (count << 1) | 0, it means no associative entries
    # The associative part is empty, marked by an empty string (U29 0x01 = length 0)
    data += b'\x01'  # empty string (end of associative part) -- NO, this is wrong
    # Actually for AMF3 array:
    # If U29 lowest bit is 0: it's a dense array with `count` elements
    # If U29 lowest bit is 1: it's a reference
    # Hmm, let me re-read the spec...
    # AMF3 Array:
    # U29 value:
    #   if (value & 1) == 1: it's a reference
    #   if (value & 1) == 0: count = value >> 1
    #     Then: associative entries (key-value pairs until empty string marker)
    #     Then: `count` dense values
    # For a pure dense array with no associative entries:
    #   U29 = (count << 1) | 0
    #   Then empty string marker (U29 0x01 = length 0, not reference)
    #   Then `count` values

    # Wait, I need to re-read. The U29:
    # if (u29 & 1) == 1: reference to previous array
    # if (u29 & 1) == 0: count = u29 >> 1, followed by:
    #   - associative entries (key=value) until empty string key
    #   - then `count` dense values

    # So for a dense-only array of 0 items:
    # U29 = 0 (count=0, no associative)
    # Empty string marker (to end associative)
    # Then 0 values

    # For dense array of 2 items:
    # U29 = 4 (count=2, no associative)
    # Empty string marker
    # value1, value2

    data = b'\x09' + amf3_u29(count << 1)
    data += bytes([0x01])  # empty string (end associative)
    for item in items:
        data += item
    return data

def amf3_typed_object(class_name, fields):
    """AMF3 typed object"""
    data = b'\x0A'  # object type marker

    # Traits:
    # U29Traits value:
    # if (value & 1) == 1: reference to previous traits
    # if (value & 1) == 0: new traits
    #   is_dynamic = (value >> 1) & 1
    #   is_externalizable = (value >> 2) & 1
    #   sealed_count = value >> 3

    # For new traits, dynamic, not externalizable, 0 sealed members:
    # value = (0 << 3) | (0 << 2) | (1 << 1) | 0 = 2
    # But wait, U29Traits: lowest bit = 0 means new traits
    # So value = (sealed_count << 4) | (is_externalizable << 3) | (is_dynamic << 2) | (new_traits << 0)
    # Hmm, I'm confusing myself. Let me look at the actual spec.

    # AMF3 Object:
    # Type: 0x0A
    # U29Traits:
    #   if (traits & 1) == 1: traits reference
    #   if (traits & 1) == 0: new traits definition
    #     sealed_count = traits >> 4
    #     is_dynamic = (traits >> 3) & 1
    #     is_externalizable = (traits >> 2) & 1  -- wait no

    # Actually from the AMF3 spec:
    # traits_ref_flag = traits & 1
    # if not reference:
    #   dynamic_flag = (traits >> 1) & 1  -- wait no
    # Let me just use the standard:
    # traits value:
    #   bit 0: 0 = new traits, 1 = reference
    #   bit 1: 0 = not externalizable, 1 = externalizable
    #   bit 2: 0 = not dynamic, 1 = dynamic
    #   bits 3+: sealed member count

    # For new traits, dynamic, not externalizable, 0 sealed:
    # value = (0 << 4) | (1 << 2) | (0 << 1) | 0 = 4

    # Wait, I think the encoding is:
    # value = (sealed_count << 4) | (is_dynamic << 2) | (is_externalizable << 1) | 0
    # For dynamic, 0 sealed: (0 << 4) | (1 << 2) | (0 << 1) | 0 = 4

    # Actually let me just look at a known implementation.
    # From PyAMF source: traits = (member_count << 4) | (dynamic << 3) | (externalizable << 2) | (trait_ref_flag)
    # Wait no, from the actual AMF3 spec:
    # u29Traits value:
    # if (value & 1) == 1: traits reference (index = value >> 1)
    # if (value & 1) == 0: new traits
    #   is_dynamic = (value >> 1) & 1
    #   is_externalizable = (value >> 2) & 1
    #   sealed_count = value >> 3

    # So for new traits, dynamic, not externalizable, 0 sealed:
    # value = (0 << 3) | (0 << 2) | (1 << 1) | 0 = 2

    # Hmm, but that means bit 0 = 0 (new traits), bit 1 = 1 (dynamic), bit 2 = 0 (not externalizable), bits 3+ = sealed_count
    # value = (0 << 3) | (0 << 2) | (1 << 1) | 0 = 2

    # Let me try both: 2 (dynamic, 0 sealed) and 3 (dynamic + externalizable? no...)
    # Actually I think for a sealed (non-dynamic) object with 2 members:
    # value = (2 << 3) | (0 << 2) | (0 << 1) | 0 = 16

    # For dynamic object with 0 sealed members:
    # value = (0 << 3) | (0 << 2) | (1 << 1) | 0 = 2

    # Let me use a dynamic object:
    traits_val = 0x02  # new traits, dynamic, not externalizable, 0 sealed
    data += amf3_u29(traits_val)

    # Class name
    data += amf3_string_val(class_name)

    # No sealed members (0 count)
    # No sealed member values

    # Dynamic members (key=value pairs)
    for key, value in fields:
        data += amf3_string_val(key)
        data += value

    # End of dynamic members: empty string
    data += bytes([0x01])  # empty string

    return data

# Build AMF3 RemotingMessage
msg_id = str(uuid.uuid4())

amf3_body = amf3_array([])  # empty array for body

fields = [
    (b'source', amf3_null()),
    (b'operation', amf3_str('getAll')),
    (b'destination', amf3_str('userService')),
    (b'messageId', amf3_str(msg_id)),
    (b'timestamp', amf3_double(0.0)),
    (b'timeToLive', amf3_double(0.0)),
    (b'body', amf3_body),
    (b'clientId', amf3_null()),
]

amf3_msg = amf3_typed_object('flex.messaging.messages.RemotingMessage', fields)

# AMF3 packet: version 0x0003
# Body: target = "null", response = "", content starts with 0x11 (AMF3 marker) then AMF3 data
packet = b'\x00\x03'  # version AMF3
packet += b'\x00\x00'  # no headers
packet += b'\x00\x01'  # 1 body
packet += struct.pack('>H', 4) + b'null'  # target
packet += struct.pack('>H', 0)  # response
packet += struct.pack('>I', len(amf3_msg) + 1)  # +1 for the AMF3 marker
packet += b'\x11'  # AMF3 marker
packet += amf3_msg

resp = session.post(AMF_URL, data=packet, headers={'Content-Type': 'application/x-amf'}, timeout=10)
print(f"AMF3 RemotingMessage: {resp.status_code}, {len(resp.content)} bytes")
strs = re.findall(rb'[\x20-\x7e]{5,}', resp.content)
for s in strs[:20]:
    print(f"  {s.decode('ascii', errors='ignore')}")

# ============================================
# 5. 尝试 transmitfile 端点
# ============================================
print("\n=== 5. 测试 transmitfile 端点 ===")
for cmd in ['upload', 'download', 'delete']:
    url = f'http://172.18.36.5:8000/transmitfile?cmd={cmd}'
    resp = session.get(url, timeout=5)
    print(f"  {cmd}: {resp.status_code}, {len(resp.content)} bytes")
    if len(resp.content) < 500:
        print(f"    Body: {resp.content[:200]}")

# ============================================
# 6. 尝试直接访问 Liferay portal API 获取用户信息
# ============================================
print("\n=== 6. 测试 Liferay Portal API ===")
liferay_api = [
    '/c/portal/layout?p_l_id=1',
    '/c/user/get-current-user',
    '/api/secure/jsonws/user/get-current-user',
    '/c/portal/session_click',
    '/c/portal/jsonservice',
]
for path in liferay_api:
    url = f'http://172.18.36.5:8000{path}'
    try:
        resp = session.get(url, timeout=5)
        print(f"  {path}: {resp.status_code}")
        if resp.status_code == 200 and len(resp.text) < 1000:
            print(f"    Body: {resp.text[:200]}")
    except:
        print(f"  {path}: 超时")
