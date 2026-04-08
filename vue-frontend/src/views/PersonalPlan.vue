<template>
  <div class="personal-plan-container">
    <div class="page-header">
      <h2 class="page-title">工作计划</h2>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索任务..."
          class="search-input"
          clearable
          :prefix-icon="Search"
        />
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新建任务
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-radio-group v-model="statusFilter" size="small">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="todo">待处理</el-radio-button>
        <el-radio-button label="in_progress">进行中</el-radio-button>
        <el-radio-button label="done">已完成</el-radio-button>
      </el-radio-group>
      <span class="task-count">共 {{ filteredTasks.length }} 项任务</span>
    </div>

    <div class="task-list">
      <div v-if="filteredTasks.length === 0" class="empty-state">
        <el-empty description="暂无任务" :image-size="120">
          <el-button type="primary" @click="showCreateDialog">创建第一个任务</el-button>
        </el-empty>
      </div>

      <div v-else class="task-items">
        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="task-item"
          :class="{ completed: task.status === 'done', overdue: isOverdue(task) }"
        >
          <div class="task-checkbox">
            <el-checkbox
              :model-value="task.status === 'done'"
              @change="toggleTaskStatus(task)"
            />
          </div>

          <div class="task-content" @click="openTaskDetail(task)">
            <div class="task-main">
              <span class="priority-dot" :class="task.priority"></span>
              <span class="task-title">{{ task.title }}</span>
              <el-tag v-if="task.tags" size="small" type="info" class="task-tag">
                {{ task.tags.split(',')[0] }}
              </el-tag>
            </div>

            <div class="task-meta">
              <span v-if="task.due_date" class="due-date" :class="{ overdue: isOverdue(task) }">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(task.due_date) }}
              </span>
              <span v-if="task.estimated_minutes" class="duration">
                <el-icon><Clock /></el-icon>
                {{ task.estimated_minutes }}分钟
              </span>
            </div>
          </div>

          <div class="task-actions">
            <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, task)">
              <el-button text size="small">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">
                    <el-icon><Edit /></el-icon>编辑
                  </el-dropdown-item>
                  <el-dropdown-item command="copy">
                    <el-icon><CopyDocument /></el-icon>复制
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>
                    <el-icon><Delete /></el-icon>删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑任务' : '新建任务'"
      width="560px"
      destroy-on-close
    >
      <el-form :model="taskForm" label-width="80px" ref="formRef">
        <el-form-item label="任务标题" prop="title" :rules="[{ required: true, message: '请输入任务标题' }]">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>

        <el-form-item label="任务描述">
          <el-input
            v-model="taskForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述（可选）"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="taskForm.priority" placeholder="选择优先级">
                <el-option label="紧急" value="urgent" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="taskForm.status" placeholder="选择状态">
                <el-option label="待处理" value="todo" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="done" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="截止日期">
              <el-date-picker
                v-model="taskForm.due_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预估时长">
              <el-input-number
                v-model="taskForm.estimated_minutes"
                :min="5"
                :step="5"
                :max="480"
                style="width: 100%"
              />
              <span class="unit-text">分钟</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="标签">
          <el-input v-model="taskForm.tags" placeholder="多个标签用逗号分隔（可选）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTask" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      :title="currentTask?.title || '任务详情'"
      width="600px"
      destroy-on-close
    >
      <div class="task-detail" v-if="currentTask">
        <div class="detail-info">
          <div class="info-row">
            <span class="label">状态：</span>
            <el-tag :type="getStatusType(currentTask.status)" size="small">
              {{ getStatusLabel(currentTask.status) }}
            </el-tag>
          </div>
          <div class="info-row">
            <span class="label">优先级：</span>
            <el-tag :type="getPriorityType(currentTask.priority)" size="small">
              {{ getPriorityLabel(currentTask.priority) }}
            </el-tag>
          </div>
          <div class="info-row" v-if="currentTask.description">
            <span class="label">描述：</span>
            <span class="value">{{ currentTask.description }}</span>
          </div>
          <div class="info-row" v-if="currentTask.due_date">
            <span class="label">截止日期：</span>
            <span class="value" :class="{ overdue: isOverdue(currentTask) }">
              {{ formatDate(currentTask.due_date) }}
            </span>
          </div>
          <div class="info-row" v-if="currentTask.estimated_minutes">
            <span class="label">预估时长：</span>
            <span class="value">{{ currentTask.estimated_minutes }} 分钟</span>
          </div>
          <div class="info-row" v-if="currentTask.tags">
            <span class="label">标签：</span>
            <el-tag
              v-for="tag in currentTask.tags.split(',').filter(t => t.trim())"
              :key="tag"
              size="small"
              type="info"
              class="detail-tag"
            >
              #{{ tag.trim() }}
            </el-tag>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="editFromDetail">编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Plus,
  Calendar,
  Clock,
  Edit,
  Delete,
  CopyDocument,
  MoreFilled
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const searchQuery = ref('')
const statusFilter = ref('')
const tasks = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const currentTask = ref(null)
const saving = ref(false)
const formRef = ref(null)

