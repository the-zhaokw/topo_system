"""检查 SWF 文件是否真的加密，尝试直接解压"""
import requests as req
import struct
import re
import zlib

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

# 下载 module SWF
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf', timeout=60)
raw = r.content
print(f"\ndraco_module.swf 原始大小: {len(raw)} bytes")
print(f"原始头 16 bytes: {raw[:16].hex()}")
print(f"原始头 ASCII: {raw[:16]}")

# 检查是否是标准 SWF
if raw[:3] == b'CWS':
    print("=> 标准压缩 SWF，无需解密!")
    try:
        decompressed = zlib.decompress(raw[8:])
        print(f"解压成功: {len(decompressed)} bytes")
        with open('d:/topo_system/backend/draco_module_full.bin', 'wb') as f:
            f.write(decompressed)
        # 提取所有字符串
        all_strs = [s.decode('utf-8', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]
        print(f"字符串数: {len(all_strs)}")

        # 搜索 service/delegate/remote 相关
        for s in sorted(set(all_strs)):
            sl = s.lower()
            if any(kw in sl for kw in ['service', 'delegate', 'remoteobject', 'destination',
                                        'amf', 'channel', 'messagebroker']):
                if len(s) < 80:
                    print(f"  {s}")
    except Exception as e:
        print(f"zlib 解压失败: {e}")
        # 尝试不同的偏移
        for offset in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            try:
                decompressed = zlib.decompress(raw[offset:])
                print(f"  偏移 {offset}: 解压成功 {len(decompressed)} bytes")
                break
            except:
                pass

elif raw[:3] == b'FWS':
    print("=> 标准未压缩 SWF")
    all_strs = [s.decode('utf-8', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', raw)]
    print(f"字符串数: {len(all_strs)}")
    for s in sorted(set(all_strs))[:50]:
        print(f"  {s}")
else:
    print(f"=> 非标准 SWF 头，可能是加密的")
    # 尝试 DES 解密
    from hashlib import md5
    try:
        from Crypto.Cipher import DES
        KEY = md5(b'hzytkjyxgs').digest()[:8]
        cipher = DES.new(KEY, DES.MODE_ECB)
        padded_len = (len(raw) // 8) * 8
        decrypted = cipher.decrypt(raw[:padded_len]) + raw[padded_len:]
        print(f"解密后头 16 bytes: {decrypted[:16].hex()}")
        print(f"解密后头 ASCII: {decrypted[:16]}")

        if decrypted[:3] == b'CWS':
            print("=> 解密后是 CWS 格式")
            # 直接尝试解压
            try:
                decompressed = zlib.decompress(decrypted[8:])
                print(f"直接解压成功: {len(decompressed)} bytes")
            except Exception as e:
                print(f"直接解压失败: {e}")
                # 尝试忽略错误
                try:
                    dec_obj = zlib.decompressobj()
                    result = dec_obj.decompress(decrypted[8:])
                    result += dec_obj.flush()
                    print(f"容错解压成功: {len(result)} bytes")
                    with open('d:/topo_system/backend/draco_module_partial.bin', 'wb') as f:
                        f.write(result)
                except Exception as e2:
                    print(f"容错解压也失败: {e2}")

                    # 尝试逐块解压
                    print("尝试逐块解压...")
                    dec_obj = zlib.decompressobj()
                    result = b''
                    chunk_size = 4096
                    data = decrypted[8:]
                    pos = 0
                    while pos < len(data):
                        try:
                            chunk = dec_obj.decompress(data[pos:pos+chunk_size])
                            result += chunk
                            pos += chunk_size
                        except:
                            pos += chunk_size
                    if result:
                        print(f"部分解压: {len(result)} bytes")
                        with open('d:/topo_system/backend/draco_module_partial.bin', 'wb') as f:
                            f.write(result)
                    else:
                        # 如果所有方法都失败，直接从解密但未解压的数据中提取字符串
                        print("直接从解密数据中提取字符串...")
                        all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decrypted)]
                        print(f"字符串数: {len(all_strs)}")
    except ImportError:
        print("PyCryptodome not installed")

# 同时下载 schema.def 并分析
print("\n\n=== 分析 schema.def ===")
r = session.get('http://172.18.36.5:8000/html/client/schema.def', timeout=30)
schema_raw = r.content
print(f"schema.def 大小: {len(schema_raw)} bytes")
print(f"头 16 bytes: {schema_raw[:16].hex()}")
print(f"头 ASCII: {schema_raw[:16]}")

# 尝试解压
try:
    schema_decompressed = zlib.decompress(schema_raw)
    print(f"zlib 解压成功: {len(schema_decompressed)} bytes")
except:
    try:
        schema_decompressed = zlib.decompress(schema_raw, -15)
        print(f"raw deflate 解压成功: {len(schema_decompressed)} bytes")
    except:
        # 尝试 DES 解密
        from hashlib import md5
        try:
            from Crypto.Cipher import DES
            KEY = md5(b'hzytkjyxgs').digest()[:8]
            cipher = DES.new(KEY, DES.MODE_ECB)
            padded_len = (len(schema_raw) // 8) * 8
            schema_dec = cipher.decrypt(schema_raw[:padded_len]) + schema_raw[padded_len:]
            print(f"解密后头: {schema_dec[:16].hex()}")

            # 尝试解压
            try:
                schema_decompressed = zlib.decompress(schema_dec)
                print(f"解密后解压成功: {len(schema_decompressed)} bytes")
            except:
                try:
                    schema_decompressed = zlib.decompress(schema_dec[8:])
                    print(f"解密后偏移8解压成功: {len(schema_decompressed)} bytes")
                except Exception as e:
                    print(f"解密后解压失败: {e}")
                    # 直接从解密数据中提取字符串
                    all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', schema_dec)]
                    print(f"解密数据字符串数: {len(all_strs)}")
                    # 找 AMF 相关
                    for s in sorted(set(all_strs)):
                        sl = s.lower()
                        if any(kw in sl for kw in ['service', 'destination', 'amf', 'method', 'operation',
                                                    'get', 'find', 'load', 'save', 'create', 'delete', 'update',
                                                    'project', 'test', 'defect', 'bug', 'module', 'plan', 'case',
                                                    'run', 'step', 'suite', 'execution', 'environment',
                                                    'build', 'report', 'task', 'scenario', 'requirement',
                                                    'user', 'role', 'permission', 'layout', 'message', 'file']):
                            if len(s) < 80:
                                print(f"  {s}")
        except ImportError:
            print("PyCryptodome not installed")

# 如果成功解压，提取字符串
if 'schema_decompressed' in dir() and schema_decompressed:
    with open('d:/topo_system/backend/schema_decoded.bin', 'wb') as f:
        f.write(schema_decompressed)
    all_strs = [s.decode('utf-8', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', schema_decompressed)]
    print(f"\nschema.def 字符串数: {len(all_strs)}")
    print("\n=== 所有唯一字符串 ===")
    for s in sorted(set(all_strs)):
        if len(s) < 80:
            print(f"  {s}")
