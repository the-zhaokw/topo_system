"""测试 Liferay portlet resource URL 和 JSON service"""
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

# === 1. Liferay JSON service - 尝试不同格式 ===
print("\n=== 1. Liferay JSON service (尝试不同格式) ===")

# 格式1: cmd JSON
cmds = [
    '{"serviceClassName":"com.liferay.portal.service.OrganizationServiceUtil","serviceMethodName":"getOrganizations","parameterValues":{}}',
    '{"serviceClassName":"com.liferay.portal.service.UserServiceUtil","serviceMethodName":"getUserByScreenName","parameterValues":{"screenName":"zhaokw"}}',
    '{"serviceClassName":"com.liferay.portal.service.GroupServiceUtil","serviceMethodName":"getUserGroups","parameterValues":{}}',
]

for cmd in cmds:
    try:
        resp = session.post('http://172.18.36.5:8000/c/portal/json_service',
                           data={'cmd': cmd},
                           timeout=5)
        if resp.status_code == 200 and len(resp.text) > 5:
            print(f"  cmd format: {resp.text[:200]}")
    except:
        pass

# 格式2: 直接参数
params = [
    ('com.liferay.portal.service.OrganizationServiceUtil', 'getOrganizations', {}),
    ('com.liferay.portal.service.UserServiceUtil', 'getUserByScreenName', {'screenName': 'zhaokw'}),
    ('com.liferay.portal.service.GroupServiceUtil', 'getUserGroups', {}),
]

for svc, method, args in params:
    data = {
        'serviceClassName': svc,
        'serviceMethodName': method,
    }
    data.update(args)
    try:
        resp = session.post('http://172.18.36.5:8000/c/portal/json_service',
                           data=data, timeout=5)
        if resp.status_code == 200 and len(resp.text) > 5:
            text = resp.text.strip()
            if 'not valid' not in text:
                print(f"  direct format: {svc}.{method}: {text[:200]}")
    except:
        pass

# 格式3: JSON body
for svc, method, args in params:
    json_body = json.dumps({
        'serviceClassName': svc,
        'serviceMethodName': method,
        'parameterValues': args,
    })
    try:
        resp = session.post('http://172.18.36.5:8000/c/portal/json_service',
                           data=json_body,
                           headers={'Content-Type': 'application/json'},
                           timeout=5)
        if resp.status_code == 200 and len(resp.text) > 5:
            text = resp.text.strip()
            if 'not valid' not in text:
                print(f"  json body format: {svc}.{method}: {text[:200]}")
    except:
        pass

# === 2. Portlet resource URL ===
print("\n=== 2. Portlet resource URL ===")
# 获取页面 HTML 找到 portlet ID
r = session.get('http://172.18.36.5:8000/user/zhaokw', timeout=15)
# 搜索 portlet ID
portlet_ids = re.findall(r'p_p_id["\']?\s*[:=]\s*["\']([^"\']+)', r.text)
print(f"找到的 portlet IDs: {sorted(set(portlet_ids))[:20]}")

# 也搜索 portlet 实例 ID
portlet_inst = re.findall(r'portletId["\']?\s*[:=]\s*["\']([^"\']+)', r.text)
print(f"找到的 portlet 实例 IDs: {sorted(set(portlet_inst))[:20]}")

# 尝试 resource URL
portlet_names = ['draco_WAR_dracoportlet', 'extdraco_WAR_extdracoportlet', 'draco', 'Draco', 'Draco_Home']
resource_ids = ['bug', 'bugs', 'project', 'projects', 'task', 'tasks',
                'organization', 'organizations', 'org', 'orgs',
                'getData', 'getBug', 'getProject', 'export', 'exportBugs',
                'exportData', 'list', 'query', 'search',
                'dmBug', 'dmProject', 'data', 'dataModel',
                'schema', 'config', 'module', 'tree',
                'rtn', 'RTN', 'ipran', 'IPRAN']

for pname in portlet_names:
    for rid in resource_ids:
        url = (f'http://172.18.36.5:8000/web/guest/home'
               f'?p_p_id={pname}'
               f'&p_p_lifecycle=2'
               f'&p_p_state=normal'
               f'&p_p_mode=view'
               f'&p_p_resource_id={rid}')
        try:
            resp = session.get(url, timeout=5)
            if resp.status_code == 200 and len(resp.text) > 5:
                ct = resp.headers.get('content-type', '')
                text = resp.text.strip()
                if text and 'not found' not in text.lower() and 'error' not in text.lower()[:20]:
                    if len(text) > 20 or 'json' in ct or 'xml' in ct:
                        print(f"  {pname}/{rid}: {resp.status_code} ({ct}, {len(resp.text)} bytes)")
                        print(f"    Content: {text[:300]}")
        except:
            pass