const taskForm = reactive({
  title: '',
  description: '',
  priority: 'medium',
  status: 'todo',
  due_date: '',
  estimated_minutes: 30,
  tags: ''
})

const filteredTasks = computed(() => {
  let result = tasks.value

  if (statusFilter.value) {
    result = result.filter(t => t.status === statusFilter.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(t =>
      t.title.toLowerCase().includes(query) ||
      t.description?.toLowerCase().includes(query) ||
      t.tags?.toLowerCase().includes(query)
    )
  }

  return result.sort((a, b) => {
    const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 }
    return (priorityOrder[a.priority] || 99) - (priorityOrder[b.priority] || 99)
  })
})

const loadTasks = async () => {
  try {
    const response = await apiService.personalPlan.getTasks()
    const data = response?.data || response
    tasks.value = Array.isArray(data?.tasks) ? data.tasks : (Array.isArray(data) ? data : [])
  } catch (error) {
    console.error('加载任务失败:', error)
    tasks.value = []
  }
}

const showCreateDialog = () => {
  isEditing.value = false
  editingId.value = null
  Object.assign(taskForm, {
    title: '',
    description: '',
    priority: 'medium',
    status: 'todo',
    due_date: '',
    estimated_minutes: 30,
    tags: ''
  })
  dialogVisible.value = true
}

const saveTask = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  saving.value = true
  try {
    if (isEditing.value && editingId.value) {
      await apiService.personalPlan.updateTask(editingId.value, taskForm)
      ElMessage.success('任务已更新')
    } else {
      const createData = {
        content: taskForm.title,
        description: taskForm.description,
        priority: taskForm.priority,
        estimated_minutes: taskForm.estimated_minutes,
        due_date: taskForm.due_date,
        tags: taskForm.tags
      }
      await apiService.personalPlan.createTask(createData)
      ElMessage.success('任务已创建')
    }
    dialogVisible.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error(isEditing.value ? '更新失败' : '创建失败')
  } finally {
    saving.value = false
  }
}

