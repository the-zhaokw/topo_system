"""
待办事项聚合API
整合系统中所有待办事项，包括审批、Bug、任务、评审等
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json
import logging

todos_bp = Blueprint('todos', __name__, url_prefix='/todos')
logger = logging.getLogger(__name__)

def get_models():
    """延迟获取模型，避免循环导入"""
    from enhanced_app import (
        db, User, Bug, BugStatus, Project,
        LeaveApplication, OvertimeApplication, AttendanceException,
        Contract, ContractApproval, ContractDelivery, ContractRisk, ContractPayment,
        ContractReview, ContractReviewStep,
        RequirementDocument, RequirementItem, RequirementReview, RequirementReviewStep,
        TestCase, TestSuite, Notification
    )
    from api.rd_kanban import _get_models as _init_rd_models
    _init_rd_models()
    from api.rd_kanban import RDKanbanItem
    return {
        'db': db,
        'User': User,
        'Bug': Bug,
        'BugStatus': BugStatus,
        'Project': Project,
        'LeaveApplication': LeaveApplication,
        'OvertimeApplication': OvertimeApplication,
        'AttendanceException': AttendanceException,
        'Contract': Contract,
        'ContractApproval': ContractApproval,
        'ContractDelivery': ContractDelivery,
        'ContractRisk': ContractRisk,
        'ContractPayment': ContractPayment,
        'ContractReview': ContractReview,
        'ContractReviewStep': ContractReviewStep,
        'RequirementDocument': RequirementDocument,
        'RequirementItem': RequirementItem,
        'RequirementReview': RequirementReview,
        'RequirementReviewStep': RequirementReviewStep,
        'TestCase': TestCase,
        'TestSuite': TestSuite,
        'Notification': Notification,
        'RDKanbanItem': RDKanbanItem
    }


def _get_requirement_review_todos(models, current_user_id, db_session):
    """基于 RequirementReviewStep 直接查当前用户需要审批的需求条目评审

    这才是待办的真相来源：review.status=pending 且 step.status=pending 且 reviewer_id=当前用户
    Notification 表只作为补充和已读标记，不作为唯一数据源。
    """
    RequirementReview = models['RequirementReview']
    RequirementReviewStep = models['RequirementReviewStep']
    RequirementItem = models['RequirementItem']
    RequirementDocument = models['RequirementDocument']
    User = models['User']

    result = []
    seen_keys = set()

    # 主数据源：查当前用户是 pending 审批节点的 reviewer
    pending_steps = db_session.query(RequirementReviewStep).join(
        RequirementReview, RequirementReviewStep.review_id == RequirementReview.id
    ).filter(
        RequirementReviewStep.reviewer_id == current_user_id,
        RequirementReviewStep.status == 'pending',
        RequirementReview.status == 'pending',
        RequirementReviewStep.step_order == RequirementReview.current_step
    ).all()

    for step in pending_steps:
        review = step.review
        item = db_session.get(RequirementItem, review.item_id)
        if not item:
            continue
        doc = db_session.get(RequirementDocument, review.doc_id)
        creator = db_session.get(User, doc.created_by) if doc else None
        key = f"review_step_{step.id}"
        if key in seen_keys:
            continue
        seen_keys.add(key)

        link = f'/projects/{review.project_id}/requirements/{review.doc_id}?itemId={item.id}'
        result.append({
            'id': f'requirement_review_{step.id}',
            'step_id': step.id,
            'review_id': review.id,
            'item_id': item.id,
            'doc_id': review.doc_id,
            'project_id': review.project_id,
            'category': 'review',
            'type': 'requirement',
            'type_name': '需求评审',
            'title': item.title,
            'creator_name': creator.username if creator else '未知',
            'status': 'pending_review',
            'priority': 'medium',
            'created_at': step.created_at.isoformat() if step.created_at else None,
            'link': link
        })

    return result



def _parse_requirement_review_link(link):
    """从评审通知的 link 中解析 project_id, doc_id, item_id

    link 示例: /projects/1/requirements/3?itemId=5
    返回: (project_id, doc_id, item_id)
    """
    if not link:
        return None, None, None
    import re
    project_id, doc_id, item_id = None, None, None
    # 匹配 /projects/<pid>/requirements/<did>?itemId=<iid>
    m = re.search(r'/projects/(\d+)/requirements/(\d+)', link)
    if m:
        project_id = int(m.group(1))
        doc_id = int(m.group(2))
    else:
        m = re.search(r'/requirements/(\d+)', link)
        if m:
            doc_id = int(m.group(1))
    # 匹配 ?itemId=<iid>
    m = re.search(r'[?&]itemId=(\d+)', link)
    if m:
        item_id = int(m.group(1))
    return project_id, doc_id, item_id


def _get_test_case_review_todos(models, current_user_id, db_session):
    """基于 TestCaseReviewStep 直接查当前用户需要审批的测试用例评审

    review.status=pending 且 step.status=pending 且 reviewer_id=当前用户
    """
    from enhanced_app import TestCaseReview, TestCaseReviewStep
    User = models['User']

    result = []
    seen_keys = set()

    pending_steps = db_session.query(TestCaseReviewStep).join(
        TestCaseReview, TestCaseReviewStep.review_id == TestCaseReview.id
    ).filter(
        TestCaseReviewStep.reviewer_id == current_user_id,
        TestCaseReviewStep.status == 'pending',
        TestCaseReview.status == 'pending',
        TestCaseReviewStep.step_order == TestCaseReview.current_step
    ).all()

    for step in pending_steps:
        review = step.review
        case = review.case
        if not case:
            continue
        creator = db_session.get(User, review.initiator_id)
        key = f"test_case_review_step_{step.id}"
        if key in seen_keys:
            continue
        seen_keys.add(key)

        link = f'/projects/{review.project_id}/tests/suites/{review.suite_id}/cases/{case.id}'
        result.append({
            'id': f'test_case_review_{step.id}',
            'step_id': step.id,
            'review_id': review.id,
            'case_id': case.id,
            'suite_id': review.suite_id,
            'project_id': review.project_id,
            'category': 'review',
            'type': 'test_case',
            'type_name': '测试用例评审',
            'title': case.title,
            'creator_name': creator.username if creator else '未知',
            'status': 'pending_review',
            'priority': 'medium',
            'created_at': step.created_at.isoformat() if step.created_at else None,
            'link': link
        })

    return result


def _get_contract_review_todos(models, current_user_id, db_session):
    """基于 ContractReviewStep 直接查当前用户需要审批的合同审批节点

    真相来源：ContractReview.status=pending 且 Step.status=pending 且
    step_order == review.current_step 且 reviewer_id=当前用户。
    """
    ContractReview = models['ContractReview']
    ContractReviewStep = models['ContractReviewStep']
    Contract = models['Contract']
    User = models['User']

    result = []
    seen_keys = set()

    pending_steps = db_session.query(ContractReviewStep).join(
        ContractReview, ContractReviewStep.review_id == ContractReview.id
    ).filter(
        ContractReviewStep.reviewer_id == current_user_id,
        ContractReviewStep.status == 'pending',
        ContractReview.status == 'pending',
        ContractReviewStep.step_order == ContractReview.current_step
    ).all()

    for step in pending_steps:
        review = step.review
        contract = db_session.get(Contract, review.contract_id) if review else None
        if not contract:
            continue
        initiator = db_session.get(User, review.initiator_id)
        key = f"contract_review_step_{step.id}"
        if key in seen_keys:
            continue
        seen_keys.add(key)

        initiator_name = '未知'
        if initiator:
            initiator_name = (
                f"{initiator.first_name or ''} {initiator.last_name or ''}".strip()
                or initiator.username or '未知'
            )

        result.append({
            'id': f'contract_review_{step.id}',
            'step_id': step.id,
            'review_id': review.id,
            'contract_id': contract.id,
            'contract_no': contract.contract_no,
            'category': 'approval',
            'type': 'contract_review',
            'type_name': '合同审批',
            'title': f"合同审批: {contract.title}",
            'applicant_name': initiator_name,
            'creator_name': initiator_name,
            'status': 'pending',
            'priority': 'high',
            'deadline': review.deadline.isoformat() if review.deadline else None,
            'created_at': review.created_at.isoformat() if review.created_at else None,
            'link': f'/contracts/{contract.id}'
        })

    return result


@todos_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_todo_summary():
    """获取待办事项统计摘要"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()
    
    try:
        summary = {
            'approvals': {
                'leave': 0,
                'overtime': 0,
                'attendance_exception': 0,
                'contract': 0,
                'total': 0
            },
            'bugs': {
                'to_resolve': 0,
                'to_verify': 0,
                'total': 0
            },
            'reviews': {
                'requirements': 0,
                'test_cases': 0,
                'total': 0
            },
            'contracts': {
                'delivery_pending': 0,
                'risk_pending': 0,
                'payment_pending': 0,
                'total': 0
            },
            'rd_kanban': {
                'in_progress': 0,
                'total': 0
            },
            'total': 0
        }
        
        current_user = db.session.get(models['User'], current_user_id)
        if not current_user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        user_role = current_user.role
        
        pending_statuses = ['pending']
        
        leave_count = models['LeaveApplication'].query.filter(
            models['LeaveApplication'].status == 'pending',
            models['LeaveApplication'].approver_id == current_user_id
        ).count()
        summary['approvals']['leave'] = leave_count
        
        overtime_count = models['OvertimeApplication'].query.filter(
            models['OvertimeApplication'].status == 'pending',
            models['OvertimeApplication'].approver_id == current_user_id
        ).count()
        summary['approvals']['overtime'] = overtime_count
        
        exception_count = models['AttendanceException'].query.filter(
            models['AttendanceException'].status == 'pending',
            models['AttendanceException'].approver_id == current_user_id
        ).count()
        summary['approvals']['attendance_exception'] = exception_count
        
        contract_count = models['ContractApproval'].query.filter(
            models['ContractApproval'].status == 'pending',
            models['ContractApproval'].approver_id == current_user_id
        ).count()
        # 新版多级合同审批（ContractReviewStep）待办
        contract_count += len(_get_contract_review_todos(models, current_user_id, db.session))
        summary['approvals']['contract'] = contract_count
        
        summary['approvals']['total'] = leave_count + overtime_count + exception_count + contract_count
        
        open_statuses = [
            models['BugStatus'].NEW.value,
            models['BugStatus'].ASSIGNED.value,
            models['BugStatus'].IN_PROGRESS.value,
            models['BugStatus'].REOPENED.value,
            models['BugStatus'].OPEN.value
        ]

        to_resolve_count = models['Bug'].query.filter(
            db.or_(
                models['Bug'].assigned_to == current_user_id,
                models['Bug'].resolved_by == current_user_id
            ),
            models['Bug'].status.in_(open_statuses)
        ).count()
        summary['bugs']['to_resolve'] = to_resolve_count

        to_verify_statuses = [models['BugStatus'].RESOLVED.value, models['BugStatus'].FIXED.value]
        to_verify_count = models['Bug'].query.filter(
            models['Bug'].verifier_id == current_user_id,
            models['Bug'].status.in_(to_verify_statuses)
        ).count()
        summary['bugs']['to_verify'] = to_verify_count
        
        summary['bugs']['total'] = to_resolve_count + to_verify_count
        
        # 需求评审待办：当前用户未读的 requirement_review 通知
        # （发起评审时仅给评审人发通知，未更新 RequirementItem 状态）
        requirement_count = models['Notification'].query.filter(
            models['Notification'].user_id == current_user_id,
            models['Notification'].type == 'requirement_review',
            models['Notification'].is_read == False
        ).count()
        summary['reviews']['requirements'] = requirement_count
        
        test_case_count = len(_get_test_case_review_todos(models, current_user_id, db.session))
        summary['reviews']['test_cases'] = test_case_count
        
        summary['reviews']['total'] = requirement_count + test_case_count
        
        delivery_pending = models['ContractDelivery'].query.filter(
            models['ContractDelivery'].status == 'pending'
        ).count()
        summary['contracts']['delivery_pending'] = delivery_pending
        
        risk_pending = models['ContractRisk'].query.filter(
            models['ContractRisk'].status.in_(['identified', 'mitigation_in_progress'])
        ).count()
        summary['contracts']['risk_pending'] = risk_pending
        
        payment_pending = models['ContractPayment'].query.filter(
            models['ContractPayment'].status == 'pending'
        ).count()
        summary['contracts']['payment_pending'] = payment_pending
        
        summary['contracts']['total'] = delivery_pending + risk_pending + payment_pending

        # 正在开发的看板卡片（指派给当前用户的）
        rd_kanban_count = models['RDKanbanItem'].query.filter(
            models['RDKanbanItem'].column == 'in_progress',
            models['RDKanbanItem'].assignee_id == current_user_id
        ).count()
        summary['rd_kanban']['in_progress'] = rd_kanban_count
        summary['rd_kanban']['total'] = rd_kanban_count

        summary['total'] = (
            summary['approvals']['total'] +
            summary['bugs']['total'] +
            summary['reviews']['total'] +
            summary['contracts']['total'] +
            summary['rd_kanban']['total']
        )
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"获取待办事项统计失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取待办事项统计失败: {str(e)}'}), 500

