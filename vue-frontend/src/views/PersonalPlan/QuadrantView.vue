<template>
  <div class="quadrant-view">
    <div class="quadrant-grid">
      <div class="quadrant q1">
        <div class="quadrant-header">
          <div class="quadrant-title">
            <span class="quadrant-icon urgent">🔥</span>
            <span>紧急且重要</span>
          </div>
          <el-tag type="danger" size="small">{{ tasks[1]?.length || 0 }}</el-tag>
        </div>
        <div class="quadrant-content">
          <div
            v-for="task in tasks[1]"
            :key="task.id"
            class="task-card urgent"
          >
            <div class="task-title">{{ task.title }}</div>
            <div class="task-meta" v-if="task.scheduled_time">
              <el-icon><Clock /></el-icon>
              {{ task.scheduled_time }}
            </div>
            <div class="task-actions">
              <el-button size="small" type="primary" @click="$emit('start', task.id)">开始</el-button>
              <el-button size="small" type="success" @click="$emit('complete', task.id)">完成</el-button>
            </div>
          </div>
          <div v-if="!tasks[1]?.length" class="empty-quadrant">
            暂无紧急任务
          </div>
        </div>
      </div>

      <div class="quadrant q2">
        <div class="quadrant-header">
          <div class="quadrant-title">
            <span class="quadrant-icon important">📌</span>
            <span>重要不紧急</span>
          </div>
          <el-tag type="warning" size="small">{{ tasks[2]?.length || 0 }}</el-tag>
        </div>
        <div class="quadrant-content">
          <div
            v-for="task in tasks[2]"
            :key="task.id"
            class="task-card important"
          >
            <div class="task-title">{{ task.title }}</div>
            <div class="task-meta" v-if="task.scheduled_date">
              <el-icon><Calendar /></el-icon>
              {{ task.scheduled_date }}
            </div>
            <div class="task-actions">
              <el-button size="small" type="primary" @click="$emit('start', task.id)">开始</el-button>
              <el-button size="small" type="success" @click="$emit('complete', task.id)">完成</el-button>
            </div>
          </div>
          <div v-if="!tasks[2]?.length" class="empty-quadrant">
            暂无重要任务
          </div>
        </div>
      </div>

      <div class="quadrant q3">
        <div class="quadrant-header">
          <div class="quadrant-title">
            <span class="quadrant-icon urgent-low">⚡</span>
            <span>紧急不重要</span>
          </div>
          <el-tag type="info" size="small">{{ tasks[3]?.length || 0 }}</el-tag>
        </div>
        <div class="quadrant-content">
          <div
            v-for="task in tasks[3]"
            :key="task.id"
            class="task-card urgent-low"
          >
            <div class="task-title">{{ task.title }}</div>
            <div class="task-actions">
              <el-button size="small" type="primary" @click="$emit('start', task.id)">开始</el-button>
              <el-button size="small" type="success" @click="$emit('complete', task.id)">完成</el-button>
            </div>
          </div>
          <div v-if="!tasks[3]?.length" class="empty-quadrant">
            暂无紧急任务
          </div>
        </div>
      </div>

      <div class="quadrant q4">
        <div class="quadrant-header">
          <div class="quadrant-title">
            <span class="quadrant-icon normal">📋</span>
            <span>不紧急不重要</span>
          </div>
          <el-tag type="info" size="small">{{ tasks[4]?.length || 0 }}</el-tag>
        </div>
        <div class="quadrant-content">
          <div
            v-for="task in tasks[4]"
            :key="task.id"
            class="task-card normal"
          >
            <div class="task-title">{{ task.title }}</div>
            <div class="task-actions">
              <el-button size="small" type="success" @click="$emit('complete', task.id)">完成</el-button>
            </div>
          </div>
          <div v-if="!tasks[4]?.length" class="empty-quadrant">
            任务列表清晰
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Clock, Calendar } from '@element-plus/icons-vue'

const props = defineProps({
  tasks: {
    type: Object,
    default: () => ({ 1: [], 2: [], 3: [], 4: [] })
  }
})

const emit = defineEmits(['refresh', 'start', 'complete'])
</script>

<style scoped>
.quadrant-view {
  height: 100%;
}

.quadrant-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 16px;
  height: 100%;
  min-height: 500px;
}

.quadrant {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.quadrant.q1 {
  background: linear-gradient(135deg, #fff1f0 0%, #ffebe6 100%);
  border: 1px solid #ffccc7;
}

.quadrant.q2 {
  background: linear-gradient(135deg, #fff7e6 0%, #fff3cc 100%);
  border: 1px solid #ffe7a0;
}

.quadrant.q3 {
  background: linear-gradient(135deg, #e6f7ff 0%, #d6eeff 100%);
  border: 1px solid #adc6ff;
}

.quadrant.q4 {
  background: linear-gradient(135deg, #f6ffed 0%, #e8f8e6 100%);
  border: 1px solid #b7eb8f;
}

.quadrant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.quadrant-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.quadrant-icon {
  font-size: 20px;
}

.quadrant-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-card {
  background: white;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.task-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.task-card.urgent {
  border-left: 4px solid #f56c6c;
}

.task-card.important {
  border-left: 4px solid #e6a23c;
}

.task-card.urgent-low {
  border-left: 4px solid #409eff;
}

.task-card.normal {
  border-left: 4px solid #67c23a;
}

.task-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 8px;
  line-height: 1.4;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.task-actions {
  display: flex;
  gap: 8px;
}

.empty-quadrant {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 20px;
}

@media screen and (max-width: 992px) {
  .quadrant-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(4, auto);
  }

  .quadrant-content {
    max-height: 300px;
  }
}
</style>