"""解密 module SWF 并用 decompressobj 处理不完整数据"""
import requests as req
import re
import zlib
from Crypto.Cipher import DES
from hashlib import md5

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

# DES-ECB 解密
KEY = md5(b'hzytkjyxgs').digest()[:8]
cipher = DES.new(KEY, DES.MODE_ECB)

# 只解密到 8 字节对齐
padded_len = (len(mod_data) // 8) * 8
decrypted = cipher.decrypt(mod_data[:padded_len])
# 追加未加密的尾部字节
decrypted += mod_data[padded_len:]

print(f"解密后大小: {len(decrypted)} bytes")
print(f"SWF header: {decrypted[:8]}")
print(f"SWF version: {decrypted[3]}")
file_size = int.from_bytes(decrypted[4:8], 'little')
print(f"SWF file size: {file_size} bytes")

# 用 decompressobj 处理可能的尾部问题
print("\n解压中...")
decompressor = zlib.decompressobj()
try:
    decompressed = decompressor.decompress(decrypted[8:])
    # 尝试 flush
    try:
        decompressed += decompressor.flush()
    except:
        pass
    print(f"解压后大小: {len(decompressed)} bytes")

    # 保存
    with open('d:/topo_system/backend/draco_module_decrypted.swf', 'wb') as f:
        f.write(decrypted)
    with open('d:/topo_system/backend/draco_module_decompressed.bin', 'wb') as f:
        f.write(decompressed)
    print("文件已保存")

    # 提取所有字符串
    all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]
    print(f"\n字符串总数: {len(all_strs)}")

    # 1. com.loader 类
    loader = [s for s in all_strs if 'com.loader' in s]
    print(f"\n=== com.loader 类 ({len(loader)}) ===")
    for s in sorted(set(loader)):
        print(f"  {s}")

    # 2. Service 名
    services = [s for s in all_strs if 'Service' in s and len(s) < 60 and not ' ' in s]
    print(f"\n=== Service 名 ({len(services)}) ===")
    for s in sorted(set(services))[:50]:
        print(f"  {s}")

    # 3. RemoteObject/destination
    remote = [s for s in all_strs if any(kw in s.lower() for kw in ['remoteobject', 'destination', 'remote_']) and len(s) < 80]
    print(f"\n=== RemoteObject ({len(remote)}) ===")
    for s in sorted(set(remote))[:30]:
        print(f"  {s}")

    # 4. 业务方法名
    methods = set()
    for s in all_strs:
        if re.match(r'^[a-z][a-zA-Z0-9]{4,60}$', s):
            sl = s.lower()
            if any(kw in sl for kw in ['gettest', 'findtest', 'getproject', 'findproject',
                                         'getplan', 'findplan', 'getcase', 'findcase',
                                         'getdefect', 'finddefect', 'getbug', 'findbug',
                                         'getmodule', 'findmodule', 'getrequirement', 'findrequirement',
                                         'getrun', 'findrun', 'getscenario', 'findscenario',
                                         'getall', 'findall', 'getlist', 'findlist',
                                         'createtest', 'createproject', 'createplan',
                                         'updatetest', 'updateproject', 'savetest', 'saveproject',
                                         'deletetest', 'deleteproject', 'loadtest', 'loadproject',
                                         'getuser', 'finduser', 'getexecution', 'findexecution',
                                         'getresult', 'findresult', 'getstep', 'findstep',
                                         'getcategory', 'getversion', 'getconfig',
                                         'export', 'import', 'report', 'statistics',
                                         'getsummary', 'getdetail', 'getcount',
                                         'getbuild', 'findbuild', 'getenvironment',
                                         'getpriority', 'getstatus', 'getseverity']):
                methods.add(s)
    print(f"\n=== 业务方法名 ({len(methods)}) ===")
    for s in sorted(methods):
        print(f"  {s}")

    # 5. URL/路径
    urls = [s for s in all_strs if (s.startswith('http://') or s.startswith('https://') or s.startswith('/')) and len(s) > 5 and len(s) < 200 and not s.startswith('//')]
    print(f"\n=== URL/路径 ({len(urls)}) ===")
    for s in sorted(set(urls)):
        print(f"  {s}")

    # 6. transmitfile 和 messagebroker
    transmit = [s for s in all_strs if 'transmit' in s.lower()]
    print(f"\n=== transmitfile 相关 ===")
    for s in sorted(set(transmit)):
        print(f"  {s}")

    # 7. 业务类名
    biz = set()
    for s in all_strs:
        if any(kw in s for kw in ['TestCase', 'TestPlan', 'TestRun', 'TestSuite', 'TestStep',
                                    'Defect', 'Bug', 'Project', 'Module', 'Requirement',
                                    'Scenario', 'Environment', 'Build', 'Release',
                                    'Execution', 'Result', 'Report', 'Statistics',
                                    'Category', 'Priority', 'Severity']) and len(s) < 100 and not s.startswith('<'):
            biz.add(s)
    print(f"\n=== 业务类名 ({len(biz)}) ===")
    for s in sorted(biz)[:50]:
        print(f"  {s}")

    # 8. Destination ID
    dest_ids = set()
    for s in all_strs:
        if re.match(r'^[a-z][a-zA-Z]+$', s) and len(s) > 5 and len(s) < 40:
            if any(kw in s.lower() for kw in ['service', 'delegate', 'proxy', 'facade']):
                dest_ids.add(s)
    print(f"\n=== Destination ID ({len(dest_ids)}) ===")
    for s in sorted(dest_ids):
        print(f"  {s}")

