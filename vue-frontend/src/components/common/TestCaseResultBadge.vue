<template>
  <div class="test-case-result-badge">
    <el-tooltip v-if="showTooltip" placement="top" :content="tooltipContent">
      <el-tag :type="badgeType" :size="size" :effect="effect" class="badge-tag">
        <el-icon v-if="showIcon" class="badge-icon">
          <SuccessFilled v-if="result === 'passed'" />
          <CircleCloseFilled v-else-if="result === 'failed'" />
          <WarningFilled v-else-if="result === 'blocked'" />
          <Minus v-else />
        </el-icon>
        <span v-if="showLabel">{{ resultLabel }}</span>
        <span v-if="showTime && lastExecutedAt" class="execute-time">
          {{ formatRelativeTime(lastExecutedAt) }}
        </span>
      </el-tag>
    </el-tooltip>
    <el-tag v-else :type="badgeType" :size="size" :effect="effect" class="badge-tag">
      <el-icon v-if="showIcon" class="badge-icon">
        <SuccessFilled v-if="result === 'passed'" />
        <CircleCloseFilled v-else-if="result === 'failed'" />
        <WarningFilled v-else-if="result === 'blocked'" />
        <Minus v-else />
      </el-icon>
      <span v-if="showLabel">{{ resultLabel }}</span>
      <span v-if="showTime && lastExecutedAt" class="execute-time">
        {{ formatRelativeTime(lastExecutedAt) }}
      </span>
    </el-tag>

    <el-popover
      v-if="showHistory"
      placement="bottom"
      :width="320"
      trigger="click"
    >
      <template #reference>
        <el-button link type="primary" size="small" class="history-link">
          <el-icon><Clock /></el-icon>
        </el-button>
      </template>
      <div class="history-content">
        <h4>执行历史</h4>
        <el-scrollbar height="200px">
          <div v-if="historyLoading" class="loading-state">
            <el-icon class="is-loading"><Loading /></el-icon>
          </div>
          <div v-else-if="executionHistory.length === 0" class="empty-state">
            暂无执行历史
          </div>
          <div v-else class="history-list">
            <div
              v-for="record in executionHistory"
              :key="record.id"
              class="history-item"
            >
              <div class="history-info">
                <el-tag :type="getHistoryType(record.result)" size="small">
                  {{ getHistoryLabel(record.result) }}
                </el-tag>
                <span class="history-executor">{{ record.executor_name }}</span>
              </div>
              <div class="history-time">
                {{ formatDateTime(record.executed_at) }}
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </el-popover>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  SuccessFilled,
  CircleCloseFilled,
  WarningFilled,
  Minus,
  Clock,
  Loading
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const props = defineProps({
  caseId: {
    type: [Number, String],
    required: true
  },
  result: {
    type: String,
    default: null,
    validator: (value) => [null, 'passed', 'failed', 'blocked', 'skipped', 'pending'].includes(value)
  },
  lastExecutedAt: {
    type: String,
    default: null
  },
  size: {
    type: String,
    default: 'small',
    validator: (value) => ['large', 'medium', 'small', 'mini'].includes(value)
  },
  effect: {
    type: String,
    default: 'light',
    validator: (value) => ['light', 'dark', 'plain'].includes(value)
  },
  showIcon: {
    type: Boolean,
    default: true
  },
  showLabel: {
    type: Boolean,
    default: true
  },
  showTime: {
    type: Boolean,
    default: false
  },
  showTooltip: {
    type: Boolean,
    default: true
  },
  showHistory: {
    type: Boolean,
    default: false
  },
  tooltipContent: {
    type: String,
    default: ''
  }
})

const executionHistory = ref([])
const historyLoading = ref(false)

const badgeType = computed(() => {
  const typeMap = {
    passed: 'success',
    failed: 'danger',
    blocked: 'warning',
    skipped: 'info',
    pending: 'info'
  }
  return typeMap[props.result] || 'info'
})

const resultLabel = computed(() => {
  const labelMap = {
    passed: '通过',
    failed: '失败',
    blocked: '阻塞',
    skipped: '跳过',
    pending: '待执行'
  }
  return labelMap[props.result] || '未执行'
})

const tooltipContent = computed(() => {
  if (props.tooltipContent) return props.tooltipContent
  if (!props.lastExecutedAt) return '未执行'
  return `最后执行: ${formatDateTime(props.lastExecutedAt)}`
})

const formatRelativeTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  return '刚刚'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getHistoryType = (result) => {
  const typeMap = {
    passed: 'success',
    failed: 'danger',
    blocked: 'warning',
    skipped: 'info'
  }
  return typeMap[result] || 'info'
}

const getHistoryLabel = (result) => {
  const labelMap = {
    passed: '通过',
    failed: '失败',
    blocked: '阻塞',
    skipped: '跳过'
  }
  return labelMap[result] || result
}

const loadExecutionHistory = async () => {
  if (!props.showHistory) return

  historyLoading.value = true
  try {
    const response = await apiService.tests.getResultsByCase(props.caseId, {
      per_page: 10
    })
    executionHistory.value = response?.data || []
  } catch (error) {
    console.error('加载执行历史失败:', error)
  } finally {
    historyLoading.value = false
  }
}

watch(() => props.caseId, () => {
  if (props.showHistory) {
    loadExecutionHistory()
  }
})

onMounted(() => {
  if (props.showHistory) {
    loadExecutionHistory()
  }
})
</script>

<style scoped>
.test-case-result-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.badge-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.badge-icon {
  font-size: 14px;
}

.execute-time {
  margin-left: 4px;
  font-size: 12px;
  opacity: 0.7;
}

.history-link {
  margin-left: 4px;
  padding: 0;
}

.history-content {
  padding: 8px 0;
}

.history-content h4 {
  margin: 0 0 12px 0;
  padding: 0 12px;
  font-size: 14px;
  color: #303133;
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100px;
  color: #909399;
}

.history-list {
  padding: 0 12px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.history-item:last-child {
  border-bottom: none;
}

.history-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-executor {
  font-size: 12px;
  color: #606266;
}

.history-time {
  font-size: 12px;
  color: #909399;
}
</style>