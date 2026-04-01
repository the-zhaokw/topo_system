"""
全文搜索模块
支持跨资源类型的统一搜索
"""
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_, func, text
from datetime import datetime

search_bp = Blueprint('search', __name__, url_prefix='/search')
search_api = Api(search_bp)

class GlobalSearchResource(Resource):
    """全局搜索 API"""
    
    method_decorators = {'get': [jwt_required()]}
    
    def get(self):
        """跨资源类型搜索"""
        from enhanced_app import db, Bug, Project, User, Task, Material, Contract
        
        # 查询参数
        keyword = request.args.get('q', '').strip()
        types = request.args.getlist('type')  # bug, project, user, task, material, contract
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if not keyword:
            return {'error': '搜索关键词不能为空'}, 400
        
        if not types:
            types = ['bug', 'project', 'user', 'task']
        
        results = []
        total = 0
        
        # 搜索 Bugs
        if 'bug' in types:
            bug_query = db.session.query(Bug).filter(
                or_(
                    Bug.title.ilike(f'%{keyword}%'),
                    Bug.description.ilike(f'%{keyword}%'),
                    Bug.status.ilike(f'%{keyword}%')
                )
            )
            bugs = bug_query.limit(10).all()
            for bug in bugs:
                results.append({
                    'type': 'bug',
                    'id': bug.id,
                    'title': bug.title,
                    'description': bug.description[:100] if bug.description else None,
                    'status': str(bug.status) if bug.status else None,
                    'priority': str(bug.priority) if bug.priority else None,
                    'severity': str(bug.severity) if bug.severity else None,
                    'url': f'/bugs/{bug.id}',
                    'created_at': bug.created_at.isoformat() if bug.created_at else None
                })
            total += bug_query.count()
        
        # 搜索 Projects
        if 'project' in types:
            project_query = db.session.query(Project).filter(
                or_(
                    Project.name.ilike(f'%{keyword}%'),
                    Project.code.ilike(f'%{keyword}%'),
                    Project.description.ilike(f'%{keyword}%')
                )
            )
            projects = project_query.limit(10).all()
            for project in projects:
                results.append({
                    'type': 'project',
                    'id': project.id,
                    'title': project.name,
                    'code': project.code,
                    'description': project.description[:100] if project.description else None,
                    'status': str(project.status) if project.status else None,
                    'url': f'/projects/{project.id}',
                    'created_at': project.created_at.isoformat() if project.created_at else None
                })
            total += project_query.count()
        
        # 搜索 Users
        if 'user' in types:
            user_query = db.session.query(User).filter(
                or_(
                    User.username.ilike(f'%{keyword}%'),
                    User.email.ilike(f'%{keyword}%'),
                    User.first_name.ilike(f'%{keyword}%'),
                    User.last_name.ilike(f'%{keyword}%'),
                    User.department.ilike(f'%{keyword}%')
                )
            )
            users = user_query.limit(10).all()
            for user in users:
                results.append({
                    'type': 'user',
                    'id': user.id,
                    'title': user.username,
                    'name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
                    'email': user.email,
                    'department': user.department,
                    'role': user.role,
                    'url': f'/users/{user.id}',
                    'avatar': user.avatar
                })
            total += user_query.count()
        
        # 搜索 Tasks
        if 'task' in types:
            task_query = db.session.query(Task).filter(
                or_(
                    Task.title.ilike(f'%{keyword}%'),
                    Task.description.ilike(f'%{keyword}%')
                )
            )
            tasks = task_query.limit(10).all()
            for task in tasks:
                results.append({
                    'type': 'task',
                    'id': task.id,
                    'title': task.title,
                    'description': task.description[:100] if task.description else None,
                    'status': str(task.status) if task.status else None,
                    'priority': str(task.priority) if task.priority else None,
                    'url': f'/tasks/{task.id}',
                    'created_at': task.created_at.isoformat() if task.created_at else None
                })
            total += task_query.count()
        
        # 搜索 Materials
        if 'material' in types:
            try:
                material_query = db.session.query(Material).filter(
                    or_(
                        Material.name.ilike(f'%{keyword}%'),
                        Material.code.ilike(f'%{keyword}%'),
                        Material.specification.ilike(f'%{keyword}%')
                    )
                )
                materials = material_query.limit(10).all()
                for material in materials:
                    results.append({
                        'type': 'material',
                        'id': material.id,
                        'title': material.name,
                        'code': material.code,
                        'specification': material.specification,
                        'category': material.category,
                        'url': f'/materials/{material.id}',
                        'created_at': material.created_at.isoformat() if material.created_at else None
                    })
                total += material_query.count()
            except:
                pass  # Material 模型字段可能不同
        
        # 搜索 Contracts
        if 'contract' in types:
            try:
                contract_query = db.session.query(Contract).filter(
                    or_(
                        Contract.title.ilike(f'%{keyword}%'),
                        Contract.contract_no.ilike(f'%{keyword}%'),
                        Contract.party_a_name.ilike(f'%{keyword}%'),
                        Contract.party_b_name.ilike(f'%{keyword}%')
                    )
                )
                contracts = contract_query.limit(10).all()
                for contract in contracts:
                    results.append({
                        'type': 'contract',
                        'id': contract.id,
                        'title': contract.title,
                        'contract_no': contract.contract_no,
                        'status': str(contract.status) if contract.status else None,
                        'total_amount': contract.total_amount,
                        'url': f'/contracts/{contract.id}',
                        'created_at': contract.created_at.isoformat() if contract.created_at else None
                    })
                total += contract_query.count()
            except:
                pass
        
        # 按相关性排序（简单的：标题匹配优先）
        def sort_key(item):
            title = item.get('title', '') or ''
            if keyword.lower() in title.lower():
                return 0
            return 1
        
        results.sort(key=sort_key)
        
        # 分页
        start = (page - 1) * per_page
        end = start + per_page
        paginated_results = results[start:end]
        
        return {
            'keyword': keyword,
            'types': types,
            'results': paginated_results,
            'total': len(results),
            'page': page,
            'per_page': per_page,
            'pages': (len(results) + per_page - 1) // per_page
        }

