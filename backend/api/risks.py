from flask import Blueprint, request, jsonify
from datetime import datetime, date
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

def get_db():
    from enhanced_app import get_db_instance
    return get_db_instance()

def get_models():
    from enhanced_app import User, Project, ProjectMember, Risk, Bug
    return User, Project, ProjectMember, Risk, Bug

def get_require_permission():
    from enhanced_app import require_permission
    return require_permission

def get_create_audit_log():
    from enhanced_app import create_audit_log
    return create_audit_log

risks_bp = Blueprint('risks', __name__, url_prefix='/risks')

@risks_bp.route('/', methods=['GET'])
@jwt_required()
def get_risks():
    db = get_db()
    User, Project, ProjectMember, Risk, Bug = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    project_id = request.args.get('project_id', type=int)
    risk_type = request.args.get('risk_type')
    status = request.args.get('status')
    level = request.args.get('level')
    priority = request.args.get('priority')
    category = request.args.get('category')
    assigned_to = request.args.get('assigned_to', type=int)
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Risk.query

    if project_id:
        query = query.filter(Risk.project_id == project_id)

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
        # if risk.related_task:
        #     risk_dict['related_task_title'] = risk.related_task.title
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

@risks_bp.route('/<int:risk_id>', methods=['GET'])
@jwt_required()
def get_risk(risk_id):
    User, Project, ProjectMember, Risk, Bug = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    risk = Risk.query.get(risk_id)
    if not risk:
        return jsonify({'error': '风险/问题不存在'}), 404

    risk_dict = risk.to_dict()
    if risk.related_bug:
        risk_dict['related_bug_title'] = risk.related_bug.title
    # if risk.related_task:
    #     risk_dict['related_task_title'] = risk.related_task.title

    return jsonify({
        'success': True,
        'message': '获取风险详情成功',
        'data': {
            'risk': risk_dict
        }
    }), 200

