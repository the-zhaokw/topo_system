<template>
  <div class="overtime-application">
    <div class="header">
      <h1>加班申请</h1>
      <div class="header-actions">
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
    </div>

    <el-card class="application-form">
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
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            提交申请
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="history-card" v-if="myApplications.length > 0">
      <template #header>
        <div class="card-header">
          <span>我的加班申请记录</span>
        </div>
      </template>
      <el-table :data="myApplications" stripe>
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
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
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
.overtime-application {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.application-form {
  margin-bottom: 20px;
}

.history-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-center {
  text-align: center;
  line-height: 32px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .overtime-application {
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

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    width: 100%;
  }

  .application-form {
    margin-bottom: 16px;
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

  .el-input__inner,
  .el-textarea__inner {
    font-size: 14px;
  }

  .text-center {
    line-height: 24px;
    padding: 8px 0;
  }

  .history-card {
    margin-top: 16px;
  }

  .card-header {
    font-size: 14px;
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

  .el-dialog__header {
    padding: 12px !important;
  }

  .el-dialog__title {
    font-size: 16px !important;
  }

  .el-dialog__body {
    padding: 12px !important;
    max-height: 60vh !important;
    overflow-y: auto !important;
  }

  .el-dialog__footer {
    padding: 12px !important;
  }
}

@media screen and (max-width: 480px) {
  .overtime-application {
    padding: 8px;
  }

  .header h1 {
    font-size: 16px;
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
