import json
from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

# 延迟导入数据库和装饰器，模型延迟导入以避免循环导入
def get_db():
    """延迟获取数据库实例，避免循环导入"""
    from enhanced_app import get_db_instance
    return get_db_instance()

def get_create_audit_log():
    from enhanced_app import create_audit_log
    return create_audit_log

def get_require_permission():
    from enhanced_app import require_permission
    return require_permission

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

# 获取任务列表
@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, ProjectMember, Task, TaskStatus, TaskPriority
    db = get_db()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    project_id = request.args.get('project_id', type=int)
    status = request.args.get('status')
    priority = request.args.get('priority')
    assignee_id = request.args.get('assignee_id', type=int)
    creator_id = request.args.get('created_by', type=int)
    milestone = request.args.get('milestone')
    search = request.args.get('search', '').strip()
    my_tasks = request.args.get('my_tasks', type=bool, default=False)
    my_created = request.args.get('my_created', type=bool, default=False)
    
    # 构建基础查询
    if current_user.role == 'admin':
        # 管理员可以查看所有任务
        query = Task.query
    else:
        # 普通用户只能查看自己参与项目的任务
        user_projects = db.session.query(ProjectMember.project_id).filter_by(user_id=current_user_id).subquery()
        query = Task.query.filter(Task.project_id.in_(user_projects))
        
    # 特殊筛选条件
    if my_tasks:
        query = query.filter_by(assigned_to=current_user_id)
    
    if my_created:
        query = query.filter_by(created_by=current_user_id)
        
    # 应用筛选条件
    if project_id:
        query = query.filter_by(project_id=project_id)
        
    if status:
        query = query.filter_by(status=status)
        
    if priority:
        query = query.filter_by(priority=priority)
        
    if assignee_id:
        query = query.filter_by(assigned_to=assignee_id)
        
    if creator_id:
        query = query.filter_by(created_by=creator_id)
        
    if milestone:
        query = query.filter_by(milestone=milestone)
        
    if search:
        query = query.filter(
            (Task.title.contains(search)) |
            (Task.description.contains(search))
        )
        
    # 分页查询
    pagination = query.order_by(Task.due_date.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 构建响应数据
    tasks_data = []
    for task in pagination.items:
        # 计算是否逾期
        is_overdue = False
        if task.status.value != TaskStatus.DONE.value and task.due_date and task.due_date < datetime.utcnow():
            is_overdue = True
        
        # 只使用Task对象直接拥有的属性，避免访问未定义的关系
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'status': task.status.value,  # 使用枚举的字符串值
            'priority': task.priority.value,  # 使用枚举的字符串值
            'project_id': task.project_id,
            'project_name': None,  # 暂时设为None，避免访问未定义的project关系
            'assignee_id': task.assigned_to,
            'assignee_name': None,  # 暂时设为None，避免访问未定义的assignee关系
            'creator_id': task.created_by,
            'creator_name': None,  # 暂时设为None，避免访问未定义的creator关系
            'progress': task.progress,
            'start_date': task.start_date.isoformat() if task.start_date else None,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'updated_at': task.updated_at.isoformat() if task.updated_at else None,
            'estimated_hours': task.estimated_hours,
            'actual_hours': task.actual_hours,
            'milestone': task.milestone,
            'related_bug_id': task.related_bug_id,
            'parent_task_id': task.parent_task_id,
            'tags': task.tags,
            'notes': task.notes,
            'is_overdue': is_overdue
        })
    
    return jsonify({
        'success': True,
        'message': '获取任务列表成功',
        'data': {
            'tasks': tasks_data,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    }), 200

# 获取任务详情
@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, ProjectMember, Task, TaskStatus
    db = get_db()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 查找任务
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'success': False, 'message': '任务不存在', 'data': None}), 404
    
    # 检查权限：管理员可以查看所有任务，普通用户只能查看自己参与项目的任务
    if current_user.role != 'admin':
        member = ProjectMember.query.filter_by(
            project_id=task.project_id,
            user_id=current_user_id
        ).first()
        if not member:
            return jsonify({'success': False, 'message': '无权查看此任务', 'data': None}), 403
    
    # 获取任务参与者
    participants = []
    if task.participants:
        for participant_id in task.participants:
            participant = User.query.get(participant_id)
            if participant:
                participants.append({
                    'id': participant.id,
                    'username': participant.username,
                    'first_name': participant.first_name,
                    'last_name': participant.last_name
                })
        
    # 构建任务详情
    task_data = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status.value if hasattr(task.status, 'value') else str(task.status),
        'priority': task.priority.value if hasattr(task.priority, 'value') else str(task.priority),
        'project_id': task.project_id,
        'project_name': None,  # 暂时设为None，避免访问未定义的project关系
        'assignee_id': task.assigned_to,
        'assignee_name': None,  # 暂时设为None，避免访问未定义的assignee关系
        'creator_id': task.created_by,
        'creator_name': None,  # 暂时设为None，避免访问未定义的creator关系
        'participants': participants,
        'progress': task.progress,
        'start_date': task.start_date.isoformat() if task.start_date else None,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'updated_at': task.updated_at.isoformat() if task.updated_at else None,
        'estimated_hours': task.estimated_hours,
        'actual_hours': task.actual_hours,
        'milestone': task.milestone,
        'related_bug_id': task.related_bug_id,
        'parent_task_id': task.parent_task_id,
        'tags': task.tags,
        'notes': task.notes
    }
    
    return jsonify({
        'success': True,
        'message': '获取任务详情成功',
        'data': {'task': task_data}
    }), 200

