from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from collections import defaultdict
from logging_decorators import log_api_call, log_business_operation, handle_validation_errors, handle_error
from logging_config import get_log_manager
import enum

def get_enum_value(value):
    """安全获取枚举的值，如果是枚举则返回.value，否则返回原值"""
    if isinstance(value, enum.Enum):
        return value.value
    return value

def enum_dict_to_str_dict(d):
    """将以枚举为键的字典转换为以字符串为键的字典"""
    return {get_enum_value(k): v for k, v in d.items()}

def get_db():
    """延迟获取数据库实例，避免循环导入"""
    from enhanced_app import get_db_instance
    return get_db_instance()

def get_app():
    """延迟获取应用实例"""
    from enhanced_app import app
    return app

def get_models():
    """延迟获取数据库模型"""
    from enhanced_app import Bug, Project, ProjectMember, User, BugStatus, RequirementDocument, RequirementItem
    return Bug, Project, ProjectMember, User, BugStatus, RequirementDocument, RequirementItem

statistics_bp = Blueprint('statistics', __name__, url_prefix='/statistics')

# 获取仪表盘统计数据
@statistics_bp.route('/dashboard', methods=['GET'])
@log_api_call
@log_business_operation
@jwt_required()
def get_dashboard_stats():
    db = get_db()
    Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]

    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))

    log_manager = get_log_manager()
    try:
        log_manager.log_request(
            user_id=current_user_id,
            action='get_dashboard_statistics',
            details={
                'days': request.args.get('days', 30, type=int),
                'description': '获取仪表盘统计'
            }
        )
    except Exception as e:
        log_manager.log_error(f"记录请求日志失败: {str(e)}")

    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    if current_user.role == 'admin':
        project_ids = [p.id for p in Project.query.all()]
    else:
        project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]

    my_bugs = Bug.query.filter(
        Bug.assigned_to == current_user_id,
        Bug.status.in_([BugStatus.NEW.value, BugStatus.IN_PROGRESS.value])
    ).count()

    bugs_created_by_me = Bug.query.filter(
        Bug.reported_by == current_user_id,
        Bug.created_at >= start_date
    ).count()

    new_bugs = Bug.query.filter(
        Bug.created_at >= start_date,
        Bug.project_id.in_(project_ids)
    ).count()

    fixed_bugs = Bug.query.filter(
        Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value]),
        Bug.updated_at >= start_date,
        Bug.project_id.in_(project_ids)
    ).count()

    active_projects = Project.query.filter(
        Project.status.in_(['active', 'in_progress']),
        Project.id.in_(project_ids)
    ).count()

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    bug_activity = defaultdict(int)
    bugs = Bug.query.filter(
        Bug.updated_at >= seven_days_ago,
        Bug.project_id.in_(project_ids)
    ).all()

    for bug in bugs:
        date = bug.updated_at.strftime('%Y-%m-%d')
        bug_activity[date] += 1

    dates = [(seven_days_ago + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(8)]

    bug_activity_data = [bug_activity.get(date, 0) for date in dates]

    severity_distribution = defaultdict(int)
    all_bugs = Bug.query.filter(Bug.project_id.in_(project_ids)).all()
    for bug in all_bugs:
        severity_distribution[get_enum_value(bug.severity)] += 1

    priority_distribution = defaultdict(int)
    for bug in all_bugs:
        priority_distribution[get_enum_value(bug.priority)] += 1

    try:
        log_manager.log_business(
            "获取仪表盘统计",
            current_user_id=current_user_id,
            details={
                'my_bugs': my_bugs,
                'new_bugs': new_bugs,
                'fixed_bugs': fixed_bugs,
                'active_projects': active_projects,
                'days': days
            }
        )
    except Exception as e:
        log_manager.log_error(f"记录业务操作日志失败: {str(e)}")

    return jsonify({
        'summary': {
            'my_tasks': 0,
            'overdue_tasks': 0,
            'my_bugs': my_bugs,
            'bugs_created_by_me': bugs_created_by_me,
            'new_bugs': new_bugs,
            'fixed_bugs': fixed_bugs,
            'active_projects': active_projects,
            'my_completion_rate': 0
        },
        'project_progress': [],
        'activity_chart': {
            'dates': dates,
            'task_activity': [0] * 8,
            'bug_activity': bug_activity_data
        },
        'severity_distribution': {
            'low': severity_distribution.get('low', 0),
            'medium': severity_distribution.get('medium', 0),
            'high': severity_distribution.get('high', 0),
            'critical': severity_distribution.get('critical', 0)
        },
        'priority_distribution': {
            'low': priority_distribution.get('low', 0),
            'medium': priority_distribution.get('medium', 0),
            'high': priority_distribution.get('high', 0)
        }
    })

# 获取需求统计数据
@statistics_bp.route('/requirements', methods=['GET'])
@log_api_call
@log_business_operation
def get_requirements_statistics():
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func

    @jwt_required_func()
    def jwt_wrapped_function():
        Bug, Project, ProjectMember, User, BugStatus, RequirementDocument, RequirementItem = get_models()
        db = get_db()
        log_manager = get_log_manager()

        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)

        try:
            log_manager.log_request(
                f"获取需求统计",
                current_user_id=current_user_id,
                project_id=request.args.get('project_id')
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")

        project_id = request.args.get('project_id', type=int)

        query = RequirementDocument.query

        if current_user.role != 'admin':
            user_projects = db.session.query(ProjectMember.project_id).filter_by(user_id=current_user_id).subquery()
            query = query.filter(RequirementDocument.project_id.in_(user_projects))

        if project_id:
            query = query.filter_by(project_id=project_id)

        documents = query.all()

        status_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        total_items = 0
        completed_items = 0

        for doc in documents:
            status_counts[doc.status] = status_counts.get(doc.status, 0) + 1
            for item in doc.items:
                total_items += 1
                priority_counts[item.priority] = priority_counts.get(item.priority, 0) + 1
                if item.status in ['completed', 'verified']:
                    completed_items += 1

        total_requirements = total_items
        completion_rate = round((completed_items / total_requirements * 100) if total_requirements > 0 else 0, 1)

        try:
            log_manager.log_business(
                f"获取需求统计",
                user_id=current_user_id,
                project_id=project_id,
                details={
                    'total_requirements': total_requirements,
                    'completed_items': completed_items,
                    'completion_rate': completion_rate
                }
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")

        return jsonify({
            'total_requirements': total_requirements,
            'completed_requirements': completed_items,
            'completion_rate': completion_rate,
            'status_distribution': dict(status_counts),
            'priority_distribution': {str(k): v for k, v in priority_counts.items()}
        }), 200

    return jwt_wrapped_function()

# 获取缺陷统计数据
@statistics_bp.route('/bugs', methods=['GET'])
@log_api_call
@log_business_operation
def get_bug_statistics():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        log_manager = get_log_manager()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        try:
            log_manager.log_request(
                f"获取缺陷统计",
                current_user_id=current_user_id,
                project_id=request.args.get('project_id'),
                start_date=request.args.get('start_date'),
                end_date=request.args.get('end_date'),
                severity=request.args.get('severity'),
                assignee_id=request.args.get('assignee_id')
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 获取查询参数
        project_id = request.args.get('project_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        severity = request.args.get('severity')
        assignee_id = request.args.get('assignee_id', type=int)
        
        # 构建查询
        query = Bug.query
        
        # 管理员可以查看所有缺陷，其他用户只能查看自己参与项目的缺陷
        if current_user.role != 'admin':
            user_projects = db.session.query(ProjectMember.project_id).filter_by(user_id=current_user_id).subquery()
            query = query.filter(Bug.project_id.in_(user_projects))
        
        # 应用过滤条件
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(Bug.created_at >= start_dt)
            except ValueError:
                return jsonify({'error': '开始日期格式不正确'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(Bug.created_at <= end_dt)
            except ValueError:
                return jsonify({'error': '结束日期格式不正确'}), 400
        
        if severity:
            query = query.filter_by(severity=severity)
        
        if assignee_id:
            query = query.filter_by(assigned_to=assignee_id)
        
        # 状态分布统计
        status_counts = defaultdict(int)
        bugs = query.all()
        
        for bug in bugs:
            status_counts[bug.status.value] += 1
        
        # 严重程度分布统计
        severity_counts = defaultdict(int)
        for bug in bugs:
            severity_counts[bug.severity.value] += 1
        
        # 优先级分布统计
        priority_counts = defaultdict(int)
        for bug in bugs:
            priority_counts[bug.priority.value] += 1
        
        # 缺陷解决率统计
        total_bugs = len(bugs)
        resolved_bugs = sum(1 for b in bugs if b.status in [BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value])
        resolution_rate = round((resolved_bugs / total_bugs * 100) if total_bugs > 0 else 0, 1)
        
        # 平均修复时间统计（对于已修复的缺陷）
        fixed_bugs = [b for b in bugs if b.status in [BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value]]
        if fixed_bugs:
            total_fix_time = sum(
                (bug.resolved_at - bug.created_at).total_seconds() / 3600  # 转换为小时
                for bug in fixed_bugs if bug.resolved_at
            )
            avg_fix_time = round(total_fix_time / len(fixed_bugs), 1)
        else:
            avg_fix_time = 0
        
        # 模块分布统计
        module_counts = defaultdict(int)
        for bug in bugs:
            module_counts[bug.module or '未分类'] += 1
        
        # 按周统计缺陷创建数量
        weekly_bug_counts = defaultdict(int)
        for bug in bugs:
            week_start = bug.created_at - timedelta(days=bug.created_at.weekday())
            week_key = week_start.strftime('%Y-%W')
            weekly_bug_counts[week_key] += 1
        
        # 排序周数据
        sorted_weeks = sorted(weekly_bug_counts.keys())
        weekly_data = [{
            'week': week,
            'count': weekly_bug_counts[week]
        } for week in sorted_weeks]
        
        # 按日统计缺陷创建和关闭数量（最近30天）
        daily_bug_stats = []
        today = datetime.utcnow().date()
        for i in range(30):
            date = today - timedelta(days=29 - i)
            date_str = date.strftime('%Y-%m-%d')
            
            # 当日新增Bug数
            new_bugs = Bug.query.filter(
                Bug.created_at >= datetime.combine(date, datetime.min.time()),
                Bug.created_at < datetime.combine(date + timedelta(days=1), datetime.min.time())
            ).count()
            
            # 当日关闭Bug数
            closed_bugs = Bug.query.filter(
                Bug.status == BugStatus.CLOSED.value,
                Bug.closed_at >= datetime.combine(date, datetime.min.time()),
                Bug.closed_at < datetime.combine(date + timedelta(days=1), datetime.min.time())
            ).count()
            
            daily_bug_stats.append({
                'date': date_str,
                'new_bugs': new_bugs,
                'closed_bugs': closed_bugs
            })
        
        # 计算Bug重新打开率
        total_reopened = Bug.query.filter(
            Bug.status == BugStatus.REOPENED.value
        ).count()
        total_resolved = Bug.query.filter(
            Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value])
        ).count()
        reopen_rate = round((total_reopened / total_resolved * 100) if total_resolved > 0 else 0, 1)
        
        # 计算Bug年龄分布
        age_distribution = {
            '0-3天': 0,
            '4-7天': 0,
            '1-4周': 0,
            '>1月': 0
        }
        
        for bug in bugs:
            if bug.closed_at:
                age_days = (bug.closed_at - bug.created_at).days
            else:
                age_days = (datetime.utcnow() - bug.created_at).days
            
            if age_days <= 3:
                age_distribution['0-3天'] += 1
            elif age_days <= 7:
                age_distribution['4-7天'] += 1
            elif age_days <= 28:
                age_distribution['1-4周'] += 1
            else:
                age_distribution['>1月'] += 1
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"获取缺陷统计",
                user_id=current_user_id,
                project_id=project_id,
                details={
                    'total_bugs': total_bugs,
                    'resolved_bugs': resolved_bugs,
                    'resolution_rate': resolution_rate,
                    'avg_fix_time_hours': avg_fix_time,
                    'reopen_rate': reopen_rate,
                    'severity': severity,
                    'assignee_id': assignee_id,
                    'start_date': str(start_date) if start_date else None,
                    'end_date': str(end_date) if end_date else None
                }
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        return jsonify({
            'total_bugs': total_bugs,
            'resolved_bugs': resolved_bugs,
            'resolution_rate': resolution_rate,
            'avg_fix_time_hours': avg_fix_time,
            'status_distribution': enum_dict_to_str_dict(status_counts),
            'severity_distribution': enum_dict_to_str_dict(severity_counts),
            'priority_distribution': enum_dict_to_str_dict(priority_counts),
            'module_distribution': dict(module_counts),
            'weekly_bug_creation': weekly_data,
            'daily_bug_stats': daily_bug_stats,
            'reopen_rate': reopen_rate,
            'age_distribution': age_distribution
        }), 200
    
    # 调用JWT包装的函数
    return jwt_wrapped_function()

# 获取全局统计概览
@statistics_bp.route('/overview', methods=['GET'])
@log_api_call
@log_business_operation
def get_global_overview():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        log_manager = get_log_manager()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        try:
            log_manager.log_request(
                f"获取全局统计概览",
                current_user_id=current_user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 管理员可以查看所有数据，其他用户只能查看自己参与项目的数据
        if current_user.role == 'admin':
            # 获取所有项目ID
            project_ids = [p.id for p in Project.query.all()]
        else:
            # 获取用户参与的项目ID
            project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
        
        # 核心指标计算
        # 未解决Bug总数
        unresolved_bugs = Bug.query.filter(
            Bug.status != BugStatus.CLOSED.value,
            Bug.project_id.in_(project_ids)
        ).count()
        
        # 本日新增Bug数
        today = datetime.utcnow().date()
        today_new_bugs = Bug.query.filter(
            Bug.created_at >= datetime.combine(today, datetime.min.time()),
            Bug.created_at < datetime.combine(today + timedelta(days=1), datetime.min.time()),
            Bug.project_id.in_(project_ids)
        ).count()
        
        # 本日已关闭Bug数
        today_closed_bugs = Bug.query.filter(
            Bug.status == BugStatus.CLOSED.value,
            Bug.closed_at >= datetime.combine(today, datetime.min.time()),
            Bug.closed_at < datetime.combine(today + timedelta(days=1), datetime.min.time()),
            Bug.project_id.in_(project_ids)
        ).count()
        
        # Bug重新打开率
        total_reopened = Bug.query.filter(
            Bug.status == BugStatus.REOPENED.value,
            Bug.project_id.in_(project_ids)
        ).count()
        total_resolved = Bug.query.filter(
            Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value]),
            Bug.project_id.in_(project_ids)
        ).count()
        reopen_rate = round((total_reopened / total_resolved * 100) if total_resolved > 0 else 0, 1)
        
        # Bug状态分布
        status_distribution = {}
        for status in BugStatus:
            status_distribution[status.value] = Bug.query.filter(
                Bug.status == status.value,
                Bug.project_id.in_(project_ids)
            ).count()
        
        # 优先级分布
        priority_distribution = {}
        for priority in ['low', 'medium', 'high', 'urgent']:
            priority_distribution[priority] = Bug.query.filter(
                Bug.priority == priority,
                Bug.project_id.in_(project_ids)
            ).count()
        
        # 严重性分布
        severity_distribution = {}
        for severity in ['low', 'medium', 'high', 'critical']:
            severity_distribution[severity] = Bug.query.filter(
                Bug.severity == severity,
                Bug.project_id.in_(project_ids)
            ).count()
        
        # 模块Bug数量TOP10
        module_counts = {}
        for bug in Bug.query.filter(Bug.project_id.in_(project_ids)).all():
            module = bug.module or '未分类'
            if module in module_counts:
                module_counts[module] += 1
            else:
                module_counts[module] = 1
        
        # 排序并取TOP10
        top_modules = sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_modules_data = [{
            'module': module,
            'count': count
        } for module, count in top_modules]
        
        # 最近30天Bug趋势
        bug_trend = []
        for i in range(30):
            date = today - timedelta(days=29 - i)
            date_str = date.strftime('%Y-%m-%d')
            
            # 当日新增Bug数
            new_bugs = Bug.query.filter(
                Bug.created_at >= datetime.combine(date, datetime.min.time()),
                Bug.created_at < datetime.combine(date + timedelta(days=1), datetime.min.time()),
                Bug.project_id.in_(project_ids)
            ).count()
            
            # 当日关闭Bug数
            closed_bugs = Bug.query.filter(
                Bug.status == BugStatus.CLOSED.value,
                Bug.closed_at >= datetime.combine(date, datetime.min.time()),
                Bug.closed_at < datetime.combine(date + timedelta(days=1), datetime.min.time()),
                Bug.project_id.in_(project_ids)
            ).count()
            
            bug_trend.append({
                'date': date_str,
                'new_bugs': new_bugs,
                'closed_bugs': closed_bugs
            })
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"获取全局统计概览",
                current_user_id=current_user_id,
                unresolved_bugs=unresolved_bugs,
                today_new_bugs=today_new_bugs,
                today_closed_bugs=today_closed_bugs,
                reopen_rate=reopen_rate,
                total_projects=len(projects)
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        return jsonify({
            'core_metrics': {
                'unresolved_bugs': unresolved_bugs,
                'today_new_bugs': today_new_bugs,
                'today_closed_bugs': today_closed_bugs,
                'reopen_rate': reopen_rate
            },
            'status_distribution': status_distribution,
            'priority_distribution': priority_distribution,
            'severity_distribution': severity_distribution,
            'top_modules': top_modules_data,
            'bug_trend': bug_trend
        })
    
    return jwt_wrapped_function()

# 获取项目级统计
@statistics_bp.route('/projects', methods=['GET'])
@log_api_call
@log_business_operation
def get_projects_statistics():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"获取项目级统计",
                current_user_id=current_user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 管理员可以查看所有项目，其他用户只能查看自己参与的项目
        if current_user.role == 'admin':
            projects = Project.query.all()
        else:
            project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
            projects = Project.query.filter(Project.id.in_(project_ids)).all()
        
        # 项目Bug分布
        project_bug_distribution = []
        for project in projects:
            bug_count = Bug.query.filter(
                Bug.project_id == project.id,
                Bug.status != BugStatus.CLOSED.value
            ).count()
            
            project_bug_distribution.append({
                'project_id': project.id,
                'project_name': project.name,
                'bug_count': bug_count
            })
        
        # 项目Bug趋势对比（最近30天）
        project_bug_trends = {}
        today = datetime.utcnow().date()
        
        for project in projects:
            project_trend = []
            for i in range(30):
                date = today - timedelta(days=29 - i)
                date_str = date.strftime('%Y-%m-%d')
                
                new_bugs = Bug.query.filter(
                    Bug.project_id == project.id,
                    Bug.created_at >= datetime.combine(date, datetime.min.time()),
                    Bug.created_at < datetime.combine(date + timedelta(days=1), datetime.min.time())
                ).count()
                
                project_trend.append({
                    'date': date_str,
                    'new_bugs': new_bugs
                })
            
            project_bug_trends[project.name] = project_trend
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"获取项目级统计",
                current_user_id=current_user_id,
                total_projects=len(projects),
                project_bug_distribution_count=len(project_bug_distribution)
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        return jsonify({
            'project_bug_distribution': project_bug_distribution,
            'project_bug_trends': project_bug_trends
        })
    
    return jwt_wrapped_function()

# 获取开发者Bug统计
@statistics_bp.route('/developers', methods=['GET'])
@log_api_call
@log_business_operation
def get_developer_statistics():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"获取开发者Bug统计",
                current_user_id=current_user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 管理员可以查看所有开发者，其他用户只能查看自己团队的开发者
        if current_user.role == 'admin':
            developers = User.query.filter(User.role.in_(['developer', 'admin'])).all()
        else:
            # 获取用户参与的项目
            project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
            # 获取这些项目的所有开发者
            developer_ids = set()
            for project_id in project_ids:
                project_members = ProjectMember.query.filter_by(project_id=project_id).all()
                for member in project_members:
                    user = User.query.get(member.user_id)
                    if user and user.role in ['developer', 'admin']:
                        developer_ids.add(user.id)
            
            developers = User.query.filter(User.id.in_(developer_ids)).all()
        
        developer_stats = []
        for developer in developers:
            # 已指派Bug总数
            assigned_bugs = Bug.query.filter(
                Bug.assigned_to == developer.id
            ).count()
            
            # 已修复Bug总数
            fixed_bugs = Bug.query.filter(
                Bug.assigned_to == developer.id,
                Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value])
            ).count()
            
            # 重新打开Bug数
            reopened_bugs = Bug.query.filter(
                Bug.assigned_to == developer.id,
                Bug.status == BugStatus.REOPENED.value
            ).count()
            
            # 计算平均修复时长
            fixed_bug_list = Bug.query.filter(
                Bug.assigned_to == developer.id,
                Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value])
            ).all()
                
            total_fix_time = 0
            fix_count = 0
            for bug in fixed_bug_list:
                if bug.resolved_at:
                    fix_time = (bug.resolved_at - bug.created_at).total_seconds() / 3600  # 转换为小时
                    total_fix_time += fix_time
                    fix_count += 1
            
            avg_fix_time = round(total_fix_time / fix_count, 1) if fix_count > 0 else 0
            
            developer_stats.append({
                'user_id': developer.id,
                'username': developer.username,
                'full_name': f'{developer.first_name} {developer.last_name}',
                'assigned_bugs': assigned_bugs,
                'fixed_bugs': fixed_bugs,
                'reopened_bugs': reopened_bugs,
                'avg_fix_time_hours': avg_fix_time
            })
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"获取开发者Bug统计",
                current_user_id=current_user_id,
                total_developers=len(developers),
                developer_stats_count=len(developer_stats)
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        return jsonify({
            'developer_stats': developer_stats
        })
    
    return jwt_wrapped_function()

