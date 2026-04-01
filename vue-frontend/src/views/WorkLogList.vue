<template>
  <div class="work-log-container">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.push('/dashboard')" type="primary" plain>
          <el-icon><ArrowLeft /></el-icon>
          返回个人工作台
        </el-button>
      </div>
      <div class="header-content">
        <h1>工作日志</h1>
        <p>记录和管理您的工作计划与进度</p>
      </div>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #E3F2FD;">
            <i class="el-icon-document" style="color: #2196F3;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total_logs || 0 }}</div>
            <div class="stat-label">总日志数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #FFF3E0;">
            <i class="el-icon-edit" style="color: #FF9800;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.draft_logs || 0 }}</div>
            <div class="stat-label">草稿</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #E8F5E9;">
            <i class="el-icon-circle-check" style="color: #4CAF50;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.completed_logs || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #FCE4EC;">
            <i class="el-icon-time" style="color: #E91E63;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total_hours || 0 }}h</div>
            <div class="stat-label">总工时</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div class="filter-section">
      <el-card>
        <el-form :model="filterForm" inline>
          <el-form-item label="工作日期">
            <el-date-picker
              v-model="filterForm.log_date"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              clearable>
            </el-date-picker>
          </el-form-item>

          <el-form-item label="工作类型">
            <el-select v-model="filterForm.work_type" placeholder="请选择类型" clearable>
              <el-option label="日报" value="daily"></el-option>
              <el-option label="周报" value="weekly"></el-option>
              <el-option label="月报" value="monthly"></el-option>
              <el-option label="项目总结" value="project_summary"></el-option>
              <el-option label="其他" value="other"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="请选择状态" clearable>
              <el-option label="草稿" value="draft"></el-option>
              <el-option label="已完成" value="completed"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item v-if="isDepartmentManager" label="员工">
            <el-select
              v-model="filterForm.user_id"
              placeholder="请选择员工"
              clearable
              style="width: 180px;">
              <el-option
                v-for="user in departmentUsers"
                :key="user.id"
                :label="user.username"
                :value="user.id">
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch" :loading="loading">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <div class="content-section">
      <el-card>
        <div class="table-header">
          <div class="table-title">
            <h3>日志列表</h3>
            <span class="total-count">共 {{ total }} 条记录</span>
          </div>
          <div class="table-actions">
            <el-button type="primary" @click="openCreateDialog">
              <el-icon><Plus /></el-icon>
              新增日志
            </el-button>
            <el-button @click="refreshData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>

        <el-table
          :data="workLogs"
          v-loading="loading"
          stripe
          style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>

          <el-table-column label="标题" min-width="200">
            <template #default="{ row }">
              <div class="log-title" @click="viewDetail(row)">
                {{ row.title }}
              </div>
            </template>
          </el-table-column>

          <el-table-column label="类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getWorkTypeTag(row.work_type)" size="small">
                {{ getWorkTypeText(row.work_type) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column v-if="isDepartmentManager" label="员工" width="120" align="center">
            <template #default="{ row }">
              {{ row.user_name || row.username || '-' }}
            </template>
          </el-table-column>

          <el-table-column label="日期" width="120" align="center">
            <template #default="{ row }">
              {{ formatDate(row.log_date) }}
            </template>
          </el-table-column>

          <el-table-column label="工时" width="100" align="center">
            <template #default="{ row }">
              {{ row.hours_spent || 0 }}h
            </template>
          </el-table-column>

          <el-table-column label="关联项目" width="150">
            <template #default="{ row }">
              <el-link v-if="row.project_id" type="primary" @click="$router.push(`/projects/${row.project_id}`)">
                {{ row.project_name }}
              </el-link>
              <span v-else>-</span>
            </template>
          </el-table-column>

          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'completed' ? 'success' : 'warning'" size="small">
                {{ row.status === 'completed' ? '已完成' : '草稿' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="操作时间" width="180" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div>{{ formatDate(row.updated_at) }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="180" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDetail(row)">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button type="primary" link @click="openEditDialog(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" link @click="handleDelete(row)">
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
      :close-on-click-modal="false">
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
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      title="工作日志详情"
      width="700px">
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
        <el-button type="primary" @click="openEditFromDetail">
          编辑
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="activityVisible"
      title="活动记录"
      width="800px">
      <div v-loading="activityLoading">
        <el-table
          v-if="activities.length > 0"
          :data="activities"
          stripe
          style="width: 100%">
          <el-table-column label="操作类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getActionType(row.action)" size="small">
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
import { Search, Refresh, Plus, View, Edit, Delete, ArrowLeft } from '@element-plus/icons-vue'
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
.work-log-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.header-left {
  margin-bottom: 16px;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.header-content p {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px 0;
}

.stat-icon-box {
  width: 16px !important;
  height: 16px !important;
  border-radius: 4px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 6px;
}

.stat-icon-box i {
  font-size: 12px;
}

.stat-content {
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.filter-section {
  margin-bottom: 20px;
}

.content-section {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.total-count {
  font-size: 14px;
  color: #909399;
  margin-left: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.log-title {
  color: #409EFF;
  cursor: pointer;
}

.log-title:hover {
  text-decoration: underline;
}

.timestamp {
  color: #606266;
  font-size: 13px;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.content-box {
  white-space: pre-wrap;
  word-break: break-word;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .work-log-list {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .filter-card {
    margin-bottom: 16px;
  }

  .filter-form {
    flex-direction: column;
    gap: 12px;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 8px;
    width: 100%;
  }

  .filter-form .el-input,
  .filter-form .el-select,
  .filter-form .el-date-picker {
    width: 100% !important;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .pagination {
    justify-content: center;
    margin-top: 16px;
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
  .work-log-list {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .content-box {
    font-size: 12px;
    padding: 8px;
  }
}
</style>