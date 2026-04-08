<template>
  <div id="app">
    <!-- 加载状态 -->
    <div v-if="isInitializing" class="loading-container">
      <div class="loading-spinner">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>系统初始化中...</span>
      </div>
    </div>

    <!-- 登录页面 -->
    <router-view v-if="!isInitializing && isRouteReady && $route.path === '/login'" />

    <!-- 移动端菜单 -->
    <MobileMenu
      v-if="!isInitializing && isRouteReady && $route.path !== '/login'"
      :is-mobile="isMobile"
      :is-menu-open="isMenuOpen"
      @close="closeMenu"
    />

    <!-- 桌面端布局 -->
    <el-container v-if="!isInitializing && isRouteReady && $route.path !== '/login'" class="app-container" :class="{ 'mobile-layout': isMobile }">
      <!-- 侧边栏导航（仅桌面端显示） -->
      <el-aside v-if="!isMobile" width="250px" class="sidebar">
        <div class="logo">
          <el-icon><Warning /></el-icon>
          <span>TOPO系统</span>
        </div>
        
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>个人工作台</span>
        </el-menu-item>

        <el-sub-menu index="projects">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>项目管理</span>
          </template>
          <el-menu-item index="/projects/list">
            <el-icon><List /></el-icon>
            <span>项目列表</span>
          </el-menu-item>
          <el-menu-item index="/projects/statistics">
            <el-icon><DataAnalysis /></el-icon>
            <span>项目统计</span>
          </el-menu-item>
          <el-menu-item index="/projects/custom-report">
            <el-icon><PieChart /></el-icon>
            <span>自定义报表</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="bugs">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>缺陷管理</span>
          </template>
          <el-menu-item index="/bugs/list">
            <el-icon><List /></el-icon>
            <span>缺陷列表</span>
          </el-menu-item>
          <el-menu-item index="/bugs/statistics">
            <el-icon><DataAnalysis /></el-icon>
            <span>Bug 统计</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="attendance">
          <template #title>
            <el-icon><Clock /></el-icon>
            <span>考勤管理系统</span>
          </template>
          <el-menu-item index="/attendance/records">
            <el-icon><List /></el-icon>
            <span>考勤记录</span>
          </el-menu-item>
          <el-menu-item index="/attendance/leave-application">
            <el-icon><DocumentAdd /></el-icon>
            <span>请假申请</span>
          </el-menu-item>
          <el-menu-item index="/attendance/overtime-application">
            <el-icon><Clock /></el-icon>
            <span>加班申请</span>
          </el-menu-item>
          <el-menu-item v-if="currentUser && hasAttendanceManagePermission" index="/attendance/leave-approval">
            <el-icon><Checked /></el-icon>
            <span>请假审批</span>
          </el-menu-item>
          <el-menu-item v-if="currentUser && hasAttendanceManagePermission" index="/attendance/overtime-approval">
            <el-icon><Clock /></el-icon>
            <span>加班审批</span>
          </el-menu-item>
          <el-menu-item v-if="currentUser && hasAttendanceManagePermission" index="/attendance/shifts">
            <el-icon><Calendar /></el-icon>
            <span>排班管理</span>
          </el-menu-item>
          <el-menu-item index="/attendance/reports">
            <el-icon><DataAnalysis /></el-icon>
            <span>统计报表</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="materials" v-if="currentUser && hasMaterialManagePermission">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>物料管理系统</span>
          </template>
          <el-menu-item index="/materials/categories">
            <el-icon><Collection /></el-icon>
            <span>物料分类</span>
          </el-menu-item>
          <el-menu-item index="/materials/list">
            <el-icon><Goods /></el-icon>
            <span>物料管理</span>
          </el-menu-item>
          <el-menu-item index="/materials/warehouses">
            <el-icon><OfficeBuilding /></el-icon>
            <span>仓库管理</span>
          </el-menu-item>
          <el-menu-item index="/materials/inventory">
            <el-icon><TrendCharts /></el-icon>
            <span>库存管理</span>
          </el-menu-item>
          <el-menu-item index="/materials/locations">
            <el-icon><MapLocation /></el-icon>
            <span>库位管理</span>
          </el-menu-item>
          <el-menu-item index="/materials/serial-numbers">
            <el-icon><Ticket /></el-icon>
            <span>序列号管理</span>
          </el-menu-item>
          <el-menu-item index="/materials/relationships">
            <el-icon><Link /></el-icon>
            <span>物料关系</span>
          </el-menu-item>
          <el-menu-item index="/materials/reports">
            <el-icon><PieChart /></el-icon>
            <span>物料报表</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="contracts" v-if="currentUser && hasContractManagePermission">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>合同管理系统</span>
          </template>
          <el-menu-item index="/contracts/list">
            <el-icon><List /></el-icon>
            <span>合同列表</span>
          </el-menu-item>
          <el-menu-item index="/contracts/statistics">
            <el-icon><DataAnalysis /></el-icon>
            <span>统计报表</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item v-if="currentUser && isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        
        <el-menu-item v-if="currentUser && isAdmin" index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
        
        <el-menu-item index="/activities">
          <el-icon><Clock /></el-icon>
          <span>活动记录</span>
        </el-menu-item>

        <el-menu-item index="/knowledge">
          <el-icon><Reading /></el-icon>
          <span>知识库</span>
        </el-menu-item>

        <el-menu-item index="/monitoring">
          <el-icon><Monitor /></el-icon>
          <span>系统监控</span>
        </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区域 -->
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <!-- 移动端汉堡菜单按钮 -->
            <el-button v-if="isMobile" class="menu-btn" @click="toggleMenu">
              <el-icon size="24"><Fold /></el-icon>
            </el-button>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentRouteName }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          
          <div class="header-right">
            <!-- 通知图标 -->
            <el-dropdown @command="handleNotificationCommand" class="notification-dropdown">
              <div class="notification-icon">
                <el-badge :value="unreadCount" :max="99" :hidden="unreadCount === 0" class="notification-badge">
                  <el-icon size="20"><Bell /></el-icon>
                </el-badge>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="notification-menu">
                  <div class="notification-header">
                    <span>通知</span>
                    <el-button v-if="unreadCount > 0" type="text" size="small" @click="markAllAsRead">全部标记为已读</el-button>
                  </div>
                  <div class="notification-list" v-if="notifications.length > 0">
                    <div v-for="notification in notifications.slice(0, 5)" :key="notification.id" 
                         class="notification-item" :class="{ 'unread': !notification.is_read }"
                         @click="viewNotification(notification)">
                      <div class="notification-title">{{ notification.title }}</div>
                      <div class="notification-content">{{ notification.content }}</div>
                      <div class="notification-time">{{ formatNotificationTime(notification.created_at) }}</div>
                    </div>
                  </div>
                  <div v-else class="notification-empty">
                    暂无通知
                  </div>
                  <el-dropdown-item divided command="viewAll">
                    <el-icon><List /></el-icon>
                    查看所有通知
                  </el-dropdown-item>
                  <el-dropdown-item command="markAllRead" v-if="unreadCount > 0">
                    <el-icon><Check /></el-icon>
                    标记全部为已读
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <el-dropdown popper-class="user-dropdown-menu" :show-timeout="0" :hide-timeout="200">
              <span class="user-info">
                <div class="user-avatar-wrapper">
                  <el-avatar :size="32" :src="userAvatar" />
                  <span class="status-indicator" :class="userStatusStore.status"></span>
                </div>
                <span class="username">{{ currentUser?.username || '用户' }}</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <div class="user-dropdown-content">
                  <!-- 用户信息头部 -->
                  <div class="user-dropdown-header">
                    <div class="user-dropdown-avatar">
                      <el-avatar :size="48" :src="userAvatar" />
                      <span class="status-indicator-large" :class="userStatusStore.status"></span>
                    </div>
                    <div class="user-dropdown-info">
                      <div class="user-dropdown-name">{{ currentUser?.username || '用户' }}</div>
                      <div class="user-dropdown-username">@{{ currentUser?.username || 'user' }}</div>
                      <div class="user-dropdown-status-text">
                        <span class="status-dot" :class="userStatusStore.status"></span>
                        {{ userStatusStore.statusText }}
                      </div>
                    </div>
                  </div>

                  <!-- 状态设置 -->
                  <div class="user-dropdown-section">
                    <div class="section-title">编辑状态</div>
                    <div class="status-options">
                      <div
                        v-for="status in userStatusStore.statusOptions"
                        :key="status.value"
                        class="status-option"
                        :class="{ active: userStatusStore.status === status.value }"
                        @click="userStatusStore.setStatus(status.value)"
                      >
                        <span class="status-dot" :class="status.value"></span>
                        <span>{{ status.label }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 菜单项 -->
                  <div class="user-dropdown-section">
                    <div class="dropdown-menu-item" @click="handleProfile">
                      <el-icon><User /></el-icon>
                      <span>编辑个人资料</span>
                    </div>
                  </div>

                  <!-- 退出登录 -->
                  <div class="user-dropdown-footer">
                    <div class="dropdown-menu-item logout" @click="handleLogout">
                      <el-icon><SwitchButton /></el-icon>
                      <span>退出</span>
                    </div>
                  </div>
                </div>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useUserStatusStore } from '@/stores/userStatus'
