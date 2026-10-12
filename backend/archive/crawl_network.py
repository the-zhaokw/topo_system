"""通过 Playwright 加载页面并捕获所有网络请求，发现实际 API 端点"""
from playwright.sync_api import sync_playwright
import json
import time

captured_requests = []

def on_request(request):
    url = request.url
    method = request.method
    post_data = request.post_data
    headers = dict(request.headers)

    # 过滤掉静态资源
    skip_ext = ('.swf', '.css', '.png', '.jpg', '.gif', '.ico', '.woff', '.ttf', '.js', '.svg')
    if any(url.lower().endswith(ext) for ext in skip_ext):
        return

    entry = {
        'method': method,
        'url': url,
        'post_data': post_data[:500] if post_data else None,
        'content_type': headers.get('content-type', ''),
    }
    captured_requests.append(entry)
    print(f"[REQ] {method} {url}")
    if post_data:
        print(f"      POST: {post_data[:200]}")

def on_response(response):
    url = response.url
    status = response.status
    ct = response.headers.get('content-type', '')

    skip_ext = ('.swf', '.css', '.png', '.jpg', '.gif', '.ico', '.woff', '.ttf', '.js', '.svg')
    if any(url.lower().endswith(ext) for ext in skip_ext):
        return

    print(f"[RES] {status} {url} ({ct[:50]})")

    # 如果是 AMF 或 JSON 响应，尝试读取
    if 'amf' in ct.lower() or 'json' in ct.lower() or 'xml' in ct.lower() or 'text' in ct.lower():
        try:
            body = response.body()
            if len(body) < 50000:
                # 尝试解码
                try:
                    text = body.decode('utf-8', errors='replace')[:500]
                    print(f"      Body: {text}")
                except:
                    print(f"      Body: <binary {len(body)} bytes>")
        except:
            pass

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()

    page.on('request', on_request)
    page.on('response', on_response)

    print("=== 1. 访问主页面 ===")
    try:
        page.goto('http://172.18.36.5:8000/html/client/topo/', timeout=30000)
    except Exception as e:
        print(f"导航错误: {e}")

    time.sleep(3)

    print("\n=== 2. 页面内容 ===")
    try:
        content = page.content()
        # 找到所有 script 和 object/embed 标签
        import re
        scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', content)
        embeds = re.findall(r'<(embed|object|param)[^>]*(?:src|data|value|name)=["\']([^"\']+)["\']', content, re.I)
        links = re.findall(r'<link[^>]*href=["\']([^"\']+)["\']', content)

        print(f"Scripts: {scripts}")
        print(f"Embeds/Objects: {embeds}")
        print(f"Links: {links}")

        # 找 AMF/messagebroker 相关
        amf_refs = re.findall(r'["\']([^"\']*(?:amf|messagebroker|blaze)[^"\']*)["\']', content, re.I)
        print(f"AMF refs: {amf_refs}")

        # 打印完整内容前 2000 字符
        print(f"\n页面内容 (前2000字符):")
        print(content[:2000])
    except Exception as e:
        print(f"读取页面错误: {e}")

    print("\n=== 3. 尝试登录 ===")
    try:
        page.goto('http://172.18.36.5:8000/', timeout=30000)
        time.sleep(2)

        # 查找登录表单
        inputs = page.locator('input').all()
        print(f"找到 {len(inputs)} 个 input")
        for i, inp in enumerate(inputs):
            name = inp.get_attribute('name') or ''
            type_ = inp.get_attribute('type') or ''
            placeholder = inp.get_attribute('placeholder') or ''
            print(f"  input[{i}]: name={name}, type={type_}, placeholder={placeholder}")

        # 填写登录信息
        login_input = page.locator('input[name*="login"], input[name*="user"], input[name*="email"]').first
        pass_input = page.locator('input[type="password"]').first

        if login_input.count() > 0 and pass_input.count() > 0:
            login_input.fill('zhaokw')
            pass_input.fill('`123qwer')
            print("已填写登录信息")

            # 查找提交按钮
            submit = page.locator('button[type="submit"], input[type="submit"], button:has-text("登录"), button:has-text("Sign")').first
            if submit.count() > 0:
                submit.click()
                print("已点击登录按钮")
            else:
                page.keyboard.press('Enter')

            time.sleep(5)
            print(f"登录后 URL: {page.url}")
    except Exception as e:
        print(f"登录错误: {e}")

    print("\n=== 4. 登录后访问 topo 页面 ===")
    try:
        page.goto('http://172.18.36.5:8000/html/client/topo/', timeout=30000)
        time.sleep(5)
        print(f"Topo 页面 URL: {page.url}")

        # 捕获页面中的 AMF 配置
        content = page.content()
        print(f"页面内容长度: {len(content)}")
        print(f"页面内容前3000字符:")
        print(content[:3000])
    except Exception as e:
        print(f"访问 topo 错误: {e}")

    print("\n=== 5. 尝试直接访问常见 AMF 端点 ===")
    amf_endpoints = [
        'http://172.18.36.5:8000/messagebroker/amf',
        'http://172.18.36.5:8000/blazeds/messagebroker/amf',
        'http://172.18.36.5:8000/html/client/topo/messagebroker/amf',
        'http://172.18.36.5:8000/amf',
        'http://172.18.36.5:8000/messagebroker/amfpolling',
        'http://172.18.36.5:8000/lcds/messagebroker/amf',
        'http://172.18.36.5:8000/flex2/messagebroker/amf',
        'http://172.18.36.5:8000/html/messagebroker/amf',
    ]
    for url in amf_endpoints:
        try:
            resp = page.request.get(url, timeout=5000)
            print(f"  {url}: {resp.status} ({resp.headers.get('content-type', '')})")
        except:
            print(f"  {url}: 超时或错误")

    print("\n=== 6. 捕获到的所有请求 ===")
    for req in captured_requests:
        print(json.dumps(req, ensure_ascii=False))

    # 保存截图
    page.screenshot(path='d:/topo_system/backend/topo_page.png', full_page=True)
    print("\n截图已保存到 topo_page.png")

    browser.close()

print("\n=== 完成 ===")
print(f"共捕获 {len(captured_requests)} 个请求")