# 获取测试者Bug统计
@statistics_bp.route('/testers', methods=['GET'])
@log_api_call
@log_business_operation
def get_tester_statistics():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"获取测试者Bug统计",
                current_user_id=current_user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 管理员可以查看所有测试者，其他用户只能查看自己团队的测试者
        if current_user.role == 'admin':
            testers = User.query.filter(User.role == 'tester').all()
        else:
            # 获取用户参与的项目
            project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
            # 获取这些项目的所有测试者
            tester_ids = set()
            for project_id in project_ids:
                project_members = ProjectMember.query.filter_by(project_id=project_id).all()
                for member in project_members:
                    user = User.query.get(member.user_id)
                    if user and user.role == 'tester':
                        tester_ids.add(user.id)
            
            testers = User.query.filter(User.id.in_(tester_ids)).all()
        
        tester_stats = []
        for tester in testers:
            # 提交的Bug总数
            submitted_bugs = Bug.query.filter(
                Bug.reported_by == tester.id
            ).count()
            
            # 已验证关闭的Bug数
            verified_bugs = Bug.query.filter(
                Bug.verifier_id == tester.id,
                Bug.status == BugStatus.CLOSED.value
            ).count()
            
            # 发现的严重/致命Bug数
            critical_bugs = Bug.query.filter(
                Bug.reported_by == tester.id,
                Bug.severity.in_(['high', 'critical'])
            ).count()
            
            tester_stats.append({
                'user_id': tester.id,
                'username': tester.username,
                'full_name': f'{tester.first_name} {tester.last_name}',
                'submitted_bugs': submitted_bugs,
                'verified_bugs': verified_bugs,
                'critical_bugs': critical_bugs
            })
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"获取测试者Bug统计",
                current_user_id=current_user_id,
                total_testers=len(testers),
                tester_stats_count=len(tester_stats)
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        return jsonify({
            'tester_stats': tester_stats
        })
    
    return jwt_wrapped_function()

