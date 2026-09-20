"""尝试 DES-CBC 解密 draco_module.swf"""
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

KEY = md5(b'hzytkjyxgs').digest()[:8]

# === 1. DES-ECB (之前的尝试) ===
print("\n=== 1. DES-ECB (之前) ===")
cipher_ecb = DES.new(KEY, DES.MODE_ECB)
padded_len = (len(raw) // 8) * 8
dec_ecb = cipher_ecb.decrypt(raw[:padded_len]) + raw[padded_len:]
print(f"ECB 解密前16字节: {dec_ecb[:16].hex()}")
print(f"ECB SWF 头: {dec_ecb[:3]}")

try:
    result = zlib.decompress(dec_ecb[8:])
    print(f"ECB zlib 解压: 成功! {len(result)} bytes")
except zlib.error as e:
    print(f"ECB zlib 解压: 失败 - {e}")

# === 2. DES-CBC, IV = 全零 ===
print("\n=== 2. DES-CBC, IV = 全零 ===")
cipher_cbc0 = DES.new(KEY, DES.MODE_CBC, iv=b'\x00' * 8)
dec_cbc0 = cipher_cbc0.decrypt(raw[:padded_len]) + raw[padded_len:]
print(f"CBC(IV=0) 前16字节: {dec_cbc0[:16].hex()}")
print(f"CBC(IV=0) SWF 头: {dec_cbc0[:3]}")

try:
    result = zlib.decompress(dec_cbc0[8:])
    print(f"CBC(IV=0) zlib 解压: 成功! {len(result)} bytes")
    # 如果成功, 保存结果
    with open('d:/topo_system/backend/draco_module_decrypted.swf', 'wb') as f:
        f.write(dec_cbc0[:8] + result)
    print("已保存解密解压后的 SWF")
except zlib.error as e:
    print(f"CBC(IV=0) zlib 解压: 失败 - {e}")

# === 3. DES-CBC, IV = 文件前8字节 ===
print("\n=== 3. DES-CBC, IV = 文件前8字节 ===")
iv1 = raw[:8]
cipher_cbc1 = DES.new(KEY, DES.MODE_CBC, iv=iv1)
dec_cbc1 = cipher_cbc1.decrypt(raw[8:padded_len])
# 前面的8字节用ECB解密
cipher_ecb2 = DES.new(KEY, DES.MODE_ECB)
header_dec = cipher_ecb2.decrypt(raw[:8])
dec_cbc1_full = header_dec + dec_cbc1 + raw[padded_len:]
print(f"CBC(IV=raw[:8]) 前16字节: {dec_cbc1_full[:16].hex()}")
print(f"CBC(IV=raw[:8]) SWF 头: {dec_cbc1_full[:3]}")

try:
    result = zlib.decompress(dec_cbc1_full[8:])
    print(f"CBC(IV=raw[:8]) zlib 解压: 成功! {len(result)} bytes")
except zlib.error as e:
    print(f"CBC(IV=raw[:8]) zlib 解压: 失败 - {e}")

# === 4. DES-CBC, IV = MD5(key)[:8] ===
print("\n=== 4. DES-CBC, IV = MD5(key)[:8] ===")
iv2 = md5(KEY).digest()[:8]
cipher_cbc2 = DES.new(KEY, DES.MODE_CBC, iv=iv2)
dec_cbc2 = cipher_cbc2.decrypt(raw[:padded_len]) + raw[padded_len:]
print(f"CBC(IV=md5(key)[:8]) 前16字节: {dec_cbc2[:16].hex()}")
print(f"CBC(IV=md5(key)[:8]) SWF 头: {dec_cbc2[:3]}")

try:
    result = zlib.decompress(dec_cbc2[8:])
    print(f"CBC(IV=md5(key)[:8]) zlib 解压: 成功! {len(result)} bytes")
except zlib.error as e:
    print(f"CBC(IV=md5(key)[:8]) zlib 解压: 失败 - {e}")

# === 5. DES3 (Triple DES) ECB ===
print("\n=== 5. DES3 (Triple DES) ECB ===")
from Crypto.Cipher import DES3
try:
    # Triple DES 需要 16 或 24 字节的 key
    key3 = md5(b'hzytkjyxgs').digest()  # 16 bytes
    cipher_3des = DES3.new(key3, DES3.MODE_ECB)
    dec_3des = cipher_3des.decrypt(raw[:padded_len]) + raw[padded_len:]
    print(f"3DES 前16字节: {dec_3des[:16].hex()}")
    print(f"3DES SWF 头: {dec_3des[:3]}")

    try:
        result = zlib.decompress(dec_3des[8:])
        print(f"3DES zlib 解压: 成功! {len(result)} bytes")
    except zlib.error as e:
        print(f"3DES zlib 解压: 失败 - {e}")
except Exception as e:
    print(f"3DES 错误: {e}")

# === 6. AES ECB ===
print("\n=== 6. AES ECB ===")
from Crypto.Cipher import AES
# AES key 可以是 16, 24, 或 32 字节
for key_size, key_name in [(16, 'MD5[:16]'), (24, 'MD5+MD5[:24]'), (32, 'MD5+MD5[:32]')]:
    try:
        if key_size == 16:
            aes_key = md5(b'hzytkjyxgs').digest()
        elif key_size == 24:
            aes_key = md5(b'hzytkjyxgs').digest() + md5(b'hzytkjyxgs2').digest()[:8]
        else:
            aes_key = md5(b'hzytkjyxgs').digest() + md5(b'hzytkjyxgs').digest()

        aes_padded_len = (len(raw) // 16) * 16
        cipher_aes = AES.new(aes_key, AES.MODE_ECB)
        dec_aes = cipher_aes.decrypt(raw[:aes_padded_len]) + raw[aes_padded_len:]
        print(f"AES({key_name}) 前16字节: {dec_aes[:16].hex()}")
        print(f"AES({key_name}) SWF 头: {dec_aes[:3]}")

        if dec_aes[:3] in [b'CWS', b'FWS', b'ZWS']:
            print(f"  => 有效 SWF 头!")
            try:
                result = zlib.decompress(dec_aes[8:])
                print(f"  AES zlib 解压: 成功! {len(result)} bytes")
                break
            except zlib.error as e:
                print(f"  AES zlib 解压: 失败 - {e}")
    except Exception as e:
        print(f"AES({key_name}) 错误: {e}")

# === 7. DES-CBC, 不同 IV 值 - 暴力搜索 ===
print("\n=== 7. DES-CBC 暴力搜索 IV ===")
# 也许 IV 是从某个固定值派生的
iv_candidates = [
    b'\x00' * 8,
    b'\xff' * 8,
    KEY,  # key 本身
    md5(b'hzytkjyxgs').digest()[:8],  # 和 key 一样
    md5(b'hzytkjyxgs').digest()[8:16],  # MD5 的后 8 字节
    b'hzytkjyx'[:8].ljust(8, b'\x00'),
    b'hzytkjyxgs'[:8].ljust(8, b'\x00'),
    raw[:8],  # 文件前8字节
    raw[:8][::-1],  # 反转
    b'\x01' * 8,
]

for iv in iv_candidates:
    try:
        cipher = DES.new(KEY, DES.MODE_CBC, iv=iv)
        dec = cipher.decrypt(raw[:padded_len]) + raw[padded_len:]
        if dec[:3] == b'CWS':
            try:
                result = zlib.decompress(dec[8:])
                print(f"  ✓✓✓ IV={iv.hex()}: 解压成功! {len(result)} bytes")
                with open('d:/topo_system/backend/draco_module_decrypted.swf', 'wb') as f:
                    f.write(dec[:8] + result)
                break
            except:
                pass
    except:
        pass

# === 8. 也许 DES ECB 解密是对的, 但 zlib 数据需要特殊处理 ===
print("\n=== 8. 特殊 zlib 处理 ===")
# 也许 zlib 数据需要先 XOR 或其他处理
dec_ecb_data = dec_ecb[8:]
# 检查前几个字节
print(f"ECB 数据前32字节: {dec_ecb_data[:32].hex()}")

# 也许需要跳过一些字节
for skip in range(0, 20):
    try:
        result = zlib.decompress(dec_ecb[8+skip:])
        print(f"  跳过 {skip} 字节: 解压成功! {len(result)} bytes")
        break
    except:
        pass

# 也许 zlib 数据是 AES 加密的 (只加密了 body, 不加密 header)
print("\n=== 9. AES CBC 解密 body ===")
for key_size in [16, 32]:
    try:
        aes_key = md5(b'hzytkjyxgs').digest()
        if key_size == 32:
            aes_key = aes_key + md5(b'hzytkjyxgs').digest()
        aes_iv = b'\x00' * 16
        aes_padded = (len(dec_ecb[8:]) // 16) * 16
        cipher_aes_cbc = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)
        body_dec = cipher_aes_cbc.decrypt(dec_ecb[8:8+aes_padded])
        # 检查是否有 zlib 头
        if body_dec[:2] in [b'\x78\x9c', b'\x78\xda', b'\x78\x01']:
            print(f"AES-CBC body 解密后前4字节: {body_dec[:4].hex()}")
            try:
                result = zlib.decompress(body_dec)
                print(f"  => 解压成功! {len(result)} bytes")
                break
            except:
                pass
    except Exception as e:
        print(f"AES-CBC({key_size}) 错误: {e}")
