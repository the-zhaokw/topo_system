"""检查登录失败原因 + 探查 Draco 后端"""
import requests
import re
import json

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'http://172.18.36.5:8000/',
})

# 1. 登录并检查错误
print("=== 1. 登录检查 ===")
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
login_data = {
    '_58_redirect': '',
    '_58_rememberMe': 'false',
    '_58_login': 'zhaokw',
    '_58_password': '123qwer',
}
r2 = s.post(login_url, data=login_data, timeout=15, allow_redirects=False)
print(f"Status: {r2.status_code}")
print(f"Location: {r2.headers.get('Location', 'N/A')}")
print(f"Set-Cookie: {r2.headers.get('Set-Cookie', 'N/A')}")

# 如果是302重定向，说明登录成功
if r2.status_code == 302:
    print("登录成功！302 重定向")
    redirect_url = r2.headers.get('Location', '')
    if not redirect_url.startswith('http'):
        redirect_url = f'http://172.18.36.5:8000{redirect_url}'
    r3 = s.get(redirect_url, timeout=10)
    print(f"Redirect page: {r3.status_code}")
else:
    # 检查错误
    errors = re.findall(r'class="[^"]*error[^"]*"[^>]*>(.*?)</div>', r2.text, re.I | re.S)
    print(f"Error divs: {errors[:3]}")
    # 查找所有 error 类
    error_spans = re.findall(r'<span[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</span>', r2.text, re.I | re.S)
    print(f"Error spans: {error_spans[:3]}")
    # 查找 portlet-msg-error
    portlet_errors = re.findall(r'portlet-msg-error[^>]*>(.*?)<', r2.text, re.I | re.S)
    print(f"Portlet errors: {portlet_errors[:3]}")

# 2. 探查 Draco 资源目录
print("\n=== 2. 探查 Draco 资源 ===")
draco_paths = [
    '/html/portlet/ext/draco/',
    '/html/portlet/ext/draco/resources/',
    '/html/portlet/ext/draco/resources/config.xml',
    '/html/portlet/ext/draco/resources/config.json',
    '/html/portlet/ext/draco/resources/config.properties',
    '/html/portlet/ext/draco/WEB-INF/',
    '/html/portlet/ext/draco/WEB-INF/web.xml',
    '/html/portlet/ext/draco/WEB-INF/portlet.xml',
    '/html/portlet/ext/draco/index.jsp',
    '/html/portlet/ext/draco/index.html',
]
for path in draco_paths:
    try:
        r = s.get(f'http://172.18.36.5:8000{path}', timeout=5)
        status_info = f"Status: {r.status_code}"
        if r.status_code == 200 and len(r.text) < 3000:
            status_info += f"\n  Body: {r.text[:1000]}"
        elif r.status_code == 200:
            status_info += f"\n  Body length: {len(r.text)}"
        print(f"  {path} -> {status_info}")
    except Exception as e:
        print(f"  {path} -> Error: {e}")

# 3. 探查常见的 Java Web API 端点
print("\n=== 3. 探查 Java Web API ===")
api_paths = [
    '/html/portlet/ext/draco/spring/',
    '/html/portlet/ext/draco/api/',
    '/html/portlet/ext/draco/service/',
    '/html/portlet/ext/draco/json/',
    '/html/portlet/ext/draco/ajax/',
    '/draco/',
    '/draco/api/',
    '/draco/testcase/list',
    '/draco/project/list',
    '/draco/plan/list',
    '/c/portal/json',
    '/api/jsonws/invoke',
    '/html/portlet/ext/draco/dwr/',
    '/dwr/',
    '/dwr/call/',
]
for path in api_paths:
    try:
        r = s.get(f'http://172.18.36.5:8000{path}', timeout=5)
        info = f"Status: {r.status_code}"
        if r.status_code == 200 and len(r.text) < 500:
            info += f" Body: {r.text[:300]}"
        elif r.status_code == 200:
            info += f" Length: {len(r.text)}"
        print(f"  {path} -> {info}")
    except Exception as e:
        print(f"  {path} -> Error: {e}")

# 4. 尝试 Liferay JSON WS
print("\n=== 4. Liferay JSON WS ===")
try:
    r = s.get('http://172.18.36.5:8000/api/jsonws/', timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        try:
            data = r.json()
            print(f"Context keys: {list(data.keys())[:15]}")
        except:
            print(f"Body[:500]: {r.text[:500]}")
    elif r.status_code == 401:
        print("需要认证 - 尝试基本认证...")
        r = s.get('http://172.18.36.5:8000/api/jsonws/', auth=('zhaokw', '123qwer'), timeout=10)
        print(f"Auth status: {r.status_code}")
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"Context keys: {list(data.keys())[:15]}")
            except:
                print(f"Body[:500]: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# 5. 查看主 Topo SWF 中的可读字符串
print("\n=== 5. 分析 SWF 文件 ===")
try:
    r = s.get('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', timeout=30)
    print(f"SWF status: {r.status_code}, size: {len(r.content)} bytes")
    # 搜索 SWF 中的可读字符串
    content = r.content
    # 提取所有可读字符串（ASCII 字符长度>=4）
    strings = re.findall(rb'[\x20-\x7e]{4,}', content)
    # 过滤出 URL 路径和 API 端点
    url_strings = [s.decode('ascii', errors='ignore') for s in strings if b'http' in s or b'/' in s and (b'.do' in s or b'.action' in s or b'.json' in s or b'api' in s or b'list' in s)]
    print(f"URL-like strings in SWF ({len(url_strings)} found):")
    for u in url_strings[:30]:
        print(f"  {u}")
except Exception as e:
    print(f"SWF download error: {e}")
