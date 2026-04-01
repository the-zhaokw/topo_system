<template>
  <div class="execution-progress">
    <div class="progress-header">
      <div class="progress-stats">
        <div class="stat-item">
          <span class="stat-label">总用例</span>
          <span class="stat-value total">{{ total }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">已完成</span>
          <span class="stat-value completed">{{ completed }}</span>
        </div>
        <div class="stat-item passed">
          <span class="stat-label">通过</span>
          <span class="stat-value">{{ passed }}</span>
        </div>
        <div class="stat-item failed">
          <span class="stat-label">失败</span>
          <span class="stat-value">{{ failed }}</span>
        </div>
        <div class="stat-item blocked">
          <span class="stat-label">阻塞</span>
          <span class="stat-value">{{ blocked }}</span>
        </div>
        <div class="stat-item skipped">
          <span class="stat-label">跳过</span>
          <span class="stat-value">{{ skipped }}</span>
        </div>
      </div>
      <div class="progress-rate" v-if="total > 0">
        <span class="rate-value" :style="{ color: rateColor }">{{ passRate }}%</span>
        <span class="rate-label">通过率</span>
      </div>
    </div>

    <div class="progress-bar-container">
      <el-progress
        :percentage="progressPercentage"
        :color="progressColor"
        :stroke-width="progressStrokeWidth"
        :show-text="showPercentage"
      />
    </div>

    <div v-if="showDetails" class="progress-details">
      <div class="detail-bar">
        <div
          class="detail-segment passed"
          :style="{ width: passedPercentage + '%' }"
          :title="`通过: ${passed}`"
        ></div>
        <div
          class="detail-segment failed"
          :style="{ width: failedPercentage + '%' }"
          :title="`失败: ${failed}`"
        ></div>
        <div
          class="detail-segment blocked"
          :style="{ width: blockedPercentage + '%' }"
          :title="`阻塞: ${blocked}`"
        ></div>
        <div
          class="detail-segment skipped"
          :style="{ width: skippedPercentage + '%' }"
          :title="`跳过: ${skipped}`"
        ></div>
        <div
          class="detail-segment pending"
          :style="{ width: pendingPercentage + '%' }"
          :title="`待执行: ${pending}`"
        ></div>
      </div>
      <div class="detail-legend">
        <span class="legend-item"><span class="dot passed"></span>通过 {{ passed }} ({{ passedPercentage }}%)</span>
        <span class="legend-item"><span class="dot failed"></span>失败 {{ failed }} ({{ failedPercentage }}%)</span>
        <span class="legend-item"><span class="dot blocked"></span>阻塞 {{ blocked }} ({{ blockedPercentage }}%)</span>
        <span class="legend-item"><span class="dot skipped"></span>跳过 {{ skipped }} ({{ skippedPercentage }}%)</span>
        <span class="legend-item"><span class="dot pending"></span>待执行 {{ pending }} ({{ pendingPercentage }}%)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: {
    type: Number,
    default: 0
  },
  passed: {
    type: Number,
    default: 0
  },
  failed: {
    type: Number,
    default: 0
  },
  blocked: {
    type: Number,
    default: 0
  },
  skipped: {
    type: Number,
    default: 0
  },
  showDetails: {
    type: Boolean,
    default: true
  },
  showPercentage: {
    type: Boolean,
    default: true
  },
  progressStrokeWidth: {
    type: Number,
    default: 12
  }
})

const completed = computed(() => {
  return props.passed + props.failed + props.blocked + props.skipped
})

const pending = computed(() => {
  return Math.max(0, props.total - completed.value)
})

const progressPercentage = computed(() => {
  if (props.total === 0) return 0
  return Math.round((completed.value / props.total) * 100)
})

const passRate = computed(() => {
  if (completed.value === 0) return 0
  return ((props.passed / completed.value) * 100).toFixed(1)
})

const rateColor = computed(() => {
  const rate = parseFloat(passRate.value)
  if (rate >= 80) return '#67C23A'
  if (rate >= 60) return '#E6A23C'
  return '#F56C6C'
})

const progressColor = computed(() => {
  const rate = parseFloat(passRate.value)
  if (rate >= 80) return '#67C23A'
  if (rate >= 60) return '#E6A23C'
  return '#F56C6C'
})

const passedPercentage = computed(() => {
  if (props.total === 0) return 0
  return ((props.passed / props.total) * 100).toFixed(1)
})

const failedPercentage = computed(() => {
  if (props.total === 0) return 0
  return ((props.failed / props.total) * 100).toFixed(1)
})

const blockedPercentage = computed(() => {
  if (props.total === 0) return 0
  return ((props.blocked / props.total) * 100).toFixed(1)
})

const skippedPercentage = computed(() => {
  if (props.total === 0) return 0
  return ((props.skipped / props.total) * 100).toFixed(1)
})

const pendingPercentage = computed(() => {
  if (props.total === 0) return 0
  return ((pending.value / props.total) * 100).toFixed(1)
})
</script>

<style scoped>
.execution-progress {
  width: 100%;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.stat-item.passed .stat-value {
  color: #67C23A;
}

.stat-item.failed .stat-value {
  color: #F56C6C;
}

.stat-item.blocked .stat-value {
  color: #E6A23C;
}

.stat-item.skipped .stat-value {
  color: #909399;
}

.progress-rate {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.rate-value {
  font-size: 28px;
  font-weight: bold;
}

.rate-label {
  font-size: 12px;
  color: #909399;
}

.progress-bar-container {
  margin-bottom: 16px;
}

.progress-details {
  margin-top: 12px;
}

.detail-bar {
  display: flex;
  height: 24px;
  border-radius: 4px;
  overflow: hidden;
  background: #f5f7fa;
}

.detail-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.detail-segment.passed {
  background: #67C23A;
}

.detail-segment.failed {
  background: #F56C6C;
}

.detail-segment.blocked {
  background: #E6A23C;
}

.detail-segment.skipped {
  background: #909399;
}

.detail-segment.pending {
  background: #DCDFE6;
}

.detail-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
}

.legend-item .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-item .dot.passed {
  background: #67C23A;
}

.legend-item .dot.failed {
  background: #F56C6C;
}

.legend-item .dot.blocked {
  background: #E6A23C;
}

.legend-item .dot.skipped {
  background: #909399;
}

.legend-item .dot.pending {
  background: #DCDFE6;
}
</style>