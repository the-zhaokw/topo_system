"""
工作日志API - 个人工作台计划功能
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json

work_logs_bp = Blueprint('work_logs', __name__, url_prefix='/work-logs')

def get_models():
    from enhanced_app import User, Activity, WorkLog, db
    return User, Activity, WorkLog, db

def log_activity(action, description, target_type, target_id, user_id):
    """记录活动日志"""
    from enhanced_app import Activity, db
    activity = Activity(
        action=action,
        description=description,
        performed_by=user_id,
        target_type=target_type,
        target_id=target_id
    )
    db.session.add(activity)
    db.session.commit()

@work_logs_bp.route('/', methods=['GET'])
@jwt_required()
def get_work_logs():
    """获取工作日志列表
    - 管理员/经理/项目经理：可以看到所有日志（可通过project_id过滤）
    - 部门经理：可以看到本部门所有员工的日志
    - 普通用户：只能看到自己的日志
    """
    User, Activity, WorkLog, db = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    log_date = request.args.get('log_date')
    work_type = request.args.get('work_type')
    status = request.args.get('status')
    project_id = request.args.get('project_id', type=int)
    user_id = request.args.get('user_id', type=int)

    has_full_access = user_role in ['admin', 'manager', 'project_manager'] if user_role else False
    is_department_manager = user_role == 'department_manager' if user_role else False

    if has_full_access and project_id:
        query = WorkLog.query.filter(WorkLog.project_id == project_id)
    elif has_full_access:
        query = WorkLog.query
    elif is_department_manager:
        department_users = User.query.filter_by(department=current_user.department).with_entities(User.id).all()
        department_user_ids = [u.id for u in department_users]
        if user_id and user_id in department_user_ids:
            query = WorkLog.query.filter(WorkLog.user_id == user_id)
        else:
            query = WorkLog.query.filter(WorkLog.user_id.in_(department_user_ids))
        if project_id:
            query = query.filter(WorkLog.project_id == project_id)
    else:
        query = WorkLog.query.filter(WorkLog.user_id == int(current_user_id))
        if project_id:
            query = query.filter(WorkLog.project_id == project_id)

    if log_date:
        query = query.filter(WorkLog.log_date >= datetime.fromisoformat(log_date))
    if work_type:
        query = query.filter(WorkLog.work_type == work_type)
    if status:
        query = query.filter(WorkLog.status == status)

    pagination = query.order_by(WorkLog.log_date.desc(), WorkLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    logs = []
    for log in pagination.items:
        log_dict = log.to_dict()
        logs.append(log_dict)

    return jsonify({
        'logs': logs,
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages,
        'per_page': per_page
    }), 200

@work_logs_bp.route('/<int:log_id>', methods=['GET'])
@jwt_required()
def get_work_log(log_id):
    """获取单个工作日志详情"""
    User, Activity, WorkLog, db = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None
    work_log = WorkLog.query.get(log_id)

    if not work_log:
        return jsonify({'error': '工作日志不存在'}), 404

    has_full_access = user_role in ['admin', 'manager', 'project_manager'] if user_role else False

    is_department_manager = user_role == 'department_manager' if user_role else False
    if is_department_manager:
        department_users = User.query.filter_by(department=current_user.department).with_entities(User.id).all()
        department_user_ids = [u.id for u in department_users]
        is_in_department = work_log.user_id in department_user_ids
    else:
        is_in_department = False

    if not has_full_access and not is_in_department and work_log.user_id != int(current_user_id):
        return jsonify({'error': '无权限查看此工作日志'}), 403

    return jsonify(work_log.to_dict()), 200

@work_logs_bp.route('/', methods=['POST'])
@jwt_required()
def create_work_log():
    """创建工作日志"""
    User, Activity, WorkLog, db = get_models()

    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('title'):
        return jsonify({'error': '标题不能为空'}), 400
    if not data.get('content'):
        return jsonify({'error': '内容不能为空'}), 400
    if not data.get('log_date'):
        return jsonify({'error': '日期不能为空'}), 400

    allowed_fields = {'title', 'content', 'log_date', 'work_type', 'project_id', 'hours_spent', 'status'}
    filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

    work_log = WorkLog(
        user_id=int(current_user_id),
        title=filtered_data.get('title'),
        content=filtered_data.get('content'),
        log_date=datetime.fromisoformat(filtered_data.get('log_date')),
        work_type=filtered_data.get('work_type', 'daily'),
        project_id=filtered_data.get('project_id'),
        hours_spent=filtered_data.get('hours_spent', 0.0),
        status=filtered_data.get('status', 'draft')
    )
    db.session.add(work_log)
    db.session.commit()

    log_activity('create', f'创建工作日志：{work_log.title}', 'work_log', work_log.id, int(current_user_id))

    return jsonify({
        'message': '工作日志创建成功',
        'log': work_log.to_dict()
    }), 201

@work_logs_bp.route('/<int:log_id>', methods=['PUT'])
@jwt_required()
def update_work_log(log_id):
    """更新工作日志"""
    User, Activity, WorkLog, db = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None
    data = request.get_json()

    work_log = WorkLog.query.get(log_id)

    if not work_log:
        return jsonify({'error': '工作日志不存在'}), 404

    has_full_access = user_role in ['admin', 'manager', 'project_manager'] if user_role else False

    is_department_manager = user_role == 'department_manager' if user_role else False
    if is_department_manager:
        department_users = User.query.filter_by(department=current_user.department).with_entities(User.id).all()
        department_user_ids = [u.id for u in department_users]
        is_in_department = work_log.user_id in department_user_ids
    else:
        is_in_department = False

    if not has_full_access and not is_in_department and work_log.user_id != int(current_user_id):
        return jsonify({'error': '无权限修改此工作日志'}), 403

    field_changes = []

    if 'title' in data and data['title'] != work_log.title:
        field_changes.append({'field': 'title', 'old_value': work_log.title, 'new_value': data['title']})
        work_log.title = data['title']

    if 'content' in data and data['content'] != work_log.content:
        field_changes.append({'field': 'content', 'old_value': work_log.content, 'new_value': data['content']})
        work_log.content = data['content']

    if 'log_date' in data:
        new_date = datetime.fromisoformat(data['log_date'])
        if new_date != work_log.log_date:
            field_changes.append({'field': 'log_date', 'old_value': work_log.log_date.isoformat(), 'new_value': data['log_date']})
            work_log.log_date = new_date

    if 'work_type' in data and data['work_type'] != work_log.work_type:
        field_changes.append({'field': 'work_type', 'old_value': work_log.work_type, 'new_value': data['work_type']})
        work_log.work_type = data['work_type']

    if 'project_id' in data:
        old_project = work_log.project_id
        new_project = data['project_id']
        if old_project != new_project:
            field_changes.append({'field': 'project_id', 'old_value': str(old_project) if old_project else None, 'new_value': str(new_project) if new_project else None})
            work_log.project_id = new_project

    if 'hours_spent' in data and data['hours_spent'] != work_log.hours_spent:
        field_changes.append({'field': 'hours_spent', 'old_value': work_log.hours_spent, 'new_value': data['hours_spent']})
        work_log.hours_spent = data['hours_spent']

    if 'status' in data and data['status'] != work_log.status:
        field_changes.append({'field': 'status', 'old_value': work_log.status, 'new_value': data['status']})
        work_log.status = data['status']

    work_log.updated_at = datetime.utcnow()

    db.session.commit()

    if field_changes:
        log_activity('update', f'更新工作日志：{work_log.title}', 'work_log', work_log.id, int(current_user_id))

    return jsonify({
        'message': '工作日志更新成功',
        'log': work_log.to_dict()
    }), 200

@work_logs_bp.route('/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_work_log(log_id):
    """删除工作日志"""
    User, Activity, WorkLog, db = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None
    work_log = WorkLog.query.get(log_id)

    if not work_log:
        return jsonify({'error': '工作日志不存在'}), 404

    has_full_access = user_role in ['admin', 'manager', 'project_manager'] if user_role else False

    is_department_manager = user_role == 'department_manager' if user_role else False
    if is_department_manager:
        department_users = User.query.filter_by(department=current_user.department).with_entities(User.id).all()
        department_user_ids = [u.id for u in department_users]
        is_in_department = work_log.user_id in department_user_ids
    else:
        is_in_department = False

    if not has_full_access and not is_in_department and work_log.user_id != int(current_user_id):
        return jsonify({'error': '无权限删除此工作日志'}), 403

    log_title = work_log.title
    db.session.delete(work_log)
    db.session.commit()

    log_activity('delete', f'删除工作日志：{log_title}', 'work_log', log_id, int(current_user_id))

    return jsonify({'message': '工作日志删除成功'}), 200

@work_logs_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_work_log_stats():
    """获取工作日志统计
    - 管理员/经理/项目经理：可以看到所有日志的统计（可通过project_id过滤）
    - 部门经理：可以看到本部门所有员工日志的统计
    - 普通用户：只能看到自己的日志统计
    """
    User, Activity, WorkLog, db = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None
    project_id = request.args.get('project_id', type=int)
    user_id = request.args.get('user_id', type=int)

    has_full_access = user_role in ['admin', 'manager', 'project_manager'] if user_role else False
    is_department_manager = user_role == 'department_manager' if user_role else False

    if has_full_access and project_id:
        total_logs = WorkLog.query.filter(WorkLog.project_id == project_id).count()
        draft_logs = WorkLog.query.filter(WorkLog.project_id == project_id, WorkLog.status == 'draft').count()
        completed_logs = WorkLog.query.filter(WorkLog.project_id == project_id, WorkLog.status == 'completed').count()
        total_hours = db.session.query(db.func.sum(WorkLog.hours_spent)).filter(
            WorkLog.project_id == project_id
        ).scalar() or 0
    elif has_full_access:
        total_logs = WorkLog.query.count()
        draft_logs = WorkLog.query.filter(WorkLog.status == 'draft').count()
        completed_logs = WorkLog.query.filter(WorkLog.status == 'completed').count()
        total_hours = db.session.query(db.func.sum(WorkLog.hours_spent)).scalar() or 0
    elif is_department_manager:
        department_users = User.query.filter_by(department=current_user.department).with_entities(User.id).all()
        department_user_ids = [u.id for u in department_users]
        if user_id and user_id in department_user_ids:
            query_filter = WorkLog.query.filter(WorkLog.user_id == user_id)
        else:
            query_filter = WorkLog.query.filter(WorkLog.user_id.in_(department_user_ids))
        if project_id:
            query_filter = query_filter.filter(WorkLog.project_id == project_id)
        total_logs = query_filter.count()
        draft_logs = query_filter.filter(WorkLog.status == 'draft').count()
        completed_logs = query_filter.filter(WorkLog.status == 'completed').count()
        hours_query = db.session.query(db.func.sum(WorkLog.hours_spent)).filter(
            WorkLog.user_id.in_(department_user_ids) if not (user_id and user_id in department_user_ids) else WorkLog.user_id == user_id
        )
        if project_id:
            hours_query = hours_query.filter(WorkLog.project_id == project_id)
        total_hours = hours_query.scalar() or 0
    else:
        query_filter = WorkLog.query.filter(WorkLog.user_id == int(current_user_id))
        if project_id:
            query_filter = query_filter.filter(WorkLog.project_id == project_id)
        total_logs = query_filter.count()
        draft_logs = query_filter.filter(WorkLog.status == 'draft').count()
        completed_logs = query_filter.filter(WorkLog.status == 'completed').count()
        hours_query = db.session.query(db.func.sum(WorkLog.hours_spent)).filter(
            WorkLog.user_id == int(current_user_id)
        )
        if project_id:
            hours_query = hours_query.filter(WorkLog.project_id == project_id)
        total_hours = hours_query.scalar() or 0

    return jsonify({
        'total_logs': total_logs,
        'draft_logs': draft_logs,
        'completed_logs': completed_logs,
        'total_hours': float(total_hours)
    }), 200