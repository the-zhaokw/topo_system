"""在 manager SWF 二进制中搜索加密密钥 + 尝试多种解密方法"""
import requests as req
import re
import zlib
from Crypto.Cipher import AES, DES, DES3, ARC4, Blowfish
from hashlib import md5, sha1, sha256

session = req.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})

# 登录
r = session.get('http://172.18.36.5:8000/', timeout=10)
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
session.post(login_url, data={
    '_58_redirect': '', '_58_rememberMe': 'false',
    '_58_login': 'zhaokw', '_58_password': '`123qwer',
}, timeout=15, allow_redirects=True)

# 下载 SWF 文件
print("=== 下载文件 ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', timeout=30)
mgr_data = r.content
mgr_decompressed = mgr_data[:8] + zlib.decompress(mgr_data[8:])

r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf', timeout=60)
mod_data = r.content
print(f"Manager: {len(mgr_decompressed)} bytes, Module: {len(mod_data)} bytes")
print(f"Module first 32 bytes: {mod_data[:32].hex()}")

# 1. 在 manager SWF 二进制中搜索密钥相关数据
print("\n=== 1. 搜索密钥 ===")

# 查找 encrypt_key 附近的二进制数据
encrypt_key_pos = mgr_decompressed.find(b'encrypt_key')
if encrypt_key_pos >= 0:
    context = mgr_decompressed[max(0, encrypt_key_pos-50):encrypt_key_pos+100]
    print(f"encrypt_key 上下文 (pos={encrypt_key_pos}):")
    print(f"  Hex: {context.hex()}")
    print(f"  String: {context}")

# 查找 DEFINITION_KEY 附近
def_key_pos = mgr_decompressed.find(b'DEFINITION_KEY')
if def_key_pos >= 0:
    context = mgr_decompressed[max(0, def_key_pos-50):def_key_pos+100]
    print(f"\nDEFINITION_KEY 上下文 (pos={def_key_pos}):")
    print(f"  Hex: {context.hex()}")
    print(f"  String: {context}")

# 查找 Df_Key 附近
df_key_pos = mgr_decompressed.find(b'Df_Key')
if df_key_pos >= 0:
    context = mgr_decompressed[max(0, df_key_pos-50):df_key_pos+100]
    print(f"\nDf_Key 上下文 (pos={df_key_pos}):")
    print(f"  Hex: {context.hex()}")
    print(f"  String: {context}")

# 查找 DESCRYPT_LENGTH 附近
descrypt_pos = mgr_decompressed.find(b'DESCRYPT_LENGTH')
if descrypt_pos >= 0:
    context = mgr_decompressed[max(0, descrypt_pos-50):descrypt_pos+100]
    print(f"\nDESCRYPT_LENGTH 上下文 (pos={descrypt_pos}):")
    print(f"  Hex: {context.hex()}")

# 查找 DRACO_MANAGER_CACHE 附近
draco_cache_pos = mgr_decompressed.find(b'DRACO_MANAGER_CACHE')
if draco_cache_pos >= 0:
    context = mgr_decompressed[max(0, draco_cache_pos-50):draco_cache_pos+200]
    print(f"\nDRACO_MANAGER_CACHE 上下文:")
    print(f"  String: {context}")

# 查找所有可能的 16 字节密钥（在加密相关字符串附近）
print("\n=== 2. 提取可能的密钥 ===")
# 在 manager SWF 中搜索所有 16 字节的二进制序列（可能是 AES 密钥）
# 寻找在 encrypt_key 或 DEFINITION_KEY 附近的固定长度二进制数据
if encrypt_key_pos >= 0:
    # 搜索 encrypt_key 之后的数据
    search_area = mgr_decompressed[encrypt_key_pos:encrypt_key_pos+500]
    # 查找非 ASCII 的二进制数据块
    bin_blocks = re.findall(rb'[\x80-\xff\x00-\x1f]{16,32}', search_area)
    print(f"encrypt_key 后的二进制块: {len(bin_blocks)}")
    for block in bin_blocks[:5]:
        print(f"  {block.hex()} (len={len(block)})")

# 3. 尝试多种密钥和解密方法
print("\n=== 3. 尝试解密 ===")

# 候选密钥
candidates = [
    b'encrypt_key',
    b'DEFINITION_KEY',
    b'Df_Key',
    b'DRACO_MANAGER_CACHE',
    b'22474',
    b'draco_manager',
    b'draco_module',
    b'draco',
    b'topo',
    b'ChenXiao',
    b'chenxiao',
    # MD5 哈希作为密钥
    md5(b'22474').digest(),
    md5(b'draco').digest(),
    md5(b'DRACO_MANAGER_CACHE').digest(),
    md5(b'encrypt_key').digest(),
    # SHA1 哈希（截取16字节）
    sha1(b'22474').digest()[:16],
    sha1(b'draco').digest()[:16],
]

# 检查模块文件是否有 ZLIB 压缩头（78 xx）
for i in range(min(200, len(mod_data))):
    if mod_data[i] == 0x78 and i+1 < len(mod_data):
        if mod_data[i+1] in [0x01, 0x5e, 0x9c, 0xda]:
            # 可能是 ZLIB 头
            print(f"  可能的 ZLIB 头在偏移 {i}: {mod_data[i:i+2].hex()}")
            try:
                test = zlib.decompress(mod_data[i:i+10000])
                if len(test) > 100:
                    print(f"    ✅ ZLIB 解压成功! 解压 {len(test)} bytes")
                    # 检查是否是 SWF 数据
                    if b'SWF' in test[:10] or b'mx.' in test[:100] or b'com.' in test[:100]:
                        print(f"    可能是 SWF 内容!")
                        break
            except:
                pass

# 尝试 AES-ECB 解密
print("\nAES-ECB 解密尝试:")
for key in candidates:
    if len(key) in [16, 24, 32]:
        try:
            cipher = AES.new(key, AES.MODE_ECB)
            test_dec = cipher.decrypt(mod_data[:32])
            if test_dec[:3] in [b'CWS', b'FWS', b'ZWS']:
                print(f"  ✅ AES-ECB key={key.hex()} -> {test_dec[:3]}")
        except:
            pass

# 尝试 AES-CBC 解密（IV = 前16字节）
print("\nAES-CBC 解密尝试:")
for key in candidates:
    if len(key) in [16, 24, 32]:
        try:
            iv = mod_data[:16]
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            test_dec = cipher.decrypt(mod_data[16:48])
            # 检查解密结果是否像 SWF 数据
            if b'WS' in test_dec[:4]:
                print(f"  ✅ AES-CBC key={key.hex()} -> {test_dec[:8].hex()}")
        except:
            pass

# 尝试 DES/3DES 解密
print("\nDES 解密尝试:")
for key in candidates:
    if len(key) == 8:
        try:
            cipher = DES.new(key, DES.MODE_ECB)
            test_dec = cipher.decrypt(mod_data[:16])
            if test_dec[:3] in [b'CWS', b'FWS', b'ZWS']:
                print(f"  ✅ DES key={key.hex()}")
        except:
            pass

# 尝试 ARC4 (RC4) 解密
print("\nARC4 解密尝试:")
for key in candidates:
    try:
        cipher = ARC4.new(key)
        test_dec = cipher.decrypt(mod_data[:16])
        if test_dec[:3] in [b'CWS', b'FWS', b'ZWS']:
            print(f"  ✅ ARC4 key={key} ({key.hex()}) -> {test_dec[:8]}")
            # 完整解密
            cipher = ARC4.new(key)
            full_dec = cipher.decrypt(mod_data)
            print(f"    解密后大小: {len(full_dec)} bytes")
            if full_dec[:3] == b'CWS':
                decompressed = full_dec[:8] + zlib.decompress(full_dec[8:])
                print(f"    ✅ ZLIB 解压成功! Size: {len(decompressed)} bytes")
                # 提取字符串
                all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]
                print(f"    字符串数: {len(all_strs)}")
                loader = [s for s in all_strs if 'com.loader' in s]
                print(f"    com.loader 类: {len(loader)}")
                for s in sorted(set(loader))[:20]:
                    print(f"      {s}")
                # 查找 destination 名称
                dest_strings = [s for s in all_strs if 'destination' in s.lower() or 'RemoteObject' in s or 'source' in s.lower() and len(s) < 50]
                print(f"    Destination 相关: {len(dest_strings)}")
                for s in sorted(set(dest_strings))[:20]:
                    print(f"      {s}")
        elif test_dec[:3] == b'FWS':
            print(f"  ✅ ARC4 key={key} -> FWS (未压缩)")
    except:
        pass

