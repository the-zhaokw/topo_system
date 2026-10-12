"""用 Playwright 打开 TOPO 系统，捕获网络请求并尝试登录"""
import json
from playwright.sync_api import sync_playwright

api_calls = []

def on_request(request):
    url = request.url
    # 过滤掉静态资源，只记录 API 调用
    if any(ext in url for ext in ['.css', '.js', '.gif', '.png', '.jpg', '.ico', '.swf']):
        return
    api_calls.append({
        'method': request.method,
        'url': url,
        'headers': dict(request.headers),
        'post_data': request.post_data
    })

def on_response(response):
    url = response.url
    if any(ext in url for ext in ['.css', '.js', '.gif', '.png', '.jpg', '.ico', '.swf']):
        return
    # 记录响应
    try:
        body = response.text()[:500]
    except:
        body = '<binary>'
    print(f"[RESPONSE] {response.status} {url[:120]}")
    if response.status in [200, 302] and ('json' in response.headers.get('content-type', '') or 'xml' in response.headers.get('content-type', '')):
        print(f"  Body: {body[:300]}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 监听网络请求
    page.on('request', on_request)
    page.on('response', on_response)

    # 1. 打开登录页面
    print("=== 1. 打开登录页面 ===")
    page.goto('http://172.18.36.5:8000/', wait_until='networkidle', timeout=30000)
    page.screenshot(path='d:/topo_system/backend/screenshot_login.png', full_page=True)
    print(f"Page title: {page.title()}")

    # 查看表单
    forms = page.query_selector_all('form')
    for form in forms:
        action = form.get_attribute('action')
        method = form.get_attribute('method')
        inputs = form.query_selector_all('input')
        print(f"Form: action={action}, method={method}")
        for inp in inputs:
            name = inp.get_attribute('name')
            itype = inp.get_attribute('type')
            value = inp.get_attribute('value')
            print(f"  input: name={name}, type={itype}, value={value}")

    # 2. 填写登录表单
    print("\n=== 2. 填写并提交登录表单 ===")
    try:
        # 找到登录输入框
        login_input = page.locator('input[name="_58_login"]')
        password_input = page.locator('input[name="_58_password"]')

        login_input.fill('zhaokw')
        password_input.fill('123qwer')
        print("已填写用户名和密码")

        # 截图
        page.screenshot(path='d:/topo_system/backend/screenshot_login_filled.png', full_page=True)

        # 提交表单
        page.click('input[type="submit"]')
        page.wait_for_load_state('networkidle', timeout=15000)

        print(f"登录后 URL: {page.url}")
        print(f"登录后 title: {page.title()}")
        page.screenshot(path='d:/topo_system/backend/screenshot_after_login.png', full_page=True)

        # 检查是否登录成功
        content = page.content()
        if 'sign-out' in content.lower() or '登出' in content:
            print("✅ 登录成功！")
        else:
            # 查找错误信息
            errors = page.query_selector_all('.portlet-msg-error')
            for err in errors:
                print(f"❌ 错误: {err.inner_text()}")

    except Exception as e:
        print(f"登录异常: {e}")

    # 3. 即使登录失败，也访问 Topo 页面看看
    print("\n=== 3. 访问 Topo 页面 ===")
    page.goto('http://172.18.36.5:8000/html/client/topo/', wait_until='networkidle', timeout=30000)
    page.screenshot(path='d:/topo_system/backend/screenshot_topo.png', full_page=True)
    print(f"Topo page title: {page.title()}")

    # 4. 打印所有捕获的 API 调用
    print(f"\n=== 4. 捕获的 API 调用 ({len(api_calls)} 个) ===")
    for call in api_calls:
        print(f"  [{call['method']}] {call['url'][:150]}")
        if call['post_data']:
            print(f"    POST data: {call['post_data'][:200]}")

    # 5. 尝试不同的密码变体
    print("\n=== 5. 尝试密码变体 ===")
    passwords = ['123qwer', '`123qwer', '123qwer`', '`123qwer`']
    for pwd in passwords:
        page2 = browser.new_page()
        page2.goto('http://172.18.36.5:8000/', wait_until='networkidle', timeout=15000)
        try:
            page2.locator('input[name="_58_login"]').fill('zhaokw')
            page2.locator('input[name="_58_password"]').fill(pwd)
            page2.click('input[type="submit"]')
            page2.wait_for_load_state('networkidle', timeout=10000)
            content = page2.content()
            if 'sign-out' in content.lower() or '登出' in content:
                print(f"  ✅ 密码 '{pwd}' 登录成功！")
                page2.screenshot(path=f'd:/topo_system/backend/screenshot_login_{pwd.replace("`","bt")}_success.png')
                break
            else:
                errors = page2.query_selector_all('.portlet-msg-error')
                err_texts = [e.inner_text() for e in errors]
                print(f"  ❌ 密码 '{pwd}' 失败: {err_texts[:2]}")
        except Exception as e:
            print(f"  ❌ 密码 '{pwd}' 异常: {e}")
        page2.close()

    browser.close()

print("\n完成！")
