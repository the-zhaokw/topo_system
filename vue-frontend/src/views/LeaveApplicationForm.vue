<template>
  <div class="leave-form-container">
    <!-- 页面头部 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Calendar /></el-icon>
          </div>
          <div class="title-text">
            <h1>填写请假申请</h1>
            <p class="subtitle">填写请假信息并提交审批</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button @click="goBack" class="btn-back">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </div>
    </div>

    <!-- 请假申请表单 -->
    <div class="form-section animate-fade-in-up delay-100">
      <el-card class="glass-card application-form" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><EditPen /></el-icon>
              请假申请信息
            </span>
          </div>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="请假类型" prop="leave_type">
            <el-select v-model="form.leave_type" placeholder="请选择请假类型" class="form-select">
              <el-option label="年假" value="annual_leave" />
              <el-option label="病假" value="sick_leave" />
              <el-option label="事假" value="personal_leave" />
              <el-option label="调休假" value="other" />
              <el-option label="婚假" value="marriage_leave" />
              <el-option label="产假" value="maternity_leave" />
              <el-option label="陪产假" value="paternity_leave" />
              <el-option label="丧假" value="bereavement_leave" />
            </el-select>
          </el-form-item>

          <el-form-item label="请假时间" required>
            <el-col :span="11">
              <el-form-item prop="start_date">
                <el-date-picker
                  v-model="form.start_date"
                  type="date"
                  placeholder="开始日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                  @change="autoCalcDays"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2" class="text-center">-</el-col>
            <el-col :span="11">
              <el-form-item prop="end_date">
                <el-date-picker
                  v-model="form.end_date"
                  type="date"
                  placeholder="结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                  @change="autoCalcDays"
                />
              </el-form-item>
            </el-col>
          </el-form-item>

          <el-form-item label="请假天数" prop="days">
            <el-input-number
              v-model="form.days"
              :min="0.5"
              :step="0.5"
              :precision="1"
              placeholder="请假天数"
            />
            <span class="days-hint">天（0.5表示半天，选择日期后自动计算，可手动调整）</span>
          </el-form-item>

          <el-form-item label="紧急情况" prop="emergency_flag">
            <el-switch
              v-model="form.emergency_flag"
              active-text="紧急"
              inactive-text="正常"
            />
            <span class="emergency-hint">紧急情况可先电话/微信口头报备，48小时内补单</span>
          </el-form-item>

          <el-form-item label="附件上传" prop="attachment">
            <el-upload
              class="upload-demo"
              :action="uploadUrl"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeUpload"
              :show-file-list="false"
            >
              <el-button type="primary" class="btn-gradient">
                <el-icon><Upload /></el-icon>
                上传附件
              </el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持上传病假证明、结婚证等附件，文件大小不超过10MB
                </div>
              </template>
            </el-upload>
            <div v-if="form.attachment_path" class="attachment-info">
              <el-icon><Document /></el-icon>
              <span>{{ getFileName(form.attachment_path) }}</span>
              <el-button type="text" @click="removeAttachment" class="btn-text-danger">删除</el-button>
            </div>
          </el-form-item>

          <el-form-item label="多级审批">
            <el-switch
              v-model="enableMultiLevelApproval"
              active-text="启用多级审批"
              inactive-text="单级审批"
            />
          </el-form-item>

          <el-form-item v-if="!enableMultiLevelApproval" label="审批人" prop="approver_id">
            <el-select
              v-model="form.approver_id"
              placeholder="请选择审批人"
              filterable
              clearable
              remote
              :remote-method="searchUsers"
              :loading="loading"
              style="width: 100%"
              class="form-select"
            >
              <el-option
                v-for="user in allUsers"
                :key="user.id"
                :label="`${user.username} (${user.email}) - ${user.position || ''}`"
                :value="user.id"
              />
            </el-select>
            <div class="approver-hint">
              支持搜索用户名、邮箱、姓名、工号
            </div>
          </el-form-item>

          <el-form-item v-if="enableMultiLevelApproval" label="审批流程">
            <div v-for="(level, index) in approvalLevels" :key="index" class="approval-level-item">
              <el-tag type="info" class="level-tag">第{{ index + 1 }}级审批</el-tag>
              <el-select
                v-model="level.approver_id"
                placeholder="选择审批人"
                filterable
                clearable
                remote
                :remote-method="searchUsers"
                :loading="loading"
                style="width: 280px; margin-left: 10px;"
                class="form-select"
              >
                <el-option
                  v-for="user in allUsers"
                  :key="user.id"
                  :label="`${user.username} (${user.position || ''})`"
                  :value="user.id"
                />
              </el-select>
              <el-button 
                v-if="index > 0" 
                type="danger" 
                link 
                @click="removeApprovalLevel(index)"
                style="margin-left: 10px;"
                class="btn-text-danger"
              >
                删除
              </el-button>
            </div>
            <el-button 
              v-if="approvalLevels.length < 3" 
              type="primary" 
              link 
              @click="addApprovalLevel"
              class="btn-link-primary"
            >
              + 添加下一级审批
            </el-button>
            <div class="approver-hint">
              最多支持3级审批（如：组长 → 经理 → 总监）
            </div>
          </el-form-item>

          <el-form-item label="请假事由" prop="reason">
            <el-input
              v-model="form.reason"
              type="textarea"
              :rows="4"
              placeholder="请详细说明请假原因"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="loading" class="btn-gradient">
              提交申请
            </el-button>
            <el-button @click="handleReset" class="btn-secondary">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Upload, Document, Calendar, EditPen } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