# 获取Bug生命周期分析
@statistics_bp.route('/bug-lifecycle', methods=['GET'])
@log_api_call
@log_business_operation
def get_bug_lifecycle():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"获取Bug生命周期分析",
                current_user_id=current_user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 管理员可以查看所有数据，其他用户只能查看自己参与项目的数据
        if current_user.role == 'admin':
            project_ids = [p.id for p in Project.query.all()]
        else:
            project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
        
        # 获取所有已关闭的Bug
        closed_bugs = Bug.query.filter(
            Bug.status == BugStatus.CLOSED.value,
            Bug.project_id.in_(project_ids),
            Bug.closed_at.isnot(None)
        ).all()
        
        # 计算生命周期时长（小时）
        lifecycle_hours = []
        for bug in closed_bugs:
            lifecycle = (bug.closed_at - bug.created_at).total_seconds() / 3600
            lifecycle_hours.append(lifecycle)
        
        # 计算平均时长和中位数时长
        if lifecycle_hours:
            avg_lifecycle = round(sum(lifecycle_hours) / len(lifecycle_hours), 1)
            # 计算中位数
            sorted_lifecycles = sorted(lifecycle_hours)
            n = len(sorted_lifecycles)
            if n % 2 == 0:
                median_lifecycle = round((sorted_lifecycles[n//2 - 1] + sorted_lifecycles[n//2]) / 2, 1)
            else:
                median_lifecycle = round(sorted_lifecycles[n//2], 1)
        else:
            avg_lifecycle = 0
            median_lifecycle = 0
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"获取Bug生命周期分析",
                current_user_id=current_user_id,
                total_closed_bugs=len(closed_bugs),
                avg_lifecycle_hours=avg_lifecycle,
                median_lifecycle_hours=median_lifecycle
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        return jsonify({
            'total_closed_bugs': len(closed_bugs),
            'avg_lifecycle_hours': avg_lifecycle,
            'median_lifecycle_hours': median_lifecycle
        })
    
    return jwt_wrapped_function()

# Bug根因分析
@statistics_bp.route('/bug-root-causes', methods=['GET'])
@log_api_call
@log_business_operation
def get_bug_root_causes():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"获取Bug根因分析",
                current_user_id=current_user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 管理员可以查看所有数据，其他用户只能查看自己参与项目的数据
        if current_user.role == 'admin':
            project_ids = [p.id for p in Project.query.all()]
        else:
            project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
        
        # 预定义的根因类别
        root_causes = {
            'code_error': '代码错误',
            'requirement_change': '需求变更',
            'environment_issue': '环境问题',
            'data_issue': '数据问题',
            'unknown': '未知'
        }
        
        # 统计每个根因类别的Bug数量
        root_cause_stats = {}
        for code, name in root_causes.items():
            # 这里假设Bug模型中有root_cause字段，如果没有，我们需要从描述中提取或使用默认值
            # 由于当前Bug模型中没有root_cause字段，我们先使用默认值'unknown'
            # 实际使用时，应该根据Bug模型的实际情况进行调整
            count = Bug.query.filter(
                Bug.project_id.in_(project_ids)
            ).count()
            # 这里我们暂时将所有Bug都归为unknown，实际使用时需要根据Bug模型的实际情况进行调整
            # 后续可以通过添加root_cause字段或从描述中提取来实现更准确的统计
            root_cause_stats[code] = 0
        
        # 实际使用时，应该根据Bug模型的实际情况进行调整
        # 例如，如果Bug模型中有root_cause字段，可以使用以下代码：
        # for bug in Bug.query.filter(Bug.project_id.in_(project_ids)).all():
        #     root_cause = bug.root_cause or 'unknown'
        #     root_cause_stats[root_cause] = root_cause_stats.get(root_cause, 0) + 1
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"获取Bug根因分析",
                current_user_id=current_user_id,
                total_bugs=sum(root_cause_stats.values()),
                root_cause_categories=len(root_causes)
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        # 由于当前模型中没有root_cause字段，我们先返回空数据
        # 后续可以根据实际情况进行调整
        return jsonify({
            'root_causes': root_causes,
            'stats': root_cause_stats
        })
    
    return jwt_wrapped_function()

# 重新打开Bug分析
@statistics_bp.route('/reopened-bugs', methods=['GET'])
@log_api_call
@log_business_operation
def get_reopened_bugs():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"获取重新打开Bug分析",
                current_user_id=current_user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 管理员可以查看所有数据，其他用户只能查看自己参与项目的数据
        if current_user.role == 'admin':
            project_ids = [p.id for p in Project.query.all()]
        else:
            project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
        
        # 获取所有重新打开的Bug
        reopened_bugs = Bug.query.filter(
            Bug.status == BugStatus.REOPENED.value,
            Bug.project_id.in_(project_ids)
        ).all()
        
        # 统计重新打开的Bug数量
        total_reopened = len(reopened_bugs)
        
        # 按原始修复者统计
        by_resolver = defaultdict(int)
        for bug in reopened_bugs:
            if bug.resolved_by:
                by_resolver[bug.resolved_by] += 1
        
        # 转换为详细信息
        resolver_stats = []
        for resolver_id, count in by_resolver.items():
            user = User.query.get(resolver_id)
            if user:
                resolver_stats.append({
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': f'{user.first_name} {user.last_name}',
                    'reopened_count': count
                })
        
        # 按重新打开的原因统计（假设Bug模型中有reopen_reason字段）
        # 由于当前Bug模型中没有reopen_reason字段，我们先返回空数据
        # 后续可以通过添加reopen_reason字段或从评论中提取来实现更准确的统计
        by_reason = {}
        
        # 按模块统计
        by_module = defaultdict(int)
        for bug in reopened_bugs:
            by_module[bug.module or '未分类'] += 1
        
        # 详细的重新打开Bug列表
        reopened_bug_list = []
        for bug in reopened_bugs:
            reopened_bug_list.append({
                'id': bug.id,
                'title': bug.title,
                'module': bug.module,
                'priority': bug.priority.value if hasattr(bug.priority, 'value') else str(bug.priority),
                'severity': bug.severity.value if hasattr(bug.severity, 'value') else str(bug.severity),
                'original_resolver': bug.resolver.username if bug.resolver else 'Unknown',
                'reporter': bug.reporter.username if bug.reporter else 'Unknown',
                'created_at': bug.created_at.isoformat(),
                'reopened_at': bug.updated_at.isoformat()
            })
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"获取重新打开Bug分析",
                current_user_id=current_user_id,
                total_reopened_bugs=total_reopened,
                resolver_count=len(resolver_stats),
                module_count=len(by_module)
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        return jsonify({
            'total_reopened': total_reopened,
            'by_resolver': resolver_stats,
            'by_reason': by_reason,
            'by_module': dict(by_module),
            'reopened_bugs': reopened_bug_list
        })
    
    return jwt_wrapped_function()

# 自定义报表生成器
@statistics_bp.route('/custom-report', methods=['POST'])
@log_api_call
@log_business_operation
def generate_custom_report():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"生成自定义报表",
                current_user_id=current_user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请提供报表配置'}), 400
        
        # 获取报表配置
        dimensions = data.get('dimensions', ['status'])
        metrics = data.get('metrics', ['count'])
        chart_type = data.get('chart_type', 'bar')
        filters = data.get('filters', {})
        
        # 管理员可以查看所有数据，其他用户只能查看自己参与项目的数据
        if current_user.role == 'admin':
            project_ids = [p.id for p in Project.query.all()]
        else:
            project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
        
        # 构建查询
        query = Bug.query.filter(Bug.project_id.in_(project_ids))
        
        # 应用过滤条件
        if 'project_id' in filters:
            query = query.filter(Bug.project_id == filters['project_id'])
        
        if 'start_date' in filters:
            try:
                start_dt = datetime.fromisoformat(filters['start_date'])
                query = query.filter(Bug.created_at >= start_dt)
            except ValueError:
                return jsonify({'error': '开始日期格式不正确'}), 400
        
        if 'end_date' in filters:
            try:
                end_dt = datetime.fromisoformat(filters['end_date'])
                query = query.filter(Bug.created_at <= end_dt)
            except ValueError:
                return jsonify({'error': '结束日期格式不正确'}), 400
        
        if 'status' in filters:
            query = query.filter(Bug.status == filters['status'])
        
        if 'priority' in filters:
            query = query.filter(Bug.priority == filters['priority'])
        
        if 'severity' in filters:
            query = query.filter(Bug.severity == filters['severity'])
        
        if 'module' in filters:
            query = query.filter(Bug.module == filters['module'])
        
        if 'assignee_id' in filters:
            query = query.filter(Bug.assigned_to == filters['assignee_id'])
        
        if 'reporter_id' in filters:
            query = query.filter(Bug.reported_by == filters['reporter_id'])
        
        bugs = query.all()
        
        # 生成报表数据
        report_data = {
            'dimensions': dimensions,
            'metrics': metrics,
            'chart_type': chart_type,
            'data': [],
            'summary': {}
        }
        
        # 计算指标
        total_count = len(bugs)
        report_data['summary']['total_count'] = total_count
        
        # 按维度分组
        grouped_data = defaultdict(dict)
        
        for bug in bugs:
            # 构建分组键
            group_key = tuple(getattr(bug, dim) for dim in dimensions)
            
            if group_key not in grouped_data:
                # 初始化分组数据
                group_data = {dim: getattr(bug, dim) for dim in dimensions}
                group_data['count'] = 0
                group_data['avg_fix_time'] = 0
                group_data['total_fix_time'] = 0
                group_data['fix_count'] = 0
                grouped_data[group_key] = group_data
            
            # 更新计数
            grouped_data[group_key]['count'] += 1
            
            # 计算平均修复时间
            if bug.resolved_at:
                fix_time = (bug.resolved_at - bug.created_at).total_seconds() / 3600  # 转换为小时
                grouped_data[group_key]['total_fix_time'] += fix_time
                grouped_data[group_key]['fix_count'] += 1
        
        # 计算平均修复时间
        for group_key, group_data in grouped_data.items():
            if group_data['fix_count'] > 0:
                group_data['avg_fix_time'] = round(group_data['total_fix_time'] / group_data['fix_count'], 1)
            else:
                group_data['avg_fix_time'] = 0
            
            report_data['data'].append(group_data)
        
        # 计算总体平均修复时间
        total_fix_time = sum(group['total_fix_time'] for group in grouped_data.values())
        total_fix_count = sum(group['fix_count'] for group in grouped_data.values())
        if total_fix_count > 0:
            report_data['summary']['avg_fix_time'] = round(total_fix_time / total_fix_count, 1)
        else:
            report_data['summary']['avg_fix_time'] = 0
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"生成自定义报表",
                current_user_id=current_user_id,
                total_bugs=len(bugs),
                dimensions=len(dimensions),
                metrics=len(metrics)
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        return jsonify(report_data)
    
    return jwt_wrapped_function()

# 获取项目统计数据
@statistics_bp.route('/projects/<int:project_id>', methods=['GET'])
@log_api_call
@log_business_operation
def get_project_statistics(project_id):
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"获取项目统计数据",
                current_user_id=current_user_id,
                project_id=project_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 查找项目
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        # 检查权限：管理员或项目成员可以查看项目统计
        if current_user.role != 'admin':
            member = ProjectMember.query.filter_by(
                project_id=project_id,
                user_id=current_user_id
            ).first()
            if not member:
                return jsonify({'error': '无权限查看此项目统计'}), 403

        
        # 获取项目缺陷统计
        total_bugs = Bug.query.filter_by(project_id=project_id).count()
        resolved_bugs = Bug.query.filter(
            Bug.project_id == project_id,
            Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value])
        ).count()
        
        bug_resolution_rate = round((resolved_bugs / total_bugs * 100) if total_bugs > 0 else 0, 1)
        
        # 获取项目成员工作量统计
        members = ProjectMember.query.filter_by(project_id=project_id).all()
        member_stats = []
        
        for member in members:
            user = User.query.get(member.user_id)
            if user:
                # 任务统计
                assigned_tasks = 0
                
                completed_user_tasks = 0
                
                # 缺陷统计
                assigned_bugs = Bug.query.filter(
                    Bug.project_id == project_id,
                    Bug.assigned_to == user.id
                ).count()
                
                resolved_bugs = Bug.query.filter(
                    Bug.project_id == project_id,
                    Bug.assigned_to == user.id,
                    Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value])
                ).count()
                
                member_stats.append({
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': f'{user.first_name} {user.last_name}',
                    'role': member.role,
                    'assigned_tasks': assigned_tasks,
                    'completed_tasks': completed_user_tasks,
                    'assigned_bugs': assigned_bugs,
                    'resolved_bugs': resolved_bugs
                })
        
        # 项目进度时间线（过去30天的完成情况）
        timeline_data = []
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=29-i)
            date_str = date.strftime('%Y-%m-%d')
            
            # 当日完成的任务
            daily_completed_tasks = 0
            
            # 当日解决的缺陷
            daily_resolved_bugs = Bug.query.filter(
                Bug.project_id == project_id,
                Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value]),
                Bug.updated_at >= date,
                Bug.updated_at < date + timedelta(days=1)
            ).count()
            
            timeline_data.append({
                'date': date_str,
                'completed_tasks': daily_completed_tasks,
                'resolved_bugs': daily_resolved_bugs
            })
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"获取项目统计数据",
                current_user_id=current_user_id,
                project_id=project_id,
                total_tasks=total_tasks,
                total_bugs=total_bugs,
                member_count=len(member_stats)
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        return jsonify({
            'project': {
                'id': project.id,
                'name': project.name,
                'status': project.status
            },
            'task_statistics': {
                'total': total_tasks,
                'completed': completed_tasks,
                'completion_rate': task_completion_rate
            },
            'bug_statistics': {
                'total': total_bugs,
                'resolved': resolved_bugs,
                'resolution_rate': bug_resolution_rate
            },
            'member_workload': member_stats,
            '30day_timeline': timeline_data
        }), 200
    
    return jwt_wrapped_function()

