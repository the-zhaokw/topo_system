"""
API 文档自动生成模块
基于 Flask-RESTful 自动生成 OpenAPI/Swagger 文档
"""
from flask import Blueprint, jsonify, render_template_string
from flask_restful import Api, Resource

api_docs_bp = Blueprint('api_docs', __name__, url_prefix='/docs')
api_docs_api = Api(api_docs_bp)

# API 文档数据
API_ENDPOINTS = {
    'auth': {
        'name': '认证管理',
        'endpoints': [
            {'path': '/auth/login', 'method': 'POST', 'desc': '用户登录', 'auth': False},
            {'path': '/auth/logout', 'method': 'POST', 'desc': '用户登出', 'auth': True},
            {'path': '/auth/me', 'method': 'GET', 'desc': '获取当前用户信息', 'auth': True},
            {'path': '/auth/register', 'method': 'POST', 'desc': '用户注册', 'auth': False},
            {'path': '/auth/change-password', 'method': 'PUT', 'desc': '修改密码', 'auth': True},
        ]
    },
    'users': {
        'name': '用户管理',
        'endpoints': [
            {'path': '/users/', 'method': 'GET', 'desc': '用户列表', 'auth': True},
            {'path': '/users/{id}/', 'method': 'GET', 'desc': '用户详情', 'auth': True},
            {'path': '/users/', 'method': 'POST', 'desc': '创建用户', 'auth': True},
            {'path': '/users/{id}/', 'method': 'PUT', 'desc': '更新用户', 'auth': True},
            {'path': '/users/{id}/', 'method': 'DELETE', 'desc': '删除用户', 'auth': True},
        ]
    },
    'projects': {
        'name': '项目管理',
        'endpoints': [
            {'path': '/projects/', 'method': 'GET', 'desc': '项目列表', 'auth': True},
            {'path': '/projects/{id}/', 'method': 'GET', 'desc': '项目详情', 'auth': True},
            {'path': '/projects/', 'method': 'POST', 'desc': '创建项目', 'auth': True},
            {'path': '/projects/{id}/', 'method': 'PUT', 'desc': '更新项目', 'auth': True},
            {'path': '/projects/{id}/', 'method': 'DELETE', 'desc': '删除项目', 'auth': True},
        ]
    },
    'bugs': {
        'name': '缺陷管理',
        'endpoints': [
            {'path': '/bugs', 'method': 'GET', 'desc': 'Bug列表', 'auth': True},
            {'path': '/bugs/{id}', 'method': 'GET', 'desc': 'Bug详情', 'auth': True},
            {'path': '/bugs', 'method': 'POST', 'desc': '创建Bug', 'auth': True},
            {'path': '/bugs/{id}', 'method': 'PUT', 'desc': '更新Bug', 'auth': True},
            {'path': '/bugs/{id}/status', 'method': 'PUT', 'desc': '更新Bug状态', 'auth': True},
            {'path': '/bugs/{id}/assign', 'method': 'PUT', 'desc': '分配Bug', 'auth': True},
        ]
    },
    'tasks': {
        'name': '任务管理',
        'endpoints': [
            {'path': '/tasks', 'method': 'GET', 'desc': '任务列表', 'auth': True},
            {'path': '/tasks/{id}', 'method': 'GET', 'desc': '任务详情', 'auth': True},
            {'path': '/tasks', 'method': 'POST', 'desc': '创建任务', 'auth': True},
            {'path': '/tasks/{id}', 'method': 'PUT', 'desc': '更新任务', 'auth': True},
        ]
    },
    'materials': {
        'name': '物料管理',
        'endpoints': [
            {'path': '/materials/', 'method': 'GET', 'desc': '物料列表', 'auth': True},
            {'path': '/materials/categories', 'method': 'GET', 'desc': '物料分类', 'auth': True},
        ]
    },
    'contracts': {
        'name': '合同管理',
        'endpoints': [
            {'path': '/contracts', 'method': 'GET', 'desc': '合同列表', 'auth': True},
            {'path': '/contracts/{id}', 'method': 'GET', 'desc': '合同详情', 'auth': True},
            {'path': '/contracts', 'method': 'POST', 'desc': '创建合同', 'auth': True},
        ]
    },
    'attendance': {
        'name': '考勤管理',
        'endpoints': [
            {'path': '/attendance/records', 'method': 'GET', 'desc': '考勤记录', 'auth': True},
            {'path': '/attendance/clock-in', 'method': 'POST', 'desc': '上班打卡', 'auth': True},
            {'path': '/attendance/clock-out', 'method': 'POST', 'desc': '下班打卡', 'auth': True},
        ]
    },
    'notifications': {
        'name': '通知系统',
        'endpoints': [
            {'path': '/notifications', 'method': 'GET', 'desc': '通知列表', 'auth': True},
            {'path': '/notifications/unread-count', 'method': 'GET', 'desc': '未读数量', 'auth': True},
            {'path': '/notifications/read-all', 'method': 'PUT', 'desc': '全部已读', 'auth': True},
        ]
    },
    'statistics': {
        'name': '统计报表',
        'endpoints': [
            {'path': '/statistics/dashboard', 'method': 'GET', 'desc': '仪表板', 'auth': True},
            {'path': '/statistics/bugs', 'method': 'GET', 'desc': 'Bug统计', 'auth': True},
            {'path': '/statistics/projects', 'method': 'GET', 'desc': '项目统计', 'auth': True},
        ]
    },
    'search': {
        'name': '搜索',
        'endpoints': [
            {'path': '/search', 'method': 'GET', 'desc': '全局搜索', 'auth': True},
            {'path': '/search/suggestions', 'method': 'GET', 'desc': '搜索建议', 'auth': True},
        ]
    },
    'audit': {
        'name': '审计日志',
        'endpoints': [
            {'path': '/audit/logs', 'method': 'GET', 'desc': '审计日志', 'auth': True},
            {'path': '/audit/statistics', 'method': 'GET', 'desc': '审计统计', 'auth': True},
        ]
    },
    'health': {
        'name': '健康检查',
        'endpoints': [
            {'path': '/health/', 'method': 'GET', 'desc': '健康检查', 'auth': False},
            {'path': '/health/info', 'method': 'GET', 'desc': '系统信息', 'auth': False},
            {'path': '/health/ready', 'method': 'GET', 'desc': '就绪检查', 'auth': False},
        ]
    },
}