// 表单数据
const form = reactive({
  leave_type: '',
  start_date: '',
  end_date: '',
  days: 1,
  reason: '',
  emergency_flag: false,
  attachment_path: '',
  approver_id: ''
})

// 文件上传URL
const uploadUrl = '/api/upload'

// 根据起止日期自动计算请假天数（含首尾两天的自然日数）
const autoCalcDays = () => {
  if (!form.start_date || !form.end_date) return
  // 直接解析 YYYY-MM-DD，避免 new Date 按 UTC 解析造成的时差误差
  const [sy, sm, sd] = form.start_date.split('-').map(Number)
  const [ey, em, ed] = form.end_date.split('-').map(Number)
  const start = new Date(sy, sm - 1, sd)
  const end = new Date(ey, em - 1, ed)
  if (end < start) return
  form.days = Math.round((end - start) / 86400000) + 1
}

// 表单验证规则
const rules = computed(() => ({
  leave_type: [{ required: true, message: '请选择请假类型', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  days: [
    { required: true, message: '请输入请假天数', trigger: 'blur' },
    { type: 'number', min: 0.5, message: '请假天数不能小于0.5天', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: '请输入请假事由', trigger: 'blur' },
    { min: 5, max: 500, message: '请假事由长度在5到500个字符之间', trigger: 'blur' }
  ],
  approver_id: enableMultiLevelApproval.value
    ? []
    : [{ required: true, message: '请选择审批人', trigger: 'change' }]
}))

// 所有用户列表（用于审批人选择）
const allUsers = ref([])

// 多级审批相关
const enableMultiLevelApproval = ref(false)
const approvalLevels = ref([
  { level: 1, approver_id: null, status: 'pending' }
])

const addApprovalLevel = () => {
  if (approvalLevels.value.length < 3) {
    approvalLevels.value.push({
      level: approvalLevels.value.length + 1,
      approver_id: null,
      status: 'pending'
    })
  }
}

const removeApprovalLevel = (index) => {
  approvalLevels.value.splice(index, 1)
  approvalLevels.value.forEach((level, i) => {
    level.level = i + 1
  })
}

// 搜索用户
const searchUsers = async (keyword) => {
  loading.value = true
  try {
    if (!keyword.trim()) {
      await fetchAllUsers()
      return
    }
    
    const response = await apiService.users.getApprovers()
    const allUsersList = response.users || []
    const keywordLower = keyword.toLowerCase()
    allUsers.value = allUsersList.filter(user => 
      user.username.toLowerCase().includes(keywordLower) ||
      user.email.toLowerCase().includes(keywordLower) ||
      (user.first_name && user.first_name.toLowerCase().includes(keywordLower)) ||
      (user.last_name && user.last_name.toLowerCase().includes(keywordLower))
    )
  } catch (error) {
    console.error('搜索用户失败:', error)
    await fetchAllUsers()
  } finally {
    loading.value = false
  }
}

// 获取所有用户列表
const fetchAllUsers = async () => {
  try {
    const response = await apiService.users.getApprovers()
    allUsers.value = response.users || []
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  }
}

// 文件上传相关函数
const handleUploadSuccess = (response, file) => {
  if (response && response.file_path) {
    form.attachment_path = response.file_path
    ElMessage.success('附件上传成功')
  } else {
    ElMessage.error('上传失败')
  }
}

const handleUploadError = (error, file) => {
  console.error('上传失败:', error)
  ElMessage.error('附件上传失败')
}

const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('附件大小不能超过10MB')
    return false
  }
  return true
}

