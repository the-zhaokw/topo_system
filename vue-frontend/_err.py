import requests, re, json

r = requests.get('http://localhost:3000/src/views/WarehouseList.vue')
print('Status:', r.status_code)
t = r.text
m = re.search(r'new ErrorOverlay\((\{.*?\})\)\s*</script>', t, re.S)
if m:
    data = json.loads(m.group(1))
    print('Message:', data.get('message'))
    print('ID:', data.get('id'))
    stack = data.get('stack', '')
    print('Stack first 10 lines:')
    print('\n'.join(stack.splitlines()[:10]))
else:
    print(t[:2000])
