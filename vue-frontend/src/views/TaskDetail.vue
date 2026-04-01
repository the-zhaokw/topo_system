<template>
  <div class="task-detail">
    <h1>任务详情</h1>
    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    <div v-else-if="error" class="error-container">
      <el-alert :title="error" type="error" show-icon />
      <el-button type="primary" @click="fetchTaskDetail">重试</el-button>
    </div>
    <el-card v-else class="task-card">
      <template #header>
        <div class="card-header">
          <h2>{{ task.title }}</h2>
          <el-tag :type="getStatusType(task.status)">{{ getStatusText(task.status) }}</el-tag>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="16">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="任务描述">{{ task.description || '-' }}</el-descriptions-item>
            <el-descriptions-item label="项目">{{ task.project?.name || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-col>
        
        <el-col :span="8">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="优先级">
              <el-tag :type="getPriorityType(task.priority)">{{ getPriorityText(task.priority) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建者">{{ task.creator?.username || '-' }}</el-descriptions-item>
            <el-descriptions-item label="负责人">{{ task.assignee?.username || '未分配' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(task.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="截止日期">{{ task.due_date ? formatDate(task.due_date) : '-' }}</el-descriptions-item>
            <el-descriptions-item label="预计时长">{{ task.estimated_hours || 0 }} 小时</el-descriptions-item>
            <el-descriptions-item label="实际时长">{{ task.actual_hours || 0 }} 小时</el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { apiService } from '@/services/api'

const route = useRoute()
const taskId = computed(() => route.params.id)

const task = ref(null)
const loading = ref(true)
const error = ref('')

const fetchTaskDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await apiService.tasks.getById(taskId.value)
    task.value = data
  } catch (err) {
    error.value = '获取任务详情失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTaskDetail()
})

const getStatusText = (status) => {
  const statusMap = {
    TODO: '待处理',
    IN_PROGRESS: '进行中',
    REVIEW: '审核中',
    DONE: '已完成',
    BLOCKED: '阻塞',
    CANCELLED: '已取消'
  }
  return statusMap[status] || status
}

const getStatusType = (status) => {
  const typeMap = {
    TODO: 'info',
    IN_PROGRESS: 'warning',
    REVIEW: 'primary',
    DONE: 'success',
    BLOCKED: 'danger',
    CANCELLED: 'info'
  }
  return typeMap[status] || 'info'
}

const getPriorityText = (priority) => {
  const priorityMap = {
    LOW: '低',
    MEDIUM: '中',
    HIGH: '高',
    URGENT: '紧急'
  }
  return priorityMap[priority] || priority
}

const getPriorityType = (priority) => {
  const typeMap = {
    LOW: 'info',
    MEDIUM: 'warning',
    HIGH: 'danger',
    URGENT: 'danger'
  }
  return typeMap[priority] || 'info'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.task-detail {
  padding: 20px;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 10px;
}

.loading-icon {
  font-size: 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-card {
  margin-top: 20px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .task-detail {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 8px 12px;
  }

  .task-info-card {
    margin-bottom: 16px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .info-item {
    padding: 10px;
  }

  .info-label {
    font-size: 12px;
  }

  .info-value {
    font-size: 14px;
  }

  .task-card {
    margin-top: 16px;
    padding: 12px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .task-detail {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .info-label {
    font-size: 11px;
  }

  .info-value {
    font-size: 13px;
  }
}
</style>