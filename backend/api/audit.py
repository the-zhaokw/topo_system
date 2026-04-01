"""
操作日志审计模块
记录所有用户操作，支持查询和导出
"""
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import json

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')
audit_api = Api(audit_bp)

# 操作类型定义
ACTION_TYPES = {
    'CREATE': '创建',
    'UPDATE': '更新',
    'DELETE': '删除',
    'VIEW': '查看',
    'EXPORT': '导出',
    'IMPORT': '导入',
    'LOGIN': '登录',
    'LOGOUT': '登出',
    'APPROVE': '审批通过',
    'REJECT': '审批拒绝',
    'ASSIGN': '分配',
    'STATUS_CHANGE': '状态变更'
}

# 资源类型定义
RESOURCE_TYPES = {
    'USER': '用户',
    'PROJECT': '项目',
    'BUG': '缺陷',
    'TASK': '任务',
    'MATERIAL': '物料',
    'CONTRACT': '合同',
    'ATTENDANCE': '考勤',
    'NOTIFICATION': '通知',
    'SYSTEM': '系统',
    'REQUIREMENT': '需求',
    'TEST_CASE': '测试用例'
}

def get_audit_models():
    """延迟获取模型，避免循环导入"""
    from enhanced_app import AuditLog, User, db
    return db, AuditLog, User

def log_action(action, resource_type, resource_id=None, details=None, user_id=None):
    """
    记录操作日志
    在请求上下文中调用，自动获取当前用户
    """
    try:
        from enhanced_app import db, AuditLog
        from flask_jwt_extended import get_jwt_identity
        
        if user_id is None:
            try:
                user_id = get_jwt_identity()
            except:
                user_id = None
        
        # 获取请求信息
        from flask import request
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent') if request else None
        
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details, ensure_ascii=False) if details else None,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        
        db.session.add(log)
        db.session.commit()
        
    except Exception as e:
        # 日志记录失败不应影响主流程
        print(f"审计日志记录失败: {e}")

class AuditLogListResource(Resource):
    """审计日志列表 API"""
    
    method_decorators = {'get': [jwt_required()]}
    
    def get(self):
        db, AuditLog, User = get_audit_models()
        
        # 权限检查 - 只有管理员可以查看所有日志
        current_user_id = get_jwt_identity()
        from enhanced_app import User as UserModel
        user = db.session.get(UserModel, current_user_id)
        is_admin = user and user.role == 'admin'
        
        # 查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id = request.args.get('user_id', type=int)
        action = request.args.get('action')
        resource_type = request.args.get('resource_type')
        resource_id = request.args.get('resource_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        keyword = request.args.get('keyword')
        
        query = db.session.query(AuditLog)
        
        # 非管理员只能查看自己的日志
        if not is_admin:
            query = query.filter(AuditLog.user_id == current_user_id)
        elif user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        # 筛选条件
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        if keyword:
            query = query.filter(
                or_(
                    AuditLog.details.ilike(f'%{keyword}%'),
                    AuditLog.action.ilike(f'%{keyword}%'),
                    AuditLog.resource_type.ilike(f'%{keyword}%')
                )
            )
        
        # 排序
        query = query.order_by(AuditLog.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        logs = pagination.items
        
        # 获取用户信息
        user_ids = [log.user_id for log in logs if log.user_id]
        users = {u.id: u for u in db.session.query(UserModel).filter(UserModel.id.in_(user_ids)).all()} if user_ids else {}
        
        result = []
        for log in logs:
            user = users.get(log.user_id)
            result.append({
                'id': log.id,
                'user_id': log.user_id,
                'username': user.username if user else '系统',
                'user_real_name': f"{user.first_name or ''} {user.last_name or ''}".strip() if user else None,
                'action': log.action,
                'action_name': ACTION_TYPES.get(log.action, log.action),
                'resource_type': log.resource_type,
                'resource_type_name': RESOURCE_TYPES.get(log.resource_type, log.resource_type),
                'resource_id': log.resource_id,
                'details': json.loads(log.details) if log.details else None,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat() if log.created_at else None
            })
        
        return {
            'logs': result,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'action_types': ACTION_TYPES,
            'resource_types': RESOURCE_TYPES
        }

class AuditLogStatisticsResource(Resource):
    """审计日志统计 API"""
    
    method_decorators = {'get': [jwt_required()]}
    
    def get(self):
        db, AuditLog, User = get_audit_models()
        
        # 权限检查
        current_user_id = get_jwt_identity()
        from enhanced_app import User as UserModel
        user = db.session.get(UserModel, current_user_id)
        if not user or user.role != 'admin':
            return {'error': '权限不足'}, 403
        
        # 时间范围
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 操作类型分布
        action_stats = db.session.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= start_date
        ).group_by(AuditLog.action).all()
        
        # 资源类型分布
        resource_stats = db.session.query(
            AuditLog.resource_type,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= start_date
        ).group_by(AuditLog.resource_type).all()
        
        # 活跃用户统计
        user_stats = db.session.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= start_date
        ).group_by(AuditLog.user_id).order_by(func.count(AuditLog.id).desc()).limit(10).all()
        
        # 每日操作趋势
        daily_stats = db.session.query(
            func.date(AuditLog.created_at).label('date'),
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= start_date
        ).group_by(func.date(AuditLog.created_at)).all()
        
        return {
            'action_distribution': [{'action': a, 'name': ACTION_TYPES.get(a, a), 'count': c} for a, c in action_stats],
            'resource_distribution': [{'type': t, 'name': RESOURCE_TYPES.get(t, t), 'count': c} for t, c in resource_stats],
            'top_users': [{'user_id': u, 'count': c} for u, c in user_stats],
            'daily_trend': [{'date': str(d), 'count': c} for d, c in daily_stats]
        }

