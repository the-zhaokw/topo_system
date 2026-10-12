"""调试 SWF 解压缩"""
import requests as req
import zlib
import struct
from hashlib import md5
from Crypto.Cipher import DES

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

# 下载 SWF
url = 'http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf'
r = session.get(url, timeout=120)
raw = r.content
print(f"原始大小: {len(raw)} bytes")
print(f"原始前16字节: {raw[:16].hex()}")

# DES 解密
KEY = md5(b'hzytkjyxgs').digest()[:8]
cipher = DES.new(KEY, DES.MODE_ECB)
padded_len = (len(raw) // 8) * 8
decrypted = cipher.decrypt(raw[:padded_len]) + raw[padded_len:]
print(f"解密后大小: {len(decrypted)} bytes")
print(f"解密后前16字节: {decrypted[:16].hex()}")

# 解析 SWF 头
signature = decrypted[:3]
version = decrypted[3]
file_length = struct.unpack('<I', decrypted[4:8])[0]
print(f"\nSWF 签名: {signature}")
print(f"SWF 版本: {version}")
print(f"SWF 文件长度: {file_length} bytes")

# 检查 zlib 头
zlib_data = decrypted[8:]
print(f"\nZlib 数据前16字节: {zlib_data[:16].hex()}")
print(f"Zlib CMF: {zlib_data[0]:02x} (CM={zlib_data[0] & 0x0f}, CINFO={zlib_data[0] >> 4})")
print(f"Zlib FLG: {zlib_data[1]:02x} (FCHECK={zlib_data[1] & 0x1f}, FDICT={(zlib_data[1] >> 5) & 1}, FLEVEL={zlib_data[1] >> 6})")
print(f"Zlib 校验: {(zlib_data[0] * 256 + zlib_data[1]) % 31 == 0}")

# 尝试直接解压
print("\n=== 尝试解压 ===")

# 方法1: 直接 decompress
try:
    result = zlib.decompress(zlib_data)
    print(f"方法1 (zlib.decompress): 成功! {len(result)} bytes")
except zlib.error as e:
    print(f"方法1 (zlib.decompress): 失败 - {e}")

# 方法2: decompressobj
try:
    dec_obj = zlib.decompressobj()
    result = dec_obj.decompress(zlib_data)
    result += dec_obj.flush()
    print(f"方法2 (decompressobj): 成功! {len(result)} bytes")
except zlib.error as e:
    print(f"方法2 (decompressobj): 失败 - {e}")

# 方法3: 逐步解压, 找到错误位置
print("\n=== 逐步解压定位错误 ===")
dec_obj = zlib.decompressobj()
total_in = 0
total_out = 0
chunk_size = 1024 * 64  # 64KB chunks
error_pos = None
for i in range(0, len(zlib_data), chunk_size):
    chunk = zlib_data[i:i+chunk_size]
    try:
        out = dec_obj.decompress(chunk)
        total_out += len(out)
        total_in += len(chunk)
    except zlib.error as e:
        error_pos = i
        print(f"  错误在偏移 {i} ({i/len(zlib_data)*100:.1f}%): {e}")
        print(f"  已成功解压: {total_out} bytes (输入 {total_in} bytes)")
        break

if error_pos is None:
    try:
        out = dec_obj.flush()
        total_out += len(out)
        print(f"  全部解压成功! {total_out} bytes")
    except:
        print(f"  flush 失败, 但已解压 {total_out} bytes")
else:
    # 尝试从错误位置后继续解压
    print(f"\n  尝试从错误位置后继续...")
    for offset in [error_pos + 1, error_pos + 2, error_pos + 8, error_pos + 16, error_pos + 32]:
        try:
            dec_obj2 = zlib.decompressobj()
            result = dec_obj2.decompress(zlib_data[offset:])
            print(f"    从偏移 {offset} 继续: 成功! {len(result)} bytes")
            break
        except:
            pass

# 方法4: 尝试 LZMA
print("\n=== 尝试 LZMA ===")
try:
    import lzma
    result = lzma.decompress(zlib_data)
    print(f"LZMA: 成功! {len(result)} bytes")
except Exception as e:
    print(f"LZMA: 失败 - {e}")

# 方法5: 检查是否 DES 只加密了部分文件
print("\n=== 检查部分加密 ===")
# 也许只有文件头部分被加密, 其余是原始数据
# 尝试: 不解密, 直接使用原始数据
print(f"原始数据前3字节: {raw[:3]}")
print(f"原始数据前8字节: {raw[:8].hex()}")

# 也许文件是 SWF 头(8字节) 未加密 + 加密的 zlib body
header = raw[:8]
body_encrypted = raw[8:]
cipher2 = DES.new(KEY, DES.MODE_ECB)
body_padded = (len(body_encrypted) // 8) * 8
body_decrypted = cipher2.decrypt(body_encrypted[:body_padded]) + body_encrypted[body_padded:]

# 构造完整的 SWF: 头 + 解密后的 body
# 但头也是加密的 (raw 前3字节不是 FWS/CWS)
# 所以整个文件都是加密的

# 也许 DES 只加密了前面的部分?
# 检查解密后的数据在中间是否有第二个 SWF 头
print("\n=== 搜索多个 CWS/FWS 头 ===")
import re
swf_headers = [(m.start(), m.group()) for m in re.finditer(rb'(CWS|FWS|ZWS)', decrypted)]
print(f"SWF 头位置: {len(swf_headers)}")
for pos, sig in swf_headers[:10]:
    ver = decrypted[pos+3] if pos+3 < len(decrypted) else '?'
    print(f"  偏移 {pos}: {sig.decode()} 版本 {ver}")

# 方法6: 尝试 wbits=-15 (raw deflate, 无 zlib 头)
print("\n=== 尝试 raw deflate ===")
for offset in [8, 10, 11, 12]:
    for wb in [-15, 15, 31, 47]:
        try:
            dec_obj = zlib.decompressobj(wbits=wb)
            result = dec_obj.decompress(decrypted[offset:])
            result += dec_obj.flush()
            print(f"  offset={offset} wbits={wb}: 成功! {len(result)} bytes")
            break
        except zlib.error as e:
            pass

# 方法7: 也许文件在加密前有额外的包装
# 检查解密后数据中间是否有 zlib 头 (78 9C, 78 DA, 78 01)
print("\n=== 搜索 zlib 头 ===")
zlib_headers = []
for i in range(len(decrypted) - 1):
    if decrypted[i] == 0x78 and decrypted[i+1] in [0x01, 0x9c, 0xda]:
        zlib_headers.append((i, decrypted[i+1]))
print(f"找到 {len(zlib_headers)} 个 zlib 头")
for pos, flag in zlib_headers[:10]:
    print(f"  偏移 {pos}: 78{flag:02x}")
    # 尝试从这个位置解压
    try:
        result = zlib.decompress(decrypted[pos:])
        print(f"    => 解压成功! {len(result)} bytes")
        # 如果成功, 保存结果
        with open(f'd:/topo_system/backend/module_decompressed_from_{pos}.bin', 'wb') as f:
            f.write(result)
        break
    except zlib.error as e:
        print(f"    => 解压失败: {e}")