const removeAttachment = () => {
  form.attachment_path = ''
}

const getFileName = (path) => {
  return path.split('/').pop()
}

const goBack = () => {
  router.back()
}

// 提交申请
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // 多级审批时校验每级都选了审批人
    if (enableMultiLevelApproval.value) {
      const emptyLevel = approvalLevels.value.find(l => !l.approver_id)
      if (emptyLevel) {
        ElMessage.warning(`请为第${emptyLevel.level}级审批选择审批人`)
        return
      }
    }

    loading.value = true
    try {
      const submitData = { ...form }

      if (enableMultiLevelApproval.value && approvalLevels.value.length > 0) {
        submitData.approval_levels = approvalLevels.value.filter(level => level.approver_id)
        if (submitData.approval_levels.length > 0) {
          submitData.approver_id = submitData.approval_levels[0].approver_id
          submitData.current_approver_level = 1
          submitData.is_multi_level = true
        }
      }

      await apiService.attendance.createLeaveApplication(submitData)
      ElMessage.success('请假申请提交成功')
      router.back()
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '提交失败')
    } finally {
      loading.value = false
    }
  })
}

// 重置表单
const handleReset = () => {
  formRef.value?.resetFields()
  form.days = 1
  enableMultiLevelApproval.value = false
  approvalLevels.value = [
    { level: 1, approver_id: null, status: 'pending' }
  ]
}

onMounted(() => {
  fetchAllUsers()
})
</script>

<style scoped>
@import '@/styles/design-system.css';

.leave-form-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

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
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.form-section {
  margin-bottom: 24px;
}

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

.application-form :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.application-form :deep(.el-card__body) {
  padding: 24px;
}

.form-select {
  width: 100%;
}

.days-hint {
  margin-left: 10px;
  color: #64748b;
  font-size: 12px;
}

.emergency-hint {
  margin-left: 10px;
  color: #64748b;
  font-size: 12px;
}

.approver-hint {
  font-size: 12px;
  color: #64748b;
  margin-top: 5px;
}

.text-center {
  text-align: center;
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 10px 14px;
  background: rgba(241, 245, 249, 0.8);
  border-radius: 10px;
  font-size: 13px;
}

.approval-level-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.level-tag {
  font-weight: 500;
}

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

.btn-text-danger {
  color: #ef4444;
}

.btn-text-danger:hover {
  color: #dc2626;
}

.btn-link-primary {
  color: #7dd3fc;
}

.btn-link-primary:hover {
  color: #38bdf8;
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
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

@media screen and (max-width: 768px) {
  .page-header {
    padding: 20px;
  }
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .header-actions {
    width: 100%;
  }
  .btn-back {
    width: 100%;
  }
  .approval-level-item {
    flex-wrap: wrap;
    gap: 8px;
  }
  .approval-level-item .el-select {
    width: 100% !important;
    margin-left: 0 !important;
  }
}
</style>
