"""下载 cache-config.xml 和搜索 SWF 中的 BlazeDS 配置"""
import requests as req
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

# === 1. 下载 cache-config.xml ===
print("\n=== 1. 下载 cache-config.xml ===")
url = 'http://172.18.36.5:8000/html/portlet/ext/draco/resources/cache-config.xml'
r = session.get(url, timeout=15)
print(f"cache-config.xml: {r.status_code} ({len(r.text)} bytes)")
if r.status_code == 200:
    print(r.text[:5000])
    with open('d:/topo_system/backend/cache-config.xml', 'w', encoding='utf-8') as f:
        f.write(r.text)

# === 2. 从 draco_manager.swf 搜索 XML 配置 ===
print("\n\n=== 2. 从 SWF 搜索 BlazeDS XML 配置 ===")
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', timeout=60)
raw = r.content
if raw[:3] == b'CWS':
    swf_data = zlib.decompress(raw[8:])
else:
    swf_data = raw

# 搜索 XML 内容 (services-config 或 remoting-config 模式)
xml_matches = re.findall(rb'<services[^>]*>.*?</services>', swf_data, re.DOTALL)
print(f"services XML 块: {len(xml_matches)}")
for xml in xml_matches:
    print(f"  {xml.decode('utf-8', errors='replace')[:2000]}")

xml_matches2 = re.findall(rb'<channel[^>]*>.*?</channel>', swf_data, re.DOTALL)
print(f"\nchannel XML 块: {len(xml_matches2)}")
for xml in xml_matches2:
    print(f"  {xml.decode('utf-8', errors='replace')[:2000]}")

xml_matches3 = re.findall(rb'<destination[^>]*>.*?</destination>', swf_data, re.DOTALL)
print(f"\ndestination XML 块: {len(xml_matches3)}")
for xml in xml_matches3:
    print(f"  {xml.decode('utf-8', errors='replace')[:2000]}")

# 搜索所有 XML 标签
xml_tags = re.findall(rb'<(\w+)[^>]*>', swf_data)
tag_counts = {}
for tag in xml_tags:
    t = tag.decode('ascii', errors='ignore')
    if t not in ['html', 'head', 'body', 'style', 'script', 'div', 'span', 'RDF', 'Description']:
        tag_counts[t] = tag_counts.get(t, 0) + 1

print(f"\nXML 标签统计:")
for t, c in sorted(tag_counts.items(), key=lambda x: -x[1])[:20]:
    print(f"  {t}: {c}")

# 搜索 channel/endpoint/amf 相关
amf_patterns = [
    rb'[\w/]+messagebroker[\w/]*',
    rb'[\w/]+amf[\w/]*',
    rb'[\w/]+channel[\w/]*',
    rb'[\w/]+endpoint[\w/]*',
]

for pattern in amf_patterns:
    matches = re.findall(pattern, swf_data, re.IGNORECASE)
    if matches:
        unique = sorted(set(m.decode('ascii', errors='ignore') for m in matches))
        print(f"\n  Pattern '{pattern.decode()}': {unique[:10]}")

# === 3. 搜索 destination 配置 ===
print("\n\n=== 3. 搜索 destination 配置 ===")
# 在 Flex SWF 中, destination 配置可能以字符串数组形式存在
# 搜索 "destination" 关键字附近的内容
dest_pattern = rb'(?:destination|Destination)[\x00-\x20]{0,5}[\x01-\x02]..([\x20-\x7e]{3,50})'
dest_matches = re.findall(dest_pattern, swf_data)
print(f"destination 相关: {len(dest_matches)}")
for m in dest_matches:
    print(f"  {m.decode('ascii', errors='ignore')}")

# 搜索 "Service" 结尾的字符串 (可能是 destination 名)
svc_pattern = rb'[\x20-\x7e]{3,50}Service'
svc_matches = set()
for m in re.findall(svc_pattern, swf_data):
    s = m.decode('ascii', errors='ignore')
    if not any(c in s for c in ['<', '>', '/']):
        svc_matches.add(s)

print(f"\n以 Service 结尾的字符串 ({len(svc_matches)}):")
for s in sorted(svc_matches):
    print(f"  {s}")

