"""完整解密 module SWF 并提取 AMF 服务信息"""
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

# 下载并解密 module SWF
print("=== 下载并解密 module SWF ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/modules/draco_module.swf', timeout=60)
mod_data = r.content

# DES-ECB 解密
KEY = md5(b'hzytkjyxgs').digest()[:8]
cipher = DES.new(KEY, DES.MODE_ECB)
# 需要对齐到 8 字节
padded_len = len(mod_data) - (len(mod_data) % 8)
decrypted = cipher.decrypt(mod_data[:padded_len])
# 追加剩余未对齐的字节
if len(mod_data) > padded_len:
    decrypted += mod_data[padded_len:]

print(f"解密后大小: {len(decrypted)} bytes")
print(f"前 8 字节: {decrypted[:8]}")

# ZLIB 解压
if decrypted[:3] == b'CWS':
    decompressed = decrypted[:8] + zlib.decompress(decrypted[8:])
    print(f"ZLIB 解压后: {len(decompressed)} bytes")
    # 保存解密后的 SWF
    with open('d:/topo_system/backend/draco_module_decrypted.swf', 'wb') as f:
        f.write(decrypted)
    with open('d:/topo_system/backend/draco_module_decompressed.bin', 'wb') as f:
        f.write(decompressed)
    print("已保存解密和解压后的文件")

    # 提取所有字符串
    all_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{4,}', decompressed)]
    print(f"字符串总数: {len(all_strs)}")

    # 1. com.loader 类
    loader = [s for s in all_strs if 'com.loader' in s]
    print(f"\n=== com.loader 类 ({len(loader)}) ===")
    for s in sorted(set(loader)):
        print(f"  {s}")

    # 2. Destination/RemoteObject 相关
    remote = [s for s in all_strs if any(kw in s.lower() for kw in ['remoteobject', 'destination', 'remote_']) and len(s) < 60]
    print(f"\n=== RemoteObject/Destination ({len(remote)}) ===")
    for s in sorted(set(remote))[:30]:
        print(f"  {s}")

    # 3. 所有 Service 字符串
    services = [s for s in all_strs if 'Service' in s and len(s) < 60 and not ' ' in s]
    print(f"\n=== Service 名 ({len(services)}) ===")
    for s in sorted(set(services))[:40]:
        print(f"  {s}")

    # 4. 业务方法名
    print(f"\n=== 业务方法名 ===")
    methods = set()
    for s in all_strs:
        if re.match(r'^[a-z][a-zA-Z0-9]{4,60}$', s):
            sl = s.lower()
            if any(kw in sl for kw in ['gettest', 'findtest', 'getproject', 'findproject', 'getplan', 'findplan',
                                         'getcase', 'findcase', 'getdefect', 'finddefect', 'getbug', 'findbug',
                                         'getmodule', 'findmodule', 'getrequirement', 'findrequirement',
                                         'getrun', 'findrun', 'getscenario', 'findscenario',
                                         'getenvironment', 'findenvironment', 'getbuild', 'findbuild',
                                         'getall', 'findall', 'getlist', 'findlist',
                                         'createtest', 'createproject', 'createplan', 'createcase',
                                         'createdefect', 'updatetest', 'updateproject', 'updateplan',
                                         'savetest', 'saveproject', 'deletetest', 'deleteproject',
                                         'loadtest', 'loadproject', 'loadplan', 'loadmodule',
                                         'querytest', 'queryproject', 'searchtest', 'searchproject',
                                         'getuser', 'finduser', 'gettask', 'findtask',
                                         'getexecution', 'findexecution', 'getresult', 'findresult',
                                         'getstep', 'findstep', 'getcategory', 'findcategory',
                                         'getversion', 'findversion', 'getconfig', 'findconfig',
                                         'getfield', 'findfield', 'getoption', 'findoption',
                                         'getpriority', 'getstatus', 'getseverity',
                                         'export', 'import', 'report', 'statistics',
                                         'getsummary', 'getdetail', 'getcount']):
                methods.add(s)
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

    mb = [s for s in all_strs if 'messagebroker' in s.lower() or 'amf' in s.lower() or 'channel' in s.lower()]
    print(f"\n=== messagebroker/amf 相关 ===")
    for s in sorted(set(mb)):
        print(f"  {s}")

    # 7. 所有看起来像 destination 名的短字符串
    # BlazeDS destination 通常是驼峰命名，如 "testCaseService"
    possible_dest = set()
    for s in all_strs:
        if re.match(r'^[a-z][a-zA-Z]+$', s) and len(s) > 5 and len(s) < 40:
            if any(kw in s.lower() for kw in ['service', 'delegate', 'proxy', 'facade']):
                possible_dest.add(s)
    print(f"\n=== 可能的 Destination 名 ({len(possible_dest)}) ===")
    for s in sorted(possible_dest):
        print(f"  {s}")

    # 8. 查找 RemoteObject 创建模式
    # 在 Flex 中, RemoteObject 通常使用 destination 属性
    # 查找包含 "destination" 或 "source" 的字符串
    dest_strings = [s for s in all_strs if 'destination' in s.lower() or s.lower().startswith('source') or s.lower().startswith('endpoint')]
    print(f"\n=== Destination/Source/Endpoint ({len(dest_strings)}) ===")
    for s in sorted(set(dest_strings))[:30]:
        print(f"  {s}")

    # 9. 查找 Flex 的 RemoteObject destination 配置
    # 在 ActionScript 中，destination 名通常是硬编码的字符串
    # 例如: new RemoteObject("testCaseService")
    # 查找所有看起来像 destination ID 的字符串
    dest_ids = set()
    for s in all_strs:
        # 驼峰命名，包含业务词汇
        if re.match(r'^[a-z][a-zA-Z]+(?:Service|Delegate|Proxy)$', s):
            dest_ids.add(s)
        # 也查找大写开头的
        if re.match(r'^[A-Z][a-zA-Z]+(?:Service|Delegate|Proxy)$', s):
            dest_ids.add(s)
    print(f"\n=== Destination ID ({len(dest_ids)}) ===")
    for s in sorted(dest_ids):
        print(f"  {s}")

    # 10. 查找所有类名中的业务关键词
    biz_classes = set()
    for s in all_strs:
        if any(kw in s for kw in ['TestCase', 'TestPlan', 'TestRun', 'TestSuite', 'TestStep',
                                    'Defect', 'Bug', 'Project', 'Module', 'Requirement',
                                    'Scenario', 'Environment', 'Build', 'Release',
                                    'Execution', 'Result', 'Report', 'Statistics',
                                    'Category', 'Priority', 'Severity']) and len(s) < 100:
            biz_classes.add(s)
    print(f"\n=== 业务类名 ({len(biz_classes)}) ===")
    for s in sorted(biz_classes)[:50]:
        print(f"  {s}")

print("\n完成！")
