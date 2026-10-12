"""Verify comments are returned in desc order."""
import json
import time
import urllib.request

LOGIN = "http://127.0.0.1:5000/api/auth/login"
BASE = "http://127.0.0.1:5000/api/rd-kanban"

# Login
req = urllib.request.Request(LOGIN, data=json.dumps({"username": "admin", "password": "admin123"}).encode(), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as r:
    token = json.loads(r.read().decode())["data"]["access_token"]
H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def call(method, path, body=None):
    if isinstance(body, (dict, list)):
        data = json.dumps(body).encode("utf-8")
    else:
        data = body
    req = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read().decode())

# Get a card
s, r = call("GET", "/2")
item_id = r["items"][0]["id"]
print(f"Using item_id={item_id}")

# Add 3 comments with small delays
for i in range(3):
    s, r = call("POST", f"/{item_id}/comments", {"content": f"测试评论 #{i+1} - {time.strftime('%H:%M:%S')}"})
    time.sleep(0.5)

# List comments
s, r = call("GET", f"/{item_id}/comments")
comments = r.get("comments", [])
print(f"\nFound {len(comments)} comments:")
for i, c in enumerate(comments, 1):
    print(f"  {i}. [{c['created_at'][:19]}] {c['content'][:30]}")

# Check order: should be desc by created_at
times = [c["created_at"] for c in comments]
is_desc = all(times[i] >= times[i+1] for i in range(len(times)-1))
print(f"\n倒序排列正确: {is_desc}")

# Cleanup
print("\n清理测试评论...")
for c in comments:
    if c["content"].startswith("测试评论 #"):
        try:
            req = urllib.request.Request(BASE + f"/comments/{c['id']}", headers=H, method="DELETE")
            with urllib.request.urlopen(req) as r:
                pass
        except Exception as e:
            print(f"  删除 {c['id']} 失败: {e}")
print("DONE")