# 创建任务
@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    # 获取权限装饰器
    require_permission = get_require_permission()
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, Project, ProjectMember, Task, TaskStatus, TaskPriority
    db = get_db()
    create_audit_log = get_create_audit_log()
    
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证输入
    if not data:
        return jsonify({'success': False, 'message': '请求数据不能为空', 'data': None}), 400
    
    required_fields = ['title', 'project_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'{field} 字段为必填项', 'data': None}), 400
    
    # 验证项目是否存在
    project = Project.query.get(data['project_id'])
    if not project:
        return jsonify({'success': False, 'message': '项目不存在', 'data': None}), 400
    
    # 验证用户是否有权限在该项目中创建任务
    current_user = User.query.get(current_user_id)
    if current_user.role != 'admin':
        member = ProjectMember.query.filter_by(
            project_id=data['project_id'],
            user_id=current_user_id
        ).first()
        if not member:
            return jsonify({'success': False, 'message': '无权在此项目中创建任务', 'data': None}), 403
    
    # 验证字段值
    valid_statuses = [status.value for status in TaskStatus]
    valid_status_names = [status.name for status in TaskStatus]
    if 'status' in data and data['status'] not in valid_statuses and data['status'] not in valid_status_names:
        return jsonify({'success': False, 'message': f'无效的任务状态，可选值: {valid_statuses}', 'data': None}), 400
    
    valid_priorities = [priority.value for priority in TaskPriority]
    valid_priority_names = [priority.name for priority in TaskPriority]
    if 'priority' in data and data['priority'] not in valid_priorities and data['priority'] not in valid_priority_names:
        return jsonify({'success': False, 'message': f'无效的任务优先级，可选值: {valid_priorities}', 'data': None}), 400
    
    # 处理日期格式
    start_date = None
    if data.get('start_date'):
        try:
            start_date = datetime.fromisoformat(data['start_date'])
        except ValueError:
            return jsonify({'success': False, 'message': '开始日期格式不正确', 'data': None}), 400
    
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return jsonify({'success': False, 'message': '截止日期格式不正确', 'data': None}), 400
    
    # 创建任务
    try:
        # 处理枚举字段
        status_value = data.get('status', 'todo')
        priority_value = data.get('priority', 'medium')
        
        # 将字符串值转换为枚举实例
        status_enum = TaskStatus.TODO  # 默认值
        priority_enum = TaskPriority.MEDIUM  # 默认值
        
        # 根据字符串值选择正确的枚举实例（支持枚举值和枚举名称）
        for status in TaskStatus:
            if status.value == status_value or status.name == status_value:
                status_enum = status
                break
        
        for priority in TaskPriority:
            if priority.value == priority_value or priority.name == priority_value:
                priority_enum = priority
                break
        
        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status=status_enum,
            priority=priority_enum,
            project_id=data['project_id'],
            created_by=current_user_id,
            assigned_to=data.get('assignee_id'),
            progress=data.get('progress', 0),
            start_date=start_date,
            due_date=due_date,
            estimated_hours=data.get('estimated_hours', 0),
            actual_hours=data.get('actual_hours', 0),
            milestone=data.get('milestone', ''),
            related_bug_id=data.get('related_bug_id'),
            tags=data.get('tags', ''),
            notes=data.get('notes', ''),
            parent_task_id=data.get('parent_task_id'),
            participants=data.get('participants', ''),
            depends_on=data.get('depends_on', ''),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        # 创建log
        create_audit_log(
            user_id=current_user_id,
            action='create_task',
            resource_type='task',
            resource_id=new_task.id,
            details=f'创建任务: {new_task.title}',
            request=request
        )
        
        return jsonify({
            'success': True,
            'message': '任务创建成功',
            'data': {
                'task': {
                    'id': new_task.id,
                    'title': new_task.title,
                    'status': new_task.status.value  # 使用枚举的字符串值
                }
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建任务失败: {str(e)}', 'data': None}), 500

# 更新任务
@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, ProjectMember, Task, TaskStatus, TaskPriority
    db = get_db()
    create_audit_log = get_create_audit_log()
    
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 查找任务
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'success': False, 'message': '任务不存在', 'data': None}), 404
    
    # 检查权限：管理员可以更新所有任务，普通用户只能更新自己参与项目的任务
    current_user = User.query.get(current_user_id)
    if current_user.role != 'admin':
        member = ProjectMember.query.filter_by(
            project_id=task.project_id,
            user_id=current_user_id
        ).first()
        if not member:
            return jsonify({'success': False, 'message': '无权更新此任务', 'data': None}), 403
    
    # 更新任务信息
    update_fields = ['title', 'description', 'progress', 'milestone', 'tags', 'notes', 'depends_on']
    for field in update_fields:
        if field in data:
            setattr(task, field, data[field])
    
    # 特殊处理枚举字段
    if 'status' in data:
        status_value = data['status']
        status_enum = TaskStatus.TODO  # 默认值
        for status in TaskStatus:
            if status.value == status_value or status.name == status_value:
                status_enum = status
                break
        task.status = status_enum
    
    if 'priority' in data:
        priority_value = data['priority']
        priority_enum = TaskPriority.MEDIUM  # 默认值
        for priority in TaskPriority:
            if priority.value == priority_value or priority.name == priority_value:
                priority_enum = priority
                break
        task.priority = priority_enum
    
    # 特殊字段处理
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({'success': False, 'message': '截止日期格式不正确', 'data': None}), 400
        else:
            task.due_date = None
    
    if 'start_date' in data:
        if data['start_date']:
            try:
                task.start_date = datetime.fromisoformat(data['start_date'])
            except ValueError:
                return jsonify({'success': False, 'message': '开始日期格式不正确', 'data': None}), 400
        else:
            task.start_date = None
    
    # 更新修改时间
    task.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # 创建log
        create_audit_log(
            user_id=current_user_id,
            action='update_task',
            resource_type='task',
            resource_id=task_id,
            details=f'更新任务: {task.title}',
            request=request
        )
        
        return jsonify({
            'success': True,
            'message': '任务更新成功',
            'data': {
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'status': task.status.value  # 使用枚举的字符串值
                }
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新任务失败: {str(e)}', 'data': None}), 500

# 删除任务
@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, ProjectMember, Task
    db = get_db()
    create_audit_log = get_create_audit_log()
    
    current_user_id = get_jwt_identity()
    
    # 查找任务
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'success': False, 'message': '任务不存在', 'data': None}), 404
    
    # 检查权限：只有管理员或创建者可以删除任务
    current_user = User.query.get(current_user_id)
    if current_user.role != 'admin' and task.created_by != current_user_id:
        return jsonify({'success': False, 'message': '无权限删除此任务', 'data': None}), 403
    
    try:
        db.session.delete(task)
        db.session.commit()
        
        # 创建log
        create_audit_log(
            user_id=current_user_id,
            action='delete_task',
            resource_type='task',
            resource_id=task_id,
            details=f'删除任务: {task.title}',
            request=request
        )
        
        return jsonify({'success': True, 'message': '任务删除成功', 'data': None}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除任务失败: {str(e)}', 'data': None}), 500

# 任务统计
@tasks_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_task_statistics():
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, ProjectMember, Task, TaskStatus
    db = get_db()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 构建基础查询
    if current_user.role == 'admin':
        # 管理员可以查看所有任务
        query = Task.query
    else:
        # 普通用户只能查看自己参与项目的任务
        user_projects = db.session.query(ProjectMember.project_id).filter_by(user_id=current_user_id).subquery()
        query = Task.query.filter(Task.project_id.in_(user_projects))
    
    # 统计各状态任务数量
    total_tasks = query.count()
    todo_tasks = query.filter_by(status=TaskStatus.TODO.value).count()
    in_progress_tasks = query.filter_by(status=TaskStatus.IN_PROGRESS.value).count()
    completed_tasks = query.filter_by(status=TaskStatus.DONE.value).count()
    
    # 统计逾期任务
    overdue_tasks = query.filter(
        Task.status != TaskStatus.DONE.value,
        Task.due_date < datetime.utcnow()
    ).count()
    
    return jsonify({
        'success': True,
        'message': '获取任务统计成功',
        'data': {
            'total': total_tasks,
            'todo': todo_tasks,
            'in_progress': in_progress_tasks,
            'completed': completed_tasks,
            'overdue': overdue_tasks
        }
    }), 200

# 更新任务状态
@tasks_bp.route('/<int:task_id>/status', methods=['PUT'])
@jwt_required()
def update_task_status(task_id):
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, ProjectMember, Task, TaskStatus
    db = get_db()
    create_audit_log = get_create_audit_log()
    
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证输入
    if not data or 'status' not in data:
        return jsonify({'success': False, 'message': '状态字段为必填项', 'data': None}), 400
    
    # 查找任务
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'success': False, 'message': '任务不存在', 'data': None}), 404
    
    # 检查权限：管理员或任务参与者可以更新状态
    current_user = User.query.get(current_user_id)
    if current_user.role != 'admin':
        member = ProjectMember.query.filter_by(
            project_id=task.project_id,
            user_id=current_user_id
        ).first()
        if not member:
            return jsonify({'success': False, 'message': '无权更新此任务状态', 'data': None}), 403
    
    # 验证状态值
    valid_statuses = [status.value for status in TaskStatus]
    valid_status_names = [status.name for status in TaskStatus]
    if data['status'] not in valid_statuses and data['status'] not in valid_status_names:
        return jsonify({'success': False, 'message': f'无效的任务状态，可选值: {valid_statuses}', 'data': None}), 400
    
    # 检查依赖任务是否已完成
    if task.depends_on:
        import json
        try:
            depends_on_list = json.loads(task.depends_on) if isinstance(task.depends_on, str) else task.depends_on
            if depends_on_list:
                incomplete_deps = []
                for dep_id in depends_on_list:
                    dep_task = Task.query.get(dep_id)
                    if dep_task and dep_task.status != TaskStatus.DONE.value:
                        incomplete_deps.append({
                            'id': dep_task.id,
                            'title': dep_task.title,
                            'status': dep_task.status.value if hasattr(dep_task.status, 'value') else str(dep_task.status)
                        })
                
                if incomplete_deps:
                    return jsonify({
                        'success': False,
                        'message': '存在未完成的依赖任务',
                        'data': {'incomplete_dependencies': incomplete_deps}
                    }), 400
        except json.JSONDecodeError:
            pass
    
    # 更新状态
    old_status = task.status
    task.status = data['status']
    task.updated_at = datetime.utcnow()
    
    # 如果任务完成，设置实际结束时间
    if data['status'] == TaskStatus.DONE.value and not task.actual_end_date:
        task.actual_end_date = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # 创建log
        create_audit_log(
            user_id=current_user_id,
            action='update_task_status',
            resource_type='task',
            resource_id=task_id,
            details=f'更新任务状态: {old_status} -> {task.status}',
            request=request
        )
        
        return jsonify({
            'success': True,
            'message': '任务状态更新成功',
            'data': {
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'status': task.status
                }
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新任务状态失败: {str(e)}', 'data': None}), 500

# 分配任务
@tasks_bp.route('/<int:task_id>/assign', methods=['PUT'])
@jwt_required()
def assign_task(task_id):
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, ProjectMember, Task
    db = get_db()
    create_audit_log = get_create_audit_log()
    
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证输入
    if not data or 'assignee_id' not in data:
        return jsonify({'success': False, 'message': '负责人ID字段为必填项', 'data': None}), 400
    
    # 查找任务
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'success': False, 'message': '任务不存在', 'data': None}), 404
    
    # 检查权限：管理员或项目管理员可以分配任务
    current_user = User.query.get(current_user_id)
    if current_user.role != 'admin':
        member = ProjectMember.query.filter_by(
            project_id=task.project_id,
            user_id=current_user_id
        ).first()
        if not member or member.role not in ['admin', 'manager']:
            return jsonify({'success': False, 'message': '无权分配此任务', 'data': None}), 403
    
    # 验证负责人是否存在
    assignee = User.query.get(data['assignee_id'])
    if not assignee:
        return jsonify({'success': False, 'message': '负责人不存在', 'data': None}), 400
    
    # 验证负责人是否在项目中
    assignee_member = ProjectMember.query.filter_by(
        project_id=task.project_id,
        user_id=data['assignee_id']
    ).first()
    if not assignee_member:
        return jsonify({'success': False, 'message': '负责人不在该项目中', 'data': None}), 400
    
    # 更新负责人
    old_assignee_id = task.assigned_to
    task.assigned_to = data['assignee_id']
    task.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # 创建log
        create_audit_log(
            user_id=current_user_id,
            action='assign_task',
            resource_type='task',
            resource_id=task_id,
            details=f'分配任务给用户: {assignee.username}',
            request=request
        )
        
        return jsonify({
            'success': True,
            'message': '任务分配成功',
            'data': {
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'assignee_id': task.assigned_to,
                    'assignee_name': assignee.username
                }
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'分配任务失败: {str(e)}', 'data': None}), 500

# 批量删除任务
@tasks_bp.route('/batch-delete', methods=['POST'])
@jwt_required()
def batch_delete_tasks():
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, ProjectMember, Task
    db = get_db()
    create_audit_log = get_create_audit_log()
    
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'ids' not in data or not isinstance(data['ids'], list):
        return jsonify({'success': False, 'message': '请提供有效的任务ID列表', 'data': None}), 400
    
    task_ids = data['ids']
    
    # 检查权限：只有管理员可以批量删除
    current_user = User.query.get(current_user_id)
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '无权批量删除任务', 'data': None}), 403
    
    try:
        # 获取要删除的任务
        tasks = Task.query.filter(Task.id.in_(task_ids)).all()
        
        if not tasks:
            return jsonify({'success': False, 'message': '未找到要删除的任务', 'data': None}), 404
        
        # 创建log
        for task in tasks:
            create_audit_log(
                user_id=current_user_id,
                action='delete_task',
                resource_type='task',
                resource_id=task.id,
                details=f'批量删除任务: {task.title}',
                request=request
            )
        
        # 批量删除
        Task.query.filter(Task.id.in_(task_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {len(tasks)} 个任务',
            'data': {'deleted_count': len(tasks)}
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '批量删除失败', 'data': None}), 500

