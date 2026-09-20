"""用密码 `123qwer 登录并访问 Topo，捕获所有网络请求"""
from playwright.sync_api import sync_playwright
import json

api_calls = []

def on_request(request):
    url = request.url
    if any(ext in url for ext in ['.css', '.js', '.gif', '.png', '.jpg', '.ico']):
        return
    api_calls.append({
        'method': request.method,
        'url': url,
        'post_data': request.post_data
    })
    print(f"[REQUEST] {request.method} {url[:150]}")

def on_response(response):
    url = response.url
    if any(ext in url for ext in ['.css', '.js', '.gif', '.png', '.jpg', '.ico']):
        return
    ct = response.headers.get('content-type', '')
    print(f"[RESPONSE] {response.status} {url[:120]} (type={ct[:30]})")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.on('request', on_request)
    page.on('response', on_response)

    # 1. 打开登录页面
    print("=== 1. 打开登录页面 ===")
    page.goto('http://172.18.36.5:8000/', wait_until='networkidle', timeout=30000)
    print(f"Title: {page.title()}, URL: {page.url}")

    # 2. 用 `123qwer 登录
    print("\n=== 2. 用 `123qwer 登录 ===")
    page.locator('input[name="_58_login"]').fill('zhaokw')
    page.locator('input[name="_58_password"]').fill('`123qwer')
    page.screenshot(path='d:/topo_system/backend/screenshot_login2_filled.png')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle', timeout=15000)
    page.screenshot(path='d:/topo_system/backend/screenshot_login2_after.png', full_page=True)
    print(f"登录后 URL: {page.url}")
    print(f"登录后 Title: {page.title()}")

    # 检查页面内容
    content = page.content()
    # 查找所有可能的登录成功/失败指标
    indicators = {
        'sign-out': 'sign-out' in content.lower(),
        '登出': '登出' in content,
        'logout': 'logout' in content.lower(),
        'my-account': 'my-account' in content.lower(),
        'isSignedIn_true': 'isSignedIn:function(){return true' in content or "isSignedIn:function(){return'true'" in content or "isSignedIn:function(){return\"true\"" in content,
        'isSignedIn_false': 'isSignedIn:function(){return false' in content,
        'error': 'portlet-msg-error' in content,
        'welcome_user': 'welcome' in content.lower(),
    }
    for k, v in indicators.items():
        print(f"  {k}: {v}")

    # 查找错误
    errors = page.query_selector_all('.portlet-msg-error')
    for err in errors:
        text = err.inner_text().strip()
        if text:
            print(f"  Error: {text}")

    # 3. 访问 Topo 页面
    print("\n=== 3. 访问 Topo 页面 ===")
    api_calls.clear()
    page.goto('http://172.18.36.5:8000/html/client/topo/', wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(3000)  # 等待 Flash 加载
    page.screenshot(path='d:/topo_system/backend/screenshot_topo2.png', full_page=True)
    print(f"Topo title: {page.title()}")
    print(f"Topo URL: {page.url}")

    # 获取页面内容中的所有 URL
    content = page.content()
    print(f"Topo page length: {len(content)}")

    # 检查页面是否有 Flash embed
    objects = page.query_selector_all('object, embed')
    for obj in objects:
        tag = obj.evaluate('el => el.tagName')
        src = obj.get_attribute('src') or obj.get_attribute('data') or ''
        movie = obj.get_attribute('movie') or ''
        print(f"  {tag}: src={src}, movie={movie}")
        # 查找 param 子元素
        params = obj.query_selector_all('param')
        for param in params:
            pname = param.get_attribute('name')
            pvalue = param.get_attribute('value')
            print(f"    param: {pname}={pvalue}")

    # 4. 捕获 Topo 页面的所有 API 调用
    print(f"\n=== 4. Topo 页面 API 调用 ({len(api_calls)} 个) ===")
    for call in api_calls:
        print(f"  [{call['method']}] {call['url'][:150]}")
        if call['post_data']:
            print(f"    POST: {call['post_data'][:200]}")

    # 5. 检查是否已登录状态下的页面不同
    print("\n=== 5. 检查 Liferay 主题状态 ===")
    theme_match = page.evaluate('''() => {
        const scripts = document.querySelectorAll('script');
        for (const s of scripts) {
            if (s.textContent.includes('isSignedIn')) {
                const m = s.textContent.match(/isSignedIn:function\\(\\)\\{return"?(true|false)"?\\}/);
                if (m) return m[1];
            }
        }
        return 'unknown';
    }''')
    print(f"isSignedIn: {theme_match}")

    # 6. 尝试访问 Liferay 用户页面
    print("\n=== 6. 访问用户页面 ===")
    user_urls = [
        '/web/guest/home',
        '/user/zhaokw',
        '/web/zhaokw',
        '/group/guest',
        '/c/portal/my-account',
        '/web/guest/home?p_p_id=2&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view',
    ]
    for u in user_urls:
        try:
            r = page.goto(f'http://172.18.36.5:8000{u}', wait_until='domcontentloaded', timeout=10000)
            print(f"  {u} -> {r.status} (final: {page.url[:100]})")
        except Exception as e:
            print(f"  {u} -> Error: {str(e)[:80]}")

    browser.close()

print("\n完成！")
