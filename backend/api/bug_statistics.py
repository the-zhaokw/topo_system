"""
Bug管理模块统计功能API
按照需求文档实现完整的统计功能
支持多维度筛选和图表配置
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from collections import defaultdict
import json

def get_db():
    """延迟获取数据库实例，避免循环导入"""
    from enhanced_app import get_db_instance
    return get_db_instance()

def get_models():
    """延迟获取数据库模型"""
    import enhanced_app
    Task = enhanced_app.Task
    Bug = enhanced_app.Bug
    Project = enhanced_app.Project
    ProjectMember = enhanced_app.ProjectMember
    User = enhanced_app.User
    BugStatus = enhanced_app.BugStatus
    TaskStatus = enhanced_app.TaskStatus
    Severity = enhanced_app.Severity
    return Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity

def get_require_permission():
    from enhanced_app import require_permission
    return require_permission

bug_statistics_bp = Blueprint('bug_statistics', __name__, url_prefix='/bug-statistics')

ROOT_CAUSE_CATEGORIES = [
    '代码错误',
    '需求变更', 
    '环境问题',
    '数据问题',
    '未知'
]

BUG_AGE_RANGES = [
    {'name': '0-3天', 'min': 0, 'max': 3},
    {'name': '4-7天', 'min': 4, 'max': 7},
    {'name': '1-4周', 'min': 8, 'max': 28},
    {'name': '>1月', 'min': 29, 'max': None}
]

BUG_TYPE_OPTIONS = ['功能缺陷', '界面优化', '性能问题', '兼容性问题', '安全漏洞', '需求变更']
SEVERITY_OPTIONS = ['critical', 'high', 'medium', 'low', 'blocker']
PRIORITY_OPTIONS = ['urgent', 'high', 'medium', 'low']
STATUS_OPTIONS = ['new', 'assigned', 'in_progress', 'resolved', 'closed', 'rejected', 'reopened']

# 全局统计概览仪表盘
@bug_statistics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_bug_dashboard():
    """获取Bug统计仪表盘数据 - 3.1.全局统计概览仪表盘"""
    
    # 延迟导入数据库模型
    db = get_db()
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    # 获取时间范围参数
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 权限过滤：获取用户有权限访问的项目
    if current_user.role == 'admin':
        project_ids = [p.id for p in Project.query.all()]
    else:
        project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
    
    if not project_ids:
        return jsonify({'error': '没有可访问的项目'}), 403
    
    # 3.1.1 核心指标卡
    # 未解决Bug总数
    unresolved_bugs = Bug.query.filter(
        Bug.status.notin_([BugStatus.CLOSED.value]),
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
    
    # Bug重新打开率（周期内）
    period_start = start_date
    reopened_bugs = Bug.query.filter(
        Bug.status == BugStatus.REOPENED.value,
        Bug.updated_at >= period_start,
        Bug.project_id.in_(project_ids)
    ).count()
    
    fixed_bugs_in_period = Bug.query.filter(
        Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value]),
        Bug.updated_at >= period_start,
        Bug.project_id.in_(project_ids)
    ).count()
    
    reopen_rate = round((reopened_bugs / fixed_bugs_in_period * 100) if fixed_bugs_in_period > 0 else 0, 1)
    
    # 3.1.2 Bug趋势图
    bug_trend_data = []
    for i in range(days):
        date = today - timedelta(days=days - 1 - i)
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
        
        bug_trend_data.append({
            'date': date_str,
            'new_bugs': new_bugs,
            'closed_bugs': closed_bugs
        })
    
    # 3.1.3 Bug状态分布
    status_distribution = defaultdict(int)
    all_bugs = Bug.query.filter(Bug.project_id.in_(project_ids)).all()
    for bug in all_bugs:
        status_distribution[bug.status] += 1
    
    # 3.1.4 优先级/严重性分布
    priority_distribution = defaultdict(int)
    severity_distribution = defaultdict(int)
    for bug in all_bugs:
        priority_distribution[bug.priority] += 1
        severity_distribution[bug.severity] += 1
    
    # 3.1.5 模块Bug数量TOP
    module_distribution = defaultdict(int)
    for bug in all_bugs:
        module_name = bug.module or '未分类'
        module_distribution[module_name] += 1
    
    # 取前10个模块
    top_modules = sorted(module_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify({
        'core_metrics': {
            'unresolved_bugs': unresolved_bugs,
            'today_new_bugs': today_new_bugs,
            'today_closed_bugs': today_closed_bugs,
            'reopen_rate': reopen_rate
        },
        'trend_data': bug_trend_data,
        'status_distribution': dict(status_distribution),
        'priority_distribution': dict(priority_distribution),
        'severity_distribution': dict(severity_distribution),
        'top_modules': [{'module': k, 'count': v} for k, v in top_modules]
    })

# 项目级统计
@bug_statistics_bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_bug_statistics(project_id):
    """获取项目级Bug统计 - 3.2.项目级统计"""
    
    # 延迟导入数据库模型
    db = get_db()
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    # 检查项目访问权限
    project = Project.query.get_or_404(project_id)
    if current_user.role != 'admin':
        member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user_id
        ).first()
        if not member:
            return jsonify({'error': '无权限访问此项目'}), 403
    
    # 获取时间范围参数
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 3.2.1 项目Bug分布（按状态）
    status_distribution = defaultdict(int)
    project_bugs = Bug.query.filter_by(project_id=project_id).all()
    for bug in project_bugs:
        status_distribution[bug.status] += 1
    
    # 3.2.2 项目Bug趋势对比（单项目趋势）
    trend_data = []
    for i in range(days):
        date = datetime.utcnow().date() - timedelta(days=days - 1 - i)
        date_str = date.strftime('%Y-%m-%d')
        
        new_bugs = Bug.query.filter(
            Bug.project_id == project_id,
            Bug.created_at >= datetime.combine(date, datetime.min.time()),
            Bug.created_at < datetime.combine(date + timedelta(days=1), datetime.min.time())
        ).count()
        
        closed_bugs = Bug.query.filter(
            Bug.project_id == project_id,
            Bug.status == BugStatus.CLOSED.value,
            Bug.closed_at >= datetime.combine(date, datetime.min.time()),
            Bug.closed_at < datetime.combine(date + timedelta(days=1), datetime.min.time())
        ).count()
        
        trend_data.append({
            'date': date_str,
            'new_bugs': new_bugs,
            'closed_bugs': closed_bugs
        })
    
    # 3.2.3 项目Bug年龄分析
    age_distribution = defaultdict(int)
    today = datetime.utcnow()
    
    for bug in project_bugs:
        if bug.status in [BugStatus.CLOSED.value]:
            # 已关闭的Bug，计算从创建到关闭的天数
            if bug.closed_at:
                age_days = (bug.closed_at - bug.created_at).days
            else:
                age_days = (today - bug.created_at).days
        else:
            # 未关闭的Bug，计算当前年龄
            age_days = (today - bug.created_at).days
        
        # 分配到年龄区间
        for age_range in BUG_AGE_RANGES:
            if age_range['max'] is None:
                if age_days >= age_range['min']:
                    age_distribution[age_range['name']] += 1
                    break
            elif age_range['min'] <= age_days <= age_range['max']:
                age_distribution[age_range['name']] += 1
                break
    
    return jsonify({
        'project': {
            'id': project.id,
            'name': project.name,
            'code': project.code
        },
        'status_distribution': dict(status_distribution),
        'trend_data': trend_data,
        'age_distribution': dict(age_distribution)
    })

# 个人/团队效能统计
@bug_statistics_bp.route('/developer-performance', methods=['GET'])
@jwt_required()
def get_developer_performance():
    """获取开发者Bug统计 - 3.3.1 开发者Bug统计"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    # 获取时间范围参数
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 权限过滤：获取用户有权限访问的项目
    if current_user.role == 'admin':
        project_ids = [p.id for p in Project.query.all()]
        developers = User.query.filter(User.role.in_(['developer', 'admin'])).all()
    else:
        project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
        # 获取用户所在项目的开发者
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
        # 已指派Bug总数（周期内）
        assigned_bugs = Bug.query.filter(
            Bug.assigned_to == developer.id,
            Bug.assigned_to != None,
            Bug.project_id.in_(project_ids)
        ).count()
        
        # 已修复Bug总数（周期内）
        fixed_bugs = Bug.query.filter(
            Bug.assigned_to == developer.id,
            Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value]),
            Bug.resolved_at >= start_date,
            Bug.project_id.in_(project_ids)
        ).count()
        
        # 平均修复时长（仅计算已关闭的Bug）
        closed_bugs = Bug.query.filter(
            Bug.assigned_to == developer.id,
            Bug.status == BugStatus.CLOSED.value,
            Bug.resolved_at >= start_date,
            Bug.project_id.in_(project_ids)
        ).all()

        total_fix_time = 0
        fix_count = 0
        for bug in closed_bugs:
            if bug.resolved_at and bug.created_at:
                fix_time = (bug.resolved_at - bug.created_at).total_seconds() / 3600  # 转换为小时
                total_fix_time += fix_time
                fix_count += 1
        
        avg_fix_time = round(total_fix_time / fix_count, 1) if fix_count > 0 else 0
        
        # 重新打开Bug数
        reopened_bugs = Bug.query.filter(
            Bug.assigned_to == developer.id,
            Bug.status == BugStatus.REOPENED.value,
            Bug.updated_at >= start_date,
            Bug.project_id.in_(project_ids)
        ).count()
        
        developer_stats.append({
            'developer_id': developer.id,
            'developer_name': f'{developer.first_name or ""} {developer.last_name or ""}'.strip() or developer.username,
            'assigned_bugs': assigned_bugs,
            'fixed_bugs': fixed_bugs,
            'avg_fix_time': avg_fix_time,
            'reopened_bugs': reopened_bugs
        })
    
    return jsonify({'developers': developer_stats})

