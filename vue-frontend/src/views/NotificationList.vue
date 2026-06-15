<template>
  <div class="notification-list-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Bell /></el-icon>
          </div>
          <div class="title-text">
            <h1>我的通知</h1>
            <p class="subtitle">查看和管理您的所有通知</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ total }}</div>
              <div class="stat-label">全部通知</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-unread">
            <div class="stat-icon-wrapper stat-icon-wrapper-unread">
              <el-icon><Message /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ unreadCount }}</div>
              <div class="stat-label">未读通知</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-today">
            <div class="stat-icon-wrapper stat-icon-wrapper-today">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ todayCount }}</div>
              <div class="stat-label">今日通知</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-read">
            <div class="stat-icon-wrapper stat-icon-wrapper-read">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ readCount }}</div>
              <div class="stat-label">已读通知</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section animate-fade-in-up delay-200">
      <el-card class="filter-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Filter /></el-icon>
              筛选条件
            </span>
          </div>
        </template>
        <el-form :model="filters" inline class="filter-form">
          <el-form-item label="通知类型">
            <el-select v-model="filters.type" placeholder="全部类型" clearable class="filter-select">
              <el-option label="缺陷分配" value="bug_assignment"></el-option>
              <el-option label="缺陷更新" value="bug_update"></el-option>
              <el-option label="提及" value="mention"></el-option>
              <el-option label="系统通知" value="system"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="阅读状态">
            <el-select v-model="filters.is_read" placeholder="全部状态" clearable class="filter-select">
              <el-option label="未读" value="false"></el-option>
              <el-option label="已读" value="true"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="loadNotifications" :loading="loading" class="btn-gradient">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset" class="btn-secondary">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
        <div class="filter-actions" v-if="unreadCount > 0">
          <el-button type="primary" @click="handleMarkAllAsRead" :loading="markingRead" class="btn-mark-all">
            <el-icon><Check /></el-icon>
            全部标记为已读 ({{ unreadCount }})
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 内容区域 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><Document /></el-icon>
              <h3>通知列表</h3>
              <span class="total-count">共 {{ total }} 条</span>
            </div>
          </div>
        </template>

        <el-table
          :data="notifications"
          v-loading="loading"
          stripe
          class="custom-table"
          style="width: 100%"
          @row-click="handleRowClick"
          :row-class-name="getRowClassName"
        >
          <el-table-column prop="is_read" label="状态" width="80" align="center">
            <template #default="{ row }">
              <div class="status-indicator" :class="{ 'unread': !row.is_read }">
                <el-icon v-if="!row.is_read" class="unread-dot"><CircleFilled /></el-icon>
                <el-icon v-else class="read-dot"><CircleCheck /></el-icon>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="type" label="类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getTypeTag(row.type)" size="small" effect="light" class="type-tag">
                {{ getTypeLabel(row.type) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <div class="notification-title-cell" :class="{ 'unread-title': !row.is_read }">
                <span class="title-text">{{ row.title }}</span>
                <el-icon v-if="!row.is_read" class="unread-badge"><StarFilled /></el-icon>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="content" label="内容" min-width="250">
            <template #default="{ row }">
              <span class="notification-content" :class="{ 'unread-content': !row.is_read }">{{ row.content }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="时间" width="180" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatTime(row.created_at) }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="140" align="center" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button
                  v-if="!row.is_read"
                  type="primary"
                  link
                  size="small"
                  @click.stop="handleMarkAsRead(row)"
                  class="action-btn read-btn"
                >
                  <el-icon><Check /></el-icon>
                  标记已读
                </el-button>
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click.stop="handleDelete(row)"
                  class="action-btn delete-btn"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadNotifications"
            @current-change="loadNotifications"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '@/services/api'
import { systemTimeService } from '@/services/systemTimeService'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Check, Delete, Bell, List, Message, Calendar, Filter, Document, CircleFilled, CircleCheck, StarFilled } from '@element-plus/icons-vue'

const router = useRouter()

const notifications = ref([])
const loading = ref(false)
const markingRead = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const unreadCount = ref(0)

const filters = ref({
  type: '',
  is_read: ''
})

// 计算统计数据
const readCount = computed(() => {
  return total.value - unreadCount.value
})

const todayCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return notifications.value.filter(n => n.created_at?.startsWith(today)).length
})

