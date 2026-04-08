<template>
  <div class="calendar-view">
    <div class="calendar-header">
      <el-button @click="prevDay" icon="ArrowLeft" circle />
      <el-date-picker
        v-model="selectedDate"
        type="date"
        placeholder="选择日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        @change="handleDateChange"
      />
      <el-button @click="nextDay" icon="ArrowRight" circle />
      <el-button @click="goToToday" size="small">今天</el-button>
    </div>

    <div class="calendar-body">
      <div class="time-gutter">
        <div v-for="hour in 24" :key="hour" class="time-slot">
          {{ String(hour - 1).padStart(2, '0') }}:00
        </div>
      </div>
      <div class="events-area">
        <div v-for="hour in 24" :key="hour" class="hour-row">
          <div class="hour-line" />
        </div>
        <div
          v-for="event in events"
          :key="event.id"
          class="event-block"
          :style="getEventStyle(event)"
          @click="handleEventClick(event)"
        >
          <div class="event-title">{{ event.title }}</div>
          <div class="event-time" v-if="event.time">{{ event.time }}</div>
        </div>
      </div>
    </div>

    <div class="time-blocks">
      <h4>今日时间块</h4>
      <div class="blocks-list" v-if="blocks.length > 0">
        <div v-for="block in blocks" :key="block.id" class="block-item">
          <div class="block-time">{{ block.start_time }}</div>
          <div class="block-content">
            <div class="block-title">{{ block.title }}</div>
            <el-tag v-if="block.is_habit" size="small" type="success">习惯</el-tag>
          </div>
          <el-tag :type="getPriorityType(block.priority)" size="small">
            {{ getPriorityText(block.priority) }}
          </el-tag>
        </div>
      </div>
      <el-empty v-else description="暂无时间块" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  events: {
    type: Array,
    default: () => []
  },
  selectedDate: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['refresh', 'select-date', 'create-block'])

const blocks = ref([])

const selectedDate = computed({
  get: () => props.selectedDate,
  set: (val) => emit('select-date', val)
})

const prevDay = () => {
  const date = new Date(selectedDate.value)
  date.setDate(date.getDate() - 1)
  emit('select-date', date.toISOString().split('T')[0])
}

const nextDay = () => {
  const date = new Date(selectedDate.value)
  date.setDate(date.getDate() + 1)
  emit('select-date', date.toISOString().split('T')[0])
}

const goToToday = () => {
  emit('select-date', new Date().toISOString().split('T')[0])
}

const handleDateChange = (date) => {
  emit('select-date', date)
}

const getEventStyle = (event) => {
  if (!event.time) return {}

  const [hours, minutes] = event.time.split(':').map(Number)
  const top = (hours * 60 + minutes) * (60 / 60)
  const duration = event.duration || 30

  return {
    top: `${top}px`,
    height: `${duration}px`,
    backgroundColor: event.color || '#409eff'
  }
}

const handleEventClick = (event) => {
  console.log('Event clicked:', event)
}

const getPriorityType = (priority) => {
  const types = {
    urgent: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info'
  }
  return types[priority] || 'info'
}

const getPriorityText = (priority) => {
  const texts = {
    urgent: '紧急',
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[priority] || '中'
}
</script>

<style scoped>
.calendar-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.calendar-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.calendar-body {
  display: flex;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  height: 600px;
}

.time-gutter {
  width: 60px;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.time-slot {
  height: 60px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 4px;
  font-size: 12px;
  color: #909399;
  border-bottom: 1px solid #e4e7ed;
}

.events-area {
  flex: 1;
  position: relative;
}

.hour-row {
  height: 60px;
  border-bottom: 1px solid #e4e7ed;
}

.hour-line {
  border-top: 1px dashed #e4e7ed;
  height: 1px;
}

.event-block {
  position: absolute;
  left: 4px;
  right: 4px;
  border-radius: 4px;
  padding: 4px 8px;
  color: white;
  font-size: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.event-block:hover {
  opacity: 0.9;
  transform: scale(1.02);
}

.event-title {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-time {
  font-size: 10px;
  opacity: 0.8;
}

.time-blocks {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}

.time-blocks h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.blocks-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.block-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
}

.block-time {
  font-size: 14px;
  font-weight: 500;
  color: #409eff;
  width: 50px;
}

.block-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.block-title {
  font-size: 14px;
  color: #303133;
}

@media screen and (max-width: 768px) {
  .calendar-body {
    height: 400px;
    overflow-x: auto;
  }

  .time-gutter {
    width: 50px;
  }

  .time-slot {
    font-size: 10px;
  }
}
</style>