class SearchSuggestionsResource(Resource):
    """搜索建议 API"""
    
    method_decorators = {'get': [jwt_required()]}
    
    def get(self):
        """根据输入提供搜索建议"""
        from enhanced_app import db, Bug, Project, User
        
        keyword = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not keyword or len(keyword) < 2:
            return {'suggestions': []}
        
        suggestions = []
        
        # Bug 标题建议
        bugs = db.session.query(Bug).filter(
            Bug.title.ilike(f'%{keyword}%')
        ).limit(limit).all()
        for bug in bugs:
            suggestions.append({
                'type': 'bug',
                'text': bug.title,
                'id': bug.id,
                'url': f'/bugs/{bug.id}'
            })
        
        # 项目名称建议
        projects = db.session.query(Project).filter(
            Project.name.ilike(f'%{keyword}%')
        ).limit(limit).all()
        for project in projects:
            suggestions.append({
                'type': 'project',
                'text': project.name,
                'id': project.id,
                'url': f'/projects/{project.id}'
            })
        
        # 用户名建议
        users = db.session.query(User).filter(
            or_(
                User.username.ilike(f'%{keyword}%'),
                User.first_name.ilike(f'%{keyword}%'),
                User.last_name.ilike(f'%{keyword}%')
            )
        ).limit(limit).all()
        for user in users:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
            suggestions.append({
                'type': 'user',
                'text': name,
                'id': user.id,
                'url': f'/users/{user.id}'
            })
        
        return {'suggestions': suggestions[:limit]}

class SearchHistoryResource(Resource):
    """搜索历史 API"""
    
    method_decorators = {'get': [jwt_required()], 'post': [jwt_required()]}
    
    def get(self):
        """获取当前用户的搜索历史"""
        # 实际项目中应该存储在数据库或 Redis
        # 这里返回空列表作为占位
        return {'history': []}
    
    def post(self):
        """保存搜索历史"""
        # 实际项目中应该存储在数据库或 Redis
        return {'message': '搜索历史已保存'}, 201

# 注册路由
search_api.add_resource(GlobalSearchResource, '/')
search_api.add_resource(SearchSuggestionsResource, '/suggestions')
search_api.add_resource(SearchHistoryResource, '/history')
