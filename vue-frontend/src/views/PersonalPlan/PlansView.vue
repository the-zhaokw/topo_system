<template>
  <div class="plan-list-view">
    <div class="list-header">
      <div class="header-left">
        <el-radio-group v-model="currentView" size="default">
          <el-radio-button value="list">
            <el-icon><List /></el-icon> 列表视图
          </el-radio-button>
          <el-radio-button value="kanban">
            <el-icon><Grid /></el-icon> 看板视图
          </el-radio-button>
        </el-radio-group>

        <el-select v-model="filterStatus" placeholder="状态筛选" clearable size="default" class="filter-select">
          <el-option label="全部" value="" />
          <el-option label="待办" value="todo" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="done" />
          <el-option label="已延期" value="overdue" />
        </el-select>

        <el-select v-model="filterTag" placeholder="标签筛选" clearable size="default" class="filter-select">
          <el-option label="全部" value="" />
          <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
        </el-select>
      </div>

      <div class="header-right">
        <el-button @click="showCreateDialog = true" type="primary">
          <el-icon><Plus /></el-icon>
          新建任务
        </el-button>
      </div>
    </div>

    <div class="list-content" v-if="currentView === 'list'">
      <!-- 桌面端表格 -->
      <el-table
        v-if="!isMobile"
        :data="filteredTasks"
        row-key="id"
        :tree-props="{ children: 'subtasks', hasChildren: 'hasSubtasks' }"
        default-expand-all
        @row-dblclick="handleRowDblClick"
        class="task-table"
        :row-class-name="getRowClassName"
      >
        <el-table-column width="40">
          <template #default="{ row }">
            <el-checkbox
              :model-value="row.completed"
              @change="toggleTaskComplete(row)"
            />
          </template>
        </el-table-column>

        <el-table-column prop="title" label="任务名称" min-width="300">
          <template #default="{ row }">
            <div class="task-title-cell">
              <span v-if="row.priority === 'urgent'" class="priority-indicator urgent">!</span>
              <span v-else-if="row.priority === 'high'" class="priority-indicator high">!!</span>
              <span class="task-title" :class="{ completed: row.completed }">{{ row.title }}</span>
              <el-tag v-if="row.subtasks?.length" size="small" type="info">
                {{ row.subtasks.filter(s => s.completed).length }}/{{ row.subtasks.length }}
              </el-tag>
              <el-button
                v-if="row.subtasks?.length"
                text
                size="small"
                @click="toggleSubtasks(row)"
              >
                <el-icon>
                  <ArrowDown v-if="!row._showSubtasks" />
                  <ArrowUp v-else />
                </el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <span class="priority-dot" :class="row.priority"></span>
          </template>
        </el-table-column>

        <el-table-column prop="due_date" label="截止时间" width="140">
          <template #default="{ row }">
            <span v-if="row.due_date" class="due-date" :class="{ overdue: isOverdue(row) }">
              {{ formatDate(row.due_date) }}
            </span>
            <span v-else class="no-date">未设置</span>
          </template>
        </el-table-column>

        <el-table-column prop="progress" label="进度" width="120">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                :percentage="row.progress || 0"
                :stroke-width="6"
                :show-text="false"
              />
              <span class="progress-text">{{ row.progress || 0 }}%</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="tags" label="标签" width="150">
          <template #default="{ row }">
            <el-tag
              v-for="tag in (row.tags || '').split(',').filter(t => t)"
              :key="tag"
              size="small"
              type="info"
              class="task-tag"
            >
              #{{ tag }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" @click="editTask(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button text size="small" @click="copyTask(row)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
            <el-button text size="small" type="danger" @click="deleteTask(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 移动端卡片列表 -->
      <div v-else class="mobile-task-list">
        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="mobile-task-card"
          :class="{ completed: task.completed, overdue: isOverdue(task) }"
          @click="editTask(task)"
        >
          <div class="task-card-top">
            <el-checkbox
              :model-value="task.completed"
              @change="toggleTaskComplete(task)"
              @click.stop
            />
            <span class="task-priority-dot" :class="task.priority"></span>
            <span class="task-card-title" :class="{ completed: task.completed }">{{ task.title }}</span>
          </div>
          <div class="task-card-meta">
            <span v-if="task.due_date" class="task-card-due" :class="{ overdue: isOverdue(task) }">
              <el-icon><Clock /></el-icon>
              {{ formatDate(task.due_date) }}
            </span>
            <div class="task-card-progress">
              <el-progress
                :percentage="task.progress || 0"
                :stroke-width="4"
                :show-text="false"
              />
              <span class="progress-text">{{ task.progress || 0 }}%</span>
            </div>
          </div>
          <div v-if="task.tags" class="task-card-tags">
            <el-tag
              v-for="tag in (task.tags || '').split(',').filter(t => t).slice(0, 3)"
              :key="tag"
              size="small"
              type="info"
            >
              #{{ tag }}
            </el-tag>
          </div>
          <div class="task-card-actions" @click.stop>
            <el-button text size="small" @click="editTask(task)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button text size="small" @click="copyTask(task)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
            <el-button text size="small" type="danger" @click="deleteTask(task)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
        <div v-if="filteredTasks.length === 0" class="empty-state">
          <el-empty description="暂无任务" />
        </div>
      </div>
    </div>

    <div class="kanban-content" v-else>
      <div
        v-for="column in kanbanColumns"
        :key="column.status"
        class="kanban-column"
      >
        <div class="column-header">
          <div class="column-title">
            <span class="column-dot" :class="column.status"></span>
            {{ column.title }}
            <span class="column-count">{{ getColumnTasks(column.status).length }}</span>
          </div>
        </div>

        <div
          class="column-content"
          @dragover.prevent
          @drop="handleKanbanDrop($event, column.status)"
        >
          <div
            v-for="task in getColumnTasks(column.status)"
            :key="task.id"
            class="kanban-card"
            draggable="true"
            @dragstart="handleKanbanDragStart($event, task)"
            @dragend="handleKanbanDragEnd"
          >
            <div class="card-header">
              <span class="card-priority" :class="task.priority"></span>
              <span class="card-title">{{ task.title }}</span>
            </div>

            <div class="card-meta">
              <span v-if="task.due_date" class="card-due" :class="{ overdue: isOverdue(task) }">
                <el-icon><Clock /></el-icon>
                {{ formatDate(task.due_date) }}
              </span>
              <div class="card-progress">
                <el-progress
                  type="circle"
                  :percentage="task.progress || 0"
                  :width="24"
                  :stroke-width="3"
                />
              </div>
            </div>

            <div class="card-footer">
              <el-tag v-for="tag in (task.tags || '').split(',').filter(t => t).slice(0, 2)" :key="tag" size="small" type="info">
                #{{ tag }}
              </el-tag>
            </div>
          </div>

          <div class="add-card" @click="addTaskToColumn(column.status)">
            <el-icon><Plus /></el-icon>
            添加任务
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedTasks.length > 0" class="batch-actions">
      <span>已选择 {{ selectedTasks.length }} 项</span>
      <el-button size="small" @click="batchChangeTags">批量改标签</el-button>
      <el-button size="small" @click="batchDelay">批量延期</el-button>
      <el-button size="small" type="success" @click="batchComplete">批量完成</el-button>
      <el-button size="small" type="danger" @click="batchDelete">批量删除</el-button>
    </div>

    <el-dialog v-model="showCreateDialog" :title="editingTask ? '编辑任务' : '新建任务'" width="600px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务标题">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>

        <el-form-item label="任务描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="taskForm.priority">
                <el-option label="紧急" value="urgent" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预估时长">
              <el-input-number v-model="taskForm.estimated_minutes" :min="5" :step="5" :max="480" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker
                v-model="taskForm.start_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="选择日期"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期">
              <el-date-picker
                v-model="taskForm.due_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="选择日期"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="标签">
          <el-input v-model="taskForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>

        <el-form-item label="依赖任务">
          <el-select v-model="taskForm.dependencies" multiple placeholder="选择依赖任务">
            <el-option v-for="t in availableTasks" :key="t.id" :label="t.title" :value="t.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="子任务">
          <div class="subtask-list">
            <div v-for="(subtask, index) in taskForm.subtasks" :key="index" class="subtask-item">
              <el-input v-model="subtask.title" placeholder="子任务名称" />
              <el-button text type="danger" @click="removeSubtask(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button text @click="addSubtask">
              <el-icon><Plus /></el-icon> 添加子任务
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTask">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBatchTagDialog" title="批量修改标签" width="400px">
      <el-form-item label="新标签">
        <el-input v-model="batchTagValue" placeholder="输入标签" />
      </el-form-item>
      <template #footer>
        <el-button @click="showBatchTagDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchTag">确认</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBatchDelayDialog" title="批量延期" width="400px">
      <el-form-item label="延期至">
        <el-date-picker v-model="batchDelayDate" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <template #footer>
        <el-button @click="showBatchDelayDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchDelay">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  List, Grid, Plus, Edit, Delete, CopyDocument, Clock, ArrowDown, ArrowUp
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import { useResponsive } from '@/composables/useResponsive'

