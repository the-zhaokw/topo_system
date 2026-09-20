<template>
  <div class="overtime-form-container">
    <!-- 页面头部 -->
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
            <h1>填写加班申请</h1>
            <p class="subtitle">填写加班信息并提交审批</p>
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

    <!-- 申请表单 -->
    <div class="form-section animate-fade-in-up delay-100">
      <el-card class="glass-card application-form" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Edit /></el-icon>
              加班申请信息
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

          <el-form-item label="转换方式" prop="compensation_type">
            <el-radio-group v-model="form.compensation_type">
              <el-radio value="leave">转调休</el-radio>
              <el-radio value="pay">转加班费</el-radio>
            </el-radio-group>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Timer, Edit, Check, Refresh } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const approverList = ref([])

const form = reactive({
  date: '',
  start_time: '',
  end_time: '',
  reason: '',
  compensation_type: 'leave',
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

const disabledDate = (time) => {
  return time.getTime() > Date.now()
}

const goBack = () => {
  router.back()
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
          compensation_type: form.compensation_type,
          total_hours: parseFloat(calculatedHours.value)
        }
        if (form.approver_id) {
          submitData.approver_id = form.approver_id
        }
        await apiService.attendance.createOvertimeApplication(submitData)
        ElMessage.success('加班申请提交成功')
        router.back()
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
  form.compensation_type = 'leave'
  form.approver_id = ''
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
  fetchApproverList()
})
</script>

<style scoped>
@import '@/styles/design-system.css';

.overtime-form-container {
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

.text-center {
  text-align: center;
  line-height: 32px;
  color: #64748b;
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
</style>
