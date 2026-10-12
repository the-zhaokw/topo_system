"""探查 TOPO 系统结构和 API"""
import requests
import re
import json

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

# 1. 获取根页面，分析登录表单
print("=== 1. 根页面分析 ===")
r = s.get('http://172.18.36.5:8000/', timeout=10)
print(f"Status: {r.status_code}")

# 查找表单
forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>', r.text, re.I)
print(f"Forms: {forms}")

# 查找隐藏字段
hidden = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']*)["\'][^>]*value=["\']([^"\']*)["\']', r.text, re.I)
print(f"Hidden fields: {hidden}")

# 查找所有 input
inputs = re.findall(r'<input[^>]*name=["\']([^"\']*)["\'][^>]*>', r.text, re.I)
print(f"All inputs: {inputs}")

# 2. 尝试 Liferay 标准登录
print("\n=== 2. 尝试登录 ===")
login_data = {}
for name, value in hidden:
    login_data[name] = value
login_data['_58_login'] = 'zhaokw'
login_data['_58_password'] = '123qwer'
login_data['_58_redirect'] = ''
login_data['_58_rememberMe'] = 'false'

r2 = s.post('http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_resource_id=&p_p_lifecycle=1&saveLastPath=false', data=login_data, timeout=15, allow_redirects=True)
print(f"Login status: {r2.status_code}")
print(f"Final URL: {r2.url}")
print(f"Cookies: {dict(s.cookies)}")
# 检查是否登录成功
if '登出' in r2.text or 'logout' in r2.text.lower() or 'sign-out' in r2.text.lower():
    print("登录成功！")
else:
    print("登录可能失败，检查页面内容...")
    # 查找错误信息
    errors = re.findall(r'class=["\']error["\'][^>]*>(.*?)<', r2.text, re.I | re.S)
    print(f"Error messages: {errors[:3]}")

# 3. 登录后访问 topo 页面
print("\n=== 3. 访问 Topo 页面 ===")
r3 = s.get('http://172.18.36.5:8000/html/client/topo/', timeout=10)
print(f"Topo page status: {r3.status_code}")
print(f"Topo page URL: {r3.url}")
print(f"Body length: {len(r3.text)}")
# 查找 iframe
iframes = re.findall(r'<iframe[^>]*src=["\']([^"\']*)["\']', r3.text, re.I)
print(f"Iframes: {iframes}")

# 4. 尝试常见 API 端点
print("\n=== 4. 探测 API 端点 ===")
api_paths = [
    '/api/jsonws/',
    '/html/client/topo/api/',
    '/topo/api/',
    '/api/topo/',
    '/html/client/topo/getData',
    '/topo/testcase/list',
    '/topo/project/list',
]
for path in api_paths:
    try:
        r4 = s.get(f'http://172.18.36.5:8000{path}', timeout=5)
        print(f"  {path} -> {r4.status_code} (len={len(r4.text)})")
    except Exception as e:
        print(f"  {path} -> Error: {e}")

# 5. 检查 Liferay JSON WS API
print("\n=== 5. Liferay JSON WS ===")
try:
    r5 = s.get('http://172.18.36.5:8000/api/jsonws/', timeout=10)
    print(f"JSON WS status: {r5.status_code}")
    if r5.status_code == 200:
        try:
            data = r5.json()
            print(f"Available contexts: {list(data.keys())[:10]}")
        except:
            print(f"Body[:500]: {r5.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
