"""探索 Liferay REST API 和 BlazeDS 配置"""
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

# === 1. 检查 Liferay JSON WS API ===
print("\n=== 1. Liferay JSON WS API ===")
endpoints = [
    '/api/jsonws/',
    '/api/jsonws/invoke',
    '/api/secure/jsonws/',
    '/api/jsonws/get-user',
    '/api/jsonws/group/get-groups',
    '/api/jsonws/organization/get-organizations',
    '/c/portal/json_service',
    '/c/json_service',
    '/web/guest/api/jsonws',
]

for ep in endpoints:
    url = f'http://172.18.36.5:8000{ep}'
    try:
        resp = session.get(url, timeout=5)
        print(f"  GET {ep}: {resp.status_code} ({resp.headers.get('content-type', '')})")
        if resp.status_code == 200 and len(resp.text) > 50:
            print(f"    Body: {resp.text[:300]}")
    except:
        print(f"  GET {ep}: 超时")

# POST invoke
for ep in ['/api/jsonws/invoke', '/api/secure/jsonws/invoke']:
    url = f'http://172.18.36.5:8000{ep}'
    try:
        resp = session.post(url, data='{}', headers={'Content-Type': 'application/json'}, timeout=5)
        print(f"  POST {ep}: {resp.status_code}")
        if resp.status_code in [200, 400, 401, 403]:
            print(f"    Body: {resp.text[:300]}")
    except:
        pass

# === 2. 检查 Liferay Portal 结构 ===
print("\n=== 2. Portal 结构 ===")
portal_urls = [
    '/web/zhaokw/home',
    '/group',
    '/user/zhaokw',
    '/web/guest/portal',
    '/c/portal/layout',
    '/group/control_panel',
    '/web/zhaokw/portal',
    '/web/guest/home?p_p_id=draco',
    '/html/portlet/ext/draco/',
    '/html/client/topo/',
    '/html/client/',
]

for ep in portal_urls:
    url = f'http://172.18.36.5:8000{ep}'
    try:
        resp = session.get(url, timeout=5, allow_redirects=False)
        status = resp.status_code
        loc = resp.headers.get('location', '')
        ct = resp.headers.get('content-type', '')
        if status in [200, 302, 301]:
            print(f"  {ep}: {status} ({ct})")
            if loc:
                print(f"    Redirect: {loc}")
            if status == 200 and 'html' in ct and len(resp.text) > 100:
                text = resp.text
                for kw in ['draco', 'topo', 'bug', 'project', 'amf', 'swf', 'portlet']:
                    if kw.lower() in text.lower():
                        count = text.lower().count(kw.lower())
                        print(f"    关键字 '{kw}': {count}次")
    except:
        pass

# === 3. 检查 BlazeDS 配置文件 ===
print("\n=== 3. BlazeDS 配置 ===")
config_files = [
    '/WEB-INF/flex/remoting-config.xml',
    '/WEB-INF/flex/services-config.xml',
    '/WEB-INF/flex/proxy-config.xml',
    '/WEB-INF/web.xml',
    '/WEB-INF/remoting-config.xml',
    '/WEB-INF/services-config.xml',
    '/messagebroker/amf',
    '/flex2/remoting-config.xml',
    '/flex2/services-config.xml',
    '/html/client/config.xml',
    '/html/client/services-config.xml',
    '/html/client/remoting-config.xml',
    '/html/portlet/ext/draco/remoting-config.xml',
    '/html/portlet/ext/draco/services-config.xml',
    '/html/portlet/ext/draco/crossdomain.xml',
]

for ep in config_files:
    url = f'http://172.18.36.5:8000{ep}'
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.text) > 10:
            print(f"  OK {ep}: {resp.status_code} ({len(resp.text)} bytes)")
            ct = resp.headers.get('content-type', '')
            if 'xml' in ct or 'json' in ct or 'text' in ct:
                print(f"    Content: {resp.text[:500]}")
        elif resp.status_code != 404:
            print(f"  {ep}: {resp.status_code}")
    except:
        pass

