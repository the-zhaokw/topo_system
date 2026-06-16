<template>
  <nav v-if="visible" class="mobile-tab-bar" :class="{ 'with-safe-area': hasSafeArea }">
    <router-link
      v-for="item in items"
      :key="item.path"
      :to="item.path"
      class="tab-item"
      :class="{ active: isActive(item) }"
    >
      <el-badge
        v-if="item.badge !== undefined && item.badge > 0"
        :value="item.badge"
        :max="99"
        class="tab-badge"
      >
        <el-icon class="tab-icon" :size="22">
          <component :is="item.icon" />
        </el-icon>
      </el-badge>
      <el-icon v-else class="tab-icon" :size="22">
        <component :is="item.icon" />
      </el-icon>
      <span class="tab-label">{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { House, Document, List, User, Bell, Folder, Calendar, Reading } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { apiService } from '@/services/api'

const route = useRoute()
const userStore = useUserStore()

const unreadCount = ref(0)
let pollTimer = null

const currentUser = computed(() => userStore.currentUser)
const isAdmin = computed(
  () => currentUser.value?.role === 'admin' || currentUser.value?.role === 'manager'
)
const hasMaterialPermission = computed(() =>
  ['admin', 'manager', 'project_manager'].includes(currentUser.value?.role)
)

const hasSafeArea = ref(false)

const isActive = (item) => {
  if (item.exact) {
    return route.path === item.path
  }
  return route.path === item.path || route.path.startsWith(item.path + '/')
}

const items = computed(() => {
  const list = [
    { path: '/dashboard', label: '工作台', icon: House, exact: true },
    { path: '/bugs/list', label: '缺陷', icon: Document },
    { path: '/projects/list', label: '项目', icon: Folder },
    { path: '/my-todos', label: '待办', icon: List },
    { path: '/notifications', label: '消息', icon: Bell, badge: unreadCount.value }
  ]
  return list
})

const visible = computed(() => route.path !== '/login')

const loadUnread = async () => {
  if (!userStore.token) return
  try {
    const resp = await apiService.notifications.getUnreadCount()
    unreadCount.value = resp?.unread_count || 0
  } catch (e) {
    // 静默失败
  }
}

onMounted(() => {
  // 检测安全区域
  if (window.CSS && CSS.supports('padding-bottom: env(safe-area-inset-bottom)')) {
    hasSafeArea.value = true
  }
  loadUnread()
  pollTimer = setInterval(loadUnread, 60 * 1000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.mobile-tab-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 998;
  display: flex;
  align-items: stretch;
  justify-content: space-around;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(226, 232, 240, 0.6);
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.06);
  padding-bottom: env(safe-area-inset-bottom, 0);
  user-select: none;
  -webkit-user-select: none;
}

.mobile-tab-bar.with-safe-area {
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 6px 4px 8px;
  color: #64748b;
  text-decoration: none;
  font-size: 11px;
  font-weight: 500;
  transition: color 0.2s, transform 0.15s;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
  position: relative;
  min-height: 52px;
}

.tab-item:active {
  transform: scale(0.92);
}

.tab-item.active {
  color: #0ea5e9;
}

.tab-item.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  border-radius: 0 0 3px 3px;
  background: linear-gradient(90deg, #38bdf8, #0ea5e9);
}

.tab-icon {
  font-size: 22px;
  transition: transform 0.2s;
}

.tab-item.active .tab-icon {
  transform: scale(1.1);
  filter: drop-shadow(0 0 6px rgba(14, 165, 233, 0.4));
}

.tab-label {
  font-size: 11px;
  line-height: 1.2;
  letter-spacing: 0.2px;
}

.tab-badge {
  display: flex;
}

.tab-badge :deep(.el-badge__content) {
  top: -4px;
  right: -10px;
  font-size: 10px;
  height: 16px;
  line-height: 16px;
  padding: 0 4px;
  min-width: 16px;
  border: 2px solid #fff;
}
</style>
