/**
 * WebSocket 实时通知服务
 * 为 TOPO 系统提供实时推送能力
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElNotification } from 'element-plus'

class WebSocketService {
  constructor() {
    this.socket = null
    this.reconnectTimer = null
    this.heartbeatTimer = null
    this.isConnected = ref(false)
    this.unreadCount = ref(0)
    this.notifications = ref([])
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
  }

  // 初始化连接
  connect() {
    const userStore = useUserStore()
    const token = localStorage.getItem('token')
    
    if (!token) {
      console.log('未登录，跳过 WebSocket 连接')
      return
    }

    // 构建 WebSocket URL
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = import.meta.env.VITE_WS_HOST || 'localhost:5000'
    const wsUrl = `${wsProtocol}//${wsHost}/socket.io/?EIO=4&transport=websocket`

    try {
      // 使用 Socket.IO 客户端（如果可用）或原生 WebSocket
      if (window.io) {
        this.socket = window.io(wsHost, {
          transports: ['websocket'],
          auth: { token }
        })
      } else {
        // 原生 WebSocket 回退
        this.socket = new WebSocket(wsUrl)
      }

      this.setupEventHandlers()
    } catch (error) {
      console.error('WebSocket 连接失败:', error)
      this.scheduleReconnect()
    }
  }

  // 设置事件处理器
  setupEventHandlers() {
    if (!this.socket) return

    // 连接成功
    this.socket.on('connect', () => {
      console.log('WebSocket 连接成功')
      this.isConnected.value = true
      this.reconnectAttempts = 0
      this.startHeartbeat()
    })

    // 断开连接
    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket 断开:', reason)
      this.isConnected.value = false
      this.stopHeartbeat()
      if (reason !== 'io client disconnect') {
        this.scheduleReconnect()
      }
    })

    // 连接错误
    this.socket.on('connect_error', (error) => {
      console.error('WebSocket 连接错误:', error)
      this.scheduleReconnect()
    })

    // 收到通知
    this.socket.on('notification', (data) => {
      this.handleNotification(data)
    })

    // 未读数量更新
    this.socket.on('unread_count', (data) => {
      this.unreadCount.value = data.count
    })

    // 连接确认
    this.socket.on('connected', (data) => {
      console.log('服务器确认连接:', data)
    })

    // 心跳响应
    this.socket.on('pong', () => {
      // 心跳正常
    })

    // 错误消息
    this.socket.on('error', (data) => {
      console.error('WebSocket 错误:', data.message)
    })
  }

  // 处理收到的通知
  handleNotification(data) {
    // 添加到通知列表
    this.notifications.value.unshift({
      ...data,
      id: Date.now(),
      isRead: false
    })

    // 未读数 +1
    this.unreadCount.value++

    // 显示桌面通知
    this.showDesktopNotification(data)

    // 显示 Element Plus 通知
    ElNotification({
      title: data.title,
      message: data.message,
      type: this.getNotificationType(data.type),
      duration: 5000,
      onClick: () => {
        // 点击通知跳转
        if (data.link) {
          window.location.href = data.link
        }
      }
    })
  }

  // 显示浏览器桌面通知
  showDesktopNotification(data) {
    if (!('Notification' in window)) return
    if (Notification.permission !== 'granted') return

    const notification = new Notification(data.title, {
      body: data.message,
      icon: '/favicon.ico',
      tag: data.type,
      requireInteraction: false
    })

    notification.onclick = () => {
      window.focus()
      if (data.link) {
        window.location.href = data.link
      }
      notification.close()
    }
  }

  // 获取通知类型
  getNotificationType(type) {
    const typeMap = {
      'bug_assigned': 'warning',
      'bug_status_changed': 'info',
      'task_assigned': 'success',
      'project_update': 'info',
      'approval_request': 'warning',
      'system_alert': 'error'
    }
    return typeMap[type] || 'info'
  }

  // 请求桌面通知权限
  requestNotificationPermission() {
    if (!('Notification' in window)) return
    if (Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }

  // 心跳检测
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.socket && this.isConnected.value) {
        this.socket.emit('ping')
      }
    }, 30000) // 30秒一次
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  // 重连机制
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('达到最大重连次数，停止重连')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * this.reconnectAttempts

    console.log(`计划 ${delay}ms 后第 ${this.reconnectAttempts} 次重连`)

    this.reconnectTimer = setTimeout(() => {
      this.connect()
    }, delay)
  }

  // 断开连接
  disconnect() {
    this.stopHeartbeat()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.isConnected.value = false
  }

  // 加入项目房间
  joinProject(projectId) {
    if (this.socket && this.isConnected.value) {
      this.socket.emit('join_project', { project_id: projectId })
    }
  }

  // 离开项目房间
  leaveProject(projectId) {
    if (this.socket && this.isConnected.value) {
      this.socket.emit('leave_project', { project_id: projectId })
    }
  }

  // 标记通知已读
  markAsRead(notificationId) {
    const index = this.notifications.value.findIndex(n => n.id === notificationId)
    if (index !== -1 && !this.notifications.value[index].isRead) {
      this.notifications.value[index].isRead = true
      this.unreadCount.value = Math.max(0, this.unreadCount.value - 1)
    }
  }

  // 标记全部已读
  markAllAsRead() {
    this.notifications.value.forEach(n => n.isRead = true)
    this.unreadCount.value = 0
  }
}

// 单例实例
const wsService = new WebSocketService()

// Vue 组合式函数
export function useWebSocket() {
  onMounted(() => {
    wsService.connect()
    wsService.requestNotificationPermission()
  })

  onUnmounted(() => {
    wsService.disconnect()
  })

  return {
    isConnected: wsService.isConnected,
    unreadCount: wsService.unreadCount,
    notifications: wsService.notifications,
    joinProject: wsService.joinProject.bind(wsService),
    leaveProject: wsService.leaveProject.bind(wsService),
    markAsRead: wsService.markAsRead.bind(wsService),
    markAllAsRead: wsService.markAllAsRead.bind(wsService)
  }
}

export default wsService
