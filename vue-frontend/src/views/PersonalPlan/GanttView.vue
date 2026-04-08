<template>
  <div class="gantt-view">
    <div class="gantt-toolbar">
      <div class="toolbar-left">
        <el-radio-group v-model="timeScale" size="default">
          <el-radio-button value="day">日</el-radio-button>
          <el-radio-button value="week">周</el-radio-button>
          <el-radio-button value="month">月</el-radio-button>
        </el-radio-group>

        <el-slider
          v-model="zoomLevel"
          :min="1"
          :max="5"
          :step="1"
          :show-tooltip="false"
          class="zoom-slider"
        />
        <span class="zoom-label">缩放</span>

        <el-switch
          v-model="showDependencies"
          active-text="依赖线"
          inactive-text=""
        />

        <el-switch
          v-model="showBaseline"
          active-text="基线"
          inactive-text=""
        />
      </div>

      <div class="toolbar-right">
        <el-button @click="saveBaseline" type="primary" plain>
          <el-icon><Document /></el-icon>
          保存基线
        </el-button>
        <el-button @click="exportGantt" type="default">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <div class="gantt-container">
      <div class="gantt-sidebar">
        <div class="sidebar-header">
          <span>任务名称</span>
          <span>负责人</span>
        </div>
        <div class="sidebar-content">
          <div
            v-for="task in ganttTasks"
            :key="task.id"
            class="task-row"
            :class="{ selected: selectedTask?.id === task.id }"
            @click="selectTask(task)"
          >
            <div class="task-name">
              <span class="task-priority" :class="task.priority"></span>
              <span class="task-title">{{ task.title }}</span>
            </div>
            <div class="task-owner">
              <el-avatar :size="24" :src="task.ownerAvatar" />
            </div>
          </div>
        </div>
      </div>

      <div class="gantt-chart" ref="chartRef">
        <div class="chart-header">
          <div
            v-for="date in headerDates"
            :key="date.key"
            class="header-cell"
            :style="{ width: cellWidth + 'px' }"
          >
            {{ date.label }}
          </div>
        </div>

        <div class="chart-body" ref="chartBodyRef">
          <div
            v-for="task in ganttTasks"
            :key="task.id"
            class="chart-row"
            :class="{ selected: selectedTask?.id === task.id }"
          >
            <div
              v-for="date in headerDates"
              :key="date.key"
              class="chart-cell"
              :style="{ width: cellWidth + 'px' }"
              :class="{ today: isToday(date.key) }"
              @click="handleCellClick(task, date)"
            ></div>

            <div
              v-if="task.start_date && task.due_date"
              class="task-bar"
              :class="[task.priority, { dragging: draggingTask?.id === task.id }]"
              :style="getTaskBarStyle(task)"
              draggable="true"
              @dragstart="onBarDragStart($event, task)"
              @drag="onBarDrag"
              @dragend="onBarDragEnd(task, $event)"
              @click.stop="selectTask(task)"
              @mouseenter="showTaskDetail(task, $event)"
              @mouseleave="hideTaskDetail"
            >
              <div class="bar-progress" :style="{ width: (task.progress || 0) + '%' }"></div>
              <span class="bar-label">{{ task.title }}</span>
              <span class="bar-progress-text">{{ task.progress || 0 }}%</span>
            </div>

            <div
              v-if="showBaseline && task.baseline"
              class="task-baseline"
              :style="getBaselineStyle(task)"
            ></div>

            <svg v-if="showDependencies" class="dependency-lines">
              <line
                v-for="dep in getTaskDependencies(task)"
                :key="dep.id"
                :x1="dep.startX"
                :y1="dep.startY"
                :x2="dep.endX"
                :y2="dep.endY"
                class="dependency-line"
              />
            </svg>
          </div>

          <div class="today-line" :style="{ left: todayPosition + 'px' }"></div>
        </div>
      </div>
    </div>

    <div
      v-if="taskDetailVisible"
      class="task-detail-popover"
      :style="{ left: popoverPosition.x + 'px', top: popoverPosition.y + 'px' }"
    >
      <div class="popover-header">
        <h4>{{ taskDetail.title }}</h4>
        <el-tag :type="getPriorityType(taskDetail.priority)" size="small">
          {{ getPriorityText(taskDetail.priority) }}
        </el-tag>
      </div>
      <div class="popover-content">
        <div class="detail-row">
          <span class="label">开始时间：</span>
          <span class="value">{{ taskDetail.start_date || '未设置' }}</span>
        </div>
        <div class="detail-row">
          <span class="label">截止时间：</span>
          <span class="value">{{ taskDetail.due_date || '未设置' }}</span>
        </div>
        <div class="detail-row">
          <span class="label">进度：</span>
          <span class="value">{{ taskDetail.progress || 0 }}%</span>
        </div>
        <div class="detail-row" v-if="taskDetail.dependencies?.length">
          <span class="label">前置任务：</span>
          <span class="value">{{ getDependencyNames(taskDetail) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Download } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const timeScale = ref('week')
const zoomLevel = ref(3)
const showDependencies = ref(true)
const showBaseline = ref(false)

const chartRef = ref(null)
const chartBodyRef = ref(null)

const ganttTasks = ref([])
const selectedTask = ref(null)
const taskDetail = ref({})
const taskDetailVisible = ref(false)
const popoverPosition = reactive({ x: 0, y: 0 })
const draggingTask = ref(null)
const todayPosition = ref(0)

const cellWidth = computed(() => {
  const widths = { day: 40, week: 120, month: 180 }
  return (widths[timeScale.value] || 120) * zoomLevel.value
})

const headerDates = computed(() => {
  const dates = []
  const now = new Date()
  let startDate, endDate, labelFormat

  if (timeScale.value === 'day') {
    startDate = new Date(now.getFullYear(), now.getMonth(), 1)
    endDate = new Date(now.getFullYear(), now.getMonth() + 2, 0)
    labelFormat = { day: 'numeric', month: 'short' }
  } else if (timeScale.value === 'week') {
    startDate = new Date(now.getFullYear(), now.getMonth(), 1)
    endDate = new Date(now.getFullYear(), now.getMonth() + 3, 0)
    labelFormat = { day: 'numeric', month: 'short' }
  } else {
    startDate = new Date(now.getFullYear(), 0, 1)
    endDate = new Date(now.getFullYear() + 1, 0, 0)
    labelFormat = { month: 'long' }
  }

  const current = new Date(startDate)
  while (current <= endDate) {
    const key = current.toISOString().split('T')[0]
    let label
    if (timeScale.value === 'day') {
      label = `${current.getMonth() + 1}月${current.getDate()}日`
    } else if (timeScale.value === 'week') {
      label = `${current.getMonth() + 1}/${current.getDate()}`
    } else {
      label = `${current.getFullYear()}年${current.getMonth() + 1}月`
    }
    dates.push({ key, label })
    current.setDate(current.getDate() + (timeScale.value === 'day' ? 1 : timeScale.value === 'week' ? 7 : 30))
  }

  return dates
})

const getTaskBarStyle = (task) => {
  if (!task.start_date || !task.due_date) return {}

  const startDate = new Date(task.start_date)
  const endDate = new Date(task.due_date)
  const now = new Date()

  let left = 0
  let width = 0

  const firstDate = new Date(headerDates.value[0]?.key)
  if (firstDate && startDate >= firstDate) {
    const daysDiff = Math.floor((startDate - firstDate) / (1000 * 60 * 60 * 24))
    if (timeScale.value === 'day') {
      left = daysDiff * cellWidth.value
    } else if (timeScale.value === 'week') {
      left = Math.floor(daysDiff / 7) * cellWidth.value
    } else {
      left = Math.floor(daysDiff / 30) * cellWidth.value
    }
  }

  const durationDays = Math.floor((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1
  if (timeScale.value === 'day') {
    width = durationDays * cellWidth.value
  } else if (timeScale.value === 'week') {
    width = Math.ceil(durationDays / 7) * cellWidth.value
  } else {
    width = Math.ceil(durationDays / 30) * cellWidth.value
  }

  const rowIndex = ganttTasks.value.indexOf(task)
  const rowHeight = 48
  const top = rowIndex * rowHeight

  return {
    left: left + 'px',
    width: Math.max(width, 30) + 'px',
    top: top + 'px',
    height: '32px'
  }
}

const getBaselineStyle = (task) => {
  if (!task.baseline) return {}

  const baselineStart = new Date(task.baseline.start_date)
  const baselineEnd = new Date(task.baseline.due_date)
  const firstDate = new Date(headerDates.value[0]?.key)

  let left = 0
  let width = 0

  if (firstDate && baselineStart >= firstDate) {
    const daysDiff = Math.floor((baselineStart - firstDate) / (1000 * 60 * 60 * 24))
    if (timeScale.value === 'day') {
      left = daysDiff * cellWidth.value
    } else if (timeScale.value === 'week') {
      left = Math.floor(daysDiff / 7) * cellWidth.value
    } else {
      left = Math.floor(daysDiff / 30) * cellWidth.value
    }
  }

  const durationDays = Math.floor((baselineEnd - baselineStart) / (1000 * 60 * 60 * 24)) + 1
  if (timeScale.value === 'day') {
    width = durationDays * cellWidth.value
  } else if (timeScale.value === 'week') {
    width = Math.ceil(durationDays / 7) * cellWidth.value
  } else {
    width = Math.ceil(durationDays / 30) * cellWidth.value
  }

  const rowIndex = ganttTasks.value.indexOf(task)
  const rowHeight = 48
  const top = rowIndex * rowHeight

  return {
    left: left + 'px',
    width: Math.max(width, 30) + 'px',
    top: (top + 8) + 'px',
    height: '16px'
  }
}

const getTaskDependencies = (task) => {
  const dependencies = []
  if (!task.dependencies?.length) return dependencies

  const rowHeight = 48
  const rowIndex = ganttTasks.value.indexOf(task)

  for (const depId of task.dependencies) {
    const depTask = ganttTasks.value.find(t => t.id === depId)
    if (depTask && depTask.due_date) {
      const depIndex = ganttTasks.value.indexOf(depTask)
      const depEnd = new Date(depTask.due_date)

      let depX = 0
      const firstDate = new Date(headerDates.value[0]?.key)
      if (firstDate && depEnd >= firstDate) {
        const daysDiff = Math.floor((depEnd - firstDate) / (1000 * 60 * 60 * 24))
        if (timeScale.value === 'day') {
          depX = daysDiff * cellWidth.value + cellWidth.value
        } else if (timeScale.value === 'week') {
          depX = Math.floor(daysDiff / 7) * cellWidth.value + cellWidth.value
        } else {
          depX = Math.floor(daysDiff / 30) * cellWidth.value + cellWidth.value
        }
      }

      const startX = 0
      const startY = rowIndex * rowHeight + 24
      const endX = depX
      const endY = depIndex * rowHeight + 24

      dependencies.push({ id: depId, startX, startY, endX, endY })
    }
  }

  return dependencies
}

const isToday = (dateKey) => {
  const today = new Date().toISOString().split('T')[0]
  return dateKey === today
}

const getPriorityType = (priority) => {
  const types = { urgent: 'danger', high: 'warning', medium: 'primary', low: 'success' }
  return types[priority] || 'info'
}

const getPriorityText = (priority) => {
  const texts = { urgent: '紧急', high: '高', medium: '中', low: '低' }
  return texts[priority] || '未知'
}

const getDependencyNames = (task) => {
  if (!task.dependencies?.length) return ''
  return task.dependencies
    .map(id => ganttTasks.value.find(t => t.id === id)?.title)
    .filter(Boolean)
    .join(', ')
}

const selectTask = (task) => {
  selectedTask.value = task
}

const showTaskDetail = (task, event) => {
  taskDetail.value = task
  taskDetailVisible.value = true

  const rect = event.target.getBoundingClientRect()
  popoverPosition.x = rect.right + 10
  popoverPosition.y = rect.top
}

const hideTaskDetail = () => {
  taskDetailVisible.value = false
}

const onBarDragStart = (event, task) => {
  draggingTask.value = task
  event.dataTransfer.effectAllowed = 'move'
}

const onBarDrag = (event) => {
}

const onBarDragEnd = async (task, event) => {
  if (!draggingTask.value) return

  const chartRect = chartBodyRef.value.getBoundingClientRect()
  const offsetX = event.clientX - chartRect.left
  const newStartIndex = Math.floor(offsetX / cellWidth.value)

  if (newStartIndex >= 0 && newStartIndex < headerDates.value.length) {
    const newStartDate = new Date(headerDates.value[newStartIndex].key)
    const duration = task.due_date && task.start_date
      ? (new Date(task.due_date) - new Date(task.start_date)) / (1000 * 60 * 60 * 24)
      : 7

    const newDueDate = new Date(newStartDate)
    newDueDate.setDate(newDueDate.getDate() + duration)

    try {
      await apiService.personalPlan.updateTask(task.id, {
        start_date: newStartDate.toISOString().split('T')[0],
        due_date: newDueDate.toISOString().split('T')[0]
      })
      ElMessage.success('任务时间已更新')
      loadGanttTasks()
    } catch (error) {
      ElMessage.error('更新失败')
    }
  }

  draggingTask.value = null
}

const handleCellClick = (task, date) => {
  if (!selectedTask.value) return

  if (!task.start_date) {
    apiService.personalPlan.updateTask(task.id, {
      start_date: date.key,
      due_date: date.key
    }).then(() => {
      ElMessage.success('已设置任务时间')
      loadGanttTasks()
    })
  }
}

const saveBaseline = async () => {
  try {
    ElMessage.success('基线已保存（模拟）')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const exportGantt = () => {
  ElMessage.info('导出功能开发中')
}

const loadGanttTasks = async () => {
  try {
    const data = await apiService.personalPlan.getTasks({})
    ganttTasks.value = Array.isArray(data?.tasks) ? data.tasks.map(t => ({
      ...t,
      ownerAvatar: '/avatar-placeholder.png',
      baseline: null
    })) : []
    updateTodayPosition()
  } catch (error) {
    console.error('加载甘特图任务失败:', error)
    ganttTasks.value = []
  }
}

const updateTodayPosition = () => {
  const today = new Date().toISOString().split('T')[0]
  const index = headerDates.value.findIndex(d => d.key === today)
  if (index >= 0) {
    todayPosition.value = index * cellWidth.value + cellWidth.value / 2
  }
}

onMounted(() => {
  loadGanttTasks()
})
</script>

<style scoped>
.gantt-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.gantt-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e6e6e6;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.zoom-slider {
  width: 120px;
}

.zoom-label {
  font-size: 12px;
  color: #909399;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.gantt-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.gantt-sidebar {
  width: 300px;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e6e6e6;
  font-weight: 600;
  font-size: 13px;
  color: #606266;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}

.task-row {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.task-row:hover {
  background: #f5f7fa;
}

.task-row.selected {
  background: #ecf5ff;
}

.task-name {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  overflow: hidden;
}

.task-priority {
  width: 4px;
  height: 16px;
  border-radius: 2px;
  flex-shrink: 0;
}

.task-priority.urgent {
  background: #f56c6c;
}

.task-priority.high {
  background: #e6a23c;
}

.task-priority.medium {
  background: #409EFF;
}

.task-priority.low {
  background: #67c23a;
}

.task-title {
  font-size: 13px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-owner {
  flex-shrink: 0;
}

.gantt-chart {
  flex: 1;
  overflow-x: auto;
  position: relative;
}

.chart-header {
  height: 48px;
  display: flex;
  background: #f5f7fa;
  border-bottom: 1px solid #e6e6e6;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #e6e6e6;
  font-size: 12px;
  color: #606266;
  flex-shrink: 0;
}

.chart-body {
  position: relative;
}

.chart-row {
  height: 48px;
  display: flex;
  position: relative;
  border-bottom: 1px solid #f0f0f0;
}

.chart-row.selected {
  background: #f5f7fa;
}

.chart-cell {
  height: 100%;
  border-right: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.chart-cell.today {
  background: #ecf5ff;
}

.task-bar {
  position: absolute;
  border-radius: 4px;
  cursor: grab;
  display: flex;
  align-items: center;
  padding: 0 8px;
  overflow: hidden;
  transition: box-shadow 0.2s;
  z-index: 5;
}

.task-bar:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.task-bar.dragging {
  cursor: grabbing;
  opacity: 0.8;
}

.task-bar.urgent {
  background: #f56c6c;
}

.task-bar.high {
  background: #e6a23c;
}

.task-bar.medium {
  background: #409EFF;
}

.task-bar.low {
  background: #67c23a;
}

.bar-progress {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px 0 0 4px;
}

.bar-label {
  position: relative;
  color: #fff;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.bar-progress-text {
  position: relative;
  color: #fff;
  font-size: 11px;
  margin-left: 4px;
}

.task-baseline {
  position: absolute;
  background: rgba(144, 147, 153, 0.4);
  border-radius: 2px;
  z-index: 4;
}

.dependency-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 6;
}

.dependency-line {
  stroke: #909399;
  stroke-width: 1.5;
  fill: none;
}

.today-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #f56c6c;
  z-index: 7;
}

.today-line::before {
  content: '今天';
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: #f56c6c;
  white-space: nowrap;
}

.task-detail-popover {
  position: fixed;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  min-width: 240px;
  z-index: 1000;
}

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.popover-header h4 {
  margin: 0;
  font-size: 14px;
  color: #303133;
}

.popover-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  font-size: 13px;
}

.detail-row .label {
  color: #909399;
  width: 80px;
}

.detail-row .value {
  color: #606266;
  flex: 1;
}
</style>
