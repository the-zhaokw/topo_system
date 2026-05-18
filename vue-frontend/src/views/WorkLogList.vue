<template>
  <div class="work-log-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-left">
          <el-button @click="$router.push('/dashboard')" class="btn-back">
            <el-icon><ArrowLeft /></el-icon>
            返回个人工作台
          </el-button>
        </div>
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Document /></el-icon>
          </div>
          <div class="title-text">
            <h1>工作日志</h1>
            <p class="subtitle">记录和管理您的工作计划与进度</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.total_logs || 0 }}</div>
              <div class="stat-label">总日志数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-draft">
            <div class="stat-icon-wrapper stat-icon-wrapper-draft">
              <el-icon><Edit /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.draft_logs || 0 }}</div>
              <div class="stat-label">草稿</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-completed">
            <div class="stat-icon-wrapper stat-icon-wrapper-completed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.completed_logs || 0 }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-hours">
            <div class="stat-icon-wrapper stat-icon-wrapper-hours">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.total_hours || 0 }}h</div>
              <div class="stat-label">总工时</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section animate-fade-in-up delay-200">
      <el-card class="filter-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Filter /></el-icon>
              筛选条件
            </span>
          </div>
        </template>
        <el-form :model="filterForm" inline class="filter-form">
          <el-form-item label="工作日期">
            <el-date-picker
              v-model="filterForm.log_date"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              clearable
              class="filter-date-picker">
            </el-date-picker>
          </el-form-item>

          <el-form-item label="工作类型">
            <el-select v-model="filterForm.work_type" placeholder="请选择类型" clearable class="filter-select">
              <el-option label="日报" value="daily"></el-option>
              <el-option label="周报" value="weekly"></el-option>
              <el-option label="月报" value="monthly"></el-option>
              <el-option label="项目总结" value="project_summary"></el-option>
              <el-option label="其他" value="other"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="请选择状态" clearable class="filter-select">
              <el-option label="草稿" value="draft"></el-option>
              <el-option label="已完成" value="completed"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item v-if="isDepartmentManager" label="员工">
            <el-select
              v-model="filterForm.user_id"
              placeholder="请选择员工"
              clearable
              class="filter-select">
              <el-option
                v-for="user in departmentUsers"
                :key="user.id"
                :label="user.username"
                :value="user.id">
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch" :loading="loading" class="btn-gradient">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset" class="btn-secondary">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 内容区域 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><List /></el-icon>
              <h3>日志列表</h3>
              <span class="total-count">共 {{ total }} 条记录</span>
            </div>
            <div class="table-actions">
              <el-button type="primary" @click="openCreateDialog" class="btn-gradient">
                <el-icon><Plus /></el-icon>
                新增日志
              </el-button>
              <el-button @click="refreshData" :loading="loading" class="btn-refresh">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>

        <el-table
          :data="workLogs"
          v-loading="loading"
          stripe
          class="custom-table"
          style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" align="center">
            <template #default="{ row }">
              <span class="id-badge">#{{ row.id }}</span>
            </template>
          </el-table-column>

          <el-table-column label="标题" min-width="200">
            <template #default="{ row }">
              <div class="log-title" @click="viewDetail(row)">
                {{ row.title }}
              </div>
            </template>
          </el-table-column>

          <el-table-column label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getWorkTypeTag(row.work_type)" size="small" effect="light" class="work-type-tag">
                {{ getWorkTypeText(row.work_type) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column v-if="isDepartmentManager" label="员工" width="120" align="center">
            <template #default="{ row }">
              <div class="user-name">{{ row.user_name || row.username || '-' }}</div>
            </template>
          </el-table-column>

          <el-table-column label="日期" width="110" align="center">
            <template #default="{ row }">
              <span class="date-text">{{ formatDate(row.log_date) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="工时" width="90" align="center">
            <template #default="{ row }">
              <span class="hours-badge">{{ row.hours_spent || 0 }}h</span>
            </template>
          </el-table-column>

          <el-table-column label="关联项目" width="150">
            <template #default="{ row }">
              <el-link v-if="row.project_id" type="primary" @click="$router.push(`/projects/${row.project_id}`)" class="project-link">
                {{ row.project_name }}
              </el-link>
              <span v-else class="empty-text">-</span>
            </template>
          </el-table-column>

          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'completed' ? 'success' : 'warning'" size="small" effect="light" class="status-tag">
                {{ row.status === 'completed' ? '已完成' : '草稿' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="操作时间" width="160" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatDate(row.updated_at) }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="180" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewDetail(row)" class="action-btn">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button type="primary" link size="small" @click="openEditDialog(row)" class="action-btn">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)" class="action-btn">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-section">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
          </el-pagination>
        </div>
      </el-card>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增日志' : '编辑日志'"
      width="700px"
      :close-on-click-modal="false"
      class="custom-dialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入日志标题" maxlength="255"></el-input>
        </el-form-item>

        <el-form-item label="工作类型" prop="work_type">
          <el-select v-model="form.work_type" placeholder="请选择工作类型" style="width: 100%;">
            <el-option label="日报" value="daily"></el-option>
            <el-option label="周报" value="weekly"></el-option>
            <el-option label="月报" value="monthly"></el-option>
            <el-option label="项目总结" value="project_summary"></el-option>
            <el-option label="其他" value="other"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="工作日期" prop="log_date">
          <el-date-picker
            v-model="form.log_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%;">
          </el-date-picker>
        </el-form-item>

        <el-form-item v-if="['weekly', 'monthly', 'project_summary'].includes(form.work_type)" label="开始时间" prop="start_date">
          <el-date-picker
            v-model="form.start_date"
            type="date"
            placeholder="选择开始时间"
            value-format="YYYY-MM-DD"
            style="width: 100%;">
          </el-date-picker>
        </el-form-item>

        <el-form-item v-if="['weekly', 'monthly', 'project_summary'].includes(form.work_type)" label="结束时间" prop="end_date">
          <el-date-picker
            v-model="form.end_date"
            type="date"
            placeholder="选择结束时间"
            value-format="YYYY-MM-DD"
            style="width: 100%;">
          </el-date-picker>
        </el-form-item>

        <el-form-item label="工时(小时)" prop="hours_spent">
          <el-input-number v-model="form.hours_spent" :min="0" :max="24" :step="0.5" style="width: 100%;"></el-input-number>
        </el-form-item>

        <el-form-item label="关联项目" prop="project_id">
          <el-select v-model="form.project_id" placeholder="请选择关联项目" clearable style="width: 100%;">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="completed">已完成</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="8"
            placeholder="请输入工作内容..."
            maxlength="5000"
            show-word-limit>
          </el-input>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading" class="btn-gradient">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      title="工作日志详情"
      width="700px"
      class="custom-dialog">
      <div class="log-detail" v-if="currentLog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="标题" :span="2">
            {{ currentLog.title }}
          </el-descriptions-item>
          <el-descriptions-item label="工作类型">
            {{ getWorkTypeText(currentLog.work_type) }}
          </el-descriptions-item>
          <el-descriptions-item label="日期">
            {{ formatDate(currentLog.log_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="工时">
            {{ currentLog.hours_spent || 0 }}h
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentLog.status === 'completed' ? 'success' : 'warning'" size="small">
              {{ currentLog.status === 'completed' ? '已完成' : '草稿' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="关联项目" :span="2">
            <el-link v-if="currentLog.project_id" type="primary" @click="$router.push(`/projects/${currentLog.project_id}`)">
              {{ currentLog.project_name }}
            </el-link>
            <span v-else>无</span>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentLog.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(currentLog.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="内容" :span="2">
            <div class="content-box">{{ currentLog.content }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="openEditFromDetail" class="btn-gradient">
          编辑
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="activityVisible"
      title="活动记录"
      width="800px"
      class="custom-dialog">
      <div v-loading="activityLoading">
        <el-table
          v-if="activities.length > 0"
          :data="activities"
          stripe
          class="custom-table"
          style="width: 100%">
          <el-table-column label="操作类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getActionType(row.action)" size="small" effect="light">
                {{ getActionText(row.action) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="描述" min-width="300">
            <template #default="{ row }">
              {{ row.description }}
            </template>
          </el-table-column>
          <el-table-column label="时间" width="180" align="center">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无活动记录"></el-empty>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, View, Edit, Delete, ArrowLeft, Document, Clock, CircleCheck, Filter, List } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import { formatDate as formatDateUtil } from '@/utils/dateUtils'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()
const currentUser = computed(() => userStore.currentUser)
const isDepartmentManager = computed(() => {
  const user = currentUser.value
  if (!user) return false
  return user.role === 'department_manager'
})

const loading = ref(false)
const submitLoading = ref(false)
const activityLoading = ref(false)
const workLogs = ref([])
const activities = ref([])
const projects = ref([])
const departmentUsers = ref([])
const total = ref(0)
const statistics = ref({})
const dialogVisible = ref(false)
const detailVisible = ref(false)
const activityVisible = ref(false)
const dialogMode = ref('create')
const currentLog = ref(null)

const pagination = reactive({
  currentPage: 1,
  pageSize: 20
})

const filterForm = reactive({
  log_date: '',
  work_type: '',
  status: '',
  user_id: null
})

const form = reactive({
  title: '',
  content: '',
  log_date: '',
  work_type: 'daily',
  project_id: null,
  hours_spent: 0,
  status: 'draft',
  start_date: null,
  end_date: null
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
  log_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  work_type: [{ required: true, message: '请选择工作类型', trigger: 'change' }]
}

const formRef = ref(null)

watch(() => form.work_type, (newType) => {
  if (['weekly', 'monthly', 'project_summary'].includes(newType)) {
    calculateDateRange(newType)
  } else {
    form.start_date = null
    form.end_date = null
  }
})

const calculateDateRange = (workType) => {
  const today = new Date()
  if (workType === 'weekly') {
    const dayOfWeek = today.getDay() || 7
    const startOfWeek = new Date(today)
    startOfWeek.setDate(today.getDate() - dayOfWeek + 1)
    const endOfWeek = new Date(startOfWeek)
    endOfWeek.setDate(startOfWeek.getDate() + 6)
    form.start_date = startOfWeek.toISOString().split('T')[0]
    form.end_date = endOfWeek.toISOString().split('T')[0]
  } else if (workType === 'monthly') {
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
    const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
    form.start_date = startOfMonth.toISOString().split('T')[0]
    form.end_date = endOfMonth.toISOString().split('T')[0]
  } else if (workType === 'project_summary') {
    form.start_date = null
    form.end_date = null
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const getWorkTypeText = (type) => {
  const texts = {
    'daily': '日报',
    'weekly': '周报',
    'monthly': '月报',
    'project_summary': '项目总结',
    'other': '其他'
  }
  return texts[type] || type
}

const getWorkTypeTag = (type) => {
  const types = {
    'daily': '',
    'weekly': 'success',
    'monthly': 'warning',
    'project_summary': 'danger',
    'other': 'info'
  }
  return types[type] || 'info'
}

const getActionType = (action) => {
  const types = {
    'create': 'success',
    'update': 'warning',
    'delete': 'danger'
  }
  return types[action] || 'info'
}

const getActionText = (action) => {
  const texts = {
    'create': '创建',
    'update': '更新',
    'delete': '删除'
  }
  return texts[action] || action
}

const loadWorkLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      per_page: pagination.pageSize,
      ...filterForm
    }
    if (!params.user_id) {
      delete params.user_id
    }
    const response = await apiService.workLogs.getList(params)
    workLogs.value = response.logs || []
    total.value = response.total || 0
  } catch (error) {
    console.error('加载工作日志失败:', error)
    ElMessage.error('加载工作日志失败')
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const params = {}
    if (filterForm.user_id) {
      params.user_id = filterForm.user_id
    }
    const response = await apiService.workLogs.getStats(params)
    statistics.value = response || {}
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadDepartmentUsers = async () => {
  if (!isDepartmentManager.value) return
  const user = currentUser.value
  if (!user || !user.department) return
  try {
    const response = await apiService.users.getDepartmentMembers(user.department)
    departmentUsers.value = response.members || []
  } catch (error) {
    console.error('获取部门成员失败:', error)
    departmentUsers.value = []
  }
}

const loadActivities = async (logId) => {
  activityLoading.value = true
  try {
    const response = await apiService.activities.getByResource('work_log', logId)
    activities.value = response || []
  } catch (error) {
    console.error('加载活动记录失败:', error)
    activities.value = []
  } finally {
    activityLoading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const response = await apiService.projects.getList({ per_page: 100 })
    projects.value = response.projects || []
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadWorkLogs()
}

const handleReset = () => {
  Object.keys(filterForm).forEach(key => {
    if (key === 'user_id') {
      filterForm[key] = null
    } else {
      filterForm[key] = ''
    }
  })
  pagination.currentPage = 1
  loadWorkLogs()
}

const refreshData = () => {
  loadWorkLogs()
  loadStatistics()
}

const openCreateDialog = () => {
  dialogMode.value = 'create'
  Object.keys(form).forEach(key => {
    if (key === 'log_date') {
      form[key] = new Date().toISOString().split('T')[0]
    } else if (key === 'hours_spent') {
      form[key] = 0
    } else if (key === 'status') {
      form[key] = 'draft'
    } else if (key === 'work_type') {
      form[key] = 'daily'
    } else if (key === 'project_id') {
      form[key] = null
    } else if (key === 'start_date' || key === 'end_date') {
      form[key] = null
    } else {
      form[key] = ''
    }
  })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  dialogMode.value = 'edit'
  currentLog.value = row
  form.title = row.title
  form.content = row.content
  form.log_date = row.log_date ? row.log_date.split('T')[0] : ''
  form.work_type = row.work_type || 'daily'
  form.project_id = row.project_id || null
  form.hours_spent = row.hours_spent || 0
  form.status = row.status || 'draft'
  form.start_date = row.start_date || null
  form.end_date = row.end_date || null
  dialogVisible.value = true
}

const viewDetail = async (row) => {
  currentLog.value = row
  detailVisible.value = true
  await loadActivities(row.id)
}

const openEditFromDetail = () => {
  detailVisible.value = false
  openEditDialog(currentLog.value)
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }

  submitLoading.value = true
  try {
    const submitData = {
      ...form,
      log_date: form.log_date
    }

    if (dialogMode.value === 'create') {
      await apiService.workLogs.create(submitData)
      ElMessage.success('工作日志创建成功')
    } else {
      await apiService.workLogs.update(currentLog.value.id, submitData)
      ElMessage.success('工作日志更新成功')
    }

    dialogVisible.value = false
    loadWorkLogs()
    loadStatistics()
  } catch (error) {
    console.error('保存工作日志失败:', error)
    ElMessage.error('保存工作日志失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除工作日志"${row.title}"吗？此操作不可撤销。`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await apiService.workLogs.delete(row.id)
      ElMessage.success('删除成功')
      loadWorkLogs()
      loadStatistics()
    } catch (error) {
      console.error('删除工作日志失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadWorkLogs()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  loadWorkLogs()
}

onMounted(() => {
  if (route.query.view === 'all' && isDepartmentManager.value) {
    filterForm.user_id = null
  }
  loadWorkLogs()
  loadStatistics()
  fetchProjects()
  if (isDepartmentManager.value) {
    loadDepartmentUsers()
  }
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.work-log-container {
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
}

.header-left {
  margin-bottom: 20px;
}

.btn-back {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
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

/* 总日志数 - 靛蓝渐变 */
.stat-card-total::before { background: linear-gradient(90deg, #667eea, #764ba2); }

/* 草稿 - 橙色渐变 */
.stat-card-draft::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }

/* 已完成 - 绿色渐变 */
.stat-card-completed::before { background: linear-gradient(90deg, #11998e, #38ef7d); }

/* 总工时 - 粉色渐变 */
.stat-card-hours::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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

/* 总日志数图标 - 靛蓝 */
.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #667eea;
  box-shadow: 0 4px 15px -3px rgba(102, 126, 234, 0.4);
}

/* 草稿图标 - 橙色 */
.stat-icon-wrapper-draft {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

/* 已完成图标 - 绿色 */
.stat-icon-wrapper-completed {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

/* 总工时图标 - 粉色 */
.stat-icon-wrapper-hours {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
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

/* 各卡片数值颜色 */
.stat-card-total .stat-value {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-draft .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-completed .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-hours .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
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

.filter-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.card-title .el-icon {
  color: #6366f1;
  font-size: 18px;
}

.filter-form {
  padding: 10px 0;
}

.filter-select,
.filter-date-picker {
  width: 160px;
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

.btn-secondary {
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: #6366f1;
  color: #6366f1;
}

.btn-refresh {
  transition: all 0.3s;
}

.btn-refresh:hover {
  transform: translateY(-2px);
}

/* 内容区域 */
.content-section {
  margin-bottom: 20px;
}

/* 表格头部 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-title .el-icon {
  color: #6366f1;
  font-size: 20px;
}

.table-title h3 {
  margin: 0;
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
}

.total-count {
  font-size: 13px;
  color: #64748b;
  margin-left: 8px;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 12px;
  border-radius: 20px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(99, 102, 241, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.id-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.log-title {
  color: #6366f1;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.log-title:hover {
  color: #4f46e5;
  text-decoration: underline;
}

.work-type-tag,
.status-tag {
  font-weight: 500;
  border-radius: 6px;
}

.user-name {
  font-weight: 500;
  color: #1e293b;
}

.date-text {
  color: #475569;
  font-size: 13px;
}

.hours-badge {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #667eea;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.project-link {
  font-weight: 500;
}

.empty-text {
  color: #94a3b8;
}

.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

.action-btn {
  opacity: 0;
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) .action-btn {
  opacity: 1;
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 详情内容 */
.content-box {
  white-space: pre-wrap;
  word-break: break-word;
  background: #f8fafc;
  padding: 16px;
  border-radius: 10px;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  color: #475569;
  line-height: 1.6;
}

/* 对话框样式 */
:deep(.custom-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 16px 16px 0 0;
  margin-right: 0;
}

:deep(.custom-dialog .el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.custom-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

:deep(.custom-dialog .el-dialog__body) {
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
  .work-log-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-left {
    margin-bottom: 16px;
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

  .filter-form {
    flex-direction: column;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 12px;
    width: 100%;
  }

  .filter-select,
  .filter-date-picker {
    width: 100% !important;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .table-actions {
    width: 100%;
  }

  .table-actions .el-button {
    flex: 1;
  }

  .action-btn {
    opacity: 1;
  }

  .custom-table :deep(.el-table__row:hover) .action-btn {
    opacity: 1;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
  }

  .pagination-section {
    justify-content: center;
  }

  :deep(.el-pagination) {
    font-size: 11px;
    flex-wrap: wrap;
    gap: 4px;
  }

  :deep(.el-pagination__sizes),
  :deep(.el-pagination__jump) {
    display: none !important;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .el-dialog__header,
  .el-dialog__body,
  .el-dialog__footer {
    padding: 12px !important;
  }

  .el-dialog__title {
    font-size: 16px !important;
  }

  .content-box {
    font-size: 13px;
    padding: 10px;
    max-height: 200px;
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

  .el-table {
    font-size: 11px !important;
  }

  .content-box {
    font-size: 12px;
    padding: 8px;
  }
}
</style>
