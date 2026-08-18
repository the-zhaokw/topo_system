"""
项目研发管理 - Kanban 看板 API
每个项目一张看板，7 列布局：
  - recent_req_pending  近期需求 - 待评估
  - recent_req_approved 近期需求 - 已确认待排期
  - in_progress         正在开发
  - completed           已完成
  - pending_test        待测试
  - weekly_report       周报
  - customer_issue      客户问题
每张卡片可编辑、可拖拽换列、可删除、可评论、可传附件、可反应。
周报列卡片支持自动汇总为 Markdown；客户问题列支持严重度/SLA。
"""

from datetime import datetime, timedelta
import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

rd_kanban_bp = Blueprint('rd_kanban', __name__, url_prefix='/rd-kanban')

# 列定义（顺序与前端一致）
COLUMNS = [
    {'key': 'recent_req_pending', 'name': '近期需求 - 待评估', 'color': '#0ea5e9'},
    {'key': 'recent_req_approved', 'name': '近期需求 - 已确认', 'color': '#0284c7'},
    {'key': 'in_progress', 'name': '正在开发', 'color': '#f59e0b'},
    {'key': 'completed', 'name': '已完成', 'color': '#10b981'},
    {'key': 'pending_test', 'name': '待测试', 'color': '#8b5cf6'},
    {'key': 'weekly_report', 'name': '周报', 'color': '#ec4899'},
    {'key': 'customer_issue', 'name': '客户问题', 'color': '#ef4444'},
]
COLUMN_KEYS = [c['key'] for c in COLUMNS]
COLUMN_NAME_MAP = {c['key']: c['name'] for c in COLUMNS}

# 状态徽章选项（与前端展示的 8 种状态徽章一致；色值与其他页面的状态色板保持一致）
STATUS_OPTIONS = [
    {'value': 'completed',         'label': '完成',         'color': '#10b981'},  # 绿 - 与 ProjectList status-green、Bug resolved 同色
    {'value': 'in_progress',       'label': '正在备战中...', 'color': '#f59e0b'},  # 黄 - 与 in_progress / pending_test 同色
    {'value': 'priority',          'label': '优先',         'color': '#ec4899'},  # 粉红 - 与 weekly_report 列同色
    {'value': 'paused',            'label': '暂停',         'color': '#94a3b8'},  # 灰 - 与 paused 既有色一致
    {'value': 'pending_discuss',   'label': '待讨论',       'color': '#ef4444'},  # 红 - 与 customer_issue 列同色
    {'value': 'not_supported',     'label': '不支持',       'color': '#6b7280'},  # 深灰
    {'value': 'test_completed',    'label': '测试完成',     'color': '#14b8a6'},  # 青绿
    {'value': 'partially_support', 'label': '部分支持',     'color': '#8b5cf6'},  # 紫 - 与 pending_test 列同色
]

# 客户问题严重度
ISSUE_SEVERITY = [
    {'value': 'critical', 'label': '致命', 'color': '#dc2626'},
    {'value': 'high', 'label': '严重', 'color': '#ef4444'},
    {'value': 'medium', 'label': '一般', 'color': '#f59e0b'},
    {'value': 'low', 'label': '轻微', 'color': '#10b981'},
]
ISSUE_SLA_HOURS = {'critical': 4, 'high': 24, 'medium': 72, 'low': 168}

# 老列名 -> 新列名 的兼容映射（数据迁移用）
LEGACY_COLUMN_MAP = {
    'recent_req_1': 'recent_req_pending',
    'recent_req_2': 'recent_req_approved',
    'requirement': 'recent_req_pending',
    'pending': 'recent_req_pending',
    'in_development': 'in_progress',
    'developing': 'in_progress',
    'test': 'pending_test',
    'testing': 'pending_test',
    'done': 'completed',
    'report': 'weekly_report',
    'issue': 'customer_issue',
}


def _migrate_legacy_columns():
    """把老列名迁移到新列名（一次性）"""
    db = get_db()
    model = _get_model()
    if model is None:
        return
    try:
        updated = 0
        for legacy, new in LEGACY_COLUMN_MAP.items():
            rows = model.query.filter(model.column == legacy).all()
            for r in rows:
                r.column = new
                updated += 1
        if updated:
            db.session.commit()
            print(f"[rd_kanban] 已迁移 {updated} 条历史列名到新列名")
    except Exception as e:
        db.session.rollback()
        print(f"[rd_kanban] 迁移历史列名失败: {e}")


def get_db():
    from enhanced_app import get_db_instance
    return get_db_instance()


def get_models():
    import enhanced_app
    return (
        enhanced_app.db,
        enhanced_app.User,
        enhanced_app.Project,
        enhanced_app.ProjectMember,
    )