import { systemTimeService } from '@/services/systemTimeService'
import { House, Folder, Document, User, Clock, List, Calendar, DataAnalysis, ArrowDown, DocumentAdd, Checked, Box, Collection, Goods, OfficeBuilding, TrendCharts, PieChart, Loading, Ticket, Link, FolderAdd, Bell, Check, Warning, Setting, DocumentChecked, Reading, Monitor, Fold, SwitchButton } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import { ElMessage } from 'element-plus'
import MobileMenu from '@/components/mobile/MobileMenu.vue'
import { useResponsive } from '@/composables/useResponsive'

const { isMobile, isMobileRef, isMenuOpen, isMenuOpenRef, toggleMenu, closeMenu } = useResponsive()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const userStatusStore = useUserStatusStore()

// 初始化状态
const isInitializing = ref(true)
const isRouteReady = ref(false)

// 监听用户状态变化，确保完全加载后再显示页面
onMounted(async () => {
  try {
    await Promise.race([
      systemTimeService.syncServerTime(),
      new Promise(resolve => setTimeout(resolve, 5000))
    ])
  } catch (error) {
    console.error('Time sync error:', error)
  }

  if (userStore.token) {
    if (userStore.currentUser) {
      isInitializing.value = false
    } else {
      try {
        await Promise.race([
          userStore.fetchCurrentUser(),
          new Promise(resolve => setTimeout(resolve, 5000))
        ])
      } catch (error) {
        console.error('Fetch user error:', error)
      }
    }
    // 从后端获取用户状态
    try {
      await userStatusStore.fetchStatusFromBackend()
    } catch (error) {
      console.error('Fetch status error:', error)
    }
    
    // 添加用户活动监听
    window.addEventListener('mousemove', userStatusStore.onUserActivity)
    window.addEventListener('keydown', userStatusStore.onUserActivity)
    window.addEventListener('click', userStatusStore.onUserActivity)
  }
  isInitializing.value = false

  await router.isReady()
  isRouteReady.value = true
})