# 测试者Bug统计
@bug_statistics_bp.route('/tester-performance', methods=['GET'])
@jwt_required()
def get_tester_performance():
    """获取测试者Bug统计 - 3.3.2 测试者Bug统计"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    # 获取时间范围参数
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 权限过滤：获取用户有权限访问的项目
    if current_user.role == 'admin':
        project_ids = [p.id for p in Project.query.all()]
        testers = User.query.filter(User.role == 'tester').all()
    else:
        project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
        # 获取用户所在项目的测试者
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
            Bug.reported_by == tester.id,
            Bug.created_at >= start_date,
            Bug.project_id.in_(project_ids)
        ).count()
        
        # 已验证关闭的Bug数
        verified_bugs = Bug.query.filter(
            Bug.verifier_id == tester.id,
            Bug.status == BugStatus.CLOSED.value,
            Bug.closed_at >= start_date,
            Bug.project_id.in_(project_ids)
        ).count()
        
        # 发现的严重/致命Bug数
        critical_bugs = Bug.query.filter(
            Bug.reported_by == tester.id,
            Bug.severity.in_(['high', 'critical']),
            Bug.created_at >= start_date,
            Bug.project_id.in_(project_ids)
        ).count()
        
        tester_stats.append({
            'tester_id': tester.id,
            'tester_name': f'{tester.first_name or ""} {tester.last_name or ""}'.strip() or tester.username,
            'submitted_bugs': submitted_bugs,
            'verified_bugs': verified_bugs,
            'critical_bugs': critical_bugs
        })
    
    return jsonify({'testers': tester_stats})

# Bug根因分析
@bug_statistics_bp.route('/root-cause-analysis', methods=['GET'])
@jwt_required()
def get_root_cause_analysis():
    """获取Bug根因分析 - 3.4.2 Bug根因分析"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    # 权限过滤：获取用户有权限访问的项目
    if current_user.role == 'admin':
        project_ids = [p.id for p in Project.query.all()]
    else:
        project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
    
    # 根因分布统计
    root_cause_distribution = defaultdict(int)
    all_bugs = Bug.query.filter(Bug.project_id.in_(project_ids)).all()
    
    for bug in all_bugs:
        root_cause = bug.root_cause or '未知'
        root_cause_distribution[root_cause] += 1
    
    # 确保所有根因类别都有数据
    for category in ROOT_CAUSE_CATEGORIES:
        if category not in root_cause_distribution:
            root_cause_distribution[category] = 0
    
    return jsonify({
        'root_cause_distribution': dict(root_cause_distribution),
        'categories': ROOT_CAUSE_CATEGORIES
    })

