"""用 hzytkjyxgs 作为密钥尝试解密 module SWF"""
import requests as req
import re
import zlib
from Crypto.Cipher import AES, DES, DES3, ARC4, Blowfish
from hashlib import md5, sha1

session = req.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})

# 登录
r = session.get('http://172.18.36.5:8000/', timeout=10)
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
session.post(login_url, data={
    '_58_redirect': '', '_58_rememberMe': 'false',
    '_58_login': 'zhaokw', '_58_password': '`123qwer',
}, timeout=15, allow_redirects=True)

# 下载 module SWF
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf', timeout=60)
mod_data = r.content
print(f"Module size: {len(mod_data)} bytes")
print(f"First 16 bytes: {mod_data[:16].hex()}")

# 密钥候选
KEY = b'hzytkjyxgs'
print(f"\n密钥: {KEY}")
print(f"密钥长度: {len(KEY)} bytes")
print(f"MD5(密钥): {md5(KEY).hexdigest()}")
print(f"MD5(密钥) bytes: {md5(KEY).digest().hex()}")
print(f"SHA1(密钥)[:16]: {sha1(KEY).digest()[:16].hex()}")

# 1. ARC4 解密
print("\n=== 1. ARC4 解密 ===")
for key in [KEY, md5(KEY).digest(), sha1(KEY).digest()[:16]]:
    cipher = ARC4.new(key)
    test_dec = cipher.decrypt(mod_data[:16])
    print(f"  ARC4 key={key.hex() if isinstance(key, bytes) else key}: {test_dec[:8].hex()} -> {test_dec[:3]}")
    if test_dec[:3] in [b'CWS', b'FWS', b'ZWS']:
        print(f"  ✅ 成功！")
        cipher = ARC4.new(key)
        full_dec = cipher.decrypt(mod_data)
        print(f"  解密后大小: {len(full_dec)} bytes")
        if full_dec[:3] == b'CWS':
            try:
                decompressed = full_dec[:8] + zlib.decompress(full_dec[8:])
                print(f"  ✅ ZLIB 解压成功! Size: {len(decompressed)} bytes")
                # 提取字符串
                all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]
                print(f"  字符串数: {len(all_strs)}")

                # com.loader 类
                loader = [s for s in all_strs if 'com.loader' in s]
                print(f"\n  com.loader 类 ({len(loader)}):")
                for s in sorted(set(loader))[:30]:
                    print(f"    {s}")

                # RemoteObject / destination
                remote = [s for s in all_strs if 'remote' in s.lower() or 'destination' in s.lower() or 'source' in s.lower() and len(s) < 50]
                print(f"\n  Remote/Destination ({len(remote)}):")
                for s in sorted(set(remote))[:30]:
                    print(f"    {s}")

                # URL/路径
                urls = [s for s in all_strs if (s.startswith('http://') or s.startswith('https://') or s.startswith('/')) and len(s) < 200 and len(s) > 5]
                print(f"\n  URL/路径 ({len(urls)}):")
                for s in sorted(set(urls))[:40]:
                    print(f"    {s}")

                # 业务方法名
                methods = set()
                for s in all_strs:
                    if re.match(r'^[a-z][a-zA-Z0-9]{4,50}$', s):
                        sl = s.lower()
                        if any(kw in sl for kw in ['gettest', 'findtest', 'getproject', 'getplan', 'getcase',
                                                     'getdefect', 'getbug', 'getmodule', 'getrequirement',
                                                     'getrun', 'getscenario', 'getbuild', 'getuser',
                                                     'createtest', 'createproject', 'updatetest',
                                                     'savetest', 'deletetest', 'loadtest',
                                                     'getall', 'getlist', 'findall']):
                            methods.add(s)
                print(f"\n  业务方法名 ({len(methods)}):")
                for s in sorted(methods):
                    print(f"    {s}")

                # 所有 Service 字符串
                services = [s for s in all_strs if 'Service' in s and len(s) < 50 and not '.' in s and not ' ' in s]
                print(f"\n  Service 名 ({len(services)}):")
                for s in sorted(set(services)):
                    print(f"    {s}")

                # 保存解密后的 SWF 以供进一步分析
                with open('d:/topo_system/backend/draco_module_decrypted.swf', 'wb') as f:
                    f.write(full_dec)
                print(f"\n  解密后的 SWF 已保存到 draco_module_decrypted.swf")

                # transmitfile 端点
                transmit = [s for s in all_strs if 'transmit' in s.lower()]
                print(f"\n  transmitfile 相关:")
                for s in sorted(set(transmit)):
                    print(f"    {s}")

                # messagebroker 端点
                mb = [s for s in all_strs if 'messagebroker' in s.lower() or 'amf' in s.lower()]
                print(f"\n  messagebroker/amf 相关:")
                for s in sorted(set(mb)):
                    print(f"    {s}")

                break
            except Exception as e:
                print(f"  ZLIB 解压失败: {e}")

