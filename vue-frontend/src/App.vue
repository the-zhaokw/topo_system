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

    <!-- 移动端底部 Tab 栏 -->
    <MobileTabBar v-if="!isInitializing && isRouteReady && $route.path !== '/login' && isMobile" />

    <!-- 桌面端布局 -->
    <el-container v-if="!isInitializing && isRouteReady && $route.path !== '/login'" class="app-container" :class="{ 'mobile-layout': isMobile }">
      <!-- 侧边栏导航（仅桌面端显示） -->
      <el-aside v-if="!isMobile" width="260px" class="sidebar">
        <div class="logo">
          <div class="logo-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <span>TOPO系统</span>
        </div>
        
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          background-color="transparent"
          text-color="#0c4a6e"
          active-text-color="#ffffff"
        >
          <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>个人工作台</span>
        </el-menu-item>

        <el-sub-menu v-if="currentUser && hasModule('module:project')" index="projects">
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

        <el-sub-menu v-if="currentUser && hasModule('module:bug')" index="bugs">
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

        <el-sub-menu v-if="currentUser && hasModule('module:attendance')" index="attendance">
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

        <el-sub-menu v-if="currentUser && hasModule('module:material')" index="materials">
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

        <el-sub-menu v-if="currentUser && hasModule('module:contract')" index="contracts">
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

        <el-sub-menu index="users" v-if="currentUser && hasModule('module:user')">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/users/list">
            <el-icon><List /></el-icon>
            <span>用户列表</span>
          </el-menu-item>
          <el-menu-item v-if="currentUser && canManageModulePerms" index="/users/module-permissions">
            <el-icon><Lock /></el-icon>
            <span>模块权限管理</span>
          </el-menu-item>
          <el-menu-item v-if="currentUser && canManageTemplates" index="/users/permission-templates">
            <el-icon><CollectionTag /></el-icon>
            <span>权限模板</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item v-if="currentUser && hasModule('module:settings')" index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>

        <el-menu-item v-if="currentUser && hasModule('module:activity')" index="/activities">
          <el-icon><Clock /></el-icon>
          <span>活动记录</span>
        </el-menu-item>

        <el-menu-item v-if="currentUser && hasModule('module:knowledge')" index="/knowledge">
          <el-icon><Reading /></el-icon>
          <span>知识库</span>
        </el-menu-item>

        <el-menu-item v-if="currentUser && hasModule('module:monitoring')" index="/monitoring">
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
                  <el-avatar :size="36" :src="userAvatar" />
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
                      <el-avatar :size="52" :src="userAvatar" />
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
import { House, Folder, Document, User, Clock, List, Calendar, DataAnalysis, ArrowDown, DocumentAdd, Checked, Box, Collection, Goods, OfficeBuilding, TrendCharts, PieChart, Loading, Ticket, Link, FolderAdd, Bell, Check, Warning, Setting, DocumentChecked, Reading, Monitor, Fold, SwitchButton, Lock } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import { ElMessage } from 'element-plus'
import MobileMenu from '@/components/mobile/MobileMenu.vue'
import MobileTabBar from '@/components/mobile/MobileTabBar.vue'
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

// 「模块权限管理」菜单可见性：
//   - 系统管理员 / 职位管理员 / 经理：可见
//   - 普通用户：必须有 module_perm:view 权限
const canManageModulePerms = computed(() => {
  const u = currentUser.value
  if (!u) return false
  if (u.is_super_admin || u.is_admin || u.role === 'admin' || u.role === 'manager') return true
  return userStore.hasPermission('module_perm:view')
})

// 「权限模板」菜单可见性：
//   - 系统管理员 / 职位管理员 / 经理：可见
//   - 普通用户：必须有 template:view 权限
const canManageTemplates = computed(() => {
  const u = currentUser.value
  if (!u) return false
  if (u.is_super_admin || u.is_admin || u.role === 'admin' || u.role === 'manager') return true
  return userStore.hasPermission('template:view')
})

