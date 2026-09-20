"""修正登录方式 + 探查 c/portal/json + 提取 SWF 字符串"""
import requests
import re
import json

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

# 1. 获取登录页面，提取 JSESSIONID 和表单 action
print("=== 1. 获取登录页面 ===")
r = s.get('http://172.18.36.5:8000/', timeout=10)
jsessionid = s.cookies.get('JSESSIONID', '')
print(f"JSESSIONID: {jsessionid}")

# 提取表单 action（包含 jsessionid）
form_action = re.search(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*method=["\']post["\']', r.text, re.I)
if form_action:
    action_url = form_action.group(1)
    print(f"Form action: {action_url}")
else:
    action_url = None
    print("No form action found")

# 2. 使用带 JSESSIONID 的 URL 登录
print("\n=== 2. 登录（带 JSESSIONID URL） ===")
if action_url:
    login_url = action_url
else:
    login_url = f'http://172.18.36.5:8000/web/guest/home;jsessionid={jsessionid}?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'

login_data = {
    '_58_redirect': '',
    '_58_rememberMe': 'false',
    '_58_login': 'zhaokw',
    '_58_password': '123qwer',
}

r2 = s.post(login_url, data=login_data, timeout=15, allow_redirects=False)
print(f"Status: {r2.status_code}")
print(f"Location: {r2.headers.get('Location', 'N/A')}")
print(f"Set-Cookie: {r2.headers.get('Set-Cookie', 'N/A')[:200]}")

if r2.status_code == 302:
    print("登录成功！302 重定向")
    redirect_url = r2.headers.get('Location', '')
    if not redirect_url.startswith('http'):
        redirect_url = f'http://172.18.36.5:8000{redirect_url}'
    # 跟随重定向
    r3 = s.get(redirect_url, timeout=10)
    print(f"Redirect page: {r3.status_code}, URL: {r3.url}")
    is_logged = 'sign-out' in r3.text.lower() or '登出' in r3.text
    print(f"Logged in: {is_logged}")
    theme = re.findall(r"isSignedIn:function\(\)\{return([^}]+)\}", r3.text, re.I)
    print(f"isSignedIn: {theme}")
else:
    # 检查错误
    errors = re.findall(r'portlet-msg-error[^>]*>(.*?)<', r2.text, re.I | re.S)
    print(f"Errors: {errors[:3]}")

# 3. 查看 c/portal/json
print("\n=== 3. c/portal/json ===")
r4 = s.get('http://172.18.36.5:8000/c/portal/json', timeout=10)
print(f"Status: {r4.status_code}, Length: {len(r4.text)}")
# 尝试解析 JSON
try:
    data = r4.json()
    print(f"JSON keys: {list(data.keys())[:10] if isinstance(data, dict) else type(data)}")
    if isinstance(data, dict):
        for k, v in list(data.items())[:5]:
            print(f"  {k}: {str(v)[:200]}")
except:
    print(f"Body[:1000]: {r4.text[:1000]}")

# 4. 尝试 c/portal/json 的不同操作
print("\n=== 4. c/portal/json 操作 ===")
json_ops = [
    '/c/portal/json?p_p_id=58&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=%2Flogin%2Flogin',
    '/c/portal/json?cmd=getUser',
    '/c/portal/json?cmd=getProjects',
    '/c/portal/json?cmd=getTestCases',
    '/c/portal/json?cmd=getTestPlans',
    '/c/portal/json?cmd=getTestRuns',
]
for op in json_ops:
    try:
        r = s.get(f'http://172.18.36.5:8000{op}', timeout=5)
        info = f"Status: {r.status_code}"
        if r.status_code == 200 and len(r.text) < 500:
            info += f" Body: {r.text[:300]}"
        else:
            info += f" Length: {len(r.text)}"
        print(f"  {op} -> {info}")
    except Exception as e:
        print(f"  {op} -> Error: {e}")

# 5. 提取 SWF 中所有可读字符串
print("\n=== 5. SWF 字符串提取 ===")
r5 = s.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', timeout=30)
if r5.status_code == 200:
    content = r5.content
    # 提取所有 ASCII 字符串（>= 5 字符）
    strings = re.findall(rb'[\x20-\x7e]{5,}', content)
    all_strings = [s.decode('ascii', errors='ignore') for s in strings]
    print(f"Total strings: {len(all_strings)}")

    # 过滤可能包含 API 端点的字符串
    api_strings = [s for s in all_strings if any(kw in s.lower() for kw in ['http', '/portal', '/draco', '.do', '.action', '.json', 'api', 'service', 'servlet', 'ajax', 'remoting', 'dwr', 'spring'])]
    print(f"API-like strings ({len(api_strings)}):")
    for s in api_strings[:40]:
        print(f"  {s}")

    # 查找 Java 类名或服务名
    java_strings = [s for s in all_strings if any(kw in s for kw in ['com.', 'org.', 'cn.', 'Service', 'Controller', 'Action', 'Servlet', 'Factory', 'Manager', 'Dao', 'Mapper'])]
    print(f"\nJava-like strings ({len(java_strings)}):")
    for s in java_strings[:30]:
        print(f"  {s}")

    # 查找 BlazeDS / AMF 端点
    amf_strings = [s for s in all_strings if any(kw in s.lower() for kw in ['amf', 'blaze', 'message', 'channel', 'endpoint', 'gateway', 'destination'])]
    print(f"\nAMF/BlazeDS strings ({len(amf_strings)}):")
    for s in amf_strings[:20]:
        print(f"  {s}")

    # 查找所有包含 / 的字符串（可能是路径）
    path_strings = [s for s in all_strings if '/' in s and len(s) > 8 and len(s) < 200 and not s.startswith('//')]
    print(f"\nPath-like strings ({len(path_strings)}):")
    for s in path_strings[:40]:
        print(f"  {s}")