# 重新打开Bug分析
@bug_statistics_bp.route('/reopen-analysis', methods=['GET'])
@jwt_required()
def get_reopen_analysis():
    """获取重新打开Bug分析 - 3.4.3 重新打开Bug分析"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    # 获取时间范围参数
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 权限过滤：获取用户有权限访问的项目
    if current_user.role == 'admin':
        project_ids = [p.id for p in Project.query.all()]
    else:
        project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
    
    # 重新打开Bug列表
    reopened_bugs = Bug.query.filter(
        Bug.status == BugStatus.REOPENED.value,
        Bug.updated_at >= start_date,
        Bug.project_id.in_(project_ids)
    ).all()
    
    # 按原始修复者统计
    resolver_reopen_stats = defaultdict(int)
    for bug in reopened_bugs:
        resolver_name = bug.resolver.username if bug.resolver else '未知'
        resolver_reopen_stats[resolver_name] += 1
    
    # 按根因统计
    root_cause_reopen_stats = defaultdict(int)
    for bug in reopened_bugs:
        root_cause = bug.root_cause or '未知'
        root_cause_reopen_stats[root_cause] += 1
    
    # 重新打开Bug详细信息
    reopen_details = []
    for bug in reopened_bugs:
        reopen_details.append({
            'bug_id': bug.id,
            'title': bug.title,
            'resolver': bug.resolver.username if bug.resolver else '未知',
            'root_cause': bug.root_cause or '未知',
            'reopen_count': bug.reopen_count,
            'last_reopen_at': bug.last_reopen_at.isoformat() if bug.last_reopen_at else None
        })
    
    return jsonify({
        'reopened_bugs_count': len(reopened_bugs),
        'resolver_reopen_stats': dict(resolver_reopen_stats),
        'root_cause_reopen_stats': dict(root_cause_reopen_stats),
        'reopen_details': reopen_details
    })

# 数据导出接口
@bug_statistics_bp.route('/export', methods=['GET'])
@jwt_required()
def export_bug_statistics():
    """导出Bug统计数据 - 3.5.2 原始数据导出"""
    export_type = request.args.get('type', 'csv')  # csv or json
    stats_type = request.args.get('stats_type', 'dashboard')  # dashboard, project, developer, etc.
    
    # 根据统计类型调用相应的统计函数
    if stats_type == 'dashboard':
        result = get_bug_dashboard()
    elif stats_type == 'project':
        project_id = request.args.get('project_id', type=int)
        if not project_id:
            return jsonify({'error': '缺少项目ID参数'}), 400
        result = get_project_bug_statistics(project_id)
    else:
        return jsonify({'error': '不支持的统计类型'}), 400
    
    # 这里应该实现具体的导出逻辑
    # 由于时间关系，暂时返回JSON格式的数据
    return result

# 自定义报表生成器API
@bug_statistics_bp.route('/custom-report/generate', methods=['POST'])
@jwt_required()
def generate_custom_report():
    """生成自定义报表 - 3.6.1 自定义报表生成器"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '缺少请求数据'}), 400
    
    name = data.get('name', '自定义报表')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    project_ids = data.get('project_ids', [])
    statuses = data.get('statuses', [])
    charts = data.get('charts', [])
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    # 权限过滤：获取用户有权限访问的项目
    if current_user.role == 'admin':
        accessible_projects = Project.query.all()
    else:
        accessible_projects = Project.query.join(ProjectMember).filter(
            ProjectMember.user_id == current_user_id
        ).all()
    
    accessible_project_ids = [p.id for p in accessible_projects]
    
    # 如果指定了项目ID，过滤掉无权限的项目
    if project_ids:
        project_ids = [pid for pid in project_ids if pid in accessible_project_ids]
    else:
        project_ids = accessible_project_ids
    
    # 构建查询条件
    query = Bug.query.filter(Bug.project_id.in_(project_ids))
    
    if start_date:
        query = query.filter(Bug.created_at >= start_date)
    if end_date:
        query = query.filter(Bug.created_at <= end_date)
    if statuses:
        query = query.filter(Bug.status.in_(statuses))
    
    bugs = query.all()
    
    # 生成图表数据
    chart_data = []
    for chart_config in charts:
        chart_type = chart_config.get('type', 'line')
        dimension = chart_config.get('dimension', 'trend')
        title = chart_config.get('title', '自定义图表')
        
        chart_option = generate_chart_option(chart_type, dimension, bugs, start_date, end_date)
        
        chart_data.append({
            'type': chart_type,
            'dimension': dimension,
            'title': title,
            'option': chart_option
        })
    
    return jsonify({
        'name': name,
        'charts': chart_data,
        'total_bugs': len(bugs),
        'generated_at': datetime.utcnow().isoformat()
    })