@risks_bp.route('/', methods=['POST'])
@jwt_required()
def create_risk():
    db = get_db()
    User, Project, ProjectMember, Risk, Bug = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    if not data.get('title'):
        return jsonify({'error': '标题为必填项'}), 400

    if not data.get('project_id'):
        return jsonify({'error': '项目ID为必填项'}), 400

    project = Project.query.get(data['project_id'])
    if not project:
        return jsonify({'error': '项目不存在'}), 404

    try:
        identified_date = None
        if data.get('identified_date'):
            identified_date = datetime.strptime(data['identified_date'], '%Y-%m-%d').date()

        due_date = None
        if data.get('due_date'):
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()

        new_risk = Risk(
            project_id=data['project_id'],
            risk_type=data.get('risk_type', 'risk'),
            title=data['title'],
            description=data.get('description'),
            status=data.get('status', 'identified'),
            priority=data.get('priority', 'medium'),
            level=data.get('level', 'medium'),
            category=data.get('category'),
            identified_by=data.get('identified_by', current_user_id),
            assigned_to=data.get('assigned_to'),
            probability=data.get('probability', 0.0),
            impact=data.get('impact', 0.0),
            mitigation_strategy=data.get('mitigation_strategy'),
            contingency_plan=data.get('contingency_plan'),
            resolution=data.get('resolution'),
            identified_date=identified_date,
            due_date=due_date,
            trigger_condition=data.get('trigger_condition'),
            indicator=data.get('indicator'),
            related_risk_id=data.get('related_risk_id'),
            related_bug_id=data.get('related_bug_id'),
            related_task_id=data.get('related_task_id'),
            created_by=current_user_id
        )

        new_risk.exposure = new_risk.calculate_exposure()

        db.session.add(new_risk)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '创建风险/问题成功',
            'data': {
                'risk': new_risk.to_dict()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建风险/问题失败: {str(e)}")
        return jsonify({'error': f'创建风险/问题失败: {str(e)}'}), 500

@risks_bp.route('/<int:risk_id>', methods=['PUT'])
@jwt_required()
def update_risk(risk_id):
    db = get_db()
    User, Project, ProjectMember, Risk, Bug = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    risk = Risk.query.get(risk_id)
    if not risk:
        return jsonify({'error': '风险/问题不存在'}), 404

    data = request.get_json()

    try:
        if 'title' in data:
            risk.title = data['title']
        if 'description' in data:
            risk.description = data['description']
        if 'status' in data:
            risk.status = data['status']
            if data['status'] == 'resolved':
                risk.resolved_date = date.today()
            elif data['status'] == 'closed':
                risk.closed_date = date.today()
        if 'priority' in data:
            risk.priority = data['priority']
        if 'level' in data:
            risk.level = data['level']
        if 'category' in data:
            risk.category = data['category']
        if 'assigned_to' in data:
            risk.assigned_to = data['assigned_to']
        if 'probability' in data:
            risk.probability = data['probability']
        if 'impact' in data:
            risk.impact = data['impact']
        if 'mitigation_strategy' in data:
            risk.mitigation_strategy = data['mitigation_strategy']
        if 'contingency_plan' in data:
            risk.contingency_plan = data['contingency_plan']
        if 'resolution' in data:
            risk.resolution = data['resolution']
        if 'identified_date' in data:
            if data['identified_date']:
                risk.identified_date = datetime.strptime(data['identified_date'], '%Y-%m-%d').date()
            else:
                risk.identified_date = None
        if 'due_date' in data:
            if data['due_date']:
                risk.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            else:
                risk.due_date = None
        if 'trigger_condition' in data:
            risk.trigger_condition = data['trigger_condition']
        if 'indicator' in data:
            risk.indicator = data['indicator']
        if 'related_risk_id' in data:
            risk.related_risk_id = data['related_risk_id']
        if 'related_bug_id' in data:
            risk.related_bug_id = data['related_bug_id']
        if 'related_task_id' in data:
            risk.related_task_id = data['related_task_id']

        risk.exposure = risk.calculate_exposure()
        risk.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '更新风险/问题成功',
            'data': {
                'risk': risk.to_dict()
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新风险/问题失败: {str(e)}")
        return jsonify({'error': f'更新风险/问题失败: {str(e)}'}), 500

@risks_bp.route('/<int:risk_id>', methods=['DELETE'])
@jwt_required()
def delete_risk(risk_id):
    db = get_db()
    User, Project, ProjectMember, Risk, Bug = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    risk = Risk.query.get(risk_id)
    if not risk:
        return jsonify({'error': '风险/问题不存在'}), 404

    try:
        db.session.delete(risk)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '删除风险/问题成功'
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除风险/问题失败: {str(e)}")
        return jsonify({'error': f'删除风险/问题失败: {str(e)}'}), 500

@risks_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_risk_statistics():
    db = get_db()
    User, Project, ProjectMember, Risk, Bug = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    project_id = request.args.get('project_id', type=int)

    query = Risk.query
    if project_id:
        query = query.filter(Risk.project_id == project_id)

    risks = query.all()

    total = len(risks)
    by_status = {}
    by_level = {}
    by_category = {}
    by_type = {'risk': 0, 'issue': 0}
    open_count = 0
    resolved_count = 0
    high_risk_count = 0

    for risk in risks:
        by_status[risk.status] = by_status.get(risk.status, 0) + 1
        by_level[risk.level] = by_level.get(risk.level, 0) + 1
        by_category[risk.category] = by_category.get(risk.category, 0) + 1
        by_type[risk.risk_type] = by_type.get(risk.risk_type, 0) + 1

        if risk.status not in ['resolved', 'closed', 'accepted']:
            open_count += 1
        if risk.status in ['resolved', 'closed']:
            resolved_count += 1
        if risk.level in ['high', 'critical']:
            high_risk_count += 1

    return jsonify({
        'success': True,
        'message': '获取风险统计成功',
        'data': {
            'total': total,
            'open': open_count,
            'resolved': resolved_count,
            'high_risk': high_risk_count,
            'by_status': by_status,
            'by_level': by_level,
            'by_category': by_category,
            'by_type': by_type
        }
    }), 200

@risks_bp.route('/matrix', methods=['GET'])
@jwt_required()
def get_risk_matrix():
    User, Project, ProjectMember, Risk, Bug = get_models()

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    project_id = request.args.get('project_id', type=int)

    query = Risk.query.filter(Risk.risk_type == 'risk')
    if project_id:
        query = query.filter(Risk.project_id == project_id)

    risks = query.filter(Risk.status.notin_(['resolved', 'closed'])).all()

    matrix = {
        'critical_high': [],
        'critical_medium': [],
        'critical_low': [],
        'high_high': [],
        'high_medium': [],
        'high_low': [],
        'medium_high': [],
        'medium_medium': [],
        'medium_low': [],
        'low_high': [],
        'low_medium': [],
        'low_low': []
    }

    for risk in risks:
        key = f"{risk.level}_{risk.priority}"
        if key in matrix:
            matrix[key].append({
                'id': risk.id,
                'title': risk.title,
                'status': risk.status,
                'exposure': risk.exposure
            })

    return jsonify({
        'success': True,
        'message': '获取风险矩阵成功',
        'data': matrix
    }), 200