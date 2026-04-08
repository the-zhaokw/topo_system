<template>
  <div class="stats-view">
    <div class="stats-header">
      <h3>数据概览</h3>
    </div>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ weeklyStats.tasks_completed || 0 }}</div>
          <div class="stat-label">本周完成</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatDuration(focusStats.total_minutes) }}</div>
          <div class="stat-label">专注时长</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ weeklyStats.completion_rate || 0 }}%</div>
          <div class="stat-label">完成率</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ focusStats.pomodoro_count || 0 }}</div>
          <div class="stat-label">番茄钟</div>
        </div>
      </div>
    </div>

    <div class="stats-charts">
      <div class="chart-card">
        <h4>每日完成趋势</h4>
        <div class="chart-placeholder">
          <div v-for="(day, index) in weekDays" :key="index" class="day-bar">
            <div class="bar" :style="{ height: getDayHeight(index) + '%' }" />
            <div class="day-label">{{ day }}</div>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <h4>时间分布</h4>
        <div class="quadrant-distribution">
          <div v-for="(value, key) in dailyStats.time_by_quadrant" :key="key" class="quadrant-item">
            <div class="quadrant-bar">
              <div
                class="bar-fill"
                :style="{
                  height: getQuadrantHeight(value) + '%',
                  background: getQuadrantColor(key)
                }"
              />
            </div>
            <div class="quadrant-label">{{ getQuadrantName(key) }}</div>
            <div class="quadrant-value">{{ value }}分钟</div>
          </div>
        </div>
      </div>
    </div>

    <div class="achievement-card">
      <div class="achievement-icon">🏆</div>
      <div class="achievement-content">
        <h4>本周成就</h4>
        <p>{{ weeklyStats.achievement || '开始记录任务，养成好习惯！' }}</p>
      </div>
    </div>

    <div class="weekly-summary">
      <h4>本周总结</h4>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="计划任务">{{ weeklyStats.tasks_total || 0 }}</el-descriptions-item>
        <el-descriptions-item label="完成任务">{{ weeklyStats.tasks_completed || 0 }}</el-descriptions-item>
        <el-descriptions-item label="逾期任务">{{ weeklyStats.tasks_overdue || 0 }}</el-descriptions-item>
        <el-descriptions-item label="完成率">{{ weeklyStats.completion_rate || 0 }}%</el-descriptions-item>
        <el-descriptions-item label="总专注">{{ formatDuration(weeklyStats.total_focus_minutes) }}</el-descriptions-item>
        <el-descriptions-item label="番茄钟">{{ focusStats.pomodoro_count || 0 }}个</el-descriptions-item>
      </el-descriptions>
    </div>

    <div class="type-breakdown" v-if="weeklyStats.by_type">
      <h4>分类统计</h4>
      <div class="type-list">
        <div v-for="(data, type) in weeklyStats.by_type" :key="type" class="type-item">
          <div class="type-info">
            <el-tag size="small">{{ type }}</el-tag>
            <span class="type-count">{{ data.completed }}/{{ data.total }}</span>
          </div>
          <el-progress
            :percentage="Math.round((data.completed / data.total) * 100) || 0"
            :stroke-width="8"
            :color="getTypeColor(type)"
          />
          <span class="type-time">{{ data.minutes }}分钟</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Clock, Timer, DataLine, TrendCharts } from '@element-plus/icons-vue'

const props = defineProps({
  dailyStats: {
    type: Object,
    default: () => ({})
  },
  weeklyStats: {
    type: Object,
    default: () => ({})
  },
  focusStats: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['refresh-daily', 'refresh-weekly'])

const weekDays = ['一', '二', '三', '四', '五', '六', '日']

const formatDuration = (minutes) => {
  if (!minutes) return '0分钟'
  if (minutes < 60) return `${minutes}分钟`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours}小时${mins}分` : `${hours}小时`
}

const getDayHeight = (index) => {
  const dailyStatsData = props.focusStats.daily_stats || {}
  const dayKeys = Object.keys(dailyStatsData).sort().slice(-7)
  const dayValue = dailyStatsData[dayKeys[index]]
  if (!dayValue) return 10
  const maxMinutes = Math.max(...Object.values(dailyStatsData).map(d => d.minutes), 1)
  return Math.max((dayValue.minutes / maxMinutes) * 80, 10)
}

const getQuadrantHeight = (value) => {
  if (!value) return 5
  const max = Math.max(...Object.values(props.dailyStats.time_by_quadrant || {}), 1)
  return Math.max((value / max) * 100, 5)
}

const getQuadrantColor = (quadrant) => {
  const colors = {
    1: '#f56c6c',
    2: '#e6a23c',
    3: '#409eff',
    4: '#67c23a'
  }
  return colors[quadrant] || '#909399'
}

const getQuadrantName = (quadrant) => {
  const names = {
    1: '紧急重要',
    2: '重要不紧急',
    3: '紧急不重要',
    4: '不紧急不重要'
  }
  return names[quadrant] || quadrant
}

const getTypeColor = (type) => {
  const colors = {
    work: '#409eff',
    study: '#67c23a',
    life: '#e6a23c',
    health: '#f56c6c'
  }
  return colors[type] || '#909399'
}
</script>

<style scoped>
.stats-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stats-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-card {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 20px;
}

.chart-card h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #606266;
}

.chart-placeholder {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 150px;
  padding-top: 20px;
}

.day-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  height: 100%;
}

.bar {
  width: 32px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
}

.day-label {
  font-size: 12px;
  color: #909399;
}

.quadrant-distribution {
  display: flex;
  justify-content: space-around;
  height: 150px;
  padding-top: 20px;
}

.quadrant-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.quadrant-bar {
  width: 40px;
  height: 120px;
  background: #e4e7ed;
  border-radius: 4px;
  display: flex;
  align-items: flex-end;
}

.bar-fill {
  width: 100%;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
}

.quadrant-label {
  font-size: 12px;
  color: #606266;
}

.quadrant-value {
  font-size: 11px;
  color: #909399;
}

.achievement-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  border-radius: 12px;
  color: #603800;
}

.achievement-icon {
  font-size: 48px;
}

.achievement-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.achievement-content p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.weekly-summary,
.type-breakdown {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 20px;
}

.weekly-summary h4,
.type-breakdown h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #606266;
}

.type-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.type-info {
  width: 100px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-count {
  font-size: 12px;
  color: #909399;
}

.type-item .el-progress {
  flex: 1;
}

.type-time {
  width: 60px;
  text-align: right;
  font-size: 12px;
  color: #909399;
}

@media screen and (max-width: 992px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-charts {
    grid-template-columns: 1fr;
  }
}

@media screen and (max-width: 576px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>