#!/usr/bin/env python3
"""
数据导入导出增强API
提供Excel/CSV批量导入导出、数据模板、导入验证功能
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd
import io
import csv
import json
import logging

logger = logging.getLogger(__name__)
data_bp = Blueprint('data', __name__, url_prefix='/data')

# 允许的导入文件类型
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

# 导入任务存储（实际应使用数据库）
import_tasks = {}
export_tasks = {}

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== 导入模板 ====================
@data_bp.route('/import/templates', methods=['GET'])
@jwt_required()
def get_import_templates():
    """获取导入模板列表"""
    templates = [
        {
            'id': 'projects',
            'name': '项目导入模板',
            'description': '导入项目基本信息',
            'fields': [
                {'name': 'code', 'label': '项目编号', 'required': True, 'type': 'string'},
                {'name': 'name', 'label': '项目名称', 'required': True, 'type': 'string'},
                {'name': 'description', 'label': '项目描述', 'required': False, 'type': 'text'},
                {'name': 'status', 'label': '状态', 'required': True, 'type': 'enum', 'options': ['active', 'completed', 'cancelled']},
                {'name': 'priority', 'label': '优先级', 'required': False, 'type': 'enum', 'options': ['high', 'medium', 'low']},
                {'name': 'start_date', 'label': '开始日期', 'required': False, 'type': 'date'},
                {'name': 'end_date', 'label': '结束日期', 'required': False, 'type': 'date'}
            ]
        },
        {
            'id': 'bugs',
            'name': 'Bug导入模板',
            'description': '导入Bug数据',
            'fields': [
                {'name': 'title', 'label': '标题', 'required': True, 'type': 'string'},
                {'name': 'description', 'label': '描述', 'required': False, 'type': 'text'},
                {'name': 'project_id', 'label': '项目ID', 'required': True, 'type': 'number'},
                {'name': 'priority', 'label': '优先级', 'required': True, 'type': 'enum', 'options': ['critical', 'high', 'medium', 'low']},
                {'name': 'severity', 'label': '严重程度', 'required': True, 'type': 'enum', 'options': ['critical', 'major', 'minor', 'trivial']},
                {'name': 'module', 'label': '模块', 'required': False, 'type': 'string'},
                {'name': 'reporter', 'label': '报告人', 'required': False, 'type': 'string'}
            ]
        },
        {
            'id': 'tasks',
            'name': '任务导入模板',
            'description': '导入任务数据',
            'fields': [
                {'name': 'title', 'label': '标题', 'required': True, 'type': 'string'},
                {'name': 'description', 'label': '描述', 'required': False, 'type': 'text'},
                {'name': 'project_id', 'label': '项目ID', 'required': True, 'type': 'number'},
                {'name': 'status', 'label': '状态', 'required': True, 'type': 'enum', 'options': ['todo', 'in_progress', 'review', 'done']},
                {'name': 'priority', 'label': '优先级', 'required': False, 'type': 'enum', 'options': ['high', 'medium', 'low']},
                {'name': 'assignee', 'label': '指派人', 'required': False, 'type': 'string'},
                {'name': 'due_date', 'label': '截止日期', 'required': False, 'type': 'date'}
            ]
        },
        {
            'id': 'users',
            'name': '用户导入模板',
            'description': '导入用户数据',
            'fields': [
                {'name': 'username', 'label': '用户名', 'required': True, 'type': 'string'},
                {'name': 'email', 'label': '邮箱', 'required': True, 'type': 'email'},
                {'name': 'first_name', 'label': '姓', 'required': False, 'type': 'string'},
                {'name': 'last_name', 'label': '名', 'required': False, 'type': 'string'},
                {'name': 'role', 'label': '角色', 'required': True, 'type': 'enum', 'options': ['admin', 'manager', 'developer', 'tester', 'user']},
                {'name': 'department', 'label': '部门', 'required': False, 'type': 'string'},
                {'name': 'phone', 'label': '电话', 'required': False, 'type': 'string'}
            ]
        },
        {
            'id': 'materials',
            'name': '物料导入模板',
            'description': '导入物料数据',
            'fields': [
                {'name': 'code', 'label': '物料编码', 'required': True, 'type': 'string'},
                {'name': 'name', 'label': '物料名称', 'required': True, 'type': 'string'},
                {'name': 'category', 'label': '分类', 'required': True, 'type': 'string'},
                {'name': 'description', 'label': '描述', 'required': False, 'type': 'text'},
                {'name': 'unit', 'label': '单位', 'required': True, 'type': 'string'},
                {'name': 'purchase_price', 'label': '采购价', 'required': False, 'type': 'number'},
                {'name': 'sale_price', 'label': '销售价', 'required': False, 'type': 'number'},
                {'name': 'current_stock', 'label': '当前库存', 'required': False, 'type': 'number'}
            ]
        }
    ]
    
    return jsonify({
        'success': True,
        'data': templates
    })

@data_bp.route('/import/templates/<template_id>/download', methods=['GET'])
@jwt_required()
def download_template(template_id):
    """下载导入模板"""
    try:
        # 获取模板信息
        templates = get_import_templates().get_json()['data']
        template = next((t for t in templates if t['id'] == template_id), None)
        
        if not template:
            return jsonify({'success': False, 'error': '模板不存在'}), 404
        
        # 生成Excel模板
        df = pd.DataFrame(columns=[f['name'] for f in template['fields']])
        
        # 添加示例数据
        example_data = {}
        for field in template['fields']:
            if field['type'] == 'enum':
                example_data[field['name']] = field['options'][0] if field['options'] else ''
            elif field['type'] == 'number':
                example_data[field['name']] = 0
            elif field['type'] == 'date':
                example_data[field['name']] = '2026-01-01'
            else:
                example_data[field['name']] = f'示例{field["label"]}'
        
        df = pd.concat([df, pd.DataFrame([example_data])], ignore_index=True)
        
        # 添加说明sheet
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='数据', index=False)
            
            # 字段说明
            info_df = pd.DataFrame([
                {
                    '字段名': f['name'],
                    '显示名': f['label'],
                    '必填': '是' if f['required'] else '否',
                    '类型': f['type'],
                    '说明': f'可选值: {", ".join(f["options"])}' if f.get('options') else ''
                }
                for f in template['fields']
            ])
            info_df.to_excel(writer, sheet_name='字段说明', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{template_id}_template.xlsx'
        )
    except Exception as e:
        logger.error(f"下载模板错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 数据导入 ====================
@data_bp.route('/import', methods=['POST'])
@jwt_required()
def import_data():
    """导入数据"""
    try:
        current_user_id = get_jwt_identity()
        
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '请选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '请选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件类型'}), 400
        
        template_id = request.form.get('template_id')
        if not template_id:
            return jsonify({'success': False, 'error': '请选择导入模板'}), 400
        
        # 创建导入任务
        task_id = f"import_{len(import_tasks) + 1}"
        import_tasks[task_id] = {
            'id': task_id,
            'status': 'processing',
            'template_id': template_id,
            'filename': secure_filename(file.filename),
            'created_by': current_user_id,
            'created_at': datetime.now().isoformat(),
            'result': None
        }
        
        # 读取文件
        filename = file.filename.lower()
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # 验证数据
        validation_result = validate_import_data(template_id, df)
        
        if not validation_result['valid']:
            import_tasks[task_id]['status'] = 'failed'
            import_tasks[task_id]['result'] = {
                'errors': validation_result['errors']
            }
            return jsonify({
                'success': False,
                'error': '数据验证失败',
                'data': {
                    'task_id': task_id,
                    'errors': validation_result['errors']
                }
            }), 400
        
        # 执行导入
        import_result = execute_import(template_id, df, current_user_id)
        
        import_tasks[task_id]['status'] = 'completed'
        import_tasks[task_id]['result'] = import_result
        
        return jsonify({
            'success': True,
            'message': '导入完成',
            'data': {
                'task_id': task_id,
                'result': import_result
            }
        })
    except Exception as e:
        logger.error(f"导入数据错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def validate_import_data(template_id, df):
    """验证导入数据"""
    errors = []
    
    # 获取模板字段
    templates = get_import_templates().get_json()['data']
    template = next((t for t in templates if t['id'] == template_id), None)
    
    if not template:
        return {'valid': False, 'errors': ['模板不存在']}
    
    required_fields = [f['name'] for f in template['fields'] if f['required']]
    
    # 检查必填字段
    for field in required_fields:
        if field not in df.columns:
            errors.append(f'缺少必填字段: {field}')
        else:
            # 检查空值
            empty_count = df[field].isna().sum()
            if empty_count > 0:
                errors.append(f'字段 {field} 有 {empty_count} 行空值')
    
    # 检查数据类型
    for field in template['fields']:
        if field['name'] in df.columns:
            if field['type'] == 'email':
                # 验证邮箱格式
                invalid_emails = df[~df[field['name']].str.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)]
                if len(invalid_emails) > 0:
                    errors.append(f'字段 {field["name"]} 有 {len(invalid_emails)} 行邮箱格式不正确')
            
            elif field['type'] == 'enum':
                # 验证枚举值
                valid_values = set(field['options'])
                invalid_values = df[~df[field['name']].isin(valid_values)]
                if len(invalid_values) > 0:
                    errors.append(f'字段 {field["name"]} 有 {len(invalid_values)} 行值不在允许范围内')
            
            elif field['type'] == 'number':
                # 验证数字
                non_numeric = pd.to_numeric(df[field['name']], errors='coerce').isna()
                if non_numeric.sum() > 0:
                    errors.append(f'字段 {field["name"]} 有 {non_numeric.sum()} 行不是有效数字')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def execute_import(template_id, df, user_id):
    """执行数据导入"""
    result = {
        'total': len(df),
        'success': 0,
        'failed': 0,
        'details': []
    }
    
    # 根据模板类型执行导入
    if template_id == 'projects':
        result = import_projects(df, user_id)
    elif template_id == 'bugs':
        result = import_bugs(df, user_id)
    elif template_id == 'tasks':
        result = import_tasks_data(df, user_id)
    elif template_id == 'users':
        result = import_users(df, user_id)
    elif template_id == 'materials':
        result = import_materials(df, user_id)
    
    return result

def import_projects(df, user_id):
    """导入项目"""
    from enhanced_app import db, Project
    
    result = {'total': len(df), 'success': 0, 'failed': 0, 'errors': []}
    
    for index, row in df.iterrows():
        try:
            # 检查项目编号是否已存在
            existing = Project.query.filter_by(code=row['code']).first()
            if existing:
                result['failed'] += 1
                result['errors'].append(f'第{index+2}行: 项目编号 {row["code"]} 已存在')
                continue
            
            project = Project(
                code=row['code'],
                name=row['name'],
                description=row.get('description', ''),
                status=row.get('status', 'active'),
                priority=row.get('priority', 'medium'),
                created_by=user_id
            )
            
            if 'start_date' in row and pd.notna(row['start_date']):
                project.start_date = row['start_date']
            if 'end_date' in row and pd.notna(row['end_date']):
                project.end_date = row['end_date']
            
            db.session.add(project)
            result['success'] += 1
        except Exception as e:
            result['failed'] += 1
            result['errors'].append(f'第{index+2}行: {str(e)}')
    
    db.session.commit()
    return result

def import_bugs(df, user_id):
    """导入Bug"""
    from enhanced_app import db, Bug, BugStatus, Priority, Severity
    
    result = {'total': len(df), 'success': 0, 'failed': 0, 'errors': []}
    
    for index, row in df.iterrows():
        try:
            bug = Bug(
                title=row['title'],
                description=row.get('description', ''),
                project_id=int(row['project_id']),
                status=BugStatus.NEW,
                priority=Priority[row.get('priority', 'medium').upper()],
                severity=Severity[row.get('severity', 'major').upper()],
                module=row.get('module', ''),
                reported_by=user_id
            )
            
            db.session.add(bug)
            result['success'] += 1
        except Exception as e:
            result['failed'] += 1
            result['errors'].append(f'第{index+2}行: {str(e)}')
    
    db.session.commit()
    return result

def import_tasks_data(df, user_id):
    """导入任务"""
    from enhanced_app import db, Task
    
    result = {'total': len(df), 'success': 0, 'failed': 0, 'errors': []}
    
    for index, row in df.iterrows():
        try:
            task = Task(
                title=row['title'],
                description=row.get('description', ''),
                project_id=int(row['project_id']),
                status=row.get('status', 'todo'),
                priority=row.get('priority', 'medium'),
                created_by=user_id
            )
            
            if 'due_date' in row and pd.notna(row['due_date']):
                task.due_date = row['due_date']
            
            db.session.add(task)
            result['success'] += 1
        except Exception as e:
            result['failed'] += 1
            result['errors'].append(f'第{index+2}行: {str(e)}')
    
    db.session.commit()
    return result

def import_users(df, user_id):
    """导入用户"""
    from enhanced_app import db, User, UserRole
    
    result = {'total': len(df), 'success': 0, 'failed': 0, 'errors': []}
    
    for index, row in df.iterrows():
        try:
            # 检查用户名是否已存在
            existing = User.query.filter_by(username=row['username']).first()
            if existing:
                result['failed'] += 1
                result['errors'].append(f'第{index+2}行: 用户名 {row["username"]} 已存在')
                continue
            
            user = User(
                username=row['username'],
                email=row['email'],
                first_name=row.get('first_name', ''),
                last_name=row.get('last_name', ''),
                role=UserRole[row.get('role', 'user').upper()],
                department=row.get('department', ''),
                phone=row.get('phone', ''),
                is_active=True
            )
            user.set_password('123456')  # 默认密码
            
            db.session.add(user)
            result['success'] += 1
        except Exception as e:
            result['failed'] += 1
            result['errors'].append(f'第{index+2}行: {str(e)}')
    
    db.session.commit()
    return result

def import_materials(df, user_id):
    """导入物料"""
    from enhanced_app import db, Material, MaterialCategory
    
    result = {'total': len(df), 'success': 0, 'failed': 0, 'errors': []}
    
    for index, row in df.iterrows():
        try:
            # 查找或创建分类
            category = MaterialCategory.query.filter_by(name=row['category']).first()
            if not category:
                category = MaterialCategory(name=row['category'])
                db.session.add(category)
                db.session.flush()
            
            # 检查物料编码是否已存在
            existing = Material.query.filter_by(code=row['code']).first()
            if existing:
                result['failed'] += 1
                result['errors'].append(f'第{index+2}行: 物料编码 {row["code"]} 已存在')
                continue
            
            material = Material(
                code=row['code'],
                name=row['name'],
                category_id=category.id,
                description=row.get('description', ''),
                unit=row['unit'],
                purchase_price=row.get('purchase_price', 0),
                sale_price=row.get('sale_price', 0),
                current_stock=row.get('current_stock', 0)
            )
            
            db.session.add(material)
            result['success'] += 1
        except Exception as e:
            result['failed'] += 1
            result['errors'].append(f'第{index+2}行: {str(e)}')
    
    db.session.commit()
    return result

@data_bp.route('/import/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_import_task(task_id):
    """获取导入任务状态"""
    if task_id not in import_tasks:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    
    return jsonify({
        'success': True,
        'data': import_tasks[task_id]
    })

# ==================== 数据导出 ====================
@data_bp.route('/export', methods=['POST'])
@jwt_required()
def export_data():
    """导出数据"""
    try:
        data = request.get_json()
        export_type = data.get('type')  # projects, bugs, tasks, users, materials
        format_type = data.get('format', 'excel')  # excel, csv, json
        filters = data.get('filters', {})
        
        # 创建导出任务
        task_id = f"export_{len(export_tasks) + 1}"
        export_tasks[task_id] = {
            'id': task_id,
            'status': 'processing',
            'type': export_type,
            'format': format_type,
            'created_at': datetime.now().isoformat()
        }
        
        # 执行导出
        if export_type == 'projects':
            result = export_projects(filters, format_type)
        elif export_type == 'bugs':
            result = export_bugs(filters, format_type)
        elif export_type == 'tasks':
            result = export_tasks_data(filters, format_type)
        elif export_type == 'users':
            result = export_users(filters, format_type)
        elif export_type == 'materials':
            result = export_materials(filters, format_type)
        else:
            return jsonify({'success': False, 'error': '未知的导出类型'}), 400
        
        export_tasks[task_id]['status'] = 'completed'
        export_tasks[task_id]['result'] = result
        
        return jsonify({
            'success': True,
            'message': '导出完成',
            'data': {
                'task_id': task_id,
                'download_url': result.get('download_url')
            }
        })
    except Exception as e:
        logger.error(f"导出数据错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def export_projects(filters, format_type):
    """导出项目"""
    from enhanced_app import Project
    
    query = Project.query
    
    if filters.get('status'):
        query = query.filter_by(status=filters['status'])
    if filters.get('priority'):
        query = query.filter_by(priority=filters['priority'])
    
    projects = query.all()
    
    data = []
    for p in projects:
        data.append({
            '项目编号': p.code,
            '项目名称': p.name,
            '描述': p.description,
            '状态': p.status,
            '优先级': p.priority,
            '进度': f"{p.progress or 0}%",
            '开始日期': p.start_date,
            '结束日期': p.end_date,
            '创建时间': p.created_at
        })
    
    df = pd.DataFrame(data)
    
    return generate_export_file(df, format_type, 'projects')

def export_bugs(filters, format_type):
    """导出Bug"""
    from enhanced_app import Bug, Project
    
    query = Bug.query
    
    if filters.get('project_id'):
        query = query.filter_by(project_id=filters['project_id'])
    if filters.get('status'):
        query = query.filter_by(status=filters['status'])
    if filters.get('priority'):
        query = query.filter_by(priority=filters['priority'])
    
    bugs = query.all()
    
    data = []
    for b in bugs:
        project = Project.query.get(b.project_id)
        data.append({
            'ID': b.id,
            '标题': b.title,
            '项目': project.name if project else '未知',
            '状态': b.status.value if hasattr(b.status, 'value') else str(b.status),
            '优先级': b.priority.value if hasattr(b.priority, 'value') else str(b.priority),
            '严重程度': b.severity.value if hasattr(b.severity, 'value') else str(b.severity),
            '模块': b.module,
            '创建时间': b.created_at,
            '解决时间': b.resolved_at
        })
    
    df = pd.DataFrame(data)
    
    return generate_export_file(df, format_type, 'bugs')

def export_tasks_data(filters, format_type):
    """导出任务"""
    from enhanced_app import Task, Project
    
    query = Task.query
    
    if filters.get('project_id'):
        query = query.filter_by(project_id=filters['project_id'])
    if filters.get('status'):
        query = query.filter_by(status=filters['status'])
    
    tasks = query.all()
    
    data = []
    for t in tasks:
        project = Project.query.get(t.project_id)
        data.append({
            'ID': t.id,
            '标题': t.title,
            '项目': project.name if project else '未知',
            '状态': t.status,
            '优先级': t.priority,
            '进度': f"{t.progress or 0}%",
            '截止日期': t.due_date,
            '创建时间': t.created_at
        })
    
    df = pd.DataFrame(data)
    
    return generate_export_file(df, format_type, 'tasks')

def export_users(filters, format_type):
    """导出用户"""
    from enhanced_app import User
    
    query = User.query
    
    if filters.get('role'):
        query = query.filter_by(role=filters['role'])
    if filters.get('department'):
        query = query.filter_by(department=filters['department'])
    
    users = query.all()
    
    data = []
    for u in users:
        data.append({
            '用户名': u.username,
            '邮箱': u.email,
            '姓名': f"{u.first_name or ''} {u.last_name or ''}".strip(),
            '角色': u.role.value if hasattr(u.role, 'value') else str(u.role),
            '部门': u.department,
            '电话': u.phone,
            '状态': '启用' if u.is_active else '禁用',
            '创建时间': u.created_at
        })
    
    df = pd.DataFrame(data)
    
    return generate_export_file(df, format_type, 'users')

def export_materials(filters, format_type):
    """导出物料"""
    from enhanced_app import Material, MaterialCategory
    
    query = Material.query
    
    if filters.get('category_id'):
        query = query.filter_by(category_id=filters['category_id'])
    
    materials = query.all()
    
    data = []
    for m in materials:
        category = MaterialCategory.query.get(m.category_id)
        data.append({
            '物料编码': m.code,
            '物料名称': m.name,
            '分类': category.name if category else '未知',
            '描述': m.description,
            '单位': m.unit,
            '采购价': m.purchase_price,
            '销售价': m.sale_price,
            '当前库存': m.current_stock,
            '最小库存': m.min_stock,
            '最大库存': m.max_stock
        })
    
    df = pd.DataFrame(data)
    
    return generate_export_file(df, format_type, 'materials')

def generate_export_file(df, format_type, filename_prefix):
    """生成导出文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{filename_prefix}_{timestamp}'
    
    if format_type == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='数据', index=False)
        output.seek(0)
        
        return {
            'filename': f'{filename}.xlsx',
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'data': output.getvalue()
        }
    
    elif format_type == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        
        return {
            'filename': f'{filename}.csv',
            'content_type': 'text/csv',
            'data': output.getvalue().encode('utf-8-sig')
        }
    
    elif format_type == 'json':
        return {
            'filename': f'{filename}.json',
            'content_type': 'application/json',
            'data': json.dumps(df.to_dict('records'), ensure_ascii=False, indent=2).encode('utf-8')
        }

@data_bp.route('/export/download/<task_id>', methods=['GET'])
@jwt_required()
def download_export(task_id):
    """下载导出文件"""
    if task_id not in export_tasks:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    
    task = export_tasks[task_id]
    
    if task['status'] != 'completed':
        return jsonify({'success': False, 'error': '导出未完成'}), 400
    
    result = task['result']
    
    return send_file(
        io.BytesIO(result['data']),
        mimetype=result['content_type'],
        as_attachment=True,
        download_name=result['filename']
    )

# ==================== 统计 ====================
@data_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_data_statistics():
    """获取数据统计"""
    try:
        from enhanced_app import Project, Bug, Task, User, Material
        
        stats = {
            'projects': Project.query.count(),
            'bugs': Bug.query.count(),
            'tasks': Task.query.count(),
            'users': User.query.count(),
            'materials': Material.query.count(),
            'import_tasks': len(import_tasks),
            'export_tasks': len(export_tasks)
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"获取统计错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
