"""尝试 Liferay JSON Service API 和查找模块配置"""
import requests as req
import json
import re

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

# === 1. Liferay JSON Service (旧版 API) ===
print("\n=== 1. Liferay JSON Service ===")

# 获取 auth token
try:
    r = session.get('http://172.18.36.5:8000/c/portal/json_service', timeout=5)
    # 搜索 p_auth token
    auth_match = re.search(r'["\']p_auth["\']:\s*["\']([^"\']+)', r.text)
    if auth_match:
        p_auth = auth_match.group(1)
        print(f"  找到 p_auth: {p_auth}")
    else:
        p_auth = ''
        print("  未找到 p_auth")
except:
    p_auth = ''

# 尝试调用 JSON service (Liferay 5/6 旧版格式)
service_calls = [
    # 组织相关
    ('com.liferay.portal.service.OrganizationServiceUtil', 'getOrganizations', {}),
    ('com.liferay.portal.service.OrganizationServiceUtil', 'getUserOrganizations', {}),
    # 用户相关
    ('com.liferay.portal.service.UserServiceUtil', 'getUserByScreenName', {'screenName': 'zhaokw'}),
    ('com.liferay.portal.service.UserServiceUtil', 'getUserIdByScreenName', {'screenName': 'zhaokw'}),
    # Group/Site
    ('com.liferay.portal.service.GroupServiceUtil', 'getGroups', {}),
    ('com.liferay.portal.service.GroupServiceUtil', 'getUserGroups', {}),
    # Company
    ('com.liferay.portal.service.CompanyServiceUtil', 'getCompanyById', {}),
]

for svc_class, svc_method, params in service_calls:
    # GET 方式
    params_url = '&'.join(f'{k}={v}' for k, v in params.items())
    url = f'http://172.18.36.5:8000/c/portal/json_service?serviceClassName={svc_class}&serviceMethodName={svc_method}&{params_url}'
    if p_auth:
        url += f'&p_auth={p_auth}'
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.text) > 10:
            text = resp.text.strip()
            if text.startswith('{') or text.startswith('['):
                print(f"\n  GET {svc_class}.{svc_method}: {resp.status_code}")
                print(f"    Response: {text[:500]}")
            elif 'not valid' in text:
                pass  # Skip error
            else:
                print(f"  GET {svc_class}.{svc_method}: {resp.status_code} (non-JSON)")
    except:
        pass

    # POST 方式
    data = {
        'serviceClassName': svc_class,
        'serviceMethodName': svc_method,
    }
    data.update(params)
    if p_auth:
        data['p_auth'] = p_auth
    try:
        resp = session.post('http://172.18.36.5:8000/c/portal/json_service',
                           data=data, timeout=5)
        if resp.status_code == 200 and len(resp.text) > 10:
            text = resp.text.strip()
            if text.startswith('{') or text.startswith('['):
                print(f"\n  POST {svc_class}.{svc_method}: {resp.status_code}")
                print(f"    Response: {text[:500]}")
            elif 'not valid' not in text:
                print(f"  POST {svc_class}.{svc_method}: {resp.status_code} ({text[:100]})")
    except:
        pass

# === 2. 查找模块配置文件 ===
print("\n\n=== 2. 查找模块配置文件 ===")
config_urls = [
    '/html/portlet/ext/draco/resources/moduleConfig.xml',
    '/html/portlet/ext/draco/resources/modules.xml',
    '/html/portlet/ext/draco/resources/config.xml',
    '/html/portlet/ext/draco/resources/draco_config.xml',
    '/html/portlet/ext/draco/resources/module.xml',
    '/html/portlet/ext/draco/resources/draco.xml',
    '/html/portlet/ext/draco/resources/config.properties',
    '/html/portlet/ext/draco/resources/config.json',
    '/html/portlet/ext/draco/modules/moduleConfig.xml',
    '/html/portlet/ext/draco/modules/config.xml',
    '/html/portlet/ext/draco/modules/modules.xml',
    '/html/portlet/ext/draco/modules/module.xml',
    '/html/portlet/ext/draco/draco.xml',
    '/html/portlet/ext/draco/config.xml',
    '/html/portlet/ext/draco/crossdomain.xml',
    '/html/portlet/ext/draco/moduleConfig.xml',
    '/html/portlet/ext/draco/draco.properties',
    '/html/portlet/ext/draco/draco-config.xml',
]

for f in config_urls:
    url = f'http://172.18.36.5:8000{f}'
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.text) > 5:
            ct = resp.headers.get('content-type', '')
            print(f"\n  OK {f}: {resp.status_code} ({len(resp.text)} bytes, {ct})")
            # 如果是 XML, 打印内容
            if 'xml' in ct or 'text' in ct or 'json' in ct:
                print(f"    Content: {resp.text[:2000]}")
    except:
        pass

# === 3. 从 draco_manager.swf 中搜索模块加载 URL ===
print("\n\n=== 3. 从 draco_manager.swf 搜索模块 URL ===")
import zlib
r = session.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', timeout=60)
raw = r.content
if raw[:3] == b'CWS':
    swf_data = zlib.decompress(raw[8:])
elif raw[:3] == b'FWS':
    swf_data = raw[8:]
else:
    swf_data = raw

all_strs = [s.decode('ascii', errors='ignore')
            for s in re.findall(rb'[\x20-\x7e]{4,}', swf_data)]

# 搜索包含 .swf 的字符串
swf_strs = sorted(set(s for s in all_strs if '.swf' in s.lower()))
print(f"\nSWF 引用 ({len(swf_strs)}):")
for s in swf_strs:
    print(f"  {s}")

# 搜索包含 /html/ 的字符串
html_strs = sorted(set(s for s in all_strs if '/html/' in s or '/portlet/' in s))
print(f"\nHTML/Portlet URL ({len(html_strs)}):")
for s in html_strs:
    print(f"  {s}")

# 搜索包含 module 的字符串
module_strs = sorted(set(s for s in all_strs if 'module' in s.lower() or 'Module' in s))
print(f"\nModule 相关 ({len(module_strs)}):")
for s in module_strs:
    if len(s) < 100:
        print(f"  {s}")

# 搜索包含 config 的字符串
config_strs = sorted(set(s for s in all_strs if 'config' in s.lower() or 'Config' in s))
print(f"\nConfig 相关 ({len(config_strs)}):")
for s in config_strs:
    if len(s) < 100:
        print(f"  {s}")

# 搜索包含 dataModel 或 query 的字符串
dm_strs = sorted(set(s for s in all_strs if 'dataModel' in s or 'query' in s.lower() or 'Query' in s))
print(f"\nDataModel/Query 相关 ({len(dm_strs)}):")
for s in dm_strs:
    if len(s) < 100:
        print(f"  {s}")

# 搜索包含 load 的字符串 (模块加载相关)
load_strs = sorted(set(s for s in all_strs
                       if 'load' in s.lower() and len(s) < 100))
print(f"\nLoad 相关 ({len(load_strs)}):")
for s in load_strs[:30]:
    print(f"  {s}")
