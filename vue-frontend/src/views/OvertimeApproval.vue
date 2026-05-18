<template>
  <div class="overtime-approval-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Timer /></el-icon>
          </div>
          <div class="title-text">
            <h1>加班审批</h1>
            <p class="subtitle">审批员工的加班申请</p>
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
              <div class="stat-value">{{ pagination.total }}</div>
              <div class="stat-label">待审批总数</div>
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
          <div class="stat-card stat-card-leave">
            <div class="stat-icon-wrapper stat-icon-wrapper-leave">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ leaveCount }}</div>
              <div class="stat-label">调休申请</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-today">
            <div class="stat-icon-wrapper stat-icon-wrapper-today">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ todayCount }}</div>
              <div class="stat-label">今日待审</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-hours">
            <div class="stat-icon-wrapper stat-icon-wrapper-hours">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalHours }}</div>
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
        <div class="toolbar">
          <el-form :inline="true" :model="filterForm" class="filter-form">
            <el-form-item label="状态">
              <el-select v-model="filterForm.status" placeholder="全部状态" clearable class="filter-select">
                <el-option label="待审批" value="pending"></el-option>
                <el-option label="已通过" value="approved"></el-option>
                <el-option label="已拒绝" value="rejected"></el-option>
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
          <div class="header-actions">
            <el-button @click="handleExport" class="btn-export">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
            <el-button type="success" @click="showImportDialog = true" class="btn-import">
              <el-icon><Upload /></el-icon>
              导入
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 申请列表 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><List /></el-icon>
              <h3>加班申请列表</h3>
              <span class="total-count">共 {{ pagination.total }} 条记录</span>
            </div>
          </div>
        </template>

        <el-table :data="applicationList" v-loading="loading" stripe class="custom-table">
          <el-table-column prop="user_real_name" label="申请人" min-width="100">
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-name">{{ row.user_real_name || row.user_name }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="date" label="加班日期" width="120">
            <template #default="{ row }">
              <span class="date-text">{{ row.date }}</span>
            </template>
          </el-table-column>
          <el-table-column label="加班时间" min-width="160">
            <template #default="{ row }">
              <div class="time-range">
                <el-icon><Clock /></el-icon>
                <span>{{ row.start_time }} - {{ row.end_time }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="total_hours" label="时长(小时)" width="100">
            <template #default="{ row }">
              <span class="hours-badge">{{ row.total_hours }}h</span>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="加班事由" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="reason-text">{{ row.reason }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" effect="light" class="status-tag">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="approver_name" label="审批人" width="120">
            <template #default="{ row }">
              <span class="approver-text">{{ row.approver_name || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="申请时间" width="160">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatDate(row.created_at) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right" align="center">
            <template #default="{ row }">
              <el-button v-if="row.status === 'pending'" type="primary" link @click="handleApprove(row)" class="action-btn approve-btn">
                <el-icon><Check /></el-icon>
                批准
              </el-button>
              <el-button v-if="row.status === 'pending'" type="danger" link @click="handleReject(row)" class="action-btn reject-btn">
                <el-icon><Close /></el-icon>
                拒绝
              </el-button>
              <el-button type="info" link @click="handleViewDetail(row)" class="action-btn view-btn">
                <el-icon><View /></el-icon>
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-section">
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
    </div>

    <el-dialog v-model="dialogVisible" title="审批加班申请" width="500px" class="approval-dialog">
      <el-descriptions :column="1" border v-if="currentApplication" class="detail-descriptions">
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
          <span class="hours-highlight">{{ currentApplication.total_hours }} 小时</span>
        </el-descriptions-item>
        <el-descriptions-item label="加班事由">
          {{ currentApplication.reason }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentApplication.status)" effect="light">
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
      
      <el-form v-if="dialogType !== 'view'" :model="approvalForm" class="approval-form">
        <el-form-item label="审批意见">
          <el-input v-model="approvalForm.comment" type="textarea" :rows="3" placeholder="请输入审批意见（拒绝时必填）"></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-if="dialogType === 'approve'" type="primary" @click="submitApproval('approve')" class="btn-approve">批准</el-button>
        <el-button v-if="dialogType === 'reject'" type="danger" @click="submitApproval('reject')" class="btn-reject">拒绝</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入加班申请" width="500px" class="import-dialog">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".csv,.xlsx"
        :on-change="handleFileChange"
        :file-list="importFileList"
        class="upload-area"
      >
        <el-button type="primary" class="btn-gradient">
          <el-icon><Upload /></el-icon>
          选择文件
        </el-button>
        <template #tip>
          <div class="el-upload__tip">
            支持 CSV/Excel 格式，必要列：申请人、加班日期、开始时间、结束时间、加班事由
          </div>
        </template>
      </el-upload>
      
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importLoading" class="btn-gradient">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Download, Upload, Timer, Document, Calendar, Bell, Clock, Filter, List, Check, Close, View } from '@element-plus/icons-vue'
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

// 计算统计数据
const overtimeCount = computed(() => {
  return applicationList.value.filter(a => a.type === 'overtime' || !a.type).length
})

const leaveCount = computed(() => {
  return applicationList.value.filter(a => a.type === 'leave').length
})

const todayCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return applicationList.value.filter(a => a.created_at?.startsWith(today)).length
})

const totalHours = computed(() => {
  return applicationList.value.reduce((sum, a) => sum + (parseFloat(a.total_hours) || 0), 0).toFixed(1)
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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.overtime-approval-container {
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
.stat-card-overtime::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-leave::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-today::before { background: linear-gradient(90deg, #ec4899, #f472b6); }
.stat-card-hours::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }

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

.stat-icon-wrapper-overtime {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-leave {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-today {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
}

.stat-icon-wrapper-hours {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
  color: #2563eb;
  box-shadow: 0 4px 15px -3px rgba(59, 130, 246, 0.4);
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

.stat-card-overtime .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-leave .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-today .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-hours .stat-value {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
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

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.filter-form {
  padding: 10px 0;
}

.filter-select {
  width: 160px;
}

.header-actions {
  display: flex;
  gap: 10px;
  padding-top: 10px;
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

.btn-export,
.btn-import {
  transition: all 0.3s;
}

.btn-export:hover,
.btn-import:hover {
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

.user-info {
  line-height: 1.4;
}

.user-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.date-text {
  font-size: 13px;
  color: #475569;
}

.time-range {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #475569;
}

.time-range .el-icon {
  color: #6366f1;
  font-size: 14px;
}

.hours-badge {
  display: inline-block;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.reason-text {
  font-size: 13px;
  color: #475569;
}

.status-tag {
  font-weight: 500;
  border-radius: 6px;
}

.approver-text {
  font-size: 13px;
  color: #64748b;
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

.approve-btn:hover {
  color: #10b981;
}

.reject-btn:hover {
  color: #ef4444;
}

.view-btn:hover {
  color: #6366f1;
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
  padding: 20px;
  margin-right: 0;
}

.approval-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.approval-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.detail-descriptions :deep(.el-descriptions__label) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.hours-highlight {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
}

.approval-form {
  margin-top: 20px;
}

.btn-approve {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  border: none;
}

.btn-reject {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  border: none;
}

/* 导入对话框 */
.import-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  margin-right: 0;
}

.import-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.import-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.upload-area {
  padding: 20px 0;
}

.upload-area :deep(.el-upload__tip) {
  margin-top: 12px;
  color: #64748b;
  font-size: 13px;
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
  .overtime-approval-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
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

  .toolbar {
    flex-direction: column;
    gap: 12px;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 12px;
    width: 100%;
  }

  .filter-select {
    width: 100% !important;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
    padding-top: 0;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 8px 12px;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .action-btn {
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

  :deep(.el-pagination__sizes), :deep(.el-pagination__jump) {
    display: none !important;
  }

  .approval-dialog,
  .import-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .approval-dialog :deep(.el-dialog__header),
  .approval-dialog :deep(.el-dialog__body),
  .approval-dialog :deep(.el-dialog__footer),
  .import-dialog :deep(.el-dialog__header),
  .import-dialog :deep(.el-dialog__body),
  .import-dialog :deep(.el-dialog__footer) {
    padding: 12px !important;
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
}
</style>
