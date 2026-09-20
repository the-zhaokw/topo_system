"""分析 manager SWF 中的解密逻辑 + 尝试解密 module SWF"""
import requests as req
import re
import zlib

session = req.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})

# 1. 登录
r = session.get('http://172.18.36.5:8000/', timeout=10)
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
session.post(login_url, data={
    '_58_redirect': '', '_58_rememberMe': 'false',
    '_58_login': 'zhaokw', '_58_password': '`123qwer',
}, timeout=15, allow_redirects=True)

# 2. 下载 manager SWF
print("=== 2. 分析 manager SWF ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', timeout=30)
mgr_data = r.content
mgr_decompressed = mgr_data[:8] + zlib.decompress(mgr_data[8:])
mgr_strings = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{3,}', mgr_decompressed)]

# 查找加密/解密相关字符串
crypto_strings = [s for s in mgr_strings if any(kw in s.lower() for kw in ['encrypt', 'decrypt', 'cipher', 'xor', 'aes', 'des', 'key', 'secret', 'decode', 'encode', 'crypt', 'hash'])]
print(f"加密相关字符串 ({len(crypto_strings)}):")
for s in sorted(set(crypto_strings))[:40]:
    print(f"  {s}")

# 查找 ModuleCacheProxy 相关
cache_strings = [s for s in mgr_strings if 'cache' in s.lower() or 'module' in s.lower()]
print(f"\nCache/Module 相关 ({len(cache_strings)}):")
for s in sorted(set(cache_strings))[:30]:
    print(f"  {s}")

# 查找 loadModule 方法
load_strings = [s for s in mgr_strings if 'load' in s.lower() and len(s) < 60]
print(f"\nLoad 相关 ({len(load_strings)}):")
for s in sorted(set(load_strings))[:30]:
    print(f"  {s}")

# 查找 version 相关
version_strings = [s for s in mgr_strings if 'version' in s.lower() or '22474' in s]
print(f"\nVersion 相关 ({len(version_strings)}):")
for s in sorted(set(version_strings)):
    print(f"  {s}")

# 3. 下载 module SWF 并尝试解密
print("\n=== 3. 尝试解密 module SWF ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf', timeout=60)
mod_data = r.content
print(f"Module size: {len(mod_data)} bytes")
print(f"First 16 bytes: {mod_data[:16].hex()}")

# 尝试1: XOR with version string "22474"
key_str = b"22474"
test1 = bytes([b ^ key_str[i % len(key_str)] for i, b in enumerate(mod_data[:8])])
print(f"\nXOR with '22474': {test1.hex()} -> {test1[:3]}")
if test1[:3] in [b'CWS', b'FWS', b'ZWS']:
    print("  ✅ XOR with version string works!")
    decrypted = bytes([b ^ key_str[i % len(key_str)] for i, b in enumerate(mod_data)])
    decompressed = decrypted[:8] + zlib.decompress(decrypted[8:])
    print(f"  解压后大小: {len(decompressed)} bytes")

# 尝试2: XOR with single bytes 0-255
print("\n尝试单字节 XOR:")
for xor_byte in range(256):
    test = bytes([b ^ xor_byte for b in mod_data[:3]])
    if test in [b'CWS', b'FWS', b'ZWS']:
        print(f"  ✅ XOR byte 0x{xor_byte:02x} ({xor_byte}) produces {test.decode()}")
        decrypted = bytes([b ^ xor_byte for b in mod_data])
        try:
            decompressed = decrypted[:8] + zlib.decompress(decrypted[8:])
            print(f"  解压成功! Size: {len(decompressed)} bytes")
            # 提取字符串
            all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]
            print(f"  字符串数: {len(all_strs)}")
            # 查找关键信息
            loader = [s for s in all_strs if 'com.loader' in s]
            print(f"  com.loader 类: {len(loader)}")
            for s in sorted(set(loader))[:20]:
                print(f"    {s}")
            break
        except Exception as e:
            print(f"  解压失败: {e}")

# 尝试3: 检查是否是 AES 加密（需要密钥）
# 查找 manager SWF 中的密钥
aes_strings = [s for s in mgr_strings if 'aes' in s.lower() or 'AESKey' in s]
print(f"\nAES 相关: {aes_strings[:5]}")

# 尝试4: 查找 manager SWF 中的 com.hurlant.crypto 类
crypto_classes = [s for s in mgr_strings if 'com.hurlant' in s]
print(f"\ncom.hurlant crypto 类 ({len(crypto_classes)}):")
for s in sorted(set(crypto_classes)):
    print(f"  {s}")

# 尝试5: 检查 manager SWF 中的二进制数据，可能包含密钥
# 查找类似密钥的字符串（16/24/32 字节的十六进制或 base64）
key_candidates = [s for s in mgr_strings if re.match(r'^[A-Za-z0-9+/]{16,44}={0,2}$', s) or re.match(r'^[0-9a-fA-F]{16,64}$', s)]
print(f"\n可能的密钥候选 ({len(key_candidates)}):")
for s in sorted(set(key_candidates))[:10]:
    print(f"  {s}")

# 尝试6: 也许模块不是加密的，而是不同的压缩格式
# 检查前 4 字节是否是某种已知格式
print(f"\n=== 4. 检查文件格式 ===")
first_bytes = mod_data[:4]
print(f"前 4 字节: {first_bytes.hex()} = {first_bytes}")
# 检查是否是 LZMA (0x5d 0x00 0x00)
# 检查是否是 bzip2 (0x42 0x5a 0x68)
# 检查是否是 7z (0x37 0x7a 0xbc 0xaf)
# 检查是否是 RAR (0x52 0x61 0x72 0x21)

# 尝试7: 也许模块 SWF 使用了 SWFEncrypt 或类似工具
# 检查是否有 "SWFEncrypt" 或 "secureSWF" 的特征
security_strings = [s for s in mgr_strings if any(kw in s.lower() for kw in ['secure', 'protect', 'obfuscat', 'encrypt', 'swfenc', 'amayeta'])]
print(f"\n安全相关: {security_strings[:10]}")

# 尝试8: 检查是否可以通过 cache 共享对象解密
# SharedObject 在 Flash 中用于本地存储
so_strings = [s for s in mgr_strings if 'sharedobject' in s.lower() or 'shared' in s.lower() or 'local' in s.lower()]
print(f"\nSharedObject 相关 ({len(so_strings)}):")
for s in sorted(set(so_strings))[:20]:
    print(f"  {s}")

# 尝试9: 查找 manager SWF 中所有看起来像配置的字符串
config_strings = [s for s in mgr_strings if any(kw in s for kw in ['Config', 'config', 'Preference', 'preference', 'Setting', 'setting'])]
print(f"\n配置相关 ({len(config_strings)}):")
for s in sorted(set(config_strings))[:20]:
    print(f"  {s}")

# 尝试10: 检查 cache-config.xml 中的 version 是否是加密密钥
print(f"\n=== 5. 尝试用版本号作为 AES 密钥 ===")
# Version = 22474
# 尝试将版本号作为 AES-128 密钥（不足的补0）
from hashlib import md5
key_hash = md5(b"22474").digest()  # 16 bytes for AES-128
print(f"MD5('22474') = {key_hash.hex()}")

# 尝试 AES-ECB 解密前 16 字节
try:
    from Crypto.Cipher import AES
    cipher = AES.new(key_hash, AES.MODE_ECB)
    test_dec = cipher.decrypt(mod_data[:16])
    print(f"AES-ECB 解密前16字节: {test_dec.hex()} -> {test_dec[:3]}")
    if test_dec[:3] in [b'CWS', b'FWS', b'ZWS']:
        print("  ✅ AES-ECB 解密成功!")
except ImportError:
    print("PyCryptodome 未安装，跳过 AES 测试")
except Exception as e:
    print(f"AES 测试失败: {e}")