def generate_chart_option(chart_type, dimension, bugs, start_date, end_date):
    """根据配置生成ECharts图表选项"""
    
    if dimension == 'status':
        # Bug状态分布
        status_counts = defaultdict(int)
        for bug in bugs:
            status = bug.status
            status_counts[status] += 1
        
        return {
            'title': {'text': 'Bug状态分布', 'left': 'center'},
            'tooltip': {'trigger': 'item'},
            'series': [{
                'name': 'Bug状态',
                'type': 'pie',
                'radius': '50%',
                'data': [{'value': count, 'name': status} for status, count in status_counts.items()],
                'emphasis': {'itemStyle': {'shadowBlur': 10, 'shadowOffsetX': 0, 'shadowColor': 'rgba(0, 0, 0, 0.5)'}}
            }]
        }
    
    elif dimension == 'priority':
        # 优先级分布
        priority_counts = defaultdict(int)
        for bug in bugs:
            priority = bug.priority.value
            priority_counts[priority] += 1
        
        return {
            'title': {'text': 'Bug优先级分布', 'left': 'center'},
            'tooltip': {'trigger': 'item'},
            'series': [{
                'name': 'Bug优先级',
                'type': 'pie',
                'radius': '50%',
                'data': [{'value': count, 'name': priority} for priority, count in priority_counts.items()],
                'emphasis': {'itemStyle': {'shadowBlur': 10, 'shadowOffsetX': 0, 'shadowColor': 'rgba(0, 0, 0, 0.5)'}}
            }]
        }
    
    elif dimension == 'trend':
        # 趋势分析
        from collections import defaultdict
        import datetime
        
        # 按日期统计Bug数量
        date_counts = defaultdict(int)
        for bug in bugs:
            date = bug.created_at.date()
            date_counts[date] += 1
        
        # 生成日期序列
        if start_date and end_date:
            start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            dates = [(start + datetime.timedelta(days=x)) for x in range((end - start).days + 1)]
        else:
            dates = sorted(date_counts.keys())
        
        x_data = [d.strftime('%Y-%m-%d') for d in dates]
        y_data = [date_counts.get(d, 0) for d in dates]
        
        return {
            'title': {'text': 'Bug趋势分析', 'left': 'center'},
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'category', 'data': x_data},
            'yAxis': {'type': 'value'},
            'series': [{
                'name': 'Bug数量',
                'type': chart_type,
                'data': y_data,
                'smooth': True
            }]
        }
    
    else:
        # 默认图表
        return {
            'title': {'text': '自定义图表', 'left': 'center'},
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'category', 'data': ['数据1', '数据2', '数据3']},
            'yAxis': {'type': 'value'},
            'series': [{
                'name': '示例数据',
                'type': chart_type,
                'data': [10, 20, 15]
            }]
        }

# 报表模板管理API
@bug_statistics_bp.route('/custom-report/templates', methods=['GET', 'POST'])
@jwt_required()
def manage_report_templates():
    """报表模板管理 - 3.6.2 报表模板管理"""
    if request.method == 'GET':
        # 获取模板列表（这里简化实现，实际应该存储到数据库）
        templates = [
            {
                'id': 1,
                'name': '默认仪表盘模板',
                'config': {
                    'name': '默认仪表盘',
                    'charts': [
                        {'type': 'line', 'title': 'Bug趋势分析', 'dimension': 'trend'},
                        {'type': 'pie', 'title': 'Bug状态分布', 'dimension': 'status'}
                    ]
                },
                'created_at': '2024-01-01T00:00:00Z'
            }
        ]
        return jsonify({'templates': templates})
    
    elif request.method == 'POST':
        # 保存模板
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': '缺少模板名称'}), 400
        
        # 这里应该将模板保存到数据库
        # 简化实现，返回成功响应
        return jsonify({'message': '模板保存成功', 'template_id': 2})

