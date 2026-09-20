import requests, glob, os

# 扫描全部 views 和 components
paths = glob.glob(r'd:\topo_system\vue-frontend\src\views\**\*.vue', recursive=True)
paths += glob.glob(r'd:\topo_system\vue-frontend\src\components\**\*.vue', recursive=True)

failed = []
for p in paths:
    rel = os.path.relpath(p, r'd:\topo_system\vue-frontend').replace('\\', '/')
    url = f'http://localhost:3000/src/{rel.replace("src/", "", 1)}'
    # rel 已经是 src/... 形式
    url = f'http://localhost:3000/{rel}'
    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            failed.append((rel, r.status_code))
    except Exception as e:
        failed.append((rel, f'ERR {e}'))

print(f'共扫描 {len(paths)} 个 .vue 文件')
if failed:
    print(f'\n失败 {len(failed)} 个:')
    for f, s in failed:
        print(f'  {s}  {f}')
else:
    print('全部 200 OK')
