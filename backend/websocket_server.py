"""
WebSocket服务器 - 实时协作系统
支持在线状态、协作房间、编辑锁等功能
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set
import websockets
from websockets.server import WebSocketServerProtocol

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局状态
class CollaborationState:
    def __init__(self):
        # 在线用户: {user_id: {ws, username, status, last_seen}}
        self.online_users: Dict[str, Dict] = {}
        # 协作房间: {room_id: {name, type, participants: Set[user_id], locks: {}}}
        self.rooms: Dict[str, Dict] = {}
        # WebSocket连接: {ws: user_id}
        self.connections: Dict[WebSocketServerProtocol, str] = {}
        
    def add_user(self, ws: WebSocketServerProtocol, user_id: str, username: str):
        """添加在线用户"""
        self.online_users[user_id] = {
            'ws': ws,
            'username': username,
            'status': 'online',
            'last_seen': datetime.now().isoformat()
        }
        self.connections[ws] = user_id
        logger.info(f"用户上线: {username} ({user_id})")
        
    def remove_user(self, ws: WebSocketServerProtocol):
        """移除在线用户"""
        user_id = self.connections.get(ws)
        if user_id:
            user_info = self.online_users.pop(user_id, None)
            self.connections.pop(ws, None)
            
            # 从所有房间移除
            for room_id, room in self.rooms.items():
                if user_id in room['participants']:
                    room['participants'].discard(user_id)
                    # 释放该用户的所有锁
                    locks_to_remove = [
                        lock_id for lock_id, lock in room['locks'].items()
                        if lock['user_id'] == user_id
                    ]
                    for lock_id in locks_to_remove:
                        room['locks'].pop(lock_id, None)
                        
            if user_info:
                logger.info(f"用户离线: {user_info['username']} ({user_id})")
                
    def update_status(self, user_id: str, status: str):
        """更新用户状态"""
        if user_id in self.online_users:
            self.online_users[user_id]['status'] = status
            self.online_users[user_id]['last_seen'] = datetime.now().isoformat()
            
    def create_room(self, room_id: str, name: str, room_type: str = 'general') -> Dict:
        """创建协作房间"""
        if room_id not in self.rooms:
            self.rooms[room_id] = {
                'id': room_id,
                'name': name,
                'type': room_type,
                'participants': set(),
                'locks': {},
                'created_at': datetime.now().isoformat()
            }
            logger.info(f"创建房间: {name} ({room_id})")
        return self.rooms[room_id]
        
    def join_room(self, room_id: str, user_id: str) -> bool:
        """用户加入房间"""
        if room_id in self.rooms and user_id in self.online_users:
            self.rooms[room_id]['participants'].add(user_id)
            logger.info(f"用户 {user_id} 加入房间 {room_id}")
            return True
        return False
        
    def leave_room(self, room_id: str, user_id: str) -> bool:
        """用户离开房间"""
        if room_id in self.rooms:
            self.rooms[room_id]['participants'].discard(user_id)
            # 释放该用户的锁
            locks_to_remove = [
                lock_id for lock_id, lock in self.rooms[room_id]['locks'].items()
                if lock['user_id'] == user_id
            ]
            for lock_id in locks_to_remove:
                self.rooms[room_id]['locks'].pop(lock_id, None)
            logger.info(f"用户 {user_id} 离开房间 {room_id}")
            return True
        return False
        
    def acquire_lock(self, room_id: str, lock_id: str, user_id: str, 
                     resource_type: str, resource_id: str) -> bool:
        """获取编辑锁"""
        if room_id not in self.rooms:
            return False
            
        room = self.rooms[room_id]
        
        # 检查是否已被锁定
        for lock in room['locks'].values():
            if lock['resource_type'] == resource_type and lock['resource_id'] == resource_id:
                if lock['user_id'] != user_id:
                    return False
                    
        # 获取锁
        room['locks'][lock_id] = {
            'id': lock_id,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'acquired_at': datetime.now().isoformat()
        }
        logger.info(f"用户 {user_id} 获取锁 {lock_id}")
        return True
        
    def release_lock(self, room_id: str, lock_id: str, user_id: str) -> bool:
        """释放编辑锁"""
        if room_id not in self.rooms:
            return False
            
        room = self.rooms[room_id]
        lock = room['locks'].get(lock_id)
        
        if lock and lock['user_id'] == user_id:
            room['locks'].pop(lock_id, None)
            logger.info(f"用户 {user_id} 释放锁 {lock_id}")
            return True
        return False
        
    def get_room_info(self, room_id: str) -> Dict:
        """获取房间信息"""
        if room_id not in self.rooms:
            return None
            
        room = self.rooms[room_id].copy()
        room['participants'] = [
            {
                'user_id': uid,
                'username': self.online_users.get(uid, {}).get('username', 'Unknown'),
                'status': self.online_users.get(uid, {}).get('status', 'offline')
            }
            for uid in room['participants']
        ]
        room['locks'] = list(room['locks'].values())
        return room
        
    def get_online_users(self) -> list:
        """获取在线用户列表"""
        return [
            {
                'user_id': uid,
                'username': info['username'],
                'status': info['status'],
                'last_seen': info['last_seen']
            }
            for uid, info in self.online_users.items()
        ]

# 全局状态实例
state = CollaborationState()

async def broadcast(message: dict, exclude_ws: WebSocketServerProtocol = None):
    """广播消息给所有连接"""
    message_str = json.dumps(message)
    for ws in list(state.connections.keys()):
        if ws != exclude_ws and ws.open:
            try:
                await ws.send(message_str)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                
async def broadcast_to_room(room_id: str, message: dict, exclude_user_id: str = None):
    """广播消息给房间内的所有用户"""
    if room_id not in state.rooms:
        return
        
    room = state.rooms[room_id]
    message_str = json.dumps(message)
    
    for user_id in room['participants']:
        if user_id == exclude_user_id:
            continue
        user_info = state.online_users.get(user_id)
        if user_info and user_info['ws'].open:
            try:
                await user_info['ws'].send(message_str)
            except Exception as e:
                logger.error(f"房间广播失败: {e}")

async def handle_message(ws: WebSocketServerProtocol, message: str):
    """处理客户端消息"""
    try:
        data = json.loads(message)
        msg_type = data.get('type')
        user_id = state.connections.get(ws)
        
        if not user_id:
            await ws.send(json.dumps({
                'type': 'error',
                'message': '未认证的用户'
            }))
            return
            
        # 心跳
        if msg_type == 'ping':
            await ws.send(json.dumps({'type': 'pong', 'timestamp': datetime.now().isoformat()}))
            return
            
        # 更新状态
        if msg_type == 'status_update':
            status = data.get('status', 'online')
            state.update_status(user_id, status)
            await broadcast({
                'type': 'user_status_changed',
                'user_id': user_id,
                'status': status
            })
            return
            
        # 创建房间
        if msg_type == 'create_room':
            room_id = data.get('room_id')
            name = data.get('name')
            room_type = data.get('room_type', 'general')
            
            if not room_id or not name:
                await ws.send(json.dumps({
                    'type': 'error',
                    'message': '房间ID和名称不能为空'
                }))
                return
                
            room = state.create_room(room_id, name, room_type)
            state.join_room(room_id, user_id)
            
            await ws.send(json.dumps({
                'type': 'room_created',
                'room': state.get_room_info(room_id)
            }))
            return
            
        # 加入房间
        if msg_type == 'join_room':
            room_id = data.get('room_id')
            
            if state.join_room(room_id, user_id):
                room_info = state.get_room_info(room_id)
                
                # 通知自己
                await ws.send(json.dumps({
                    'type': 'room_joined',
                    'room': room_info
                }))
                
                # 通知房间内其他人
                await broadcast_to_room(room_id, {
                    'type': 'user_joined_room',
                    'room_id': room_id,
                    'user': {
                        'user_id': user_id,
                        'username': state.online_users.get(user_id, {}).get('username', 'Unknown')
                    }
                }, exclude_user_id=user_id)
            else:
                await ws.send(json.dumps({
                    'type': 'error',
                    'message': '加入房间失败'
                }))
            return
            
        # 离开房间
        if msg_type == 'leave_room':
            room_id = data.get('room_id')
            
            if state.leave_room(room_id, user_id):
                await broadcast_to_room(room_id, {
                    'type': 'user_left_room',
                    'room_id': room_id,
                    'user_id': user_id
                })
                
                await ws.send(json.dumps({
                    'type': 'room_left',
                    'room_id': room_id
                }))
            return
            
        # 获取锁
        if msg_type == 'acquire_lock':
            room_id = data.get('room_id')
            lock_id = data.get('lock_id')
            resource_type = data.get('resource_type')
            resource_id = data.get('resource_id')
            
            if state.acquire_lock(room_id, lock_id, user_id, resource_type, resource_id):
                await broadcast_to_room(room_id, {
                    'type': 'lock_acquired',
                    'room_id': room_id,
                    'lock': {
                        'id': lock_id,
                        'user_id': user_id,
                        'resource_type': resource_type,
                        'resource_id': resource_id
                    }
                })
                
                await ws.send(json.dumps({
                    'type': 'lock_acquired_confirm',
                    'lock_id': lock_id
                }))
            else:
                await ws.send(json.dumps({
                    'type': 'lock_failed',
                    'message': '资源已被锁定'
                }))
            return
            
        # 释放锁
        if msg_type == 'release_lock':
            room_id = data.get('room_id')
            lock_id = data.get('lock_id')
            
            if state.release_lock(room_id, lock_id, user_id):
                await broadcast_to_room(room_id, {
                    'type': 'lock_released',
                    'room_id': room_id,
                    'lock_id': lock_id
                })
            return
            
        # 发送协作消息
        if msg_type == 'collaboration_message':
            room_id = data.get('room_id')
            content = data.get('content')
            
            await broadcast_to_room(room_id, {
                'type': 'collaboration_message',
                'room_id': room_id,
                'user_id': user_id,
                'username': state.online_users.get(user_id, {}).get('username', 'Unknown'),
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
            return
            
        # 编辑操作
        if msg_type == 'edit_operation':
            room_id = data.get('room_id')
            operation = data.get('operation')  # insert, delete, update
            target = data.get('target')
            changes = data.get('changes')
            
            await broadcast_to_room(room_id, {
                'type': 'edit_operation',
                'room_id': room_id,
                'user_id': user_id,
                'username': state.online_users.get(user_id, {}).get('username', 'Unknown'),
                'operation': operation,
                'target': target,
                'changes': changes,
                'timestamp': datetime.now().isoformat()
            })
            return
            
        # 获取在线用户
        if msg_type == 'get_online_users':
            await ws.send(json.dumps({
                'type': 'online_users',
                'users': state.get_online_users()
            }))
            return
            
        # 获取房间信息
        if msg_type == 'get_room_info':
            room_id = data.get('room_id')
            room_info = state.get_room_info(room_id)
            
            await ws.send(json.dumps({
                'type': 'room_info',
                'room': room_info
            }))
            return
            
    except json.JSONDecodeError:
        await ws.send(json.dumps({
            'type': 'error',
            'message': '无效的JSON格式'
        }))
    except Exception as e:
        logger.error(f"处理消息失败: {e}")
        await ws.send(json.dumps({
            'type': 'error',
            'message': str(e)
        }))

async def handle_connection(ws: WebSocketServerProtocol, path: str):
    """处理WebSocket连接"""
    logger.info(f"新连接: {ws.remote_address}")
    
    try:
        # 等待认证消息
        auth_message = await asyncio.wait_for(ws.recv(), timeout=10)
        auth_data = json.loads(auth_message)
        
        if auth_data.get('type') != 'auth':
            await ws.send(json.dumps({
                'type': 'error',
                'message': '首先需要认证'
            }))
            return
            
        user_id = auth_data.get('user_id')
        username = auth_data.get('username')
        
        if not user_id or not username:
            await ws.send(json.dumps({
                'type': 'error',
                'message': 'user_id和username不能为空'
            }))
            return
            
        # 添加用户
        state.add_user(ws, user_id, username)
        
        # 发送认证成功消息
        await ws.send(json.dumps({
            'type': 'auth_success',
            'user_id': user_id,
            'online_users': state.get_online_users()
        }))
        
        # 广播用户上线
        await broadcast({
            'type': 'user_online',
            'user': {
                'user_id': user_id,
                'username': username,
                'status': 'online'
            }
        }, exclude_ws=ws)
        
        # 处理消息
        async for message in ws:
            await handle_message(ws, message)
            
    except asyncio.TimeoutError:
        logger.warning(f"连接超时: {ws.remote_address}")
        await ws.send(json.dumps({
            'type': 'error',
            'message': '认证超时'
        }))
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"连接关闭: {ws.remote_address}")
    except Exception as e:
        logger.error(f"连接处理错误: {e}")
    finally:
        # 清理
        user_id = state.connections.get(ws)
        if user_id:
            user_info = state.online_users.get(user_id, {})
            state.remove_user(ws)
            
            # 广播用户离线
            await broadcast({
                'type': 'user_offline',
                'user_id': user_id,
                'username': user_info.get('username', 'Unknown')
            })

async def start_server(host: str = '0.0.0.0', port: int = 8765):
    """启动WebSocket服务器"""
    logger.info(f"启动WebSocket服务器: ws://{host}:{port}")
    
    async with websockets.serve(handle_connection, host, port):
        logger.info(f"WebSocket服务器已启动: ws://{host}:{port}")
        await asyncio.Future()  # 永久运行

if __name__ == '__main__':
    asyncio.run(start_server())
