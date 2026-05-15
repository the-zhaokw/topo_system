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
          text-color="#cbd5e1"
          active-text-color="#ffffff"
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
  return currentUser.value?.role === 'admin' || current