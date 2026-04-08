"""
通知API - @提及与系统通知功能
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity

# 创建通知蓝图
notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

def get_db():
    from enhanced_app import get_db_instance
    return get_db_instance()

def get_models():
    from enhanced_app import User, Notification, Bug, Comment, create_notification, send_mention_notifications
    return User, Notification, Bug, Comment, create_notification, send_mention_notifications

# 获取通知列表
@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """获取当前用户的通知列表"""
    User, Notification, Bug, Comment, create_notification, send_mention_notifications = get_models()
    db = get_db()
    
    current_user_id = get_jwt_identity()
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_read = request.args.get('is_read')  # true/false
    notification_type = request.args.get('type')
    
    # 构建查询
    query = Notification.query.filter_by(user_id=current_user_id)
    
    # 已读/未读筛选
    if is_read is not None:
        if is_read.lower() == 'true':
            query = query.filter(Notification.is_read == True)
        elif is_read.lower() == 'false':
            query = query.filter(Notification.is_read == False)
    
    # 类型筛选
    if notification_type:
        query = query.filter(Notification.type == notification_type)
    
    # 按创建时间倒序排序
    query = query.order_by(Notification.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    notifications = pagination.items
    
    # 转换为字典
    result = []
    for notification in notifications:
        notification_dict = notification.to_dict()
        
        # 添加关联信息
        if notification.related_bug_id:
            bug = Bug.query.get(notification.related_bug_id)
            if bug:
                notification_dict['bug_title'] = bug.title
                notification_dict['bug_status'] = bug.status.value if hasattr(bug.status, 'value') else str(bug.status)
        
        if notification.related_comment_id:
            comment = Comment.query.get(notification.related_comment_id)
            if comment:
                notification_dict['comment_content_preview'] = comment.content[:100] + '...' if len(comment.content) > 100 else comment.content
        
        # 添加用户信息
        user = User.query.get(notification.user_id)
        if user:
            notification_dict['username'] = user.username
        
        result.append(notification_dict)
    
    return jsonify({
        'notifications': result,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })

# 获取未读通知数量
@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """获取当前用户的未读通知数量"""
    User, Notification, Bug, Comment, create_notification, send_mention_notifications = get_models()
    db = get_db()
    
    current_user_id = get_jwt_identity()
    
    # 统计未读通知数量
    unread_count = Notification.query.filter_by(
        user_id=current_user_id,
        is_read=False
    ).count()
    
    return jsonify({
        'unread_count': unread_count
    })

# 标记通知为已读
@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    """标记通知为已读"""
    User, Notification, Bug, Comment, create_notification, send_mention_notifications = get_models()
    db = get_db()
    
    current_user_id = get_jwt_identity()
    
    # 获取通知
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user_id
    ).first()
    
    if not notification:
        return jsonify({'error': '通知不存在或无权访问'}), 404
    
    # 标记为已读
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': '通知已标记为已读',
        'notification': notification.to_dict()
    })

# 标记所有通知为已读
@notifications_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    """标记当前用户的所有通知为已读"""
    User, Notification, Bug, Comment, create_notification, send_mention_notifications = get_models()
    db = get_db()
    
    current_user_id = get_jwt_identity()
    
    # 获取所有未读通知
    unread_notifications = Notification.query.filter_by(
        user_id=current_user_id,
        is_read=False
    ).all()
    
    # 批量标记为已读
    for notification in unread_notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'已标记 {len(unread_notifications)} 条通知为已读',
        'marked_count': len(unread_notifications)
    })

# 删除通知
@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """删除通知"""
    User, Notification, Bug, Comment, create_notification, send_mention_notifications = get_models()
    db = get_db()
    
    current_user_id = get_jwt_identity()
    
    # 获取通知
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user_id
    ).first()
    
    if not notification:
        return jsonify({'error': '通知不存在或无权访问'}), 404
    
    # 删除通知
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({
        'message': '通知已删除'
    })

# 发送测试通知
@notifications_bp.route('/test', methods=['POST'])
@jwt_required()
def send_test_notification():
    """发送测试通知（仅用于调试）"""
    User, Notification, Bug, Comment, create_notification, send_mention_notifications = get_models()
    db = get_db()
    
    current_user_id = get_jwt_identity()
    
    # 获取当前用户
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 创建测试通知
    notification = create_notification(
        user_id=current_user_id,
        notification_type='system',
        title='测试通知',
        content=f'这是一条测试通知，发送给用户 {current_user.username}。系统时间：{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}',
        related_bug_id=None,
        related_comment_id=None
    )
    
    if notification:
        return jsonify({
            'message': '测试通知已发送',
            'notification': notification.to_dict()
        })
    else:
        return jsonify({'error': '发送测试通知失败'}), 500

# 获取通知类型统计
@notifications_bp.route('/type-stats', methods=['GET'])
@jwt_required()
def get_notification_type_stats():
    """获取通知类型统计"""
    User, Notification, Bug, Comment, create_notification, send_mention_notifications = get_models()
    db = get_db()

    current_user_id = get_jwt_identity()

    from sqlalchemy import func
    stats = db.session.query(
        Notification.type,
        func.count(Notification.id).label('count')
    ).filter(
        Notification.user_id == current_user_id
    ).group_by(
        Notification.type
    ).all()

    result = {stat.type: stat.count for stat in stats}

    return jsonify(result)

@notifications_bp.route('/email/config', methods=['GET'])
@jwt_required()
def get_email_config():
    """获取邮件配置状态"""
    from enhanced_app import EMAIL_CONFIG, email_service
    config = {
        'enabled': EMAIL_CONFIG.get('EMAIL_ENABLED', False),
        'host': EMAIL_CONFIG.get('SMTP_SERVER', ''),
        'port': EMAIL_CONFIG.get('SMTP_PORT', 465),
        'username': EMAIL_CONFIG.get('SMTP_USERNAME', ''),
        'from_address': EMAIL_CONFIG.get('FROM_EMAIL', ''),
        'is_configured': email_service.is_configured() if hasattr(email_service, 'is_configured') else bool(EMAIL_CONFIG.get('SMTP_USERNAME'))
    }
    config['password_masked'] = '********' if EMAIL_CONFIG.get('SMTP_PASSWORD') else ''
    return jsonify(config)

@notifications_bp.route('/email/send-test', methods=['POST'])
@jwt_required()
def send_test_email():
    """发送测试邮件"""
    from enhanced_app import email_service

    data = request.get_json()
    to_address = data.get('to_address')

    if not to_address:
        return jsonify({'error': '请提供收件人邮箱地址'}), 400

    result = email_service.send_test_email(to_address)
    return jsonify(result)

@notifications_bp.route('/email/send', methods=['POST'])
@jwt_required()
def send_email():
    """发送邮件"""
    from enhanced_app import email_service

    data = request.get_json()
    to_address = data.get('to_address')
    subject = data.get('subject', 'TOPO系统通知')
    body = data.get('body', '')
    html_body = data.get('html_body')

    if not to_address:
        return jsonify({'error': '请提供收件人邮箱地址'}), 400

    if not body:
        return jsonify({'error': '邮件内容不能为空'}), 400

    result = email_service.send_email(to_address, subject, body, html_body)
    return jsonify(result)

@notifications_bp.route('/email/bug-notification', methods=['POST'])
@jwt_required()
def send_bug_notification_email():
    """发送Bug通知邮件"""
    from enhanced_app import email_service

    data = request.get_json()
    to_address = data.get('to_address')
    bug_title = data.get('bug_title', 'Bug通知')
    assignee_name = data.get('assignee_name', 'Unknown')

    if not to_address:
        return jsonify({'error': '请提供收件人邮箱地址'}), 400

    result = email_service.send_bug_assigned_email(to_address, bug_title, assignee_name)
    return jsonify(result)