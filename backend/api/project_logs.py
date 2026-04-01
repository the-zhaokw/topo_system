"""
项目日志管理 API
支持项目日志的 CRUD 操作
对于项目经理和经理、超级管理员，可以看到项目关联的所有日志
其他用户，只能看到自己创建的日志
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json

project_logs_bp = Blueprint('project_logs', __name__, url_prefix='/project-logs')

def get_models():
    from enhanced_app import User, Project, ProjectMember, ProjectLog, ProjectLogStatus, ProjectLogType, db, Activity, create_audit_log
    return User, Project, ProjectMember, ProjectLog, ProjectLogStatus, ProjectLogType, db, Activity, create_audit_log

def check_project_access(project_id, user_id, user_role):
    """检查用户对项目的访问权限"""
    User, Project, ProjectMember, ProjectLog, ProjectLogStatus, ProjectLogType, db, Activity, create_audit_log = get_models()

    if user_role in ['admin', 'manager']:
        return True

    project = Project.query.get(project_id)
    if not project:
        return False

    if user_role == 'project_manager' and project.manager_id == user_id:
        return True

    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    return member is not None

@project_logs_bp.route('/', methods=['GET'])
@jwt_required()
def get_logs():
    """获取项目日志列表"""
    User, Project, ProjectMember, ProjectLog, ProjectLogStatus, ProjectLogType, db, Activity, create_audit_log = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None

    project_id = request.args.get('project_id', type=int)
    log_type = request.args.get('log_type')
    status = request.args.get('status')
    created_by = request.args.get('created_by', type=int)
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')

    if not project_id:
        return jsonify({'success': False, 'message': '项目ID不能为空', 'data': None}), 400

    has_full_access = check_project_access(project_id, current_user_id, user_role)

    query = ProjectLog.query.filter_by(project_id=project_id)

    if not has_full_access:
        query = query.filter_by(created_by=current_user_id)

    if log_type:
        query = query.filter_by(log_type=log_type)
    if status:
        query = query.filter_by(status=status)
    if created_by and has_full_access:
        query = query.filter_by(created_by=created_by)
    if search:
        query = query.filter(
            db.or_(
                ProjectLog.title.contains(search),
                ProjectLog.content.contains(search)
            )
        )

    sort_column = getattr(ProjectLog, sort, ProjectLog.created_at)
    if order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items

    log_list = []
    for log in logs:
        log_dict = log.to_dict()
        if log.creator:
            log_dict['creator_name'] = f'{log.creator.first_name or ""} {log.creator.last_name or ""}'.strip() or log.creator.username
        else:
            log_dict['creator_name'] = '未知'
        log_list.append(log_dict)

    return jsonify({
        'success': True,
        'message': '获取日志列表成功',
        'data': {
            'logs': log_list,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })

@project_logs_bp.route('/<int:log_id>', methods=['GET'])
@jwt_required()
def get_log(log_id):
    """获取单个日志详情"""
    User, Project, ProjectMember, ProjectLog, ProjectLogStatus, ProjectLogType, db, Activity, create_audit_log = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None

    log = ProjectLog.query.get(log_id)
    if not log:
        return jsonify({'success': False, 'message': '日志不存在', 'data': None}), 404

    has_full_access = check_project_access(log.project_id, current_user_id, user_role)
    if not has_full_access and log.created_by != current_user_id:
        return jsonify({'success': False, 'message': '无权查看此日志', 'data': None}), 403

    log_dict = log.to_dict()
    if log.creator:
        log_dict['creator_name'] = f'{log.creator.first_name or ""} {log.creator.last_name or ""}'.strip() or log.creator.username
    else:
        log_dict['creator_name'] = '未知'

    return jsonify({
        'success': True,
        'message': '获取日志详情成功',
        'data': {'log': log_dict}
    })

@project_logs_bp.route('/', methods=['POST'])
@jwt_required()
def create_log():
    """创建项目日志"""
    User, Project, ProjectMember, ProjectLog, ProjectLogStatus, ProjectLogType, db, Activity, create_audit_log = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据不能为空', 'data': None}), 400

    required_fields = ['title', 'content', 'project_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'{field} 字段为必填项', 'data': None}), 400

    project = Project.query.get(data['project_id'])
    if not project:
        return jsonify({'success': False, 'message': '指定的项目不存在', 'data': None}), 404

    if not check_project_access(data['project_id'], current_user_id, user_role):
        return jsonify({'success': False, 'message': '无权在此项目中创建日志', 'data': None}), 403

    log_type = data.get('log_type', 'general')
    valid_log_types = [lt.value for lt in ProjectLogType]
    if log_type not in valid_log_types:
        log_type = 'general'

    status = data.get('status', 'draft')
    valid_statuses = [ls.value for ls in ProjectLogStatus]
    if status not in valid_statuses:
        status = 'draft'

    logged_at = None
    if data.get('logged_at'):
        try:
            logged_at = datetime.fromisoformat(data['logged_at'].replace('Z', '+00:00'))
        except ValueError:
            try:
                logged_at = datetime.strptime(data['logged_at'], '%Y-%m-%d')
            except ValueError:
                logged_at = None

    start_date = None
    if data.get('start_date'):
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        except ValueError:
            start_date = None

    end_date = None
    if data.get('end_date'):
        try:
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            end_date = None

    try:
        log = ProjectLog(
            project_id=data['project_id'],
            title=data['title'],
            content=data['content'],
            log_type=log_type,
            status=status,
            created_by=int(current_user_id),
            logged_at=logged_at or datetime.utcnow(),
            start_date=start_date,
            end_date=end_date
        )

        db.session.add(log)
        db.session.commit()

        activity = Activity(
            action='create_project_log',
            description=f'创建项目日志: {log.title}',
            performed_by=int(current_user_id),
            target_type='project_log',
            target_id=log.id
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '日志创建成功',
            'data': {'log': log.to_dict()}
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建日志失败: {str(e)}', 'data': None}), 500

@project_logs_bp.route('/<int:log_id>', methods=['PUT'])
@jwt_required()
def update_log(log_id):
    """更新项目日志"""
    User, Project, ProjectMember, ProjectLog, ProjectLogStatus, ProjectLogType, db, Activity, create_audit_log = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据不能为空', 'data': None}), 400

    log = ProjectLog.query.get(log_id)
    if not log:
        return jsonify({'success': False, 'message': '日志不存在', 'data': None}), 404

    has_full_access = check_project_access(log.project_id, current_user_id, user_role)

    if not has_full_access and log.created_by != current_user_id:
        return jsonify({'success': False, 'message': '无权更新此日志', 'data': None}), 403

    field_changes = []

    if 'title' in data and data['title'] != log.title:
        field_changes.append({'field': 'title', 'old_value': log.title, 'new_value': data['title']})
        log.title = data['title']

    if 'content' in data and data['content'] != log.content:
        field_changes.append({'field': 'content', 'old_value': log.content, 'new_value': data['content']})
        log.content = data['content']

    if 'log_type' in data:
        valid_log_types = [lt.value for lt in ProjectLogType]
        if data['log_type'] in valid_log_types and data['log_type'] != log.log_type:
            field_changes.append({'field': 'log_type', 'old_value': log.log_type, 'new_value': data['log_type']})
            log.log_type = data['log_type']

    if 'status' in data:
        valid_statuses = [ls.value for ls in ProjectLogStatus]
        if data['status'] in valid_statuses and data['status'] != log.status:
            field_changes.append({'field': 'status', 'old_value': log.status, 'new_value': data['status']})
            log.status = data['status']

    if 'logged_at' in data and data['logged_at']:
        try:
            new_logged_at = datetime.fromisoformat(data['logged_at'].replace('Z', '+00:00'))
            if new_logged_at != log.logged_at:
                field_changes.append({
                    'field': 'logged_at',
                    'old_value': log.logged_at.isoformat() if log.logged_at else None,
                    'new_value': new_logged_at.isoformat()
                })
                log.logged_at = new_logged_at
        except ValueError:
            try:
                new_logged_at = datetime.strptime(data['logged_at'], '%Y-%m-%d')
                if new_logged_at != log.logged_at:
                    field_changes.append({
                        'field': 'logged_at',
                        'old_value': log.logged_at.isoformat() if log.logged_at else None,
                        'new_value': new_logged_at.isoformat()
                    })
                    log.logged_at = new_logged_at
            except ValueError:
                pass

    if 'start_date' in data:
        try:
            new_start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data['start_date'] else None
            if new_start_date != log.start_date:
                field_changes.append({
                    'field': 'start_date',
                    'old_value': log.start_date.isoformat() if log.start_date else None,
                    'new_value': data['start_date']
                })
                log.start_date = new_start_date
        except ValueError:
            pass

    if 'end_date' in data:
        try:
            new_end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data['end_date'] else None
            if new_end_date != log.end_date:
                field_changes.append({
                    'field': 'end_date',
                    'old_value': log.end_date.isoformat() if log.end_date else None,
                    'new_value': data['end_date']
                })
                log.end_date = new_end_date
        except ValueError:
            pass

    log.updated_at = datetime.utcnow()

    try:
        db.session.commit()

        if field_changes:
            activity = Activity(
                action='update_project_log',
                description=f'更新项目日志: {log.title}',
                performed_by=int(current_user_id),
                target_type='project_log',
                target_id=log.id,
                field_changes=json.dumps(field_changes, ensure_ascii=False)
            )
            db.session.add(activity)
            db.session.commit()

        return jsonify({
            'success': True,
            'message': '日志更新成功',
            'data': {'log': log.to_dict()}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新日志失败: {str(e)}', 'data': None}), 500

@project_logs_bp.route('/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_log(log_id):
    """删除项目日志"""
    User, Project, ProjectMember, ProjectLog, ProjectLogStatus, ProjectLogType, db, Activity, create_audit_log = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None

    log = ProjectLog.query.get(log_id)
    if not log:
        return jsonify({'success': False, 'message': '日志不存在', 'data': None}), 404

    has_full_access = check_project_access(log.project_id, current_user_id, user_role)

    if not has_full_access and log.created_by != current_user_id:
        return jsonify({'success': False, 'message': '无权删除此日志', 'data': None}), 403

    try:
        log_title = log.title
        db.session.delete(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '日志删除成功',
            'data': None
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除日志失败: {str(e)}', 'data': None}), 500

@project_logs_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_log_stats():
    """获取项目日志统计"""
    User, Project, ProjectMember, ProjectLog, ProjectLogStatus, ProjectLogType, db, Activity, create_audit_log = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    user_role = current_user.role if current_user else None

    project_id = request.args.get('project_id', type=int)

    if not project_id:
        return jsonify({'success': False, 'message': '项目ID不能为空', 'data': None}), 400

    has_full_access = check_project_access(project_id, current_user_id, user_role)

    query = ProjectLog.query.filter_by(project_id=project_id)

    if not has_full_access:
        query = query.filter_by(created_by=current_user_id)

    total_count = query.count()
    draft_count = query.filter_by(status='draft').count()
    published_count = query.filter_by(status='published').count()
    archived_count = query.filter_by(status='archived').count()

    type_stats = {}
    for lt in ProjectLogType:
        count = query.filter_by(log_type=lt.value).count()
        type_stats[lt.value] = count

    return jsonify({
        'success': True,
        'message': '获取统计成功',
        'data': {
            'total': total_count,
            'draft': draft_count,
            'published': published_count,
            'archived': archived_count,
            'by_type': type_stats
        }
    })