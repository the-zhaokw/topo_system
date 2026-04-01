<template>
  <div class="attendance-detail">
    <div class="header">
      <h1>考勤记录详情</h1>
      <div class="header-actions">
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-button type="primary" @click="handleEdit" v-if="hasManagePermission">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
      </div>
    </div>

    <!-- 基本信息 -->
    <el-card class="basic-info">
      <div class="info-grid">
        <div class="info-item">
          <label>员工姓名：</label>
          <span>{{ record.user?.username || '未知' }}</span>
        </div>
        <div class="info-item">
          <label>日期：</label>
          <span>{{ record.date }}</span>
        </div>
        <div class="info-item">
          <label>班次：</label>
          <span>{{ record.shift?.name || '未排班' }}</span>
        </div>
        <div class="info-item">
          <label>工作日类型：</label>
          <el-tag :type="record.is_working_day ? 'success' : 'info'">
            {{ record.is_working_day ? '工作日' : '休息日' }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 打卡信息 -->
    <el-card class="punch-info">
      <h3>打卡信息</h3>
      <div class="punch-grid">
        <div class="punch-item">
          <div class="punch-label">上班打卡</div>
          <div class="punch-time">{{ record.clock_in_time || '未打卡' }}</div>
          <div :class="getStatusClass(record.clock_in_status)">
            {{ getStatusText(record.clock_in_status) }}
          </div>
        </div>
        <div class="punch-item">
          <div class="punch-label">下班打卡</div>
          <div class="punch-time">{{ record.clock_out_time || '未打卡' }}</div>
          <div :class="getStatusClass(record.clock_out_status)">
            {{ getStatusText(record.clock_out_status) }}
          </div>
        </div>
      </div>
    </el-card>

    <!-- 工作时长统计 -->
    <el-card class="time-stats">
      <h3>工作时长统计</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-label">标准工作时长</div>
          <div class="stat-value">{{ record.standard_hours || 0 }} 小时</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">实际工作时长</div>
          <div class="stat-value">{{ record.work_hours || 0 }} 小时</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">加班时长</div>
          <div class="stat-value" style="color: #409eff;">{{ record.overtime_hours || 0 }} 小时</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">缺勤时长</div>
          <div class="stat-value" style="color: #f56c6c;">{{ record.absence_hours || 0 }} 小时</div>
        </div>
      </div>
    </el-card>

    <!-- 异常处理记录 -->
    <el-card class="exception-records" v-if="record.exceptions && record.exceptions.length > 0">
      <h3>异常处理记录</h3>
      <el-table :data="record.exceptions">
        <el-table-column prop="type" label="异常类型">
          <template #default="{ row }">
            <el-tag :type="getExceptionTypeClass(row.type)">
              {{ getExceptionTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="原因说明" />
        <el-table-column prop="status" label="处理状态">
          <template #default="{ row }">
            <el-tag :type="getExceptionStatusClass(row.status)">
              {{ getExceptionStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="handler" label="处理人" />
        <el-table-column prop="handled_at" label="处理时间" />
      </el-table>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑考勤记录" width="500px">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="上班时间" prop="clock_in_time">
          <el-time-picker 
            v-model="editForm.clock_in_time" 
            format="HH:mm" 
            value-format="HH:mm"
            placeholder="选择上班时间"
          />
        </el-form-item>
        <el-form-item label="下班时间" prop="clock_out_time">
          <el-time-picker 
            v-model="editForm.clock_out_time" 
            format="HH:mm" 
            value-format="HH:mm"
            placeholder="选择下班时间"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input 
            v-model="editForm.notes" 
            type="textarea" 
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const record = ref({})
const loading = ref(false)

// 权限检查
const hasManagePermission = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  const position = user.position
  return position === '管理员' ||
         position?.includes('经理') ||
         position === '项目经理' ||
         position === '人事'
})

// 编辑对话框
const editDialogVisible = ref(false)
const editFormRef = ref()
const editForm = ref({
  clock_in_time: '',
  clock_out_time: '',
  notes: ''
})

const editRules = {
  clock_in_time: [{ required: true, message: '请选择上班时间', trigger: 'change' }],
  clock_out_time: [{ required: true, message: '请选择下班时间', trigger: 'change' }]
}

// 获取考勤记录详情
const fetchAttendanceDetail = async () => {
  loading.value = true
  try {
    const recordId = route.params.id
    const response = await fetch(`/api/attendance/records/${recordId}`)
    const data = await response.json()
    
    if (response.ok) {
      record.value = data
    } else {
      ElMessage.error(data.message || '获取考勤记录失败')
      router.back()
    }
  } catch (error) {
    ElMessage.error('网络错误')
    router.back()
  } finally {
    loading.value = false
  }
}

// 状态样式和文本
const getStatusClass = (status) => {
  const classes = {
    normal: 'status-normal',
    late: 'status-late',
    early_leave: 'status-early-leave',
    missing: 'status-missing',
    overtime: 'status-overtime'
  }
  return classes[status] || ''
}

const getStatusText = (status) => {
  const texts = {
    normal: '正常',
    late: '迟到',
    early_leave: '早退',
    missing: '缺卡',
    overtime: '加班'
  }
  return texts[status] || status
}

// 异常类型样式和文本
const getExceptionTypeClass = (type) => {
  const classes = {
    late: 'warning',
    early_leave: 'warning',
    absence: 'danger',
    overtime: 'info'
  }
  return classes[type] || ''
}

const getExceptionTypeText = (type) => {
  const texts = {
    late: '迟到',
    early_leave: '早退',
    absence: '缺勤',
    overtime: '加班'
  }
  return texts[type] || type
}

const getExceptionStatusClass = (status) => {
  const classes = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return classes[status] || ''
}

const getExceptionStatusText = (status) => {
  const texts = {
    pending: '待处理',
    approved: '已批准',
    rejected: '已拒绝'
  }
  return texts[status] || status
}

// 编辑操作
const handleEdit = () => {
  editForm.value = {
    clock_in_time: record.value.clock_in_time || '',
    clock_out_time: record.value.clock_out_time || '',
    notes: record.value.notes || ''
  }
  editDialogVisible.value = true
}

const handleSaveEdit = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      const response = await fetch(`/api/attendance/records/${record.value.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(editForm.value)
      })
      
      const data = await response.json()
      
      if (response.ok) {
        ElMessage.success('更新成功')
        editDialogVisible.value = false
        fetchAttendanceDetail()
      } else {
        ElMessage.error(data.message || '更新失败')
      }
    } catch (error) {
      ElMessage.error('网络错误')
    }
  })
}

onMounted(() => {
  fetchAttendanceDetail()
})
</script>

<style scoped>
.attendance-detail {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.basic-info, .punch-info, .time-stats, .exception-records {
  margin-bottom: 20px;
}

.info-grid, .punch-grid, .stats-grid {
  display: grid;
  gap: 20px;
}

.info-grid {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.punch-grid {
  grid-template-columns: repeat(2, 1fr);
}

.stats-grid {
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-item label {
  font-weight: bold;
  color: #606266;
  min-width: 100px;
}

.punch-item {
  text-align: center;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.punch-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.punch-time {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-item {
  text-align: center;
  padding: 15px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.status-normal { color: #67c23a; }
.status-late { color: #e6a23c; }
.status-early-leave { color: #e6a23c; }
.status-missing { color: #f56c6c; }
.status-overtime { color: #409eff; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .attendance-detail {
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

  .info-card,
  .records-card,
  .stats-card,
  .abnormal-card {
    margin-bottom: 16px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .info-item {
    padding: 10px;
  }

  .info-label {
    font-size: 12px;
  }

  .info-value {
    font-size: 14px;
  }

  .records-timeline {
    padding: 12px;
  }

  .timeline-item {
    padding: 12px;
  }

  .time-display {
    font-size: 14px;
  }

  .location-display {
    font-size: 12px;
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

  .abnormal-list {
    padding: 12px;
  }

  .abnormal-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px;
  }

  .abnormal-info {
    width: 100%;
  }

  .abnormal-title {
    font-size: 13px;
  }

  .abnormal-desc {
    font-size: 12px;
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
}

@media screen and (max-width: 480px) {
  .attendance-detail {
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

  .time-display {
    font-size: 13px;
  }

  .location-display {
    font-size: 11px;
  }
}
</style>