# === 4. 检查其他 resources 文件 ===
print("\n\n=== 4. 检查其他 resources 文件 ===")
other_files = [
    '/html/portlet/ext/draco/resources/cache-config.xml',
    '/html/portlet/ext/draco/resources/framework.swf',
    '/html/portlet/ext/draco/resources/draco_framework.swf',
    '/html/portlet/ext/draco/resources/rpclibs.swf',
    '/html/portlet/ext/draco/resources/draco_lib.swf',
    '/html/portlet/ext/draco/resources/draco_common.swf',
    '/html/portlet/ext/draco/resources/draco_core.swf',
    '/html/portlet/ext/draco/resources/draco_rpclib.swf',
    '/html/portlet/ext/draco/resources/draco_flex.swf',
    '/html/portlet/ext/draco/resources/draco_rpc.swf',
    '/html/portlet/ext/draco/resources/draco.swf',
    '/html/portlet/ext/draco/resources/rpc.swf',
    '/html/portlet/ext/draco/resources/rpclib.swf',
    '/html/portlet/ext/draco/resources/frameworks.swf',
    '/html/portlet/ext/draco/resources/main.swf',
    '/html/portlet/ext/draco/resources/app.swf',
    '/html/portlet/ext/draco/resources/draco_manager_config.xml',
    '/html/portlet/ext/draco/resources/draco_module.swf',
    '/html/portlet/ext/draco/resources/draco.swf',
    '/html/portlet/ext/draco/modules/draco_module.swf',
    '/html/portlet/ext/draco/modules/draco_drmng.swf',
    '/html/portlet/ext/draco/modules/draco_devMng.swf',
    '/html/portlet/ext/draco/modules/draco_devmng.swf',
    '/html/portlet/ext/draco/modules/draco_user.swf',
    '/html/portlet/ext/draco/modules/draco_project.swf',
    '/html/portlet/ext/draco/modules/draco_bug.swf',
    '/html/portlet/ext/draco/modules/draco_test.swf',
    '/html/portlet/ext/draco/modules/draco_report.swf',
    '/html/portlet/ext/draco/modules/draco_risk.swf',
    '/html/portlet/ext/draco/modules/draco_version.swf',
    '/html/portlet/ext/draco/modules/draco_baseline.swf',
    '/html/portlet/ext/draco/modules/draco_cost.swf',
    '/html/portlet/ext/draco/modules/draco_layout.swf',
    '/html/portlet/ext/draco/modules/draco_task.swf',
    '/html/portlet/ext/draco/modules/draco_requirement.swf',
    '/html/portlet/ext/draco/modules/draco_phase.swf',
    '/html/portlet/ext/draco/modules/draco_codeReview.swf',
    '/html/portlet/ext/draco/modules/draco_docReview.swf',
    '/html/portlet/ext/draco/modules/draco_testcase.swf',
    '/html/portlet/ext/draco/modules/draco_testrun.swf',
    '/html/portlet/ext/draco/modules/draco_testsuite.swf',
]

for f in other_files:
    url = f'http://172.18.36.5:8000{f}'
    try:
        resp = session.head(url, timeout=5, allow_redirects=True)
        if resp.status_code == 200:
            ct = resp.headers.get('content-type', '')
            size = resp.headers.get('content-length', '?')
            print(f"  OK {f}: {resp.status_code} ({ct}, {size} bytes)")
    except:
        pass

# === 5. 尝试 transmitfile 端点 ===
print("\n\n=== 5. transmitfile 端点 ===")
for cmd in ['download', 'upload', 'list', 'get']:
    url = f'http://172.18.36.5:8000/transmitfile?cmd={cmd}'
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200:
            print(f"  GET transmitfile?cmd={cmd}: {resp.status_code} ({len(resp.text)} bytes)")
            print(f"    Content: {resp.text[:200]}")
    except:
        pass

# 尝试不同的 URL 参数来获取 bug 数据
print("\n\n=== 6. 尝试 URL 参数方式获取数据 ===")
url_tests = [
    'http://172.18.36.5:8000/html/client/topo/?pageType=query&queryName=all&queryScope=dmBug',
    'http://172.18.36.5:8000/html/client/topo/?model=dmBug&query=all',
    'http://172.18.36.5:8000/html/client/topo/?dataModel=dmBug&queryName=all',
    'http://172.18.36.5:8000/html/client/topo/#pageType=query&queryName=all&queryScope=dmBug',
    'http://172.18.36.5:8000/html/client/topo/?bug=all',
    'http://172.18.36.5:8000/html/client/topo/?entity=dmBug&query=all',
]
for url in url_tests:
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.text) > 100:
            print(f"  {url}: {resp.status_code} ({len(resp.text)} bytes)")
    except:
        pass