# 获取用户统计数据
@statistics_bp.route('/users/<int:user_id>', methods=['GET'])
@log_api_call
@log_business_operation
def get_user_statistics(user_id):
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        current_user = User.query.get(current_user_id)
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"获取用户统计数据",
                current_user_id=current_user_id,
                target_user_id=user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 查找用户
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查权限：用户只能查看自己的统计，管理员可以查看所有用户的统计
        if current_user.role != 'admin' and current_user_id != user_id:
            return jsonify({'error': '无权限查看其他用户的统计数据'}), 403
        
        # 默认时间范围为最近30天
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 用户任务统计
        assigned_tasks = 0
        
        completed_tasks = 0
        
        created_tasks = 0
        
        overdue_tasks = 0
        
        # 用户缺陷统计
        assigned_bugs = Bug.query.filter(
            Bug.assigned_to == user_id
        ).count()
        
        resolved_bugs = Bug.query.filter(
            Bug.assigned_to == user_id,
            Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value])
        ).count()
        
        created_bugs = Bug.query.filter(
            Bug.reported_by == user_id
        ).count()
        
        verified_bugs = Bug.query.filter(
            Bug.verifier_id == user_id,
            Bug.status == BugStatus.VERIFIED.value
        ).count()
        
        # 最近工作统计
        recent_tasks = []
        
        recent_bugs = Bug.query.filter(
            Bug.assigned_to == user_id,
            Bug.updated_at >= start_date
        ).order_by(Bug.updated_at.desc()).limit(5).all()
        
        # 转换最近工作数据
        recent_tasks_data = [{
            'id': task.id,
            'title': task.title,
            'project_name': task.project.name if task.project else None,
            'status': task.status.value if hasattr(task.status, 'value') else str(task.status),
            'updated_at': task.updated_at.isoformat() if task.updated_at else None
        } for task in recent_tasks]
        
        recent_bugs_data = [{
            'id': bug.id,
            'title': bug.title,
            'project_name': bug.project.name if bug.project else None,
            'status': bug.status.value if hasattr(bug.status, 'value') else str(bug.status),
            'severity': bug.severity.value if hasattr(bug.severity, 'value') else str(bug.severity),
            'updated_at': bug.updated_at.isoformat() if bug.updated_at else None
        } for bug in recent_bugs]
        
        # 工作效率趋势（按周）
        weekly_stats = []
        for i in range(5):  # 最近5周
            week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday()) - timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)
            
            # 本周完成的任务
            week_completed_tasks = 0
            
            # 本周解决的缺陷
            week_resolved_bugs = Bug.query.filter(
                Bug.assigned_to == user_id,
                Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value]),
                Bug.updated_at >= week_start,
                Bug.updated_at <= week_end
            ).count()
            
            weekly_stats.append({
                'week': week_start.strftime('%Y-%W'),
                'completed_tasks': week_completed_tasks,
                'resolved_bugs': week_resolved_bugs
            })
        
        # 反转以获得时间顺序
        weekly_stats.reverse()
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"获取用户统计数据",
                current_user_id=current_user_id,
                target_user_id=user_id,
                assigned_tasks=assigned_tasks,
                assigned_bugs=assigned_bugs,
                days=days
            )
        except Exception as e:
            log_manager.log_error(f"记录业务操作日志失败: {str(e)}")
        
        return jsonify({
            'user': {
                'id': target_user.id,
                'username': target_user.username,
                'full_name': f'{target_user.first_name} {target_user.last_name}'
            },
            'task_statistics': {
                'assigned': assigned_tasks,
                'completed': completed_tasks,
                'created': created_tasks,
                'overdue': overdue_tasks,
                'completion_rate': round((completed_tasks / assigned_tasks * 100) if assigned_tasks > 0 else 0, 1)
            },
            'bug_statistics': {
                'assigned': assigned_bugs,
                'resolved': resolved_bugs,
                'created': created_bugs,
                'verified': verified_bugs,
                'resolution_rate': round((resolved_bugs / assigned_bugs * 100) if assigned_bugs > 0 else 0, 1)
            },
            'recent_work': {
                'tasks': recent_tasks_data,
                'bugs': recent_bugs_data
            },
            'weekly_performance': weekly_stats
        }), 200
    
    return jwt_wrapped_function()

