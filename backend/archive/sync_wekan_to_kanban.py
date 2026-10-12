#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WeKan -> TOPO 研发管理看板 数据同步脚本

从 WeKan 看板 (http://172.28.71.239:8080) 拉取 T84研发管理 看板数据，
写入 TOPO 系统 IPRAN 项目的研发管理看板数据库 (rd_kanban_items 表)。

增量更新策略：
  1. 拉取 WeKan 全部列表 + 卡片
  2. 对每张卡片，先按 wekan_id 匹配本地记录；匹配不到则按 (列+标题) 兜底匹配
  3. 比较关键字段 (标题/列/状态/评论数/排序)，有变化才 UPDATE，无变化跳过
  4. 本地有但 WeKan 已删除的卡片仅记录日志，不物理删除

用法:
    python sync_wekan_to_kanban.py            # 正常同步
    python sync_wekan_to_kanban.py --dry-run  # 只比对不写库
    python sync_wekan_to_kanban.py --debug    # 打印详细调试信息
"""

import requests
import sqlite3
import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta

# ============================================================
# 配置区 (按需修改)
# ============================================================
WEKAN_BASE_URL = "http://172.28.71.239:8080"
WEKAN_BOARD_ID = "RHxSmKtgtA95uvPMK"
WEKAN_BOARD_TITLE_HINT = "t84"
WEKAN_LOGIN = "zhaokangwei@chenxiaotech.com"
WEKAN_PASSWORD = "z12345"

PROJECT_ID = 1
PROJECT_NAME = "IPRAN"

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "instance", "topo_system.db"
)

REQUEST_TIMEOUT = 30

COLUMN_KEYWORD_MAP = [
    ("远期", "long_term_req"),
    ("近期", "short_term_req"),
    ("开发", "in_progress"),
    ("完成", "completed"),
    ("测试", "pending_test"),
    ("周报", "weekly_report"),
    ("客户", "customer_issue"),
    ("挂起", "pending_issue"),
    ("重要", "important_update"),
]

LABEL_STATUS_MAP = {
    "正在奋战": ("in_progress", "#f59e0b"),
    "奋战": ("in_progress", "#f59e0b"),
    "完成": ("completed", "#10b981"),
    "待讨论": ("pending_discuss", "#ef4444"),
    "讨论": ("pending_discuss", "#ef4444"),
    "暂停": ("paused", "#94a3b8"),
    "部分支持": ("partially_support", "#8b5cf6"),
    "不支持": ("not_supported", "#6b7280"),
}

CST = timezone(timedelta(hours=8))


# ============================================================
# 工具函数
# ============================================================
def now_china():
    return datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S")


def parse_wekan_time(raw):
    if not raw:
        return None
    if isinstance(raw, dict):
        raw = raw.get("$date") or raw.get("date")
    if isinstance(raw, (int, float)):
        if raw > 1e12:
            raw = raw / 1000.0
        try:
            return datetime.fromtimestamp(raw, tz=CST).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return None
    if isinstance(raw, str):
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                dt = datetime.strptime(raw, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(CST).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
    return None


def match_column(list_title):
    if not list_title:
        return None
    for keyword, col_key in COLUMN_KEYWORD_MAP:
        if keyword in list_title:
            return col_key
    return None


def match_label_status(label_names):
    if not label_names:
        return (None, None)
    for name in label_names:
        for keyword, (status, color) in LABEL_STATUS_MAP.items():
            if keyword in name:
                return (status, color)
    return (None, None)


def normalize_title(t):
    if not t:
        return ""
    return re.sub(r"\s+", " ", t).strip()


def titles_equal(a, b):
    return normalize_title(a) == normalize_title(b)


# ============================================================
# WeKan API 客户端
# ============================================================
class WeKanClient:
    def __init__(self, base_url, debug=False):
        self.base = base_url.rstrip("/")
        self.token = None
        self.user_id = None
        self.debug = debug
        self.board_obj = None
        self.s = requests.Session()
        self.s.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
            }
        )

    def _auth_headers(self):
        h = {}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _safe_json(self, r, label=""):
        try:
            return r.json()
        except Exception:
            ct = r.headers.get("Content-Type", "")
            body = r.text[:300] if r.text else "(empty)"
            print(f"  [警告] {label} 响应非JSON (status={r.status_code}, Content-Type={ct})")
            if self.debug:
                print(f"    body[:300]={body}")
            return None

    def _get(self, path):
        url = f"{self.base}{path}"
        if self.debug:
            print(f"    [GET] {url}")
        r = self.s.get(url, headers=self._auth_headers(), timeout=REQUEST_TIMEOUT)
        if self.debug:
            print(f"    -> {r.status_code} ({len(r.content)} bytes)")
        return r

    def _post_json(self, path, body):
        url = f"{self.base}{path}"
        if self.debug:
            print(f"    [POST] {url}  body={json.dumps(body, ensure_ascii=False)[:200]}")
        r = self.s.post(
            url, json=body, headers=self._auth_headers(), timeout=REQUEST_TIMEOUT
        )
        if self.debug:
            print(f"    -> {r.status_code}  {r.text[:200]}")
        return r

    def login(self, username, password):
        candidates = [username]
        if "@" in username:
            local = username.split("@")[0]
            if local not in candidates:
                candidates.append(local)

        for u in candidates:
            print(f"  尝试登录 WeKan (用户: {u}) ...")
            try:
                r = self._post_json(
                    "/users/login", {"username": u, "password": password}
                )
                if r.status_code == 200:
                    data = r.json()
                    self.token = data.get("token")
                    self.user_id = data.get("id")
                    if self.token:
                        print(f"  登录成功! userId={self.user_id}")
                        return True
                print(f"  登录返回 {r.status_code}: {r.text[:150]}")
            except Exception as e:
                print(f"  登录异常: {e}")
        return False

    def get_boards(self):
        r = self._get("/api/boards")
        if r.status_code == 200:
            data = self._safe_json(r, "get_boards")
            if data is not None:
                return data
        if self.debug:
            print(f"  get_boards 失败: {r.status_code} {r.text[:200]}")
        return []

    def resolve_board_id(self, board_id, title_hint):
        r = self._get(f"/api/boards/{board_id}")
        if r.status_code == 200:
            b = self._safe_json(r, "resolve_board")
            if b is not None:
                self.board_obj = b
                print(f"  看板确认: {b.get('title', '?')}  (id={board_id})")
                return board_id
        print(f"  看板ID {board_id} 直接获取失败({r.status_code})，尝试按标题匹配...")
        boards = self.get_boards()
        if self.debug:
            print(f"  所有看板: {json.dumps(boards, ensure_ascii=False)[:500]}")
        for b in boards:
            bt = b.get("title", "")
            bid = b.get("_id", b.get("id", ""))
            if bid == board_id:
                self.board_obj = b
                print(f"  看板确认: {bt}  (id={bid})")
                return bid
            if title_hint and title_hint.lower() in bt.lower():
                self.board_obj = b
                print(f"  按标题匹配到看板: {bt}  (id={bid})")
                return bid
        if boards:
            print("  可用看板列表:")
            for b in boards:
                print(f"    - {b.get('title', '?')}  id={b.get('_id', b.get('id', ''))}")
        return None

    def get_lists(self, board_id):
        r = self._get(f"/api/boards/{board_id}/lists")
        if r.status_code == 200:
            data = self._safe_json(r, "get_lists")
            if data is not None:
                return data
        if self.debug:
            print(f"  get_lists 失败: {r.status_code} {r.text[:200]}")
        return []

    def get_cards(self, board_id, list_id):
        r = self._get(f"/api/boards/{board_id}/lists/{list_id}/cards")
        if r.status_code == 200:
            data = self._safe_json(r, "get_cards")
            if data is not None:
                return data
        if self.debug:
            print(f"  get_cards 失败: {r.status_code} {r.text[:200]}")
        return []

    def get_labels(self, board_id):
        r = self._get(f"/api/boards/{board_id}/labels")
        if r.status_code == 200:
            data = self._safe_json(r, "get_labels")
            if data is not None:
                return data
        if self.debug:
            print(f"  get_labels 失败: {r.status_code} {r.text[:200]}")
        return []

    def get_card_comments(self, board_id, card_id):
        r = self._get(f"/api/boards/{board_id}/cards/{card_id}/comments")
        if r.status_code == 200:
            data = self._safe_json(r, "get_card_comments")
            if data is not None:
                return data
        return []


# ============================================================
# 数据库同步
# ============================================================
class KanbanDB:
    def __init__(self, db_path, dry_run=False):
        self.db_path = db_path
        self.dry_run = dry_run
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_wekan_column()
        self._ensure_comment_wekan_column()

    def _ensure_wekan_column(self):
        c = self.conn.cursor()
        c.execute("PRAGMA table_info(rd_kanban_items)")
        cols = [row[1] for row in c.fetchall()]
        if "wekan_id" not in cols:
            print("  数据库: 添加 wekan_id 字段到 rd_kanban_items ...")
            c.execute(
                "ALTER TABLE rd_kanban_items ADD COLUMN wekan_id VARCHAR(40)"
            )
            c.execute(
                "CREATE INDEX IF NOT EXISTS ix_rd_kanban_wekan_id "
                "ON rd_kanban_items (wekan_id)"
            )
            self.conn.commit()
        if "wekan_list_id" not in cols:
            print("  数据库: 添加 wekan_list_id 字段到 rd_kanban_items ...")
            c.execute(
                "ALTER TABLE rd_kanban_items ADD COLUMN wekan_list_id VARCHAR(40)"
            )
            self.conn.commit()

    def _ensure_comment_wekan_column(self):
        c = self.conn.cursor()
        c.execute("PRAGMA table_info(rd_kanban_comments)")
        cols = [row[1] for row in c.fetchall()]
        if "wekan_id" not in cols:
            print("  数据库: 添加 wekan_id 字段到 rd_kanban_comments ...")
            c.execute(
                "ALTER TABLE rd_kanban_comments ADD COLUMN wekan_id VARCHAR(40)"
            )
            c.execute(
                "CREATE INDEX IF NOT EXISTS ix_rd_kanban_cmt_wekan_id "
                "ON rd_kanban_comments (wekan_id)"
            )
            self.conn.commit()

    def get_existing_by_wekan(self, project_id):
        c = self.conn.cursor()
        c.execute(
            "SELECT * FROM rd_kanban_items WHERE project_id=? AND wekan_id IS NOT NULL",
            (project_id,),
        )
        return {row["wekan_id"]: dict(row) for row in c.fetchall()}

    def find_by_title(self, project_id, column, title):
        c = self.conn.cursor()
        c.execute(
            "SELECT * FROM rd_kanban_items WHERE project_id=? AND column=? AND title=?",
            (project_id, column, title),
        )
        rows = c.fetchall()
        if rows:
            return dict(rows[0])
        c.execute(
            "SELECT * FROM rd_kanban_items WHERE project_id=? AND column=?",
            (project_id, column),
        )
        for row in c.fetchall():
            if titles_equal(row["title"], title):
                return dict(row)
        return None

    def get_all_wekan_ids(self, project_id):
        c = self.conn.cursor()
        c.execute(
            "SELECT wekan_id FROM rd_kanban_items WHERE project_id=? AND wekan_id IS NOT NULL",
            (project_id,),
        )
        return {row[0] for row in c.fetchall()}

    def insert_item(self, item):
        if self.dry_run:
            return
        c = self.conn.cursor()
        c.execute(
            """INSERT INTO rd_kanban_items
               (project_id, column, title, status, status_color, comment_count,
                sort_order, created_at, updated_at, tags, wekan_id, wekan_list_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                item["project_id"],
                item["column"],
                item["title"],
                item.get("status"),
                item.get("status_color"),
                item.get("comment_count", 0),
                item.get("sort_order", 0),
                item.get("created_at", now_china()),
                item.get("updated_at", now_china()),
                item.get("tags"),
                item.get("wekan_id"),
                item.get("wekan_list_id"),
            ),
        )
        self.conn.commit()

    def update_item(self, row_id, item):
        if self.dry_run:
            return
        c = self.conn.cursor()
        c.execute(
            """UPDATE rd_kanban_items SET
               column=?, title=?, status=?, status_color=?, comment_count=?,
               sort_order=?, tags=?, wekan_id=?, wekan_list_id=?, updated_at=?
               WHERE id=?""",
            (
                item["column"],
                item["title"],
                item.get("status"),
                item.get("status_color"),
                item.get("comment_count", 0),
                item.get("sort_order", 0),
                item.get("tags"),
                item.get("wekan_id"),
                item.get("wekan_list_id"),
                now_china(),
                row_id,
            ),
        )
        self.conn.commit()

    def get_item_id_by_wekan(self, wekan_id):
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM rd_kanban_items WHERE wekan_id=?", (wekan_id,)
        )
        row = c.fetchone()
        return row[0] if row else None

    def get_comments_by_item(self, item_id):
        c = self.conn.cursor()
        c.execute(
            "SELECT * FROM rd_kanban_comments WHERE item_id=?", (item_id,)
        )
        return [dict(r) for r in c.fetchall()]

    def find_comment_by_wekan(self, wekan_id):
        c = self.conn.cursor()
        c.execute(
            "SELECT * FROM rd_kanban_comments WHERE wekan_id=?", (wekan_id,)
        )
        row = c.fetchone()
        return dict(row) if row else None

    def find_comment_by_content(self, item_id, content):
        c = self.conn.cursor()
        c.execute(
            "SELECT * FROM rd_kanban_comments WHERE item_id=? AND content=? AND wekan_id IS NULL",
            (item_id, content),
        )
        row = c.fetchone()
        return dict(row) if row else None

    def get_comment_wekan_ids(self, item_id):
        c = self.conn.cursor()
        c.execute(
            "SELECT wekan_id FROM rd_kanban_comments WHERE item_id=? AND wekan_id IS NOT NULL",
            (item_id,),
        )
        return {row[0] for row in c.fetchall()}

    def insert_comment(self, comment):
        if self.dry_run:
            return
        c = self.conn.cursor()
        c.execute(
            """INSERT INTO rd_kanban_comments
               (item_id, user_id, content, created_at, updated_at, wekan_id)
               VALUES (?,?,?,?,?,?)""",
            (
                comment["item_id"],
                comment.get("user_id"),
                comment["content"],
                comment.get("created_at", now_china()),
                comment.get("updated_at", now_china()),
                comment.get("wekan_id"),
            ),
        )
        self.conn.commit()

    def update_comment(self, row_id, comment):
        if self.dry_run:
            return
        c = self.conn.cursor()
        c.execute(
            """UPDATE rd_kanban_comments SET
               content=?, updated_at=?, wekan_id=?
               WHERE id=?""",
            (
                comment["content"],
                now_china(),
                comment.get("wekan_id"),
                row_id,
            ),
        )
        self.conn.commit()

    def bind_comment_wekan(self, row_id, wekan_id):
        if self.dry_run:
            return
        c = self.conn.cursor()
        c.execute(
            "UPDATE rd_kanban_comments SET wekan_id=? WHERE id=?",
            (wekan_id, row_id),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()


# ============================================================
# 主同步逻辑
# ============================================================
def sync(dry_run=False, debug=False):
    print("=" * 60)
    print(f"WeKan -> TOPO 看板同步  项目={PROJECT_NAME}(id={PROJECT_ID})")
    print(f"数据库: {DB_PATH}")
    print(f"模式: {'DRY-RUN (只比对不写库)' if dry_run else '正常同步'}")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"错误: 数据库文件不存在: {DB_PATH}")
        return

    wk = WeKanClient(WEKAN_BASE_URL, debug=debug)
    if not wk.login(WEKAN_LOGIN, WEKAN_PASSWORD):
        print("错误: WeKan 登录失败，请检查账号密码及网络。")
        return

    board_id = wk.resolve_board_id(WEKAN_BOARD_ID, WEKAN_BOARD_TITLE_HINT)
    if not board_id:
        print("错误: 无法确定看板 ID，请检查 WEKAN_BOARD_ID 配置。")
        return

    print("\n--- 拉取 WeKan 列表 ---")
    lists = wk.get_lists(board_id)
    lists = [l for l in lists if not l.get("archived", False)]
    print(f"  共 {len(lists)} 个列表 (已排除归档)")
    for l in lists:
        lt = l.get("title", "?")
        lid = l.get("_id", l.get("id", "?"))
        col = match_column(lt)
        flag = "OK" if col else "!! 未匹配"
        print(f"    [{flag}] {lt}  ->  {col or '???'}  (listId={lid})")

    print("\n--- 拉取 WeKan 标签 ---")
    labels = []
    if wk.board_obj and wk.board_obj.get("labels"):
        labels = wk.board_obj["labels"]
        print(f"  从看板详情提取标签: {len(labels)} 个")
    if not labels:
        labels = wk.get_labels(board_id)
        print(f"  从 labels 端点获取标签: {len(labels)} 个")
    label_map = {}
    for lb in labels:
        lid = lb.get("_id", lb.get("id", ""))
        lname = lb.get("name", "")
        label_map[lid] = lname
    print(f"  共 {len(label_map)} 个标签: {list(label_map.values())}")

    print("\n--- 拉取各列表卡片 ---")
    all_cards = []
    for l in lists:
        lid = l.get("_id", l.get("id", ""))
        ltitle = l.get("title", "?")
        cards = wk.get_cards(board_id, lid)
        cards = [c for c in cards if not c.get("archived", False)]
        for c in cards:
            c["_wekan_list_id"] = lid
            c["_wekan_list_title"] = ltitle
        all_cards.extend(cards)
        print(f"    {ltitle}: {len(cards)} 张卡片")
    print(f"  合计 {len(all_cards)} 张卡片")

    print("\n--- 打开本地数据库 ---")
    db = KanbanDB(DB_PATH, dry_run=dry_run)
    existing_by_wekan = db.get_existing_by_wekan(PROJECT_ID)
    print(f"  本地已绑定 wekan_id 的记录: {len(existing_by_wekan)} 条")

    print("\n--- 开始增量比对 ---")
    stats = {"new": 0, "updated": 0, "skipped": 0, "unmapped_list": 0, "error": 0}
    seen_wekan_ids = set()

    for idx, card in enumerate(all_cards):
        cid = card.get("_id", card.get("id", ""))
        if not cid:
            continue
        seen_wekan_ids.add(cid)

        list_title = card.get("_wekan_list_title", "")
        list_id = card.get("_wekan_list_id", "")
        col_key = match_column(list_title)
        if not col_key:
            stats["unmapped_list"] += 1
            if debug:
                print(f"  [跳过] 列'{list_title}'无映射  card={cid}")
            continue

        title = card.get("title", "").strip()
        if not title:
            continue

        label_ids = card.get("labelIds", []) or []
        label_names = [label_map.get(lid, "") for lid in label_ids if lid in label_map]
        if not label_names:
            for lb in card.get("labels", []) or []:
                if isinstance(lb, dict):
                    ln = lb.get("name", "")
                    if ln:
                        label_names.append(ln)
                elif isinstance(lb, str):
                    label_names.append(lb)
        status, status_color = match_label_status(label_names)

        comment_count = card.get("commentCount", 0) or 0
        sort_val = card.get("sort")
        if sort_val is None:
            sort_val = idx
        try:
            sort_order = float(sort_val)
        except Exception:
            sort_order = float(idx)

        tags_json = json.dumps(label_names, ensure_ascii=False) if label_names else None

        created = parse_wekan_time(card.get("createdAt")) or now_china()
        updated = (
            parse_wekan_time(card.get("updatedAt"))
            or parse_wekan_time(card.get("dateLastActivity"))
            or now_china()
        )

        item = {
            "project_id": PROJECT_ID,
            "column": col_key,
            "title": title,
            "status": status,
            "status_color": status_color,
            "comment_count": comment_count,
            "sort_order": sort_order,
            "tags": tags_json,
            "wekan_id": cid,
            "wekan_list_id": list_id,
            "created_at": created,
            "updated_at": updated,
        }

        existing = existing_by_wekan.get(cid)
        if existing is None:
            existing = db.find_by_title(PROJECT_ID, col_key, title)
            if existing and not existing.get("wekan_id"):
                if debug:
                    print(f"  [绑定] wekan_id={cid} -> 本地id={existing['id']} (按标题匹配)")

        if existing is None:
            stats["new"] += 1
            print(f"  [新增] [{col_key}] {title[:60]}")
            db.insert_item(item)
        else:
            changed = False
            reasons = []
            if not titles_equal(existing["title"], title):
                changed = True
                reasons.append("标题")
            if existing["column"] != col_key:
                changed = True
                reasons.append(f"列 {existing['column']}->{col_key}")
            if (existing["status"] or None) != (status or None):
                changed = True
                reasons.append("状态")
            if (existing["status_color"] or None) != (status_color or None):
                changed = True
                reasons.append("状态色")
            if int(existing["comment_count"] or 0) != int(comment_count or 0):
                changed = True
                reasons.append("评论数")
            try:
                if abs(float(existing["sort_order"] or 0) - float(sort_order)) > 0.001:
                    changed = True
                    reasons.append("排序")
            except Exception:
                pass
            old_tags = existing["tags"]
            if (old_tags or None) != (tags_json or None):
                changed = True
                reasons.append("标签")

            if changed:
                stats["updated"] += 1
                print(
                    f"  [更新] id={existing['id']} [{col_key}] {title[:50]}  原因: {', '.join(reasons)}"
                )
                db.update_item(existing["id"], item)
            else:
                stats["skipped"] += 1
                if not existing.get("wekan_id") and not dry_run:
                    c2 = db.conn.cursor()
                    c2.execute(
                        "UPDATE rd_kanban_items SET wekan_id=?, wekan_list_id=? WHERE id=?",
                        (cid, list_id, existing["id"]),
                    )
                    db.conn.commit()
                if debug:
                    print(f"  [跳过] id={existing['id']} [{col_key}] {title[:50]}")

    local_wekan_ids = db.get_all_wekan_ids(PROJECT_ID)
    deleted_in_wekan = local_wekan_ids - seen_wekan_ids
    if deleted_in_wekan:
        print(f"\n--- WeKan 已删除但本地仍存在的卡片: {len(deleted_in_wekan)} 条 ---")
        for wid in sorted(deleted_in_wekan):
            c2 = db.conn.cursor()
            c2.execute(
                "SELECT id, column, title FROM rd_kanban_items WHERE wekan_id=?",
                (wid,),
            )
            row = c2.fetchone()
            if row:
                print(f"    id={row[0]} [{row[1]}] {row[2][:50]}  (wekan_id={wid})")
        print("  (仅记录，未做删除。如需清理请手动处理或加 --remove-deleted)")

    print("\n--- 同步卡片评论 ---")
    cmt_stats = {"new": 0, "updated": 0, "skipped": 0, "deleted": 0}
    cards_with_comments = 0
    total_wekan_comments = 0

    for card in all_cards:
        cid = card.get("_id", card.get("id", ""))
        if not cid:
            continue
        local_item_id = db.get_item_id_by_wekan(cid)
        if not local_item_id:
            continue

        list_id = card.get("_wekan_list_id", "")
        comments = wk.get_card_comments(board_id, cid)
        if not comments:
            continue
        cards_with_comments += 1
        total_wekan_comments += len(comments)

        local_wekan_cmt_ids = db.get_comment_wekan_ids(local_item_id)
        seen_cmt_ids = set()

        for cm in comments:
            cm_id = cm.get("_id", cm.get("id", ""))
            if not cm_id:
                continue
            seen_cmt_ids.add(cm_id)

            text = cm.get("comment", "") or cm.get("text", "") or ""
            if not text.strip():
                continue
            created = parse_wekan_time(cm.get("createdAt")) or now_china()
            updated = (
                parse_wekan_time(cm.get("updatedAt"))
                or parse_wekan_time(cm.get("modifiedAt"))
                or created
            )

            comment = {
                "item_id": local_item_id,
                "content": text,
                "wekan_id": cm_id,
                "created_at": created,
                "updated_at": updated,
            }

            existing_cmt = db.find_comment_by_wekan(cm_id)
            if existing_cmt is None:
                existing_cmt = db.find_comment_by_content(local_item_id, text)

            if existing_cmt is None:
                cmt_stats["new"] += 1
                db.insert_comment(comment)
            else:
                changed = existing_cmt["content"] != text
                if changed:
                    cmt_stats["updated"] += 1
                    db.update_comment(existing_cmt["id"], comment)
                else:
                    cmt_stats["skipped"] += 1
                    if not existing_cmt.get("wekan_id"):
                        db.bind_comment_wekan(existing_cmt["id"], cm_id)

        deleted_cmts = local_wekan_cmt_ids - seen_cmt_ids
        if deleted_cmts:
            cmt_stats["deleted"] += len(deleted_cmts)
            if debug:
                print(f"    卡片 {cid} 本地有 {len(deleted_cmts)} 条评论在 WeKan 已删除")

    print(f"  有评论的卡片: {cards_with_comments}")
    print(f"  WeKan 评论总数: {total_wekan_comments}")
    print(f"  评论新增: {cmt_stats['new']}  更新: {cmt_stats['updated']}  跳过: {cmt_stats['skipped']}  WeKan已删除: {cmt_stats['deleted']}")

    db.close()

    print("\n" + "=" * 60)
    print("同步结果汇总")
    print("=" * 60)
    print(f"  WeKan 卡片总数 : {len(all_cards)}")
    print(f"  新增            : {stats['new']}")
    print(f"  更新            : {stats['updated']}")
    print(f"  跳过(无变化)    : {stats['skipped']}")
    print(f"  列未映射(跳过)  : {stats['unmapped_list']}")
    print(f"  WeKan已删除     : {len(deleted_in_wekan)}")
    print(f"  --- 评论 ---")
    print(f"  评论新增        : {cmt_stats['new']}")
    print(f"  评论更新        : {cmt_stats['updated']}")
    print(f"  评论跳过        : {cmt_stats['skipped']}")
    print(f"  评论WeKan已删除 : {cmt_stats['deleted']}")
    if dry_run:
        print("  (DRY-RUN 模式，未实际写库)")
    print("=" * 60)


def main():
    dry_run = "--dry-run" in sys.argv
    debug = "--debug" in sys.argv
    sync(dry_run=dry_run, debug=debug)


if __name__ == "__main__":
    main()