# 尝试 Blowfish 解密
print("\nBlowfish 解密尝试:")
for key in candidates:
    try:
        cipher = Blowfish.new(key, Blowfish.MODE_ECB)
        test_dec = cipher.decrypt(mod_data[:16])
        if test_dec[:3] in [b'CWS', b'FWS', b'ZWS']:
            print(f"  ✅ Blowfish key={key} ({key.hex()})")
    except:
        pass

# 4. 检查模块文件结构 - 也许只有头部加密
print("\n=== 4. 检查部分加密 ===")
# 如果 DESCRYPT_LENGTH 是加密部分的长度，也许只有前 N 字节加密
# 尝试在模块文件的不同偏移位置查找 ZLIB 头
zlib_offsets = []
for i in range(min(500, len(mod_data))):
    if mod_data[i] == 0x78 and i+1 < len(mod_data) and mod_data[i+1] in [0x01, 0x5e, 0x9c, 0xda]:
        try:
            test = zlib.decompress(mod_data[i:i+min(10000, len(mod_data)-i)])
            if len(test) > 100:
                zlib_offsets.append((i, len(test)))
                print(f"  ZLIB 头在偏移 {i}: 解压 {len(test)} bytes")
        except:
            pass

# 5. 尝试搜索 manager SWF 中的所有 16 字节二进制数据作为 AES 密钥
print("\n=== 5. 暴力搜索 AES 密钥 ===")
# 在 manager SWF 中查找所有可能的 16 字节密钥
# 重点关注加密相关字符串附近的数据
search_areas = []
for keyword in [b'encrypt_key', b'DEFINITION_KEY', b'Df_Key', b'DESCRYPT_LENGTH', b'DRACO_MANAGER_CACHE']:
    pos = mgr_decompressed.find(keyword)
    if pos >= 0:
        search_areas.append((keyword, pos, mgr_decompressed[max(0,pos-200):pos+500]))