# 数据导出API
@statistics_bp.route('/export', methods=['POST'])
@log_api_call
@log_business_operation
@jwt_required()
def export_data():
    import pandas as pd
    from io import BytesIO
    from flask import send_file
    
    # 延迟导入数据库模型
    Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
    db = get_db()
    
    # 直接处理导出请求
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 记录请求日志
    log_manager = get_log_manager()
    try:
        log_manager.log_request(
            f"数据导出",
            user_id=current_user_id
        )
    except Exception as e:
        log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        data = request.get_json()
        
        if not data or 'export_type' not in data:
            return jsonify({'error': '请提供导出类型'}), 400
        
        export_type = data['export_type']
        project_id = data.get('project_id')
        format = data.get('format', 'json')  # 支持json, csv, excel
        
        # 根据导出类型获取数据
        if export_type == 'tasks':
            # 导出任务数据
            query = Bug.query
            if project_id:
                query = query.filter_by(project_id=project_id)
            
            tasks = query.all()
            
            export_data = []
            for task in tasks:
                export_data.append({
                    'id': task.id,
                    'title': task.title,
                    'status': task.status.value if hasattr(task.status, 'value') else str(task.status),
                    'priority': task.priority.value if hasattr(task.priority, 'value') else str(task.priority),
                    'project_id': task.project_id,
                    'assigned_to': task.assigned_to,
                    'created_by': task.created_by,
                    'progress': task.progress,
                    'estimated_hours': task.estimated_hours,
                    'actual_hours': task.actual_hours,
                    'created_at': task.created_at.isoformat() if task.created_at else '',
                    'updated_at': task.updated_at.isoformat() if task.updated_at else ''
                })
                
        elif export_type == 'bugs':
            # 导出缺陷数据
            query = Bug.query
            if project_id:
                query = query.filter_by(project_id=project_id)
            
            bugs = query.all()
            
            export_data = []
            for bug in bugs:
                export_data.append({
                    'id': bug.id,
                    'title': bug.title,
                    'status': bug.status.value if hasattr(bug.status, 'value') else str(bug.status),
                    'severity': bug.severity.value if hasattr(bug.severity, 'value') else str(bug.severity),
                    'priority': bug.priority.value if hasattr(bug.priority, 'value') else str(bug.priority),
                    'project_id': bug.project_id,
                    'assigned_to': bug.assigned_to,
                    'reported_by': bug.reported_by,
                    'resolved_by': bug.resolved_by,
                    'verifier_id': bug.verifier_id,
                    'module': bug.module,
                    'category': bug.category,
                    'issue_type': bug.issue_type,
                    'reproduce_frequency': bug.reproduce_frequency,
                    'found_build': bug.found_build,
                    'test_version': bug.test_version,
                    'created_at': bug.created_at.isoformat() if bug.created_at else '',
                    'updated_at': bug.updated_at.isoformat() if bug.updated_at else '',
                    'resolved_at': bug.resolved_at.isoformat() if bug.resolved_at else '',
                    'closed_at': bug.closed_at.isoformat() if bug.closed_at else ''
                })
                
        elif export_type == 'projects':
            # 导出项目数据（按项目详情字段导出）
            query = Project.query
            
            # 权限检查：管理员可以查看所有项目，其他用户只能查看自己参与的项目
            if current_user.role != 'admin':
                user_projects = db.session.query(ProjectMember.project_id).filter_by(user_id=current_user_id).subquery()
                query = query.filter(Project.id.in_(user_projects))
            
            projects = query.all()
            
            export_data = []
            for project in projects:
                # 计算项目统计
                total_tasks = 0
                completed_tasks = 0
                
                total_bugs = Bug.query.filter_by(project_id=project.id).count()
                resolved_bugs = Bug.query.filter(
                    Bug.project_id == project.id,
                    Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value])
                ).count()
                
                # 获取项目经理和创建者姓名
                owner_name = None
                manager_name = None
                try:
                    if project.owner:
                        owner_name = f'{project.owner.first_name} {project.owner.last_name}'.strip()
                except Exception:
                    pass
                try:
                    if project.manager:
                        manager_name = f'{project.manager.first_name} {project.manager.last_name}'.strip()
                except Exception:
                    pass
                
                # 获取项目成员信息
                members = ProjectMember.query.filter_by(project_id=project.id).all()
                members_info = []
                for m in members:
                    try:
                        member_name = f'{m.user.first_name} {m.user.last_name}'.strip() if m.user else ''
                        members_info.append(f"{member_name or m.user.username}({m.role})")
                    except Exception:
                        pass
                
                # 转换 cost 字段为字符串标识
                cost_value = project.cost
                if cost_value is None:
                    cost_str = ''
                elif cost_value == 0.0:
                    cost_str = 'normal'
                elif cost_value > 0:
                    cost_str = 'over'
                else:
                    cost_str = 'under'
                
                export_data.append({
                    'id': project.id,
                    'name': project.name,
                    'code': project.code,
                    'description': project.description,
                    'owner_id': project.owner_id,
                    'owner_name': owner_name,
                    'manager_id': project.manager_id,
                    'manager_name': manager_name,
                    'status': project.status,
                    'priority': project.priority,
                    'current_stage': project.current_stage,
                    'progress': project.progress,
                    'quality': project.quality,
                    'risk': project.risk,
                    'resources': project.resources,
                    'cost': cost_str,
                    'start_date': project.start_date.isoformat() if project.start_date else '',
                    'end_date': project.end_date.isoformat() if project.end_date else '',
                    'created_at': project.created_at.isoformat() if project.created_at else '',
                    'updated_at': project.updated_at.isoformat() if project.updated_at else '',
                    'project_type': project.project_type,
                    'client_name': project.client_name,
                    'client_contact': project.client_contact,
                    'contract_value': project.contract_value,
                    'budget': project.budget,
                    'actual_cost': project.actual_cost,
                    'estimated_hours': project.estimated_hours,
                    'actual_hours': project.actual_hours,
                    'team_size': project.team_size,
                    'technology_stack': project.technology_stack,
                    'tags': project.tags,
                    'milestones': project.milestones,
                    'versions': project.versions,
                    'modules': project.modules,
                    'members': ', '.join(members_info),
                    'member_count': len(members_info),
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'total_bugs': total_bugs,
                    'resolved_bugs': resolved_bugs
                })
        else:
            return jsonify({'error': '不支持的导出类型'}), 400
        
        # 根据格式导出数据
        if format == 'json':
            return jsonify({
                'message': '数据导出成功',
                'data': export_data,
                'export_type': export_type,
                'export_time': datetime.utcnow().isoformat(),
                'record_count': len(export_data)
            }), 200
        elif format in ['csv', 'excel']:
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 根据格式生成文件
            if format == 'csv':
                output = BytesIO()
                df.to_csv(output, index=False, encoding='utf-8-sig')
                output.seek(0)
                filename = f'{export_type}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
                return send_file(output, mimetype='text/csv', as_attachment=True, download_name=filename)
            elif format == 'excel':
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name=export_type)
                output.seek(0)
                filename = f'{export_type}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.xlsx'
                return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': '不支持的导出格式'}), 400
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"数据导出成功",
                user_id=current_user_id,
                details={
                    'export_type': export_type,
                    'format': format,
                    'record_count': len(export_data),
                    'project_id': project_id if 'project_id' in locals() else None
                }
            )
        except Exception as e:
            log_manager.log_error(f"记录业务日志失败: {str(e)}")

