<template>
  <div class="notification-list-container">
    <div class="page-header">
      <h1>我的通知</h1>
      <p>查看和管理您的所有通知</p>
    </div>

    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="通知类型">
          <el-select v-model="filters.type" placeholder="全部类型" clearable>
            <el-option label="缺陷分配" value="bug_assignment"></el-option>
            <el-option label="缺陷更新" value="bug_update"></el-option>
            <el-option label="提及" value="mention"></el-option>
            <el-option label="系统通知" value="system"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="阅读状态">
          <el-select v-model="filters.is_read" placeholder="全部状态" clearable>
            <el-option label="未读" value="false"></el-option>
            <el-option label="已读" value="true"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadNotifications" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
      <div class="filter-actions">
        <el-button
          v-if="unreadCount > 0"
          type="primary"
          @click="handleMarkAllAsRead"
          :loading="markingRead"
        >
          <el-icon><Check /></el-icon>
          全部标记为已读 ({{ unreadCount }})
        </el-button>
      </div>
    </el-card>

    <el-card class="content-card">
      <div class="table-header">
        <h3>通知列表</h3>
        <span class="total-count">共 {{ total }} 条</span>
      </div>

      <el-table
        :data="notifications"
        v-loading="loading"
        style="width: 100%"
        @row-click="handleRowClick"
        :row-class-name="getRowClassName"
      >
        <el-table-column prop="is_read" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_read ? 'info' : 'danger'" size="small">
              {{ row.is_read ? '已读' : '未读' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" size="small">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <div class="notification-title-cell">
              <span :class="{ 'unread-title': !row.is_read }">{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="content" label="内容" min-width="250">
          <template #default="{ row }">
            <span class="notification-content">{{ row.content }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_read"
              type="primary"
              link
              @click.stop="handleMarkAsRead(row)"
            >
              标记已读
            </el-button>
            <el-button
              type="danger"
              link
              @click.stop="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
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
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '@/services/api'
import { systemTimeService } from '@/services/systemTimeService'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Check, Delete } from '@element-plus/icons-vue'

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
.notification-list-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-actions {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.content-card {
  min-height: 400px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.total-count {
  color: #909399;
  font-size: 14px;
}

.notification-title-cell {
  font-weight: 500;
}

.unread-title {
  color: #f56c6c;
  font-weight: 600;
}

.notification-content {
  color: #606266;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
  max-width: 300px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.unread-row) {
  background-color: #fef0f0;
  cursor: pointer;
}

:deep(.unread-row:hover > td) {
  background-color: #fde2e2 !important;
}

@media screen and (max-width: 768px) {
  .notification-list-container {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 16px;
  }

  .page-header h1 {
    font-size: 18px;
    margin: 0 0 8px 0;
  }

  .page-header p {
    font-size: 12px;
  }

  .filter-card {
    margin-bottom: 16px;
  }

  .filter-card .el-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .filter-card .el-form-item {
    margin-bottom: 8px;
  }

  .filter-card .el-form-item__label {
    width: 80px !important;
    min-width: 80px !important;
    font-size: 12px;
  }

  .filter-card .el-input,
  .filter-card .el-select {
    width: 100% !important;
  }

  .filter-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-start;
    margin-top: 8px;
  }

  .filter-actions .el-button {
    flex: none;
    font-size: 12px;
    padding: 6px 12px;
  }

  .content-card {
    min-height: 300px;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 12px;
    padding-bottom: 12px;
  }

  .table-header h3 {
    font-size: 14px;
  }

  .total-count {
    font-size: 12px;
  }

  .notification-content {
    max-width: 200px;
    font-size: 12px;
  }

  .pagination-wrapper {
    margin-top: 16px;
    justify-content: center;
  }

  .el-pagination {
    font-size: 11px !important;
    flex-wrap: wrap;
    gap: 4px;
  }

  .el-pagination__sizes,
  .el-pagination__jump {
    display: none !important;
  }

  .el-pagination button,
  .el-pager li {
    min-width: 26px !important;
    height: 26px !important;
    line-height: 26px !important;
    font-size: 11px !important;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .el-dialog__header {
    padding: 12px !important;
  }

  .el-dialog__body {
    padding: 12px !important;
    max-height: 60vh !important;
    overflow-y: auto !important;
  }

  .el-dialog__footer {
    padding: 12px !important;
  }
}

@media screen and (max-width: 480px) {
  .notification-list-container {
    padding: 8px;
  }

  .page-header h1 {
    font-size: 16px;
  }

  .filter-actions .el-button {
    font-size: 11px;
    padding: 5px 10px;
  }

  .table-header h3 {
    font-size: 13px;
  }

  .notification-content {
    max-width: 150px;
    font-size: 11px;
  }

  .el-table {
    font-size: 10px !important;
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
