"""
活动记录API - 系统审计日志
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
import json
import re

# 创建活动记录蓝图
activities_bp = Blueprint('activities', __name__, url_prefix='/activities')

def get_models():
    from enhanced_app import User, Activity, Bug, Project, WorkLog, app, db
    return User, Activity, Bug, Project, WorkLog, app, db

# 获取活动记录统计
@activities_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取活动记录统计数据（全量，非当前页）"""
    User, Activity, Bug, Project, WorkLog, app, db = get_models()

    with app.app_context():
        total = db.session.query(func.count(Activity.id)).scalar() or 0
        create_count = db.session.query(func.count(Activity.id)).filter(
            Activity.action.like('%create%')
        ).scalar() or 0
        update_count = db.session.query(func.count(Activity.id)).filter(
            Activity.action.like('%update%')
        ).scalar() or 0
        delete_count = db.session.query(func.count(Activity.id)).filter(
            Activity.action.like('%delete%')
        ).scalar() or 0

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.session.query(func.count(Activity.id)).filter(
            Activity.created_at >= today_start
        ).scalar() or 0

        return jsonify({
            'total': total,
            'create_count': create_count,
            'update_count': update_count,
            'delete_count': delete_count,
            'today_count': today_count
        }), 200

# 获取活动记录列表
@activities_bp.route('/', methods=['GET'])
@jwt_required()
def get_activities():
    """获取活动记录列表"""
    User, Activity, Bug, Project, WorkLog, app, db = get_models()

    with app.app_context():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        resource_type = request.args.get('resource_type')
        action = request.args.get('action')
        user_name = request.args.get('user_name')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Activity.query

        if resource_type:
            query = query.filter(Activity.target_type == resource_type)

        if action:
            query = query.filter(Activity.action.like(f'%{action}%'))

        if user_name:
            query = query.join(User).filter(User.username.contains(user_name))

        if start_date:
            query = query.filter(Activity.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Activity.created_at <= datetime.fromisoformat(end_date))

        pagination = query.order_by(Activity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        activities = []
        for activity in pagination.items:
            activity_dict = {
                'id': activity.id,
                'action': activity.action,
                'description': activity.description,
                'target_type': activity.target_type,
                'target_id': activity.target_id,
                'resource_type': activity.target_type,
                'resource_id': activity.target_id,
                'user_id': activity.performed_by,
                'performed_by': activity.performed_by,
                'created_at': activity.created_at.isoformat() if activity.created_at else None,
                'field_changes': json.loads(activity.field_changes) if activity.field_changes else [],
                'resource_name': resolve_resource_name(activity),
            }

            performer = User.query.get(activity.performed_by)
            if performer:
                activity_dict['user_name'] = performer.username
                activity_dict['user_role'] = performer.role

            activities.append(activity_dict)

        return jsonify({
            'activities': activities,
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
            'per_page': per_page
        }), 200


def resolve_resource_name(activity):
    """根据 target_type 和 target_id 解析资源名称"""
    try:
        if activity.target_id == 0:
            return activity.description or '系统操作'

        target_type = activity.target_type
        target_id = activity.target_id

        if target_type == 'bug':
            from enhanced_app import Bug
            bug = Bug.query.get(target_id)
            return bug.title if bug else '缺陷已删除'
        elif target_type == 'project':
            from enhanced_app import Project
            project = Project.query.get(target_id)
            return project.name if project else '项目已删除'
        elif target_type == 'user':
            from enhanced_app import User
            user = User.query.get(target_id)
            return user.username if user else '用户已删除'
        elif target_type == 'work_log':
            from enhanced_app import WorkLog
            work_log = WorkLog.query.get(target_id)
            if work_log:
                return work_log.title
            match = re.search(r'工作日志[：:](.+)', activity.description)
            return match.group(1) if match else '工作日志已删除'
        elif target_type == 'project_log':
            from enhanced_app import ProjectLog
            log = ProjectLog.query.get(target_id)
            return log.title if log else '项目日志已删除'
        elif target_type == 'project_member':
            from enhanced_app import ProjectMember
            member = ProjectMember.query.get(target_id)
            if member:
                user = member.user
                return f'{user.username} (项目成员)' if user else '项目成员'
            return '项目成员'
        elif target_type == 'leave_application':
            from enhanced_app import LeaveApplication
            app_obj = LeaveApplication.query.get(target_id)
            if app_obj:
                return f'请假申请 #{app_obj.id}'
            return '请假申请'
        elif target_type == 'overtime_application':
            from enhanced_app import OvertimeApplication
            app_obj = OvertimeApplication.query.get(target_id)
            if app_obj:
                return f'加班申请 #{app_obj.id}'
            return '加班申请'
        elif target_type == 'attendance':
            from enhanced_app import AttendanceRecord
            record = AttendanceRecord.query.get(target_id)
            if record:
                return f'考勤记录 #{record.id}'
            return '考勤记录'
        elif target_type == 'shift_schedule':
            from enhanced_app import ShiftSchedule
            shift = ShiftSchedule.query.get(target_id)
            return shift.name if shift else '班次'
        elif target_type == 'risk':
            from enhanced_app import Risk
            risk = Risk.query.get(target_id)
            return risk.title if risk else '风险已删除'
        elif target_type == 'test_suite':
            from enhanced_app import TestSuite
            suite = TestSuite.query.get(target_id)
            return suite.name if suite else '测试套件已删除'
        elif target_type == 'test_case':
            from enhanced_app import TestCase
            case = TestCase.query.get(target_id)
            return case.title if case else '测试用例已删除'
        else:
            # 从描述中提取资源名称
            return activity.description or target_type
    except Exception:
        return activity.description or '未知'


# 获取最近的活動记录
@activities_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_activities():
    """获取最近的活動记录"""
    User, Activity, Bug, Project, WorkLog, app, db = get_models()

    with app.app_context():
        recent_date = datetime.utcnow() - timedelta(days=7)
        activities = Activity.query.filter(
            Activity.created_at >= recent_date
        ).order_by(Activity.created_at.desc()).limit(50).all()

        result = []
        for activity in activities:
            activity_dict = {
                'id': activity.id,
                'action': activity.action,
                'description': activity.description,
                'target_type': activity.target_type,
                'target_id': activity.target_id,
                'created_at': activity.created_at.isoformat() if activity.created_at else None,
                'field_changes': json.loads(activity.field_changes) if activity.field_changes else [],
                'resource_name': resolve_resource_name(activity),
            }

            performer = User.query.get(activity.performed_by)
            if performer:
                activity_dict['user_name'] = performer.username

            result.append(activity_dict)

        return jsonify(result), 200

# 获取特定资源的活动记录
@activities_bp.route('/<string:resource_type>/<int:resource_id>', methods=['GET'])
@jwt_required()
def get_activities_by_resource(resource_type, resource_id):
    """获取特定资源的活动记录"""
    User, Activity, Bug, Project, WorkLog, app, db = get_models()

    with app.app_context():
        activities = Activity.query.filter(
            Activity.target_type == resource_type,
            Activity.target_id == resource_id
        ).order_by(Activity.created_at.desc()).all()

        result = []
        for activity in activities:
            activity_dict = {
                'id': activity.id,
                'action': activity.action,
                'description': activity.description,
                'target_type': activity.target_type,
                'target_id': activity.target_id,
                'user_id': activity.performed_by,
                'created_at': activity.created_at.isoformat() if activity.created_at else None,
                'field_changes': json.loads(activity.field_changes) if activity.field_changes else [],
                'resource_name': resolve_resource_name(activity),
            }

            performer = User.query.get(activity.performed_by)
            if performer:
                activity_dict['user_name'] = performer.username

            result.append(activity_dict)

        return jsonify(result), 200

# 获取单个活动记录详情
@activities_bp.route('/<int:activity_id>', methods=['GET'])
@jwt_required()
def get_activity(activity_id):
    """获取单个活动记录详情"""
    User, Activity, Bug, Project, WorkLog, app, db = get_models()

    with app.app_context():
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({'error': '活动记录不存在'}), 404

        activity_dict = {
            'id': activity.id,
            'action': activity.action,
            'description': activity.description,
            'target_type': activity.target_type,
            'target_id': activity.target_id,
            'user_id': activity.performed_by,
            'created_at': activity.created_at.isoformat() if activity.created_at else None,
            'field_changes': json.loads(activity.field_changes) if activity.field_changes else [],
            'resource_name': resolve_resource_name(activity),
        }

        performer = User.query.get(activity.performed_by)
        if performer:
            activity_dict['user_name'] = performer.username
            activity_dict['user_role'] = performer.role

        return jsonify(activity_dict), 200

# 创建活动记录
@activities_bp.route('/', methods=['POST'])
@jwt_required()
def create_activity():
    """创建活动记录"""
    User, Activity, Bug, Project, WorkLog, app, db = get_models()

    with app.app_context():
        current_user_id = get_jwt_identity()
        data = request.get_json()

        activity = Activity(
            action=data.get('action'),
            description=data.get('description'),
            performed_by=int(current_user_id),
            target_type=data.get('target_type'),
            target_id=data.get('target_id')
        )

        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'message': '活动记录创建成功',
            'activity': {
                'id': activity.id,
                'action': activity.action,
                'description': activity.description
            }
        }), 201

# 删除活动记录
@activities_bp.route('/<int:activity_id>', methods=['DELETE'])
@jwt_required()
def delete_activity(activity_id):
    """删除活动记录（仅管理员）"""
    User, Activity, Bug, Project, WorkLog, app, db = get_models()

    with app.app_context():
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if current_user.role != 'admin':
            return jsonify({'error': '无权限删除活动记录'}), 403

        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({'error': '活动记录不存在'}), 404

        db.session.delete(activity)
        db.session.commit()

        return jsonify({'message': '活动记录删除成功'}), 200
