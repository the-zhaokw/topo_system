import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/services/api'
import { useUserStore } from './user'

export const useUserStatusStore = defineStore('userStatus', () => {
  // 状态
  const status = ref(localStorage.getItem('userStatus') || 'online')
  const syncing = ref(false)
  const heartbeatInterval = ref(null)
  const lastActivity = ref(Date.now())

  // 状态选项
  const statusOptions = [
    { value: 'online', label: '在线' },
    { value: 'busy', label: '忙碌' },
    { value: 'away', label: '离开' },
    { value: 'offline', label: '离线' }
  ]

  // 状态文字
  const statusText = computed(() => {
    const statusMap = {
      online: '在线',
      busy: '忙碌',
      away: '离开',
      offline: '离线'
    }
    return statusMap[status.value] || '在线'
  })

  // 设置状态（本地 + 同步到后端）
  const setStatus = async (newStatus) => {
    const oldStatus = status.value
    status.value = newStatus
    localStorage.setItem('userStatus', newStatus)

    // 同步到后端
    const userStore = useUserStore()
    if (userStore.currentUser?.id) {
      syncing.value = true
      try {
        await apiService.users.updateStatus(userStore.currentUser.id, { status: newStatus })
      } catch (error) {
        console.error('同步状态到后端失败:', error)
      } finally {
        syncing.value = false
      }
    }
  }

  // 更新用户活动（心跳）
  const updateActivity = async () => {
    const userStore = useUserStore()
    if (!userStore.currentUser?.id) return

    // 如果用户设置的状态是离线，不更新活动
    if (status.value === 'offline') return

    try {
      await apiService.users.updateActivity(userStore.currentUser.id)
      lastActivity.value = Date.now()
    } catch (error) {
      console.error('更新用户活动失败:', error)
    }
  }

  // 启动心跳
  const startHeartbeat = () => {
    // 每2分钟发送一次心跳
    if (heartbeatInterval.value) {
      clearInterval(heartbeatInterval.value)
    }
    heartbeatInterval.value = setInterval(() => {
      updateActivity()
    }, 2 * 60 * 1000) // 2分钟
  }

  // 停止心跳
  const stopHeartbeat = () => {
    if (heartbeatInterval.value) {
      clearInterval(heartbeatInterval.value)
      heartbeatInterval.value = null
    }
  }

  // 仅从后端获取状态（用于初始化）
  const fetchStatusFromBackend = async () => {
    const userStore = useUserStore()
    if (userStore.currentUser?.id) {
      try {
        const response = await apiService.users.getById(userStore.currentUser.id)
        if (response.status) {
          status.value = response.status
          localStorage.setItem('userStatus', response.status)
        }
        // 如果用户设置的状态不是离线，启动心跳
        if (response.user_set_status !== 'offline') {
          startHeartbeat()
        }
      } catch (error) {
        console.error('从后端获取状态失败:', error)
      }
    }
  }

  // 初始化状态
  const initStatus = () => {
    const storedStatus = localStorage.getItem('userStatus')
    if (storedStatus) {
      status.value = storedStatus
    }
  }

  // 用户活动时更新（鼠标移动、键盘输入等）
  const onUserActivity = () => {
    const now = Date.now()
    // 每30秒最多更新一次
    if (now - lastActivity.value > 30 * 1000) {
      updateActivity()
    }
  }

  return {
    status,
    syncing,
    statusOptions,
    statusText,
    setStatus,
    updateActivity,
    startHeartbeat,
    stopHeartbeat,
    fetchStatusFromBackend,
    initStatus,
    onUserActivity
  }
})