@bug_statistics_bp.route('/custom-report/templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_report_template(template_id):
    """删除报表模板"""
    # 这里应该从数据库删除模板
    # 简化实现，返回成功响应
    return jsonify({'message': '模板删除成功'})

# Bug生命周期分析
@bug_statistics_bp.route('/lifecycle-analysis', methods=['GET'])
@jwt_required()
def get_bug_lifecycle_analysis():
    """获取Bug生命周期分析 - 3.3.3 Bug生命周期分析"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    # 获取筛选参数
    project_id = request.args.get('project_id', type=int)
    module = request.args.get('module')
    
    # 权限过滤：获取用户有权限访问的项目
    if current_user.role == 'admin':
        project_ids = [p.id for p in Project.query.all()]
    else:
        project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
    
    # 构建查询条件
    query = Bug.query.filter(Bug.project_id.in_(project_ids))
    
    if project_id and project_id in project_ids:
        query = query.filter(Bug.project_id == project_id)
    
    if module:
        query = query.filter(Bug.module == module)
    
    # 只统计已关闭的Bug
    closed_bugs = query.filter(Bug.status == BugStatus.CLOSED.value).all()
    
    # 计算生命周期时长（从创建到关闭的天数）
    lifecycle_durations = []
    for bug in closed_bugs:
        if bug.closed_at and bug.created_at:
            duration_days = (bug.closed_at - bug.created_at).days
            lifecycle_durations.append(duration_days)
    
    # 计算统计指标
    if lifecycle_durations:
        avg_lifecycle = round(sum(lifecycle_durations) / len(lifecycle_durations), 1)
        median_lifecycle = sorted(lifecycle_durations)[len(lifecycle_durations) // 2]
        min_lifecycle = min(lifecycle_durations)
        max_lifecycle = max(lifecycle_durations)
    else:
        avg_lifecycle = 0
        median_lifecycle = 0
        min_lifecycle = 0
        max_lifecycle = 0
    
    # 生命周期分布统计（按天数区间）
    lifecycle_distribution = defaultdict(int)
    for duration in lifecycle_durations:
        if duration <= 1:
            lifecycle_distribution['1天内'] += 1
        elif duration <= 3:
            lifecycle_distribution['2-3天'] += 1
        elif duration <= 7:
            lifecycle_distribution['4-7天'] += 1
        elif duration <= 14:
            lifecycle_distribution['8-14天'] += 1
        elif duration <= 30:
            lifecycle_distribution['15-30天'] += 1
        else:
            lifecycle_distribution['30天以上'] += 1
    
    return jsonify({
        'total_closed_bugs': len(closed_bugs),
        'lifecycle_stats': {
            'average_days': avg_lifecycle,
            'median_days': median_lifecycle,
            'min_days': min_lifecycle,
            'max_days': max_lifecycle
        },
        'lifecycle_distribution': dict(lifecycle_distribution),
        'filters': {
            'project_id': project_id,
            'module': module
        }
    })

# 自定义报表导出
@bug_statistics_bp.route('/custom-report/export', methods=['POST'])
@jwt_required()
def export_custom_report():
    """导出自定义报表 - 3.6.3 报表导出"""
    data = request.get_json()
    if not data:
        return jsonify({'error': '缺少请求数据'}), 400
    
    # 这里应该实现报表导出逻辑
    # 简化实现，返回成功响应
    return jsonify({
        'message': '报表导出成功',
        'download_url': '/api/bug-statistics/export/custom-report.pdf'
    })

@bug_statistics_bp.route('/filter-options', methods=['GET'])
@jwt_required()
def get_filter_options():
    """获取筛选选项列表"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    if current_user.role == 'admin':
        projects = Project.query.all()
    else:
        project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
        projects = Project.query.filter(Project.id.in_(project_ids)).all() if project_ids else []
    
    users = User.query.all()
    
    return jsonify({
        'projects': [{'id': p.id, 'name': p.name, 'code': p.code} for p in projects],
        'bug_types': BUG_TYPE_OPTIONS,
        'severities': SEVERITY_OPTIONS,
        'priorities': PRIORITY_OPTIONS,
        'statuses': STATUS_OPTIONS,
        'users': [{'id': u.id, 'name': f'{u.first_name or ""} {u.last_name or ""}'.strip() or u.username} for u in users]
    })

@bug_statistics_bp.route('/kpi-metrics', methods=['GET'])
@jwt_required()
def get_kpi_metrics():
    """获取KPI指标数据 - 支持多维度筛选"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    project_ids = request.args.get('project_ids', '')
    bug_types = request.args.get('bug_types', '')
    severities = request.args.get('severities', '')
    statuses = request.args.get('statuses', '')
    priorities = request.args.get('priorities', '')
    assigned_to = request.args.get('assigned_to', '')
    reported_by = request.args.get('reported_by', '')
    
    if current_user.role == 'admin':
        accessible_project_ids = [p.id for p in Project.query.all()]
    else:
        accessible_project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
    
    if not accessible_project_ids:
        return jsonify({'error': '没有可访问的项目'}), 403
    
    project_id_list = [int(p) for p in project_ids.split(',') if p.isdigit()] if project_ids else accessible_project_ids
    project_id_list = [p for p in project_id_list if p in accessible_project_ids]
    
    if not project_id_list:
        project_id_list = accessible_project_ids
    
    query = Bug.query.filter(Bug.project_id.in_(project_id_list))
    
    if start_date:
        query = query.filter(Bug.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Bug.created_at <= datetime.fromisoformat(end_date))
    if bug_types:
        type_list = bug_types.split(',')
        query = query.filter(Bug.bug_type.in_(type_list))
    if severities:
        severity_list = severities.split(',')
        query = query.filter(Bug.severity.in_(severity_list))
    if statuses:
        status_list = statuses.split(',')
        query = query.filter(Bug.status.in_(status_list))
    if priorities:
        priority_list = priorities.split(',')
        query = query.filter(Bug.priority.in_(priority_list))
    if assigned_to:
        assignee_list = [int(a) for a in assigned_to.split(',') if a.isdigit()]
        query = query.filter(Bug.assigned_to.in_(assignee_list))
    if reported_by:
        reporter_list = [int(r) for r in reported_by.split(',') if r.isdigit()]
        query = query.filter(Bug.reported_by.in_(reporter_list))
    
    all_bugs = query.all()
    total_bugs = len(all_bugs)
    
    resolved_statuses = [BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value]
    resolved_bugs = sum(1 for bug in all_bugs if bug.status in resolved_statuses)
    unresolved_bugs = total_bugs - resolved_bugs
    
    resolution_rate = round((resolved_bugs / total_bugs * 100) if total_bugs > 0 else 0, 1)
    
    avg_fix_time = 0
    closed_bugs_for_time = [bug for bug in all_bugs if bug.status == BugStatus.CLOSED.value and bug.resolved_at and bug.created_at]
    
    if closed_bugs_for_time:
        total_time = 0
        count = 0
        for bug in closed_bugs_for_time:
            if bug.resolved_at and bug.created_at:
                days = (bug.resolved_at - bug.created_at).days
                total_time += days
                count += 1
        avg_fix_time = round(total_time / count, 1) if count > 0 else 0
    
    period_start = start_date if start_date else (datetime.utcnow() - timedelta(days=30)).isoformat()
    prev_query = Bug.query.filter(
        Bug.project_id.in_(project_id_list),
        Bug.created_at < datetime.fromisoformat(period_start)
    )
    
    prev_total = prev_query.count()
    current_total = total_bugs
    
    total_change = 0
    if prev_total > 0:
        total_change = round(((current_total - prev_total) / prev_total) * 100, 1)
    
    new_in_period = query.filter(
        Bug.created_at >= datetime.fromisoformat(period_start)
    ).count() if start_date else all_bugs
    
    return jsonify({
        'total_bugs': total_bugs,
        'new_bugs': new_in_period,
        'resolved_bugs': resolved_bugs,
        'unresolved_bugs': unresolved_bugs,
        'resolution_rate': resolution_rate,
        'avg_fix_time': avg_fix_time,
        'total_change': total_change,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'project_ids': project_id_list,
            'bug_types': bug_types.split(',') if bug_types else [],
            'severities': severities.split(',') if severities else [],
            'statuses': statuses.split(',') if statuses else [],
            'priorities': priorities.split(',') if priorities else [],
            'assigned_to': assigned_to.split(',') if assigned_to else [],
            'reported_by': reported_by.split(',') if reported_by else []
        }
    })

@bug_statistics_bp.route('/trend-analysis', methods=['GET'])
@jwt_required()
def get_trend_analysis():
    """获取Bug趋势分析 - 支持多维度筛选"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    project_ids = request.args.get('project_ids', '')
    time_granularity = request.args.get('granularity', 'day')
    bug_types = request.args.get('bug_types', '')
    severities = request.args.get('severities', '')
    statuses = request.args.get('statuses', '')
    priorities = request.args.get('priorities', '')
    
    if current_user.role == 'admin':
        accessible_project_ids = [p.id for p in Project.query.all()]
    else:
        accessible_project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
    
    if not accessible_project_ids:
        return jsonify({'error': '没有可访问的项目'}), 403
    
    project_id_list = [int(p) for p in project_ids.split(',') if p.isdigit()] if project_ids else accessible_project_ids
    project_id_list = [p for p in project_id_list if p in accessible_project_ids]
    
    if not project_id_list:
        project_id_list = accessible_project_ids
    
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.utcnow().strftime('%Y-%m-%d')
    
    query = Bug.query.filter(
        Bug.project_id.in_(project_id_list),
        Bug.created_at >= datetime.fromisoformat(start_date),
        Bug.created_at <= datetime.fromisoformat(end_date + ' 23:59:59')
    )
    
    if bug_types:
        type_list = bug_types.split(',')
        query = query.filter(Bug.bug_type.in_(type_list))
    if severities:
        severity_list = severities.split(',')
        query = query.filter(Bug.severity.in_(severity_list))
    if statuses:
        status_list = statuses.split(',')
        query = query.filter(Bug.status.in_(status_list))
    if priorities:
        priority_list = priorities.split(',')
        query = query.filter(Bug.priority.in_(priority_list))
    
    all_bugs = query.all()
    
    if time_granularity == 'day':
        date_format = '%Y-%m-%d'
    elif time_granularity == 'week':
        date_format = '%Y-W%W'
    elif time_granularity == 'month':
        date_format = '%Y-%m'
    else:
        date_format = '%Y-%m-%d'
    
    new_bugs_by_date = defaultdict(int)
    resolved_bugs_by_date = defaultdict(int)
    cumulative_unresolved = defaultdict(int)
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    date_range = []
    current = start
    while current <= end:
        if time_granularity == 'week':
            date_key = current.strftime('%Y-W%W')
        elif time_granularity == 'month':
            date_key = current.strftime('%Y-%m')
        else:
            date_key = current.strftime('%Y-%m-%d')
        date_range.append(date_key)
        current += timedelta(days=1)
    
    for bug in all_bugs:
        if time_granularity == 'week':
            date_key = bug.created_at.strftime('%Y-W%W')
        elif time_granularity == 'month':
            date_key = bug.created_at.strftime('%Y-%m')
        else:
            date_key = bug.created_at.strftime('%Y-%m-%d')
        new_bugs_by_date[date_key] += 1
        
        if bug.resolved_at:
            if time_granularity == 'week':
                date_key = bug.resolved_at.strftime('%Y-W%W')
            elif time_granularity == 'month':
                date_key = bug.resolved_at.strftime('%Y-%m')
            else:
                date_key = bug.resolved_at.strftime('%Y-%m-%d')
            resolved_bugs_by_date[date_key] += 1
    
    trend_data = []
    running_unresolved = 0
    
    for date_key in date_range:
        new_count = new_bugs_by_date.get(date_key, 0)
        resolved_count = resolved_bugs_by_date.get(date_key, 0)
        running_unresolved += new_count - resolved_count
        
        trend_data.append({
            'date': date_key,
            'new_bugs': new_count,
            'resolved_bugs': resolved_count,
            'cumulative_unresolved': running_unresolved
        })
    
    return jsonify({
        'trend_data': trend_data,
        'granularity': time_granularity,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'project_ids': project_id_list
        }
    })

