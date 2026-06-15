<template>
  <div class="overtime-application-container">
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
            <h1>加班申请</h1>
            <p class="subtitle">提交和管理您的加班申请记录</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button @click="$router.back()" class="btn-back">
            <el-icon><ArrowLeft /></el-icon>
            返回
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
              <div class="stat-value">{{ totalCount }}</div>
              <div class="stat-label">申请总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-pending">
            <div class="stat-icon-wrapper stat-icon-wrapper-pending">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ pendingCount }}</div>
              <div class="stat-label">待审批</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-approved">
            <div class="stat-icon-wrapper stat-icon-wrapper-approved">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ approvedCount }}</div>
              <div class="stat-label">已通过</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-rejected">
            <div class="stat-icon-wrapper stat-icon-wrapper-rejected">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ rejectedCount }}</div>
              <div class="stat-label">已拒绝</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 本月工时统计 -->
    <div class="stats-row animate-fade-in-up delay-150">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="24" :md="24" :lg="24">
          <div class="stat-card stat-card-hours">
            <div class="stat-icon-wrapper stat-icon-wrapper-hours">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ monthHours }}</div>
              <div class="stat-label">本月累计工时（小时）</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 申请表单 -->
    <div class="form-section animate-fade-in-up delay-200">
      <el-card class="glass-card application-form" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Edit /></el-icon>
              填写申请
            </span>
          </div>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="加班日期" prop="date">
            <el-date-picker
              v-model="form.date"
              type="date"
              placeholder="选择加班日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
              :disabled-date="disabledDate"
            />
          </el-form-item>

          <el-form-item label="加班时间" required>
            <el-col :span="11">
              <el-form-item prop="start_time">
                <el-time-picker
                  v-model="form.start_time"
                  placeholder="开始时间"
                  format="HH:mm"
                  value-format="HH:mm"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" class="text-center">-</el-col>
            <el-col :span="11">
              <el-form-item prop="end_time">
                <el-time-picker
                  v-model="form.end_time"
                  placeholder="结束时间"
                  format="HH:mm"
                  value-format="HH:mm"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="加班时长">
            <el-input v-model="calculatedHours" readonly>
              <template #append>小时</template>
            </el-input>
          </el-form-item>

          <el-form-item label="加班事由" prop="reason">
            <el-input
              v-model="form.reason"
              type="textarea"
              :rows="4"
              placeholder="请详细说明加班原因和内容"
            />
          </el-form-item>

          <el-form-item label="审批人" prop="approver_id">
            <el-select
              v-model="form.approver_id"
              placeholder="请选择审批人"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="user in approverList"
                :key="user.id"
                :label="`${user.real_name || user.username} (${user.department || ''})`"
                :value="user.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="submitting" class="btn-gradient">
              <el-icon><Check /></el-icon>
              提交申请
            </el-button>
            <el-button @click="handleReset" class="btn-secondary">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 申请历史 -->
    <div class="history-section animate-fade-in-up delay-300" v-if="myApplications.length > 0">
      <el-card class="glass-card history-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><List /></el-icon>
              我的加班申请记录
            </span>
            <span class="total-count">共 {{ myApplications.length }} 条记录</span>
          </div>
        </template>
        <el-table :data="myApplications" stripe class="custom-table">
          <el-table-column prop="date" label="加班日期" width="120" align="center">
            <template #default="{ row }">
              <span class="date-badge">{{ row.date }}</span>
            </template>
          </el-table-column>
          <el-table-column label="加班时间" min-width="160" align="center">
            <template #default="{ row }">
              <div class="time-range">
                <span class="time-start">{{ row.start_time }}</span>
                <span class="time-separator">→</span>
                <span class="time-end">{{ row.end_time }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="total_hours" label="时长" width="100" align="center">
            <template #default="{ row }">
              <span class="hours-badge">{{ row.total_hours }}h</span>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="加班事由" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="reason-text">{{ row.reason }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small" effect="light" class="status-tag">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="approver_name" label="审批人" width="120" align="center">
            <template #default="{ row }">
              <div class="approver-info">
                <el-icon><User /></el-icon>
                <span>{{ row.approver_name || '-' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="申请时间" width="160" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatDate(row.created_at) }}</div>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Timer, Document, Clock, CircleCheck, CircleClose, Calendar, Edit, Check, Refresh, List, User } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const myApplications = ref([])
const approverList = ref([])

const form = reactive({
  date: '',
  start_time: '',
  end_time: '',
  reason: '',
  approver_id: ''
})

const rules = {
  date: [
    { required: true, message: '请选择加班日期', trigger: 'change' }
  ],
  start_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  end_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ],
  reason: [
    { required: true, message: '请输入加班事由', trigger: 'blur' },
    { min: 5, message: '加班事由至少5个字符', trigger: 'blur' }
  ]
}

// 计算加班时长
const calculatedHours = computed(() => {
  if (!form.start_time || !form.end_time) return '0'
  
  const [startHour, startMin] = form.start_time.split(':').map(Number)
  const [endHour, endMin] = form.end_time.split(':').map(Number)
  
  const startMinutes = startHour * 60 + startMin
  const endMinutes = endHour * 60 + endMin
  
  if (endMinutes <= startMinutes) {
    return '0'
  }
  
  const diffMinutes = endMinutes - startMinutes
  return (diffMinutes / 60).toFixed(1)
})

