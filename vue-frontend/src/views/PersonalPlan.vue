<template>
  <div class="personal-plan-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Calendar /></el-icon>
          </div>
          <div class="title-text">
            <h1>工作计划</h1>
            <p class="subtitle">管理您的个人任务和计划</p>
          </div>
        </div>
        <div class="header-actions">
          <el-input
            v-model="searchQuery"
            placeholder="搜索任务..."
            class="search-input"
            clearable
            :prefix-icon="Search"
          />
          <el-button type="primary" @click="showCreateDialog" class="btn-gradient">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalCount }}</div>
              <div class="stat-label">总计划数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-progress">
            <div class="stat-icon-wrapper stat-icon-wrapper-progress">
              <el-icon><Loading /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ inProgressCount }}</div>
              <div class="stat-label">进行中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-completed">
            <div class="stat-icon-wrapper stat-icon-wrapper-completed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ completedCount }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-overdue">
            <div class="stat-icon-wrapper stat-icon-wrapper-overdue">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overdueCount }}</div>
              <div class="stat-label">延期</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-section animate-fade-in-up delay-200">
      <el-card class="filter-card glass-card" shadow="hover">
        <div class="filter-bar">
          <el-radio-group v-model="statusFilter" size="small">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="todo">待处理</el-radio-button>
            <el-radio-button label="in_progress">进行中</el-radio-button>
            <el-radio-button label="done">已完成</el-radio-button>
          </el-radio-group>
          <span class="task-count">共 {{ filteredTasks.length }} 项任务</span>
        </div>
      </el-card>
    </div>

    <!-- 任务列表 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card task-list-card" shadow="hover">
        <div class="task-list">
          <div v-if="filteredTasks.length === 0" class="empty-state">
            <el-empty description="暂无任务" :image-size="120">
              <el-button type="primary" @click="showCreateDialog" class="btn-gradient">创建第一个任务</el-button>
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
      </el-card>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑任务' : '新建任务'"
      width="560px"
      destroy-on-close
      class="task-dialog"
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
        <el-button type="primary" @click="saveTask" :loading="saving" class="btn-gradient">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      :title="currentTask?.title || '任务详情'"
      width="600px"
      destroy-on-close
      class="task-dialog"
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
        <el-button type="primary" @click="editFromDetail" class="btn-gradient">编辑</el-button>
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
  MoreFilled,
  List,
  Loading,
  CircleCheck,
  Warning
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

// 统计数据计算
const totalCount = computed(() => tasks.value.length)
const inProgressCount = computed(() => tasks.value.filter(t => t.status === 'in_progress').length)
const completedCount = computed(() => tasks.value.filter(t => t.status === 'done').length)
const overdueCount = computed(() => tasks.value.filter(t => isOverdue(t)).length)

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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.personal-plan-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(102, 126, 234, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(118, 75, 162, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.page-header::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
  pointer-events: none;
}

.header-bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
}

.orb-1 {
  width: 200px;
  height: 200px;
  background: #f093fb;
  top: -50px;
  right: 10%;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 150px;
  height: 150px;
  background: #4facfe;
  bottom: -30px;
  right: 30%;
  animation: float 8s ease-in-out infinite reverse;
}

.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-icon-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.title-icon {
  font-size: 32px;
  color: white;
}

.title-text h1 {
  margin: 0 0 6px 0;
  color: white;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 400;
}

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  width: 280px;
}

.search-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.stat-card::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  transform: scaleX(0);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15), 0 10px 20px -5px rgba(0, 0, 0, 0.1);
}

.stat-card:hover::before {
  transform: scaleX(1);
}