# 批量更新任务状态
@tasks_bp.route('/batch-update-status', methods=['POST'])
@jwt_required()
def batch_update_task_status():
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, ProjectMember, Task, TaskStatus
    db = get_db()
    create_audit_log = get_create_audit_log()
    
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'ids' not in data or 'status' not in data:
        return jsonify({'success': False, 'message': '请提供有效的任务ID列表和状态', 'data': None}), 400
    
    task_ids = data['ids']
    new_status = data['status']
    
    # 验证状态值
    valid_statuses = [status.value for status in TaskStatus]
    valid_status_names = [status.name for status in TaskStatus]
    if new_status not in valid_statuses and new_status not in valid_status_names:
        return jsonify({'success': False, 'message': f'无效的任务状态，可选值: {valid_statuses}', 'data': None}), 400
    
    # 检查权限：管理员可以批量更新状态
    current_user = User.query.get(current_user_id)
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '无权批量更新任务状态', 'data': None}), 403
    
    try:
        # 批量更新状态
        updated_count = Task.query.filter(Task.id.in_(task_ids)).update(
            {'status': new_status, 'updated_at': datetime.utcnow()},
            synchronize_session=False
        )
        
        db.session.commit()
        
        # 创建log
        create_audit_log(
            user_id=current_user_id,
            action='batch_update_task_status',
            resource_type='task',
            resource_id=0,
            details=f'批量更新 {updated_count} 个任务状态为: {new_status}',
            request=request
        )
        
        return jsonify({
            'success': True,
            'message': f'成功更新 {updated_count} 个任务状态',
            'data': {'updated_count': updated_count}
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '批量更新任务状态失败', 'data': None}), 500
