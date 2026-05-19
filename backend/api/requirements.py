"""
需求管理API模块
提供需求文档、需求条目、评论、关联关系、版本历史等功能的RESTful API
增强版本：支持需求管理完整工作流
"""

from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from datetime import datetime
import json
import io

from services.email_service import email_service

requirements_bp = Blueprint('requirements', __name__, url_prefix='/')

# 延迟导入数据库模型以避免循环导入
def get_db_and_models():
    from enhanced_app import db, RequirementDocument, RequirementItem, RequirementComment, RequirementLink, RequirementVersion, User
    return db, RequirementDocument, RequirementItem, RequirementComment, RequirementLink, RequirementVersion, User


def get_current_user_id():
    """获取当前用户ID"""
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('id')
    return identity


def check_project_permission(project_id, user_id):
    """检查用户是否有项目权限"""
    from enhanced_app import ProjectMember, Project
    
    # 检查是否是项目成员或管理员
    user = User.query.get(user_id)
    if user and user.role in ['admin', 'manager', 'project_manager']:
        return True
    
    member = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=user_id
    ).first()
    
    return member is not None


# ==================== 需求文档 API ====================

@requirements_bp.route('/projects/<int:project_id>/requirement-documents', methods=['GET'])
@jwt_required()
def get_requirement_documents(project_id):
    """获取项目下的需求文档列表"""
    try:
        user_id = get_current_user_id()
        
        # 检查权限
        if not check_project_permission(project_id, user_id):
            return jsonify({'error': '无权访问该项目'}), 403
        
        # 查询参数
        status = request.args.get('status')
        doc_type = request.args.get('doc_type')
        keyword = request.args.get('keyword')
        
        query = RequirementDocument.query.filter_by(project_id=project_id)
        
        if status:
            query = query.filter_by(status=status)
        if doc_type:
            query = query.filter_by(doc_type=doc_type)
        if keyword:
            query = query.filter(RequirementDocument.name.contains(keyword))
        
        documents = query.order_by(RequirementDocument.updated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'documents': [doc.to_dict() for doc in documents]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/projects/<int:project_id>/requirement-documents', methods=['POST'])
@jwt_required()
def create_requirement_document(project_id):
    """创建需求文档"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        # 检查权限（只有项目经理或管理员可以创建）
        user = User.query.get(user_id)
        if user.role not in ['admin', 'manager', 'project_manager']:
            return jsonify({'error': '无权创建需求文档'}), 403
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'error': '文档名称不能为空'}), 400
        
        document = RequirementDocument(
            project_id=project_id,
            name=data['name'],
            description=data.get('description', ''),
            doc_type=data.get('doc_type', 'functional'),
            owner_id=data.get('owner_id'),
            status='draft',
            version=1,
            created_by=user_id
        )
        
        db.session.add(document)
        db.session.commit()
        
        # 创建初始版本记录
        version = RequirementVersion(
            doc_id=document.id,
            version=1,
            change_summary='创建文档',
            created_by=user_id
        )
        db.session.add(version)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '需求文档创建成功',
            'document': document.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-documents/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_requirement_document(doc_id):
    """获取需求文档详情"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该文档'}), 403
        
        # 获取文档下的需求条目
        items = RequirementItem.query.filter_by(doc_id=doc_id).order_by(RequirementItem.identifier).all()
        
        result = document.to_dict()
        result['items'] = [item.to_dict() for item in items]
        
        return jsonify({
            'success': True,
            'document': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-documents/<int:doc_id>', methods=['PUT'])
@jwt_required()
def update_requirement_document(doc_id):
    """更新需求文档"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        data = request.get_json()
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权修改该文档'}), 403
        
        # 更新字段
        if 'name' in data:
            document.name = data['name']
        if 'description' in data:
            document.description = data['description']
        if 'doc_type' in data:
            document.doc_type = data['doc_type']
        if 'status' in data:
            document.status = data['status']
        
        document.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '需求文档更新成功',
            'document': document.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-documents/<int:doc_id>', methods=['DELETE'])
@jwt_required()
def delete_requirement_document(doc_id):
    """删除需求文档"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        
        # 检查权限（只有创建者或管理员可以删除）
        user = User.query.get(user_id)
        if document.created_by != user_id and user.role not in ['manager', 'project_manager']:
            return jsonify({'error': '无权删除该文档'}), 403
        
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '需求文档删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-documents/<int:doc_id>/change-status', methods=['POST'])
@jwt_required()
def change_document_status(doc_id):
    """变更需求文档状态"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        data = request.get_json()
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({'error': '状态不能为空'}), 400
        
        # 检查权限
        user = User.query.get(user_id)
        if user.role not in ['admin', 'manager', 'project_manager']:
            return jsonify({'error': '无权创建版本'}), 403
        
        document.status = new_status
        document.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'文档状态已更新为 {new_status}',
            'document': document.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== 需求条目 API ====================

@requirements_bp.route('/requirement-documents/<int:doc_id>/items', methods=['GET'])
@jwt_required()
def get_requirement_items(doc_id):
    """获取需求文档下的条目列表"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该文档'}), 403
        
        # 查询参数
        status = request.args.get('status')
        priority = request.args.get('priority')
        module = request.args.get('module')
        
        query = RequirementItem.query.filter_by(doc_id=doc_id)
        
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=int(priority))
        if module:
            query = query.filter_by(module=module)
        
        items = query.order_by(RequirementItem.identifier).all()
        
        return jsonify({
            'success': True,
            'items': [item.to_dict() for item in items]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-documents/<int:doc_id>/items', methods=['POST'])
@jwt_required()
def create_requirement_item(doc_id):
    """创建需求条目"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        data = request.get_json()
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权在该文档下创建条目'}), 403
        
        # 验证必填字段
        if not data.get('title'):
            return jsonify({'error': '需求标题不能为空'}), 400
        
        # 生成唯一标识符
        existing_items = RequirementItem.query.filter_by(doc_id=doc_id).count()
        identifier = data.get('identifier', f'REQ-{existing_items + 1:03d}')
        
        item = RequirementItem(
            doc_id=doc_id,
            parent_id=data.get('parent_id'),
            identifier=identifier,
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 2),
            status=data.get('status', 'pending_review'),
            module=data.get('module', ''),
            owner_id=data.get('owner_id'),
            created_by=user_id,
            planned_version=data.get('planned_version', ''),
            actual_version=data.get('actual_version', '')
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '需求条目创建成功',
            'item': item.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-items/<int:item_id>', methods=['GET'])
@jwt_required()
def get_requirement_item(item_id):
    """获取需求条目详情"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        document = RequirementDocument.query.get(item.doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该条目'}), 403
        
        # 获取关联关系
        links = RequirementLink.query.filter_by(requirement_id=item_id).all()
        
        result = item.to_dict()
        result['links'] = [link.to_dict() for link in links]
        
        return jsonify({
            'success': True,
            'item': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_requirement_item(item_id):
    """更新需求条目"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        document = RequirementDocument.query.get(item.doc_id)
        data = request.get_json()
        
        # 检查权限（只有负责人、创建者或管理员可以修改）
        user = User.query.get(user_id)
        if item.owner_id != user_id and item.created_by != user_id and user.role not in ['admin', 'manager', 'project_manager']:
            return jsonify({'error': '无权修改该条目'}), 403
        
        # 更新字段
        if 'title' in data:
            item.title = data['title']
        if 'description' in data:
            item.description = data['description']
        if 'priority' in data:
            item.priority = data['priority']
        if 'status' in data:
            item.status = data['status']
        if 'module' in data:
            item.module = data['module']
        if 'owner_id' in data:
            item.owner_id = data['owner_id']
        if 'planned_version' in data:
            item.planned_version = data['planned_version']
        if 'actual_version' in data:
            item.actual_version = data['actual_version']
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '需求条目更新成功',
            'item': item.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_requirement_item(item_id):
    """删除需求条目"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        document = RequirementDocument.query.get(item.doc_id)
        
        # 检查权限
        user = User.query.get(user_id)
        if item.created_by != user_id and user.role not in ['admin', 'manager', 'project_manager']:
            return jsonify({'error': '无权删除该条目'}), 403
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '需求条目删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-items/<int:item_id>/change-status', methods=['POST'])
@jwt_required()
def change_item_status(item_id):
    """变更需求条目状态"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        document = RequirementDocument.query.get(item.doc_id)
        data = request.get_json()
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({'error': '状态不能为空'}), 400
        
        # 检查权限
        user = User.query.get(user_id)
        if item.owner_id != user_id and item.created_by != user_id and user.role not in ['admin', 'manager', 'project_manager']:
            return jsonify({'error': '无权变更该条目状态'}), 403
        
        item.status = new_status
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'需求状态已更新为 {new_status}',
            'item': item.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== 评论 API ====================

@requirements_bp.route('/requirement-documents/<int:doc_id>/comments', methods=['GET'])
@jwt_required()
def get_document_comments(doc_id):
    """获取文档评论列表"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该文档'}), 403
        
        comments = RequirementComment.query.filter_by(
            target_type='document',
            target_id=doc_id
        ).order_by(RequirementComment.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'comments': [comment.to_dict() for comment in comments]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-items/<int:item_id>/comments', methods=['GET'])
@jwt_required()
def get_item_comments(item_id):
    """获取需求条目评论列表"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        document = RequirementDocument.query.get(item.doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该条目'}), 403
        
        comments = RequirementComment.query.filter_by(
            target_type='item',
            target_id=item_id
        ).order_by(RequirementComment.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'comments': [comment.to_dict() for comment in comments]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-comments', methods=['POST'])
@jwt_required()
def create_comment():
    """创建评论"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        content = data.get('content')
        
        if not target_type or not target_id or not content:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 检查权限
        if target_type == 'document':
            document = RequirementDocument.query.get_or_404(target_id)
            if not check_project_permission(document.project_id, user_id):
                return jsonify({'error': '无权评论该文档'}), 403
        elif target_type == 'item':
            item = RequirementItem.query.get_or_404(target_id)
            document = RequirementDocument.query.get(item.doc_id)
            if not check_project_permission(document.project_id, user_id):
                return jsonify({'error': '无权评论该条目'}), 403
        else:
            return jsonify({'error': '无效的目标类型'}), 400
        
        comment = RequirementComment(
            target_type=target_type,
            target_id=target_id,
            item_id=target_id if target_type == 'item' else None,
            content=content,
            created_by=user_id,
            reply_to=data.get('reply_to')
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '评论创建成功',
            'comment': comment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """删除评论"""
    try:
        user_id = get_current_user_id()
        comment = RequirementComment.query.get_or_404(comment_id)
        
        # 检查权限
        user = User.query.get(user_id)
        if comment.created_by != user_id and user.role not in ['manager', 'project_manager']:
            return jsonify({'error': '无权删除该评论'}), 403
        
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '评论删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== 关联关系 API ====================

@requirements_bp.route('/requirement-items/<int:item_id>/links', methods=['GET'])
@jwt_required()
def get_requirement_links(item_id):
    """获取需求条目的关联关系"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        document = RequirementDocument.query.get(item.doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该条目'}), 403
        
        links = RequirementLink.query.filter_by(requirement_id=item_id).all()
        
        return jsonify({
            'success': True,
            'links': [link.to_dict() for link in links]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-links', methods=['POST'])
@jwt_required()
def create_requirement_link():
    """创建需求关联关系"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        requirement_id = data.get('requirement_id')
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        
        if not requirement_id or not target_type or not target_id:
            return jsonify({'error': '缺少必要参数'}), 400
        
        item = RequirementItem.query.get_or_404(requirement_id)
        document = RequirementDocument.query.get(item.doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权创建关联关系'}), 403
        
        link = RequirementLink(
            requirement_id=requirement_id,
            target_type=target_type,
            target_id=target_id,
            link_type=data.get('link_type', 'implements'),
            created_by=user_id
        )
        
        db.session.add(link)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '关联关系创建成功',
            'link': link.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-links/<int:link_id>', methods=['DELETE'])
@jwt_required()
def delete_requirement_link(link_id):
    """删除需求关联关系"""
    try:
        user_id = get_current_user_id()
        link = RequirementLink.query.get_or_404(link_id)
        item = RequirementItem.query.get(link.requirement_id)
        document = RequirementDocument.query.get(item.doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权删除该关联关系'}), 403
        
        db.session.delete(link)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '关联关系删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== 版本历史 API ====================

@requirements_bp.route('/requirement-documents/<int:doc_id>/versions', methods=['GET'])
@jwt_required()
def get_document_versions(doc_id):
    """获取需求文档版本历史"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该文档'}), 403
        
        versions = RequirementVersion.query.filter_by(doc_id=doc_id).order_by(RequirementVersion.version.desc()).all()
        
        return jsonify({
            'success': True,
            'versions': [version.to_dict() for version in versions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-documents/<int:doc_id>/create-version', methods=['POST'])
@jwt_required()
def create_document_version(doc_id):
    """创建需求文档新版本"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        data = request.get_json()
        
        # 检查权限
        user = User.query.get(user_id)
        if user.role not in ['admin', 'manager', 'project_manager']:
            return jsonify({'error': '无权创建版本'}), 403
        
        # 获取当前所有条目
        items = RequirementItem.query.filter_by(doc_id=doc_id).all()
        
        # 创建快照
        snapshot = {
            'document': {
                'name': document.name,
                'description': document.description,
                'doc_type': document.doc_type,
                'status': document.status
            },
            'items': [item.to_dict() for item in items]
        }
        
        # 新版本号
        new_version = document.version + 1
        
        version = RequirementVersion(
            doc_id=doc_id,
            version=new_version,
            snapshot=json.dumps(snapshot, ensure_ascii=False),
            change_summary=data.get('change_summary', ''),
            created_by=user_id
        )
        
        db.session.add(version)
        
        # 更新文档版本号
        document.version = new_version
        document.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'版本 {new_version} 创建成功',
            'version': version.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-versions/<int:version_id>', methods=['GET'])
@jwt_required()
def get_version_detail(version_id):
    """获取版本详情"""
    try:
        user_id = get_current_user_id()
        version = RequirementVersion.query.get_or_404(version_id)
        document = RequirementDocument.query.get(version.doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该版本'}), 403
        
        result = version.to_dict()
        if version.snapshot:
            result['snapshot'] = json.loads(version.snapshot)
        
        return jsonify({
            'success': True,
            'version': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 统计 API ====================

@requirements_bp.route('/projects/<int:project_id>/requirement-statistics', methods=['GET'])
@jwt_required()
def get_requirement_statistics(project_id):
    """获取项目需求统计信息"""
    try:
        user_id = get_current_user_id()
        
        # 检查权限
        if not check_project_permission(project_id, user_id):
            return jsonify({'error': '无权访问该项目'}), 403
        
        # 文档统计
        doc_status_counts = db.session.query(
            RequirementDocument.status,
            db.func.count(RequirementDocument.id)
        ).filter_by(project_id=project_id).group_by(RequirementDocument.status).all()
        
        # 条目统计
        item_status_counts = db.session.query(
            RequirementItem.status,
            db.func.count(RequirementItem.id)
        ).join(RequirementDocument).filter(
            RequirementDocument.project_id == project_id
        ).group_by(RequirementItem.status).all()
        
        item_priority_counts = db.session.query(
            RequirementItem.priority,
            db.func.count(RequirementItem.id)
        ).join(RequirementDocument).filter(
            RequirementDocument.project_id == project_id
        ).group_by(RequirementItem.priority).all()
        
        return jsonify({
            'success': True,
            'statistics': {
                'document_status': {status: count for status, count in doc_status_counts},
                'item_status': {status: count for status, count in item_status_counts},
                'item_priority': {str(priority): count for priority, count in item_priority_counts}
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-documents/<int:doc_id>/trace-matrix', methods=['GET'])
@jwt_required()
def get_requirement_trace_matrix(doc_id):
    """获取需求跟踪矩阵"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        
        # 检查权限
        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该文档'}), 403
        
        # 查询参数
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        # 获取文档下的所有需求条目
        query = RequirementItem.query.filter_by(doc_id=doc_id)
        
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=int(priority))
        
        items = query.order_by(RequirementItem.identifier).all()
        
        # 构建跟踪矩阵数据
        matrix_data = []
        for item in items:
            # 统计各类关联数量
            links = RequirementLink.query.filter_by(requirement_id=item.id).all()
            
            task_count = sum(1 for link in links if link.target_type == 'task')
            bug_count = sum(1 for link in links if link.target_type == 'bug')
            test_case_count = sum(1 for link in links if link.target_type == 'test_case')
            
            # 计算覆盖率 (有任一关联即为已覆盖)
            total_links = task_count + bug_count + test_case_count
            coverage = 100 if total_links > 0 else 0
            
            matrix_data.append({
                'id': item.id,
                'doc_id': item.doc_id,
                'identifier': item.identifier,
                'title': item.title,
                'priority': item.priority,
                'status': item.status,
                'owner_id': item.owner_id,
                'owner_name': item.owner.username if item.owner else None,
                'task_count': task_count,
                'bug_count': bug_count,
                'test_case_count': test_case_count,
                'coverage': coverage
            })
        
        # 统计信息
        total_requirements = len(matrix_data)
        linked_requirements = sum(1 for item in matrix_data if item['task_count'] > 0 or item['bug_count'] > 0 or item['test_case_count'] > 0)
        total_tasks = sum(item['task_count'] for item in matrix_data)
        total_bugs = sum(item['bug_count'] for item in matrix_data)
        
        return jsonify({
            'success': True,
            'matrix_data': matrix_data,
            'statistics': {
                'total_requirements': total_requirements,
                'linked_requirements': linked_requirements,
                'total_tasks': total_tasks,
                'total_bugs': total_bugs
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 增强权限检查 API ====================

def check_requirement_permission(project_id, user_id, permission_type='view'):
    """检查用户在需求文档上的权限
    permission_type: view, edit, delete, approve, manage
    """
    from enhanced_app import ProjectMember, Project

    user = User.query.get(user_id)
    if not user:
        return False

    if user.role in ['admin', 'manager']:
        return True

    member = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=user_id
    ).first()

    if not member:
        return False

    if user.role == 'project_manager':
        return True

    member_role = member.role if hasattr(member, 'role') else 'member'

    permission_map = {
        'view': ['project_manager', 'developer', 'tester', 'member', 'guest'],
        'edit': ['project_manager', 'developer', 'tester', 'member'],
        'delete': ['project_manager'],
        'approve': ['project_manager'],
        'manage': ['project_manager']
    }

    return member_role in permission_map.get(permission_type, ['project_manager'])


@requirements_bp.route('/requirement-documents/<int:doc_id>/permissions', methods=['GET'])
@jwt_required()
def get_document_permissions(doc_id):
    """获取当前用户对需求文档的权限"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)

        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该文档'}), 403

        user = User.query.get(user_id)
        is_manager = user.role in ['manager', 'project_manager']

        permissions = {
            'can_view': True,
            'can_edit': is_manager or check_requirement_permission(document.project_id, user_id, 'edit'),
            'can_delete': is_manager,
            'can_approve': is_manager,
            'can_manage': is_manager,
            'can_review': not is_manager,
            'is_owner': document.created_by == user_id
        }

        return jsonify({
            'success': True,
            'permissions': permissions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 需求条目复制/移动 API ====================

@requirements_bp.route('/requirement-items/<int:item_id>/copy', methods=['POST'])
@jwt_required()
def copy_requirement_item(item_id):
    """复制需求条目到同一文档或不同文档"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        document = RequirementDocument.query.get(item.doc_id)
        data = request.get_json()

        target_doc_id = data.get('target_doc_id', item.doc_id)
        target_document = RequirementDocument.query.get_or_404(target_doc_id)

        if not check_requirement_permission(target_document.project_id, user_id, 'edit'):
            return jsonify({'error': '无权在目标文档创建条目'}), 403

        existing_items = RequirementItem.query.filter_by(doc_id=target_doc_id).count()
        new_identifier = data.get('identifier', f'REQ-{existing_items + 1:03d}')

        new_item = RequirementItem(
            doc_id=target_doc_id,
            parent_id=None,
            identifier=new_identifier,
            title=data.get('title', item.title) + ' (副本)',
            description=item.description,
            priority=item.priority,
            status='pending_review',
            module=item.module,
            owner_id=None,
            created_by=user_id,
            planned_version=item.planned_version,
            actual_version=None
        )

        db.session.add(new_item)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '需求条目复制成功',
            'item': new_item.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-items/<int:item_id>/move', methods=['POST'])
@jwt_required()
def move_requirement_item(item_id):
    """移动需求条目到其他文档"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        source_document = RequirementDocument.query.get(item.doc_id)
        data = request.get_json()

        target_doc_id = data.get('target_doc_id')
        if not target_doc_id:
            return jsonify({'error': '目标文档ID不能为空'}), 400

        target_document = RequirementDocument.query.get_or_404(target_doc_id)

        if not check_requirement_permission(source_document.project_id, user_id, 'edit'):
            return jsonify({'error': '无权移动该条目'}), 403

        if not check_requirement_permission(target_document.project_id, user_id, 'edit'):
            return jsonify({'error': '无权在目标文档创建条目'}), 403

        existing_items = RequirementItem.query.filter_by(doc_id=target_doc_id).count()
        new_identifier = data.get('identifier', f'REQ-{existing_items + 1:03d}')

        item.doc_id = target_doc_id
        item.identifier = new_identifier
        item.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '需求条目移动成功',
            'item': item.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== 需求条目历史记录 API ====================

@requirements_bp.route('/requirement-items/<int:item_id>/history', methods=['GET'])
@jwt_required()
def get_item_history(item_id):
    """获取需求条目的变更历史"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        document = RequirementDocument.query.get(item.doc_id)

        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该条目'}), 403

        history = item.get_change_history() if hasattr(item, 'get_change_history') else []

        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 评审工作流 API ====================

@requirements_bp.route('/requirement-documents/<int:doc_id>/review', methods=['POST'])
@jwt_required()
def initiate_review(doc_id):
    """发起需求文档评审"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)
        data = request.get_json()

        if not check_requirement_permission(document.project_id, user_id, 'approve'):
            return jsonify({'error': '无权发起评审'}), 403

        reviewers = data.get('reviewers', [])
        deadline = data.get('deadline')
        review_type = data.get('review_type', 'document')

        document.status = 'reviewing'
        document.updated_at = datetime.utcnow()

        from enhanced_app import Notification

        # 获取发起人信息
        initiator = User.query.get(user_id)
        initiator_name = initiator.username if initiator else '系统'

        # 格式化截止时间
        deadline_str = None
        if deadline:
            if isinstance(deadline, str):
                deadline_str = deadline
            else:
                deadline_str = deadline.strftime('%Y-%m-%d %H:%M') if hasattr(deadline, 'strftime') else str(deadline)

        # 构建跳转链接
        review_link = f'/projects/{document.project_id}/requirements/{doc_id}'

        for reviewer_id in reviewers:
            # 创建系统通知
            notification = Notification(
                user_id=reviewer_id,
                type='requirement_review',
                title='您有新的需求评审',
                content=f'需求文档 "{document.name}" 需要您进行评审',
                link=review_link
            )
            db.session.add(notification)

            # 发送邮件通知
            reviewer = User.query.get(reviewer_id)
            if reviewer and reviewer.email:
                email_service.send_review_notification_email(
                    to_address=reviewer.email,
                    doc_name=document.name,
                    initiator_name=initiator_name,
                    deadline=deadline_str,
                    review_type='文档评审',
                    review_link=review_link
                )

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '评审已发起',
            'document': document.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-items/<int:item_id>/review', methods=['POST'])
@jwt_required()
def review_item(item_id):
    """评审需求条目"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        document = RequirementDocument.query.get(item.doc_id)
        data = request.get_json()

        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权评审该条目'}), 403

        conclusion = data.get('conclusion')
        if conclusion:
            status_map = {
                'approved': 'approved',
                'needs_modification': 'pending_review',
                'rejected': 'rejected'
            }
            item.status = status_map.get(conclusion, item.status)

        comment_content = data.get('comment', '')
        if comment_content:
            reviewer_comment = RequirementComment(
                target_type='item',
                target_id=item_id,
                item_id=item_id,
                content=f"[评审意见] {comment_content}",
                created_by=user_id
            )
            db.session.add(reviewer_comment)

        item.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '评审完成',
            'item': item.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== 版本对比与回滚 API ====================

@requirements_bp.route('/requirement-documents/<int:doc_id>/compare-versions', methods=['GET'])
@jwt_required()
def compare_versions(doc_id):
    """对比两个版本的差异"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)

        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该文档'}), 403

        version1 = request.args.get('v1', type=int)
        version2 = request.args.get('v2', type=int)

        if not version1 or not version2:
            return jsonify({'error': '需要提供两个版本号'}), 400

        ver1 = RequirementVersion.query.filter_by(doc_id=doc_id, version=version1).first()
        ver2 = RequirementVersion.query.filter_by(doc_id=doc_id, version=version2).first()

        if not ver1 or not ver2:
            return jsonify({'error': '版本不存在'}), 404

        snapshot1 = json.loads(ver1.snapshot) if ver1.snapshot else {}
        snapshot2 = json.loads(ver2.snapshot) if ver2.snapshot else {}

        differences = {
            'document': {
                'name_changed': snapshot1.get('document', {}).get('name') != snapshot2.get('document', {}).get('name'),
                'description_changed': snapshot1.get('document', {}).get('description') != snapshot2.get('document', {}).get('description'),
                'status_changed': snapshot1.get('document', {}).get('status') != snapshot2.get('document', {}).get('status')
            },
            'items_added': [],
            'items_removed': [],
            'items_modified': []
        }

        items1 = {item['identifier']: item for item in snapshot1.get('items', [])}
        items2 = {item['identifier']: item for item in snapshot2.get('items', [])}

        for identifier in items2:
            if identifier not in items1:
                differences['items_added'].append(items2[identifier])
            elif items1[identifier] != items2[identifier]:
                differences['items_modified'].append({
                    'identifier': identifier,
                    'before': items1[identifier],
                    'after': items2[identifier]
                })

        for identifier in items1:
            if identifier not in items2:
                differences['items_removed'].append(items1[identifier])

        return jsonify({
            'success': True,
            'v1': version1,
            'v2': version2,
            'differences': differences
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requirements_bp.route('/requirement-documents/<int:doc_id>/rollback/<int:version_num>', methods=['POST'])
@jwt_required()
def rollback_to_version(doc_id, version_num):
    """回滚到指定版本"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)

        if not check_requirement_permission(document.project_id, user_id, 'manage'):
            return jsonify({'error': '无权执行回滚操作'}), 403

        version = RequirementVersion.query.filter_by(doc_id=doc_id, version=version_num).first()
        if not version:
            return jsonify({'error': '指定版本不存在'}), 404

        snapshot = json.loads(version.snapshot) if version.snapshot else {}
        doc_data = snapshot.get('document', {})
        items_data = snapshot.get('items', [])

        document.name = doc_data.get('name', document.name)
        document.description = doc_data.get('description', document.description)
        document.doc_type = doc_data.get('doc_type', document.doc_type)
        document.status = doc_data.get('status', document.status)
        document.updated_at = datetime.utcnow()

        RequirementItem.query.filter_by(doc_id=doc_id).delete()

        for item_data in items_data:
            new_item = RequirementItem(
                doc_id=doc_id,
                identifier=item_data.get('identifier'),
                title=item_data.get('title'),
                description=item_data.get('description'),
                priority=item_data.get('priority', 2),
                status=item_data.get('status', 'pending_review'),
                module=item_data.get('module', ''),
                owner_id=item_data.get('owner_id'),
                created_by=user_id,
                planned_version=item_data.get('planned_version', ''),
                actual_version=item_data.get('actual_version', '')
            )
            db.session.add(new_item)

        new_version = RequirementVersion(
            doc_id=doc_id,
            version=document.version + 1,
            snapshot=json.dumps(snapshot, ensure_ascii=False),
            change_summary=f'从版本 {version_num} 回滚',
            created_by=user_id
        )
        db.session.add(new_version)
        document.version = document.version + 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'已回滚到版本 {version_num}',
            'document': document.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== 文档导出 API ====================

@requirements_bp.route('/requirement-documents/<int:doc_id>/export', methods=['GET'])
@jwt_required()
def export_document(doc_id):
    """导出需求文档"""
    try:
        user_id = get_current_user_id()
        document = RequirementDocument.query.get_or_404(doc_id)

        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该文档'}), 403

        export_format = request.args.get('format', 'markdown').lower()
        items = RequirementItem.query.filter_by(doc_id=doc_id).order_by(RequirementItem.identifier).all()

        if export_format == 'markdown':
            content = generate_markdown(document, items)
            mime_type = 'text/markdown'
            filename = f'{document.name}.md'
        elif export_format == 'json':
            content = json.dumps({
                'document': document.to_dict(),
                'items': [item.to_dict() for item in items]
            }, ensure_ascii=False, indent=2)
            mime_type = 'application/json'
            filename = f'{document.name}.json'
        elif export_format == 'html':
            content = generate_html(document, items)
            mime_type = 'text/html'
            filename = f'{document.name}.html'
        else:
            return jsonify({'error': '不支持的导出格式'}), 400

        response = make_response(content)
        response.headers['Content-Type'] = mime_type
        response.headers['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{filename}'

        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_markdown(document, items):
    """生成Markdown格式的文档"""
    md = []
    md.append(f'# {document.name}\n')

    status_map = {
        'draft': '草稿',
        'reviewing': '评审中',
        'approved': '已批准',
        'deprecated': '已废弃'
    }

    doc_type_map = {
        'functional': '功能需求',
        'non_functional': '非功能需求'
    }

    md.append(f'- **文档类型**: {doc_type_map.get(document.doc_type, document.doc_type)}')
    md.append(f'- **状态**: {status_map.get(document.status, document.status)}')
    md.append(f'- **版本**: v{document.version}')
    md.append(f'- **创建时间**: {document.created_at.strftime("%Y-%m-%d %H:%M") if document.created_at else "-"}')
    md.append(f'- **更新时间**: {document.updated_at.strftime("%Y-%m-%d %H:%M") if document.updated_at else "-"}\n')

    if document.description:
        md.append(f'## 文档描述\n{document.description}\n')

    md.append(f'## 需求条目 (共 {len(items)} 项)\n')

    priority_map = {1: '低', 2: '中', 3: '高'}
    status_item_map = {
        'pending_review': '待评审',
        'reviewed': '已评审',
        'approved': '已批准',
        'in_progress': '开发中',
        'completed': '已完成',
        'verified': '已验证'
    }

    for item in items:
        md.append(f'### {item.identifier} - {item.title}\n')
        md.append(f'- **优先级**: {priority_map.get(item.priority, "中")}')
        md.append(f'- **状态**: {status_item_map.get(item.status, item.status)}')
        md.append(f'- **模块**: {item.module or "-"}')
        md.append(f'- **负责人**: {item.owner.username if item.owner else "未分配"}')
        md.append(f'- **计划版本**: {item.planned_version or "-"}')
        md.append(f'- **实际版本**: {item.actual_version or "-"}\n')

        if item.description:
            md.append(f'**描述**: \n{item.description}\n')

        md.append('---\n')

    return '\n'.join(md)


def generate_html(document, items):
    """生成HTML格式的文档"""
    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html><head><meta charset="utf-8">')
    html.append(f'<title>{document.name}</title>')
    html.append('<style>')
    html.append('body{font-family:Arial,sans-serif;max-width:900px;margin:0 auto;padding:20px;}')
    html.append('h1{color:#333;border-bottom:2px solid #409eff;padding-bottom:10px;}')
    html.append('h2{color:#666;margin-top:30px;}')
    html.append('h3{color:#409eff;}')
    html.append('.meta{margin:10px 0;color:#666;}')
    html.append('.item{border:1px solid #e4e7ed;padding:15px;margin:15px 0;border-radius:8px;}')
    html.append('.tag{display:inline-block;padding:2px 8px;margin-right:5px;border-radius:4px;font-size:12px;}')
    html.append('.tag-info{background:#ecf5ff;color:#409eff;}')
    html.append('.tag-success{background:#f0f9eb;color:#67c23a;}')
    html.append('.tag-warning{background:#fdf6ec;color:#e6a23c;}')
    html.append('.tag-danger{background:#fef0f0;color:#f56c6c;}')
    html.append('</style></head><body>')

    html.append(f'<h1>{document.name}</h1>')
    html.append('<div class="meta">')
    html.append(f'<span>类型: {"功能需求" if document.doc_type == "functional" else "非功能需求"}</span> | ')
    html.append(f'<span>状态: {"草稿" if document.status == "draft" else "评审中" if document.status == "reviewing" else "已批准" if document.status == "approved" else "已废弃"}</span> | ')
    html.append(f'<span>版本: v{document.version}</span>')
    html.append('</div>')

    if document.description:
        html.append(f'<h2>文档描述</h2><p>{document.description}</p>')

    html.append(f'<h2>需求条目 (共 {len(items)} 项)</h2>')

    for item in items:
        html.append('<div class="item">')
        html.append(f'<h3>{item.identifier} - {item.title}</h3>')
        priority_class = 'danger' if item.priority == 3 else 'warning' if item.priority == 2 else 'info'
        priority_text = '高' if item.priority == 3 else '中' if item.priority == 2 else '低'
        html.append(f'<span class="tag tag-{priority_class}">{priority_text}优先级</span>')

        status_class = 'info' if item.status in ['pending_review', 'reviewed'] else 'success' if item.status in ['approved', 'completed', 'verified'] else 'warning'
        status_text = '待评审' if item.status == 'pending_review' else '已评审' if item.status == 'reviewed' else '已批准' if item.status == 'approved' else '开发中' if item.status == 'in_progress' else '已完成' if item.status == 'completed' else '已验证'
        html.append(f'<span class="tag tag-{status_class}">{status_text}</span>')

        html.append(f'<p><strong>模块:</strong> {item.module or "-"} | <strong>负责人:</strong> {item.owner.username if item.owner else "未分配"}</p>')

        if item.description:
            html.append(f'<p><strong>描述:</strong> {item.description}</p>')
        html.append('</div>')

    html.append('</body></html>')
    return ''.join(html)


# ==================== 个人待办 API ====================

@requirements_bp.route('/my/requirement-todos', methods=['GET'])
@jwt_required()
def get_my_requirement_todos():
    """获取当前用户的需求相关待办"""
    try:
        user_id = get_current_user_id()

        items_as_owner = RequirementItem.query.filter(
            RequirementItem.owner_id == user_id,
            RequirementItem.status.in_(['pending_review', 'in_progress'])
        ).all()

        items_as_reviewer = RequirementItem.query.join(
            RequirementDocument
        ).filter(
            RequirementDocument.status == 'reviewing'
        ).all()

        documents_to_review = RequirementDocument.query.filter_by(
            status='reviewing'
        ).all()

        todos = []

        for item in items_as_owner:
            todos.append({
                'type': 'item_assigned',
                'id': item.id,
                'doc_id': item.doc_id,
                'identifier': item.identifier,
                'title': item.title,
                'status': item.status,
                'message': f'您负责的需求 "{item.identifier}" 需要处理'
            })

        for item in items_as_reviewer:
            todos.append({
                'type': 'item_review',
                'id': item.id,
                'doc_id': item.doc_id,
                'identifier': item.identifier,
                'title': item.title,
                'status': item.status,
                'message': f'需求 "{item.identifier}" 等待您的评审意见'
            })

        for doc in documents_to_review:
            todos.append({
                'type': 'document_review',
                'id': doc.id,
                'doc_id': doc.id,
                'title': doc.name,
                'status': doc.status,
                'message': f'需求文档 "{doc.name}" 等待您的评审'
            })

        return jsonify({
            'success': True,
            'todos': todos,
            'total': len(todos)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 需求变更影响分析 API ====================

@requirements_bp.route('/requirement-items/<int:item_id>/impact-analysis', methods=['GET'])
@jwt_required()
def analyze_requirement_impact(item_id):
    """分析需求变更影响的工作项"""
    try:
        user_id = get_current_user_id()
        item = RequirementItem.query.get_or_404(item_id)
        document = RequirementDocument.query.get(item.doc_id)

        if not check_project_permission(document.project_id, user_id):
            return jsonify({'error': '无权访问该条目'}), 403

        links = RequirementLink.query.filter_by(requirement_id=item_id).all()

        impacted_items = {
            'tasks': [],
            'bugs': [],
            'test_cases': []
        }

        for link in links:
            if link.target_type == 'task':
                impacted_items['tasks'].append({
                    'id': link.target_id,
                    'link_type': link.link_type
                })
            elif link.target_type == 'bug':
                impacted_items['bugs'].append({
                    'id': link.target_id,
                    'link_type': link.link_type
                })
            elif link.target_type == 'test_case':
                impacted_items['test_cases'].append({
                    'id': link.target_id,
                    'link_type': link.link_type
                })

        return jsonify({
            'success': True,
            'requirement': {
                'id': item.id,
                'identifier': item.identifier,
                'title': item.title,
                'status': item.status
            },
            'impacted_items': impacted_items,
            'total_impacted': len(links)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 覆盖分析 API ====================

@requirements_bp.route('/projects/<int:project_id>/requirement-coverage', methods=['GET'])
@jwt_required()
def get_requirement_coverage(project_id):
    """获取项目的需求覆盖分析"""
    try:
        user_id = get_current_user_id()

        if not check_project_permission(project_id, user_id):
            return jsonify({'error': '无权访问该项目'}), 403

        documents = RequirementDocument.query.filter_by(project_id=project_id).all()

        total_requirements = 0
        covered_requirements = 0
        test_case_coverage = 0
        uncovered_requirements = []

        for doc in documents:
            items = RequirementItem.query.filter_by(doc_id=doc.id).all()

            for item in items:
                total_requirements += 1
                links = RequirementLink.query.filter_by(requirement_id=item.id).all()

                has_test_case = any(link.target_type == 'test_case' for link in links)
                has_task = any(link.target_type == 'task' for link in links)
                has_bug = any(link.target_type == 'bug' for link in links)

                if has_test_case and has_task:
                    covered_requirements += 1
                    test_case_coverage += 1
                elif has_task or has_bug:
                    covered_requirements += 1
                else:
                    uncovered_requirements.append({
                        'id': item.id,
                        'identifier': item.identifier,
                        'title': item.title,
                        'doc_name': doc.name
                    })

        coverage_rate = (covered_requirements / total_requirements * 100) if total_requirements > 0 else 0
        test_coverage_rate = (test_case_coverage / total_requirements * 100) if total_requirements > 0 else 0

        return jsonify({
            'success': True,
            'statistics': {
                'total_requirements': total_requirements,
                'covered_requirements': covered_requirements,
                'uncovered_requirements': len(uncovered_requirements),
                'coverage_rate': round(coverage_rate, 2),
                'test_case_coverage_rate': round(test_coverage_rate, 2)
            },
            'uncovered_list': uncovered_requirements[:10]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