# === 3. 检查 /c/json_service 页面 ===
print("\n=== 3. 检查 /c/json_service ===")
r = session.get('http://172.18.36.5:8000/c/json_service', timeout=15)
print(f"页面大小: {len(r.text)} bytes")
# 保存完整内容
with open('d:/topo_system/backend/json_service_page.html', 'w', encoding='utf-8') as f:
    f.write(r.text)
print("已保存到 json_service_page.html")

# 搜索关键信息
for kw in ['amf', 'service', 'destination', 'swf', 'module', 'config',
           'bug', 'project', 'org', 'api', 'rest', 'json']:
    count = r.text.lower().count(kw.lower())
    if count > 0:
        print(f"  关键字 '{kw}': {count}次")

# === 4. 尝试 /c/portal/render_portlet ===
print("\n=== 4. Portlet render ===")
for pname in portlet_names:
    url = (f'http://172.18.36.5:8000/web/guest/home'
           f'?p_p_id={pname}'
           f'&p_p_lifecycle=1'
           f'&p_p_state=normal'
           f'&p_p_mode=view')
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.text) > 100:
            text = resp.text
            for kw in ['bug', 'project', 'dmBug', 'amf', 'destination', 'service']:
                if kw.lower() in text.lower():
                    print(f"  {pname}: 包含 '{kw}'")
    except:
        pass

# === 5. 尝试直接 HTTP 端点 ===
print("\n=== 5. 直接 HTTP 端点 ===")
endpoints = [
    '/html/portlet/ext/draco/getData.jsp',
    '/html/portlet/ext/draco/api.jsp',
    '/html/portlet/ext/draco/service.jsp',
    '/html/portlet/ext/draco/data.jsp',
    '/html/portlet/ext/draco/bug.jsp',
    '/html/portlet/ext/draco/export.jsp',
    '/html/portlet/ext/draco/query.jsp',
    '/html/portlet/ext/draco/index.jsp',
    '/html/portlet/ext/draco/view.jsp',
    '/html/portlet/ext/draco/edit.jsp',
    '/html/portlet/ext/draco/',
    '/html/portlet/ext/draco/init.jsp',
    '/html/portlet/ext/draco/main.jsp',
    '/html/portlet/ext/draco/action.jsp',
    '/html/portlet/ext/draco/process.jsp',
    '/html/portlet/ext/draco/ajax.jsp',
    '/html/portlet/ext/draco/json.jsp',
    '/html/portlet/ext/draco/rest.jsp',
]

for ep in endpoints:
    url = f'http://172.18.36.5:8000{ep}'
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.text) > 10:
            ct = resp.headers.get('content-type', '')
            print(f"  OK {ep}: {resp.status_code} ({ct}, {len(resp.text)} bytes)")
            if 'text' in ct or 'json' in ct or 'xml' in ct:
                content = resp.text[:500]
                if any(kw in content.lower() for kw in ['bug', 'project', 'service', 'amf', 'destination', 'data']):
                    print(f"    Content: {content[:300]}")
    except:
        pass

# === 6. 尝试 POST 到各种端点 ===
print("\n=== 6. POST 端点 ===")
for ep in ['/html/portlet/ext/draco/action.jsp', '/html/portlet/ext/draco/data.jsp']:
    url = f'http://172.18.36.5:8000{ep}'
    for data in [
        {'action': 'getBugs', 'org': 'RTN'},
        {'action': 'getBugs', 'project': 'IPRAN'},
        {'action': 'query', 'model': 'dmBug', 'query': 'all'},
        {'action': 'list', 'entity': 'dmBug'},
        {'cmd': 'getBugs'},
        {'cmd': 'getBugs', 'org': 'RTN'},
    ]:
        try:
            resp = session.post(url, data=data, timeout=5)
            if resp.status_code == 200 and len(resp.text) > 10:
                text = resp.text.strip()
                if 'not found' not in text.lower()[:20]:
                    print(f"  POST {ep}: {list(data.items())} => {text[:200]}")
                    break
        except:
            pass