// 统计计算
const totalCount = computed(() => myApplications.value.length)
const pendingCount = computed(() => myApplications.value.filter(a => a.status === 'pending').length)
const approvedCount = computed(() => myApplications.value.filter(a => a.status === 'approved').length)
const rejectedCount = computed(() => myApplications.value.filter(a => a.status === 'rejected').length)
const monthHours = computed(() => {
  const currentMonth = new Date().toISOString().slice(0, 7)
  return myApplications.value
    .filter(a => a.date && a.date.startsWith(currentMonth) && a.status === 'approved')
    .reduce((sum, a) => sum + (parseFloat(a.total_hours) || 0), 0)
    .toFixed(1)
})

const disabledDate = (time) => {
  return time.getTime() > Date.now()
}

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

const handleSubmit = async () => {
  if (parseFloat(calculatedHours.value) <= 0) {
    ElMessage.warning('加班时间必须大于 0')
    return
  }
  
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const submitData = {
          date: form.date,
          start_time: form.start_time,
          end_time: form.end_time,
          reason: form.reason,
          total_hours: parseFloat(calculatedHours.value)
        }
        if (form.approver_id) {
          submitData.approver_id = form.approver_id
        }
        await apiService.attendance.createOvertimeApplication(submitData)
        ElMessage.success('加班申请提交成功')
        handleReset()
        fetchMyApplications()
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '提交失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleReset = () => {
  formRef.value?.resetFields()
  form.date = ''
  form.start_time = ''
  form.end_time = ''
  form.reason = ''
  form.approver_id = ''
}

const fetchMyApplications = async () => {
  try {
    const response = await apiService.attendance.getOvertimeApplications({})
    myApplications.value = response.applications || []
  } catch (error) {
    console.error('获取加班申请记录失败', error)
  }
}

const fetchApproverList = async () => {
  try {
    const response = await apiService.users.getList({ 
      per_page: 100 
    })
    approverList.value = response.users || []
  } catch (error) {
    console.error('获取审批人列表失败', error)
  }
}

onMounted(() => {
  fetchMyApplications()
  fetchApproverList()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.overtime-application-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(56, 189, 248, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(14, 165, 233, 0.3) 0%, transparent 50%);
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

.btn-back {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 16px;
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
.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-pending::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-approved::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-rejected::before { background: linear-gradient(90deg, #ef4444, #f87171); }
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

.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-icon-wrapper-pending {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-approved {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-rejected {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 15px -3px rgba(239, 68, 68, 0.4);
}

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

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-pending .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-approved .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-rejected .stat-value {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
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

/* 表单区域 */
.form-section {
  margin-bottom: 24px;
}

.application-form :deep(.el-card__header) {
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
  color: #0ea5e9;
  font-size: 18px;
}

.total-count {
  font-size: 13px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 12px;
  border-radius: 20px;
}

.text-center {
  text-align: center;
  line-height: 32px;
  color: #64748b;
  font-weight: 500;
}

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5);
}

.btn-secondary {
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(56, 189, 248, 0.1);
  border-color: #0ea5e9;
  color: #0ea5e9;
}

/* 历史记录区域 */
.history-section {
  margin-bottom: 20px;
}

.history-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(56, 189, 248, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.date-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #475569;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.time-range {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.time-start, .time-end {
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.time-separator {
  color: #94a3b8;
  font-size: 12px;
}

.hours-badge {
  font-size: 14px;
  font-weight: 700;
  color: #7dd3fc;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  padding: 4px 12px;
  border-radius: 20px;
}

.reason-text {
  color: #475569;
  font-size: 13px;
  line-height: 1.5;
}

.status-tag {
  font-weight: 500;
  border-radius: 6px;
}

.approver-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 13px;
  color: #475569;
}

.approver-info .el-icon {
  font-size: 14px;
  color: #94a3b8;
}

.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 12px;
  color: #64748b;
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
.delay-150 { animation-delay: 150ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .overtime-application-container {
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
  }

  .header-actions .el-button {
    width: 100%;
  }

  .stats-row {
    margin-bottom: 16px;
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

  .form-section {
    margin-bottom: 20px;
  }

  .application-form :deep(.el-card__body) {
    padding: 16px;
  }

  .el-form-item {
    margin-bottom: 16px;
  }

  .el-form-item__label {
    font-size: 13px;
    padding-bottom: 4px;
  }

  .text-center {
    line-height: 24px;
    padding: 8px 0;
  }

  .history-section {
    margin-top: 16px;
  }

  .history-card :deep(.el-card__body) {
    padding: 12px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .time-range {
    flex-direction: column;
    gap: 2px;
  }

  .time-separator {
    transform: rotate(90deg);
  }

  .hours-badge {
    padding: 2px 8px;
    font-size: 12px;
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

  .application-form :deep(.el-card__body) {
    padding: 12px;
  }

  .el-form-item__label {
    font-size: 12px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .text-center {
    padding: 4px 0;
  }
}
</style>