// 组件卸载时清理
onUnmounted(() => {
  userStatusStore.stopHeartbeat()
  window.removeEventListener('mousemove', userStatusStore.onUserActivity)
  window.removeEventListener('keydown', userStatusStore.onUserActivity)
  window.removeEventListener('click', userStatusStore.onUserActivity)
})

const currentRouteName = computed(() => {
  const routeMap = {
    '/dashboard': '仪表板',
    '/bugs/list': 'Bug 列表',
    '/bugs/new': '新建 Bug',
    '/bugs/:id': 'Bug 详情',
    '/bugs/:id/edit': '编辑 Bug',
    '/bugs/statistics': 'Bug 统计',
    '/projects/list': '项目列表',
    '/projects/statistics': '项目统计',
    '/projects/custom-report': '自定义报表',
    '/projects/:id': '项目详情',
    '/projects/:id/edit': '编辑项目',
    '/attendance/records': '考勤记录',
    '/attendance/records/:id': '考勤详情',
    '/attendance/leave-application': '请假申请',
    '/attendance/overtime-application': '加班申请',
    '/attendance/leave-approval': '请假审批',
    '/attendance/overtime-approval': '加班审批',
    '/attendance/shifts': '排班管理',
    '/attendance/reports': '统计报表',
    '/users/list': '用户列表',
    '/users/:id': '用户详情',
    '/profile': '个人配置',
    '/materials/categories': '物料分类管理',
    '/materials/list': '物料管理',
    '/materials/warehouses': '仓库管理',
    '/materials/inventory': '库存管理',
    '/materials/locations': '库位管理',
    '/materials/serial-numbers': '序列号管理',
    '/materials/relationships': '物料关系',
    '/materials/reports': '物料报表',
    '/contracts/list': '合同列表',
    '/contracts/statistics': '合同统计',
    '/contracts/:id': '合同详情',
    '/test-management/suites': '测试集管理',
    '/test-management/cases/:suiteId': '测试用例',
    '/test-management/executions/:projectId': '测试执行',
    '/reports/bug-statistics': 'Bug 统计',
    '/activities': '活动记录',
    '/work-logs': '工作日志',
    '/settings': '系统设置',
    '/knowledge': '知识库',
    '/monitoring': '系统监控'
  }
  
  // 尝试精确匹配
  if (routeMap[route.path]) {
    return routeMap[route.path]
  }
  
  // 尝试参数化匹配
  for (const [pattern, name] of Object.entries(routeMap)) {
    if (pattern.includes(':') && route.path.match(new RegExp(pattern.replace(/:[^/]+/g, '[^/]+')))) {
      return name
    }
  }
  
  return '页面'
})

