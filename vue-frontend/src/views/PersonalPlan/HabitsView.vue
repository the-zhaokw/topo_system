<template>
  <div class="habits-view">
    <div class="habits-header">
      <h3>习惯追踪</h3>
      <div class="streak-info">
        <span class="streak-icon">🔥</span>
        <span class="streak-label">最长连续:</span>
        <span class="streak-value">{{ maxStreak }} 天</span>
      </div>
    </div>

    <div class="habits-list">
      <div v-for="habit in habits" :key="habit.task.id" class="habit-card">
        <div class="habit-header">
          <div class="habit-title">
            <span class="habit-name">{{ habit.task.title }}</span>
            <el-tag v-if="habit.streak > 0" type="warning" size="small">
              🔥 {{ habit.streak }}天连续
            </el-tag>
          </div>
          <div class="habit-actions">
            <el-button
              size="small"
              type="primary"
              @click="handleCheckIn(habit.task.id)"
              :disabled="hasCheckedInToday(habit)"
            >
              {{ hasCheckedInToday(habit) ? '已打卡' : '打卡' }}
            </el-button>
          </div>
        </div>

        <div class="habit-calendar">
          <div class="calendar-header">
            <span v-for="day in ['日', '一', '二', '三', '四', '五', '六']" :key="day" class="day-label">
              {{ day }}
            </span>
          </div>
          <div class="calendar-grid">
            <div
              v-for="(date, index) in getMonthDates()"
              :key="index"
              class="calendar-day"
              :class="{
                checked: isDateChecked(habit.records, date),
                today: isToday(date)
              }"
            >
              <span class="day-number">{{ date.getDate() }}</span>
            </div>
          </div>
        </div>

        <div class="habit-stats">
          <div class="stat-item">
            <span class="stat-value">{{ habit.total_completions }}</span>
            <span class="stat-label">总打卡</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ habit.streak }}</span>
            <span class="stat-label">当前连续</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ habit.task.estimated_minutes || 30 }}</span>
            <span class="stat-label">分钟/次</span>
          </div>
        </div>
      </div>

      <el-empty v-if="habits.length === 0" description="还没有习惯，创建一个吧！">
        <template #image>
          <el-icon :size="60" color="#909399"><CircleCheck /></el-icon>
        </template>
        <el-button type="primary" @click="$emit('create')">创建习惯</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CircleCheck } from '@element-plus/icons-vue'

const props = defineProps({
  habits: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['refresh', 'check-in'])

const maxStreak = computed(() => {
  if (props.habits.length === 0) return 0
  return Math.max(...props.habits.map(h => h.streak), 0)
})

const getMonthDates = () => {
  const dates = []
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)

  const startPadding = firstDay.getDay()
  for (let i = 0; i < startPadding; i++) {
    const date = new Date(firstDay)
    date.setDate(date.getDate() - (startPadding - i))
    dates.push(date)
  }

  for (let d = 1; d <= lastDay.getDate(); d++) {
    dates.push(new Date(today.getFullYear(), today.getMonth(), d))
  }

  const endPadding = 42 - dates.length
  for (let i = 1; i <= endPadding; i++) {
    const date = new Date(lastDay)
    date.setDate(date.getDate() + i)
    dates.push(date)
  }

  return dates
}

const isDateChecked = (records, date) => {
  if (!records || records.length === 0) return false
  const dateStr = date.toISOString().split('T')[0]
  return records.some(r => r.completed_date === dateStr)
}

const isToday = (date) => {
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

const hasCheckedInToday = (habit) => {
  if (!habit.records || habit.records.length === 0) return false
  const today = new Date().toISOString().split('T')[0]
  return habit.records.some(r => r.completed_date === today)
}

const handleCheckIn = (taskId) => {
  emit('check-in', taskId, 30)
}
</script>

<style scoped>
.habits-view {
  height: 100%;
}

.habits-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.habits-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.streak-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  border-radius: 20px;
  color: #603800;
}

.streak-icon {
  font-size: 20px;
}

.streak-label {
  font-size: 14px;
}

.streak-value {
  font-size: 16px;
  font-weight: 600;
}

.habits-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.habit-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.habit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.habit-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.habit-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.habit-calendar {
  margin-bottom: 16px;
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.day-label {
  text-align: center;
  font-size: 12px;
  color: #909399;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-size: 12px;
  color: #c0c4cc;
  background: #f5f7fa;
}

.calendar-day.checked {
  background: #67c23a;
  color: white;
}

.calendar-day.today {
  border: 2px solid #409eff;
  font-weight: 600;
}

.calendar-day.today.checked {
  background: #67c23a;
  border-color: #67c23a;
}

.day-number {
  line-height: 1;
}

.habit-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

@media screen and (max-width: 768px) {
  .habits-list {
    grid-template-columns: 1fr;
  }
}
</style>