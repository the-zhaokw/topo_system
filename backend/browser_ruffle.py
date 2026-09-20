"""注入 Ruffle 模拟器运行 Flash 并捕获 AMF 流量"""
from playwright.sync_api import sync_playwright
import json
import time

amf_calls = []

def on_request(request):
    url = request.url
    if 'messagebroker' in url or 'transmitfile' in url or '/c/' in url or 'amf' in url.lower():
        amf_calls.append({
            'method': request.method,
            'url': url,
            'headers': dict(request.headers),
            'post_data': request.post_data[:500] if request.post_data else None
        })
        print(f"[AMF REQUEST] {request.method} {url[:120]}")
        if request.post_data:
            print(f"  POST data ({len(request.post_data)} bytes): {request.post_data[:200] if isinstance(request.post_data, str) else '<binary>'}")

def on_response(response):
    url = response.url
    if 'messagebroker' in url or 'transmitfile' in url or '/c/' in url or 'amf' in url.lower():
        ct = response.headers.get('content-type', '')
        print(f"[AMF RESPONSE] {response.status} {url[:120]} (type={ct})")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.on('request', on_request)
    page.on('response', on_response)

    # 注入 Ruffle 脚本 - 在页面加载前注入
    page.add_init_script('''
        // 加载 Ruffle Flash 模拟器
        var script = document.createElement('script');
        script.src = 'https://unpkg.com/@ruffle-rs/ruffle';
        document.head.appendChild(script);
        window.RufflePlayer = window.RufflePlayer || {};
        window.RufflePlayer.config = {
            "autoplay": "on",
            "uncaughtError": "on"
        };
    ''')

    # 1. 登录
    print("=== 1. 登录 ===")
    page.goto('http://172.18.36.5:8000/', wait_until='networkidle', timeout=30000)
    page.locator('input[name="_58_login"]').fill('zhaokw')
    page.locator('input[name="_58_password"]').fill('`123qwer')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle', timeout=15000)
    print(f"登录后 URL: {page.url}")

    # 2. 访问 Topo 页面（Ruffle 应该自动加载 Flash）
    print("\n=== 2. 访问 Topo 页面 ===")
    page.goto('http://172.18.36.5:8000/html/client/topo/', wait_until='networkidle', timeout=30000)
    # 等待 Ruffle 加载和初始化
    page.wait_for_timeout(5000)
    page.screenshot(path='d:/topo_system/backend/screenshot_ruffle.png', full_page=True)

    # 检查 Ruffle 是否加载成功
    ruffle_status = page.evaluate('''() => {
        return {
            ruffle_loaded: typeof window.Ruffle !== 'undefined',
            ruffle_player: typeof window.RufflePlayer !== 'undefined',
            flash_objects: document.querySelectorAll('object, embed').length,
            ruffle_elements: document.querySelectorAll('ruffle-player, ruffle-object, canvas').length,
            body_text: document.body.innerText.substring(0, 500)
        };
    }''')
    print(f"Ruffle 状态: {json.dumps(ruffle_status, indent=2, ensure_ascii=False)}")

    # 等待更多时间让 Flash 应用初始化并发送 AMF 请求
    print("\n等待 Flash 应用初始化...")
    page.wait_for_timeout(10000)
    page.screenshot(path='d:/topo_system/backend/screenshot_ruffle2.png', full_page=True)

    # 3. 检查是否有 AMF 请求
    print(f"\n=== 3. AMF 请求捕获 ({len(amf_calls)} 个) ===")
    for call in amf_calls:
        print(f"  [{call['method']}] {call['url'][:150]}")
        if call.get('post_data'):
            print(f"    POST: {call['post_data'][:200]}")

    # 4. 查看 Ruffle 控制台日志
    print("\n=== 4. 控制台日志 ===")
    logs = page.evaluate('''() => {
        // 检查是否有 ruffle-player 元素
        const players = document.querySelectorAll('ruffle-player');
        const objects = document.querySelectorAll('object');
        const embeds = document.querySelectorAll('embed');
        return {
            players: players.length,
            objects: objects.length,
            embeds: embeds.length,
            // 获取所有 iframe
            iframes: document.querySelectorAll('iframe').length,
            // 获取 body 内容
            bodyHTML: document.body.innerHTML.substring(0, 2000)
        };
    }''')
    print(f"DOM 状态: {json.dumps(logs, indent=2, ensure_ascii=False)[:2000]}")

    # 5. 尝试直接导航到 SWF 文件
    print("\n=== 5. 直接打开 SWF ===")
    page.goto('http://172.18.36.5:8000/html/portlet/ext/draco/resources/draco_manager.swf', wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(5000)
    page.screenshot(path='d:/topo_system/backend/screenshot_swf_direct.png', full_page=True)
    swf_status = page.evaluate('''() => {
        return {
            title: document.title,
            body_text: document.body.innerText.substring(0, 500),
            canvas: document.querySelectorAll('canvas').length,
            ruffle: document.querySelectorAll('ruffle-player').length,
        };
    }''')
    print(f"SWF 直接打开: {json.dumps(swf_status, indent=2, ensure_ascii=False)}")

    # 6. 最终 AMF 请求统计
    print(f"\n=== 6. 总 AMF 请求 ({len(amf_calls)}) ===")
    for call in amf_calls:
        print(f"  [{call['method']}] {call['url'][:150]}")

    browser.close()

print("\n完成！")