def _serialize_item(item, user_dict=None):
    assignee = None
    if item.assignee_id and user_dict and item.assignee_id in user_dict:
        u = user_dict[item.assignee_id]
        assignee = {
            'id': u.id,
            'name': (u.first_name or '') + (u.last_name or '') or u.username,
            'username': u.username,
            'avatar': u.avatar,
        }
    elif item.assignee_id:
        # 仍尝试查一次（轻量）
        try:
            _, User, _, _ = get_models()
            u = User.query.get(item.assignee_id)
            if u:
                assignee = {
                    'id': u.id,
                    'name': (u.first_name or '') + (u.last_name or '') or u.username,
                    'username': u.username,
                    'avatar': u.avatar,
                }
        except Exception:
            pass
    import json as _json
    tags = []
    if item.tags:
        try:
            tags = _json.loads(item.tags) or []
        except Exception:
            tags = []
    return {
        'id': item.id,
        'project_id': item.project_id,
        'column': item.column,
        'title': item.title,
        'status': item.status,
        'status_color': item.status_color,
        'comment_count': item.comment_count or 0,
        'assignee': assignee,
        'sort_order': item.sort_order or 0,
        'created_at': item.created_at.isoformat() if item.created_at else None,
        'updated_at': item.updated_at.isoformat() if item.updated_at else None,
        'created_by': item.created_by,
        'severity': item.severity,
        'due_at': item.due_at.isoformat() if item.due_at else None,
        'resolved_at': item.resolved_at.isoformat() if item.resolved_at else None,
        'is_pinned': bool(item.is_pinned),
        'tags': tags,
    }


def _check_project_access(project_id, user_id, user_role):
    """校验用户对项目有访问权限"""
    _, _, Project, ProjectMember = get_models()
    project = Project.query.get(project_id)
    if not project:
        return None, (jsonify({'success': False, 'error': '项目不存在', 'code': 'NOT_FOUND'}), 404)
    if user_role == 'admin':
        return project, None
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if not member:
        return None, (jsonify({'success': False, 'error': '无权限访问此项目', 'code': 'FORBIDDEN'}), 403)
    return project, None


@rd_kanban_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def list_items(project_id):
    """获取某项目所有 Kanban 卡片

    支持 query 参数：
      - column: 按列过滤
      - assignee_id: 按指派人过滤
      - keyword: 按标题模糊搜索
    """
    db = get_db()
    _, User, Project, ProjectMember = get_models()
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'success': False, 'error': '用户不存在'}), 401

    project, err = _check_project_access(project_id, current_user_id, current_user.role)
    if err:
        return err

    # 确保表存在（首次访问时建立 schema）
    _get_models()

    # 迁移老列名（recent_req_1/2 等）
    _migrate_legacy_columns()

    model = _get_model()
    q = model.query.filter_by(project_id=project_id)
    column_filter = (request.args.get('column') or '').strip()
    if column_filter and column_filter in COLUMN_KEYS:
        q = q.filter(model.column == column_filter)
    assignee_filter = request.args.get('assignee_id')
    if assignee_filter:
        try:
            q = q.filter(model.assignee_id == int(assignee_filter))
        except (TypeError, ValueError):
            pass
    keyword = (request.args.get('keyword') or '').strip()
    if keyword:
        like = f'%{keyword}%'
        q = q.filter(model.title.like(like))
    items = q.order_by(model.column, model.sort_order, model.id).all()

    # 批量加载用户
    user_ids = {it.assignee_id for it in items if it.assignee_id}
    user_ids.add(current_user_id)
    users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    user_dict = {u.id: u for u in users}

    # 计算各列数量
    column_counts = {c['key']: 0 for c in COLUMNS}
    for it in items:
        if it.column in column_counts:
            column_counts[it.column] += 1

    return jsonify({
        'success': True,
        'columns': COLUMNS,
        'status_options': STATUS_OPTIONS,
        'issue_severity': ISSUE_SEVERITY,
        'column_counts': column_counts,
        'items': [_serialize_item(it, user_dict) for it in items],
        'project': {'id': project.id, 'name': project.name, 'code': project.code}
    })


@rd_kanban_bp.route('', methods=['POST'])
@jwt_required()
def create_item():
    """新建卡片"""
    data = request.get_json(silent=True) or {}
    project_id = data.get('project_id')
    column = data.get('column')
    title = (data.get('title') or '').strip()

    if not project_id or not column or not title:
        return jsonify({'success': False, 'error': 'project_id/column/title 必填'}), 400
    if column not in COLUMN_KEYS:
        return jsonify({'success': False, 'error': f'不支持的列: {column}'}), 400

    db = get_db()
    _, User, Project, ProjectMember = get_models()
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)

    project, err = _check_project_access(project_id, current_user_id, current_user.role)
    if err:
        return err

    model = _get_model()
    # 同一列内最大 sort_order + 10
    max_order = db.session.query(model.sort_order).filter_by(project_id=project_id, column=column).order_by(model.sort_order.desc()).first()
    next_order = (max_order[0] + 10) if max_order and max_order[0] is not None else 0

    # 客户问题自动计算 due_at
    severity = data.get('severity') or None
    due_at = None
    if column == 'customer_issue' and severity in ISSUE_SLA_HOURS:
        due_at = datetime.utcnow() + timedelta(hours=ISSUE_SLA_HOURS[severity])

    item = model(
        project_id=project_id,
        column=column,
        title=title,
        status=data.get('status') or None,
        status_color=data.get('status_color') or None,
        assignee_id=data.get('assignee_id') or None,
        sort_order=next_order,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by=current_user_id,
        comment_count=0,
        severity=severity,
        due_at=due_at,
        resolved_at=None,
        is_pinned=1 if data.get('is_pinned') else 0,
        tags=_json_dumps_safe(data.get('tags')),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'success': True, 'item': _serialize_item(item)})