# 定时报告管理API
@statistics_bp.route('/scheduled-reports', methods=['GET'])
@log_api_call
@log_business_operation
def get_scheduled_reports():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"查询定时报告列表",
                current_user_id=current_user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        current_user = User.query.get(current_user_id)
        
        # 只有管理员可以查看所有定时报告，其他用户只能查看自己创建的
        if current_user.role == 'admin':
            # 这里应该查询定时报告表，但当前模型中没有，所以返回空列表
            # 后续可以添加定时报告模型
            scheduled_reports = []
        else:
            scheduled_reports = []
        
        return jsonify({
            'scheduled_reports': scheduled_reports
        })
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"查询定时报告列表成功",
                current_user_id=current_user_id,
                details={
                    'report_count': len(scheduled_reports),
                    'user_role': current_user.role
                }
            )
        except Exception as e:
            log_manager.log_error(f"记录业务日志失败: {str(e)}")
    
    return jwt_wrapped_function()

@statistics_bp.route('/scheduled-reports', methods=['POST'])
@log_api_call
@log_business_operation
def create_scheduled_report():
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"创建定时报告",
                current_user_id=current_user_id
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请提供定时报告配置'}), 400
        
        # 这里应该创建定时报告，但当前模型中没有定时报告表，所以返回成功
        # 后续可以添加定时报告模型和相关功能
        
        return jsonify({
            'message': '定时报告创建成功',
            'report_id': 1  # 临时返回，实际应该返回创建的报告ID
        }), 201
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"创建定时报告成功",
                current_user_id=current_user_id,
                details={
                    'report_id': 1,
                    'report_config': data
                }
            )
        except Exception as e:
            log_manager.log_error(f"记录业务日志失败: {str(e)}")
    
    return jwt_wrapped_function()