# === 4. 检查 crossdomain.xml 和其他根目录文件 ===
print("\n=== 4. 根目录文件 ===")
root_files = [
    '/crossdomain.xml',
    '/html/crossdomain.xml',
    '/html/client/crossdomain.xml',
    '/html/client/topo/crossdomain.xml',
    '/html/client/topo/config.xml',
    '/html/client/topo/services-config.xml',
    '/html/client/topo/index.html',
    '/html/client/topo/index.jsp',
    '/html/client/topo/topo.swf',
    '/html/client/topo/main.swf',
    '/html/client/topo/app.swf',
    '/html/client/topo/topo.html',
    '/html/client/topo/topo.jsp',
    '/html/client/topo/',
]

for ep in root_files:
    url = f'http://172.18.36.5:8000{ep}'
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200:
            ct = resp.headers.get('content-type', '')
            print(f"  OK {ep}: {resp.status_code} ({ct}, {len(resp.content)} bytes)")
            if 'text' in ct or 'xml' in ct:
                content = resp.text[:1000]
                if any(kw in content.lower() for kw in ['amf', 'service', 'destination', 'channel', 'swf', 'flash']):
                    print(f"    Content: {content[:500]}")
    except:
        pass

# === 5. 直接访问 AMF 端点 GET ===
print("\n=== 5. AMF 端点 GET ===")
try:
    resp = session.get('http://172.18.36.5:8000/messagebroker/amf', timeout=5)
    print(f"  GET /messagebroker/amf: {resp.status_code} ({resp.headers.get('content-type', '')})")
    print(f"  Body: {resp.content[:200].hex()}")
except Exception as e:
    print(f"  Error: {e}")

# === 6. 尝试访问 Liferay 7 API ===
print("\n=== 6. Liferay 7 API ===")
try:
    resp = session.get('http://172.18.36.5:8000/o/headless-admin-user/v1.0/organization', timeout=5)
    print(f"  /o/headless-admin-user/v1.0/organization: {resp.status_code}")
    if resp.status_code == 200:
        print(f"  Body: {resp.text[:500]}")
except:
    pass

try:
    resp = session.get('http://172.18.36.5:8000/o/headless-admin-user/v1.0/user-account', timeout=5)
    print(f"  /o/headless-admin-user/v1.0/user-account: {resp.status_code}")
except:
    pass

# === 7. 搜索所有 draco portlet URL ===
print("\n=== 7. Draco portlet 页面 ===")
draco_urls = [
    '/web/guest/draco',
    '/web/zhaokw/draco',
    '/web/guest/home?p_p_id=draco_WAR_dracoportlet',
    '/web/guest/home?p_p_id=dracoportlet_WAR_dracoportlet',
    '/web/guest/home?p_p_id=extdraco_WAR_extdracoportlet',
    '/web/guest/home?p_p_id=draco',
    '/web/zhaokw/home',
    '/web/guest/portal',
    '/group/guest/portal',
    '/group/zhaokw/portal',
]

for ep in draco_urls:
    url = f'http://172.18.36.5:8000{ep}'
    try:
        resp = session.get(url, timeout=5, allow_redirects=True)
        if resp.status_code == 200 and 'html' in resp.headers.get('content-type', ''):
            text = resp.text.lower()
            if 'draco' in text or 'topo' in text or 'bug' in text or 'amf' in text:
                print(f"  OK {ep}: {resp.status_code} (包含 draco/topo/bug)")
                urls_found = re.findall(r'(/html/[^"\']*draco[^"\']*)', resp.text)
                for u in sorted(set(urls_found))[:20]:
                    print(f"    URL: {u}")
                urls_found2 = re.findall(r'(/html/[^"\']*topo[^"\']*)', resp.text)
                for u in sorted(set(urls_found2))[:10]:
                    print(f"    URL: {u}")
    except:
        pass