@rd_kanban_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    """更新卡片（标题/状态/负责人/列/排序等）"""
    data = request.get_json(silent=True) or {}
    db = get_db()
    _, User, _, _ = get_models()
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)

    model = _get_model()
    item = model.query.get(item_id)
    if not item:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404

    project, err = _check_project_access(item.project_id, current_user_id, current_user.role)
    if err:
        return err

    # 字段更新
    if 'title' in data:
        new_title = (data.get('title') or '').strip()
        if not new_title:
            return jsonify({'success': False, 'error': '标题不能为空'}), 400
        item.title = new_title
    if 'column' in data:
        new_col = data.get('column')
        if new_col not in COLUMN_KEYS:
            return jsonify({'success': False, 'error': f'不支持的列: {new_col}'}), 400
        item.column = new_col
    if 'status' in data:
        item.status = data.get('status') or None
    if 'status_color' in data:
        item.status_color = data.get('status_color') or None
    if 'assignee_id' in data:
        item.assignee_id = data.get('assignee_id') or None
    if 'sort_order' in data:
        try:
            item.sort_order = int(data.get('sort_order') or 0)
        except (TypeError, ValueError):
            pass
    if 'comment_count' in data:
        try:
            item.comment_count = max(0, int(data.get('comment_count') or 0))
        except (TypeError, ValueError):
            pass
    if 'severity' in data:
        new_sev = data.get('severity') or None
        old_sev = item.severity
        item.severity = new_sev
        # 客户问题：只要严重度改变，就按新的 SLA 重新计算 due_at
        if item.column == 'customer_issue' and new_sev in ISSUE_SLA_HOURS and new_sev != old_sev:
            item.due_at = datetime.utcnow() + timedelta(hours=ISSUE_SLA_HOURS[new_sev])
    if 'due_at' in data:
        item.due_at = _parse_iso(data.get('due_at'))
    if 'resolved_at' in data:
        item.resolved_at = _parse_iso(data.get('resolved_at'))
    if 'is_pinned' in data:
        item.is_pinned = 1 if data.get('is_pinned') else 0
    if 'tags' in data:
        item.tags = _json_dumps_safe(data.get('tags'))

    item.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'item': _serialize_item(item)})


@rd_kanban_bp.route('/sort', methods=['PUT'])
@jwt_required()
def batch_sort():
    """批量更新排序/换列（拖拽场景）"""
    data = request.get_json(silent=True) or {}
    moves = data.get('moves') or []
    if not isinstance(moves, list):
        return jsonify({'success': False, 'error': 'moves 必须是数组'}), 400

    db = get_db()
    _, User, _, _ = get_models()
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'success': False, 'error': '用户不存在'}), 401

    model = _get_model()
    for m in moves:
        if not isinstance(m, dict):
            continue
        item_id = m.get('id')
        if not item_id:
            continue
        item = model.query.get(item_id)
        if not item:
            continue
        # 权限
        project, err = _check_project_access(item.project_id, current_user_id, current_user.role)
        if err:
            continue
        if 'column' in m and m['column'] in COLUMN_KEYS:
            item.column = m['column']
        if 'sort_order' in m:
            try:
                item.sort_order = int(m['sort_order'] or 0)
            except (TypeError, ValueError):
                pass
        item.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})


@rd_kanban_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    db = get_db()
    _, User, _, _ = get_models()
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)

    model = _get_model()
    item = model.query.get(item_id)
    if not item:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404

    project, err = _check_project_access(item.project_id, current_user_id, current_user.role)
    if err:
        return err

    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})


# ---------------- 模型定义（运行时注入到 enhanced_app） ----------------
RDKanbanItem = None
RDKanbanComment = None
RDKanbanAttachment = None

# 附件存储目录
RD_ATTACHMENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads', 'rd_kanban')
os.makedirs(RD_ATTACHMENT_DIR, exist_ok=True)


