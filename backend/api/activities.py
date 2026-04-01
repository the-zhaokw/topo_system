"""
活动记录API - 系统审计日志
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

# 创建活动记录蓝图
activities_bp = Blueprint('activities', __name__, url_prefix='/activities')

def get_models():
    from enhanced_app import User, Activity, Bug, Project, Task, app
    return User, Activity, Bug, Project, Task, app

# 获取活动记录列表
@activities_bp.route('/', methods=['GET'])
@jwt_required()
def get_activities():
    """获取活动记录列表"""
    User, Activity, Bug, Project, Task, app = get_models()
    
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
            query = query.filter(Activity.action == action)
        
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
            }
            
            performer = User.query.get(activity.performed_by)
            if performer:
                activity_dict['user_name'] = performer.username
                activity_dict['user_role'] = performer.role
            
            if activity.target_type == 'bug':
                bug = Bug.query.get(activity.target_id)
                activity_dict['resource_name'] = bug.title if bug else '未知'
            elif activity.target_type == 'project':
                project = Project.query.get(activity.target_id)
                activity_dict['resource_name'] = project.name if project else '未知'
            elif activity.target_type == 'task':
                task = Task.query.get(activity.target_id)
                activity_dict['resource_name'] = task.title if task else '未知'
            
            activities.append(activity_dict)
        
        return jsonify({
            'activities': activities,
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
            'per_page': per_page
        }), 200

# 获取最近的活動记录
@activities_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_activities():
    """获取最近的活動记录"""
    User, Activity, Bug, Project, Task, app = get_models()
    
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
    User, Activity, Bug, Project, Task, app = get_models()
    
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
    User, Activity, Bug, Project, Task, app = get_models()
    
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
    User, Activity, Bug, Project, Task, app = get_models()
    db = app.extensions.get('sqlalchemy')
    
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
    User, Activity, Bug, Project, Task, app = get_models()
    db = app.extensions.get('sqlalchemy')
    
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