@statistics_bp.route('/scheduled-reports/<int:report_id>', methods=['PUT'])
@log_api_call
@log_business_operation
def update_scheduled_report(report_id):
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"更新定时报告",
                current_user_id=current_user_id,
                details={'report_id': report_id}
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请提供定时报告配置'}), 400
        
        # 这里应该更新定时报告，但当前模型中没有定时报告表，所以返回成功
        # 后续可以添加定时报告模型和相关功能
        
        return jsonify({
            'message': '定时报告更新成功'
        }), 200
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"更新定时报告成功",
                current_user_id=current_user_id,
                details={
                    'report_id': report_id,
                    'updated_config': data
                }
            )
        except Exception as e:
            log_manager.log_error(f"记录业务日志失败: {str(e)}")
    
    return jwt_wrapped_function()

@statistics_bp.route('/scheduled-reports/<int:report_id>', methods=['DELETE'])
@log_api_call
@log_business_operation
def delete_scheduled_report(report_id):
    # 延迟导入JWT装饰器和数据库模型
    from flask_jwt_extended import jwt_required as jwt_required_func, get_jwt_identity as get_jwt_identity_func
    
    @jwt_required_func()
    def jwt_wrapped_function():
        # 延迟导入数据库模型
        Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
        db = get_db()
        
        current_user_id = get_jwt_identity_func()
        
        # 记录请求日志
        log_manager = get_log_manager()
        try:
            log_manager.log_request(
                f"删除定时报告",
                current_user_id=current_user_id,
                details={'report_id': report_id}
            )
        except Exception as e:
            log_manager.log_error(f"记录请求日志失败: {str(e)}")
        
        # 这里应该删除定时报告，但当前模型中没有定时报告表，所以返回成功
        # 后续可以添加定时报告模型和相关功能
        
        return jsonify({
            'message': '定时报告删除成功'
        }), 200
        
        # 记录业务操作日志
        try:
            log_manager.log_business(
                f"删除定时报告成功",
                current_user_id=current_user_id,
                details={
                    'report_id': report_id
                }
            )
        except Exception as e:
            log_manager.log_error(f"记录业务日志失败: {str(e)}")
    
    return jwt_wrapped_function()