class AuditLogExportResource(Resource):
    """审计日志导出 API"""
    
    method_decorators = {'post': [jwt_required()]}
    
    def post(self):
        db, AuditLog, User = get_audit_models()
        
        # 权限检查
        current_user_id = get_jwt_identity()
        from enhanced_app import User as UserModel
        user = db.session.get(UserModel, current_user_id)
        if not user or user.role != 'admin':
            return {'error': '权限不足'}, 403
        
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        format_type = data.get('format', 'excel')  # excel, csv, json
        
        query = db.session.query(AuditLog)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        query = query.order_by(AuditLog.created_at.desc())
        logs = query.all()
        
        # 准备导出数据
        export_data = []
        for log in logs:
            user = db.session.get(UserModel, log.user_id) if log.user_id else None
            export_data.append({
                '时间': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
                '用户': user.username if user else '系统',
                '操作': ACTION_TYPES.get(log.action, log.action),
                '资源类型': RESOURCE_TYPES.get(log.resource_type, log.resource_type),
                '资源ID': log.resource_id,
                '详情': log.details,
                'IP地址': log.ip_address
            })
        
        if format_type == 'json':
            return {'data': export_data}
        
        # Excel/CSV 导出
        try:
            import pandas as pd
            from io import BytesIO
            
            df = pd.DataFrame(export_data)
            
            if format_type == 'csv':
                output = BytesIO()
                df.to_csv(output, index=False, encoding='utf-8-sig')
                output.seek(0)
                from flask import send_file
                return send_file(
                    output,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f'audit_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                )
            else:  # excel
                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                from flask import send_file
                return send_file(
                    output,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=f'audit_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
                )
        except ImportError:
            return {'error': '导出功能需要 pandas 和 openpyxl，请安装: pip install pandas openpyxl'}, 500

# 注册路由
audit_api.add_resource(AuditLogListResource, '/logs')
audit_api.add_resource(AuditLogStatisticsResource, '/statistics')
audit_api.add_resource(AuditLogExportResource, '/export')