.stat-card-total::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card-progress::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.stat-card-completed::before { background: linear-gradient(90deg, #10b981, #34d399); }
.stat-card-overdue::before { background: linear-gradient(90deg, #ef4444, #f87171); }

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.4s;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #667eea;
  box-shadow: 0 4px 15px -3px rgba(102, 126, 234, 0.4);
}

.stat-icon-wrapper-progress {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #3b82f6;
  box-shadow: 0 4px 15px -3px rgba(59, 130, 246, 0.4);
}

.stat-icon-wrapper-completed {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #10b981;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-overdue {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #ef4444;
  box-shadow: 0 4px 15px -3px rgba(239, 68, 68, 0.4);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-progress .stat-value {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-completed .stat-value {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-overdue .stat-value {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s;
}

.glass-card:hover {
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 10px 20px -5px rgba(0, 0, 0, 0.08);
}

/* 筛选区域 */
.filter-section {
  margin-bottom: 24px;
}

.filter-card :deep(.el-card__body) {
  padding: 16px 20px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-count {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
  background: rgba(241, 245, 249, 0.8);
  padding: 6px 14px;
  border-radius: 20px;
}

/* 内容区域 */
.content-section {
  margin-bottom: 20px;
}

.task-list-card :deep(.el-card__body) {
  padding: 0;
}

.task-list {
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
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.5);
}

.task-item:last-child {
  border-bottom: none;
}

.task-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateX(4px);
}

.task-item.completed {
  opacity: 0.7;
  background: rgba(248, 250, 252, 0.8);
}

.task-item.completed .task-title {
  text-decoration: line-through;
  color: #94a3b8;
}

.task-item.overdue {
  background: rgba(254, 242, 242, 0.8);
  border-left: 3px solid #ef4444;
}

.task-item.overdue:hover {
  background: rgba(254, 226, 226, 0.9);
}

.task-checkbox {
  flex-shrink: 0;
}

.task-checkbox :deep(.el-checkbox__inner) {
  width: 20px;
  height: 20px;
  border-radius: 6px;
}

.task-checkbox :deep(.el-checkbox__inner::after) {
  left: 6px;
  top: 3px;
}

.task-content {
  flex: 1;
  cursor: pointer;
  min-width: 0;
}

.task-main {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.priority-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.priority-dot.urgent {
  background: linear-gradient(135deg, #ef4444, #f87171);
}

.priority-dot.high {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.priority-dot.medium {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.priority-dot.low {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.task-title {
  font-size: 15px;
  color: #1e293b;
  font-weight: 600;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-tag {
  flex-shrink: 0;
  border-radius: 6px;
  font-weight: 500;
}

.task-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #64748b;
  margin-left: 20px;
}

.task-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.task-meta .el-icon {
  font-size: 14px;
}

.due-date.overdue {
  color: #ef4444;
  font-weight: 600;
}

.task-actions {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.3s;
}

.task-item:hover .task-actions {
  opacity: 1;
}

/* 详情信息 */
.detail-info {
  padding: 10px 0;
}

.info-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  line-height: 1.6;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  width: 80px;
  color: #64748b;
  font-size: 14px;
  flex-shrink: 0;
  font-weight: 500;
}

.info-row .value {
  color: #1e293b;
  font-size: 14px;
  flex: 1;
  word-break: break-all;
}

.info-row .value.overdue {
  color: #ef4444;
  font-weight: 600;
}

.detail-tag {
  margin-right: 6px;
  border-radius: 6px;
}

.unit-text {
  margin-left: 8px;
  color: #64748b;
  font-size: 13px;
}

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.5);
}

/* 对话框样式 */
.task-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 24px;
  margin-right: 0;
}

.task-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.task-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: rgba(255, 255, 255, 0.8);
}

.task-dialog :deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: white;
}

.task-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-fade-in-down {
  animation: fadeInDown 0.6s ease-out;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out;
  animation-fill-mode: both;
}

.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .personal-plan-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }

  .header-title {
    gap: 14px;
  }

  .title-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 14px;
  }

  .title-icon {
    font-size: 24px;
  }

  .title-text h1 {
    font-size: 22px;
  }

  .subtitle {
    font-size: 13px;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .stats-row {
    margin-bottom: 20px;
  }

  .stat-card {
    padding: 16px;
    gap: 12px;
    margin-bottom: 12px;
  }

  .stat-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  .filter-bar {
    flex-direction: column;
    gap: 12px;
  }

  .task-meta {
    flex-wrap: wrap;
    gap: 10px;
  }

  .task-actions {
    opacity: 1;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-value {
    font-size: 20px;
  }

  .task-item {
    padding: 12px 16px;
  }

  .task-title {
    font-size: 14px;
  }
}
</style>