except zlib.error as e:
    print(f"ZLIB 解压失败: {e}")
    # 尝试使用 wbits=-15 (raw deflate)
    print("\n尝试 raw deflate...")
    try:
        decompressor = zlib.decompressobj(wbits=-15)
        decompressed = decompressor.decompress(decrypted[8:])
        print(f"Raw deflate 成功! Size: {len(decompressed)} bytes")
    except Exception as e2:
        print(f"Raw deflate 也失败: {e2}")

        # 最后尝试：只解密前 8 字节头部，其余不变
        print("\n尝试只解密头部...")
        header = cipher.decrypt(mod_data[:8])
        print(f"Header: {header}")
        rest = mod_data[8:]
        full = header + rest
        print(f"Full first 16: {full[:16].hex()}")
        try:
            decompressor = zlib.decompressobj()
            decompressed = decompressor.decompress(full[8:])
            print(f"成功! Size: {len(decompressed)} bytes")
        except Exception as e3:
            print(f"仍然失败: {e3}")
            # 也许整个文件不是 DES 加密的，只有头部是
            # 也许只有 DESCRYPT_LENGTH 个字节被加密
            print("\n也许只有部分字节被加密...")
            for descrypt_len in [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]:
                if descrypt_len > len(mod_data):
                    break
                decrypted_part = cipher.decrypt(mod_data[:descrypt_len])
                rest_part = mod_data[descrypt_len:]
                combined = decrypted_part + rest_part
                try:
                    decompressor = zlib.decompressobj()
                    test = decompressor.decompress(combined[8:8+10000])
                    if len(test) > 100:
                        print(f"  ✅ DESCRYPT_LENGTH = {descrypt_len}: 解压 {len(test)} bytes")
                        # 继续完整解压
                        decompressor = zlib.decompressobj()
                        decompressed = decompressor.decompress(combined[8:])
                        try:
                            decompressed += decompressor.flush()
                        except:
                            pass
                        print(f"  完整解压: {len(decompressed)} bytes")
                        with open('d:/topo_system/backend/draco_module_decompressed.bin', 'wb') as f:
                            f.write(decompressed)
                        # 提取字符串
                        all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]
                        print(f"  字符串数: {len(all_strs)}")
                        loader = [s for s in all_strs if 'com.loader' in s]
                        print(f"  com.loader 类: {len(loader)}")
                        for s in sorted(set(loader))[:30]:
                            print(f"    {s}")
                        services = [s for s in all_strs if 'Service' in s and len(s) < 60 and not ' ' in s]
                        print(f"  Service 名: {len(services)}")
                        for s in sorted(set(services))[:30]:
                            print(f"    {s}")
                        urls = [s for s in all_strs if (s.startswith('http://') or s.startswith('/')) and len(s) > 5 and len(s) < 200 and not s.startswith('//')]
                        print(f"  URL/路径: {len(urls)}")
                        for s in sorted(set(urls)):
                            print(f"    {s}")
                        break
                except:
                    pass
