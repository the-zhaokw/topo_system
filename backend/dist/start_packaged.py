#!/usr/bin/env python3
"""
TOPO System 打包版本启动脚本
用于PyInstaller打包后的可执行文件
"""
import os
import sys
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import importlib.util

def get_app_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_pyinstaller_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return get_app_path()

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def start_backend(port):
    app_path = get_app_path()
    pyinstaller_path = get_pyinstaller_path()

    api_path = os.path.join(pyinstaller_path, 'api')
    models_path = os.path.join(pyinstaller_path, 'models')
    services_path = os.path.join(pyinstaller_path, 'services')

    if api_path not in sys.path:
        sys.path.insert(0, api_path)
    if models_path not in sys.path:
        sys.path.insert(0, models_path)
    if services_path not in sys.path:
        sys.path.insert(0, services_path)

    os.chdir(app_path)

    try:
        from enhanced_app import app, db, init_db
        from restful_api import api_bp
        from websocket_notifications import init_socketio

        def register_api_blueprints():
            app.register_blueprint(api_bp, url_prefix='/api')

        init_extensions = getattr(__import__('enhanced_app', fromlist=['init_extensions']), 'init_extensions')

        init_extensions(app)
        register_api_blueprints()

        with app.app_context():
            init_db()

        socketio = init_socketio(app)
        socketio.run(app, debug=False, host='127.0.0.1', port=port, use_reloader=False)
    except Exception as e:
        print(f"[错误] 后端启动失败: {e}")
        import traceback
        traceback.print_exc()
        raise

def start_frontend(port):
    app_path = get_app_path()
    pyinstaller_path = get_pyinstaller_path()
    frontend_path = os.path.join(pyinstaller_path, 'frontend')

    if not os.path.exists(frontend_path):
        print(f"[警告] 前端文件未找到: {frontend_path}")
        frontend_path = os.path.join(app_path, 'frontend')
        if not os.path.exists(frontend_path):
            print(f"[错误] 前端文件完全缺失")
            return

    os.chdir(frontend_path)

    class CustomHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=frontend_path, **kwargs)

        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            super().end_headers()

        def do_OPTIONS(self):
            self.send_response(200)
            self.end_headers()

    httpd = HTTPServer(('127.0.0.1', port), CustomHandler)
    print(f"[INFO] 前端服务启动: http://127.0.0.1:{port}")
    httpd.serve_forever()

def main():
    print("=" * 50)
    print("   TOPO System 启动中...")
    print("=" * 50)
    print()

    app_path = get_app_path()
    pyinstaller_path = get_pyinstaller_path()

    instance_path = os.path.join(app_path, 'instance')
    db_path = os.path.join(instance_path, 'topo_system.db')

    os.makedirs(instance_path, exist_ok=True)
    os.makedirs(os.path.join(app_path, 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(app_path, 'logs'), exist_ok=True)
    os.makedirs(os.path.join(app_path, 'backups'), exist_ok=True)

    init_script_path = os.path.join(pyinstaller_path, 'init_on_install.py')
    if not os.path.exists(db_path):
        print("[INFO] 首次运行，正在初始化数据库...")
        if os.path.exists(init_script_path):
            spec = importlib.util.spec_from_file_location("init_on_install", init_script_path)
            init_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(init_module)
            init_module.init_database()
        else:
            print(f"[警告] 初始化脚本未找到: {init_script_path}")
        print()

    backend_port = find_free_port()
    frontend_port = find_free_port()

    print(f"[INFO] 后端服务端口: {backend_port}")
    print(f"[INFO] 前端服务端口: {frontend_port}")
    print()

    backend_thread = threading.Thread(target=start_backend, args=(backend_port,), daemon=True)
    backend_thread.start()

    import time
    time.sleep(3)

    frontend_thread = threading.Thread(target=start_frontend, args=(frontend_port,), daemon=True)
    frontend_thread.start()

    time.sleep(1)

    url = f"http://127.0.0.1:{frontend_port}"
    print(f"[INFO] 浏览器将打开: {url}")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 50)

    try:
        webbrowser.open(url)
    except:
        pass

    try:
        frontend_thread.join()
    except KeyboardInterrupt:
        print("\n[INFO] 正在停止服务...")
        sys.exit(0)

if __name__ == '__main__':
    main()
