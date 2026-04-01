<template>
  <div class="leave-approval">
    <div class="header">
      <h1>请假审批</h1>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
        <el-button type="success" @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          导入
        </el-button>
        <el-button @click="fetchPendingApplications">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 待审批申请 -->
    <el-card class="pending-applications">
      <template #header>
        <div class="card-header">
          <span>待审批申请</span>
          <el-tag type="warning">{{ pendingApplications.length }}</el-tag>
        </div>
      </template>

      <el-table :data="pendingApplications" v-loading="tableLoading">
        <el-table-column prop="id" label="申请ID" width="80" />
        <el-table-column prop="applicant" label="申请人" width="120" />
        <el-table-column prop="leave_type" label="请假类型">
          <template #default="{ row }">
            <el-tag :type="getLeaveTypeTag(row.leave_type)">
              {{ getLeaveTypeText(row.leave_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column prop="days" label="天数" width="80" />
        <el-table-column prop="reason" label="请假事由" min-width="200" show-overflow-tooltip />
        <el-table-column prop="current_approver_level" label="审批层级" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.current_approver_level">
              第{{ row.current_approver_level }}级
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="emergency_flag" label="紧急" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.emergency_flag" type="danger">紧急</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="160" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleApprove(row)">
              批准
            </el-button>
            <el-button size="small" type="danger" @click="handleReject(row)">
              拒绝
            </el-button>
            <el-button size="small" @click="viewApplicationDetail(row)">
              详情
            </el-button>
            <el-button size="small" v-if="row.attachment_path" @click="downloadAttachment(row)">
              附件
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 审批历史 -->
    <el-card class="approval-history">
      <template #header>
        <div class="card-header">
          <span>审批历史</span>
          <el-button @click="fetchApprovalHistory">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="approvalHistory" v-loading="historyLoading">
        <el-table-column prop="id" label="申请ID" width="80" />
        <el-table-column prop="applicant" label="申请人" width="120" />
        <el-table-column prop="leave_type" label="请假类型">
          <template #default="{ row }">
            <el-tag :type="getLeaveTypeTag(row.leave_type)">
              {{ getLeaveTypeText(row.leave_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column prop="days" label="天数" width="80" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approver" label="审批人" />
        <el-table-column prop="approved_at" label="审批时间" width="160" />
        <el-table-column prop="approval_comment" label="审批意见" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" @click="viewApplicationDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="historyPage"
          v-model:page-size="historyPageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="historyTotal"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleHistorySizeChange"
          @current-change="handleHistoryPageChange"
        />
      </div>
    </el-card>

    <!-- 审批对话框 -->
    <el-dialog
      v-model="approvalDialog.visible"
      :title="approvalDialog.title"
      width="500px"
    >
      <el-form :model="approvalForm" label-width="80px">
        <el-form-item label="申请信息">
          <div class="application-info">
            <p><strong>申请人：</strong>{{ approvalDialog.currentApplication?.applicant }}</p>
            <p><strong>请假类型：</strong>{{ getLeaveTypeText(approvalDialog.currentApplication?.leave_type) }}</p>
            <p><strong>请假时间：</strong>{{ approvalDialog.currentApplication?.start_date }} 至 {{ approvalDialog.currentApplication?.end_date }}</p>
            <p><strong>请假天数：</strong>{{ approvalDialog.currentApplication?.days }} 天</p>
            <p><strong>当前审批层级：</strong>第{{ approvalDialog.currentApplication?.current_approver_level || 1 }}级</p>
            <p><strong>紧急情况：</strong>
              <el-tag v-if="approvalDialog.currentApplication?.emergency_flag" type="danger">紧急</el-tag>
              <el-tag v-else type="success">正常</el-tag>
            </p>
            <p><strong>请假事由：</strong>{{ approvalDialog.currentApplication?.reason }}</p>
            <p v-if="approvalDialog.currentApplication?.attachment_path">
              <strong>附件：</strong>
              <el-button type="text" @click="downloadAttachment(approvalDialog.currentApplication)">
                {{ getFileName(approvalDialog.currentApplication?.attachment_path) }}
              </el-button>
            </p>
          </div>
        </el-form-item>
        <el-form-item label="审批意见" prop="comment">
          <el-input
            v-model="approvalForm.comment"
            type="textarea"
            :rows="3"
            placeholder="请输入审批意见（可选）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="approvalDialog.visible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmApproval"
            :loading="approvalLoading"
          >
            确认{{ approvalDialog.type === 'approve' ? '批准' : '拒绝' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 申请详情对话框 -->
    <el-dialog
      v-model="detailDialog.visible"
      title="申请详情"
      width="600px"
    >
      <div class="application-detail" v-if="detailDialog.currentApplication">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="申请ID">{{ detailDialog.currentApplication.id }}</el-descriptions-item>
          <el-descriptions-item label="申请人">{{ detailDialog.currentApplication.applicant }}</el-descriptions-item>
          <el-descriptions-item label="请假类型">
            <el-tag :type="getLeaveTypeTag(detailDialog.currentApplication.leave_type)">
              {{ getLeaveTypeText(detailDialog.currentApplication.leave_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="请假天数">{{ detailDialog.currentApplication.days }} 天</el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ detailDialog.currentApplication.start_date }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ detailDialog.currentApplication.end_date }}</el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ detailDialog.currentApplication.created_at }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(detailDialog.currentApplication.status)">
              {{ getStatusText(detailDialog.currentApplication.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="审批人" :span="2">
            {{ detailDialog.currentApplication.approver || '待审批' }}
          </el-descriptions-item>
          <el-descriptions-item label="审批时间" :span="2">
            {{ detailDialog.currentApplication.approved_at || '待审批' }}
          </el-descriptions-item>
          <el-descriptions-item label="请假事由" :span="2">
            {{ detailDialog.currentApplication.reason }}
          </el-descriptions-item>
          <el-descriptions-item label="审批意见" :span="2" v-if="detailDialog.currentApplication.approval_comment">
            {{ detailDialog.currentApplication.approval_comment }}
          </el-descriptions-item>
          <el-descriptions-item label="审批流程" :span="2" v-if="detailDialog.currentApplication.approval_levels && detailDialog.currentApplication.approval_levels.length > 0">
            <el-timeline>
              <el-timeline-item
                v-for="(level, index) in detailDialog.currentApplication.approval_levels"
                :key="index"
                :type="level.status === 'approved' ? 'success' : level.status === 'rejected' ? 'danger' : 'info'"
                :timestamp="level.approved_at"
                placement="top"
              >
                <div>第{{ level.level }}级审批: {{ level.approver_name || '待审批' }}</div>
                <div v-if="level.status">状态: {{ level.status === 'approved' ? '已批准' : level.status === 'rejected' ? '已拒绝' : '待审批' }}</div>
                <div v-if="level.comment">意见: {{ level.comment }}</div>
              </el-timeline-item>
            </el-timeline>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialog.visible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入请假申请" width="500px">
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
            支持 CSV/Excel 格式，必要列：申请人、请假类型、开始日期、结束日期、请假事由<br/>
            请假类型可选：年假、病假、事假、调休假、婚假、产假、陪产假、丧假
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
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Download, Upload } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const tableLoading = ref(false)
const historyLoading = ref(false)
const approvalLoading = ref(false)

// 导入对话框
const showImportDialog = ref(false)
const importFileList = ref([])
const importLoading = ref(false)
const uploadRef = ref(null)

// 待审批申请
const pendingApplications = ref([])

// 审批历史
const approvalHistory = ref([])
const historyPage = ref(1)
const historyPageSize = ref(10)
const historyTotal = ref(0)

// 审批对话框
const approvalDialog = reactive({
  visible: false,
  title: '',
  type: '', // 'approve' or 'reject'
  currentApplication: null
})

const approvalForm = reactive({
  comment: ''
})

// 详情对话框
const detailDialog = reactive({
  visible: false,
  currentApplication: null
})

// 附件下载
const downloadAttachment = (application) => {
  if (application.attachment_path) {
    const link = document.createElement('a')
    link.href = application.attachment_path
    link.download = getFileName(application.attachment_path)
    link.click()
  }
}

// 获取文件名
const getFileName = (path) => {
  return path ? path.split('/').pop() : ''
}

// 获取待审批申请
const fetchPendingApplications = async () => {
  tableLoading.value = true
  try {
    const response = await apiService.attendance.getLeaveApplications()
    const applications = response.applications || response || []
    pendingApplications.value = applications.filter(app => 
      app.status === 'pending' || 
      app.status === 'approved_level_1' || 
      app.status === 'approved_level_2'
    )
  } catch (error) {
    console.error('获取待审批申请失败:', error)
    ElMessage.error('获取待审批申请失败')
  } finally {
    tableLoading.value = false
  }
}

// 获取审批历史
const fetchApprovalHistory = async () => {
  historyLoading.value = true
  try {
    const response = await apiService.attendance.getLeaveApplications()
    const applications = response.applications || response || []
    approvalHistory.value = applications.filter(app => 
      app.status === 'approved' || 
      app.status === 'rejected'
    )
    historyTotal.value = approvalHistory.value.length
  } catch (error) {
    console.error('获取审批历史失败:', error)
    ElMessage.error('获取审批历史失败')
  } finally {
    historyLoading.value = false
  }
}

// 请假类型标签
const getLeaveTypeTag = (type) => {
  const tags = {
    annual: 'success',
    sick: 'warning',
    personal: 'info',
    compensatory: 'primary',
    marriage: 'danger',
    maternity: 'danger',
    paternity: 'primary',
    bereavement: 'info'
  }
  return tags[type] || ''
}

const getLeaveTypeText = (type) => {
  const texts = {
    annual: '年假',
    sick: '病假',
    personal: '事假',
    compensatory: '调休假',
    marriage: '婚假',
    maternity: '产假',
    paternity: '陪产假',
    bereavement: '丧假'
  }
  return texts[type] || type
}

// 状态标签
const getStatusTag = (status) => {
  const tags = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return tags[status] || ''
}

const getStatusText = (status) => {
  const texts = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    'approved_level_1': '一级审批通过',
    'approved_level_2': '二级审批通过',
    'approved_level_3': '三级审批通过'
  }
  return texts[status] || status
}

// 批准申请
const handleApprove = (application) => {
  approvalDialog.visible = true
  approvalDialog.title = '批准请假申请'
  approvalDialog.type = 'approve'
  approvalDialog.currentApplication = application
  approvalForm.comment = ''
}

// 拒绝申请
const handleReject = (application) => {
  approvalDialog.visible = true
  approvalDialog.title = '拒绝请假申请'
  approvalDialog.type = 'reject'
  approvalDialog.currentApplication = application
  approvalForm.comment = ''
}

// 确认审批
const confirmApproval = async () => {
  if (!approvalDialog.currentApplication) return
  
  approvalLoading.value = true
  try {
    const approvalData = {
      action: approvalDialog.type === 'approve' ? 'approve' : 'reject',
      comment: approvalForm.comment
    }
    
    const response = await apiService.attendance.approveLeaveApplication(
      approvalDialog.currentApplication.id, 
      approvalData
    )
    
    ElMessage.success(`申请已${approvalDialog.type === 'approve' ? '批准' : '拒绝'}`)
    approvalDialog.visible = false
    fetchPendingApplications()
    fetchApprovalHistory()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '操作失败')
  } finally {
    approvalLoading.value = false
  }
}

// 查看申请详情
const viewApplicationDetail = (application) => {
  detailDialog.visible = true
  detailDialog.currentApplication = application
}

// 分页处理
const handleHistorySizeChange = (size) => {
  historyPageSize.value = size
  historyPage.value = 1
  fetchApprovalHistory()
}

const handleHistoryPageChange = (page) => {
  historyPage.value = page
  fetchApprovalHistory()
}

const handleExport = async () => {
  try {
    const response = await apiService.attendance.exportLeaveApplications()
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `请假申请_${new Date().toISOString().slice(0, 10)}.xlsx`
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
    
    const response = await apiService.attendance.importLeaveApplications(formData)
    ElMessage.success(response.data.message || '导入成功')
    showImportDialog.value = false
    importFileList.value = []
    fetchPendingApplications()
    fetchApprovalHistory()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '导入失败')
  } finally {
    importLoading.value = false
  }
}

onMounted(() => {
  fetchPendingApplications()
  fetchApprovalHistory()
})
</script>

<style scoped>
.leave-approval {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pending-applications, .approval-history {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.application-info p {
  margin: 5px 0;
  line-height: 1.5;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.application-detail {
  max-height: 400px;
  overflow-y: auto;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .leave-approval {
    padding: 12px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .header h1 {
    font-size: 18px;
  }

  .pending-applications, .approval-history {
    margin-bottom: 16px;
  }

  .card-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .application-info p {
    font-size: 13px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th, .el-table td {
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

  .application-detail {
    max-height: 60vh;
  }

  .el-form-item {
    margin-bottom: 12px;
  }

  .el-form-item__label {
    font-size: 12px;
  }
}

@media screen and (max-width: 480px) {
  .leave-approval {
    padding: 8px;
  }

  .header h1 {
    font-size: 16px;
  }

  .application-info p {
    font-size: 12px;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>