def _get_models():
    """惰性获取 RD Kanban 全部模型类"""
    global RDKanbanItem, RDKanbanComment, RDKanbanAttachment
    import enhanced_app
    from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger
    from enhanced_app import db

    if RDKanbanItem is None:
        class RDKanbanItem(db.Model):
            __tablename__ = 'rd_kanban_items'
            id = Column(Integer, primary_key=True, autoincrement=True)
            project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
            column = Column(String(40), nullable=False, index=True)
            title = Column(String(500), nullable=False)
            status = Column(String(40), nullable=True)
            status_color = Column(String(20), nullable=True)
            comment_count = Column(Integer, default=0, nullable=False)
            assignee_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
            sort_order = Column(Integer, default=0, nullable=False, index=True)
            created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
            created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
            # 客户问题专用
            severity = Column(String(20), nullable=True)
            due_at = Column(DateTime, nullable=True)
            resolved_at = Column(DateTime, nullable=True)
            # 周报专用
            is_pinned = Column(Integer, default=0, nullable=False)
            # 通用
            tags = Column(Text, nullable=True)  # JSON 数组字符串

            def __repr__(self):
                return f'<RDKanbanItem {self.id} {self.column} {self.title[:20]}>'

        enhanced_app.RDKanbanItem = RDKanbanItem
        RDKanbanItem = RDKanbanItem

    if RDKanbanComment is None:
        class RDKanbanComment(db.Model):
            __tablename__ = 'rd_kanban_comments'
            id = Column(Integer, primary_key=True, autoincrement=True)
            item_id = Column(Integer, ForeignKey('rd_kanban_items.id', ondelete='CASCADE'), nullable=False, index=True)
            user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
            content = Column(Text, nullable=False)
            # 简单表情反应：JSON 字符串，{"👍": [user_ids], "❤️": [user_ids]}
            reactions = Column(Text, nullable=True)
            parent_id = Column(Integer, ForeignKey('rd_kanban_comments.id', ondelete='CASCADE'), nullable=True)
            created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

            def __repr__(self):
                return f'<RDKanbanComment {self.id} item={self.item_id}>'

        enhanced_app.RDKanbanComment = RDKanbanComment
        RDKanbanComment = RDKanbanComment

    if RDKanbanAttachment is None:
        class RDKanbanAttachment(db.Model):
            __tablename__ = 'rd_kanban_attachments'
            id = Column(Integer, primary_key=True, autoincrement=True)
            item_id = Column(Integer, ForeignKey('rd_kanban_items.id', ondelete='CASCADE'), nullable=False, index=True)
            original_name = Column(String(255), nullable=False)
            stored_name = Column(String(255), nullable=False)
            file_path = Column(String(500), nullable=False)
            file_size = Column(BigInteger, default=0, nullable=False)
            mime_type = Column(String(120), nullable=True)
            uploaded_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
            uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

            def __repr__(self):
                return f'<RDKanbanAttachment {self.id} {self.original_name}>'

        enhanced_app.RDKanbanAttachment = RDKanbanAttachment
        RDKanbanAttachment = RDKanbanAttachment

    try:
        db.create_all()
    except Exception as e:
        print(f'Create rd_kanban tables error: {e}')

    return enhanced_app.RDKanbanItem, enhanced_app.RDKanbanComment, enhanced_app.RDKanbanAttachment


def _get_model():
    return _get_models()[0]


def get_rd_kanban_bp():
    return rd_kanban_bp


def _json_dumps_safe(value):
    """将 tags 等字段安全序列化为 JSON 字符串"""
    import json as _json
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return _json.dumps(value, ensure_ascii=False)
    except Exception:
        return None


