"""深度探查 TOPO 系统 - 登录 + Topo页面分析"""
import requests
import re
import json

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

# 1. 获取根页面，完整分析
print("=== 1. 分析登录表单 ===")
r = s.get('http://172.18.36.5:8000/', timeout=10)

# 找完整 form 标签
form_match = re.search(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>(.*?)</form>', r.text, re.I | re.S)
if form_match:
    action = form_match.group(1)
    form_html = form_match.group(2)
    print(f"Form action: {action}")
    # 所有 input
    inputs = re.findall(r'<input[^>]*>', form_html, re.I)
    for inp in inputs:
        name = re.search(r'name=["\']([^"\']*)["\']', inp, re.I)
        value = re.search(r'value=["\']([^"\']*)["\']', inp, re.I)
        itype = re.search(r'type=["\']([^"\']*)["\']', inp, re.I)
        print(f"  Input: name={name.group(1) if name else '?'}, value={value.group(1)[:30] if value else '?'}, type={itype.group(1) if itype else '?'}")

# 2. 使用正确的 action 登录
print("\n=== 2. 登录 ===")
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
login_data = {
    '_58_redirect': '',
    '_58_rememberMe': 'false',
    '_58_login': 'zhaokw',
    '_58_password': '123qwer',
}
r2 = s.post(login_url, data=login_data, timeout=15, allow_redirects=True)
print(f"Login response status: {r2.status_code}")
print(f"Final URL: {r2.url}")
print(f"Cookies after login: {dict(s.cookies)}")

# 检查是否登录成功
is_logged_in = 'sign-out' in r2.text.lower() or 'logout' in r2.text.lower() or '登出' in r2.text or 'my-account' in r2.text.lower()
print(f"Logged in: {is_logged_in}")

# 如果未登录，尝试 Liferay 6 标准登录
if not is_logged_in:
    print("\n=== 2b. 尝试另一种登录方式 ===")
    r2b = s.post('http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1',
        data={
            '_58_redirect': '',
            '_58_rememberMe': 'false',
            '_58_login': 'zhaokw',
            '_58_password': '123qwer',
            '_58_struts_action': '/login/login',
        }, timeout=15, allow_redirects=True)
    print(f"Status: {r2b.status_code}, URL: {r2b.url}")
    is_logged_in2 = 'sign-out' in r2b.text.lower() or 'logout' in r2b.text.lower() or '登出' in r2b.text
    print(f"Logged in (attempt 2): {is_logged_in2}")
    if is_logged_in2:
        r2 = r2b

# 3. 访问 Topo 页面，完整分析
print("\n=== 3. Topo 页面深度分析 ===")
r3 = s.get('http://172.18.36.5:8000/html/client/topo/', timeout=10)
print(f"Topo page status: {r3.status_code}")
print(f"Body length: {len(r3.text)}")

# 查找所有 script src
scripts = re.findall(r'<script[^>]*src=["\']([^"\']*)["\']', r3.text, re.I)
print(f"Script srcs: {scripts}")

# 查找所有 link href
links_css = re.findall(r'<link[^>]*href=["\']([^"\']*)["\']', r3.text, re.I)
print(f"CSS/Link hrefs: {links_css}")

# 查找内联 JS 中的 URL 或 API 调用
js_urls = re.findall(r'["\']([^"\']*(?:api|ajax|json|data|list|get|load)[^"\']*)["\']', r3.text, re.I)
print(f"JS URLs (filtered): {js_urls[:20]}")

# 查找 AJAX 调用
ajax_patterns = re.findall(r'\.(?:ajax|get|post|getJSON)\s*\(\s*["\']([^"\']*)["\']', r3.text, re.I)
print(f"AJAX calls: {ajax_patterns[:20]}")

# 查找 iframe 和 frame
frames = re.findall(r'<(?:i)frame[^>]*src=["\']([^"\']*)["\']', r3.text, re.I)
print(f"Frames: {frames}")

# 打印 Topo 页面 body 的前 5000 字符（看JS逻辑）
print("\n=== Topo 页面前 5000 字符 ===")
print(r3.text[:5000])
