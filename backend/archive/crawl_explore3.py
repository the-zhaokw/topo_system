"""分析 Topo 页面完整内容 + 尝试正确登录"""
import requests
import re
import json

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

# 1. 获取根页面，分析完整登录表单
print("=== 1. 根页面完整分析 ===")
r = s.get('http://172.18.36.5:8000/', timeout=10)

# 查找所有 form 标签
all_forms = re.findall(r'<form[^>]*>.*?</form>', r.text, re.I | re.S)
for i, form in enumerate(all_forms):
    action = re.search(r'action=["\']([^"\']*)["\']', form, re.I)
    method = re.search(r'method=["\']([^"\']*)["\']', form, re.I)
    inputs = re.findall(r'<input[^>]*>', form, re.I)
    print(f"\nForm {i}: action={action.group(1) if action else '?'}, method={method.group(1) if method else '?'}")
    for inp in inputs:
        name = re.search(r'name=["\']([^"\']*)["\']', inp, re.I)
        value = re.search(r'value=["\']([^"\']*)["\']', inp, re.I)
        itype = re.search(r'type=["\']([^"\']*)["\']', inp, re.I)
        print(f"  input: name={name.group(1) if name else None}, type={itype.group(1) if itype else None}, value={value.group(1)[:50] if value else None}")

# 2. 完整登录
print("\n=== 2. 登录 ===")
# Liferay 6 登录URL
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
login_data = {
    '_58_redirect': '',
    '_58_rememberMe': 'false',
    '_58_login': 'zhaokw',
    '_58_password': '123qwer',
}
r2 = s.post(login_url, data=login_data, timeout=15, allow_redirects=True)
print(f"Status: {r2.status_code}")
print(f"URL: {r2.url}")
print(f"Cookies: {dict(s.cookies)}")

# 检查登录状态 - 看是否有用户名显示
user_check = re.findall(r'signed.?in|sign.?out|my.?account|welcome|user?.?name|currentuser', r2.text, re.I)
print(f"Login indicators: {user_check[:5]}")

# 查找 Liferay ThemeDisplay
theme = re.findall(r"isSignedIn:function\(\)\{return([^}]+)\}", r2.text, re.I)
print(f"ThemeDisplay isSignedIn: {theme}")

# 3. Topo 页面后半部分分析
print("\n=== 3. Topo 页面后 5000 字符 ===")
r3 = s.get('http://172.18.36.5:8000/html/client/topo/', timeout=10)
# 打印后半部分
mid = len(r3.text) // 2
print(r3.text[mid:mid+5000])

# 4. 查找 Flash embed 或 object 标签
print("\n=== 4. Flash/Object/Embed 分析 ===")
objects = re.findall(r'<object[^>]*>.*?</object>', r3.text, re.I | re.S)
embeds = re.findall(r'<embed[^>]*>', r3.text, re.I)
print(f"Object tags: {len(objects)}")
print(f"Embed tags: {len(embeds)}")
for obj in objects:
    # 查找 flashvars, data, src 等
    flashvars = re.search(r'flashvars=["\']([^"\']*)["\']', obj, re.I)
    data_attr = re.search(r'data=["\']([^"\']*)["\']', obj, re.I)
    params = re.findall(r'<param[^>]*name=["\']([^"\']*)["\'][^>]*value=["\']([^"\']*)["\']', obj, re.I)
    print(f"  Object: data={data_attr.group(1) if data_attr else '?'}, flashvars={flashvars.group(1) if flashvars else '?'}")
    for pname, pvalue in params:
        print(f"    param: {pname}={pvalue[:100]}")

for emb in embeds:
    src = re.search(r'src=["\']([^"\']*)["\']', emb, re.I)
    flashvars = re.search(r'flashvars=["\']([^"\']*)["\']', emb, re.I)
    print(f"  Embed: src={src.group(1) if src else '?'}, flashvars={flashvars.group(1) if flashvars else '?'}")

# 5. 查找所有 URL 模式
print("\n=== 5. 所有 URL 模式 ===")
urls = re.findall(r'(?:src|href|action|data|url)\s*=\s*["\']([^"\']+)["\']', r3.text, re.I)
for u in urls:
    if 'http' in u or u.startswith('/') or 'topo' in u.lower():
        print(f"  {u}")

# 6. 查找 JavaScript 变量中的 URL
print("\n=== 6. JS 变量中的 URL ===")
js_vars = re.findall(r'var\s+\w+\s*=\s*["\']([^"\']*(?:http|\.do|\.action|\.json|\.jsp)[^"\']*)["\']', r3.text, re.I)
for v in js_vars:
    print(f"  {v}")

# 查找 .do 或 .action 端点
do_urls = re.findall(r'["\']([^"\']*\.do[^"\']*)["\']', r3.text, re.I)
action_urls = re.findall(r'["\']([^"\']*\.action[^"\']*)["\']', r3.text, re.I)
print(f".do endpoints: {do_urls[:10]}")
print(f".action endpoints: {action_urls[:10]}")
