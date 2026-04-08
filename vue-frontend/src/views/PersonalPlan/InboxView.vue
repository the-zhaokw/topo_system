<template>
  <div class="inbox-view">
    <div class="inbox-header">
      <div class="header-left">
        <h3>收件箱</h3>
        <el-tag type="info">{{ tasks.length }} 条待整理</el-tag>
      </div>
      <div class="header-actions">
        <el-button @click="handleSelectAll" type="primary" plain size="small">
          {{ selectedTasks.length === tasks.length ? '取消全选' : '全选' }}
        </el-button>
        <el-button @click="handleBatchAction('organize')" :disabled="selectedTasks.length === 0" type="success" plain size="small">
          整理到任务
        </el-button>
        <el-button @click="handleBatchAction('delete')" :disabled="selectedTasks.length === 0" type="danger" plain size="small">
          删除
        </el-button>
      </div>
    </div>

    <div class="task-list" v-if="tasks.length > 0">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="task-item"
        :class="{ selected: selectedTasks.includes(task.id) }"
        @click="toggleSelect(task.id)"
      >
        <div class="task-checkbox">
          <el-checkbox :model-value="selectedTasks.includes(task.id)" @click.stop />
        </div>
        <div class="task-content">
          <div class="task-title">
            <span v-if="task.priority === 'urgent'" class="priority-badge urgent">!</span>
            <span v-if="task.priority === 'high'" class="priority-badge high">!!</span>
            {{ task.title }}
          </div>
          <div class="task-meta" v-if="task.tags || task.estimated_minutes">
            <el-tag v-if="task.tags" size="small" type="info">{{ task.tags.split(',')[0] }}</el-tag>
            <span v-if="task.estimated_minutes" class="duration">{{ task.estimated_minutes }}分钟</span>
          </div>
          <div class="task-time">{{ formatTime(task.created_at) }}</div>
        </div>
        <div class="task-actions">
          <el-button size="small" @click.stop="$emit('edit', task)">编辑</el-button>
          <el-button size="small" type="danger" @click.stop="$emit('delete', task.id)">删除</el-button>
        </div>
      </div>
    </div>

    <el-empty v-else description="收件箱空空如也，快去记录点什么吧！">
      <template #image>
        <el-icon :size="60" color="#909399"><Box /></el-icon>
      </template>
    </el-empty>

    <el-dialog v-model="organizeDialogVisible" title="整理任务" width="400px">
      <el-form :model="organizeForm" label-width="80px">
        <el-form-item label="移动到">
          <el-select v-model="organizeForm.status" placeholder="选择目标列表">
            <el-option label="待办" value="todo" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="done" />
          </el-select>
        </el-form-item>
        <el-form-item label="象限">
          <el-select v-model="organizeForm.quadrant" placeholder="选择象限">
            <el-option label="第一象限（紧急且重要）" :value="1" />
            <el-option label="第二象限（重要不紧急）" :value="2" />
            <el-option label="第三象限（紧急不重要）" :value="3" />
            <el-option label="第四象限（不紧急不重要）" :value="4" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="organizeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmOrganize">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Box } from '@element-plus/icons-vue'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['refresh', 'process', 'edit', 'delete'])

const selectedTasks = ref([])
const organizeDialogVisible = ref(false)
const organizeForm = reactive({
  status: 'todo',
  quadrant: null
})

const toggleSelect = (taskId) => {
  const index = selectedTasks.value.indexOf(taskId)
  if (index === -1) {
    selectedTasks.value.push(taskId)
  } else {
    selectedTasks.value.splice(index, 1)
  }
}

const handleSelectAll = () => {
  if (selectedTasks.value.length === props.tasks.length) {
    selectedTasks.value = []
  } else {
    selectedTasks.value = props.tasks.map(t => t.id)
  }
}

const handleBatchAction = (action) => {
  if (action === 'organize') {
    organizeDialogVisible.value = true
  } else if (action === 'delete') {
    emit('process', { taskIds: selectedTasks.value, action: 'delete' })
    selectedTasks.value = []
  }
}

const confirmOrganize = () => {
  emit('process', {
    taskIds: selectedTasks.value,
    action: 'organize',
    status: organizeForm.status
  })
  if (organizeForm.quadrant) {
    selectedTasks.value.forEach(taskId => {
      emit('edit', { id: taskId, quadrant: organizeForm.quadrant })
    })
  }
  organizeDialogVisible.value = false
  selectedTasks.value = []
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.inbox-view {
  height: 100%;
}

.inbox-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.task-item:hover {
  background: #ecf5ff;
}

.task-item.selected {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
}

.task-checkbox {
  margin-right: 12px;
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.priority-badge {
  font-weight: bold;
  font-size: 12px;
}

.priority-badge.urgent {
  color: #f56c6c;
}

.priority-badge.high {
  color: #e6a23c;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.duration {
  margin-left: 4px;
}

.task-time {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}

.task-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.task-item:hover .task-actions {
  opacity: 1;
}

@media screen and (max-width: 768px) {
  .task-actions {
    opacity: 1;
  }
}
</style>