<template>
  <div class="focus-view">
    <div class="focus-main" :class="{ 'focus-active': isFocusActive }">
      <div class="focus-timer">
        <div class="timer-display">
          <span class="timer-minutes">{{ displayMinutes }}</span>
          <span class="timer-separator">:</span>
          <span class="timer-seconds">{{ displaySeconds }}</span>
        </div>
        <div class="timer-status">
          <el-tag v-if="isFocusActive" type="success" size="large">专注中</el-tag>
          <el-tag v-else type="info" size="large">等待开始</el-tag>
        </div>
      </div>

      <div class="focus-task" v-if="currentTask">
        <div class="task-label">当前任务</div>
        <div class="task-name">{{ currentTask.title }}</div>
      </div>
      <div class="focus-task" v-else>
        <div class="task-label">未选择任务</div>
        <div class="task-name">点击下方按钮选择一个任务</div>
      </div>

      <div class="focus-controls">
        <el-button
          v-if="!isFocusActive"
          type="primary"
          size="large"
          @click="handleStartFocus"
        >
          开始专注
        </el-button>
        <el-button
          v-else
          type="danger"
          size="large"
          @click="handleEndFocus(false)"
        >
          结束专注
        </el-button>
      </div>

      <div class="focus-options">
        <div class="option-label">专注时长</div>
        <el-radio-group v-model="focusDuration" size="large">
          <el-radio-button :value="25">25分钟</el-radio-button>
          <el-radio-button :value="45">45分钟</el-radio-button>
          <el-radio-button :value="60">60分钟</el-radio-button>
          <el-radio-button :value="90">90分钟</el-radio-button>
        </el-radio-group>
      </div>

      <div class="session-counter">
        <span class="counter-label">今日专注</span>
        <span class="counter-value">{{ focusStats.total_minutes || 0 }} 分钟</span>
        <span class="counter-label">专注次数</span>
        <span class="counter-value">{{ focusStats.total_sessions || 0 }} 次</span>
      </div>
    </div>

    <div class="focus-sidebar">
      <h4>选择任务</h4>
      <div class="task-selector">
        <el-input
          v-model="taskSearch"
          placeholder="搜索任务..."
          prefix-icon="Search"
          clearable
        />
      </div>
      <div class="task-list">
        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="task-item"
          :class="{ selected: currentTask?.id === task.id }"
          @click="handleSelectTask(task)"
        >
          <div class="task-priority" :class="task.priority" />
          <div class="task-info">
            <div class="task-title">{{ task.title }}</div>
            <div class="task-meta" v-if="task.quadrant">
              象限{{ task.quadrant }}
            </div>
          </div>
        </div>
        <el-empty v-if="filteredTasks.length === 0" description="暂无任务" />
      </div>
    </div>

    <el-dialog v-model="breakDialogVisible" title="休息一下" width="400px" :close-on-click-modal="false">
      <div class="break-content">
        <div class="break-message">
          <span class="break-emoji">☕</span>
          <p>太棒了！你完成了一个专注周期。</p>
          <p>休息 {{ breakDuration }} 分钟，让大脑放松一下。</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="skipBreak">跳过休息</el-button>
        <el-button type="primary" @click="startBreak">开始休息</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="restAlertVisible" title="休息提醒" width="400px">
      <div class="rest-alert-content">
        <div class="rest-emoji">⚠️</div>
        <p>你已经连续工作超过1小时了！</p>
        <p>建议休息5-10分钟，保护眼睛和身体。</p>
      </div>
      <template #footer>
        <el-button @click="restAlertVisible = false">继续工作</el-button>
        <el-button type="warning" @click="handleTakeRest">休息一下</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { apiService } from '@/services/api'

const props = defineProps({
  currentTask: Object,
  focusSession: Object,
  settings: Object
})

const emit = defineEmits(['start-focus', 'end-focus', 'select-task'])

const focusDuration = ref(25)
const remainingSeconds = ref(25 * 60)
const isFocusActive = ref(false)
const timerInterval = ref(null)
const focusStats = ref({})
const taskSearch = ref('')
const allTasks = ref([])

const breakDialogVisible = ref(false)
const breakDuration = ref(5)
const restAlertVisible = ref(false)
const workStartTime = ref(null)

const displayMinutes = computed(() => {
  return String(Math.floor(remainingSeconds.value / 60)).padStart(2, '0')
})

const displaySeconds = computed(() => {
  return String(remainingSeconds.value % 60).padStart(2, '0')
})

const filteredTasks = computed(() => {
  if (!allTasks.value || !Array.isArray(allTasks.value)) return []
  if (!taskSearch.value) return allTasks.value
  const keyword = taskSearch.value.toLowerCase()
  return allTasks.value.filter(t => t.title.toLowerCase().includes(keyword))
})