const getTypeLabel = (type) => {
  const typeMap = {
    'bug_assignment': '缺陷分配',
    'bug_update': '缺陷更新',
    'mention': '提及',
    'system': '系统通知',
    'requirement_review': '需求评审',
    'testcase_review': '用例评审'
  }
  return typeMap[type] || type
}

const getTypeTag = (type) => {
  const tagMap = {
    'bug_assignment': 'danger',
    'bug_update': 'warning',
    'mention': 'success',
    'system': 'info',
    'requirement_review': 'warning',
    'testcase_review': 'success'
  }
  return tagMap[type] || 'info'
}

const formatTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  const now = systemTimeService.getServerTime()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getRowClassName = ({ row }) => {
  return row.is_read ? '' : 'unread-row'
}

const loadNotifications = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }

    if (filters.value.type) {
      params.type = filters.value.type
    }
    if (filters.value.is_read) {
      params.is_read = filters.value.is_read
    }

    const response = await apiService.notifications.getList(params)

    if (response && response.notifications) {
      notifications.value = response.notifications
      total.value = response.pagination?.total || 0
    } else if (Array.isArray(response)) {
      notifications.value = response
      total.value = response.length
    } else {
      notifications.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('加载通知失败:', error)
    ElMessage.error('加载通知失败')
    notifications.value = []
  } finally {
    loading.value = false
  }
}

const loadUnreadCount = async () => {
  try {
    const response = await apiService.notifications.getUnreadCount()
    unreadCount.value = response?.unread_count || 0
  } catch (error) {
    console.error('获取未读数量失败:', error)
  }
}

const handleReset = () => {
  filters.value = {
    type: '',
    is_read: ''
  }
  currentPage.value = 1
  loadNotifications()
}

const handleMarkAsRead = async (notification) => {
  try {
    await apiService.notifications.markAsRead(notification.id)
    notification.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
    ElMessage.success('标记已读成功')
  } catch (error) {
    console.error('标记已读失败:', error)
    ElMessage.error('标记已读失败')
  }
}

const handleMarkAllAsRead = async () => {
  markingRead.value = true
  try {
    const response = await apiService.notifications.markAllAsRead()
    ElMessage.success(response?.message || '已全部标记为已读')
    unreadCount.value = 0
    notifications.value = notifications.value.map(n => ({ ...n, is_read: true }))
  } catch (error) {
    console.error('标记全部已读失败:', error)
    ElMessage.error('操作失败')
  } finally {
    markingRead.value = false
  }
}

