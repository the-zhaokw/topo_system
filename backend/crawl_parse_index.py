"""解析 index.jsp 找到 SWF 文件和参数"""
import requests as req
import re

session = req.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})
r = session.get('http://172.18.36.5:8000/', timeout=10)
login_url = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin'
session.post(login_url, data={
    '_58_redirect': '', '_58_rememberMe': 'false',
    '_58_login': 'zhaokw', '_58_password': '`123qwer',
}, timeout=15, allow_redirects=True)

r = session.get('http://172.18.36.5:8000/html/client/topo/index.jsp', timeout=15)
text = r.text

# 保存完整内容
with open('d:/topo_system/backend/topo_index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print(f"保存完整 index.jsp ({len(text)} bytes)")

# 搜索 swf 文件引用
swf_refs = re.findall(r'[\w/\.]+\.swf', text)
print('\nSWF 引用:')
for s in sorted(set(swf_refs)):
    print(f'  {s}')

# 搜索 FlashVars
fv_match = re.findall(r'[Ff]lash[Vv]ars["\']?\s*[=:]\s*["\']([^"\']*)', text)
print(f'\nFlashVars ({len(fv_match)}):')
for fv in fv_match:
    print(f'  {fv[:500]}')

# 搜索 AC_FL_RunContent 调用
ac_match = re.findall(r'AC_FL_RunContent\([^)]*', text, re.DOTALL)
print(f'\nAC_FL_RunContent ({len(ac_match)}):')
for ac in ac_match:
    print(f'  {ac[:500]}')

# 搜索 embed/object 标签
embed_match = re.findall(r'<(?:embed|object|param)[^>]*>', text, re.IGNORECASE)
print(f'\nHTML embed/object ({len(embed_match)}):')
for e in embed_match:
    print(f'  {e[:300]}')

# 搜索变量赋值
var_match = re.findall(r'(?:var|let|const)\s+\w+\s*=\s*["\'](.*?)["\']', text)
print(f'\n变量 ({len(var_match)}):')
for v in var_match:
    if len(v) > 3:
        print(f'  {v[:200]}')

# 搜索 script 块
script_matches = re.findall(r'<script[^>]*>(.*?)</script>', text, re.DOTALL)
print(f'\nScript 块数: {len(script_matches)}')
if len(script_matches) > 1:
    last_script = script_matches[-1]
    print(f'\n最后 Script 块 ({len(last_script)} chars):')
    print(last_script[:5000])

# 也获取 /user/zhaokw 页面
print("\n\n=== 获取 /user/zhaokw 页面 ===")
r2 = session.get('http://172.18.36.5:8000/user/zhaokw', timeout=15)
text2 = r2.text
print(f"页面大小: {len(text2)} bytes")

# 搜索 bug 相关内容
bug_lines = [line.strip() for line in text2.split('\n') if 'bug' in line.lower() and len(line.strip()) > 10]
print(f"包含 'bug' 的行 ({len(bug_lines)}):")
for line in bug_lines[:20]:
    print(f"  {line[:200]}")

# 搜索 portlet 配置
portlet_lines = [line.strip() for line in text2.split('\n') if 'portlet' in line.lower() and len(line.strip()) > 10]
print(f"\n包含 'portlet' 的行 ({len(portlet_lines)}):")
for line in portlet_lines[:10]:
    print(f"  {line[:200]}")