const { isMobile } = useResponsive()

const route = useRoute()

const currentView = ref('list')
const filterStatus = ref('')
const filterTag = ref('')
const showCreateDialog = ref(false)
const editingTask = ref(null)

const tasks = ref([])
const selectedTasks = ref([])
const availableTasks = ref([])
const availableTags = ref(['高优先级', '沟通', '开发', '文档', '会议'])

const showBatchTagDialog = ref(false)
const batchTagValue = ref('')
const showBatchDelayDialog = ref(false)
const batchDelayDate = ref('')

const draggedTask = ref(null)

const taskForm = reactive({
  title: '',
  description: '',
  priority: 'medium',
  estimated_minutes: 30,
  start_date: '',
  due_date: '',
  tags: '',
  dependencies: [],
  subtasks: []
})

const kanbanColumns = [
  { title: '待办', status: 'todo' },
  { title: '进行中', status: 'in_progress' },
  { title: '已完成', status: 'done' },
  { title: '已延期', status: 'overdue' }
]

const filteredTasks = computed(() => {
  let result = tasks.value

  if (filterStatus.value) {
    if (filterStatus.value === 'overdue') {
      result = result.filter(t => isOverdue(t))
    } else {
      result = result.filter(t => t.status === filterStatus.value)
    }
  }

  if (filterTag.value) {
    result = result.filter(t => t.tags && t.tags.includes(filterTag.value))
  }

  return result
})

