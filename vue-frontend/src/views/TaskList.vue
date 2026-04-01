<template>
  <div class="task-list">
    <div class="task-list-header">
      <h2>任务管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建任务
        </el-button>
        <el-button type="success" @click="exportTasks('csv')">
          <el-icon><Download /></el-icon>
          导出CSV
        </el-button>
        <el-button type="success" @click="exportTasks('xlsx')">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card shadow="never" class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="项目">
          <el-select v-model="filterForm.project_id" placeholder="选择项目" clearable>
            <el-option 
              v-for="project in projects" 
              :key="project.id" 
              :label="project.name" 
              :value="project.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="选择状态" clearable>
            <el-option label="待处理" value="TODO" />
            <el-option label="进行中" value="IN_PROGRESS" />
            <el-option label="审核中" value="REVIEW" />
            <el-option label="已完成" value="DONE" />
            <el-option label="阻塞" value="BLOCKED" />
            <el-option label="已取消" value="CANCELLED" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="优先级">
          <el-select v-model="filterForm.priority" placeholder="选择优先级" clearable>
            <el-option label="低" value="LOW" />
            <el-option label="中" value="MEDIUM" />
            <el-option label="高" value="HIGH" />
            <el-option label="紧急" value="URGENT" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="负责人">
          <el-select v-model="filterForm.assignee_id" placeholder="选择负责人" clearable>
            <el-option 
              v-for="user in users" 
              :key="user.id" 
              :label="user.username" 
              :value="user.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="创建者">
          <el-select v-model="filterForm.creator_id" placeholder="选择创建者" clearable>
            <el-option 
              v-for="user in users" 
              :key="user.id" 
              :label="user.username" 
              :value="user.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="搜索">
          <el-input 
            v-model="filterForm.search" 
            placeholder="搜索任务标题或描述" 
            style="width: 200px"
            @keyup.enter="fetchTasks"
          >
            <template #append>
              <el-button @click="fetchTasks">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="fetchTasks">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 任务表格 -->
    <el-card shadow="never">
      <el-table :data="tasks" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="title" label="任务标题" min-width="200">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link 
              size="small" 
              @click="viewTaskDetail(row)"
            >
              {{ row.title }}
            </el-button>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="project_name" label="项目" width="120" />
        
        <el-table-column prop="assignee_name" label="负责人" width="100" />
        
        <el-table-column prop="progress" label="进度" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :show-text="false" />
          </template>
        </el-table-column>
        
        <el-table-column prop="start_date" label="开始日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.start_date) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="due_date" label="截止日期" width="120">
          <template #default="{ row }">
            <span :class="{ 'overdue': row.is_overdue && row.status !== 'DONE' }">
              {{ formatDate(row.due_date) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="actual_hours" label="实际时长" width="100">
          <template #default="{ row }">
            {{ row.actual_hours ? `${row.actual_hours}h` : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="tags" label="标签" width="120">
          <template #default="{ row }">
            <div v-if="row.tags" class="tags-container">
              <el-tag 
                v-for="tag in getTagsArray(row.tags)" 
                :key="tag" 
                size="small" 
                style="margin: 2px;"
              >
                {{ tag.trim() }}
              </el-tag>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="depends_on" label="依赖" width="100">
          <template #default="{ row }">
            <el-tooltip 
              v-if="row.depends_on" 
              :content="getDependencyTooltip(row)" 
              placement="top"
            >
              <el-badge :value="getDependencyCount(row.depends_on)" type="warning">
                <el-tag size="small">依赖</el-tag>
              </el-badge>
            </el-tooltip>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link 
              size="small" 
              @click="editTask(row)"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small" 
              @click="deleteTask(row)"
            >
              删除
            </el-button>
            <el-button 
              type="warning" 
              link 
              size="small" 
              @click="updateTaskStatus(row)"
            >
              更新状态
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 创建/编辑任务对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingTask ? '编辑任务' : '新建任务'"
      width="600px"
    >
      <el-form 
        ref="taskFormRef" 
        :model="taskForm" 
        :rules="taskRules" 
        label-width="100px"
      >
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>
        
        <el-form-item label="任务描述" prop="description">
          <el-input 
            v-model="taskForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入任务描述" 
          />
        </el-form-item>
        
        <el-form-item label="项目" prop="project_id">
          <el-select v-model="taskForm.project_id" placeholder="请选择项目">
            <el-option 
              v-for="project in projects" 
              :key="project.id" 
              :label="project.name" 
              :value="project.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="taskForm.priority" placeholder="请选择优先级">
            <el-option label="低" value="LOW" />
            <el-option label="中" value="MEDIUM" />
            <el-option label="高" value="HIGH" />
            <el-option label="紧急" value="URGENT" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="taskForm.status" placeholder="请选择状态">
            <el-option label="待处理" value="TODO" />
            <el-option label="进行中" value="IN_PROGRESS" />
            <el-option label="审核中" value="REVIEW" />
            <el-option label="已完成" value="DONE" />
            <el-option label="阻塞" value="BLOCKED" />
            <el-option label="已取消" value="CANCELLED" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="负责人" prop="assignee_id">
          <el-select v-model="taskForm.assignee_id" placeholder="请选择负责人" clearable>
            <el-option 
              v-for="user in users" 
              :key="user.id" 
              :label="user.username" 
              :value="user.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="截止日期" prop="due_date">
          <el-date-picker 
            v-model="taskForm.due_date" 
            type="date" 
            placeholder="请选择截止日期" 
            style="width: 100%" 
            format="YYYY/MM/DD" 
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker 
            v-model="taskForm.start_date" 
            type="date" 
            placeholder="请选择开始日期" 
            style="width: 100%" 
            format="YYYY/MM/DD" 
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="预计时长" prop="estimated_hours">
          <el-input-number 
            v-model="taskForm.estimated_hours" 
            :min="0" 
            :step="0.5" 
            placeholder="请输入预计时长"
          />
          <span style="margin-left: 8px">小时</span>
        </el-form-item>
        
        <el-form-item label="实际时长" prop="actual_hours">
          <el-input-number 
            v-model="taskForm.actual_hours" 
            :min="0" 
            :step="0.5" 
            placeholder="请输入实际时长"
          />
          <span style="margin-left: 8px">小时</span>
        </el-form-item>
        
        <el-form-item label="进度" prop="progress">
          <el-slider v-model="taskForm.progress" :step="10" show-stops />
          <span style="margin-left: 8px">{{ taskForm.progress }}%</span>
        </el-form-item>
        
        <el-form-item label="父任务" prop="parent_task_id">
          <el-select v-model="taskForm.parent_task_id" placeholder="请选择父任务" clearable>
            <el-option 
              v-for="task in tasks" 
              :key="task.id" 
              :label="task.title" 
              :value="task.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="依赖任务" prop="depends_on">
          <el-select 
            v-model="taskForm.depends_on" 
            multiple 
            placeholder="请选择依赖的任务"
            clearable
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="2"
          >
            <el-option 
              v-for="task in availableDepTasks" 
              :key="task.id" 
              :label="task.title" 
              :value="task.id"
            >
              <span>{{ task.title }}</span>
              <el-tag v-if="task.status !== 'DONE'" type="warning" size="small" style="margin-left: 8px">
                {{ getStatusText(task.status) }}
              </el-tag>
              <el-tag v-else type="success" size="small" style="margin-left: 8px">
                {{ getStatusText(task.status) }}
              </el-tag>
            </el-option>
          </el-select>
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">
            选择此任务所依赖的前置任务，依赖任务未完成时无法将状态变更为"已完成"
          </div>
        </el-form-item>
        
        <el-form-item label="关联缺陷" prop="related_bug_id">
          <el-input v-model="taskForm.related_bug_id" placeholder="请输入关联缺陷ID" />
        </el-form-item>
        
        <el-form-item label="里程碑" prop="milestone">
          <el-input v-model="taskForm.milestone" placeholder="请输入里程碑" />
        </el-form-item>
        
        <el-form-item label="标签" prop="tags">
          <el-input v-model="taskForm.tags" placeholder="请输入标签，多个标签用逗号分隔" />
        </el-form-item>
        
        <el-form-item label="参与者" prop="participants">
          <el-select 
            v-model="selectedParticipants" 
            multiple 
            filterable 
            placeholder="请选择参与者"
            style="width: 100%"
          >
            <el-option 
              v-for="user in users" 
              :key="user.id" 
              :label="user.username" 
              :value="user.id" 
            />
          </el-select>
          <div style="margin-top: 8px; font-size: 12px; color: #909399;">
            已选择 {{ selectedParticipants.length }} 名参与者
          </div>
        </el-form-item>
      </el-form>
    
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="submitTaskForm">
            {{ editingTask ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.tags-container {
  display: flex;
  flex-wrap: wrap;
  max-width: 120px;
}

.overdue {
  color: #f56c6c;
  font-weight: bold;
}

.task-list {
  padding: 20px;
}

.task-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.progress-text {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}
</style>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Plus, Search } from '@element-plus/icons-vue'
import { apiService as api } from '@/services/api'

const router = useRouter()
const loading = ref(false)
const tasks = ref([])
const projects = ref([])
const users = ref([])
const showCreateDialog = ref(false)
const editingTask = ref(null)
const taskFormRef = ref(null)

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 参与者选择
const selectedParticipants = ref([])

const filterForm = reactive({
  project_id: '',
  status: '',
  priority: '',
  assignee_id: '',
  creator_id: '',
  search: ''
})

const taskForm = reactive({
  title: '',
  description: '',
  project_id: '',
  priority: 'MEDIUM',
  status: 'TODO',
  assignee_id: '',
  due_date: '',
  start_date: '',
  estimated_hours: 0,
  actual_hours: 0,
  progress: 0,
  parent_task_id: '',
  related_bug_id: '',
  milestone: '',
  tags: '',
  participants: ''
})

const taskRules = {
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' },
    { min: 2, max: 100, message: '任务标题长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  project_id: [
    { required: true, message: '请选择项目', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 获取任务列表
const fetchTasks = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      per_page: pagination.pageSize,
      ...filterForm
    }
    
    // 移除空值参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const response = await api.tasks.getList(params)
    tasks.value = response.tasks || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取任务列表失败:', error)
    ElMessage.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

// 获取项目列表
const fetchProjects = async () => {
  try {
    const response = await api.projects.getList({ per_page: 1000 })
    projects.value = response.projects || []
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

// 获取用户列表
const fetchUsers = async () => {
  try {
    const response = await api.users.getList({ per_page: 1000 })
    users.value = response.users || []
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

// 创建任务
const createTask = async (data) => {
  try {
    await api.tasks.create(data)
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
    resetTaskForm()
    fetchTasks()
  } catch (error) {
    console.error('创建任务失败:', error)
    ElMessage.error('创建任务失败')
  }
}

// 更新任务
const updateTask = async (id, data) => {
  try {
    await api.tasks.update(id, data)
    ElMessage.success('任务更新成功')
    showCreateDialog.value = false
    resetTaskForm()
    fetchTasks()
  } catch (error) {
    console.error('更新任务失败:', error)
    ElMessage.error('更新任务失败')
  }
}

// 删除任务
const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${task.title}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.tasks.delete(task.id)
    ElMessage.success('任务删除成功')
    fetchTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
      ElMessage.error('删除任务失败')
    }
  }
}

// 更新任务状态
const updateTaskStatus = async (task) => {
  try {
    const statusOptions = [
      { label: '待处理', value: 'TODO' },
      { label: '进行中', value: 'IN_PROGRESS' },
      { label: '审核中', value: 'REVIEW' },
      { label: '已完成', value: 'DONE' },
      { label: '阻塞', value: 'BLOCKED' },
      { label: '已取消', value: 'CANCELLED' }
    ]
    
    const { value: newStatus } = await ElMessageBox.prompt(
      `请选择任务 "${task.title}" 的新状态`,
      '更新任务状态',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'select',
        inputOptions: statusOptions.reduce((acc, option) => {
          acc[option.value] = option.label
          return acc
        }, {})
      }
    )
    
    try {
      await api.tasks.updateStatus(task.id, newStatus)
      ElMessage.success('任务状态更新成功')
      fetchTasks()
    } catch (error) {
      if (error.response && error.response.data && error.response.data.incomplete_dependencies) {
        const deps = error.response.data.incomplete_dependencies
        const depList = deps.map(d => `- ${d.title} (${getStatusText(d.status)})`).join('\n')
        ElMessageBox.alert(
          `以下依赖任务尚未完成，无法将状态变更为"已完成"：\n\n${depList}`,
          '存在未完成的依赖任务',
          {
            confirmButtonText: '确定',
            type: 'warning'
          }
        )
      } else {
        throw error
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('更新任务状态失败:', error)
      ElMessage.error(error.response?.data?.error || '更新任务状态失败')
    }
  }
}

// 查看任务详情
const viewTaskDetail = (task) => {
  router.push(`/tasks/${task.id}`)
}

// 编辑任务
const editTask = (task) => {
  editingTask.value = task
  taskForm.title = task.title
  taskForm.description = task.description || ''
  taskForm.project_id = task.project_id
  taskForm.priority = task.priority
  taskForm.status = task.status
  taskForm.assignee_id = task.assignee_id || ''
  taskForm.due_date = task.due_date || ''
  taskForm.start_date = task.start_date || ''
  taskForm.estimated_hours = task.estimated_hours || 0
  taskForm.actual_hours = task.actual_hours || 0
  taskForm.progress = task.progress || 0
  taskForm.parent_task_id = task.parent_task_id || ''
  taskForm.related_bug_id = task.related_bug_id || ''
  taskForm.milestone = task.milestone || ''
  taskForm.tags = task.tags || ''
  taskForm.participants = task.participants || ''
  
  // 处理参与者选择
  if (task.participants) {
    try {
      const participantsArray = JSON.parse(task.participants)
      selectedParticipants.value = participantsArray
    } catch (error) {
      console.error('解析参与者数据失败:', error)
      selectedParticipants.value = []
    }
  } else {
    selectedParticipants.value = []
  }
  
  showCreateDialog.value = true
}

// 提交任务表单
const submitTaskForm = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    
    const formData = { 
      ...taskForm,
      // 处理参与者数据，转换为JSON字符串
      participants: selectedParticipants.value.length > 0 
        ? JSON.stringify(selectedParticipants.value) 
        : null
    }
    
    if (editingTask.value) {
      await updateTask(editingTask.value.id, formData)
    } else {
      await createTask(formData)
    }
  } catch (error) {
    // 表单验证失败
  }
}

// 重置任务表单
const resetTaskForm = () => {
  taskForm.title = ''
  taskForm.description = ''
  taskForm.project_id = ''
  taskForm.priority = 'MEDIUM'
  taskForm.status = 'TODO'
  taskForm.assignee_id = ''
  taskForm.due_date = ''
  taskForm.start_date = ''
  taskForm.estimated_hours = 0
  taskForm.actual_hours = 0
  taskForm.progress = 0
  taskForm.parent_task_id = ''
  taskForm.related_bug_id = ''
  taskForm.milestone = ''
  taskForm.tags = ''
  taskForm.participants = ''
  selectedParticipants.value = []
  editingTask.value = null
  if (taskFormRef.value) {
    taskFormRef.value.resetFields()
  }
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.project_id = ''
  filterForm.status = ''
  filterForm.priority = ''
  filterForm.assignee_id = ''
  filterForm.creator_id = ''
  filterForm.search = ''
  fetchTasks()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  fetchTasks()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchTasks()
}

// 状态类型映射
const getStatusType = (status) => {
  const typeMap = {
    'TODO': 'info',
    'IN_PROGRESS': 'warning',
    'REVIEW': 'primary',
    'DONE': 'success',
    'BLOCKED': 'danger',
    'CANCELLED': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'TODO': '待处理',
    'IN_PROGRESS': '进行中',
    'REVIEW': '审核中',
    'DONE': '已完成',
    'BLOCKED': '阻塞',
    'CANCELLED': '已取消'
  }
  return textMap[status] || status
}

// 优先级类型映射
const getPriorityType = (priority) => {
  const typeMap = {
    'LOW': 'info',
    'MEDIUM': '',
    'HIGH': 'warning',
    'URGENT': 'danger'
  }
  return typeMap[priority] || ''
}

const getPriorityText = (priority) => {
  const textMap = {
    'LOW': '低',
    'MEDIUM': '中',
    'HIGH': '高',
    'URGENT': '紧急'
  }
  return textMap[priority] || priority
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 导出任务数据
const exportTasks = async (format) => {
  try {
    ElMessage.info('导出功能开发中...')
  } catch (error) {
    console.error('导出任务数据失败:', error)
    ElMessage.error('导出任务数据失败')
  }
}

// 处理标签字符串转换为数组
const getTagsArray = (tagsString) => {
  if (!tagsString) return []
  return tagsString.split(',').filter(tag => tag.trim() !== '')
}

// 获取依赖任务数量
const getDependencyCount = (dependsOn) => {
  if (!dependsOn) return 0
  try {
    const deps = typeof dependsOn === 'string' ? JSON.parse(dependsOn) : dependsOn
    return Array.isArray(deps) ? deps.length : 0
  } catch {
    return 0
  }
}

// 获取依赖任务提示信息
const getDependencyTooltip = (row) => {
  if (!row.depends_on) return ''
  try {
    const depIds = typeof row.depends_on === 'string' ? JSON.parse(row.depends_on) : row.depends_on
    if (!Array.isArray(depIds) || depIds.length === 0) return ''
    
    const depTasks = depIds.map(id => {
      const task = tasks.value.find(t => t.id === id)
      if (task) {
        const statusText = getStatusText(task.status)
        const statusType = task.status === 'DONE' ? '✓' : '✗'
        return `${statusType} ${task.title} (${statusText})`
      }
      return `未知任务 #${id}`
    })
    return depTasks.join('\n')
  } catch {
    return ''
  }
}

// 可选的依赖任务列表（排除自身和已完成的任务，仅显示未完成的任务供选择）
const availableDepTasks = computed(() => {
  if (!editingTask.value) {
    return tasks.value.filter(t => t.status !== 'DONE')
  }
  return tasks.value.filter(t => t.id !== editingTask.value.id && t.status !== 'DONE')
})

// 监听筛选条件变化
watch(filterForm, () => {
  pagination.currentPage = 1
  fetchTasks()
}, { deep: true })

onMounted(() => {
  fetchTasks()
  fetchProjects()
  fetchUsers()
})
</script>

<style scoped>
.task-list {
  padding: 20px;
}

.task-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.overdue {
  color: #f56c6c;
  font-weight: bold;
}

@media screen and (max-width: 768px) {
  .task-list {
    padding: 12px;
  }

  .task-list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .task-list-header h2 {
    font-size: 18px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    max-width: calc(50% - 4px);
    font-size: 12px;
    padding: 8px 12px;
  }

  .filter-card {
    margin-bottom: 16px;
  }

  .filter-card .el-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .filter-card .el-form-item {
    margin-bottom: 0;
    width: 100%;
  }

  .filter-card .el-select,
  .filter-card .el-input {
    width: 100% !important;
  }

  .pagination-container {
    margin-top: 16px;
    text-align: center;
  }
}

@media screen and (max-width: 480px) {
  .task-list {
    padding: 8px;
  }

  .task-list-header h2 {
    font-size: 16px;
  }

  .header-actions .el-button {
    max-width: 100%;
    flex: none;
    width: 100%;
  }
}
</style>