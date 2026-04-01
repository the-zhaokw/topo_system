<template>
  <div class="work-logs-container">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.push('/dashboard')" type="primary" plain>
          <el-icon><ArrowLeft /></el-icon>
          返回个人工作台
        </el-button>
      </div>
      <h2>工作日志</h2>
    </div>

    <el-card class="filter-card" shadow="hover">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="日期">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="handleFilterChange"
          />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filterForm.workType" placeholder="请选择" clearable @change="handleFilterChange">
            <el-option label="日报" value="daily" />
            <el-option label="周报" value="weekly" />
            <el-option label="月报" value="monthly" />
            <el-option label="项目日志" value="project" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="请选择" clearable @change="handleFilterChange">
            <el-option label="草稿" value="draft" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键字">
          <el-input v-model="filterForm.keyword" placeholder="搜索标题或内容" clearable @change="handleFilterChange" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="action-card" shadow="hover">
      <div class="action-bar">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建日志
        </el-button>
      </div>

      <el-table :data="workLogs" style="width: 100%" v-loading="loading">
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="handleView(row)">{{ row.title }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="log_date" label="日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.log_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="work_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getWorkTypeTag(row.work_type)">{{ getWorkTypeText(row.work_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="关联项目" width="150">
          <template #default="{ row }">
            <el-link v-if="row.project_id" type="primary" @click="$router.push(`/projects/${row.project_id}`)">
              {{ row.project_name }}
            </el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="hours_spent" label="工时" width="80">
          <template #default="{ row }">
            {{ row.hours_spent }}h
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'info'">
              {{ row.status === 'completed' ? '已完成' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.perPage"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" @close="handleDialogClose">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入日志标题" />
        </el-form-item>
        <el-form-item label="日期" prop="log_date">
          <el-date-picker
            v-model="form.log_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="类型" prop="work_type">
          <el-select v-model="form.work_type" placeholder="请选择日志类型" style="width: 100%">
            <el-option label="日报" value="daily" />
            <el-option label="周报" value="weekly" />
            <el-option label="月报" value="monthly" />
            <el-option label="项目日志" value="project" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联项目" prop="project_id">
          <el-select v-model="form.project_id" placeholder="请选择关联项目" clearable style="width: 100%">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="工时(小时)" prop="hours_spent">
          <el-input-number v-model="form.hours_spent" :min="0" :max="24" :step="0.5" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="completed">已完成</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="8" placeholder="请输入日志内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="viewDialogVisible" title="日志详情" width="700px">
      <div class="log-detail" v-if="currentLog">
        <div class="detail-header">
          <h3>{{ currentLog.title }}</h3>
          <el-tag :type="currentLog.status === 'completed' ? 'success' : 'info'">
            {{ currentLog.status === 'completed' ? '已完成' : '草稿' }}
          </el-tag>
        </div>
        <div class="detail-info">
          <div class="info-item">
            <span class="label">日期：</span>
            <span class="value">{{ formatDate(currentLog.log_date) }}</span>
          </div>
          <div class="info-item">
            <span class="label">类型：</span>
            <span class="value">{{ getWorkTypeText(currentLog.work_type) }}</span>
          </div>
          <div class="info-item">
            <span class="label">关联项目：</span>
            <el-link v-if="currentLog.project_id" type="primary" @click="$router.push(`/projects/${currentLog.project_id}`)">
              {{ currentLog.project_name }}
            </el-link>
            <span v-else>-</span>
          </div>
          <div class="info-item">
            <span class="label">工时：</span>
            <span class="value">{{ currentLog.hours_spent }}h</span>
          </div>
        </div>
        <el-divider />
        <div class="detail-content">
          <div class="content-label">日志内容：</div>
          <div class="content-body">{{ currentLog.content }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromView">编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const router = useRouter()

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const dialogTitle = ref('新建日志')
const formRef = ref(null)
const currentLog = ref(null)

const workLogs = ref([])
const projects = ref([])

const filterForm = reactive({
  dateRange: [],
  workType: '',
  status: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  perPage: 20,
  total: 0
})

const form = reactive({
  id: null,
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

const formRules = {
  title: [{ required: true, message: '请输入日志标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入日志内容', trigger: 'blur' }],
  log_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  work_type: [{ required: true, message: '请选择日志类型', trigger: 'change' }]
}

const fetchWorkLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage
    }

    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_date = filterForm.dateRange[0]
      params.end_date = filterForm.dateRange[1]
    }
    if (filterForm.workType) {
      params.work_type = filterForm.workType
    }
    if (filterForm.status) {
      params.status = filterForm.status
    }
    if (filterForm.keyword) {
      params.keyword = filterForm.keyword
    }

    const response = await apiService.workLogs.getList(params)
    workLogs.value = response.work_logs || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取工作日志失败:', error)
    ElMessage.error('获取工作日志失败')
  } finally {
    loading.value = false
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

const handleFilterChange = () => {
  pagination.page = 1
  fetchWorkLogs()
}

const handleSearch = () => {
  pagination.page = 1
  fetchWorkLogs()
}

const handleReset = () => {
  filterForm.dateRange = []
  filterForm.workType = ''
  filterForm.status = ''
  filterForm.keyword = ''
  pagination.page = 1
  fetchWorkLogs()
}

const handleSizeChange = (val) => {
  pagination.perPage = val
  pagination.page = 1
  fetchWorkLogs()
}

const handlePageChange = (val) => {
  pagination.page = val
  fetchWorkLogs()
}

const handleCreate = () => {
  dialogTitle.value = '新建日志'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑日志'
  form.id = row.id
  form.title = row.title
  form.content = row.content
  form.log_date = row.log_date ? row.log_date.split('T')[0] : ''
  form.work_type = row.work_type
  form.project_id = row.project_id
  form.hours_spent = row.hours_spent
  form.status = row.status
  dialogVisible.value = true
}

const handleEditFromView = () => {
  viewDialogVisible.value = false
  handleEdit(currentLog.value)
}

const handleView = (row) => {
  currentLog.value = row
  viewDialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除工作日志 "${row.title}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await apiService.workLogs.delete(row.id)
    ElMessage.success('删除成功')
    fetchWorkLogs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除工作日志失败:', error)
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true

    const submitData = {
      title: form.title,
      content: form.content,
      log_date: form.log_date,
      work_type: form.work_type,
      project_id: form.project_id,
      hours_spent: form.hours_spent,
      status: form.status
    }

    if (form.id) {
      await apiService.workLogs.update(form.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await apiService.workLogs.create(submitData)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    fetchWorkLogs()
  } catch (error) {
    if (error !== false) {
      console.error('保存工作日志失败:', error)
      ElMessage.error('保存工作日志失败')
    }
  } finally {
    submitLoading.value = false
  }
}

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  form.id = null
  form.title = ''
  form.content = ''
  form.log_date = ''
  form.work_type = 'daily'
  form.project_id = null
  form.hours_spent = 0
  form.status = 'draft'
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getWorkTypeText = (type) => {
  const map = {
    daily: '日报',
    weekly: '周报',
    monthly: '月报',
    project: '项目日志'
  }
  return map[type] || type
}

const getWorkTypeTag = (type) => {
  const map = {
    daily: '',
    weekly: 'success',
    monthly: 'warning',
    project: 'info'
  }
  return map[type] || ''
}

onMounted(() => {
  fetchWorkLogs()
  fetchProjects()
})
</script>

<style scoped>
.work-logs-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.header-left {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin-bottom: 0;
}

.action-bar {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.log-detail {
  padding: 10px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.detail-header h3 {
  margin: 0;
  color: #303133;
}

.detail-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item .label {
  color: #606266;
  font-weight: 500;
}

.info-item .value {
  color: #303133;
}

.detail-content {
  margin-top: 20px;
}

.content-label {
  color: #606266;
  font-weight: 500;
  margin-bottom: 12px;
}

.content-body {
  color: #303133;
  line-height: 1.8;
  white-space: pre-wrap;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .work-logs-container {
    padding: 12px;
  }

  .page-header {
    margin-bottom: 16px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .filter-card {
    margin-bottom: 16px;
  }

  .filter-form .el-form-item {
    margin-bottom: 12px;
  }

  .filter-form .el-input,
  .filter-form .el-select,
  .filter-form .el-date-picker {
    width: 100% !important;
  }

  .action-bar {
    margin-bottom: 12px;
  }

  .action-bar .el-button {
    font-size: 12px;
    padding: 8px 12px;
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

  .log-detail {
    padding: 8px;
  }

  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 16px;
  }

  .detail-header h3 {
    font-size: 16px;
  }

  .detail-info {
    grid-template-columns: 1fr;
    gap: 12px;
    margin-bottom: 16px;
  }

  .info-item {
    font-size: 13px;
  }

  .detail-content {
    margin-top: 16px;
  }

  .content-body {
    font-size: 13px;
  }
}

@media screen and (max-width: 480px) {
  .work-logs-container {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .detail-info {
    gap: 8px;
  }

  .info-item {
    font-size: 12px;
  }

  .content-body {
    font-size: 12px;
  }
}
</style>
