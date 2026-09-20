"""容错解压 SWF 数据，提取部分内容"""
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

# DES-ECB 解密
KEY = md5(b'hzytkjyxgs').digest()[:8]
cipher = DES.new(KEY, DES.MODE_ECB)
padded_len = (len(mod_data) // 8) * 8
decrypted = cipher.decrypt(mod_data[:padded_len]) + mod_data[padded_len:]

print(f"解密后: {len(decrypted)} bytes, header: {decrypted[:8]}")

# 尝试多种 wbits
print("\n=== 尝试解压 ===")
best_result = b''
for wbits in [15, -15, 31, 47, 0]:
    try:
        dec_obj = zlib.decompressobj(wbits=wbits if wbits > 0 or wbits == -15 else 15)
        result = dec_obj.decompress(decrypted[8:])
        try:
            result += dec_obj.flush()
        except:
            pass
        if len(result) > len(best_result):
            best_result = result
            print(f"  wbits={wbits}: 解压 {len(result)} bytes")
    except zlib.error as e:
        # 即使出错，也可能有部分数据
        try:
            dec_obj = zlib.decompressobj(wbits=wbits if wbits > 0 or wbits == -15 else 15)
            result = dec_obj.decompress(decrypted[8:], 100*1024*1024)
            if len(result) > len(best_result):
                best_result = result
                print(f"  wbits={wbits} (partial): 解压 {len(result)} bytes, error: {str(e)[:50]}")
        except:
            pass

print(f"\n最佳解压结果: {len(best_result)} bytes")

if len(best_result) > 100:
    # 保存部分结果
    with open('d:/topo_system/backend/draco_module_partial.bin', 'wb') as f:
        f.write(best_result)

    # 提取所有字符串
    all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', best_result)]
    print(f"字符串总数: {len(all_strs)}")

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

    # 3. Destination ID
    dest_ids = set()
    for s in all_strs:
        if re.match(r'^[a-z][a-zA-Z]+$', s) and len(s) > 5 and len(s) < 40:
            if any(kw in s.lower() for kw in ['service', 'delegate', 'proxy', 'facade']):
                dest_ids.add(s)
    print(f"\n=== Destination ID ({len(dest_ids)}) ===")
    for s in sorted(dest_ids):
        print(f"  {s}")

    # 4. URL/路径
    urls = [s for s in all_strs if (s.startswith('http://') or s.startswith('https://') or s.startswith('/')) and len(s) > 5 and len(s) < 200 and not s.startswith('//')]
    print(f"\n=== URL/路径 ({len(urls)}) ===")
    for s in sorted(set(urls)):
        print(f"  {s}")

    # 5. 业务方法名
    methods = set()
    for s in all_strs:
        if re.match(r'^[a-z][a-zA-Z0-9]{4,60}$', s):
            sl = s.lower()
            if any(kw in sl for kw in ['gettest', 'findtest', 'getproject', 'findproject',
                                         'getplan', 'findplan', 'getcase', 'findcase',
                                         'getdefect', 'finddefect', 'getbug', 'findbug',
                                         'getmodule', 'findmodule', 'getrequirement',
                                         'getrun', 'findrun', 'getscenario', 'findscenario',
                                         'getall', 'findall', 'getlist', 'findlist',
                                         'createtest', 'createproject', 'updatetest',
                                         'savetest', 'saveproject', 'deletetest',
                                         'loadtest', 'loadproject',
                                         'getuser', 'finduser', 'getexecution',
                                         'getresult', 'getstep', 'getcategory',
                                         'export', 'report', 'statistics',
                                         'getsummary', 'getdetail', 'getcount',
                                         'getbuild', 'getenvironment',
                                         'getpriority', 'getstatus', 'getseverity',
                                         'getversion', 'getconfig', 'getfield',
                                         'getoption', 'getmodule']):
                methods.add(s)
    print(f"\n=== 业务方法名 ({len(methods)}) ===")
    for s in sorted(methods):
        print(f"  {s}")

    # 6. transmitfile
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
                                    'Execution', 'Result', 'Report', 'Statistics']) and len(s) < 100 and not s.startswith('<'):
            biz.add(s)
    print(f"\n=== 业务类名 ({len(biz)}) ===")
    for s in sorted(biz)[:50]:
        print(f"  {s}")

    # 8. RemoteObject 相关
    remote = [s for s in all_strs if 'remote' in s.lower() and len(s) < 60]
    print(f"\n=== Remote 相关 ({len(remote)}) ===")
    for s in sorted(set(remote))[:30]:
        print(f"  {s}")

    # 9. 所有看起来像 BlazeDS destination 的字符串
    # 在 Flex 中, destination 名通常是 snake_case 或 camelCase
    # 且会出现在 RemoteObject 或 ChannelSet 配置中
    flex_dest = set()
    for s in all_strs:
        if re.match(r'^[a-z][a-zA-Z]+$', s) and len(s) > 8 and len(s) < 30:
            sl = s.lower()
            # 排除 Flex 内置类名
            if not any(kw in sl for kw in ['effect', 'style', 'manager', 'event', 'error',
                                            'binding', 'animation', 'transition', 'effect',
                                            'cursor', 'focus', 'drag', 'tooltip', 'validator',
                                            'formatter', 'skin', 'layout', 'container',
                                            'button', 'label', 'text', 'list', 'grid',
                                            'chart', 'series', 'stroke', 'fill',
                                            'default', 'class', 'instance', 'factory',
                                            'info', 'descriptor', 'record', 'item',
                                            'header', 'footer', 'navigator']):
                flex_dest.add(s)
    print(f"\n=== 可能的 Destination（过滤后）({len(flex_dest)}) ===")
    for s in sorted(flex_dest)[:50]:
        print(f"  {s}")

    # 10. 打印前 200 个唯一字符串
    unique_strs = sorted(set(all_strs))
    print(f"\n=== 前 200 个唯一字符串（共 {len(unique_strs)}） ===")
    for s in unique_strs[:200]:
        print(f"  {s}")
else:
    print("解压结果太小，无法分析")

    # 直接从解密但未解压的数据中提取字符串
    print("\n=== 从解密但未解压的数据中提取 ===")
    all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decrypted)]
    print(f"字符串数: {len(all_strs)}")
    for s in sorted(set(all_strs))[:100]:
        print(f"  {s}")