# 图表数据导出API (F-007-06)
@statistics_bp.route('/chart-export', methods=['POST'])
@log_api_call
@log_business_operation
@jwt_required()
def export_chart_data():
    """导出图表数据为图片或CSV"""
    import pandas as pd
    from io import BytesIO
    from flask import send_file
    
    current_user_id = get_jwt_identity()
    Bug, Project, ProjectMember, User, BugStatus = get_models()[:5]
    db = get_db()
    current_user = User.query.get(int(current_user_id))
    
    log_manager = get_log_manager()
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '请提供导出配置'}), 400
    
    chart_type = data.get('chart_type', 'dashboard')
    export_format = data.get('format', 'csv')
    date_range = data.get('date_range', 30)
    
    start_date = datetime.utcnow() - timedelta(days=date_range)
    
    if current_user.role == 'admin':
        project_ids = [p.id for p in Project.query.all()]
    else:
        project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
    
    chart_data = []
    
    if chart_type == 'dashboard':
        status_distribution = defaultdict(int)
        bugs = Bug.query.filter(Bug.project_id.in_(project_ids)).all()
        for bug in bugs:
            status_distribution[bug.status.value] += 1
        
        priority_distribution = defaultdict(int)
        for bug in bugs:
            priority_distribution[bug.priority.value] += 1
        
        severity_distribution = defaultdict(int)
        for bug in bugs:
            severity_distribution[bug.severity.value] += 1
        
        trend_data = []
        for i in range(date_range):
            date = datetime.utcnow().date() - timedelta(days=date_range - 1 - i)
            date_str = date.strftime('%Y-%m-%d')
            
            new_bugs = Bug.query.filter(
                Bug.created_at >= datetime.combine(date, datetime.min.time()),
                Bug.created_at < datetime.combine(date + timedelta(days=1), datetime.min.time()),
                Bug.project_id.in_(project_ids)
            ).count()
            
            closed_bugs = Bug.query.filter(
                Bug.status == BugStatus.CLOSED.value,
                Bug.closed_at >= datetime.combine(date, datetime.min.time()),
                Bug.closed_at < datetime.combine(date + timedelta(days=1), datetime.min.time()),
                Bug.project_id.in_(project_ids)
            ).count()
            
            trend_data.append({
                'date': date_str,
                'new_bugs': new_bugs,
                'closed_bugs': closed_bugs
            })
        
        chart_data = {
            'status_distribution': dict(status_distribution),
            'priority_distribution': dict(priority_distribution),
            'severity_distribution': dict(severity_distribution),
            'trend_data': trend_data
        }
    
    elif chart_type == 'tasks':
        status_distribution = defaultdict(int)
        tasks = []
        for task in tasks:
            status_distribution[task.status.value] += 1
        
        priority_distribution = defaultdict(int)
        for task in tasks:
            priority_distribution[task.priority.value] += 1
        
        chart_data = {
            'status_distribution': dict(status_distribution),
            'priority_distribution': dict(priority_distribution)
        }
    
    elif chart_type == 'projects':
        project_stats = []
        for project in Project.query.filter(Project.id.in_(project_ids)).all():
            total_tasks = 0
            completed_tasks = 0
            
            total_bugs = Bug.query.filter_by(project_id=project.id).count()
            resolved_bugs = Bug.query.filter(
                Bug.project_id == project.id,
                Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value])
            ).count()
            
            project_stats.append({
                'project_name': project.name,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'task_completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
                'total_bugs': total_bugs,
                'resolved_bugs': resolved_bugs,
                'bug_resolution_rate': round((resolved_bugs / total_bugs * 100) if total_bugs > 0 else 0, 1)
            })
        
        chart_data = {'project_stats': project_stats}
    
    else:
        return jsonify({'error': '不支持的图表类型'}), 400
    
    if export_format == 'json':
        return jsonify({
            'message': '图表数据导出成功',
            'chart_type': chart_type,
            'data': chart_data,
            'export_time': datetime.utcnow().isoformat()
        }), 200
    
    elif export_format in ['csv', 'excel']:
        flat_data = []
        
        if chart_type == 'dashboard':
            for key, value in chart_data.get('status_distribution', {}).items():
                flat_data.append({'维度': '状态', '分类': key, '数值': value})
            for key, value in chart_data.get('priority_distribution', {}).items():
                flat_data.append({'维度': '优先级', '分类': key, '数值': value})
            for key, value in chart_data.get('severity_distribution', {}).items():
                flat_data.append({'维度': '严重程度', '分类': key, '数值': value})
            for item in chart_data.get('trend_data', []):
                flat_data.append({'维度': '趋势', '分类': item['date'], '新增Bug': item['new_bugs'], '关闭Bug': item['closed_bugs']})
        
        elif chart_type == 'tasks':
            for key, value in chart_data.get('status_distribution', {}).items():
                flat_data.append({'维度': '任务状态', '分类': key, '数值': value})
            for key, value in chart_data.get('priority_distribution', {}).items():
                flat_data.append({'维度': '任务优先级', '分类': key, '数值': value})
        
        elif chart_type == 'projects':
            for item in chart_data.get('project_stats', []):
                flat_data.append(item)
        
        df = pd.DataFrame(flat_data)
        
        if export_format == 'csv':
            output = BytesIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            filename = f'{chart_type}_chart_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name=filename)
        
        elif export_format == 'excel':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=chart_type)
            output.seek(0)
            filename = f'{chart_type}_chart_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.xlsx'
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
    
    try:
        log_manager.log_business(
            f"图表数据导出成功",
            user_id=current_user_id,
            details={
                'chart_type': chart_type,
                'export_format': export_format
            }
        )
    except Exception as e:
        log_manager.log_error(f"记录业务日志失败: {str(e)}")