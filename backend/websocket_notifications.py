"""
WebSocket 实时通知模块
为 TOPO 系统提供实时推送能力
"""
from flask import Blueprint, request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import json
import logging

logger = logging.getLogger(__name__)

ws_bp = Blueprint('websocket', __name__)

socketio = None

def init_socketio(app):
    """初始化 SocketIO"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    @socketio.on('connect')
    def handle_connect():
        """客户端连接"""
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            join_room(f'user_{user_id}')
            join_room('broadcast')
            
            logger.info(f'用户 {user_id} WebSocket 连接成功')
            emit('connected', {'status': 'success', 'user_id': user_id})
            
            from enhanced_app import Notification, db
            unread_count = db.session.query(Notification).filter_by(
                user_id=user_id, is_read=False
            ).count()
            emit('unread_count', {'count': unread_count})
            
        except Exception as e:
            logger.warning(f'WebSocket 连接验证失败: {e}')
            emit('error', {'message': '认证失败'})
            disconnect()

    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开"""
        logger.info('客户端 WebSocket 断开')

    @socketio.on('join_project')
    def handle_join_project(data):
        """加入项目房间"""
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            project_id = data.get('project_id')
            
            if project_id:
                room_name = f'project_{project_id}'
                join_room(room_name)
                logger.info(f'用户 {user_id} 加入项目房间 {room_name}')
                emit('joined', {'room': room_name, 'project_id': project_id})
        except Exception as e:
            logger.error(f'加入项目房间失败: {e}')
            emit('error', {'message': '加入房间失败'})

    @socketio.on('leave_project')
    def handle_leave_project(data):
        """离开项目房间"""
        try:
            project_id = data.get('project_id')
            if project_id:
                room_name = f'project_{project_id}'
                leave_room(room_name)
                emit('left', {'room': room_name, 'project_id': project_id})
        except Exception as e:
            logger.error(f'离开项目房间失败: {e}')

    @socketio.on('ping')
    def handle_ping():
        """心跳检测"""
        emit('pong', {'timestamp': datetime.now().isoformat()})
    
    return socketio

def get_socketio():
    """获取 SocketIO 实例"""
    return socketio

def send_notification_to_user(user_id, notification_data):
    """向指定用户发送实时通知"""
    if socketio:
        room = f'user_{user_id}'
        socketio.emit('notification', notification_data, room=room)
        logger.info(f'向用户 {user_id} 发送通知: {notification_data.get("title")}')

def send_notification_to_project(project_id, notification_data):
    """向项目所有成员发送通知"""
    if socketio:
        room = f'project_{project_id}'
        socketio.emit('notification', notification_data, room=room)
        logger.info(f'向项目 {project_id} 发送通知: {notification_data.get("title")}')

def broadcast_notification(notification_data):
    """广播通知给所有在线用户"""
    if socketio:
        socketio.emit('notification', notification_data, room='broadcast')
        logger.info(f'广播通知: {notification_data.get("title")}')

def update_unread_count(user_id, count):
    """更新用户未读通知数量"""
    if socketio:
        room = f'user_{user_id}'
        socketio.emit('unread_count', {'count': count}, room=room)

def notify_bug_assigned(bug_id, assignee_id, assigner_name):
    """Bug 分配通知"""
    send_notification_to_user(assignee_id, {
        'type': 'bug_assigned',
        'title': 'Bug 分配通知',
        'message': f'{assigner_name} 将 Bug #{bug_id} 分配给您',
        'bug_id': bug_id,
        'link': f'/bugs/{bug_id}',
        'created_at': datetime.now().isoformat()
    })

def notify_bug_status_changed(bug_id, user_ids, old_status, new_status, changer_name):
    """Bug 状态变更通知"""
    for user_id in user_ids:
        send_notification_to_user(user_id, {
            'type': 'bug_status_changed',
            'title': 'Bug 状态变更',
            'message': f'{changer_name} 将 Bug #{bug_id} 状态从 "{old_status}" 改为 "{new_status}"',
            'bug_id': bug_id,
            'old_status': old_status,
            'new_status': new_status,
            'link': f'/bugs/{bug_id}',
            'created_at': datetime.now().isoformat()
        })

def notify_task_assigned(task_id, assignee_id, assigner_name):
    """任务分配通知"""
    send_notification_to_user(assignee_id, {
        'type': 'task_assigned',
        'title': '任务分配通知',
        'message': f'{assigner_name} 将任务 #{task_id} 分配给您',
        'task_id': task_id,
        'link': f'/tasks/{task_id}',
        'created_at': datetime.now().isoformat()
    })

def notify_project_update(project_id, user_ids, message):
    """项目更新通知"""
    for user_id in user_ids:
        send_notification_to_user(user_id, {
            'type': 'project_update',
            'title': '项目更新',
            'message': message,
            'project_id': project_id,
            'link': f'/projects/{project_id}',
            'created_at': datetime.now().isoformat()
        })

def notify_approval_request(user_id, request_type, request_id, requester_name):
    """审批请求通知"""
    type_names = {
        'leave': '请假申请',
        'overtime': '加班申请',
        'contract': '合同审批'
    }
    send_notification_to_user(user_id, {
        'type': 'approval_request',
        'title': f'{type_names.get(request_type, "审批")}待审批',
        'message': f'{requester_name} 提交了{type_names.get(request_type, "申请")}，需要您的审批',
        'request_type': request_type,
        'request_id': request_id,
        'link': f'/approvals/{request_type}/{request_id}',
        'created_at': datetime.now().isoformat()
    })

def notify_system_alert(user_ids, title, message, level='info'):
    """系统告警通知"""
    for user_id in user_ids:
        send_notification_to_user(user_id, {
            'type': 'system_alert',
            'title': title,
            'message': message,
            'level': level,
            'created_at': datetime.now().isoformat()
        })

from datetime import datetime