@bug_statistics_bp.route('/distribution-analysis', methods=['GET'])
@jwt_required()
def get_distribution_analysis():
    """获取Bug分布分析 - 支持多维度筛选"""
    try:
        try:
            Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
        except Exception as e:
            current_app.logger.error(f"获取模型失败: {str(e)}")
            return jsonify({'error': f'获取模型失败: {str(e)}'}), 500

        try:
            current_user_id = get_jwt_identity()
            current_user = User.query.get(int(current_user_id))
        except Exception as e:
            current_app.logger.error(f"获取用户失败: {str(e)}")
            return jsonify({'error': f'获取用户失败: {str(e)}'}), 500

        dimension = request.args.get('dimension', 'project')
        project_ids = request.args.get('project_ids', '')
        bug_types = request.args.get('bug_types', '')
        severities_filter = request.args.get('severities', '')
        statuses = request.args.get('statuses', '')
        priorities = request.args.get('priorities', '')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if current_user.role == 'admin':
            accessible_project_ids = [p.id for p in Project.query.all()]
        else:
            accessible_project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]

        if not accessible_project_ids:
            return jsonify({'error': '没有可访问的项目'}), 403

        project_id_list = [int(p) for p in project_ids.split(',') if p.isdigit()] if project_ids else accessible_project_ids
        project_id_list = [p for p in project_id_list if p in accessible_project_ids]

        if not project_id_list:
            project_id_list = accessible_project_ids

        query = Bug.query.filter(Bug.project_id.in_(project_id_list))

        if start_date:
            query = query.filter(Bug.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Bug.created_at <= datetime.fromisoformat(end_date + ' 23:59:59'))
        if bug_types:
            type_list = bug_types.split(',')
            query = query.filter(Bug.bug_type.in_(type_list))
        if severities_filter:
            severity_list = severities_filter.split(',')
            query = query.filter(Bug.severity.in_(severity_list))
        if statuses:
            status_list = statuses.split(',')
            query = query.filter(Bug.status.in_(status_list))
        if priorities:
            priority_list = priorities.split(',')
            query = query.filter(Bug.priority.in_(priority_list))

        all_bugs = query.all()

        if dimension == 'project':
            distribution = defaultdict(lambda: {'total': 0, 'new': 0, 'resolved': 0, 'closed': 0})
            for bug in all_bugs:
                proj = Project.query.get(bug.project_id)
                proj_name = proj.name if proj else '未知'
                distribution[proj_name]['total'] += 1
                if bug.status == BugStatus.NEW.value:
                    distribution[proj_name]['new'] += 1
                elif bug.status in [BugStatus.RESOLVED.value, BugStatus.VERIFIED.value]:
                    distribution[proj_name]['resolved'] += 1
                elif bug.status == BugStatus.CLOSED.value:
                    distribution[proj_name]['closed'] += 1

        elif dimension == 'severity':
            distribution = defaultdict(lambda: {'total': 0, 'new': 0, 'resolved': 0, 'closed': 0})
            for bug in all_bugs:
                severity = bug.severity.value if bug.severity else '未知'
                distribution[severity]['total'] += 1
                if bug.status == BugStatus.NEW.value:
                    distribution[severity]['new'] += 1
                elif bug.status in [BugStatus.RESOLVED.value, BugStatus.VERIFIED.value]:
                    distribution[severity]['resolved'] += 1
                elif bug.status == BugStatus.CLOSED.value:
                    distribution[severity]['closed'] += 1

        elif dimension == 'status':
            distribution = defaultdict(int)
            for bug in all_bugs:
                status = bug.status if bug.status else '未知'
                distribution[status] += 1

        elif dimension == 'priority':
            distribution = defaultdict(lambda: {'total': 0, 'new': 0, 'resolved': 0, 'closed': 0})
            for bug in all_bugs:
                priority = bug.priority.value if bug.priority else '未知'
                distribution[priority]['total'] += 1
                if bug.status == BugStatus.NEW.value:
                    distribution[priority]['new'] += 1
                elif bug.status in [BugStatus.RESOLVED.value, BugStatus.VERIFIED.value]:
                    distribution[priority]['resolved'] += 1
                elif bug.status == BugStatus.CLOSED.value:
                    distribution[priority]['closed'] += 1

        elif dimension == 'type':
            distribution = defaultdict(lambda: {'total': 0, 'new': 0, 'resolved': 0, 'closed': 0})
            for bug in all_bugs:
                bug_type = bug.bug_type or '未知'
                distribution[bug_type]['total'] += 1
                if bug.status == BugStatus.NEW.value:
                    distribution[bug_type]['new'] += 1
                elif bug.status in [BugStatus.RESOLVED.value, BugStatus.VERIFIED.value]:
                    distribution[bug_type]['resolved'] += 1
                elif bug.status == BugStatus.CLOSED.value:
                    distribution[bug_type]['closed'] += 1

        elif dimension == 'assignee':
            distribution = defaultdict(lambda: {'total': 0, 'new': 0, 'resolved': 0, 'closed': 0})
            for bug in all_bugs:
                if bug.assigned_to:
                    assignee = User.query.get(bug.assigned_to)
                    assignee_name = f'{assignee.first_name or ""} {assignee.last_name or ""}'.strip() or assignee.username if assignee else '未知'
                else:
                    assignee_name = '未分配'
                distribution[assignee_name]['total'] += 1
                if bug.status == BugStatus.NEW.value:
                    distribution[assignee_name]['new'] += 1
                elif bug.status in [BugStatus.RESOLVED.value, BugStatus.VERIFIED.value]:
                    distribution[assignee_name]['resolved'] += 1
                elif bug.status == BugStatus.CLOSED.value:
                    distribution[assignee_name]['closed'] += 1

        else:
            distribution = {}

        return jsonify({
            'dimension': dimension,
            'distribution': dict(distribution),
            'total_bugs': len(all_bugs),
            'filters': {
                'project_ids': project_id_list,
                'bug_types': bug_types.split(',') if bug_types else [],
                'severities': severities_filter.split(',') if severities_filter else [],
                'statuses': statuses.split(',') if statuses else [],
                'priorities': priorities.split(',') if priorities else [],
                'start_date': start_date,
                'end_date': end_date
            }
        })

    except Exception as e:
        import traceback
        current_app.logger.error(f"distribution-analysis 错误: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

@bug_statistics_bp.route('/type-distribution', methods=['GET'])
@jwt_required()
def get_type_distribution():
    """获取Bug类型占比分析"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    project_ids = request.args.get('project_ids', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if current_user.role == 'admin':
        accessible_project_ids = [p.id for p in Project.query.all()]
    else:
        accessible_project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
    
    project_id_list = [int(p) for p in project_ids.split(',') if p.isdigit()] if project_ids else accessible_project_ids
    project_id_list = [p for p in project_id_list if p in accessible_project_ids]
    
    if not project_id_list:
        project_id_list = accessible_project_ids
    
    query = Bug.query.filter(Bug.project_id.in_(project_id_list))
    
    if start_date:
        query = query.filter(Bug.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Bug.created_at <= datetime.fromisoformat(end_date + ' 23:59:59'))
    
    all_bugs = query.all()
    
    type_distribution = defaultdict(int)
    for bug in all_bugs:
        bug_type = bug.bug_type or '未知'
        type_distribution[bug_type] += 1
    
    total = len(all_bugs)
    result = []
    for bug_type, count in type_distribution.items():
        percentage = round((count / total * 100), 1) if total > 0 else 0
        result.append({
            'name': bug_type,
            'value': count,
            'percentage': percentage
        })
    
    result.sort(key=lambda x: x['value'], reverse=True)
    
    return jsonify({
        'type_distribution': result,
        'total': total
    })

@bug_statistics_bp.route('/person-workload', methods=['GET'])
@jwt_required()
def get_person_workload():
    """获取人员工作量分析"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    project_ids = request.args.get('project_ids', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if current_user.role == 'admin':
        accessible_project_ids = [p.id for p in Project.query.all()]
    else:
        accessible_project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
    
    project_id_list = [int(p) for p in project_ids.split(',') if p.isdigit()] if project_ids else accessible_project_ids
    project_id_list = [p for p in project_id_list if p in accessible_project_ids]
    
    if not project_id_list:
        project_id_list = accessible_project_ids
    
    query = Bug.query.filter(Bug.project_id.in_(project_id_list))
    
    if start_date:
        query = query.filter(Bug.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Bug.created_at <= datetime.fromisoformat(end_date + ' 23:59:59'))
    
    all_bugs = query.all()
    
    workload_data = defaultdict(lambda: {'assigned': 0, 'resolved': 0, 'closed': 0, 'in_progress': 0})
    
    for bug in all_bugs:
        if bug.assigned_to:
            assignee = User.query.get(bug.assigned_to)
            assignee_name = f'{assignee.first_name or ""} {assignee.last_name or ""}'.strip() or assignee.username if assignee else '未知'
        else:
            assignee_name = '未分配'
        
        workload_data[assignee_name]['assigned'] += 1
        
        if bug.status in [BugStatus.RESOLVED.value, BugStatus.VERIFIED.value]:
            workload_data[assignee_name]['resolved'] += 1
        elif bug.status == BugStatus.CLOSED.value:
            workload_data[assignee_name]['closed'] += 1
        elif bug.status == 'in_progress':
            workload_data[assignee_name]['in_progress'] += 1
    
    result = []
    for name, stats in workload_data.items():
        result.append({
            'name': name,
            'assigned': stats['assigned'],
            'resolved': stats['resolved'],
            'closed': stats['closed'],
            'in_progress': stats['in_progress'],
            'total_resolved': stats['resolved'] + stats['closed']
        })
    
    result.sort(key=lambda x: x['assigned'], reverse=True)
    
    return jsonify({
        'workload_data': result,
        'total_bugs': len(all_bugs)
    })

@bug_statistics_bp.route('/survival-duration', methods=['GET'])
@jwt_required()
def get_survival_duration():
    """获取Bug存活时长分布"""
    Task, Bug, Project, ProjectMember, User, BugStatus, TaskStatus, Severity = get_models()
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    project_ids = request.args.get('project_ids', '')
    
    if current_user.role == 'admin':
        accessible_project_ids = [p.id for p in Project.query.all()]
    else:
        accessible_project_ids = [m.project_id for m in ProjectMember.query.filter_by(user_id=current_user_id).all()]
    
    project_id_list = [int(p) for p in project_ids.split(',') if p.isdigit()] if project_ids else accessible_project_ids
    project_id_list = [p for p in project_id_list if p in accessible_project_ids]
    
    if not project_id_list:
        project_id_list = accessible_project_ids
    
    resolved_bugs = Bug.query.filter(
        Bug.project_id.in_(project_id_list),
        Bug.status.in_([BugStatus.RESOLVED.value, BugStatus.VERIFIED.value, BugStatus.CLOSED.value]),
        Bug.resolved_at.isnot(None),
        Bug.created_at.isnot(None)
    ).all()
    
    duration_distribution = {
        '24小时内': 0,
        '1-3天': 0,
        '3-7天': 0,
        '7-30天': 0,
        '30天以上': 0
    }
    
    for bug in resolved_bugs:
        if bug.resolved_at and bug.created_at:
            days = (bug.resolved_at - bug.created_at).days
            
            if days <= 1:
                duration_distribution['24小时内'] += 1
            elif days <= 3:
                duration_distribution['1-3天'] += 1
            elif days <= 7:
                duration_distribution['3-7天'] += 1
            elif days <= 30:
                duration_distribution['7-30天'] += 1
            else:
                duration_distribution['30天以上'] += 1
    
    result = [{'name': k, 'value': v} for k, v in duration_distribution.items()]
    
    return jsonify({
        'duration_distribution': result,
        'total_resolved': len(resolved_bugs)
    })