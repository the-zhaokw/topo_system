<template>
  <div class="leave-approval-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><DocumentChecked /></el-icon>
          </div>
          <div class="title-text">
            <h1>请假审批</h1>
            <p class="subtitle">管理和审批员工的请假申请</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button class="btn-export" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          <el-button class="btn-import" type="success" @click="showImportDialog = true">
            <el-icon><Upload /></el-icon>
            导入
          </el-button>
          <el-button class="btn-refresh" @click="fetchPendingApplications">
            <el-icon><Refresh /></el-icon>
            刷新
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
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ pendingApplications.length }}</div>
              <div class="stat-label">待审批总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-leave">
            <div class="stat-icon-wrapper stat-icon-wrapper-leave">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ leaveCount }}</div>
              <div class="stat-label">请假申请</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-overtime">
            <div class="stat-icon-wrapper stat-icon-wrapper-overtime">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overtimeCount }}</div>
              <div class="stat-label">加班申请</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-compensatory">
            <div class="stat-icon-wrapper stat-icon-wrapper-compensatory">
              <el-icon><RefreshLeft /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ compensatoryCount }}</div>
              <div class="stat-label">调休申请</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 待审批申请 -->
    <div class="content-section animate-fade-in-up delay-200">
      <el-card class="glass-card pending-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon><Bell /></el-icon>
              <h3>待审批申请</h3>
              <span class="count-badge badge-warning">{{ pendingApplications.length }}</span>
            </div>
          </div>
        </template>

        <el-table :data="pendingApplications" v-loading="tableLoading" class="custom-table" stripe>
          <el-table-column prop="id" label="申请ID" width="80" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="applicant" label="申请人" width="120">
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-name">{{ row.applicant?.name || row.applicant?.username || row.applicant }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="leave_type" label="请假类型" width="110" align="center">
            <template #default="{ row }">
              <el-tag :type="getLeaveTypeTag(row.leave_type)" size="small" effect="light" class="type-tag">
                {{ getLeaveTypeText(row.leave_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始日期" width="110" align="center">
            <template #default="{ row }">
              <span class="date-text">{{ row.start_date }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="end_date" label="结束日期" width="110" align="center">
            <template #default="{ row }">
              <span class="date-text">{{ row.end_date }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="days" label="天数" width="70" align="center">
            <template #default="{ row }">
              <span class="days-badge">{{ row.days }}天</span>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="请假事由" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="reason-text">{{ row.reason }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="current_approver_level" label="审批层级" width="90" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.current_approver_level" type="info" size="small" effect="light" class="level-tag">
                第{{ row.current_approver_level }}级
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="emergency_flag" label="紧急" width="70" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.emergency_flag" type="danger" size="small" effect="dark" class="emergency-tag">
                <el-icon><Warning /></el-icon>
                紧急
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="申请时间" width="150" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatTime(row.created_at) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" type="success" @click="handleApprove(row)" class="btn-approve">
                  <el-icon><Check /></el-icon>
                  批准
                </el-button>
                <el-button size="small" type="danger" @click="handleReject(row)" class="btn-reject">
                  <el-icon><Close /></el-icon>
                  拒绝
                </el-button>
                <el-button size="small" @click="viewApplicationDetail(row)" class="btn-detail">
                  详情
                </el-button>
                <el-button size="small" v-if="row.attachment_path" @click="downloadAttachment(row)" class="btn-attachment">
                  <el-icon><Paperclip /></el-icon>
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 审批历史 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card history-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon><Clock /></el-icon>
              <h3>审批历史</h3>
              <span class="count-badge badge-info">{{ historyTotal }}</span>
            </div>
            <el-button @click="fetchApprovalHistory" class="btn-refresh-small">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>

        <el-table :data="approvalHistory" v-loading="historyLoading" class="custom-table" stripe>
          <el-table-column prop="id" label="申请ID" width="80" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="applicant" label="申请人" width="120">
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-name">{{ row.applicant?.name || row.applicant?.username || row.applicant }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="leave_type" label="请假类型" width="110" align="center">
            <template #default="{ row }">
              <el-tag :type="getLeaveTypeTag(row.leave_type)" size="small" effect="light" class="type-tag">
                {{ getLeaveTypeText(row.leave_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始日期" width="110" align="center">
            <template #default="{ row }">
              <span class="date-text">{{ row.start_date }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="end_date" label="结束日期" width="110" align="center">
            <template #default="{ row }">
              <span class="date-text">{{ row.end_date }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="days" label="天数" width="70" align="center">
            <template #default="{ row }">
              <span class="days-badge">{{ row.days }}天</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)" size="small" effect="light" class="status-tag">
                <el-icon v-if="row.status === 'approved'"><CircleCheck /></el-icon>
                <el-icon v-else-if="row.status === 'rejected'"><CircleClose /></el-icon>
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="approver" label="审批人" width="120">
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-name">{{ row.approver?.name || row.approver?.username || row.approver || '-' }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="approved_at" label="审批时间" width="150" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatTime(row.approved_at) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="approval_comment" label="审批意见" min-width="150" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="comment-text">{{ row.approval_comment || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90" align="center" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewApplicationDetail(row)" class="btn-detail">
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-section">
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
    </div>

    <!-- 审批对话框 -->
    <el-dialog
      v-model="approvalDialog.visible"
      :title="approvalDialog.title"
      width="520px"
      class="approval-dialog"
      destroy-on-close
    >
      <div class="dialog-content">
        <div class="application-info-card">
          <div class="info-header">
            <el-icon><Document /></el-icon>
            <span>申请信息</span>
          </div>
          <div class="info-body">
            <div class="info-row">
              <span class="info-label">申请人</span>
              <span class="info-value">{{ approvalDialog.currentApplication?.applicant?.name || approvalDialog.currentApplication?.applicant?.username || approvalDialog.currentApplication?.applicant }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">请假类型</span>
              <el-tag :type="getLeaveTypeTag(approvalDialog.currentApplication?.leave_type)" size="small">
                {{ getLeaveTypeText(approvalDialog.currentApplication?.leave_type) }}
              </el-tag>
            </div>
            <div class="info-row">
              <span class="info-label">请假时间</span>
              <span class="info-value">{{ approvalDialog.currentApplication?.start_date }} 至 {{ approvalDialog.currentApplication?.end_date }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">请假天数</span>
              <span class="info-value highlight">{{ approvalDialog.currentApplication?.days }} 天</span>
            </div>
            <div class="info-row">
              <span class="info-label">审批层级</span>
              <span class="info-value">第{{ approvalDialog.currentApplication?.current_approver_level || 1 }}级</span>
            </div>
            <div class="info-row">
              <span class="info-label">紧急情况</span>
              <el-tag v-if="approvalDialog.currentApplication?.emergency_flag" type="danger" size="small" effect="dark">
                <el-icon><Warning /></el-icon> 紧急
              </el-tag>
              <el-tag v-else type="success" size="small">正常</el-tag>
            </div>
            <div class="info-row full-width">
              <span class="info-label">请假事由</span>
              <p class="info-text">{{ approvalDialog.currentApplication?.reason }}</p>
            </div>
            <div class="info-row full-width" v-if="approvalDialog.currentApplication?.attachment_path">
              <span class="info-label">附件</span>
              <el-button type="primary" link @click="downloadAttachment(approvalDialog.currentApplication)" class="attachment-link">
                <el-icon><Paperclip /></el-icon>
                {{ getFileName(approvalDialog.currentApplication?.attachment_path) }}
              </el-button>
            </div>
          </div>
        </div>
        
        <el-form :model="approvalForm" label-position="top" class="approval-form">
          <el-form-item label="审批意见" prop="comment">
            <el-input
              v-model="approvalForm.comment"
              type="textarea"
              :rows="3"
              placeholder="请输入审批意见（可选）"
              maxlength="200"
              show-word-limit
              class="comment-input"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="approvalDialog.visible = false" class="btn-cancel">取消</el-button>
          <el-button 
            :type="approvalDialog.type === 'approve' ? 'success' : 'danger'" 
            @click="confirmApproval"
            :loading="approvalLoading"
            class="btn-confirm"
          >
            <el-icon v-if="approvalDialog.type === 'approve'"><Check /></el-icon>
            <el-icon v-else><Close /></el-icon>
            确认{{ approvalDialog.type === 'approve' ? '批准' : '拒绝' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 申请详情对话框 -->
    <el-dialog
      v-model="detailDialog.visible"
      title="申请详情"
      width="640px"
      class="detail-dialog"
      destroy-on-close
    >
      <div class="detail-content" v-if="detailDialog.currentApplication">
        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="申请ID" align="center">
            <span class="id-highlight">{{ detailDialog.currentApplication.id }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="申请人" align="center">
            {{ detailDialog.currentApplication.applicant?.name || detailDialog.currentApplication.applicant?.username || detailDialog.currentApplication.applicant }}
          </el-descriptions-item>
          <el-descriptions-item label="请假类型" align="center">
            <el-tag :type="getLeaveTypeTag(detailDialog.currentApplication.leave_type)" size="small">
              {{ getLeaveTypeText(detailDialog.currentApplication.leave_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="请假天数" align="center">
            <span class="days-highlight">{{ detailDialog.currentApplication.days }} 天</span>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期" align="center">
            {{ detailDialog.currentApplication.start_date }}
          </el-descriptions-item>
          <el-descriptions-item label="结束日期" align="center">
            {{ detailDialog.currentApplication.end_date }}
          </el-descriptions-item>
          <el-descriptions-item label="申请时间" align="center">
            {{ detailDialog.currentApplication.created_at }}
          </el-descriptions-item>
          <el-descriptions-item label="状态" align="center">
            <el-tag :type="getStatusTag(detailDialog.currentApplication.status)" size="small" effect="light">
              {{ getStatusText(detailDialog.currentApplication.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="审批人" :span="2">
            {{ detailDialog.currentApplication.approver?.name || detailDialog.currentApplication.approver?.username || detailDialog.currentApplication.approver || '待审批' }}
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
        </el-descriptions>
        
        <div class="approval-flow-section" v-if="detailDialog.currentApplication.approval_levels && detailDialog.currentApplication.approval_levels.length > 0">
          <div class="flow-header">
            <el-icon><Connection /></el-icon>
            <span>审批流程</span>
          </div>
          <el-timeline class="approval-timeline">
            <el-timeline-item
              v-for="(level, index) in detailDialog.currentApplication.approval_levels"
              :key="index"
              :type="level.status === 'approved' ? 'success' : level.status === 'rejected' ? 'danger' : 'info'"
              :timestamp="level.approved_at"
              placement="top"
              class="timeline-item"
            >
              <div class="timeline-content">
                <div class="timeline-title">第{{ level.level }}级审批</div>
                <div class="timeline-approver">{{ level.approver_name || '待审批' }}</div>
                <div class="timeline-status" v-if="level.status">
                  <el-tag :type="level.status === 'approved' ? 'success' : level.status === 'rejected' ? 'danger' : 'info'" size="small">
                    {{ level.status === 'approved' ? '已批准' : level.status === 'rejected' ? '已拒绝' : '待审批' }}
                  </el-tag>
                </div>
                <div class="timeline-comment" v-if="level.comment">{{ level.comment }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialog.visible = false" class="btn-close">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入请假申请" width="500px" class="import-dialog" destroy-on-close>
      <div class="import-content">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".csv,.xlsx"
          :on-change="handleFileChange"
          :file-list="importFileList"
          class="upload-area"
          drag
        >
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="upload-text">
            <em>点击上传</em> 或拖拽文件到此处
          </div>
          <template #tip>
            <div class="upload-tip">
              <p>支持 CSV/Excel 格式</p>
              <p>必要列：申请人、请假类型、开始日期、结束日期、请假事由</p>
              <p>请假类型可选：年假、病假、事假、调休假、婚假、产假、陪产假、丧假</p>
            </div>
          </template>
        </el-upload>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showImportDialog = false" class="btn-cancel">取消</el-button>
          <el-button type="primary" @click="handleImport" :loading="importLoading" class="btn-confirm">
            <el-icon><Upload /></el-icon>
            导入
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Download, Upload, DocumentChecked, Document, Bell, Clock, Calendar, Timer, RefreshLeft, Check, Close, Warning, Paperclip, CircleCheck, CircleClose, UploadFilled, Connection } from '@element-plus/icons-vue'
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

// 计算统计数据
const leaveCount = computed(() => {
  return pendingApplications.value.filter(app => 
    ['annual', 'sick', 'personal', 'marriage', 'maternity', 'paternity', 'bereavement'].includes(app.leave_type)
  ).length
})

const overtimeCount = computed(() => {
  return pendingApplications.value.filter(app => app.leave_type === 'overtime').length
})

const compensatoryCount = computed(() => {
  return pendingApplications.value.filter(app => app.leave_type === 'compensatory').length
})

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

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return timeStr
}

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
    bereavement: 'info',
    overtime: 'warning'
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
    bereavement: '丧假',
    overtime: '加班'
  }
  return texts[type] || type
}

// 状态标签
const getStatusTag = (status) => {
  const tags = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    approved_level_1: 'info',
    approved_level_2: 'info',
    approved_level_3: 'info'
  }
  return tags[status] || ''
}

const getStatusText = (status) => {
  const texts = {
    pending: '待审批',
    approved: '已通过',
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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.leave-approval-container {
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
  gap: 12px;
}

.btn-export,
.btn-import,
.btn-refresh {
  transition: all 0.3s;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.btn-export:hover,
.btn-import:hover,
.btn-refresh:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
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

/* 5种不同的渐变配色 */
.stat-card-total::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card-leave::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-overtime::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-compensatory::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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

.stat-icon-wrapper-leave {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-overtime {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-compensatory {
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

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-leave .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-overtime .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-compensatory .stat-value {
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

.content-section {
  margin-bottom: 24px;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-title .el-icon {
  color: #6366f1;
  font-size: 20px;
}

.card-title h3 {
  margin: 0;
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
}

.count-badge {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
}

.badge-warning {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
}

.badge-info {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #6366f1;
}

.btn-refresh-small {
  transition: all 0.3s;
}

.btn-refresh-small:hover {
  transform: translateY(-2px);
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

.user-info {
  line-height: 1.4;
}

.user-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.type-tag,
.status-tag,
.level-tag {
  font-weight: 500;
  border-radius: 6px;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.emergency-tag {
  font-weight: 600;
  border-radius: 6px;
}

.date-text {
  color: #475569;
  font-size: 13px;
}

.days-badge {
  font-weight: 600;
  color: #6366f1;
  background: rgba(99, 102, 241, 0.1);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
}

.reason-text {
  color: #475569;
  font-size: 13px;
}

.comment-text {
  color: #64748b;
  font-size: 13px;
}

.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

.action-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.btn-approve,
.btn-reject,
.btn-detail,
.btn-attachment {
  transition: all 0.3s;
}

.btn-approve:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.btn-reject:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.btn-detail:hover {
  transform: translateY(-2px);
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 审批对话框 */
.approval-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 24px;
  margin-right: 0;
}

.approval-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.approval-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.dialog-content {
  padding: 8px 0;
}

.application-info-card {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  background: rgba(99, 102, 241, 0.1);
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  font-weight: 600;
  color: #6366f1;
}

.info-body {
  padding: 18px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-row.full-width {
  grid-column: span 2;
}

.info-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
}

.info-value.highlight {
  color: #6366f1;
  font-weight: 700;
}

.info-text {
  margin: 0;
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
  background: white;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.attachment-link {
  justify-content: flex-start;
}

.approval-form {
  margin-top: 20px;
}

.comment-input :deep(.el-textarea__inner) {
  border-radius: 10px;
  resize: none;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel,
.btn-confirm {
  transition: all 0.3s;
}

.btn-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

/* 详情对话框 */
.detail-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 24px;
  margin-right: 0;
}

.detail-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.detail-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.detail-content {
  padding: 8px 0;
}

.detail-descriptions {
  margin-bottom: 24px;
}

.detail-descriptions :deep(.el-descriptions__label) {
  background: rgba(241, 245, 249, 0.8);
  font-weight: 600;
  color: #475569;
}

.id-highlight {
  font-family: 'Monaco', 'Menlo', monospace;
  font-weight: 600;
  color: #6366f1;
}

.days-highlight {
  font-weight: 700;
  color: #6366f1;
}

.approval-flow-section {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.flow-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-weight: 600;
  color: #6366f1;
}

.approval-timeline {
  padding-left: 8px;
}

.timeline-item :deep(.el-timeline-item__node) {
  width: 12px;
  height: 12px;
}

.timeline-content {
  background: white;
  padding: 14px;
  border-radius: 10px;
  border: 1px solid rgba(226, 232, 240, 0.6);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.timeline-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.timeline-approver {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.timeline-status {
  margin-bottom: 8px;
}

.timeline-comment {
  font-size: 13px;
  color: #475569;
  background: rgba(241, 245, 249, 0.5);
  padding: 8px 12px;
  border-radius: 6px;
  margin-top: 8px;
}

.btn-close {
  transition: all 0.3s;
}

.btn-close:hover {
  transform: translateY(-2px);
}

/* 导入对话框 */
.import-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 24px;
  margin-right: 0;
}

.import-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.import-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.import-content {
  padding: 20px 0;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
  border-radius: 12px;
  border: 2px dashed rgba(99, 102, 241, 0.3);
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: all 0.3s;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #6366f1;
  background: rgba(99, 102, 241, 0.05);
}

.upload-icon {
  font-size: 48px;
  color: #6366f1;
  margin-bottom: 16px;
}

.upload-text {
  color: #64748b;
  font-size: 14px;
}

.upload-text em {
  color: #6366f1;
  font-style: normal;
  font-weight: 600;
}

.upload-tip {
  margin-top: 16px;
  text-align: center;
}

.upload-tip p {
  margin: 4px 0;
  font-size: 12px;
  color: #94a3b8;
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
  .leave-approval-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
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
    flex-wrap: wrap;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
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

  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .action-buttons {
    flex-wrap: wrap;
  }

  .action-buttons .el-button {
    padding: 6px 10px;
    font-size: 12px;
  }

  .info-body {
    grid-template-columns: 1fr;
  }

  .info-row.full-width {
    grid-column: span 1;
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

  .upload-area :deep(.el-upload-dragger) {
    height: 160px;
  }

  .upload-icon {
    font-size: 36px;
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

  .action-buttons .el-button {
    padding: 4px 8px;
    font-size: 11px;
  }
}
</style>
