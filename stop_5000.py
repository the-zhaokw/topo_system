import psutil
import os
import signal

# 获取所有监听 5000 端口的进程
print("正在查找监听端口 5000 的进程...")
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        for conn in proc.net_connections():
            if conn.laddr.port == 5000 and conn.status == 'LISTEN':
                print(f"进程 {proc.pid}: {' '.join(proc.info['cmdline'])}")
                try:
                    os.kill(proc.pid, signal.SIGTERM)
                    print(f"已终止 PID {proc.pid}")
                except:
                    try:
                        os.kill(proc.pid, signal.SIGKILL)
                        print(f"已强制终止 PID {proc.pid}")
                    except:
                        print(f"无法终止 PID {proc.pid}")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

print("完成")
