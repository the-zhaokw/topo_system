<template>
  <div class="project-log-list">
    <div class="log-list-header">
      <h2>项目日志</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true" v-if="currentUser">
          <el-icon><Plus /></el-icon>
          新建日志
        </el-button>
      </div>
    </div>

    <el-card v-if="projectId" class="project-filter-tip" shadow="never">
      <div class="project-filter-content">
        <el-icon><Filter /></el-icon>
        <span>当前显示项目 ID {{ projectId }} 下的日志</span>
        <el-button type="primary" link @click="goBackToProject">
          返回项目
        </el-button>
      </div>
    </el-card>

    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="关键词">
              <el-input
                v-model="filters.search"
                placeholder="搜索标题或内容"
                clearable
                @clear="handleFilter"
                @keyup.enter="handleFilter"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>

          <el-col :span="4">
            <el-form-item label="日志类型">
              <el-select v-model="filters.work_type" placeholder="全部" clearable @change="handleFilter">
                <el-option label="日报" value="daily" />
                <el-option label="周报" value="weekly" />
                <el-option label="月报" value="monthly" />
                <el-option label="项目总结" value="project_summary" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="4">
            <el-form-item label="状态">
              <el-select v-model="filters.status" placeholder="全部" clearable @change="handleFilter">
                <el-option label="草稿" value="draft" />
                <el-option label="已发布" value="published" />
                <el-option label="已归档" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="4">
            <el-form-item label="排序">
              <el-select v-model="sortOrder" @change="handleSortChange">
                <el-option label="最新在前" value="desc" />
                <el-option label="最早在前" value="asc" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="操作">
              <el-button type="primary" @click="handleFilter">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
              <el-button @click="resetFilters">
                重置
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="stats-card" shadow="never" v-if="stats">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ stats.total_logs || 0 }}</div>
            <div class="stat-label">总日志数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ stats.draft_logs || 0 }}</div>
            <div class="stat-label">草稿</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ stats.completed_logs || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ stats.total_hours || 0 }}h</div>
            <div class="stat-label">总工时</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="log-list-card" shadow="never">
      <el-table
        :data="logs"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewLogDetail(row)">
              {{ row.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="work_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getWorkTypeTag(row.work_type)" size="small">
              {{ getWorkTypeText(row.work_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="创建人" width="120">
          <template #default="{ row }">
            <span class="clickable-link" @click="goToUser(row.created_by)">{{ row.creator_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="log_date" label="记录时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.log_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewLogDetail(row)">
              查看
            </el-button>
            <el-button
              type="primary"
              link
              size="small"
              @click="editLog(row)"
              v-if="canEditOrDelete(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click="handleDelete(row)"
              v-if="canEditOrDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <el-dialog
      v-model="showCreateDialog"
      :title="editingLog ? '编辑日志' : '新增日志'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="logForm" :rules="logFormRules" ref="logFormRef" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="logForm.title" placeholder="请输入日志标题" />
        </el-form-item>

        <el-form-item label="工作类型" prop="work_type">
          <el-select v-model="logForm.work_type" placeholder="请选择工作类型" style="width: 100%">
            <el-option label="日报" value="daily" />
            <el-option label="周报" value="weekly" />
            <el-option label="月报" value="monthly" />
            <el-option label="项目总结" value="project_summary" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="工作日期" prop="log_date">
          <el-date-picker
            v-model="logForm.log_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%">
          </el-date-picker>
        </el-form-item>

        <el-form-item label="工时(小时)" prop="hours_spent">
          <el-input-number v-model="logForm.hours_spent" :min="0" :max="24" :step="0.5" style="width: 100%" />
        </el-form-item>

        <el-form-item v-if="['weekly', 'monthly', 'project_summary'].includes(logForm.work_type)" label="开始时间" prop="start_date">
          <el-date-picker
            v-model="logForm.start_date"
            type="date"
            placeholder="选择开始时间"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item v-if="['weekly', 'monthly', 'project_summary'].includes(logForm.work_type)" label="结束时间" prop="end_date">
          <el-date-picker
            v-model="logForm.end_date"
            type="date"
            placeholder="选择结束时间"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-select v-model="logForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="草稿" value="draft" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="logForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入日志内容"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showDetailDialog"
      title="日志详情"
      width="700px"
    >
      <div v-if="currentLog" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="标题" :span="2">
            {{ currentLog.title }}
          </el-descriptions-item>
          <el-descriptions-item label="日志类型">
            <el-tag :type="getWorkTypeTag(currentLog.work_type)" size="small">
              {{ getWorkTypeText(currentLog.work_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentLog.status)" size="small">
              {{ getStatusText(currentLog.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ currentLog.creator_name }}
          </el-descriptions-item>
          <el-descriptions-item label="记录时间">
            {{ formatDate(currentLog.log_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDate(currentLog.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="内容" :span="2">
            <div class="log-content">{{ currentLog.content }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button
          type="primary"
          @click="editLog(currentLog)"
          v-if="currentLog && canEditOrDelete(currentLog)"
        >
          编辑
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Filter } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const projectId = computed(() => {
  return route.params.projectId ? parseInt(route.params.projectId) : route.query.project_id ? parseInt(route.query.project_id) : null
})

const loading = ref(false)
const logs = ref([])
const stats = ref(null)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const editingLog = ref(null)
const currentLog = ref(null)
const submitLoading = ref(false)
const isMounted = ref(true)

const logFormRef = ref(null)

const filters = reactive({
  search: '',
  work_type: '',
  status: ''
})

const sortOrder = ref('desc')

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

watch(projectId, (newVal) => {
  if (newVal) {
    fetchLogs()
    fetchStats()
  }
})

const logForm = reactive({
  title: '',
  content: '',
  work_type: 'daily',
  status: 'draft',
  log_date: null,
  hours_spent: 0,
  start_date: null,
  end_date: null
})

watch(() => logForm.work_type, (newType) => {
  if (['weekly', 'monthly', 'project_summary'].includes(newType)) {
    calculateDateRange(newType)
  } else {
    logForm.start_date = null
    logForm.end_date = null
  }
})

const logFormRules = {
  title: [{ required: true, message: '请输入日志标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入日志内容', trigger: 'blur' }],
  work_type: [{ required: true, message: '请选择工作类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  log_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

const currentUser = computed(() => userStore.currentUser)

const canEditOrDelete = (log) => {
  if (!currentUser.value || !log) return false
  const role = currentUser.value.role
  if (['admin', 'manager', 'project_manager'].includes(role)) return true
  return log.created_by === currentUser.value.id
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

const getStatusText = (status) => {
  const map = {
    draft: '草稿',
    completed: '已完成'
  }
  return map[status] || status
}

const getStatusTagType = (status) => {
  const map = {
    draft: 'info',
    completed: 'success'
  }
  return map[status] || ''
}

const calculateDateRange = (workType) => {
  const today = new Date()
  if (workType === 'weekly') {
    const dayOfWeek = today.getDay() || 7
    const startOfWeek = new Date(today)
    startOfWeek.setDate(today.getDate() - dayOfWeek + 1)
    const endOfWeek = new Date(startOfWeek)
    endOfWeek.setDate(startOfWeek.getDate() + 6)
    logForm.start_date = startOfWeek.toISOString().split('T')[0]
    logForm.end_date = endOfWeek.toISOString().split('T')[0]
  } else if (workType === 'monthly') {
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
    const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
    logForm.start_date = startOfMonth.toISOString().split('T')[0]
    logForm.end_date = endOfMonth.toISOString().split('T')[0]
  } else if (workType === 'project_summary') {
    logForm.start_date = null
    logForm.end_date = null
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const goToUser = (userId) => {
  if (userId) {
    router.push(`/users/${userId}`)
  }
}

const fetchLogs = async () => {
  if (!projectId.value) {
    ElMessage.warning('项目ID不能为空')
    return
  }

  loading.value = true
  try {
    const params = {
      project_id: projectId.value,
      page: pagination.currentPage,
      per_page: pagination.pageSize
    }

    if (filters.search) params.search = filters.search
    if (filters.work_type) params.work_type = filters.work_type
    if (filters.status) params.status = filters.status

    const response = await apiService.workLogs.getList(params)
    if (isMounted.value) {
      logs.value = response.logs || []
      pagination.total = response.total || 0
    }
  } catch (error) {
    console.error('获取日志列表失败:', error)
    if (isMounted.value) {
      ElMessage.error('获取日志列表失败')
    }
  } finally {
    if (isMounted.value) {
      loading.value = false
    }
  }
}

const fetchStats = async () => {
  if (!projectId.value) return

  try {
    const response = await apiService.workLogs.getStats({ project_id: projectId.value })
    if (isMounted.value) {
      stats.value = response
    }
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

const handleFilter = () => {
  pagination.currentPage = 1
  fetchLogs()
}

const handleSortChange = () => {
  pagination.currentPage = 1
  fetchLogs()
}

const resetFilters = () => {
  filters.search = ''
  filters.work_type = ''
  filters.status = ''
  sortOrder.value = 'desc'
  pagination.currentPage = 1
  fetchLogs()
}

const handleSizeChange = () => {
  pagination.currentPage = 1
  fetchLogs()
}

const handleCurrentChange = () => {
  fetchLogs()
}

const viewLogDetail = async (log) => {
  try {
    const response = await apiService.workLogs.getById(log.id)
    currentLog.value = response.log || response
    showDetailDialog.value = true
  } catch (error) {
    console.error('获取日志详情失败:', error)
    ElMessage.error('获取日志详情失败')
  }
}

const editLog = (log) => {
  if (typeof log === 'object' && log.id) {
    currentLog.value = log
  }
  editingLog.value = log
  logForm.title = log.title
  logForm.content = log.content
  logForm.work_type = log.work_type || 'daily'
  logForm.status = log.status || 'draft'
  logForm.log_date = log.log_date ? log.log_date.split('T')[0] : null
  logForm.hours_spent = log.hours_spent || 0
  logForm.start_date = log.start_date || null
  logForm.end_date = log.end_date || null
  showDetailDialog.value = false
  showCreateDialog.value = true
}

const resetForm = () => {
  editingLog.value = null
  logForm.title = ''
  logForm.content = ''
  logForm.work_type = 'daily'
  logForm.status = 'draft'
  logForm.log_date = null
  logForm.hours_spent = 0
  logForm.start_date = null
  logForm.end_date = null
  if (logFormRef.value) {
    logFormRef.value.resetFields()
  }
}

const handleSubmit = async () => {
  if (!logFormRef.value) return

  try {
    await logFormRef.value.validate()
  } catch (e) {
    return
  }

  submitLoading.value = true
  try {
    const data = {
      title: logForm.title,
      content: logForm.content,
      work_type: logForm.work_type,
      status: logForm.status,
      project_id: projectId.value,
      log_date: logForm.log_date || new Date().toISOString().split('T')[0],
      hours_spent: logForm.hours_spent || 0
    }

    if (['weekly', 'monthly', 'project_summary'].includes(logForm.work_type)) {
      if (logForm.start_date) data.start_date = logForm.start_date
      if (logForm.end_date) data.end_date = logForm.end_date
    }

    if (editingLog.value) {
      await apiService.workLogs.update(editingLog.value.id, data)
      ElMessage.success('日志更新成功')
    } else {
      await apiService.workLogs.create(data)
      ElMessage.success('日志创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    fetchLogs()
    fetchStats()
  } catch (error) {
    console.error('保存日志失败:', error)
    const errorMsg = error?.response?.data?.message || error?.message || '保存失败'
    ElMessage.error(errorMsg)
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (log) => {
  ElMessageBox.confirm(
    `确定要删除日志 "${log.title}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await apiService.workLogs.delete(log.id)
      ElMessage.success('日志删除成功')
      fetchLogs()
      fetchStats()
    } catch (error) {
      console.error('删除日志失败:', error)
      const errorMsg = error?.response?.data?.message || error?.message || '删除失败'
      ElMessage.error(errorMsg)
    }
  }).catch(() => {})
}

const goBackToProject = () => {
  if (projectId.value) {
    router.push(`/projects/${projectId.value}`)
  }
}

onMounted(() => {
  if (projectId.value) {
    fetchLogs()
    fetchStats()
  }
})

onUnmounted(() => {
  isMounted.value = false
})
</script>

<style scoped>
.project-log-list {
  padding: 20px;
}

.log-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.log-list-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.project-filter-tip {
  margin-bottom: 16px;
  background-color: #f5f7fa;
}

.project-filter-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-card {
  margin-bottom: 16px;
}

.stats-card {
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.log-list-card {
  margin-bottom: 16px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.log-detail {
  padding: 10px;
}

.log-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.clickable-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: none;
}

.clickable-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .project-log-list {
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

  .stats-card {
    margin-bottom: 16px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-item {
    padding: 12px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .list-card {
    margin-bottom: 16px;
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

  .log-detail-content {
    font-size: 13px;
  }

  .clickable-link {
    font-size: 12px;
  }
}

@media screen and (max-width: 480px) {
  .project-log-list {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .stat-value {
    font-size: 18px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .log-detail-content {
    font-size: 12px;
  }
}
</style>