/**
 * 判断当前用户是否可访问指定大功能模块
 * - 系统管理员 / 职位是 admin|manager：拥有所有模块
 * - 其他用户：依据 currentUser.accessible_modules
 */
const hasModule = (moduleCode) => {
  const u = currentUser.value
  if (!u) return false
  // 超级管理员、admin/manager 角色默认拥有所有模块
  if (u.is_super_admin || u.is_admin) return true
  const list = u.accessible_modules
  if (Array.isArray(list)) {
    return list.includes(moduleCode)
  }
  return false
}

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
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.loading-spinner span {
  color: #0ea5e9;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.loading-icon {
  font-size: 56px;
  color: #0ea5e9;
  animation: spin 1s linear infinite, pulse 2s ease-in-out infinite;
  filter: drop-shadow(0 0 15px rgba(56, 189, 248, 0.5));
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: rotate(0deg) scale(1); }
  50% { opacity: 0.85; transform: rotate(0deg) scale(1.05); }
}

/* 通知菜单样式 */
.notification-menu {
  max-width: 360px;
  min-width: 320px;
  border-radius: 16px;
  overflow: hidden;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid #f1f5f9;
  font-weight: 600;
  color: #1e293b;
  background: linear-gradient(to bottom, #fafafa, #f8fafc);
}

.notification-header span {
  font-size: 15px;
}

.notification-list {
  max-height: 320px;
  overflow-y: auto;
}

.notification-item {
  padding: 14px 18px;
  cursor: pointer;
  transition: all 0.3s;
  border-bottom: 1px solid #f8fafc;
}

.notification-item:hover {
  background: rgba(56, 189, 248, 0.04);
}

.notification-item.unread {
  background: rgba(56, 189, 248, 0.06);
  border-left: 3px solid #38bdf8;
}

.notification-item.unread:hover {
  background: rgba(56, 189, 248, 0.1);
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 4px;
}

.notification-content {
  font-size: 13px;
  color: #64748b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-time {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 6px;
}

.notification-empty {
  padding: 32px 16px;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}

.notification-empty .el-icon {
  font-size: 32px;
  margin-bottom: 8px;
  color: #d1d5db;
}

.app-container {
  height: 100vh;
}

/* 侧边栏 - 淡蓝主题 */
.sidebar {
  background: linear-gradient(180deg, #bae6fd 0%, #7dd3fc 100%) !important;
  color: #0c4a6e;
  position: relative;
  overflow: hidden;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(ellipse at top, rgba(56, 189, 248, 0.5) 0%, transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(14, 165, 233, 0.3) 0%, transparent 40%);
  pointer-events: none;
}

.sidebar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%2338bdf8' fill-opacity='0.03' fill-rule='evenodd'/%3E%3C/svg%3E");
  opacity: 0.6;
  pointer-events: none;
}

.logo {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
  color: #0c4a6e;
  border-bottom: 1px solid rgba(14, 165, 233, 0.25);
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.5) 0%, rgba(14, 165, 233, 0.4) 100%);
  position: relative;
  z-index: 1;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.5);
}

.logo-icon .el-icon {
  font-size: 22px;
  color: white;
}

.sidebar-menu {
  --el-menu-text-color: #0c4a6e;
  --el-menu-hover-text-color: #075985;
  --el-menu-active-color: #ffffff;
  --el-menu-bg-color: transparent;
  --el-menu-border-color: transparent;
  border: none;
  background: transparent !important;
  position: relative;
  z-index: 1;
  max-height: calc(100vh - 70px);
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background: rgba(56, 189, 248, 0.3);
  border-radius: 2px;
}

.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background: rgba(56, 189, 248, 0.5);
}

.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 10px;
  margin: 6px 12px;
  padding-left: 16px !important;
  padding-right: 16px !important;
  height: 46px;
  line-height: 46px;
  color: #0c4a6e !important;
  font-weight: 500;
}

.sidebar-menu .el