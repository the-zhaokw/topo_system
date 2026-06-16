from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
import logging
from functools import wraps
from logging_config import get_log_manager
from logging_decorators import log_api_call, log_business_operation
from enhanced_app import db as _proj_db, User as _ProjUser


def _check_proj_perm(user, perm_code):
    if not user:
        return False
    if user.is_super_admin:
        return True
    pos = user.get_position_info()
    if pos and (pos.is_admin or pos.is_manager):
        return True
    return user.check_permission(perm_code)


def require_project_permission(perm_code):
    """项目子路由权限校验装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = _proj_db.session.query(_ProjUser).get(current_user_id)
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            if not _check_proj_perm(user, perm_code):
                return jsonify({'error': '权限不足', 'code': 'PERMISSION_DENIED', 'required_permission': perm_code}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


logger = logging.getLogger(__name__)

def get_log_manager_safe():
    """延迟获取日志管理器，避免在模块加载时调用"""
    from logging_config import get_log_manager
    return get_log_manager()

def convert_cost_to_string(cost_value):
    """将数据库中的cost float值转换为前端需要的字符串"""
    if cost_value is None:
        return None
    if cost_value == 0.0:
        return 'normal'
    elif cost_value > 0:
        return 'over'
    elif cost_value < 0:
        return 'under'
    return 'normal'

# 延迟导入数据库和装饰器，模型延迟导入以避免循环导入
def get_db():
    """延迟获取数据库实例，避免循环导入"""
    from enhanced_app import get_db_instance
    return get_db_instance()

def get_models():
    """延迟获取数据库模型"""
    from enhanced_app import User, UserRole, Project, ProjectMember, ProjectStatus, Risk, Bug
    return User, UserRole, Project, ProjectMember, ProjectStatus, Risk, Bug

def get_require_permission():
    from enhanced_app import require_permission
    return require_permission

def get_create_audit_log():
    from enhanced_app import create_audit_log
    return create_audit_log

def get_db_and_models():
    """获取数据库实例和模型，避免循环导入"""
    # 先导入数据库实例
    from enhanced_app import db
    # 单独导入每个模型，避免可能的导入问题
    from enhanced_app import User
    from enhanced_app import UserRole
    from enhanced_app import Project
    from enhanced_app import ProjectMember
    from enhanced_app import ProjectStatus
    from enhanced_app import create_audit_log
    from enhanced_app import Bug
    return db, Project, User, ProjectMember, ProjectStatus, create_audit_log, UserRole, Bug

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

def get_db():
    """延迟获取数据库实例，避免循环导入"""
    from enhanced_app import get_db_instance
    return get_db_instance()

# 获取项目列表
@projects_bp.route('/', methods=['GET'])
@log_api_call
@log_business_operation
@jwt_required()
def get_projects():
    """获取项目列表"""
    log_manager = get_log_manager_safe()
    
    # 延迟导入数据库模型
    db = get_db()
    User, UserRole, Project, ProjectMember, ProjectStatus, Risk, Bug = get_models()
    
    # 直接使用get_jwt_identity函数
    current_user_id = get_jwt_identity()
    current_user = db.session.query(User).get(current_user_id)
    
    # 使用增强日志系统记录请求
    try:
        log_manager.log_request(
            action='get_projects_request',
            user_id=current_user_id,
            details={
                'page': request.args.get('page', 1),
                'per_page': request.args.get('per_page', 20),
                'status': request.args.get('status'),
                'manager': request.args.get('manager'),
                'search': request.args.get('search', '').strip(),
                'only_my': request.args.get('only_my', False),
                'user_role': current_user.role
            }
        )
    except Exception as e:
        logger.error(f"获取项目列表请求日志记录失败: {str(e)}")
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    manager = request.args.get('manager', type=int)
    search = request.args.get('search', '').strip()
    only_my = request.args.get('only_my', type=bool, default=False)
    user_id = request.args.get('user_id', type=int)
    
    # 构建查询 - 使用 joinedload 避免 N+1 查询
    if user_id:
        query = db.session.query(Project).options(
            joinedload(Project.members).joinedload(ProjectMember.user)
        ).join(ProjectMember).filter(ProjectMember.user_id == user_id)
    elif current_user.role == UserRole.ADMIN.value:
        # 管理员可以查看所有项目
        query = db.session.query(Project).options(
            joinedload(Project.members).joinedload(ProjectMember.user)
        )
    else:
        # 普通用户只能查看自己参与的项目
        query = db.session.query(Project).options(
            joinedload(Project.members).joinedload(ProjectMember.user)
        ).join(ProjectMember).filter(ProjectMember.user_id == current_user_id)
    
    # 如果只看我创建的项目
    if only_my:
        query = query.filter(Project.owner_id == current_user_id)
    
    # 应用筛选条件
    if status:
        query = query.filter_by(status=status)
    
    if manager:
        query = query.filter_by(manager_id=manager)
    
    if search:
        query = query.filter(
            (Project.name.contains(search)) |
            (Project.description.contains(search)) |
            (Project.code.contains(search))
        )
    
    # 分页查询
    pagination = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 构建响应数据 - 使用已加载的数据避免 N+1 查询
    projects_data = []
    for project in pagination.items:
        # 成员数据已从 joinedload 加载
        member_count = len(project.members) if project.members else 0
        
        # 直接使用已加载的成员数据
        members_data = []
        for member in project.members:
            member_first_name = ''
            member_last_name = ''
            member_department = ''
            member_position = ''
            try:
                if member.user:
                    member_first_name = member.user.first_name or ''
                    member_last_name = member.user.last_name or ''
                    member_department = member.user.department or ''
                    member_position = member.user.position or ''
            except Exception:
                pass
            
            members_data.append({
                'id': member.id,
                'user_id': member.user_id,
                'username': member.user.username if member.user else None,
                'role': member.role,
                'joined_at': member.join_date.isoformat() if member.join_date else None,
                'first_name': member_first_name,
                'last_name': member_last_name,
                'department': member_department,
                'position': member_position
            })
        
        # 安全获取项目经理姓名
        manager_name = None
        try:
            if project.manager:
                manager_name = f'{project.manager.first_name} {project.manager.last_name}'
        except Exception:
            manager_name = None
        
        projects_data.append({
            'id': project.id,
            'name': project.name,
            'code': project.code,
            'description': project.description,
            'status': project.status,
            'owner_id': project.owner_id,
            'manager_id': project.manager_id,
            'manager_name': manager_name,
            'start_date': project.start_date.isoformat() if project.start_date else None,
            'end_date': project.end_date.isoformat() if project.end_date else None,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None,
            'member_count': member_count,
            'members': members_data,
            'progress': project.progress,
            'current_stage': project.current_stage,
            'quality': project.quality,
            'risk': project.risk,
            'resources': project.resources,
            'cost': convert_cost_to_string(project.cost),
            'priority': project.priority,
            'technology_stack': project.technology_stack,
            'budget': project.budget,
            'actual_cost': project.actual_cost,
            'project_type': project.project_type,
            'client_name': project.client_name,
            'client_contact': project.client_contact,
            'contract_value': project.contract_value,
            'estimated_hours': project.estimated_hours,
            'actual_hours': project.actual_hours,
            'team_size': project.team_size,
            'tags': project.tags,
            'milestones': project.milestones,
            'versions': project.versions
        })
        
    # 使用增强日志系统记录业务操作
    try:
        log_manager.log_business(
            operation='projects_listed',
            user_id=current_user_id,
            project_id=0,
            details={
                'total_projects': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'filtered_by_status': status,
                'filtered_by_manager': manager,
                'search_term': search,
                'only_my_projects': only_my
            }
        )
    except Exception as e:
        logger.error(f"获取项目列表业务日志记录失败: {str(e)}")
    
    return jsonify({
        'success': True,
        'message': '获取项目列表成功',
        'data': {
            'projects': projects_data,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    }), 200

# 获取项目详情
@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    
    current_user_id = get_jwt_identity()
    
    # 延迟导入数据库模型
    db, Project, User, ProjectMember, ProjectStatus, create_audit_log, UserRole, Bug = get_db_and_models()
    
    current_user = db.session.query(User).get(current_user_id)
    
    # 查找项目
    project = db.session.query(Project).get(project_id)
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    # 检查权限：管理员可以查看所有项目，普通用户只能查看自己参与的项目
    if current_user.role != UserRole.ADMIN.value:
        member = db.session.query(ProjectMember).filter_by(
            project_id=project_id,
            user_id=current_user_id
        ).first()
        if not member:
            return jsonify({'error': '无权查看此项目'}), 403
    
    # 获取项目成员信息
    members = db.session.query(ProjectMember).filter_by(project_id=project_id).all()
    members_data = []
    for member in members:
        member_first_name = ''
        member_last_name = ''
        member_department = ''
        member_position = ''
        try:
            if member.user:
                member_first_name = member.user.first_name or ''
                member_last_name = member.user.last_name or ''
                member_department = member.user.department or ''
                member_position = member.user.position or ''
        except Exception:
            pass
        
        members_data.append({
            'id': member.id,
            'user_id': member.user_id,
            'username': member.user.username if member.user else None,
            'role': member.role,
            'joined_at': member.join_date.isoformat() if member.join_date else None,
            'first_name': member_first_name,
            'last_name': member_last_name,
            'department': member_department,
            'position': member_position
        })
    
    # 安全获取项目经理和创建者姓名
    owner_name = None
    manager_name = None
    try:
        if project.owner:
            owner_name = f'{project.owner.first_name} {project.owner.last_name}'
    except Exception:
        pass
    
    try:
        if project.manager:
            manager_name = f'{project.manager.first_name} {project.manager.last_name}'
    except Exception:
        pass
    
    # 获取项目下的缺陷数量
    bug_count = db.session.query(Bug).filter_by(project_id=project_id).count()
    
    # 构建项目详情
    project_data = {
        'id': project.id,
        'name': project.name,
        'code': project.code,
        'description': project.description,
        'status': project.status,
        'owner_id': project.owner_id,
        'owner_name': owner_name,
        'manager_id': project.manager_id,
        'manager_name': manager_name,
        'start_date': project.start_date.isoformat() if project.start_date else None,
        'end_date': project.end_date.isoformat() if project.end_date else None,
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'updated_at': project.updated_at.isoformat() if project.updated_at else None,
        'progress': project.progress,
        'current_stage': project.current_stage,
        'quality': project.quality,
        'risk': project.risk,
        'resources': project.resources,
        'cost': convert_cost_to_string(project.cost),
        'priority': project.priority,
        'members': members_data,
        'technology_stack': project.technology_stack,
        'budget': project.budget,
        'actual_cost': project.actual_cost,
        'project_type': project.project_type,
        'client_name': project.client_name,
        'client_contact': project.client_contact,
        'contract_value': project.contract_value,
        'estimated_hours': project.estimated_hours,
        'actual_hours': project.actual_hours,
        'team_size': project.team_size,
        'tags': project.tags,
        'milestones': project.milestones,
        'versions': project.versions,
        'modules': project.modules,
        'risks': project.risk,
        'bug_count': bug_count
    }
    
    return jsonify({
        'success': True,
        'message': '获取项目详情成功',
        'data': {
            'project': project_data
        }
    }), 200

# 创建项目
@projects_bp.route('/', methods=['POST'])
@log_api_call
@log_business_operation
@jwt_required()
@require_project_permission('project:create')
def create_project():
    log_manager = get_log_manager_safe()

    # 获取当前用户ID（在JWT上下文中）
    current_user_id = get_jwt_identity()
    
    # 延迟导入数据库模型
    db, Project, User, ProjectMember, ProjectStatus, create_audit_log, UserRole, Bug = get_db_and_models()
    
    # 获取当前用户
    current_user = db.session.query(User).get(current_user_id)
    
    # 检查权限
    if not current_user.can('create'):
        return jsonify({
            'success': False,
            'error': '权限不足',
            'code': 'PERMISSION_DENIED'
        }), 403
    
    # 获取请求数据
    data = request.get_json()
    
    # 处理 members 字段 - 单独处理，不将其作为项目属性更新
    members_data = data.pop('members', None)
    
    # 确保 members_data 是一个列表（处理可能的 Proxy 对象或其他格式）
    if members_data is not None:
        try:
            # 尝试转换为列表
            members_data = list(members_data)
        except:
            members_data = None
    
    # 记录请求日志
    try:
        log_manager.log_request(
            action='create_project',
            user_id=current_user_id,
            details={
                'name': data.get('name'),
                'code': data.get('code'),
                'manager_id': data.get('manager_id'),
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date')
            }
        )
    except Exception as e:
        logger.error(f"创建项目请求日志记录失败: {str(e)}")
    
    if not data:
        log_manager.log_error(
            error_type='create_project_validation_error',
            message="请求数据不能为空"
        )
        return jsonify({
            'success': False,
            'error': '请求数据不能为空',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    required_fields = ['name', 'code']
    for field in required_fields:
        if field not in data or not data[field]:
            log_manager.log_error(
                message=f"创建项目验证错误: 缺少必填字段: {field}"
            )
            return jsonify({
                'success': False,
                'error': f'{field} 字段为必填项',
                'code': 'VALIDATION_ERROR'
            }), 400
    
    if db.session.query(Project).filter_by(code=data['code']).first():
        log_manager.log_error(
            message=f"创建项目验证错误: 项目代码已存在: {data['code']}"
        )
        return jsonify({'error': '项目代码已存在'}), 400
    
    try:
        start_date = None
        if 'start_date' in data and data['start_date']:
            try:
                date_str = data['start_date']
                if date_str.endswith('Z'):
                    date_str = date_str[:-1] + '+00:00'
                start_date = datetime.fromisoformat(date_str)
            except ValueError:
                log_manager.log_error(
                    message=f"创建项目验证错误: 开始日期格式不正确: {data['start_date']}"
                )
                return jsonify({'error': '开始日期格式不正确'}), 400
        
        end_date = None
        if 'end_date' in data and data['end_date']:
            try:
                date_str = data['end_date']
                if date_str.endswith('Z'):
                    date_str = date_str[:-1] + '+00:00'
                end_date = datetime.fromisoformat(date_str)
            except ValueError:
                log_manager.log_error(
                    message=f"创建项目验证错误: 结束日期格式不正确: {data['end_date']}"
                )
                return jsonify({'error': '结束日期格式不正确'}), 400
        
        if 'quality' in data and data['quality']:
            valid_qualities = ['Excellent', 'Good', 'Fair', 'Poor']
            if data['quality'] not in valid_qualities:
                log_manager.log_error(
                    error_type='create_project_validation_error',
                    message=f"无效的质量值: {data['quality']}"
                )
                return jsonify({'error': f'无效的质量值，可选值: {valid_qualities}'}), 400
        
        if 'risk' in data and data['risk']:
            valid_risks = ['Low', 'Medium', 'High']
            if data['risk'] not in valid_risks:
                log_manager.log_error(
                    error_type='create_project_validation_error',
                    message=f"无效的风险值: {data['risk']}"
                )
                return jsonify({'error': f'无效的风险值，可选值: {valid_risks}'}), 400
        
        progress = data.get('progress', 0)
        if progress < 0 or progress > 100:
            log_manager.log_error(
                error_type='create_project_validation_error',
                message=f"进度值超出范围: {progress}"
            )
            return jsonify({'error': '进度值必须在0-100之间'}), 400
        
        cost = data.get('cost')
        if cost is not None:
            valid_cost_values = ['normal', 'over', 'under']
            if cost not in valid_cost_values:
                log_manager.log_error(
                    error_type='create_project_validation_error',
                    message=f"无效的费用状态: {cost}"
                )
                return jsonify({'error': f'无效的费用状态，可选值: {valid_cost_values}'}), 400
            cost_mapping = {'normal': 0.0, 'over': 1.0, 'under': -1.0}
            cost = cost_mapping.get(cost, 0.0)

        new_project = Project(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            manager_id=data.get('manager_id'),
            start_date=start_date,
            end_date=end_date,
            progress=progress,
            quality=data.get('quality'),
            risk=data.get('risk'),
            resources=data.get('resources'),
            cost=cost,
            status='active',
            owner_id=current_user_id,
            priority=data.get('priority', 'medium')
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        # 处理成员添加
        if members_data is not None:
            # 验证 members_data 是否为列表
            if isinstance(members_data, list):
                for user_id in members_data:
                    try:
                        user_id_int = int(user_id)
                    except (ValueError, TypeError):
                        continue
                    
                    user = db.session.query(User).get(user_id_int)
                    if user:
                        new_member = ProjectMember(
                            project_id=new_project.id,
                            user_id=user_id_int,
                            role='member',
                            join_date=datetime.utcnow()
                        )
                        db.session.add(new_member)
                db.session.commit()
        
        # 确保项目经理是项目成员（如果有设置）
        if new_project.manager_id:
            manager_member = db.session.query(ProjectMember).filter_by(
                project_id=new_project.id,
                user_id=new_project.manager_id
            ).first()
            
            if not manager_member:
                new_manager_member = ProjectMember(
                    project_id=new_project.id,
                    user_id=new_project.manager_id,
                    role='manager',
                    join_date=datetime.utcnow()
                )
                db.session.add(new_manager_member)
                db.session.commit()
        
        log_manager.log_business(
            operation='project_created',
            user_id=current_user_id,
            project_id=new_project.id,
            details={
                'name': new_project.name,
                'code': new_project.code,
                'manager_id': new_project.manager_id,
                'start_date': str(new_project.start_date),
                'end_date': str(new_project.end_date),
                'progress': new_project.progress,
                'quality': new_project.quality,
                'risk': new_project.risk
            }
        )
        
        create_audit_log(
            user_id=current_user_id,
            action='create_project',
            resource_type='project',
            resource_id=new_project.id,
            details=f'创建项目: {new_project.name}',
            request=request
        )
        
        return jsonify({
            'success': True,
            'message': '项目创建成功',
            'data': {
                'project': {
                    'id': new_project.id,
                    'name': new_project.name,
                    'code': new_project.code,
                    'status': new_project.status
                }
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        log_manager.log_error(
            error_type='create_project_database_error',
            message=f"创建项目失败: {str(e)}"
        )
        return jsonify({'error': f'创建项目失败: {str(e)}'}), 500

# 更新项目信息
@projects_bp.route('/<int:project_id>', methods=['PUT'])
@log_api_call
@log_business_operation
@jwt_required()
@require_project_permission('project:edit')
def update_project(project_id):
    log_manager = get_log_manager_safe()

    # 延迟导入权限装饰器
    require_permission_func = get_require_permission()
    
    @require_permission_func('edit')
    def jwt_wrapped_function():
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 记录请求数据，便于调试
        logger.info(f"更新项目请求数据: {data}")
        
        # 处理 members 字段 - 单独处理，不将其作为项目属性更新
        members_data = data.pop('members', None)
        
        # 更健壮的 members_data 处理
        if members_data is not None:
            try:
                # 尝试多种方式转换为标准列表
                if hasattr(members_data, '__iter__') and not isinstance(members_data, (str, bytes)):
                    # 如果是可迭代对象但不是字符串，转换为列表
                    members_data = list(members_data)
                elif not isinstance(members_data, list):
                    # 如果不是列表，尝试 JSON 解析或其他转换
                    import json
                    try:
                        members_data = json.loads(json.dumps(members_data))
                        if not isinstance(members_data, list):
                            members_data = None
                    except:
                        members_data = None
            except Exception as e:
                logger.warning(f"处理 members_data 时出错: {str(e)}")
                members_data = None
        
        logger.info(f"处理后的 members_data: {members_data}")
        
        # 延迟导入数据库模型
        db, Project, User, ProjectMember, ProjectStatus, create_audit_log, UserRole, Bug = get_db_and_models()
        
        current_user = db.session.query(User).get(current_user_id)
        
        # 查找项目
        project = db.session.query(Project).get(project_id)
        if not project:
            log_manager.log_error(
                error_type='update_project_failed',
                message='项目不存在',
                user_id=current_user_id,
                details={'project_id': project_id}
            )
            return jsonify({'error': '项目不存在'}), 404
        
        # 检查权限：只有管理员、项目经理或创建者可以更新项目
        if current_user.role != UserRole.ADMIN.value and \
           project.manager_id != current_user_id and \
           project.owner_id != current_user_id:
            log_manager.log_audit(
                user_id=current_user_id,
                action='update_project_unauthorized',
                resource_type='project',
                resource_id=project_id,
                details={'error': '无权限更新此项目', 'username': current_user.username}
            )
            return jsonify({'error': '无权限更新此项目'}), 403
        
        # 记录更新前的项目状态
        old_project_data = {
            'name': project.name,
            'code': project.code,
            'status': project.status,
            'quality': project.quality,
            'risk': project.risk,
            'progress': project.progress,
            'cost': project.cost
        }
        
        # 更新项目信息
        # 注意：cost 字段在下面单独处理，不在此处批量更新
        update_fields = [
            'name', 'description', 'priority', 'technology_stack', 
            'budget', 'actual_cost', 'progress', 'quality', 'risk', 
            'resources', 'status', 'current_stage',
            'project_type', 'client_name', 'client_contact', 
            'contract_value', 'estimated_hours', 'actual_hours',
            'team_size', 'tags', 'milestones', 'versions', 'modules'
        ]
        
        # 先处理 cost 字段，因为它可能在 autoflush 时导致类型转换错误
        # 数据库中 cost 是 Float 类型: 0=normal, >0=over, <0=under
        if 'cost' in data:
            if data['cost'] is not None:
                valid_cost_values = ['normal', 'over', 'under']
                if data['cost'] not in valid_cost_values:
                    return jsonify({'error': f'无效的费用状态，可选值: {valid_cost_values}'}), 400
                cost_mapping = {'normal': 0.0, 'over': 1.0, 'under': -1.0}
                project.cost = cost_mapping.get(data['cost'], 0.0)
            else:
                project.cost = None
            # 从 data 中移除 cost 字段，防止被其他逻辑覆盖
            data.pop('cost')
        
        for field in update_fields:
            if field in data:
                setattr(project, field, data[field])
        
        # 特殊字段处理
        if 'code' in data and data['code']:
            # 验证项目代码格式
            code = data['code'].strip()
            if not code:
                return jsonify({'error': '项目代码不能为空', 'code': 'VALIDATION_ERROR'}), 400
            
            if len(code) < 2:
                return jsonify({'error': '项目代码长度至少为2个字符', 'code': 'VALIDATION_ERROR'}), 400
                
            if len(code) > 20:
                return jsonify({'error': '项目代码长度不能超过20个字符', 'code': 'VALIDATION_ERROR'}), 400
            
            # 检查项目代码是否已被其他项目使用
            existing_project = db.session.query(Project).filter_by(code=code).first()
            if existing_project and existing_project.id != project_id:
                return jsonify({'error': f'项目代码 "{code}" 已存在，请使用其他代码', 'code': 'VALIDATION_ERROR'}), 400
            project.code = code
        
        if 'manager_id' in data:
            # 如果 manager_id 为 null 或 0，允许清空项目经理
            if data['manager_id'] is None or data['manager_id'] == 0:
                project.manager_id = None
            else:
                # 验证用户是否存在且有效
                try:
                    manager_id_int = int(data['manager_id'])
                    if manager_id_int <= 0:
                        return jsonify({'error': '项目经理ID必须为正整数', 'code': 'VALIDATION_ERROR'}), 400
                    
                    manager = db.session.query(User).get(manager_id_int)
                    if not manager:
                        return jsonify({'error': '指定的项目经理不存在', 'code': 'VALIDATION_ERROR'}), 400
                    
                    project.manager_id = manager_id_int
                    
                    # 确保项目经理是项目成员
                    manager_member = db.session.query(ProjectMember).filter_by(
                        project_id=project_id,
                        user_id=manager_id_int
                    ).first()
                    
                    if not manager_member:
                        new_manager_member = ProjectMember(
                            project_id=project_id,
                            user_id=manager_id_int,
                            role='manager',
                            join_date=datetime.utcnow()
                        )
                        db.session.add(new_manager_member)
                except (ValueError, TypeError):
                    return jsonify({'error': '项目经理ID格式不正确', 'code': 'VALIDATION_ERROR'}), 400
        
        if 'status' in data and data['status'] is not None:
            # 验证状态
            valid_statuses = ['active', 'completed', 'closed', 'archived']
            if data['status'] not in valid_statuses:
                return jsonify({'error': f'无效的项目状态，可选值: {valid_statuses}'}), 400

            # 状态流转验证（简单实现）
            status_flow = {
                'active': ['completed', 'closed', 'archived'],
                'completed': ['closed', 'archived'],
                'closed': ['archived'],
                'archived': []
            }

            # 只在新状态与当前状态不同时进行流转验证
            if project.status != data['status']:
                if project.status in status_flow and data['status'] not in status_flow[project.status]:
                    return jsonify({'error': f'无效的状态流转，当前状态为 {project.status}，只能流转为 {status_flow[project.status]}'}), 400

            project.status = data['status']
        elif 'status' in data and data['status'] is None:
            # 允许将状态设置为 null
            project.status = None
        
        # 处理日期格式
        if 'start_date' in data:
            if data['start_date']:
                try:
                    date_str = data['start_date']
                    if date_str.endswith('Z'):
                        date_str = date_str[:-1] + '+00:00'
                    project.start_date = datetime.fromisoformat(date_str)
                except ValueError as e:
                    logger.error(f"开始日期解析失败: {date_str}, 错误: {str(e)}")
                    return jsonify({'error': f'开始日期格式不正确: {str(e)}'}), 400
            else:
                project.start_date = None
        
        if 'end_date' in data:
            if data['end_date']:
                try:
                    date_str = data['end_date']
                    if date_str.endswith('Z'):
                        date_str = date_str[:-1] + '+00:00'
                    project.end_date = datetime.fromisoformat(date_str)
                except ValueError as e:
                    logger.error(f"结束日期解析失败: {date_str}, 错误: {str(e)}")
                    return jsonify({'error': f'结束日期格式不正确: {str(e)}'}), 400
            else:
                project.end_date = None
        
        if 'progress' in data:
            try:
                progress = float(data['progress'])
                if progress < 0 or progress > 100:
                    return jsonify({'error': '进度值必须在0-100之间', 'code': 'VALIDATION_ERROR'}), 400
                project.progress = progress
            except (ValueError, TypeError):
                return jsonify({'error': '进度值必须是有效的数字', 'code': 'VALIDATION_ERROR'}), 400
        
        # 处理质量字段
        if 'quality' in data:
            valid_qualities = ['Excellent', 'Good', 'Fair', 'Poor']
            if data['quality'] and data['quality'] not in valid_qualities:
                return jsonify({'error': f'无效的质量值，可选值: {valid_qualities}'}), 400
            project.quality = data['quality']
        
        # 处理风险字段
        if 'risk' in data:
            valid_risks = ['Low', 'Medium', 'High']
            if data['risk'] and data['risk'] not in valid_risks:
                return jsonify({'error': f'无效的风险值，可选值: {valid_risks}'}), 400
            project.risk = data['risk']
        
        # 处理资源字段
        if 'resources' in data:
            project.resources = data['resources']
        
        # 注意：cost 字段已在上面处理过，此处不再重复处理
        
        # 更新修改时间
        project.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            
            # 处理成员更新
            if members_data is not None:
                # 验证 members_data 是否为有效的成员列表
                if not isinstance(members_data, list):
                    return jsonify({'error': '成员数据格式不正确，应为数组', 'code': 'VALIDATION_ERROR'}), 400
                
                # 过滤和验证成员ID
                valid_member_ids = []
                for user_id in members_data:
                    try:
                        user_id_int = int(user_id)
                        if user_id_int <= 0:
                            continue  # 跳过无效ID
                        
                        # 验证用户是否存在
                        user = db.session.query(User).get(user_id_int)
                        if user:
                            valid_member_ids.append(user_id_int)
                        else:
                            logger.warning(f"跳过不存在的用户ID: {user_id_int}")
                    except (ValueError, TypeError):
                        logger.warning(f"跳过无效的成员ID: {user_id}")
                        continue
                
                if valid_member_ids:
                    # 删除现有成员（除了项目经理）
                    existing_members = db.session.query(ProjectMember).filter_by(project_id=project_id).all()
                    for member in existing_members:
                        # 保留项目经理记录
                        if member.user_id != project.manager_id:
                            db.session.delete(member)
                    
                    # 添加新成员
                    for user_id_int in valid_member_ids:
                        # 避免重复添加项目经理
                        if user_id_int != project.manager_id:
                            new_member = ProjectMember(
                                project_id=project_id,
                                user_id=user_id_int,
                                role='member',
                                join_date=datetime.utcnow()
                            )
                            db.session.add(new_member)
                    
                    db.session.commit()
            
            # 记录项目更新成功的详细日志
            new_project_data = {
                'name': project.name,
                'code': project.code,
                'status': project.status,
                'quality': project.quality,
                'risk': project.risk,
                'progress': project.progress,
                'cost': project.cost
            }
            
            # 计算变更的字段
            changed_fields = []
            for field in old_project_data:
                if old_project_data[field] != new_project_data[field]:
                    changed_fields.append({
                        'field': field,
                        'old_value': old_project_data[field],
                        'new_value': new_project_data[field]
                    })
            
            # 创建log
            create_audit_log(
                user_id=current_user_id,
                action='update_project',
                resource_type='project',
                resource_id=project_id,
                details=f'更新项目: {project.name}，变更字段: {[f["field"] for f in changed_fields]}',
                request=request
            )
            
            # 使用增强的日志系统记录业务操作
            log_manager.log_business(
                operation='project_updated',
                user_id=current_user_id,
                project_id=project_id,
                details={
                    'project_name': project.name,
                    'changed_fields': changed_fields,
                    'old_data': old_project_data,
                    'new_data': new_project_data
                }
            )
            
            return jsonify({
                'success': True,
                'message': '项目更新成功',
                'data': {
                    'project': {
                        'id': project.id,
                        'name': project.name,
                        'code': project.code,
                        'status': project.status,
                        'current_stage': project.current_stage,
                        'quality': project.quality,
                        'risk': project.risk,
                        'resources': project.resources,
                        'cost': convert_cost_to_string(project.cost),
                        'progress': project.progress,
                        'start_date': project.start_date.isoformat() if project.start_date else None,
                        'end_date': project.end_date.isoformat() if project.end_date else None,
                        'manager_id': project.manager_id
                    }
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            log_manager.log_error(
                error_type='update_project_failed',
                message=f'更新项目失败: {str(e)}',
                user_id=current_user_id,
                details={'project_id': project_id, 'project_name': project.name}
            )
            return jsonify({'error': f'更新项目失败: {str(e)}'}), 500
    
    return jwt_wrapped_function()

# 获取项目成员列表
@projects_bp.route('/<int:project_id>/members', methods=['GET'])
@log_api_call
def get_project_members(project_id):
    log_manager = get_log_manager_safe()

    require_permission_func = get_require_permission()

    @require_permission_func('view')
    def jwt_wrapped_function():
        db, Project, User, ProjectMember, ProjectStatus, create_audit_log, UserRole, Bug = get_db_and_models()

        current_user_id = get_jwt_identity()
        current_user = db.session.query(User).get(current_user_id)

        project = db.session.query(Project).get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404

        if current_user.role != UserRole.ADMIN.value:
            member = db.session.query(ProjectMember).filter_by(
                project_id=project_id,
                user_id=current_user_id
            ).first()
            if not member:
                return jsonify({'error': '无权查看此项目成员'}), 403

        members = db.session.query(ProjectMember).filter_by(project_id=project_id).all()
        members_data = []
        for member in members:
            member_first_name = ''
            member_last_name = ''
            member_department = ''
            member_position = ''
            try:
                if member.user:
                    member_first_name = member.user.first_name or ''
                    member_last_name = member.user.last_name or ''
                    member_department = member.user.department or ''
                    member_position = member.user.position or ''
            except Exception:
                pass

            members_data.append({
                'id': member.id,
                'user_id': member.user_id,
                'username': member.user.username if member.user else None,
                'role': member.role,
                'joined_at': member.join_date.isoformat() if member.join_date else None,
                'first_name': member_first_name,
                'last_name': member_last_name,
                'department': member_department,
                'position': member_position
            })

        return jsonify({
            'members': members_data,
            'total': len(members_data)
        }), 200

    return jwt_wrapped_function()

# 获取项目的风险列表
@projects_bp.route('/<int:project_id>/risks', methods=['GET'])
@jwt_required()
def get_project_risks(project_id):
    db = get_db()
    User, UserRole, Project, ProjectMember, ProjectStatus, Risk, Bug = get_models()

    current_user_id = get_jwt_identity()
    current_user = db.session.query(User).get(current_user_id)

    project = db.session.query(Project).get(project_id)
    if not project:
        return jsonify({'error': '项目不存在'}), 404

    risk_type = request.args.get('risk_type')
    status = request.args.get('status')
    level = request.args.get('level')
    priority = request.args.get('priority')
    category = request.args.get('category')
    assigned_to = request.args.get('assigned_to', type=int)
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = db.session.query(Risk).filter(Risk.project_id == project_id)

    if risk_type:
        query = query.filter(Risk.risk_type == risk_type)

    if status:
        query = query.filter(Risk.status == status)

    if level:
        query = query.filter(Risk.level == level)

    if priority:
        query = query.filter(Risk.priority == priority)

    if category:
        query = query.filter(Risk.category == category)

    if assigned_to:
        query = query.filter(Risk.assigned_to == assigned_to)

    if search:
        query = query.filter(
            db.or_(
                Risk.title.contains(search),
                Risk.description.contains(search)
            )
        )

    pagination = query.order_by(Risk.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    risks_data = []
    for risk in pagination.items:
        risk_dict = risk.to_dict()
        if risk.related_bug:
            risk_dict['related_bug_title'] = risk.related_bug.title
        risks_data.append(risk_dict)

    return jsonify({
        'success': True,
        'message': '获取风险列表成功',
        'data': {
            'risks': risks_data,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
    }), 200

# 添加项目成员
@projects_bp.route('/<int:project_id>/members', methods=['POST'])
@log_api_call
@log_business_operation
def add_project_member(project_id):
    log_manager = get_log_manager_safe()

    # 延迟导入权限装饰器
    require_permission_func = get_require_permission()
    
    @require_permission_func('edit')
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        db, Project, User, ProjectMember, ProjectStatus, create_audit_log, UserRole, Bug = get_db_and_models()
        
        current_user_id = get_jwt_identity()
        current_user = db.session.query(User).get(current_user_id)
        data = request.get_json()
        
        # 处理 members 字段 - 单独处理，不将其作为项目属性更新
        members_data = data.pop('members', None)
        
        # 确保 members_data 是一个列表
        if members_data is not None and not isinstance(members_data, list):
            return jsonify({'error': '成员数据格式不正确'}), 400
        
        # 延迟导入数据库模型查找项目
        project = db.session.query(Project).get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        # 检查权限：只有管理员或项目经理可以添加成员
        if current_user.role != UserRole.ADMIN.value and project.manager_id != current_user_id:
            return jsonify({'error': '无权限添加项目成员'}), 403
        
        # 验证输入
        if not data or 'user_id' not in data:
            return jsonify({'error': '请提供用户ID'}), 400
        
        user_id = data['user_id']
        role = data.get('role', 'member')  # 默认角色为普通成员
        
        # 验证用户是否存在
        user = db.session.query(User).get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 400
        
        # 检查用户是否已经是项目成员
        existing_member = db.session.query(ProjectMember).filter_by(
            project_id=project_id,
            user_id=user_id
        ).first()
        
        if existing_member:
            return jsonify({'error': '用户已经是项目成员'}), 400
        
        # 添加成员
        try:
            new_member = ProjectMember(
                project_id=project_id,
                user_id=user_id,
                role=role,
                join_date=datetime.utcnow()
            )
            
            db.session.add(new_member)
            db.session.commit()
            
            # 创建log
            create_audit_log(
                user_id=current_user_id,
                action='add_project_member',
                resource_type='project_member',
                resource_id=new_member.id,
                details=f'添加项目成员: {user.username} 到项目: {project.name}',
                request=request
            )
            
            return jsonify({
                'message': '项目成员添加成功',
                'member': {
                    'id': new_member.id,
                    'user_id': new_member.user_id,
                    'username': user.username,
                    'role': new_member.role
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'添加项目成员失败: {str(e)}'}), 500
    
    return jwt_wrapped_function()

# 更新项目成员角色
@projects_bp.route('/<int:project_id>/members/<int:member_id>', methods=['PUT'])
@log_api_call
@log_business_operation
def update_project_member(project_id, member_id):
    log_manager = get_log_manager_safe()

    # 延迟导入权限装饰器
    require_permission_func = get_require_permission()
    
    @require_permission_func('edit')
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        db, Project, User, ProjectMember, ProjectStatus, create_audit_log, UserRole, Bug = get_db_and_models()
        
        current_user_id = get_jwt_identity()
        current_user = db.session.query(User).get(current_user_id)
        data = request.get_json()
        
        # 查找项目
        project = db.session.query(Project).get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        # 检查权限：只有管理员或项目经理可以更新成员角色
        if current_user.role != UserRole.ADMIN.value and project.manager_id != current_user_id:
            return jsonify({'error': '无权限更新项目成员'}), 403
        
        # 查找项目成员
        member = db.session.query(ProjectMember).filter_by(
            id=member_id,
            project_id=project_id
        ).first()
        
        if not member:
            return jsonify({'error': '项目成员不存在'}), 404
        
        # 更新角色
        if 'role' in data:
            member.role = data['role']
        
        try:
            db.session.commit()
            
            # 创建log
            create_audit_log(
                user_id=current_user_id,
                action='update_project_member',
                resource_type='project_member',
                resource_id=member_id,
                details=f'更新项目成员角色: {member.user.username} 在项目: {project.name}',
                request=request
            )
            
            return jsonify({
                'message': '项目成员更新成功',
                'member': {
                    'id': member.id,
                    'user_id': member.user_id,
                    'username': member.user.username,
                    'role': member.role
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': "更新项目成员失败: " + str(e)}), 500
    
    return jwt_wrapped_function()

# 删除项目成员
@projects_bp.route('/<int:project_id>/members/<int:member_id>', methods=['DELETE'])
@log_api_call
@log_business_operation
def remove_project_member(project_id, member_id):
    log_manager = get_log_manager_safe()

    # 延迟导入权限装饰器
    require_permission_func = get_require_permission()
    
    @require_permission_func('edit')
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        db, Project, User, ProjectMember, ProjectStatus, create_audit_log, UserRole, Bug = get_db_and_models()
        
        current_user_id = get_jwt_identity()
        current_user = db.session.query(User).get(current_user_id)
        
        # 查找项目
        project = db.session.query(Project).get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        # 检查权限：只有管理员或项目经理可以删除成员
        if current_user.role != UserRole.ADMIN.value and project.manager_id != current_user_id:
            return jsonify({'error': '无权限删除项目成员'}), 403
        
        # 查找项目成员
        member = db.session.query(ProjectMember).filter_by(
            id=member_id,
            project_id=project_id
        ).first()
        
        if not member:
            return jsonify({'error': '项目成员不存在'}), 404
        
        # 不能删除项目经理
        if member.user_id == project.manager_id:
            return jsonify({'error': '不能删除项目经理'}), 403
        
        try:
            # 创建log（删除前）
            create_audit_log(
                user_id=current_user_id,
                action='remove_project_member',
                resource_type='project_member',
                resource_id=member_id,
                details=f'移除项目成员: {member.user.username} 从项目: {project.name}',
                request=request
            )
            
            db.session.delete(member)
            db.session.commit()
            
            return jsonify({'message': '项目成员删除成功'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': '删除项目成员失败: ' + str(e)}), 500
    
    return jwt_wrapped_function()

# 删除项目
@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@log_api_call
@log_business_operation
@jwt_required()
@require_project_permission('project:delete')
def delete_project(project_id):
    log_manager = get_log_manager_safe()

    # 延迟导入权限装饰器
    require_permission_func = get_require_permission()
    
    @require_permission_func('delete')
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        db, Project, User, ProjectMember, ProjectStatus, create_audit_log, UserRole, Bug = get_db_and_models()
        
        current_user_id = get_jwt_identity()
        current_user = db.session.query(User).get(current_user_id)
        
        print(f"删除项目请求: project_id={project_id}, current_user_id={current_user_id}, current_user_role={current_user.role}")
        
        # 查找项目
        project = db.session.query(Project).get(project_id)
        if not project:
            print(f"项目不存在: {project_id}")
            return jsonify({'error': '项目不存在'}), 404
        
        print(f"找到项目: {project.name}, owner_id={project.owner_id}")
        
        # 检查权限：只有管理员或创建者可以删除项目
        if current_user.role != UserRole.ADMIN.value and project.owner_id != current_user_id:
            print(f"权限不足: current_user_role={current_user.role}, project_owner_id={project.owner_id}")
            return jsonify({'error': '无权限删除此项目'}), 403
        
        print("权限检查通过，开始删除项目...")
        
        try:
            # 检查项目是否有关联Bug
            bugs = db.session.query(Bug).filter_by(project_id=project_id).all()
            bug_count = len(bugs)

            # 构建bug列表
            bug_list = []
            for bug in bugs:
                bug_list.append({
                    'id': bug.id,
                    'title': bug.title,
                    'status': bug.status.value if hasattr(bug.status, 'value') else str(bug.status),
                    'priority': bug.priority.value if hasattr(bug.priority, 'value') else str(bug.priority),
                    'severity': bug.severity.value if hasattr(bug.severity, 'value') else str(bug.severity),
                    'created_at': bug.created_at.isoformat() if bug.created_at else None
                })

            # 如果有关联Bug，返回列表供前端显示
            if bug_count > 0:
                return jsonify({
                    'error': f'该项目下还有 {bug_count} 个Bug未处理，请先删除后再删除项目',
                    'code': 'PROJECT_HAS_ITEMS',
                    'bug_count': bug_count,
                    'bug_list': bug_list
                }), 400
            
            # 创建log（删除前）
            create_audit_log(
                user_id=current_user_id,
                action='delete_project',
                resource_type='project',
                resource_id=project_id,
                details=f'删除项目: {project.name}',
                request=request
            )
            
            # 删除项目成员关系
            db.session.query(ProjectMember).filter_by(project_id=project_id).delete()
            
            # 删除项目
            db.session.delete(project)
            db.session.commit()
            
            print("项目删除成功")
            return jsonify({'message': '项目删除成功'}), 200
        except Exception as e:
            db.session.rollback()
            print(f"删除项目失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': "删除项目失败: " + str(e)}), 500
    
    return jwt_wrapped_function()