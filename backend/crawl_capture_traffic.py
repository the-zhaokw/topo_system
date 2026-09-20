"""使用 Playwright 捕获目标网站的 AMF 流量和页面结构"""
from playwright.sync_api import sync_playwright
import json
import time
import struct

AMF_URL = 'http://172.18.36.5:8000/messagebroker/amf'
BASE_URL = 'http://172.18.36.5:8000/'

captured_requests = []
captured_amf = []

def decode_amf0_response(data):
    """简单解码 AMF0 响应"""
    result = {}
    try:
        if len(data) < 6:
            return {"error": "too short", "raw": data[:100].hex()}
        version = struct.unpack('>H', data[0:2])[0]
        headers_count = struct.unpack('>H', data[2:4])[0]
        bodies_count = struct.unpack('>H', data[4:6])[0]
        result['version'] = version
        result['headers_count'] = headers_count
        result['bodies_count'] = bodies_count

        # 跳过 headers
        pos = 6
        for _ in range(headers_count):
            # header name
            if pos + 2 > len(data):
                break
            name_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2 + name_len
            # required flag (bool)
            if pos < len(data):
                pos += 1
            # value type
            if pos < len(data):
                val_type = data[pos]
                pos += 1
                # 简单跳过值
                if val_type == 0x02:  # string
                    if pos + 2 <= len(data):
                        slen = struct.unpack('>H', data[pos:pos+2])[0]
                        pos += 2 + slen
                elif val_type == 0x00:  # number
                    pos += 8
                elif val_type == 0x05:  # null
                    pass

        # 解析 bodies
        bodies = []
        for _ in range(bodies_count):
            if pos + 2 > len(data):
                break
            target_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            target_uri = data[pos:pos+target_len].decode('utf-8', errors='replace')
            pos += target_len

            if pos + 2 > len(data):
                break
            response_len = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2
            pos += response_len  # response URI (usually empty)

            if pos + 4 > len(data):
                break
            body_len = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            body_data = data[pos:pos+body_len]
            pos += body_len

            body_info = {
                'target_uri': target_uri,
                'body_length': body_len,
                'body_hex_preview': body_data[:200].hex() if body_data else '',
            }

            # 尝试提取字符串
            all_strs = []
            i = 0
            while i < len(body_data):
                # AMF0 string marker
                if body_data[i] == 0x02 and i + 2 < len(body_data):
                    slen = struct.unpack('>H', body_data[i+1:i+3])[0]
                    if i + 3 + slen <= len(body_data) and slen > 0:
                        s = body_data[i+3:i+3+slen].decode('utf-8', errors='replace')
                        if s.strip():
                            all_strs.append(s)
                        i += 3 + slen
                        continue
                # AMF3 string marker (0x06)
                elif body_data[i] == 0x06 and i + 1 < len(body_data):
                    # U29 length encoding
                    b = body_data[i+1]
                    if b & 0x80 == 0:
                        slen = (b >> 1) & 0x7F
                        if slen > 0 and i + 2 + slen <= len(body_data):
                            s = body_data[i+2:i+2+slen].decode('utf-8', errors='replace')
                            if s.strip():
                                all_strs.append(s)
                        i += 2 + slen
                        continue
                i += 1

            body_info['strings_found'] = all_strs[:50]
            bodies.append(body_info)

        result['bodies'] = bodies
    except Exception as e:
        result['error'] = str(e)
        result['raw_hex'] = data[:200].hex()

    return result


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        ignore_https_errors=True,
        extra_http_headers={'Accept-Language': 'zh-CN,zh;q=0.9'}
    )
    page = context.new_page()

    # 监听所有网络请求
    def on_request(request):
        url = request.url
        if 'messagebroker/amf' in url or 'amf' in url.lower():
            captured_amf.append({
                'url': url,
                'method': request.method,
                'headers': dict(request.headers),
                'post_data': request.post_data[:500] if request.post_data else None,
            })
            print(f"\n[AMF请求] {request.method} {url}")
            if request.post_data:
                print(f"  POST数据长度: {len(request.post_data)}")
                print(f"  POST数据HEX: {request.post_data[:100].hex()}")

    def on_response(response):
        url = response.url
        if 'messagebroker/amf' in url or 'amf' in url.lower():
            try:
                body = response.body()
                print(f"\n[AMF响应] {response.status} {url}")
                print(f"  响应长度: {len(body)} bytes")
                decoded = decode_amf0_response(body)
                print(f"  解码: {json.dumps(decoded, ensure_ascii=False, indent=2)[:2000]}")
                captured_amf.append({
                    'url': url,
                    'status': response.status,
                    'body_length': len(body),
                    'decoded': decoded,
                })
            except Exception as e:
                print(f"  [AMF响应读取失败] {e}")
        elif 'json' in response.headers.get('content-type', '').lower() or 'xml' in response.headers.get('content-type', '').lower():
            try:
                body = response.body()
                if len(body) < 50000:
                    text = body.decode('utf-8', errors='replace')
                    if any(kw in text.lower() for kw in ['bug', 'project', 'org', 'rtn', 'ipran']):
                        print(f"\n[JSON/XML响应] {response.status} {url}")
                        print(f"  内容: {text[:1000]}")
                        captured_requests.append({
                            'url': url,
                            'status': response.status,
                            'content': text[:5000],
                        })
            except:
                pass

    page.on('request', on_request)
    page.on('response', on_response)

    # 1. 先访问首页
    print("=== 1. 访问首页 ===")
    page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
    page.screenshot(path='d:/topo_system/backend/screenshot_home.png', full_page=True)
    print(f"首页标题: {page.title()}")
    print(f"首页URL: {page.url}")

    # 2. 登录
    print("\n=== 2. 登录 ===")
    page.goto('http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin',
              wait_until='networkidle', timeout=30000)

    # 使用 form 提交登录
    page.evaluate('''() => {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = 'http://172.18.36.5:8000/web/guest/home?p_p_id=58&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&saveLastPath=0&_58_struts_action=%2Flogin%2Flogin';
        form.innerHTML = `
            <input name="_58_redirect" value="">
            <input name="_58_rememberMe" value="false">
            <input name="_58_login" value="zhaokw">
            <input name="_58_password" value="`123qwer">
        `;
        document.body.appendChild(form);
        form.submit();
    }''')
    page.wait_for_load_state('networkidle', timeout=30000)
    print(f"登录后URL: {page.url}")
    page.screenshot(path='d:/topo_system/backend/screenshot_login.png', full_page=True)

    # 3. 访问 topo 客户端
    print("\n=== 3. 访问 topo 客户端 ===")
    page.goto('http://172.18.36.5:8000/html/client/topo/', wait_until='networkidle', timeout=30000)
    time.sleep(5)
    page.screenshot(path='d:/topo_system/backend/screenshot_topo.png', full_page=True)
    print(f"Topo页面标题: {page.title()}")
    print(f"Topo页面URL: {page.url}")

    # 获取页面内容
    content = page.content()
    print(f"页面内容长度: {len(content)}")
    # 搜索关键字
    for kw in ['RTN', 'IPRAN', 'bug', 'Bug', '缺陷', 'amf', 'messagebroker', 'flash', 'swf', 'embed', 'object']:
        count = content.lower().count(kw.lower())
        if count > 0:
            print(f"  关键字 '{kw}': 出现 {count} 次")

    # 列出页面上的所有 iframe
    frames = page.frames
    print(f"\nFrame 数量: {len(frames)}")
    for i, frame in enumerate(frames):
        print(f"  Frame {i}: URL={frame.url}, Name={frame.name}")

    # 4. 尝试访问一些可能的 API 端点
    print("\n=== 4. 探索 API 端点 ===")
    api_urls = [
        'http://172.18.36.5:8000/api/jsonws/',
        'http://172.18.36.5:8000/api/jsonws/invoke',
        'http://172.18.36.5:8000/c/portal/login',
        'http://172.18.36.5:8000/web/guest/home',
        'http://172.18.36.5:8000/group/guest/home',
        'http://172.18.36.5:8000/user/zhaokw/home',
        'http://172.18.36.5:8000/web/zhaokw/home',
    ]
    for url in api_urls:
        try:
            resp = page.goto(url, wait_until='domcontentloaded', timeout=10000)
            if resp:
                ct = resp.headers.get('content-type', '')
                print(f"  {url} => {resp.status} ({ct})")
        except:
            print(f"  {url} => 超时/错误")

    # 5. 等待并收集更多 AMF 流量
    print(f"\n=== 5. 等待 AMF 流量 ===")
    time.sleep(3)

    # 6. 尝试通过 JavaScript 发起 AMF 请求
    print("\n=== 6. 通过 JS 发起 AMF 请求 ===")
    # 构造一个简单的 AMF0 请求 (RemotingMessage)
    js_code = '''
    async function sendAmfRequest() {
        // 构造 AMF0 RemotingMessage 请求
        const target = "organizationService.getAll";

        // AMF0 编码
        function amf0String(s) {
            const encoder = new TextEncoder();
            const bytes = encoder.encode(s);
            const result = new Uint8Array(3 + bytes.length);
            result[0] = 0x02; // string marker
            result[1] = (bytes.length >> 8) & 0xFF;
            result[2] = bytes.length & 0xFF;
            result.set(bytes, 3);
            return result;
        }

        function amf0Number(n) {
            const result = new Uint8Array(9);
            result[0] = 0x00; // number marker
            const view = new DataView(result.buffer);
            view.setFloat64(1, n, false); // big-endian
            return result;
        }

        function amf0Null() {
            return new Uint8Array([0x05]);
        }

        function amf0Array(arr) {
            const parts = [new Uint8Array([0x0A])]; // strict array marker
            const lenBytes = new Uint8Array(4);
            const view = new DataView(lenBytes.buffer);
            view.setUint32(0, arr.length, false);
            parts.push(lenBytes);
            for (const item of arr) {
                parts.push(item);
            }
            // 合并
            let total = 0;
            for (const p of parts) total += p.length;
            const result = new Uint8Array(total);
            let offset = 0;
            for (const p of parts) {
                result.set(p, offset);
                offset += p.length;
            }
            return result;
        }

        function amf0Object(obj) {
            const parts = [new Uint8Array([0x03])]; // object marker
            for (const [key, val] of Object.entries(obj)) {
                const keyBytes = new TextEncoder().encode(key);
                const keyHeader = new Uint8Array(3);
                keyHeader[1] = (keyBytes.length >> 8) & 0xFF;
                keyHeader[2] = keyBytes.length & 0xFF;
                parts.push(keyHeader, keyBytes, val);
            }
            parts.push(new Uint8Array([0x00, 0x00, 0x09])); // end of object
            let total = 0;
            for (const p of parts) total += p.length;
            const result = new Uint8Array(total);
            let offset = 0;
            for (const p of parts) {
                result.set(p, offset);
                offset += p.length;
            }
            return result;
        }

        // 构造 RemotingMessage
        const emptyStr = amf0String("");
        const sourceStr = amf0String("organizationService");
        const operationStr = amf0String("getAll");

        const msgBody = amf0Array([
            amf0Object({
                "correlationId": emptyStr,
                "clientId": amf0Null(),
                "destination": sourceStr,
                "messageId": amf0String("msg_" + Date.now()),
                "operation": operationStr,
                "source": amf0Null(),
                "timeToLive": amf0Number(0),
                "timestamp": amf0Number(0),
                "body": amf0Array([])
            })
        ]);

        // 构造完整 AMF 包
        const header = new Uint8Array(6);
        const hView = new DataView(header.buffer);
        hView.setUint16(0, 0, false); // version
        hView.setUint16(2, 0, false); // headers count
        hView.setUint16(4, 1, false); // bodies count

        // target URI
        const targetBytes = new TextEncoder().encode("organizationService.getAll");
        const targetHeader = new Uint8Array(2);
        targetHeader[0] = (targetBytes.length >> 8) & 0xFF;
        targetHeader[1] = targetBytes.length & 0xFF;

        // response URI (empty)
        const respHeader = new Uint8Array(2);

        // body length
        const bodyLenBytes = new Uint8Array(4);
        const bView = new DataView(bodyLenBytes.buffer);
        bView.setUint32(0, msgBody.length, false);

        // 合并所有部分
        const allParts = [header, targetHeader, targetBytes, respHeader, bodyLenBytes, msgBody];
        let totalLen = 0;
        for (const p of allParts) totalLen += p.length;
        const packet = new Uint8Array(totalLen);
        let offset = 0;
        for (const part of allParts) {
            packet.set(part, offset);
            offset += part.length;
        }

        // 发送
        try {
            const resp = await fetch('http://172.18.36.5:8000/messagebroker/amf', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-amf'},
                body: packet
            });
            const buf = await resp.arrayBuffer();
            return {
                status: resp.status,
                length: buf.byteLength,
                hex: Array.from(new Uint8Array(buf).slice(0, 200)).map(b => b.toString(16).padStart(2, '0')).join('')
            };
        } catch(e) {
            return {error: e.message};
        }
    }
    sendAmfRequest().then(r => window.__amf_result = JSON.stringify(r));
    '''

    try:
        page.evaluate(js_code)
        time.sleep(3)
        result = page.evaluate('window.__amf_result')
        print(f"  JS AMF 结果: {result}")
    except Exception as e:
        print(f"  JS 执行失败: {e}")

    # 7. 打印捕获的 AMF 流量
    print(f"\n=== 7. 捕获的 AMF 请求/响应 ({len(captured_amf)}) ===")
    for i, item in enumerate(captured_amf):
        print(f"\n--- AMF #{i} ---")
        print(json.dumps(item, ensure_ascii=False, indent=2)[:1000])

    print(f"\n=== 捕获的 JSON/XML 请求 ({len(captured_requests)}) ===")
    for i, item in enumerate(captured_requests):
        print(f"\n--- Request #{i} ---")
        print(f"URL: {item['url']}")
        print(f"内容: {item['content'][:500]}")

    browser.close()
    print("\n=== 完成 ===")
