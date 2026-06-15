<template>
  <div class="plan-dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <h1>{{ greeting }}, {{ userName }}!</h1>
        <p class="date">{{ currentDate }}</p>
        <p class="motivation">{{ motivationQuote }}</p>
      </div>
      <div class="weather-widget" v-if="weather">
        <el-icon><Sunny /></el-icon>
        <span>{{ weather }}</span>
      </div>
    </div>

    <!-- 仪表盘网格 -->
    <div class="dashboard-grid">
      <!-- 今日三件事 -->
      <div class="dashboard-card top-tasks-card">
        <div class="card-header">
          <h3>今日三件事</h3>
          <el-button text size="small" @click="showAddTopTask = true">
            <el-icon><Plus /></el-icon>添加
          </el-button>
        </div>
        <div class="card-content">
          <div
            v-for="(task, index) in topTasks"
            :key="task.id"
            class="top-task-item"
            :class="{ completed: task.completed }"
          >
            <div class="task-drag-handle">
              <el-icon><Rank /></el-icon>
            </div>
            <el-checkbox
              :model-value="task.completed"
              @change="$emit('toggle-complete', task)"
            />
            <div class="task-info" @click="$emit('edit-task', task)">
              <span class="task-name" :class="{ completed: task.completed }">{{ task.title }}</span>
              <div class="task-meta">
                <span class="task-time" v-if="task.scheduled_time">
                  <el-icon><Clock /></el-icon>{{ task.scheduled_time }}
                </span>
                <span class="task-duration" v-if="task.estimated_minutes">
                  <el-icon><Timer /></el-icon>{{ task.estimated_minutes }}分钟
                </span>
              </div>
            </div>
            <div class="task-progress">
              <el-progress
                type="circle"
                :percentage="task.progress || 0"
                :width="36"
                :stroke-width="3"
                :status="task.completed ? 'success' : ''"
              />
            </div>
          </div>
          <el-empty v-if="topTasks.length === 0" description="暂无置顶任务" :image-size="60">
            <el-button size="small" @click="showAddTopTask = true">添加任务</el-button>
          </el-empty>
        </div>
      </div>

      <!-- 今日时间轴 -->
      <div class="dashboard-card timeline-card">
        <div class="card-header">
          <h3>今日时间轴</h3>
          <div class="time-scale">
            <el-button-group size="small">
              <el-button @click="timeScale = '30min'" :type="timeScale === '30min' ? 'primary' : ''">30分钟</el-button>
              <el-button @click="timeScale = '1hour'" :type="timeScale === '1hour' ? 'primary' : ''">1小时</el-button>
            </el-button-group>
          </div>
        </div>
        <div class="card-content timeline-content">
          <div class="timeline-track">
            <div
              v-for="hour in timelineHours"
              :key="hour"
              class="timeline-hour"
              :class="{ current: isCurrentHour(hour) }"
            >
              <span class="hour-label">{{ hour }}:00</span>
              <div class="hour-tasks">
                <div
                  v-for="task in getTasksForHour(hour)"
                  :key="task.id"
                  class="timeline-task"
                  :style="{ backgroundColor: getPriorityColor(task.priority) }"
                  @click="$emit('edit-task', task)"
                >
                  <span class="task-title">{{ task.title }}</span>
                  <span class="task-time" v-if="task.scheduled_time">{{ task.scheduled_time }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="unscheduled-area">
            <div class="unscheduled-header">
              <span>待排期任务</span>
              <span class="task-count">{{ unscheduledTasks.length }}</span>
            </div>
            <div class="unscheduled-list">
              <div
                v-for="task in unscheduledTasks.slice(0, 5)"
                :key="task.id"
                class="unscheduled-task"
                @click="$emit('edit-task', task)"
              >
                <span class="task-name">{{ task.title }}</span>
                <span class="task-duration" v-if="task.estimated_minutes">{{ task.estimated_minutes }}分钟</span>
              </div>
              <el-empty v-if="unscheduledTasks.length === 0" description="暂无待排期任务" :image-size="40" />
            </div>
          </div>
        </div>
      </div>

      <!-- 进度预警 -->
      <div class="dashboard-card warnings-card">
        <div class="card-header">
          <h3>进度预警</h3>
        </div>
        <div class="card-content warnings-content">
          <div class="warning-item overdue" @click="$emit('go-to-overdue')">
            <div class="warning-icon">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="warning-info">
              <span class="warning-count">{{ overdueTasks.length }}</span>
              <span class="warning-label">已超时任务</span>
            </div>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>

          <div class="warning-item at-risk" @click="$emit('go-to-at-risk')">
            <div class="warning-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="warning-info">
              <span class="warning-count">{{ atRiskTasks.length }}</span>
              <span class="warning-label">今日截止且进度&lt;50%</span>
            </div>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 快速复盘 -->
      <div class="dashboard-card quick-review-card">
        <div class="card-header">
          <h3>快速复盘</h3>
        </div>
        <div class="card-content">
          <p class="review-tip">记录今日已完成的工作</p>
          <el-button type="primary" @click="showReviewDialog = true" class="review-btn">
            <el-icon><Check /></el-icon>
            记录今日已完成
          </el-button>
          <div class="today-completed" v-if="todayCompleted.length > 0">
            <el-divider />
            <div class="completed-list">
              <div v-for="task in todayCompleted.slice(0, 5)" :key="task.id" class="completed-item">
                <el-icon><CircleCheck /></el-icon>
                <span class="completed-title">{{ task.title }}</span>
                <span class="actual-time" v-if="task.actual_minutes">{{ task.actual_minutes }}分钟</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 本周概览 -->
      <div class="dashboard-card stats-overview-card">
        <div class="card-header">
          <h3>本周概览</h3>
        </div>
        <div class="card-content stats-content">
          <div class="stat-item">
            <div class="stat-value">{{ weekStats.total }}</div>
            <div class="stat-label">计划任务</div>
          </div>
          <div class="stat-item">
            <div class="stat-value success">{{ weekStats.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-item">
            <div class="stat-value warning">{{ weekStats.inProgress || 0 }}</div>
            <div class="stat-label">进行中</div>
          </div>
          <div class="stat-item">
            <div class="stat-value danger">{{ weekStats.overdue || 0 }}</div>
            <div class="stat-label">已延期</div>
          </div>
          <div class="stat-item completion-rate">
            <el-progress
              type="circle"
              :percentage="weekStats.completionRate || 0"
              :width="70"
              :stroke-width="6"
            />
            <div class="stat-label">完成率</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加置顶任务弹窗 -->
    <el-dialog v-model="showAddTopTask" title="添加置顶任务" width="500px">
      <el-form :model="topTaskForm" label-width="100px">
        <el-form-item label="选择任务">
          <el-select v-model="topTaskForm.taskId" placeholder="请选择任务" filterable style="width: 100%">
            <el-option
              v-for="task in availableTasksForTop"
              :key="task.id"
              :label="task.title"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddTopTask = false">取消</el-button>
        <el-button type="primary" @click="addTopTask">确认</el-button>
      </template>
    </el-dialog>

    <!-- 复盘弹窗 -->
    <el-dialog v-model="showReviewDialog" title="记录今日完成" width="600px">
      <div class="review-content">
        <p class="review-desc">勾选今日已完成的任务：</p>
        <div class="review-task-list">
          <div
            v-for="task in reviewableTasks"
            :key="task.id"
            class="review-task-item"
          >
            <el-checkbox v-model="task.selected" />
            <span class="task-name">{{ task.title }}</span>
            <el-input-number
              v-if="task.selected"
              v-model="task.actualMinutes"
              :min="1"
              :max="480"
              size="small"
              style="width: 100px"
            />
            <span v-if="task.selected" class="unit">分钟</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button type="primary" @click="submitReview">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Sunny, Plus, Rank, Clock, Warning, ArrowRight, Check,
  CircleCheck, Timer
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const props = defineProps({
  topTasks: { type: Array, default: () => [] },
  unscheduledTasks: { type: Array, default: () => [] },
  todayCompleted: { type: Array, default: () => [] },
  overdueTasks: { type: Array, default: () => [] },
  atRiskTasks: { type: Array, default: () => [] },
  weekStats: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['refresh', 'toggle-complete', 'edit-task', 'go-to-overdue', 'go-to-at-risk'])

const userName = ref('用户')
const currentDate = ref('')
const weather = ref('晴 26°C')
const motivationQuote = ref('')

const timeScale = ref('30min')
const timelineHours = computed(() => {
  if (timeScale.value === '30min') {
    return Array.from({ length: 24 }, (_, i) => i)
  }
  return Array.from({ length: 15 }, (_, i) => i + 8) // 8:00 - 22:00
})

const showAddTopTask = ref(false)
const topTaskForm = ref({ taskId: null })
const availableTasksForTop = ref([])

const showReviewDialog = ref(false)
const reviewableTasks = ref([])

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const quotes = [
  '每一天都是新的开始，每一次努力都在靠近目标 💪',
  '保持专注，高效工作，今天的你很棒！',
  '小小的进步也是进步，继续加油！',
  '完成任务的感觉真好，继续保持！',
  '今日事今日毕，你是最棒的！'
]

const getPriorityColor = (priority) => {
  const colors = {
    urgent: '#f56c6c',
    high: '#e6a23c',
    medium: '#409EFF',
    low: '#67c23a'
  }
  return colors[priority] || '#909399'
}

const isCurrentHour = (hour) => {
  return new Date().getHours() === hour
}

const getTasksForHour = (hour) => {
  // 模拟根据小时获取任务
  return props.topTasks.filter(task => {
    if (!task.scheduled_time) return false
    const taskHour = parseInt(task.scheduled_time.split(':')[0])
    return taskHour === hour
  })
}

const addTopTask = async () => {
  if (!topTaskForm.value.taskId) {
    ElMessage.warning('请选择任务')
    return
  }
  // 这里应该调用API添加置顶任务
  ElMessage.success('已添加置顶任务')
  showAddTopTask.value = false
  emit('refresh')
}

const submitReview = async () => {
  const completedTasks = reviewableTasks.value.filter(t => t.selected)
  if (completedTasks.length === 0) {
    ElMessage.warning('请至少选择一个任务')
    return
  }

  try {
    for (const task of completedTasks) {
      await apiService.personalPlan.updateTask(task.id, {
        completed: true,
        actual_minutes: task.actualMinutes
      })
    }
    ElMessage.success('已记录今日完成')
    showReviewDialog.value = false
    emit('refresh')
  } catch (error) {
    ElMessage.error('记录失败')
  }
}

const loadAvailableTopTasks = async () => {
  try {
    const data = await apiService.personalPlan.getTasks({ status: 'todo' })
    availableTasksForTop.value = Array.isArray(data?.tasks) ? (data.tasks || []).filter(
      t => !props.topTasks.find(top => top.id === t.id)
    ) : []
  } catch (error) {
    console.error('加载任务失败:', error)
    availableTasksForTop.value = []
  }
}

const loadReviewableTasks = async () => {
  try {
    const data = await apiService.personalPlan.getTasks({
      date_from: new Date().toISOString().split('T')[0],
      status: 'in_progress'
    })
    reviewableTasks.value = Array.isArray(data?.tasks) ? data.tasks.map(t => ({
      ...t,
      selected: false,
      actualMinutes: t.estimated_minutes || 30
    })) : []
  } catch (error) {
    console.error('加载任务失败:', error)
    reviewableTasks.value = []
  }
}

onMounted(() => {
  const now = new Date()
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })

  motivationQuote.value = quotes[Math.floor(Math.random() * quotes.length)]

  // 获取用户信息
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  userName.value = userInfo.name || userInfo.username || '用户'

  loadAvailableTopTasks()
  loadReviewableTasks()
})
</script>

<style scoped>
.plan-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 16px;
  padding: 32px 40px;
  color: #fff;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(56, 189, 248, 0.3);
}

.welcome-content h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 600;
}

