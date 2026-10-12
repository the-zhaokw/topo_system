#!/usr/bin/env python
"""TOPO 系统后端服务管理脚本

用法:
    python start_backend.py          # 启动后端服务（端口 5000）
    python start_backend.py stop     # 停止占用 5000 端口的后端进程
"""
import os
import signal
import sys


def start_backend(port=5000):
    """启动 Flask 后端服务"""
    # 添加backend目录到Python路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

    # 导入enhanced_app模块
    import enhanced_app

    # 注册API蓝图
    enhanced_app.register_api_blueprints()

    # 初始化扩展和数据库
    enhanced_app.init_extensions(enhanced_app.app)
    enhanced_app.init_db()

    # 启动应用
    print(f"Starting backend server on http://localhost:{port}")
    enhanced_app.app.run(debug=True, host='0.0.0.0', port=port)


def stop_backend(port=5000):
    """终止所有监听指定端口的进程"""
    import psutil

    # psutil 6.x 用 net_connections()，5.x 用 connections()
    get_conns = getattr(psutil.Process, 'net_connections', None)

    print(f"正在查找监听端口 {port} 的进程...")
    found = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            conns = proc.net_connections() if get_conns else proc.connections()
            for conn in conns:
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    found = True
                    print(f"进程 {proc.pid}: {' '.join(proc.info['cmdline'])}")
                    try:
                        os.kill(proc.pid, signal.SIGTERM)
                        print(f"已终止 PID {proc.pid}")
                    except Exception:
                        try:
                            os.kill(proc.pid, signal.SIGKILL)
                            print(f"已强制终止 PID {proc.pid}")
                        except Exception:
                            print(f"无法终止 PID {proc.pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not found:
        print(f"未发现监听端口 {port} 的进程")
    print("完成")


if __name__ == '__main__':
    action = sys.argv[1].lower() if len(sys.argv) > 1 else 'start'

    if action == 'start':
        start_backend()
    elif action == 'stop':
        stop_backend()
    else:
        print(__doc__)
        sys.exit(1)
