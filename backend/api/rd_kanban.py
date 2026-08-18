"""
项目研发管理 - Kanban 看板 API
每个项目一张看板，7 列布局：
  - recent_req_1      近期需求列表
  - recent_req_2      近期需求列表（备选/补充）
  - in_progress       正在开发列表
  - completed         完成列表
  - pending_test      待测试列表
  - weekly_report     周报列表
  - customer_issue    客户问题
每张卡片可编辑、可拖拽换列、可删除、可评论计数。
"""

from datetime import datetime
import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

rd_kanban_bp = Blueprint('rd_kanban', __name__, url_prefix='/rd-kanban')

# 列定义（顺序与前端一致）
COLUMNS = [
    {'key': 'recent_req_1', 'name': '近期需求列表', 'color': '#0ea5e9'},
    {'key': 'recent_req_2', 'name': '近期需求列表', 'color': '#0ea5e9'},
    {'key': 'in_progress', 'name': '正在开发列表', 'color': '#f59e0b'},
    {'key': 'completed', 'name': '完成列表', 'color': '#10b981'},
    {'key': 'pending_test', 'name': '待测试列表', 'color': '#8b5cf6'},
    {'key': 'weekly_report', 'name': '周报列表', 'color': '#ec4899'},
    {'key': 'customer_issue', 'name': '客户问题', 'color': '#ef4444'},
]
COLUMN_KEYS = [c['key'] for c in COLUMNS]
COLUMN_NAME_MAP = {c['key']: c['name'] for c in COLUMNS}

# 状态徽章选项
STATUS_OPTIONS = [
    {'value': 'in_progress', 'label': '正在备战中...', 'color': '#f59e0b'},
    {'value': 'paused', 'label': '暂停', 'color': '#94a3b8'},
    {'value': 'completed', 'label': '完成', 'color': '#10b981'},
    {'value': 'review', 'label': '评审中', 'color': '#3b82f6'},
]


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
    """获取某项目所有 Kanban 卡片"""
    db = get_db()
    _, User, Project, ProjectMember = get_models()
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'success': False, 'error': '用户不存在'}), 401

    project, err = _check_project_access(project_id, current_user_id, current_user.role)
    if err:
        return err

    # 动态创建表（如果不存在）
    try:
        db.create_all()
    except Exception:
        pass

    model = _get_model()
    items = model.query.filter_by(project_id=project_id).order_by(model.column, model.sort_order, model.id).all()

    # 批量加载用户
    user_ids = {it.assignee_id for it in items if it.assignee_id}
    user_ids.add(current_user_id)
    users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    user_dict = {u.id: u for u in users}

    return jsonify({
        'success': True,
        'columns': COLUMNS,
        'status_options': STATUS_OPTIONS,
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