.date {
  margin: 0 0 8px 0;
  font-size: 16px;
  opacity: 0.9;
}

.motivation {
  margin: 0;
  font-size: 14px;
  opacity: 0.85;
}

.weather-widget {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.2);
  padding: 12px 20px;
  border-radius: 12px;
  font-size: 16px;
}

.weather-widget .el-icon {
  font-size: 24px;
}

/* 仪表盘网格 */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 20px;
}

.dashboard-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.3s;
}

.dashboard-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 卡片布局 */
.top-tasks-card {
  grid-column: span 5;
}

.timeline-card {
  grid-column: span 7;
}

.warnings-card {
  grid-column: span 4;
}

.quick-review-card {
  grid-column: span 4;
}

.stats-overview-card {
  grid-column: span 4;
}

/* 今日三件事 */
.top-task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: #f8f9fa;
  border-radius: 10px;
  margin-bottom: 10px;
  transition: all 0.2s;
  cursor: pointer;
}

.top-task-item:hover {
  background: #ecf5ff;
  transform: translateX(4px);
}

.top-task-item.completed {
  opacity: 0.7;
}

.top-task-item:last-child {
  margin-bottom: 0;
}

.task-drag-handle {
  color: #c0c4cc;
  cursor: grab;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  display: block;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-name.completed {
  text-decoration: line-through;
  color: #909399;
}

.task-meta {
  display: flex;
  gap: 12px;
}

.task-time, .task-duration {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-progress {
  flex-shrink: 0;
}

/* 时间轴 */
.timeline-content {
  display: flex;
  gap: 20px;
}

.timeline-track {
  flex: 1;
  max-height: 420px;
  overflow-y: auto;
}

.timeline-hour {
  display: flex;
  min-height: 50px;
  border-bottom: 1px solid #f0f0f0;
  padding: 4px 0;
}

.timeline-hour.current {
  background: #ecf5ff;
  border-radius: 6px;
}

.hour-label {
  width: 50px;
  font-size: 12px;
  color: #909399;
  padding: 4px 8px;
  flex-shrink: 0;
}

.hour-tasks {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 2px;
}

.timeline-task {
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  color: #fff;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline-task:hover {
  filter: brightness(1.1);
}

.timeline-task .task-time {
  color: rgba(255, 255, 255, 0.9);
  font-size: 11px;
}

.unscheduled-area {
  width: 200px;
  border-left: 1px solid #e6e6e6;
  padding-left: 16px;
  flex-shrink: 0;
}

.unscheduled-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.task-count {
  background: #f0f0f0;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  color: #909399;
}

.unscheduled-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 380px;
  overflow-y: auto;
}

.unscheduled-task {
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.unscheduled-task:hover {
  background: #ecf5ff;
}

.unscheduled-task .task-name {
  display: block;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #303133;
}

.unscheduled-task .task-duration {
  font-size: 11px;
  color: #909399;
}

/* 预警卡片 */
.warnings-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.warning-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.warning-item:hover {
  transform: translateX(4px);
}

.warning-item.overdue {
  background: #fef0f0;
}

.warning-item.at-risk {
  background: #fdf6ec;
}

.warning-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.warning-item.overdue .warning-icon {
  background: #f56c6c;
  color: #fff;
}

.warning-item.at-risk .warning-icon {
  background: #e6a23c;
  color: #fff;
}

.warning-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.warning-count {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.warning-label {
  font-size: 12px;
  color: #909399;
}

.arrow {
  color: #c0c4cc;
}

/* 快速复盘 */
.review-tip {
  color: #909399;
  font-size: 14px;
  margin: 0 0 16px 0;
}

.review-btn {
  width: 100%;
  border-radius: 8px;
}

.today-completed {
  margin-top: 16px;
}

.completed-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.completed-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #67c23a;
  padding: 8px 12px;
  background: #f0f9eb;
  border-radius: 6px;
}

.completed-item .el-icon {
  color: #67c23a;
  font-size: 16px;
}

.completed-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actual-time {
  margin-left: auto;
  font-size: 11px;
  color: #909399;
}

/* 统计概览 */
.stats-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 10px;
}

.stat-item.completion-rate {
  grid-column: span 3;
  background: transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.warning {
  color: #e6a23c;
}

.stat-value.danger {
  color: #f56c6c;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 复盘弹窗 */
.review-content {
  padding: 0 8px;
}

.review-desc {
  color: #606266;
  margin-bottom: 16px;
}

.review-task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.review-task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: #f8f9fa;
  border-radius: 8px;
}

.review-task-item .task-name {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.review-task-item .unit {
  font-size: 13px;
  color: #909399;
}

/* 响应式 */
@media screen and (max-width: 1200px) {
  .top-tasks-card,
  .timeline-card {
    grid-column: span 12;
  }

  .warnings-card,
  .quick-review-card,
  .stats-overview-card {
    grid-column: span 6;
  }
}

@media screen and (max-width: 768px) {
  .welcome-banner {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 24px;
  }

  .welcome-content h1 {
    font-size: 24px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .top-tasks-card,
  .timeline-card,
  .warnings-card,
  .quick-review-card,
  .stats-overview-card {
    grid-column: span 1;
  }

  .timeline-content {
    flex-direction: column;
  }

  .unscheduled-area {
    width: 100%;
    border-left: none;
    border-top: 1px solid #e6e6e6;
    padding-left: 0;
    padding-top: 16px;
  }

  .stats-content {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-item.completion-rate {
    grid-column: span 2;
  }
}
</style>