const toggleTaskStatus = async (task) => {
  try {
    const newStatus = task.status === 'done' ? 'todo' : 'done'
    await apiService.personalPlan.updateTask(task.id, { status: newStatus })
    ElMessage.success(newStatus === 'done' ? '任务已完成' : '任务已重新打开')
    loadTasks()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const openTaskDetail = (task) => {
  currentTask.value = { ...task }
  detailVisible.value = true
}

const editFromDetail = () => {
  if (!currentTask.value) return

  isEditing.value = true
  editingId.value = currentTask.value.id
  Object.assign(taskForm, {
    title: currentTask.value.title || '',
    description: currentTask.value.description || '',
    priority: currentTask.value.priority || 'medium',
    status: currentTask.value.status || 'todo',
    due_date: currentTask.value.due_date || '',
    estimated_minutes: currentTask.value.estimated_minutes || 30,
    tags: currentTask.value.tags || ''
  })
  detailVisible.value = false
  dialogVisible.value = true
}

const handleCommand = async (command, task) => {
  switch (command) {
    case 'edit':
      isEditing.value = true
      editingId.value = task.id
      Object.assign(taskForm, {
        title: task.title || '',
        description: task.description || '',
        priority: task.priority || 'medium',
        status: task.status || 'todo',
        due_date: task.due_date || '',
        estimated_minutes: task.estimated_minutes || 30,
        tags: task.tags || ''
      })
      dialogVisible.value = true
      break

    case 'copy':
      try {
        await apiService.personalPlan.createTask({
          content: task.title + ' (副本)',
          description: task.description,
          priority: task.priority,
          estimated_minutes: task.estimated_minutes,
          tags: task.tags,
          due_date: task.due_date
        })
        ElMessage.success('任务已复制')
        loadTasks()
      } catch (error) {
        ElMessage.error('复制失败')
      }
      break

    case 'delete':
      try {
        await ElMessageBox.confirm('确定要删除这个任务吗？', '提示', {
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
      break
  }
}

const isOverdue = (task) => {
  if (!task.due_date || task.status === 'done') return false
  return new Date(task.due_date) < new Date(new Date().toDateString())
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const getPriorityType = (priority) => {
  const types = { urgent: 'danger', high: 'warning', medium: '', low: 'success' }
  return types[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const labels = { urgent: '紧急', high: '高', medium: '中', low: '低' }
  return labels[priority] || priority
}

const getStatusType = (status) => {
  const types = { todo: 'info', in_progress: '', review: 'warning', done: 'success' }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = { todo: '待处理', in_progress: '进行中', review: '待审核', done: '已完成' }
  return labels[status] || status
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.personal-plan-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  width: 280px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.task-count {
  font-size: 14px;
  color: #909399;
}

.task-list {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.empty-state {
  padding: 60px 20px;
}

.task-items {
  display: flex;
  flex-direction: column;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.2s;
}

.task-item:last-child {
  border-bottom: none;
}

.task-item:hover {
  background: #fafafa;
}

.task-item.completed {
  opacity: 0.6;
}

.task-item.completed .task-title {
  text-decoration: line-through;
  color: #909399;
}

.task-item.overdue {
  background: #fef0f0;
}

.task-checkbox {
  flex-shrink: 0;
}

.task-content {
  flex: 1;
  cursor: pointer;
  min-width: 0;
}

.task-main {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.priority-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.priority-dot.urgent {
  background: #f56c6c;
}

.priority-dot.high {
  background: #e6a23c;
}

.priority-dot.medium {
  background: #409eff;
}

.priority-dot.low {
  background: #67c23a;
}

.task-title {
  font-size: 15px;
  color: #303133;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-tag {
  flex-shrink: 0;
}

.task-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #909399;
  margin-left: 16px;
}

.task-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.due-date.overdue {
  color: #f56c6c;
  font-weight: 500;
}

.task-actions {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.task-item:hover .task-actions {
  opacity: 1;
}

.detail-info {
  padding: 10px 0;
}

.info-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 14px;
  line-height: 1.6;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  width: 80px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-row .value {
  color: #303133;
  font-size: 14px;
  flex: 1;
  word-break: break-all;
}

.info-row .value.overdue {
  color: #f56c6c;
  font-weight: 500;
}

.detail-tag {
  margin-right: 4px;
}

.unit-text {
  margin-left: 8px;
  color: #909399;
  font-size: 13px;
}

@media screen and (max-width: 768px) {
  .personal-plan-container {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .filter-bar {
    flex-direction: column;
    gap: 12px;
  }

  .task-meta {
    flex-wrap: wrap;
  }

  .task-actions {
    opacity: 1;
  }
}
</style>
