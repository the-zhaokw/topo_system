<template>
  <div class="overtime-approval-container">
    <div class="page-header">
      <h1>加班审批</h1>
      <p>审批员工的加班申请</p>
    </div>

    <el-card>
      <div class="toolbar">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
              <el-option label="待审批" value="pending"></el-option>
              <el-option label="已通过" value="approved"></el-option>
              <el-option label="已拒绝" value="rejected"></el-option>
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
        <div class="header-actions">
          <el-button @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          <el-button type="success" @click="showImportDialog = true">
            <el-icon><Upload /></el-icon>
            导入
          </el-button>
        </div>
      </div>

      <el-table :data="applicationList" v-loading="loading" stripe>
        <el-table-column prop="user_real_name" label="申请人" min-width="100">
          <template #default="{ row }">
            {{ row.user_real_name || row.user_name }}
          </template>
        </el-table-column>
        <el-table-column prop="date" label="加班日期" width="120"></el-table-column>
        <el-table-column label="加班时间" min-width="160">
          <template #default="{ row }">
            {{ row.start_time }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="total_hours" label="时长(小时)" width="100"></el-table-column>
        <el-table-column prop="reason" label="加班事由" min-width="200" show-overflow-tooltip></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approver_name" label="审批人" width="120">
          <template #default="{ row }">
            {{ row.approver_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" type="primary" link @click="handleApprove(row)">
              批准
            </el-button>
            <el-button v-if="row.status === 'pending'" type="danger" link @click="handleReject(row)">
              拒绝
            </el-button>
            <el-button type="info" link @click="handleViewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" title="审批加班申请" width="500px">
      <el-descriptions :column="1" border v-if="currentApplication">
        <el-descriptions-item label="申请人">
          {{ currentApplication.user_real_name || currentApplication.user_name }}
        </el-descriptions-item>
        <el-descriptions-item label="加班日期">
          {{ currentApplication.date }}
        </el-descriptions-item>
        <el-descriptions-item label="加班时间">
          {{ currentApplication.start_time }} - {{ currentApplication.end_time }}
        </el-descriptions-item>
        <el-descriptions-item label="加班时长">
          {{ currentApplication.total_hours }} 小时
        </el-descriptions-item>
        <el-descriptions-item label="加班事由">
          {{ currentApplication.reason }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentApplication.status)">
            {{ getStatusText(currentApplication.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审批人">
          {{ currentApplication.approver_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="申请时间">
          {{ formatDate(currentApplication.created_at) }}
        </el-descriptions-item>
      </el-descriptions>
      
      <el-form v-if="dialogType !== 'view'" :model="approvalForm" style="margin-top: 20px">
        <el-form-item label="审批意见">
          <el-input v-model="approvalForm.comment" type="textarea" :rows="3" placeholder="请输入审批意见（拒绝时必填）"></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-if="dialogType === 'approve'" type="primary" @click="submitApproval('approve')">批准</el-button>
        <el-button v-if="dialogType === 'reject'" type="danger" @click="submitApproval('reject')">拒绝</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入加班申请" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".csv,.xlsx"
        :on-change="handleFileChange"
        :file-list="importFileList"
      >
        <el-button type="primary">选择文件</el-button>
        <template #tip>
          <div class="el-upload__tip">
            支持 CSV/Excel 格式，必要列：申请人、加班日期、开始时间、结束时间、加班事由
          </div>
        </template>
      </el-upload>
      
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importLoading">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Download, Upload } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const loading = ref(false)
const applicationList = ref([])
const dialogVisible = ref(false)
const dialogType = ref('view')
const currentApplication = ref(null)

// 导入对话框
const showImportDialog = ref(false)
const importFileList = ref([])
const importLoading = ref(false)
const uploadRef = ref(null)

const filterForm = reactive({
  status: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const approvalForm = reactive({
  comment: ''
})

const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'pending': '待审批',
    'approved': '已通过',
    'rejected': '已拒绝'
  }
  return textMap[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const fetchApplications = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    if (filterForm.status) {
      params.status = filterForm.status
    }
    const response = await apiService.attendance.getOvertimeApplications(params)
    applicationList.value = response.applications || []
    pagination.total = response.total || 0
  } catch (error) {
    ElMessage.error('获取加班申请列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchApplications()
}

const handleReset = () => {
  filterForm.status = ''
  pagination.page = 1
  fetchApplications()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchApplications()
}

const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  fetchApplications()
}

const handleApprove = (row) => {
  currentApplication.value = row
  approvalForm.comment = ''
  dialogType.value = 'approve'
  dialogVisible.value = true
}

const handleReject = (row) => {
  currentApplication.value = row
  approvalForm.comment = ''
  dialogType.value = 'reject'
  dialogVisible.value = true
}

const handleViewDetail = (row) => {
  currentApplication.value = row
  dialogType.value = 'view'
  dialogVisible.value = true
}

const submitApproval = async (action) => {
  if (action === 'reject' && !approvalForm.comment) {
    ElMessage.warning('拒绝申请时必须填写审批意见')
    return
  }
  
  try {
    await apiService.attendance.approveOvertimeApplication(currentApplication.value.id, {
      action: action,
      comment: approvalForm.comment
    })
    ElMessage.success(action === 'approve' ? '审批已通过' : '已拒绝申请')
    dialogVisible.value = false
    fetchApplications()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '审批操作失败')
  }
}

onMounted(() => {
  fetchApplications()
})

const handleExport = async () => {
  try {
    const response = await apiService.attendance.exportOvertimeApplications()
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `加班申请_${new Date().toISOString().slice(0, 10)}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleFileChange = (file) => {
  importFileList.value = [file]
}

const handleImport = async () => {
  if (!importFileList.value || importFileList.value.length === 0) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  
  importLoading.value = true
  try {
    const file = importFileList.value[0].raw
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiService.attendance.importOvertimeApplications(formData)
    ElMessage.success(response.data.message || '导入成功')
    showImportDialog.value = false
    importFileList.value = []
    fetchApplications()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '导入失败')
  } finally {
    importLoading.value = false
  }
}
</script>

<style scoped>
.overtime-approval-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .overtime-approval-container {
    padding: 12px;
  }

  .page-header {
    margin-bottom: 16px;
  }

  .page-header h1 {
    font-size: 18px;
  }

  .page-header p {
    font-size: 12px;
  }

  .toolbar {
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 8px 12px;
  }

  .el-form-item {
    margin-bottom: 12px;
  }

  .el-form-item__label {
    font-size: 12px;
  }

  .el-input__inner, .el-textarea__inner {
    font-size: 14px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th, .el-table td {
    padding: 6px 4px !important;
  }

  .pagination-container {
    justify-content: center;
    margin-top: 16px;
  }

  :deep(.el-pagination) {
    font-size: 11px;
    flex-wrap: wrap;
    gap: 4px;
  }

  :deep(.el-pagination__sizes), :deep(.el-pagination__jump) {
    display: none !important;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .el-dialog__header, .el-dialog__body, .el-dialog__footer {
    padding: 12px !important;
  }

  .el-dialog__title {
    font-size: 16px !important;
  }
}

@media screen and (max-width: 480px) {
  .overtime-approval-container {
    padding: 8px;
  }

  .page-header h1 {
    font-size: 16px;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>