const currentUser = computed(() => userStore.currentUser)
const isAdmin = computed(() => {
  return currentUser.value?.role === 'admin' || currentUser.value?.role === 'manager'
})

const hasAttendanceManagePermission = computed(() => {
  return currentUser.value?.role === 'admin' || currentUser.value?.role === 'manager' || currentUser.value?.role === 'project_manager' || currentUser.value?.role === 'hr' || currentUser.value?.role === 'department_manager'
})

const hasMaterialManagePermission = computed(() => {
  return currentUser.value?.role === 'admin' || currentUser.value?.role === 'manager' || currentUser.value?.role === 'project_manager'
})

const hasContractManagePermission = computed(() => {
  return currentUser.value?.role === 'admin' || currentUser.value?.role === 'manager' || currentUser.value?.role === 'project_manager'
})
const userAvatar = computed(() => {
  if (currentUser.value?.avatar) {
    // 如果头像URL已经是完整URL，直接返回
    if (currentUser.value.avatar.startsWith('http')) {
      return currentUser.value.avatar
    }
    // 拼接完整的API基础URL
    const baseURL = import.meta.env.PROD ? 'http://localhost:5000' : ''
    return `${baseURL}${currentUser.value.avatar}`
  }
  return '/avatar-placeholder.png'
})

const handleProfile = () => {
  // 导航到个人配置页面
  router.push('/profile')
}

const handleLogout = () => {
  // 处理退出登录
  userStore.logout()
  // 跳转到登录页面
  router.push('/login')
}