const isOverdue = (task) => {
  if (!task.due_date) return false
  const now = new Date()
  const due = new Date(task.due_date)
  return due < now && !task.completed
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const getRowClassName = ({ row }) => {
  if (isOverdue(row)) return 'overdue-row'
  if (row.at_risk) return 'at-risk-row'
  return ''
}

const toggleTaskComplete = async (task) => {
  try {
    await apiService.personalPlan.updateTask(task.id, { completed: !task.completed })
    task.completed = !task.completed
    ElMessage.success(task.completed ? '任务已完成' : '任务已取消完成')
    loadTasks()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const toggleSubtasks = (row) => {
  row._showSubtasks = !row._showSubtasks
}

const getColumnTasks = (status) => {
  if (status === 'overdue') {
    return tasks.value.filter(t => isOverdue(t))
  }
  return tasks.value.filter(t => t.status === status)
}

const handleKanbanDragStart = (event, task) => {
  draggedTask.value = task
  event.dataTransfer.effectAllowed = 'move'
}

const handleKanbanDragEnd = () => {
  draggedTask.value = null
}

const handleKanbanDrop = async (event, status) => {
  if (!draggedTask.value) return

  try {
    await apiService.personalPlan.updateTask(draggedTask.value.id, { status })
    ElMessage.success('任务状态已更新')
    loadTasks()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleRowDblClick = (row) => {
  editTask(row)
}

const editTask = (task) => {
  editingTask.value = task
  taskForm.title = task.title
  taskForm.description = task.description || ''
  taskForm.priority = task.priority || 'medium'
  taskForm.estimated_minutes = task.estimated_minutes || 30
  taskForm.start_date = task.start_date || ''
  taskForm.due_date = task.due_date || ''
  taskForm.tags = task.tags || ''
  taskForm.dependencies = task.dependencies || []
  taskForm.subtasks = task.subtasks ? [...task.subtasks] : []
  showCreateDialog.value = true
}

const copyTask = async (task) => {
  try {
    await apiService.personalPlan.createTask({
      title: task.title + ' (副本)',
      description: task.description,
      priority: task.priority,
      estimated_minutes: task.estimated_minutes,
      tags: task.tags
    })
    ElMessage.success('任务已复制')
    loadTasks()
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await apiService.personalPlan.deleteTask(task.id)
    ElMessage.success('任务已删除')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const addTaskToColumn = (status) => {
  editingTask.value = null
  Object.assign(taskForm, {
    title: '',
    description: '',
    priority: 'medium',
    estimated_minutes: 30,
    start_date: '',
    due_date: '',
    tags: '',
    dependencies: [],
    subtasks: []
  })
  taskForm.status = status
  showCreateDialog.value = true
}

const addSubtask = () => {
  taskForm.subtasks.push({ title: '', completed: false })
}

const removeSubtask = (index) => {
  taskForm.subtasks.splice(index, 1)
}

const saveTask = async () => {
  if (!taskForm.title) {
    ElMessage.warning('请输入任务标题')
    return
  }

  try {
    if (editingTask.value) {
      await apiService.personalPlan.updateTask(editingTask.value.id, taskForm)
      ElMessage.success('任务已更新')
    } else {
      await apiService.personalPlan.createTask(taskForm)
      ElMessage.success('任务已创建')
    }
    showCreateDialog.value = false
    editingTask.value = null
    loadTasks()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const batchChangeTags = () => {
  showBatchTagDialog.value = true
}

const confirmBatchTag = async () => {
  if (!batchTagValue.value) return
  try {
    for (const taskId of selectedTasks.value) {
      const task = tasks.value.find(t => t.id === taskId)
      const newTags = task.tags ? task.tags + ',' + batchTagValue.value : batchTagValue.value
      await apiService.personalPlan.updateTask(taskId, { tags: newTags })
    }
    ElMessage.success('标签已更新')
    selectedTasks.value = []
    showBatchTagDialog.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error('批量修改失败')
  }
}

const batchDelay = () => {
  showBatchDelayDialog.value = true
}

const confirmBatchDelay = async () => {
  if (!batchDelayDate.value) return
  try {
    for (const taskId of selectedTasks.value) {
      await apiService.personalPlan.updateTask(taskId, { due_date: batchDelayDate.value })
    }
    ElMessage.success('已延期')
    selectedTasks.value = []
    showBatchDelayDialog.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error('批量延期失败')
  }
}

const batchComplete = async () => {
  try {
    for (const taskId of selectedTasks.value) {
      await apiService.personalPlan.updateTask(taskId, { completed: true })
    }
    ElMessage.success('任务已完成')
    selectedTasks.value = []
    loadTasks()
  } catch (error) {
    ElMessage.error('批量完成失败')
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedTasks.value.length} 个任务吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    for (const taskId of selectedTasks.value) {
      await apiService.personalPlan.deleteTask(taskId)
    }
    ElMessage.success('已删除')
    selectedTasks.value = []
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const loadTasks = async () => {
  try {
    const data = await apiService.personalPlan.getTasks({
      tag: filterTag.value || undefined,
      status: filterStatus.value || undefined
    })
    tasks.value = data.tasks || []
  } catch (error) {
    console.error('加载任务失败:', error)
  }
}

const loadAvailableTasks = async () => {
  try {
    const data = await apiService.personalPlan.getTasks({ status: 'todo,in_progress' })
    availableTasks.value = data.tasks || []
  } catch (error) {
    console.error('加载任务失败:', error)
  }
}

watch([filterStatus, filterTag], () => {
  loadTasks()
})

watch(() => route.query, (query) => {
  if (query.tag) {
    filterTag.value = query.tag
  }
  if (query.filter === 'overdue') {
    filterStatus.value = 'overdue'
  }
  if (query.filter === 'at_risk') {
    filterStatus.value = 'in_progress'
  }
}, { immediate: true })

onMounted(() => {
  loadTasks()
  loadAvailableTasks()
})
</script>

<style scoped>
.plan-list-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-select {
  width: 140px;
}

.list-content {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  overflow: auto;
}

.task-table {
  width: 100%;
}

.task-title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.priority-indicator {
  font-weight: bold;
  font-size: 12px;
}

.priority-indicator.urgent {
  color: #f56c6c;
}

.priority-indicator.high {
  color: #e6a23c;
}

.task-title {
  font-size: 14px;
}

.task-title.completed {
  text-decoration: line-through;
  color: #909399;
}

.task-tag {
  margin-right: 4px;
}

.priority-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.priority-dot.urgent {
  background: #f56c6c;
}

.priority-dot.high {
  background: #e6a23c;
}

.priority-dot.medium {
  background: #409EFF;
}

.priority-dot.low {
  background: #67c23a;
}

.due-date {
  font-size: 13px;
  color: #606266;
}

.due-date.overdue {
  color: #f56c6c;
  font-weight: 500;
}

.no-date {
  color: #c0c4cc;
  font-size: 13px;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #909399;
  min-width: 35px;
}

:deep(.overdue-row) {
  background: #fef0f0 !important;
}

:deep(.at-risk-row) {
  background: #fdf6ec !important;
}

.kanban-content {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 20px;
}

.kanban-column {
  flex: 0 0 280px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 240px);
}

.column-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e6e6e6;
}

.column-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.column-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.column-dot.todo {
  background: #909399;
}

.column-dot.in_progress {
  background: #409EFF;
}

.column-dot.done {
  background: #67c23a;
}

.column-dot.overdue {
  background: #f56c6c;
}

.column-count {
  background: #e6e6e6;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: normal;
}

.column-content {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.kanban-card {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  cursor: grab;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.kanban-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.kanban-card:active {
  cursor: grabbing;
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.card-priority {
  width: 4px;
  height: 16px;
  border-radius: 2px;
  flex-shrink: 0;
}

.card-priority.urgent {
  background: #f56c6c;
}

.card-priority.high {
  background: #e6a23c;
}

.card-priority.medium {
  background: #409EFF;
}

.card-priority.low {
  background: #67c23a;
}

.card-title {
  font-size: 14px;
  color: #303133;
  flex: 1;
  word-break: break-word;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-due {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.card-due.overdue {
  color: #f56c6c;
}

.card-footer {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.add-card {
  padding: 12px;
  text-align: center;
  color: #909399;
  cursor: pointer;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  transition: all 0.2s;
}

.add-card:hover {
  border-color: #409EFF;
  color: #409EFF;
}

.batch-actions {
  position: fixed;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  background: #303133;
  color: #fff;
  padding: 12px 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 100;
}

.batch-actions span {
  font-size: 14px;
}

.subtask-list {
  width: 100%;
}

.subtask-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.subtask-item .el-input {
  flex: 1;
}

.mobile-task-list {
  display: none;
}

@media screen and (max-width: 768px) {
  .plan-list-view {
    padding: 0;
  }

  .list-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .header-left {
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-left .el-radio-group {
    width: 100%;
  }

  .header-left .el-radio-group :deep(.el-radio-button__inner) {
    flex: 1;
    padding: 8px 12px;
    font-size: 13px;
  }

  .filter-select {
    width: calc(50% - 4px) !important;
    flex: 1;
  }

  .list-content {
    padding: 8px;
    background: transparent;
  }

  .mobile-task-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .mobile-task-card {
    background: #fff;
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    cursor: pointer;
    transition: all 0.2s;
    -webkit-tap-highlight-color: transparent;
  }

  .mobile-task-card:active {
    transform: scale(0.98);
    background: #f5f7fa;
  }

  .mobile-task-card.overdue {
    border-left: 3px solid #f56c6c;
  }

  .mobile-task-card.completed {
    opacity: 0.6;
  }

  .task-card-top {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }

  .task-priority-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .task-priority-dot.urgent { background: #f56c6c; }
  .task-priority-dot.high { background: #e6a23c; }
  .task-priority-dot.medium { background: #409EFF; }
  .task-priority-dot.low { background: #67c23a; }

  .task-card-title {
    flex: 1;
    font-size: 14px;
    color: #303133;
    line-height: 1.4;
    word-break: break-word;
  }

  .task-card-title.completed {
    text-decoration: line-through;
    color: #909399;
  }

  .task-card-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 8px;
  }

  .task-card-due {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #909399;
  }

  .task-card-due.overdue {
    color: #f56c6c;
    font-weight: 500;
  }

  .task-card-progress {
    display: flex;
    align-items: center;
    gap: 6px;
    flex: 1;
    max-width: 140px;
  }

  .task-card-progress .progress-text {
    font-size: 12px;
    color: #909399;
    min-width: 32px;
  }

  .task-card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 8px;
  }

  .task-card-actions {
    display: flex;
    justify-content: flex-end;
    gap: 4px;
    padding-top: 6px;
    border-top: 1px solid #f5f5f5;
  }

  .empty-state {
    background: #fff;
    border-radius: 12px;
    padding: 32px 16px;
  }

  .kanban-content {
    flex-direction: column;
    overflow-x: visible;
  }

  .kanban-column {
    flex: 0 0 auto;
    width: 100%;
    max-height: none;
  }

  .batch-actions {
    bottom: 16px;
    padding: 10px 16px;
    font-size: 13px;
    width: calc(100% - 32px);
    max-width: 400px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .batch-actions .el-button {
    padding: 6px 8px;
    font-size: 12px;
  }
}

@media screen and (max-width: 480px) {
  .header-left .el-radio-group :deep(.el-radio-button__inner) {
    padding: 6px 8px;
    font-size: 12px;
  }
}
</style>
