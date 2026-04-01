<template>
  <div v-if="isMobile" class="mobile-menu-overlay" :class="{ 'show': isMenuOpen }" @click.self="closeMenu">
    <div class="mobile-menu">
      <div class="mobile-menu-header">
        <div class="logo">
          <el-icon><Warning /></el-icon>
          <span>TOPO系统</span>
        </div>
        <el-icon class="close-btn" @click="closeMenu"><Close /></el-icon>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        class="mobile-menu-nav"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        @select="closeMenu"
      >
        <el-menu-item index="/dashboard" @click="closeMenu">
          <el-icon><House /></el-icon>
          <span>个人工作台</span>
        </el-menu-item>

        <el-sub-menu index="projects">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>项目管理</span>
          </template>
          <el-menu-item index="/projects/list">
            <span>项目列表</span>
          </el-menu-item>
          <el-menu-item index="/projects/statistics">
            <span>项目统计</span>
          </el-menu-item>
          <el-menu-item index="/projects/custom-report">
            <span>自定义报表</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="bugs">
          <template #title>
            <el-icon><Ticket /></el-icon>
            <span>缺陷管理</span>
          </template>
          <el-menu-item index="/bugs/list">
            <span>缺陷列表</span>
          </el-menu-item>
          <el-menu-item index="/bugs/statistics">
            <span>Bug统计</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="attendance">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>考勤管理系统</span>
          </template>
          <el-menu-item index="/attendance/records">
            <span>考勤记录</span>
          </el-menu-item>
          <el-menu-item index="/attendance/leave-application">
            <span>请假申请</span>
          </el-menu-item>
          <el-menu-item index="/attendance/overtime-application">
            <span>加班申请</span>
          </el-menu-item>
          <el-menu-item v-if="currentUser && hasAttendanceManagePermission" index="/attendance/leave-approval">
            <span>请假审批</span>
          </el-menu-item>
          <el-menu-item v-if="currentUser && hasAttendanceManagePermission" index="/attendance/overtime-approval">
            <span>加班审批</span>
          </el-menu-item>
          <el-menu-item v-if="currentUser && hasAttendanceManagePermission" index="/attendance/shifts">
            <span>排班管理</span>
          </el-menu-item>
          <el-menu-item index="/attendance/reports">
            <span>统计报表</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="materials" v-if="currentUser && hasMaterialManagePermission">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>物料管理系统</span>
          </template>
          <el-menu-item index="/materials/categories">
            <span>物料分类</span>
          </el-menu-item>
          <el-menu-item index="/materials/list">
            <span>物料管理</span>
          </el-menu-item>
          <el-menu-item index="/materials/warehouses">
            <span>仓库管理</span>
          </el-menu-item>
          <el-menu-item index="/materials/inventory">
            <span>库存管理</span>
          </el-menu-item>
          <el-menu-item index="/materials/locations">
            <span>库位管理</span>
          </el-menu-item>
          <el-menu-item index="/materials/serial-numbers">
            <span>序列号管理</span>
          </el-menu-item>
          <el-menu-item index="/materials/relationships">
            <span>物料关系</span>
          </el-menu-item>
          <el-menu-item index="/materials/reports">
            <span>物料报表</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="contracts" v-if="currentUser && hasContractManagePermission">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>合同管理系统</span>
          </template>
          <el-menu-item index="/contracts/list">
            <span>合同列表</span>
          </el-menu-item>
          <el-menu-item index="/contracts/statistics">
            <span>统计报表</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/activities" @click="closeMenu">
          <el-icon><Clock /></el-icon>
          <span>活动记录</span>
        </el-menu-item>

        <el-menu-item index="/knowledge" @click="closeMenu">
          <el-icon><Reading /></el-icon>
          <span>知识库</span>
        </el-menu-item>

        <el-menu-item index="/monitoring" @click="closeMenu">
          <el-icon><Monitor /></el-icon>
          <span>系统监控</span>
        </el-menu-item>

        <el-menu-item v-if="currentUser && isAdmin" index="/users" @click="closeMenu">
          <el-icon><UserFilled /></el-icon>
          <span>用户管理</span>
        </el-menu-item>

        <el-menu-item v-if="currentUser && isAdmin" index="/settings" @click="closeMenu">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>

        <el-menu-item index="/notifications" @click="closeMenu">
          <el-icon><Bell /></el-icon>
          <span>通知</span>
        </el-menu-item>

        <el-menu-item index="/profile" @click="closeMenu">
          <el-icon><User /></el-icon>
          <span>个人设置</span>
        </el-menu-item>
      </el-menu>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { House, Folder, Ticket, Calendar, Bell, User, Warning, Close, Box, Document, Clock, Reading, Monitor, UserFilled, Setting } from '@element-plus/icons-vue'

const userStore = useUserStore()

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

defineProps({
  isMobile: {
    type: Boolean,
    default: false
  },
  isMenuOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const closeMenu = () => {
  emit('close')
}
</script>

<style scoped>
.mobile-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.mobile-menu-overlay.show {
  opacity: 1;
  visibility: visible;
}

.mobile-menu {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 280px;
  max-width: 80vw;
  background: #304156;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.mobile-menu-overlay.show .mobile-menu {
  transform: translateX(0);
}

.mobile-menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #263445;
  color: #fff;
}

.mobile-menu-header .logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
}

.close-btn {
  font-size: 24px;
  cursor: pointer;
  color: #bfcbd9;
  padding: 4px;
}

.close-btn:hover {
  color: #fff;
}

.mobile-menu-nav {
  border-right: none;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
  padding-left: 16px !important;
  padding-right: 16px !important;
  font-size: 14px;
}

:deep(.el-menu-item span),
:deep(.el-sub-menu__title span) {
  margin-left: 8px;
}

:deep(.el-sub-menu .el-menu-item) {
  height: 44px;
  line-height: 44px;
  padding-left: 32px !important;
  font-size: 13px;
}

@media screen and (max-width: 480px) {
  .mobile-menu {
    width: 85vw;
  }

  .mobile-menu-header {
    padding: 12px;
  }

  .mobile-menu-header .logo {
    font-size: 16px;
  }

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 46px;
    line-height: 46px;
    font-size: 13px;
  }

  :deep(.el-sub-menu .el-menu-item) {
    height: 40px;
    line-height: 40px;
    font-size: 12px;
  }
}
</style>