// ==================== 通知功能 ====================
const unreadCount = ref(0)
const notifications = ref([])
const loadingNotifications = ref(false)

// 加载通知数据
const loadNotifications = async () => {
  if (!userStore.token) return
  
  try {
    loadingNotifications.value = true
    // 加载未读数量
    const countResponse = await apiService.notifications.getUnreadCount()
    unreadCount.value = countResponse?.unread_count || 0
    
    // 加载最近通知
    const notificationsResponse = await apiService.notifications.getList({
      per_page: 10,
      is_read: 'false'
    })
    notifications.value = notificationsResponse?.notifications || []
  } catch (error) {
    console.error('加载通知失败:', error)
  } finally {
    loadingNotifications.value = false
  }
}

// 标记所有通知为已读
const markAllAsRead = async () => {
  try {
    await apiService.notifications.markAllAsRead()
    unreadCount.value = 0
    // 更新本地通知状态
    notifications.value = notifications.value.map(notification => ({
      ...notification,
      is_read: true
    }))
    ElMessage.success('所有通知已标记为已读')
  } catch (error) {
    console.error('标记全部为已读失败:', error)
    ElMessage.error('操作失败')
  }
}

// 处理通知命令
const handleNotificationCommand = (command) => {
  switch (command) {
    case 'viewAll':
      router.push('/notifications')
      break
    case 'markAllRead':
      markAllAsRead()
      break
  }
}

// 查看通知详情
const viewNotification = async (notification) => {
  try {
    // 如果未读，标记为已读
    if (!notification.is_read) {
      await apiService.notifications.markAsRead(notification.id)
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
    
    // 优先使用 link 字段跳转（支持评审通知等）
    if (notification.link) {
      router.push(notification.link)
    }
    // 如果有关联的 Bug，跳转到 Bug 详情页
    else if (notification.related_bug_id) {
      router.push(`/bugs/${notification.related_bug_id}`)
    }
  } catch (error) {
    console.error('处理通知失败:', error)
  }
}

// 格式化通知时间
const formatNotificationTime = (timeString) => {
  if (!timeString) return ''

  const now = systemTimeService.getServerTime()
  const notificationTime = new Date(timeString)
  const diffMinutes = Math.floor((now - notificationTime) / (1000 * 60))

  if (diffMinutes < 1) return '刚刚'
  if (diffMinutes < 60) return `${diffMinutes}分钟前`

  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours}小时前`

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}天前`

  return notificationTime.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 定时刷新通知（每5分钟）
let notificationInterval = null

// 监听用户登录状态变化，加载通知
watch(() => userStore.token, (newToken) => {
  if (newToken) {
    loadNotifications()
    // 启动定时刷新
    if (notificationInterval) clearInterval(notificationInterval)
    notificationInterval = setInterval(loadNotifications, 5 * 60 * 1000) // 5分钟
  } else {
    // 清除定时器
    if (notificationInterval) {
      clearInterval(notificationInterval)
      notificationInterval = null
    }
    // 清空通知数据
    unreadCount.value = 0
    notifications.value = []
  }
}, { immediate: true })

// 组件卸载时清除定时器
onUnmounted(() => {
  if (notificationInterval) {
    clearInterval(notificationInterval)
    notificationInterval = null
  }
})
</script>

<style scoped>
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-icon {
  font-size: 48px;
  color: #409EFF;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.app-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  color: #bfcbd9;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  border-bottom: 1px solid #2b3848;
}

.logo .el-icon {
  margin-right: 8px;
  font-size: 20px;
}

.sidebar-menu {
  border: none;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin: 0 8px;
  font-size: 14px;
}

/* 用户头像包装器 */
.user-avatar-wrapper {
  position: relative;
  display: inline-block;
}

/* 状态指示器 - 小 */
.status-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid #fff;
  background-color: #67c23a;
}

.status-indicator.online {
  background-color: #67c23a;
}