class ApiDocsResource(Resource):
    """API 文档 HTML 页面"""
    
    def get(self):
        """返回 API 文档 HTML"""
        html = '''
<!DOCTYPE html>
<html>
<head>
    <title>TOPO System API 文档</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .module { background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .module h2 { color: #2196F3; margin-top: 0; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        .method { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
        .method-GET { background: #4CAF50; color: white; }
        .method-POST { background: #2196F3; color: white; }
        .method-PUT { background: #FF9800; color: white; }
        .method-DELETE { background: #f44336; color: white; }
        .auth { font-size: 12px; }
        .auth-required { color: #f44336; }
        .auth-optional { color: #4CAF50; }
        .base-url { background: #333; color: #4CAF50; padding: 10px; border-radius: 4px; font-family: monospace; }
    </style>
</head>
<body>
    <h1>🏢 TOPO System API 文档</h1>
    <div class="base-url">Base URL: /api</div>
    
    {% for module_id, module in modules.items() %}
    <div class="module">
        <h2>{{ module.name }}</h2>
        <table>
            <tr>
                <th>方法</th>
                <th>路径</th>
                <th>描述</th>
                <th>认证</th>
            </tr>
            {% for endpoint in module.endpoints %}
            <tr>
                <td><span class="method method-{{ endpoint.method }}">{{ endpoint.method }}</span></td>
                <td><code>{{ endpoint.path }}</code></td>
                <td>{{ endpoint.desc }}</td>
                <td class="auth {% if endpoint.auth %}auth-required{% else %}auth-optional{% endif %}">
                    {% if endpoint.auth %}需要认证{% else %}公开{% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endfor %}
    
    <div style="margin-top: 40px; padding: 20px; background: #333; color: white; border-radius: 8px;">
        <h3>📋 认证说明</h3>
        <p>需要认证的 API 请在请求头中添加：</p>
        <code>Authorization: Bearer {access_token}</code>
        <p style="margin-top: 10px;">Token 通过 <code>POST /api/auth/login</code> 获取</p>
    </div>
</body>
</html>
        '''
        from jinja2 import Template
        template = Template(html)
        return render_template_string(template.render(modules=API_ENDPOINTS))

class ApiJsonResource(Resource):
    """API JSON 文档"""
    
    def get(self):
        """返回 API 文档 JSON"""
        return {
            'name': 'TOPO System API',
            'version': '1.0.0',
            'base_url': '/api',
            'modules': API_ENDPOINTS
        }

class OpenApiSpecResource(Resource):
    """OpenAPI/Swagger 规范"""
    
    def get(self):
        """返回 OpenAPI 3.0 规范"""
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'TOPO System API',
                'version': '1.0.0',
                'description': 'TOPO 系统 RESTful API'
            },
            'servers': [
                {'url': '/api', 'description': 'API 服务器'}
            ],
            'paths': {}
        }
        
        # 生成 paths
        for module_id, module in API_ENDPOINTS.items():
            for endpoint in module['endpoints']:
                path = endpoint['path']
                if path not in spec['paths']:
                    spec['paths'][path] = {}
                
                method = endpoint['method'].lower()
                spec['paths'][path][method] = {
                    'summary': endpoint['desc'],
                    'security': [{'bearerAuth': []}] if endpoint['auth'] else [],
                    'responses': {
                        '200': {'description': '成功'},
                        '401': {'description': '未认证'},
                        '403': {'description': '无权限'}
                    }
                }
        
        # 添加安全定义
        spec['components'] = {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT'
                }
            }
        }
        
        return spec

# 注册路由
api_docs_api.add_resource(ApiDocsResource, '/')
api_docs_api.add_resource(ApiJsonResource, '/json')
api_docs_api.add_resource(OpenApiSpecResource, '/openapi.json')