const handleStartFocus = () => {
  emit('start-focus', {
    taskId: props.currentTask?.id,
    focusType: 'pomodoro',
    duration: focusDuration.value
  })

  isFocusActive.value = true
  remainingSeconds.value = focusDuration.value * 60
  workStartTime.value = new Date()

  timerInterval.value = setInterval(() => {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--

      if (remainingSeconds.value === 0) {
        handleFocusComplete()
      }

      const workedMinutes = (new Date() - workStartTime.value) / 60000
      if (workedMinutes >= 60 && workedMinutes % 60 < 1) {
        restAlertVisible.value = true
      }
    }
  }, 1000)
}

const handleEndFocus = (completed = true) => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }

  emit('end-focus', completed)

  isFocusActive.value = false
  remainingSeconds.value = focusDuration.value * 60
}

const handleFocusComplete = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }

  isFocusActive.value = false
  breakDialogVisible.value = true
  ElMessage.success('恭喜完成一个专注周期！')
}

const startBreak = () => {
  breakDialogVisible.value = false
  remainingSeconds.value = breakDuration.value * 60

  timerInterval.value = setInterval(() => {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--
    } else {
      clearInterval(timerInterval.value)
      timerInterval.value = null
      ElMessage.success('休息结束，开始新的专注吧！')
      remainingSeconds.value = focusDuration.value * 60
    }
  }, 1000)
}

const skipBreak = () => {
  breakDialogVisible.value = false
  remainingSeconds.value = focusDuration.value * 60
}

const handleTakeRest = () => {
  restAlertVisible.value = false
  breakDuration.value = 10
  startBreak()
}

const handleSelectTask = (task) => {
  emit('select-task', task)
}

const fetchTasks = async () => {
  try {
    const data = await apiService.personalPlan.getTasks({
      status: 'active'
    })
    allTasks.value = Array.isArray(data?.tasks) ? data.tasks : []
  } catch (error) {
    console.error('获取任务失败:', error)
    allTasks.value = []
  }
}

const fetchFocusStats = async () => {
  try {
    const data = await apiService.personalPlan.getFocusStats(1)
    focusStats.value = data || {}
  } catch (error) {
    console.error('获取专注统计失败:', error)
  }
}

onMounted(() => {
  fetchTasks()
  fetchFocusStats()
})

onUnmounted(() => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
})
</script>

<style scoped>
.focus-view {
  display: flex;
  gap: 24px;
  height: 100%;
}

.focus-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  transition: all 0.3s;
}

.focus-main.focus-active {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.focus-timer {
  text-align: center;
  margin-bottom: 32px;
}

.timer-display {
  font-size: 96px;
  font-weight: 300;
  font-family: 'Roboto Mono', monospace;
  letter-spacing: 4px;
}

.timer-separator {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}

.timer-status {
  margin-top: 16px;
}

.focus-task {
  text-align: center;
  margin-bottom: 32px;
}

.task-label {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 8px;
}

.task-name {
  font-size: 20px;
  font-weight: 500;
}

.focus-controls {
  margin-bottom: 32px;
}

.focus-controls .el-button {
  width: 160px;
  height: 48px;
  font-size: 16px;
}

.focus-options {
  text-align: center;
  margin-bottom: 32px;
}

.option-label {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 12px;
}

.session-counter {
  display: flex;
  gap: 24px;
  font-size: 14px;
}

.counter-label {
  opacity: 0.8;
}

.counter-value {
  font-weight: 500;
  margin-left: 4px;
}

.focus-sidebar {
  width: 300px;
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.focus-sidebar h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.task-selector {
  margin-bottom: 12px;
}

.task-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.task-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.task-item.selected {
  border: 2px solid #409eff;
  background: #ecf5ff;
}

.task-priority {
  width: 4px;
  height: 32px;
  border-radius: 2px;
}

.task-priority.urgent {
  background: #f56c6c;
}

.task-priority.high {
  background: #e6a23c;
}

.task-priority.medium {
  background: #409eff;
}

.task-priority.low {
  background: #909399;
}

.task-info {
  flex: 1;
}

.task-title {
  font-size: 14px;
  color: #303133;
}

.task-meta {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.break-content,
.rest-alert-content {
  text-align: center;
  padding: 20px;
}

.break-emoji,
.rest-emoji {
  font-size: 48px;
  margin-bottom: 16px;
}

.break-message p,
.rest-alert-content p {
  margin: 8px 0;
  color: #606266;
}

@media screen and (max-width: 768px) {
  .focus-view {
    flex-direction: column;
  }

  .focus-sidebar {
    width: 100%;
  }

  .timer-display {
    font-size: 64px;
  }

  .focus-main {
    padding: 24px;
  }
}
</style>