.status-indicator.busy {
  background-color: #f56c6c;
}

.status-indicator.away {
  background-color: #e6a23c;
}

.status-indicator.offline {
  background-color: #909399;
}

/* 状态指示器 - 大 */
.status-indicator-large {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid #fff;
  background-color: #67c23a;
}

.status-indicator-large.online {
  background-color: #67c23a;
}

.status-indicator-large.busy {
  background-color: #f56c6c;
}

.status-indicator-large.away {
  background-color: #e6a23c;
}

.status-indicator-large.offline {
  background-color: #909399;
}

/* 状态点 */
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  background-color: #67c23a;
}

.status-dot.online {
  background-color: #67c23a;
}

.status-dot.busy {
  background-color: #f56c6c;
}

.status-dot.away {
  background-color: #e6a23c;
}

.status-dot.offline {
  background-color: #909399;
}

/* 用户下拉菜单样式 */
:deep(.user-dropdown-menu) {
  padding: 0 !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

:deep(.user-dropdown-menu .el-dropdown-menu__item) {
  padding: 0 !important;
}

.user-dropdown-content {
  min-width: 240px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

/* 下拉菜单头部 */
.user-dropdown-header {
  display: flex;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.user-dropdown-avatar {
  position: relative;
  margin-right: 12px;
}

.user-dropdown-info {
  flex: 1;
  min-width: 0;
}

.user-dropdown-name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 2px;
}

.user-dropdown-username {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 4px;
}

.user-dropdown-status-text {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

/* 下拉菜单分区 */
.user-dropdown-section {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.user-dropdown-section:last-of-type {
  border-bottom: none;
}

.section-title {
  padding: 8px 16px;
  font-size: 12px;
  color: #909399;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 状态选项 */
.status-options {
  padding: 0 8px;
}

.status-option {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #606266;
}

.status-option:hover {
  background-color: #f5f7fa;
}

.status-option.active {
  background-color: #ecf5ff;
  color: #409eff;
}

/* 下拉菜单项 */
.dropdown-menu-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #606266;
}

.dropdown-menu-item:hover {
  background-color: #f5f7fa;
  color: #409eff;
}

.dropdown-menu-item .el-icon {
  margin-right: 10px;
  font-size: 16px;
}

.dropdown-menu-item.logout {
  color: #f56c6c;
}

.dropdown-menu-item.logout:hover {
  background-color: #fef0f0;
  color: #f56c6c;
}

/* 下拉菜单底部 */
.user-dropdown-footer {
  padding: 8px 0;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
}

@media screen and (max-width: 768px) {
  .app-container.mobile-layout {
    flex-direction: column;
  }

  .header {
    padding: 0 12px;
    height: 50px !important;
    line-height: 50px;
  }

  .header-left {
    flex: 1;
  }

  .menu-btn {
    border: none;
    background: transparent;
    padding: 4px 8px;
    margin-right: 8px;
  }

  .header-right {
    display: flex;
    align-items: center;
  }

  .username {
    display: none;
  }

  .notification-dropdown {
    margin-left: 8px;
  }

  .main-content {
    padding: 12px;
    overflow-x: hidden;
  }

  .user-info .el-avatar {
    width: 28px !important;
    height: 28px !important;
    min-width: 28px !important;
    line-height: 28px !important;
  }

  .sidebar {
    display: none !important;
  }

  .el-aside {
    display: none !important;
  }

  .notification-icon {
    padding: 4px;
  }

  .el-badge__content {
    right: 0 !important;
    top: -2px !important;
  }
}

@media screen and (max-width: 480px) {
  .header {
    padding: 0 8px;
    height: 46px !important;
    line-height: 46px;
  }

  .header-left .el-breadcrumb {
    display: none;
  }

  .main-content {
    padding: 8px;
  }

  .menu-btn .el-icon {
    font-size: 20px !important;
  }
}
</style>