const handleDelete = async (notification) => {
  try {
    await ElMessageBox.confirm('确定要删除这条通知吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await apiService.notifications.delete(notification.id)
    ElMessage.success('删除成功')
    if (!notification.is_read) {
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
    loadNotifications()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除通知失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleRowClick = async (row) => {
  if (!row.is_read) {
    await handleMarkAsRead(row)
  }

  if (row.link) {
    router.push(row.link)
  } else if (row.related_bug_id) {
    router.push(`/bugs/${row.related_bug_id}`)
  }
}

onMounted(() => {
  loadNotifications()
  loadUnreadCount()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.notification-list-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(56, 189, 248, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(14, 165, 233, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.page-header::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
  pointer-events: none;
}

.header-bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
}

.orb-1 {
  width: 200px;
  height: 200px;
  background: #f093fb;
  top: -50px;
  right: 10%;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 150px;
  height: 150px;
  background: #4facfe;
  bottom: -30px;
  right: 30%;
  animation: float 8s ease-in-out infinite reverse;
}

.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-icon-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.title-icon {
  font-size: 32px;
  color: white;
}

.title-text h1 {
  margin: 0 0 6px 0;
  color: white;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 400;
}

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.stat-card::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  transform: scaleX(0);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15), 0 10px 20px -5px rgba(0, 0, 0, 0.1);
}

.stat-card:hover::before {
  transform: scaleX(1);
}

.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-unread::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-today::before { background: linear-gradient(90deg, #ec4899, #f472b6); }
.stat-card-read::before { background: linear-gradient(90deg, #11998e, #38ef7d); }

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.4s;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-icon-wrapper-unread {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-today {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
}

.stat-icon-wrapper-read {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-unread .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-today .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-read .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s;
}

.glass-card:hover {
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 10px 20px -5px rgba(0, 0, 0, 0.08);
}

/* 筛选区域 */
.filter-section {
  margin-bottom: 24px;
}

.filter-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.card-title .el-icon {
  color: #0ea5e9;
  font-size: 18px;
}

.filter-form {
  padding: 10px 0;
}

.filter-select {
  width: 160px;
}

.filter-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(226, 232, 240, 0.6);
}

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5);
}

.btn-secondary {
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(56, 189, 248, 0.1);
  border-color: #0ea5e9;
  color: #0ea5e9;
}

.btn-mark-all {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-mark-all:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(17, 153, 142, 0.5);
}

/* 内容区域 */
.content-section {
  margin-bottom: 20px;
}

/* 表格头部 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-title .el-icon {
  color: #0ea5e9;
  font-size: 20px;
}

.table-title h3 {
  margin: 0;
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
}

.total-count {
  font-size: 13px;
  color: #64748b;
  margin-left: 8px;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 12px;
  border-radius: 20px;
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(56, 189, 248, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

/* 状态指示器 */
.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
}

.unread-dot {
  font-size: 12px;
  color: #f56c6c;
  animation: pulse 2s ease-in-out infinite;
}

.read-dot {
  font-size: 14px;
  color: #67c23a;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 类型标签 */
.type-tag {
  font-weight: 500;
  border-radius: 6px;
}

/* 通知标题单元格 */
.notification-title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.unread-title .title-text {
  color: #f56c6c;
  font-weight: 700;
}

.unread-badge {
  font-size: 12px;
  color: #f56c6c;
  animation: pulse 2s ease-in-out infinite;
}

/* 通知内容 */
.notification-content {
  color: #606266;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
  max-width: 300px;
}

.unread-content {
  color: #1e293b;
  font-weight: 500;
}

/* 时间戳 */
.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.action-btn {
  opacity: 0;
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) .action-btn {
  opacity: 1;
}

.read-btn {
  color: #7dd3fc;
}

.read-btn:hover {
  color: #38bdf8;
}

.delete-btn {
  color: #f56c6c;
}

.delete-btn:hover {
  color: #f78989;
}

/* 未读行样式 */
:deep(.unread-row) {
  background-color: rgba(254, 240, 240, 0.6);
  cursor: pointer;
}

:deep(.unread-row:hover > td) {
  background-color: rgba(253, 226, 226, 0.8) !important;
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-fade-in-down {
  animation: fadeInDown 0.6s ease-out;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out;
  animation-fill-mode: both;
}

.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .notification-list-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-title {
    gap: 14px;
  }

  .title-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 14px;
  }

  .title-icon {
    font-size: 24px;
  }

  .title-text h1 {
    font-size: 22px;
  }

  .subtitle {
    font-size: 13px;
  }

  .stats-row {
    margin-bottom: 20px;
  }

  .stat-card {
    padding: 16px;
    gap: 12px;
    margin-bottom: 12px;
  }

  .stat-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  .filter-form {
    flex-direction: column;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 12px;
    width: 100%;
  }

  .filter-select {
    width: 100% !important;
  }

  .filter-actions {
    width: 100%;
  }

  .filter-actions .el-button {
    width: 100%;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .action-btn {
    opacity: 1;
  }

  .notification-content {
    max-width: 200px;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
  }

  .pagination-section {
    justify-content: center;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-value {
    font-size: 20px;
  }

  .notification-content {
    max-width: 150px;
    font-size: 11px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-pagination {
    font-size: 10px !important;
  }

  .el-pagination button,
  .el-pager li {
    min-width: 24px !important;
    height: 24px !important;
    line-height: 24px !important;
  }
}
</style>