def _parse_iso(value):
    """解析 ISO 时间字符串为 datetime，无法解析则返回 None"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        s = value.replace('Z', '+00:00')
        return datetime.fromisoformat(s).replace(tzinfo=None)
    except Exception:
        return None


# ============================================================
# 评论 / 附件 / 文件下载 接口
# ============================================================

def _get_item_or_404(item_id):
    Item, _, _ = _get_models()
    return Item.query.get(item_id)


def _check_item_access(item, user_id, user_role):
    import enhanced_app
    Project = enhanced_app.Project
    ProjectMember = enhanced_app.ProjectMember
    project = Project.query.get(item.project_id)
    if not project:
        return jsonify({'success': False, 'error': '项目不存在'}), 404
    if user_role == 'admin':
        return None
    member = ProjectMember.query.filter_by(project_id=item.project_id, user_id=user_id).first()
    if not member:
        return jsonify({'success': False, 'error': '无权限访问此卡片'}), 403
    return None


def _serialize_comment(c, user_dict=None):
    user = None
    if c.user_id and user_dict and c.user_id in user_dict:
        u = user_dict[c.user_id]
    elif c.user_id:
        import enhanced_app
        u = enhanced_app.User.query.get(c.user_id)
    else:
        u = None
    if u:
        user = {
            'id': u.id,
            'name': ((u.first_name or '') + (u.last_name or '')) or u.username,
            'username': u.username,
            'avatar': u.avatar,
        }
    # 解析 reactions
    reactions = {}
    if c.reactions:
        try:
            import json as _json
            reactions = _json.loads(c.reactions) or {}
        except Exception:
            reactions = {}
    return {
        'id': c.id,
        'item_id': c.item_id,
        'parent_id': c.parent_id,
        'user': user,
        'content': c.content,
        'reactions': reactions,
        'created_at': c.created_at.isoformat() if c.created_at else None,
        'updated_at': c.updated_at.isoformat() if c.updated_at else None,
    }


def _serialize_attachment(a, user_dict=None):
    user = None
    if a.uploaded_by:
        import enhanced_app
        u = user_dict.get(a.uploaded_by) if user_dict else enhanced_app.User.query.get(a.uploaded_by)
        if u:
            user = {
                'id': u.id,
                'name': ((u.first_name or '') + (u.last_name or '')) or u.username,
                'username': u.username,
            }
    return {
        'id': a.id,
        'item_id': a.item_id,
        'original_name': a.original_name,
        'stored_name': a.stored_name,
        'file_size': a.file_size,
        'mime_type': a.mime_type,
        'download_url': f'/api/rd-kanban/attachments/{a.id}/download',
        'uploader': user,
        'uploaded_at': a.uploaded_at.isoformat() if a.uploaded_at else None,
    }


# ---------- 评论 ----------

@rd_kanban_bp.route('/<int:item_id>/comments', methods=['GET'])
@jwt_required()
def list_comments(item_id):
    item = _get_item_or_404(item_id)
    if not item:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404
    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    err = _check_item_access(item, current_user_id, current_user.role)
    if err:
        return err
    _, Comment, _ = _get_models()
    comments = Comment.query.filter_by(item_id=item_id).order_by(Comment.created_at.asc()).all()
    user_ids = {c.user_id for c in comments if c.user_id}
    users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    user_dict = {u.id: u for u in users}
    return jsonify({
        'success': True,
        'comments': [_serialize_comment(c, user_dict) for c in comments]
    })


@rd_kanban_bp.route('/<int:item_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(item_id):
    item = _get_item_or_404(item_id)
    if not item:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404
    data = request.get_json(silent=True) or {}
    content = (data.get('content') or '').strip()
    if not content:
        return jsonify({'success': False, 'error': '评论内容不能为空'}), 400
    parent_id = data.get('parent_id')
    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    err = _check_item_access(item, current_user_id, current_user.role)
    if err:
        return err
    _, Comment, _ = _get_models()
    comment = Comment(
        item_id=item_id,
        user_id=current_user_id,
        content=content,
        parent_id=parent_id,
        reactions='{}',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db = get_db()
    db.session.add(comment)
    # 同步更新 card.comment_count
    Item, _, _ = _get_models()
    it = Item.query.get(item_id)
    if it:
        it.comment_count = (it.comment_count or 0) + 1
        it.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'comment': _serialize_comment(comment, {current_user_id: current_user})})


@rd_kanban_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    _, Comment, _ = _get_models()
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'success': False, 'error': '评论不存在'}), 404
    data = request.get_json(silent=True) or {}
    new_content = (data.get('content') or '').strip()
    if not new_content:
        return jsonify({'success': False, 'error': '评论内容不能为空'}), 400
    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    # 权限：管理员或作者本人
    if current_user.role != 'admin' and comment.user_id != current_user_id:
        return jsonify({'success': False, 'error': '无权编辑此评论'}), 403
    comment.content = new_content
    comment.updated_at = datetime.utcnow()
    db = get_db()
    db.session.commit()
    return jsonify({'success': True, 'comment': _serialize_comment(comment, {current_user_id: current_user})})


@rd_kanban_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    _, Comment, _ = _get_models()
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'success': False, 'error': '评论不存在'}), 404
    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    if current_user.role != 'admin' and comment.user_id != current_user_id:
        return jsonify({'success': False, 'error': '无权删除此评论'}), 403
    item_id = comment.item_id
    db = get_db()
    db.session.delete(comment)
    # 同步 -1
    Item, _, _ = _get_models()
    it = Item.query.get(item_id)
    if it and (it.comment_count or 0) > 0:
        it.comment_count = it.comment_count - 1
        it.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})


@rd_kanban_bp.route('/comments/<int:comment_id>/react', methods=['POST'])
@jwt_required()
def react_comment(comment_id):
    """切换表情反应：{emoji: '+1' or '-1' or 'toggle'}"""
    _, Comment, _ = _get_models()
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'success': False, 'error': '评论不存在'}), 404
    data = request.get_json(silent=True) or {}
    emoji = data.get('emoji')
    if not emoji:
        return jsonify({'success': False, 'error': 'emoji 必填'}), 400
    import json as _json
    current_user_id = int(get_jwt_identity())
    reactions = {}
    if comment.reactions:
        try:
            reactions = _json.loads(comment.reactions) or {}
        except Exception:
            reactions = {}
    user_list = reactions.get(emoji, [])
    if current_user_id in user_list:
        user_list.remove(current_user_id)
    else:
        user_list.append(current_user_id)
    if user_list:
        reactions[emoji] = user_list
    elif emoji in reactions:
        del reactions[emoji]
    comment.reactions = _json.dumps(reactions, ensure_ascii=False)
    comment.updated_at = datetime.utcnow()
    db = get_db()
    db.session.commit()
    return jsonify({'success': True, 'reactions': reactions})


# ---------- 附件 ----------

@rd_kanban_bp.route('/<int:item_id>/attachments', methods=['GET'])
@jwt_required()
def list_attachments(item_id):
    item = _get_item_or_404(item_id)
    if not item:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404
    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    err = _check_item_access(item, current_user_id, current_user.role)
    if err:
        return err
    _, _, Attachment = _get_models()
    atts = Attachment.query.filter_by(item_id=item_id).order_by(Attachment.uploaded_at.desc()).all()
    user_ids = {a.uploaded_by for a in atts if a.uploaded_by}
    users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    user_dict = {u.id: u for u in users}
    return jsonify({
        'success': True,
        'attachments': [_serialize_attachment(a, user_dict) for a in atts]
    })


@rd_kanban_bp.route('/<int:item_id>/attachments', methods=['POST'])
@jwt_required()
def upload_attachment(item_id):
    item = _get_item_or_404(item_id)
    if not item:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有上传文件'}), 400
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': '文件为空'}), 400
    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    err = _check_item_access(item, current_user_id, current_user.role)
    if err:
        return err

    # 限制 20MB
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > 20 * 1024 * 1024:
        return jsonify({'success': False, 'error': '文件大小不能超过 20MB'}), 400

    original_name = file.filename
    safe_name = secure_filename(original_name) or 'file'
    # 唯一文件名：item_id_timestamp_safe_name
    stored_name = f"item{item_id}_{int(datetime.utcnow().timestamp() * 1000)}_{safe_name}"
    target_dir = os.path.join(RD_ATTACHMENT_DIR, str(item_id))
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, stored_name)
    file.save(file_path)

    _, _, Attachment = _get_models()
    att = Attachment(
        item_id=item_id,
        original_name=original_name,
        stored_name=stored_name,
        file_path=file_path,
        file_size=size,
        mime_type=file.mimetype,
        uploaded_by=current_user_id,
        uploaded_at=datetime.utcnow(),
    )
    db = get_db()
    db.session.add(att)
    db.session.commit()
    return jsonify({'success': True, 'attachment': _serialize_attachment(att, {current_user_id: current_user})})


@rd_kanban_bp.route('/attachments/<int:att_id>/download', methods=['GET'])
@jwt_required()
def download_attachment(att_id):
    _, _, Attachment = _get_models()
    att = Attachment.query.get(att_id)
    if not att:
        return jsonify({'success': False, 'error': '附件不存在'}), 404
    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    # 附件无 project_id，先查所属 item 再校验
    Item, _, _ = _get_models()
    parent_item = Item.query.get(att.item_id)
    if not parent_item:
        return jsonify({'success': False, 'error': '所属卡片不存在'}), 404
    err = _check_item_access(parent_item, current_user_id, current_user.role)
    if err:
        return err
    if not os.path.exists(att.file_path):
        return jsonify({'success': False, 'error': '文件不存在'}), 404
    return send_from_directory(
        os.path.dirname(att.file_path),
        att.stored_name,
        as_attachment=True,
        download_name=att.original_name,
    )


# 纯文本附件预览用：返回原始文本内容（不走 attachment），限制最大 5MB
_PREVIEW_TEXT_MAX_BYTES = 5 * 1024 * 1024
_PREVIEW_TEXT_EXTENSIONS = {
    '.txt', '.md', '.markdown', '.log',
    '.json', '.csv', '.tsv',
    '.xml', '.html', '.htm', '.css', '.js', '.ts',
    '.yaml', '.yml', '.ini', '.conf', '.cfg', '.env',
    '.sh', '.bat', '.ps1', '.sql', '.py', '.java',
}


@rd_kanban_bp.route('/attachments/<int:att_id>/raw', methods=['GET'])
@jwt_required()
def preview_attachment_raw(att_id):
    """纯文本附件预览：返回文本内容 + 元信息（mime / 行数等）"""
    _, _, Attachment = _get_models()
    att = Attachment.query.get(att_id)
    if not att:
        return jsonify({'success': False, 'error': '附件不存在'}), 404
    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    Item, _, _ = _get_models()
    parent_item = Item.query.get(att.item_id)
    if not parent_item:
        return jsonify({'success': False, 'error': '所属卡片不存在'}), 404
    err = _check_item_access(parent_item, current_user_id, current_user.role)
    if err:
        return err
    if not os.path.exists(att.file_path):
        return jsonify({'success': False, 'error': '文件不存在'}), 404
    # 仅允许白名单后缀
    _, ext = os.path.splitext(att.original_name or '')
    ext = ext.lower()
    if ext not in _PREVIEW_TEXT_EXTENSIONS:
        return jsonify({'success': False, 'error': f'该类型文件不支持在线预览（{ext}）'}), 400
    # 大小限制
    size = os.path.getsize(att.file_path)
    truncated = False
    read_bytes = min(size, _PREVIEW_TEXT_MAX_BYTES)
    try:
        with open(att.file_path, 'rb') as f:
            raw = f.read(read_bytes)
        # 尝试 utf-8 解码，失败回退 gbk（常见中文编码），再失败用 replace
        try:
            text = raw.decode('utf-8')
            encoding = 'utf-8'
        except UnicodeDecodeError:
            try:
                text = raw.decode('gbk')
                encoding = 'gbk'
            except UnicodeDecodeError:
                text = raw.decode('utf-8', errors='replace')
                encoding = 'utf-8'
    except Exception as e:
        return jsonify({'success': False, 'error': f'读取失败：{e}'}), 500
    if size > _PREVIEW_TEXT_MAX_BYTES:
        truncated = True
        text += f'\n\n... (文件过大，仅显示前 {_PREVIEW_TEXT_MAX_BYTES // 1024 // 1024} MB，已截断)'
    return jsonify({
        'success': True,
        'content': text,
        'encoding': encoding,
        'size': size,
        'truncated': truncated,
        'original_name': att.original_name,
        'line_count': text.count('\n') + (0 if text.endswith('\n') else 1),
    })


@rd_kanban_bp.route('/attachments/<int:att_id>', methods=['DELETE'])
@jwt_required()
def delete_attachment(att_id):
    _, _, Attachment = _get_models()
    att = Attachment.query.get(att_id)
    if not att:
        return jsonify({'success': False, 'error': '附件不存在'}), 404
    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    # 校验项目访问
    Item, _, _ = _get_models()
    parent_item = Item.query.get(att.item_id)
    if not parent_item:
        return jsonify({'success': False, 'error': '所属卡片不存在'}), 404
    err = _check_item_access(parent_item, current_user_id, current_user.role)
    if err:
        return err
    if current_user.role != 'admin' and att.uploaded_by != current_user_id:
        return jsonify({'success': False, 'error': '无权删除此附件'}), 403
    # 物理删除
    try:
        if att.file_path and os.path.exists(att.file_path):
            os.remove(att.file_path)
    except Exception:
        pass
    db = get_db()
    db.session.delete(att)
    db.session.commit()
    return jsonify({'success': True})


# ---------- 详情聚合 ----------

@rd_kanban_bp.route('/<int:item_id>/detail', methods=['GET'])
@jwt_required()
def get_card_detail(item_id):
    """聚合返回卡片详情：item + comments + attachments"""
    item = _get_item_or_404(item_id)
    if not item:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404
    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    err = _check_item_access(item, current_user_id, current_user.role)
    if err:
        return err

    Item, Comment, Attachment = _get_models()
    comments = Comment.query.filter_by(item_id=item_id).order_by(Comment.created_at.desc()).all()
    atts = Attachment.query.filter_by(item_id=item_id).order_by(Attachment.uploaded_at.desc()).all()
    user_ids = {c.user_id for c in comments if c.user_id}
    user_ids.update(a.uploaded_by for a in atts if a.uploaded_by)
    user_ids.add(item.assignee_id)
    user_ids.add(item.created_by)
    users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    user_dict = {u.id: u for u in users}
    return jsonify({
        'success': True,
        'item': _serialize_item(item, user_dict),
        'comments': [_serialize_comment(c, user_dict) for c in comments],
        'attachments': [_serialize_attachment(a, user_dict) for a in atts],
    })


# ============================================================
# 统计 / 周报汇总 / 客户问题跟踪
# ============================================================

@rd_kanban_bp.route('/<int:project_id>/stats', methods=['GET'])
@jwt_required()
def get_project_stats(project_id):
    """项目 Kanban 整体统计：每列数量、按指派人分组、按状态分组、逾期客户问题"""
    db = get_db()
    _, User, _, _ = get_models()
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'success': False, 'error': '用户不存在'}), 401

    project, err = _check_project_access(project_id, current_user_id, current_user.role)
    if err:
        return err

    Item, _, _ = _get_models()
    items = Item.query.filter_by(project_id=project_id).all()

    # 各列数量
    by_column = {c['key']: 0 for c in COLUMNS}
    for it in items:
        if it.column in by_column:
            by_column[it.column] += 1

    # 按指派人
    by_assignee = {}
    for it in items:
        if it.assignee_id:
            by_assignee[it.assignee_id] = by_assignee.get(it.assignee_id, 0) + 1

    # 按状态
    by_status = {}
    for it in items:
        if it.status:
            by_status[it.status] = by_status.get(it.status, 0) + 1

    # 逾期客户问题
    now = datetime.utcnow()
    overdue_issues = []
    open_issues_by_severity = {s['value']: 0 for s in ISSUE_SEVERITY}
    for it in items:
        if it.column == 'customer_issue' and not it.resolved_at:
            if it.severity in open_issues_by_severity:
                open_issues_by_severity[it.severity] += 1
            if it.due_at and it.due_at < now:
                overdue_issues.append({
                    'id': it.id,
                    'title': it.title,
                    'severity': it.severity,
                    'due_at': it.due_at.isoformat(),
                    'overdue_hours': int((now - it.due_at).total_seconds() // 3600),
                })

    # 解析指派人
    assignee_ids = list(by_assignee.keys())
    users = User.query.filter(User.id.in_(assignee_ids)).all() if assignee_ids else []
    assignee_list = [
        {
            'id': u.id,
            'name': (u.first_name or '') + (u.last_name or '') or u.username,
            'count': by_assignee.get(u.id, 0),
        }
        for u in users
    ]
    assignee_list.sort(key=lambda x: -x['count'])

    return jsonify({
        'success': True,
        'project_id': project_id,
        'total': len(items),
        'by_column': by_column,
        'by_status': by_status,
        'by_assignee': assignee_list,
        'open_issues': {
            'total': sum(open_issues_by_severity.values()),
            'by_severity': open_issues_by_severity,
            'overdue': overdue_issues,
        },
    })


@rd_kanban_bp.route('/<int:project_id>/weekly-summary', methods=['GET'])
@jwt_required()
def get_weekly_summary(project_id):
    """自动汇总周报列卡片为 Markdown

    可选 query: days（默认 7）
    将周报列标题按时间排序后拼接成 Markdown 文档。
    """
    db = get_db()
    _, User, _, _ = get_models()
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'success': False, 'error': '用户不存在'}), 401

    project, err = _check_project_access(project_id, current_user_id, current_user.role)
    if err:
        return err

    try:
        days = int(request.args.get('days', 7))
    except (TypeError, ValueError):
        days = 7
    days = max(1, min(days, 90))

    Item, _, _ = _get_models()
    since = datetime.utcnow() - timedelta(days=days)
    reports = Item.query.filter(
        Item.project_id == project_id,
        Item.column == 'weekly_report',
        Item.created_at >= since,
    ).order_by(Item.is_pinned.desc(), Item.created_at.desc()).all()

    # 解析指派人
    user_ids = {it.assignee_id for it in reports if it.assignee_id}
    user_ids.add(current_user_id)
    users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    user_dict = {u.id: u for u in users}

    # 生成 Markdown
    lines = [f'# {project.name} - 近 {days} 天周报汇总', '']
    lines.append(f'> 生成时间: {datetime.utcnow().strftime("%Y-%m-%d %H:%M")} UTC')
    lines.append(f'> 条目数: {len(reports)}')
    lines.append('')
    if not reports:
        lines.append('_本周暂无周报。_')
    else:
        for r in reports:
            pin = '📌 ' if r.is_pinned else ''
            assignee_name = ''
            if r.assignee_id and r.assignee_id in user_dict:
                u = user_dict[r.assignee_id]
                assignee_name = (u.first_name or '') + (u.last_name or '') or u.username
            date_str = r.created_at.strftime('%Y-%m-%d') if r.created_at else ''
            lines.append(f'## {pin}{date_str} - {assignee_name or "未指派"}')
            lines.append('')
            lines.append(r.title)
            lines.append('')
            if r.status:
                status_label = next((s['label'] for s in STATUS_OPTIONS if s['value'] == r.status), r.status)
                lines.append(f'**状态**: {status_label}')
            if r.tags:
                import json as _json
                try:
                    tags = _json.loads(r.tags) or []
                    if tags:
                        lines.append('**标签**: ' + ' '.join([f'`{t}`' for t in tags]))
                except Exception:
                    pass
            lines.append('')

    markdown = '\n'.join(lines)
    return jsonify({
        'success': True,
        'project_id': project_id,
        'days': days,
        'count': len(reports),
        'markdown': markdown,
        'items': [_serialize_item(r, user_dict) for r in reports],
    })


@rd_kanban_bp.route('/<int:project_id>/issue-stats', methods=['GET'])
@jwt_required()
def get_issue_stats(project_id):
    """客户问题 SLA 概览：按严重度、解决率、平均解决时长"""
    db = get_db()
    _, User, _, _ = get_models()
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'success': False, 'error': '用户不存在'}), 401

    project, err = _check_project_access(project_id, current_user_id, current_user.role)
    if err:
        return err

    Item, _, _ = _get_models()
    issues = Item.query.filter_by(project_id=project_id, column='customer_issue').all()

    now = datetime.utcnow()
    by_severity = {s['value']: {'open': 0, 'resolved': 0, 'overdue': 0, 'sla_hours': ISSUE_SLA_HOURS[s['value']]} for s in ISSUE_SEVERITY}
    total_resolved_hours = 0.0
    resolved_count = 0
    in_24h_resolved = 0  # 24 小时内解决数
    for it in issues:
        sev = it.severity if it.severity in by_severity else None
        if not sev:
            continue
        if it.resolved_at:
            by_severity[sev]['resolved'] += 1
            hours = (it.resolved_at - it.created_at).total_seconds() / 3600
            total_resolved_hours += hours
            resolved_count += 1
            if hours <= 24:
                in_24h_resolved += 1
        else:
            by_severity[sev]['open'] += 1
            if it.due_at and it.due_at < now:
                by_severity[sev]['overdue'] += 1

    avg_resolve_hours = round(total_resolved_hours / resolved_count, 2) if resolved_count else 0
    total = len(issues)
    return jsonify({
        'success': True,
        'project_id': project_id,
        'total': total,
        'open': sum(s['open'] for s in by_severity.values()),
        'resolved': sum(s['resolved'] for s in by_severity.values()),
        'overdue': sum(s['overdue'] for s in by_severity.values()),
        'avg_resolve_hours': avg_resolve_hours,
        'in_24h_resolved': in_24h_resolved,
        'by_severity': by_severity,
    })


@rd_kanban_bp.route('/<int:item_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_issue(item_id):
    """标记客户问题为已解决：记录 resolved_at，若在 SLA 内则视为及时"""
    Item, _, _ = _get_models()
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404
    if item.column != 'customer_issue':
        return jsonify({'success': False, 'error': '仅客户问题卡片可标记解决'}), 400

    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    err = _check_item_access(item, current_user_id, current_user.role)
    if err:
        return err

    if not item.resolved_at:
        item.resolved_at = datetime.utcnow()
        item.updated_at = item.resolved_at
        db = get_db()
        db.session.commit()
    return jsonify({
        'success': True,
        'item': _serialize_item(item),
        'within_sla': bool(item.due_at and item.resolved_at <= item.due_at),
    })


@rd_kanban_bp.route('/<int:item_id>/reopen', methods=['POST'])
@jwt_required()
def reopen_issue(item_id):
    """重新打开已解决的客户问题：清空 resolved_at"""
    Item, _, _ = _get_models()
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'success': False, 'error': '卡片不存在'}), 404
    if item.column != 'customer_issue':
        return jsonify({'success': False, 'error': '仅客户问题卡片可重开'}), 400

    import enhanced_app
    User = enhanced_app.User
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    err = _check_item_access(item, current_user_id, current_user.role)
    if err:
        return err

    item.resolved_at = None
    item.updated_at = datetime.utcnow()
    db = get_db()
    db.session.commit()
    return jsonify({'success': True, 'item': _serialize_item(item)})

