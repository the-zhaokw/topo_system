"""
工作日志API - 个人工作台计划功能
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from utils.time_utils import now_china
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
    - 项目日志视图（传入project_id）：显示该项目下所有人的日志
    - 个人工作日志视图（不传project_id）：只显示当前登录用户的日志
    - 部门经理：可查看本部门所有员工的日志
    """
    User, Activity, WorkLog, db = get_models()
    from enhanced_app import ProjectLog

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

    is_department_manager = user_role == 'department_manager' if user_role else False

    if project_id:
        # === 项目日志视图：显示该项目下所有人的日志 ===
        work_query = WorkLog.query.filter(WorkLog.project_id == project_id)
    elif is_department_manager:
        # === 部门经理个人视图：本部门所有员工的日志 ===
        department_users = User.query.filter_by(department=current_user.department).with_entities(User.id).all()
        department_user_ids = [u.id for u in department_users]
        if user_id and user_id in department_user_ids:
            work_query = WorkLog.query.filter(WorkLog.user_id == user_id)
        else:
            work_query = WorkLog.query.filter(WorkLog.user_id.in_(department_user_ids))
    else:
        # === 个人工作日志视图：只显示当前登录用户的 ===
        work_query = WorkLog.query.filter(WorkLog.user_id == int(current_user_id))

    if log_date:
        work_query = work_query.filter(WorkLog.log_date >= datetime.fromisoformat(log_date))
    if work_type:
        work_query = work_query.filter(WorkLog.work_type == work_type)
    if status:
        work_query = work_query.filter(WorkLog.status == status)

    work_logs = work_query.order_by(WorkLog.log_date.desc(), WorkLog.created_at.desc()).all()
    all_logs = []
    for log in work_logs:
        log_dict = log.to_dict()
        log_dict['log_source'] = 'work_log'
        all_logs.append(log_dict)

    # === 查询项目日志（合并显示） ===
    if project_id:
        # 项目日志视图：显示该项目的所有项目日志
        project_query = ProjectLog.query.filter(ProjectLog.project_id == project_id)
    else:
        # 个人工作日志视图：只显示当前登录用户的项目日志
        project_query = ProjectLog.query.filter(ProjectLog.created_by == int(current_user_id))

    if log_date:
        project_query = project_query.filter(ProjectLog.logged_at >= datetime.fromisoformat(log_date))
    if work_type:
        project_query = project_query.filter(ProjectLog.log_type == work_type)
    if status:
        if status == 'completed':
            project_query = project_query.filter(ProjectLog.status.in_(['published', 'archived']))
        elif status == 'draft':
            project_query = project_query.filter(ProjectLog.status == 'draft')

    project_logs = project_query.order_by(ProjectLog.created_at.desc()).all()
    for log in project_logs:
        log_dict = log.to_dict()
        log_dict['log_source'] = 'project_log'
        log_dict['project_log_id'] = log.id
        log_dict['user_id'] = log.created_by
        log_dict['user_name'] = log_dict.get('creator_name', '')
        log_dict['log_date'] = log.logged_at.isoformat() if log.logged_at else (log.created_at.isoformat() if log.created_at else None)
        log_dict['work_type'] = log.log_type
        log_dict['hours_spent'] = 0
        if log.status in ('published', 'archived'):
            log_dict['status'] = 'completed'
        all_logs.append(log_dict)

    # 合并后按日期和创建时间排序
    all_logs.sort(key=lambda x: (x.get('log_date') or '', x.get('created_at') or ''), reverse=True)

    # 内存分页
    total = len(all_logs)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_logs = all_logs[start:end]

    return jsonify({
        'logs': paginated_logs,
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page if per_page > 0 else 1,
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

    work_log.updated_at = now_china()

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
    - 项目日志视图（传入project_id）：统计该项目下所有人的日志
    - 个人工作日志视图（不传project_id）：只统计当前登录用户的日志
    - 部门经理：可查看本部门所有员工日志的统计
    """
    User, Activity, WorkLog, db = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None
    project_id = request.args.get('project_id', type=int)
    user_id = request.args.get('user_id', type=int)

    is_department_manager = user_role == 'department_manager' if user_role else False

    if project_id:
        # === 项目日志视图：统计该项目下所有人的日志 ===
        query_filter = WorkLog.query.filter(WorkLog.project_id == project_id)
        total_logs = query_filter.count()
        draft_logs = query_filter.filter(WorkLog.status == 'draft').count()
        completed_logs = query_filter.filter(WorkLog.status == 'completed').count()
        total_hours = db.session.query(db.func.sum(WorkLog.hours_spent)).filter(
            WorkLog.project_id == project_id
        ).scalar() or 0
    elif is_department_manager:
        # === 部门经理个人视图 ===
        department_users = User.query.filter_by(department=current_user.department).with_entities(User.id).all()
        department_user_ids = [u.id for u in department_users]
        if user_id and user_id in department_user_ids:
            query_filter = WorkLog.query.filter(WorkLog.user_id == user_id)
        else:
            query_filter = WorkLog.query.filter(WorkLog.user_id.in_(department_user_ids))
        total_logs = query_filter.count()
        draft_logs = query_filter.filter(WorkLog.status == 'draft').count()
        completed_logs = query_filter.filter(WorkLog.status == 'completed').count()
        hours_query = db.session.query(db.func.sum(WorkLog.hours_spent)).filter(
            WorkLog.user_id.in_(department_user_ids) if not (user_id and user_id in department_user_ids) else WorkLog.user_id == user_id
        )
        total_hours = hours_query.scalar() or 0
    else:
        # === 个人工作日志视图：只统计当前登录用户的 ===
        query_filter = WorkLog.query.filter(WorkLog.user_id == int(current_user_id))
        total_logs = query_filter.count()
        draft_logs = query_filter.filter(WorkLog.status == 'draft').count()
        completed_logs = query_filter.filter(WorkLog.status == 'completed').count()
        total_hours = db.session.query(db.func.sum(WorkLog.hours_spent)).filter(
            WorkLog.user_id == int(current_user_id)
        ).scalar() or 0

    # === 合并项目日志统计 ===
    from enhanced_app import ProjectLog
    if project_id:
        p_query = ProjectLog.query.filter(ProjectLog.project_id == project_id)
    else:
        p_query = ProjectLog.query.filter(ProjectLog.created_by == int(current_user_id))

    total_logs += p_query.count()
    draft_logs += p_query.filter(ProjectLog.status == 'draft').count()
    completed_logs += p_query.filter(ProjectLog.status.in_(['published', 'archived'])).count()

    return jsonify({
        'total_logs': total_logs,
        'draft_logs': draft_logs,
        'completed_logs': completed_logs,
        'total_hours': float(total_hours)
    }), 200