@todos_bp.route('/approvals', methods=['GET'])
@jwt_required()
def get_approval_todos():
    """获取审批类待办事项"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()
    
    try:
        current_user = db.session.get(models['User'], current_user_id)
        if not current_user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        approvals = []
        
        leave_apps = models['LeaveApplication'].query.filter(
            models['LeaveApplication'].status == 'pending',
            models['LeaveApplication'].approver_id == current_user_id
        ).all()
        
        for app in leave_apps:
            applicant = db.session.get(models['User'], app.user_id)
            approvals.append({
                'id': app.id,
                'type': 'leave',
                'type_name': '请假申请',
                'title': f"{applicant.username if applicant else '未知'}的请假申请",
                'applicant_id': app.user_id,
                'applicant_name': f"{applicant.first_name or ''} {applicant.last_name or ''}".strip() or applicant.username if applicant else '未知',
                'status': app.status,
                'created_at': app.created_at.isoformat() if app.created_at else None,
                'details': {
                    'leave_type': app.leave_type,
                    'start_date': app.start_date.isoformat() if app.start_date else None,
                    'end_date': app.end_date.isoformat() if app.end_date else None,
                    'reason': app.reason,
                    'emergency_flag': app.emergency_flag
                },
                'link': f'/attendance/leave-approval/{app.id}'
            })
        
        overtime_apps = models['OvertimeApplication'].query.filter(
            models['OvertimeApplication'].status == 'pending',
            models['OvertimeApplication'].approver_id == current_user_id
        ).all()
        
        for app in overtime_apps:
            applicant = db.session.get(models['User'], app.user_id)
            approvals.append({
                'id': app.id,
                'type': 'overtime',
                'type_name': '加班申请',
                'title': f"{applicant.username if applicant else '未知'}的加班申请",
                'applicant_id': app.user_id,
                'applicant_name': f"{applicant.first_name or ''} {applicant.last_name or ''}".strip() or applicant.username if applicant else '未知',
                'status': app.status,
                'created_at': app.created_at.isoformat() if app.created_at else None,
                'details': {
                    'date': app.date.isoformat() if app.date else None,
                    'start_time': app.start_time,
                    'end_time': app.end_time,
                    'reason': app.reason
                },
                'link': f'/attendance/overtime-approval/{app.id}'
            })
        
        exceptions = models['AttendanceException'].query.filter(
            models['AttendanceException'].status == 'pending',
            models['AttendanceException'].approver_id == current_user_id
        ).all()
        
        for exc in exceptions:
            applicant = db.session.get(models['User'], exc.user_id)
            approvals.append({
                'id': exc.id,
                'type': 'attendance_exception',
                'type_name': '考勤异常',
                'title': f"{applicant.username if applicant else '未知'}的考勤异常申请",
                'applicant_id': exc.user_id,
                'applicant_name': f"{applicant.first_name or ''} {applicant.last_name or ''}".strip() or applicant.username if applicant else '未知',
                'status': exc.status,
                'created_at': exc.created_at.isoformat() if exc.created_at else None,
                'details': {
                    'exception_type': exc.exception_type,
                    'record_date': exc.record_date.isoformat() if exc.record_date else None,
                    'reason': exc.reason
                },
                'link': f'/attendance/exception-approval/{exc.id}'
            })
        
        contract_approvals = models['ContractApproval'].query.filter(
            models['ContractApproval'].status == 'pending',
            models['ContractApproval'].approver_id == current_user_id
        ).all()
        
        for ca in contract_approvals:
            contract = db.session.get(models['Contract'], ca.contract_id)
            if contract:
                approvals.append({
                    'id': ca.id,
                    'type': 'contract',
                    'type_name': '合同审批',
                    'title': f"合同审批: {contract.title}",
                    'contract_id': contract.id,
                    'contract_no': contract.contract_no,
                    'status': ca.status,
                    'created_at': ca.created_at.isoformat() if ca.created_at else None,
                    'details': {
                        'contract_type': contract.contract_type,
                        'total_amount': contract.total_amount,
                        'party_a': contract.party_a_name,
                        'party_b': contract.party_b_name
                    },
                    'link': f'/contracts/{contract.id}'
                })

        # 新版多级合同审批：当前用户处于待审批节点
        approvals.extend(_get_contract_review_todos(models, current_user_id, db.session))

        approvals.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'approvals': approvals,
                'total': len(approvals)
            }
        })
        
    except Exception as e:
        logger.error(f"获取审批待办失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取审批待办失败: {str(e)}'}), 500

def _get_enum_value(enum_or_str, default=''):
    """Safely extract value from enum or return string as-is"""
    if hasattr(enum_or_str, 'value'):
        return enum_or_str.value
    return str(enum_or_str) if enum_or_str else default

def _get_user_name(user):
    """Safely get user display name"""
    if not user:
        return '未知'
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return name or user.username or '未知'

@todos_bp.route('/bugs', methods=['GET'])
@jwt_required()
def get_bug_todos():
    """获取Bug相关待办事项"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()
    
    try:
        current_user = db.session.get(models['User'], current_user_id)
        if not current_user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        bugs = []
        
        open_statuses = [
            models['BugStatus'].NEW.value,
            models['BugStatus'].ASSIGNED.value,
            models['BugStatus'].IN_PROGRESS.value,
            models['BugStatus'].REOPENED.value,
            models['BugStatus'].OPEN.value,
            models['BugStatus'].FIXED.value
        ]

        to_resolve = models['Bug'].query.filter(
            db.or_(
                models['Bug'].assigned_to == current_user_id,
                models['Bug'].resolved_by == current_user_id
            ),
            models['Bug'].status.in_(open_statuses)
        ).all()
        
        for bug in to_resolve:
            project = db.session.get(models['Project'], bug.project_id)
            bugs.append({
                'id': bug.id,
                'type': 'to_resolve',
                'type_name': '待解决',
                'title': bug.title,
                'status': _get_enum_value(bug.status),
                'severity': _get_enum_value(bug.severity),
                'priority': _get_enum_value(bug.priority),
                'project_id': bug.project_id,
                'project_name': project.name if project else '未知项目',
                'created_at': bug.created_at.isoformat() if bug.created_at else None,
                'deadline': bug.deadline.isoformat() if bug.deadline else None,
                'link': f'/bugs/{bug.id}'
            })
        
        to_verify_statuses = [models['BugStatus'].RESOLVED.value, models['BugStatus'].FIXED.value]
        to_verify = models['Bug'].query.filter(
            models['Bug'].verifier_id == current_user_id,
            models['Bug'].status.in_(to_verify_statuses)
        ).all()
        
        for bug in to_verify:
            project = db.session.get(models['Project'], bug.project_id)
            resolver = db.session.get(models['User'], bug.resolved_by) if bug.resolved_by else None
            bugs.append({
                'id': bug.id,
                'type': 'to_verify',
                'type_name': '待验证',
                'title': bug.title,
                'status': _get_enum_value(bug.status),
                'severity': _get_enum_value(bug.severity),
                'priority': _get_enum_value(bug.priority),
                'project_id': bug.project_id,
                'project_name': project.name if project else '未知项目',
                'resolved_by': bug.resolved_by,
                'resolver_name': _get_user_name(resolver),
                'resolved_at': bug.resolved_at.isoformat() if bug.resolved_at else None,
                'created_at': bug.created_at.isoformat() if bug.created_at else None,
                'link': f'/bugs/{bug.id}'
            })
        
        bugs.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'bugs': bugs,
                'total': len(bugs)
            }
        })
        
    except Exception as e:
        logger.error(f"获取Bug待办失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取Bug待办失败: {str(e)}'}), 500

@todos_bp.route('/reviews', methods=['GET'])
@jwt_required()
def get_review_todos():
    """获取评审类待办事项"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()
    
    try:
        current_user = db.session.get(models['User'], current_user_id)
        if not current_user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        reviews = []

        # 需求评审：以 RequirementReviewStep 为真相源（当前用户是 pending 审批节点的 reviewer）
        reviews.extend(_get_requirement_review_todos(models, current_user_id, db.session))

        # 测试用例评审：以 TestCaseReviewStep 为真相源
        reviews.extend(_get_test_case_review_todos(models, current_user_id, db.session))
        
        reviews.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'reviews': reviews,
                'total': len(reviews)
            }
        })
        
    except Exception as e:
        logger.error(f"获取评审待办失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取评审待办失败: {str(e)}'}), 500

@todos_bp.route('/contracts', methods=['GET'])
@jwt_required()
def get_contract_todos():
    """获取合同相关待办事项"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()
    
    try:
        current_user = db.session.get(models['User'], current_user_id)
        if not current_user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        contracts_todos = []
        
        pending_deliveries = models['ContractDelivery'].query.filter(
            models['ContractDelivery'].status == 'pending'
        ).all()
        
        for delivery in pending_deliveries:
            contract = db.session.get(models['Contract'], delivery.contract_id)
            contracts_todos.append({
                'id': delivery.id,
                'type': 'delivery',
                'type_name': '待交付',
                'title': f"交付待处理: {delivery.site_name or delivery.delivery_no}",
                'contract_id': delivery.contract_id,
                'contract_title': contract.title if contract else '未知合同',
                'equipment_type': delivery.equipment_type,
                'quantity': delivery.quantity,
                'planned_date': delivery.planned_date.isoformat() if delivery.planned_date else None,
                'status': delivery.status,
                'link': f'/contracts/{delivery.contract_id}'
            })
        
        pending_risks = models['ContractRisk'].query.filter(
            models['ContractRisk'].status.in_(['identified', 'mitigation_in_progress'])
        ).all()
        
        for risk in pending_risks:
            contract = db.session.get(models['Contract'], risk.contract_id)
            contracts_todos.append({
                'id': risk.id,
                'type': 'risk',
                'type_name': '待处理风险',
                'title': risk.risk_description[:100] if risk.risk_description else '未描述风险',
                'contract_id': risk.contract_id,
                'contract_title': contract.title if contract else '未知合同',
                'risk_level': risk.risk_level,
                'risk_type': risk.risk_type,
                'status': risk.status,
                'link': f'/contracts/{risk.contract_id}'
            })
        
        pending_payments = models['ContractPayment'].query.filter(
            models['ContractPayment'].status == 'pending'
        ).all()
        
        for payment in pending_payments:
            contract = db.session.get(models['Contract'], payment.contract_id)
            contracts_todos.append({
                'id': payment.id,
                'type': 'payment',
                'type_name': '待付款',
                'title': f"付款待处理: {payment.payment_stage}",
                'contract_id': payment.contract_id,
                'contract_title': contract.title if contract else '未知合同',
                'payment_stage': payment.payment_stage,
                'planned_amount': payment.planned_amount,
                'planned_date': payment.planned_date.isoformat() if payment.planned_date else None,
                'status': payment.status,
                'link': f'/contracts/{payment.contract_id}'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'contracts': contracts_todos,
                'total': len(contracts_todos)
            }
        })
        
    except Exception as e:
        logger.error(f"获取合同待办失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取合同待办失败: {str(e)}'}), 500

@todos_bp.route('/rd-kanban', methods=['GET'])
@jwt_required()
def get_rd_kanban_todos():
    """获取正在开发的看板卡片待办"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        current_user = db.session.get(models['User'], current_user_id)
        if not current_user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        rd_items = models['RDKanbanItem'].query.filter(
            models['RDKanbanItem'].column == 'in_progress',
            models['RDKanbanItem'].assignee_id == current_user_id
        ).order_by(models['RDKanbanItem'].sort_order.asc()).all()

        rd_todos = []
        for item in rd_items:
            project = db.session.get(models['Project'], item.project_id)
            assignee = db.session.get(models['User'], item.assignee_id) if item.assignee_id else None
            rd_todos.append({
                'id': item.id,
                'category': 'rd_kanban',
                'type': 'in_progress',
                'type_name': '正在开发',
                'title': item.title,
                'project_id': item.project_id,
                'project_name': project.name if project else '未知项目',
                'status': item.status or 'in_progress',
                'status_color': item.status_color,
                'comment_count': item.comment_count,
                'assignee_name': assignee.username if assignee else None,
                'assignee_avatar': assignee.avatar if assignee else None,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
                'due_at': item.due_at.isoformat() if item.due_at else None,
                'tags': json.loads(item.tags) if item.tags else [],
                'link': f'/projects/rd-management?project={item.project_id}'
            })

        return jsonify({
            'success': True,
            'data': {
                'rd_kanban': rd_todos,
                'total': len(rd_todos)
            }
        })

    except Exception as e:
        logger.error(f"获取看板待办失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取看板待办失败: {str(e)}'}), 500

@todos_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_todos():
    """获取所有待办事项"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()
    
    try:
        current_user = db.session.get(models['User'], current_user_id)
        if not current_user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        all_todos = []
        
        leave_apps = models['LeaveApplication'].query.filter(
            models['LeaveApplication'].status == 'pending',
            models['LeaveApplication'].approver_id == current_user_id
        ).all()
        
        for app in leave_apps:
            applicant = db.session.get(models['User'], app.user_id)
            all_todos.append({
                'id': f'leave_{app.id}',
                'category': 'approval',
                'type': 'leave',
                'type_name': '请假申请',
                'title': f"{applicant.username if applicant else '未知'}的请假申请",
                'applicant_name': f"{applicant.first_name or ''} {applicant.last_name or ''}".strip() or applicant.username if applicant else '未知',
                'status': app.status,
                'priority': 'high' if app.emergency_flag else 'medium',
                'created_at': app.created_at.isoformat() if app.created_at else None,
                'link': f'/attendance/leave-approval/{app.id}'
            })
        
        overtime_apps = models['OvertimeApplication'].query.filter(
            models['OvertimeApplication'].status == 'pending',
            models['OvertimeApplication'].approver_id == current_user_id
        ).all()
        
        for app in overtime_apps:
            applicant = db.session.get(models['User'], app.user_id)
            all_todos.append({
                'id': f'overtime_{app.id}',
                'category': 'approval',
                'type': 'overtime',
                'type_name': '加班申请',
                'title': f"{applicant.username if applicant else '未知'}的加班申请",
                'applicant_name': f"{applicant.first_name or ''} {applicant.last_name or ''}".strip() or applicant.username if applicant else '未知',
                'status': app.status,
                'priority': 'medium',
                'created_at': app.created_at.isoformat() if app.created_at else None,
                'link': f'/attendance/overtime-approval/{app.id}'
            })
        
        contract_approvals = models['ContractApproval'].query.filter(
            models['ContractApproval'].status == 'pending',
            models['ContractApproval'].approver_id == current_user_id
        ).all()
        
        for ca in contract_approvals:
            contract = db.session.get(models['Contract'], ca.contract_id)
            if contract:
                all_todos.append({
                    'id': f'contract_{ca.id}',
                    'category': 'approval',
                    'type': 'contract',
                    'type_name': '合同审批',
                    'title': f"合同审批: {contract.title}",
                    'status': ca.status,
                    'priority': 'high',
                    'created_at': ca.created_at.isoformat() if ca.created_at else None,
                    'link': f'/contracts/{contract.id}'
                })
        
        open_statuses = [
            models['BugStatus'].NEW.value,
            models['BugStatus'].ASSIGNED.value,
            models['BugStatus'].IN_PROGRESS.value,
            models['BugStatus'].REOPENED.value,
            models['BugStatus'].OPEN.value,
            models['BugStatus'].FIXED.value
        ]

        to_resolve = models['Bug'].query.filter(
            db.or_(
                models['Bug'].assigned_to == current_user_id,
                models['Bug'].resolved_by == current_user_id
            ),
            models['Bug'].status.in_(open_statuses)
        ).all()
        
        for bug in to_resolve:
            priority_map = {
                'critical': 'urgent',
                'high': 'high',
                'medium': 'medium',
                'low': 'low'
            }
            bug_priority = _get_enum_value(bug.priority)
            reporter = db.session.get(models['User'], bug.reported_by)
            all_todos.append({
                'id': f'bug_resolve_{bug.id}',
                'category': 'bug',
                'type': 'to_resolve',
                'type_name': '待解决Bug',
                'title': bug.title,
                'creator_name': reporter.username if reporter else '未知',
                'status': _get_enum_value(bug.status),
                'priority': priority_map.get(bug_priority, 'medium'),
                'created_at': bug.created_at.isoformat() if bug.created_at else None,
                'link': f'/bugs/{bug.id}'
            })

        to_verify_statuses = [models['BugStatus'].RESOLVED.value, models['BugStatus'].FIXED.value]
        to_verify = models['Bug'].query.filter(
            models['Bug'].verifier_id == current_user_id,
            models['Bug'].status.in_(to_verify_statuses)
        ).all()

        for bug in to_verify:
            reporter = db.session.get(models['User'], bug.reported_by)
            all_todos.append({
                'id': f'bug_verify_{bug.id}',
                'category': 'bug',
                'type': 'to_verify',
                'type_name': '待验证Bug',
                'title': bug.title,
                'creator_name': reporter.username if reporter else '未知',
                'status': _get_enum_value(bug.status),
                'priority': 'medium',
                'created_at': bug.resolved_at.isoformat() if bug.resolved_at else None,
                'link': f'/bugs/{bug.id}'
            })
        
        # 需求评审：以 RequirementReviewStep 为真相源
        for rev_todo in _get_requirement_review_todos(models, current_user_id, db.session):
            all_todos.append(rev_todo)

        # 测试用例评审：以 TestCaseReviewStep 为真相源
        for rev_todo in _get_test_case_review_todos(models, current_user_id, db.session):
            all_todos.append(rev_todo)

        # 新版多级合同审批：以 ContractReviewStep 为真相源
        all_todos.extend(_get_contract_review_todos(models, current_user_id, db.session))
        
        pending_deliveries = models['ContractDelivery'].query.filter(
            models['ContractDelivery'].status == 'pending'
        ).all()
        
        for delivery in pending_deliveries:
            contract = db.session.get(models['Contract'], delivery.contract_id)
            all_todos.append({
                'id': f'delivery_{delivery.id}',
                'category': 'contract',
                'type': 'delivery_pending',
                'type_name': '待交付',
                'title': f"合同交付待处理: {delivery.site_name or delivery.delivery_no}",
                'contract_id': delivery.contract_id,
                'contract_title': contract.title if contract else '未知合同',
                'status': delivery.status,
                'priority': 'high',
                'created_at': delivery.planned_date.isoformat() if delivery.planned_date else None,
                'link': f'/contracts/{delivery.contract_id}'
            })
        
        pending_risks = models['ContractRisk'].query.filter(
            models['ContractRisk'].status.in_(['identified', 'mitigation_in_progress'])
        ).all()
        
        for risk in pending_risks:
            contract = db.session.get(models['Contract'], risk.contract_id)
            risk_priority = 'high' if risk.risk_level in ['high', 'critical'] else 'medium'
            all_todos.append({
                'id': f'risk_{risk.id}',
                'category': 'contract',
                'type': 'risk_pending',
                'type_name': '待处理风险',
                'title': f"合同风险: {risk.risk_description[:50] if risk.risk_description else '未描述'}",
                'contract_id': risk.contract_id,
                'contract_title': contract.title if contract else '未知合同',
                'status': risk.status,
                'priority': risk_priority,
                'created_at': risk.created_at.isoformat() if hasattr(risk, 'created_at') and risk.created_at else None,
                'link': f'/contracts/{risk.contract_id}'
            })
        
        pending_payments = models['ContractPayment'].query.filter(
            models['ContractPayment'].status == 'pending'
        ).all()
        
        for payment in pending_payments:
            contract = db.session.get(models['Contract'], payment.contract_id)
            all_todos.append({
                'id': f'payment_{payment.id}',
                'category': 'contract',
                'type': 'payment_pending',
                'type_name': '待付款',
                'title': f"合同付款待处理: {payment.payment_stage}",
                'contract_id': payment.contract_id,
                'contract_title': contract.title if contract else '未知合同',
                'amount': payment.planned_amount,
                'status': payment.status,
                'priority': 'high',
                'created_at': payment.planned_date.isoformat() if payment.planned_date else None,
                'link': f'/contracts/{payment.contract_id}'
            })

        # 正在开发的看板卡片（指派给当前用户的）
        rd_items = models['RDKanbanItem'].query.filter(
            models['RDKanbanItem'].column == 'in_progress',
            models['RDKanbanItem'].assignee_id == current_user_id
        ).order_by(models['RDKanbanItem'].sort_order.asc()).all()

        for item in rd_items:
            project = db.session.get(models['Project'], item.project_id)
            all_todos.append({
                'id': f'rd_kanban_{item.id}',
                'category': 'rd_kanban',
                'type': 'in_progress',
                'type_name': '正在开发',
                'title': item.title,
                'project_id': item.project_id,
                'project_name': project.name if project else '未知项目',
                'status': item.status or 'in_progress',
                'priority': 'medium',
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'link': f'/projects/rd-management?project={item.project_id}'
            })

        priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_todos.sort(key=lambda x: (
            priority_order.get(x.get('priority', 'medium'), 2),
            x['created_at'] or ''
        ))
        
        return jsonify({
            'success': True,
            'data': {
                'todos': all_todos,
                'total': len(all_todos)
            }
        })
        
    except Exception as e:
        logger.error(f"获取所有待办事项失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取所有待办事项失败: {str(e)}'}), 500