# 2. 如果 ARC4 不行，尝试 AES
print("\n=== 2. AES 解密 ===")
aes_keys = [
    (md5(KEY).digest(), "MD5(key)"),
    (KEY.ljust(16, b'\x00'), "key padded to 16"),
    (KEY.ljust(24, b'\x00'), "key padded to 24"),
    (KEY.ljust(32, b'\x00'), "key padded to 32"),
    (sha1(KEY).digest()[:16], "SHA1(key)[:16]"),
    (sha1(KEY).digest()[:24], "SHA1(key)[:24]"),
    (KEY + KEY[:6], "key+key[:6] (16 bytes)"),
]
for key, desc in aes_keys:
    if len(key) not in [16, 24, 32]:
        continue
    # ECB
    try:
        cipher = AES.new(key, AES.MODE_ECB)
        test = cipher.decrypt(mod_data[:16])
        if test[:3] in [b'CWS', b'FWS', b'ZWS']:
            print(f"  ✅ AES-ECB {desc}: {test[:3]}")
    except:
        pass
    # CBC with IV=0
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv=b'\x00'*16)
        test = cipher.decrypt(mod_data[:16])
        if test[:3] in [b'CWS', b'FWS', b'ZWS']:
            print(f"  ✅ AES-CBC(IV=0) {desc}: {test[:3]}")
    except:
        pass
    # CBC with IV from first 16 bytes
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv=mod_data[:16])
        test = cipher.decrypt(mod_data[16:32])
        if test[:3] in [b'CWS', b'FWS', b'ZWS']:
            print(f"  ✅ AES-CBC(IV=first16) {desc}: {test[:3]}")
    except:
        pass

# 3. DES 解密
print("\n=== 3. DES 解密 ===")
des_keys = [
    (KEY[:8], "key[:8]"),
    (md5(KEY).digest()[:8], "MD5(key)[:8]"),
    (sha1(KEY).digest()[:8], "SHA1(key)[:8]"),
]
for key, desc in des_keys:
    try:
        cipher = DES.new(key, DES.MODE_ECB)
        test = cipher.decrypt(mod_data[:8])
        if test[:3] in [b'CWS', b'FWS', b'ZWS']:
            print(f"  ✅ DES-ECB {desc}: {test[:3]}")
    except:
        pass

# 4. 3DES 解密
print("\n=== 4. 3DES 解密 ===")
for key, desc in [(md5(KEY).digest() + md5(KEY).digest()[:8], "MD5(key)+MD5(key)[:8]"),
                   (sha1(KEY).digest() + sha1(KEY).digest()[:4], "SHA1(key)+SHA1(key)[:4]")]:
    if len(key) >= 24:
        try:
            cipher = DES3.new(key[:24], DES3.MODE_ECB)
            test = cipher.decrypt(mod_data[:8])
            if test[:3] in [b'CWS', b'FWS', b'ZWS']:
                print(f"  ✅ 3DES-ECB {desc}: {test[:3]}")
        except:
            pass

# 5. 检查是否只有部分加密（DESCRYPT_LENGTH）
print("\n=== 5. 检查部分加密 ===")
# 如果只有前 N 字节加密，尝试找到明文 ZLIB 头
# ZLIB 头通常是 78 9c, 78 01, 78 da, 78 5e
for i in range(min(1000, len(mod_data))):
    if mod_data[i] == 0x78 and i+1 < len(mod_data):
        next_byte = mod_data[i+1]
        if next_byte in [0x01, 0x5e, 0x9c, 0xda]:
            # 尝试从这个位置解压
            try:
                test = zlib.decompress(mod_data[i:i+min(100000, len(mod_data)-i)])
                if len(test) > 1000:
                    print(f"  ✅ ZLIB 头在偏移 {i}: 解压 {len(test)} bytes")
                    # 检查内容
                    if b'com.loader' in test or b'mx.' in test or b'SWF' in test[:10]:
                        print(f"  内容看起来是 SWF 数据!")
                        all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', test)]
                        loader = [s for s in all_strs if 'com.loader' in s]
                        print(f"  字符串数: {len(all_strs)}, com.loader: {len(loader)}")
                        for s in sorted(set(loader))[:20]:
                            print(f"    {s}")
                    break
            except:
                pass

print("\n完成！")