# 在每个搜索区域中尝试所有 16 字节对齐的数据作为密钥
found = False
for area_name, _, area_data in search_areas:
    if found:
        break
    for i in range(0, len(area_data)-16):
        key = area_data[i:i+16]
        # 跳过全 ASCII 的数据
        if all(0x20 <= b <= 0x7e for b in key):
            continue
        try:
            cipher = AES.new(key, AES.MODE_ECB)
            test_dec = cipher.decrypt(mod_data[:16])
            if test_dec[:3] in [b'CWS', b'FWS', b'ZWS']:
                print(f"  ✅ AES-ECB 密钥在 {area_name} 附近: {key.hex()}")
                full_dec = cipher.decrypt(mod_data[:len(mod_data) - (len(mod_data) % 16)])
                if full_dec[:3] == b'CWS':
                    decompressed = full_dec[:8] + zlib.decompress(full_dec[8:])
                    print(f"    ✅ 完全解密成功! Size: {len(decompressed)} bytes")
                found = True
                break
        except:
            pass

        # 也尝试 CBC 模式
        try:
            iv = b'\x00' * 16
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            test_dec = cipher.decrypt(mod_data[:16])
            if test_dec[:3] in [b'CWS', b'FWS', b'ZWS']:
                print(f"  ✅ AES-CBC (IV=0) 密钥: {key.hex()}")
                found = True
                break
        except:
            pass

if not found:
    print("  未找到 AES 密钥")

# 6. 尝试 ARC4 密钥暴力搜索
print("\n=== 6. ARC4 密钥暴力搜索 ===")
for area_name, _, area_data in search_areas:
    if found:
        break
    for i in range(0, min(len(area_data)-4, 200)):
        for length in [4, 8, 16, 20, 24, 32]:
            if i+length > len(area_data):
                break
            key = area_data[i:i+length]
            try:
                cipher = ARC4.new(key)
                test_dec = cipher.decrypt(mod_data[:4])
                if test_dec[:3] in [b'CWS', b'FWS', b'ZWS']:
                    print(f"  ✅ ARC4 密钥在 {area_name} 附近: {key.hex()} (len={length})")
                    # 完整解密
                    cipher = ARC4.new(key)
                    full_dec = cipher.decrypt(mod_data)
                    if full_dec[:3] == b'CWS':
                        decompressed = full_dec[:8] + zlib.decompress(full_dec[8:])
                        print(f"    ✅ 完全解密成功! Size: {len(decompressed)} bytes")
                        all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]
                        loader = [s for s in all_strs if 'com.loader' in s]
                        print(f"    字符串数: {len(all_strs)}, com.loader 类: {len(loader)}")
                    found = True
                    break
            except:
                pass
        if found:
            break

if not found:
    print("  未找到 ARC4 密钥")
