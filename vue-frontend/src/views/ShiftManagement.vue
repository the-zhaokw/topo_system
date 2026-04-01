<template>
  <div class="shift-management">
    <div class="header">
      <h1>排班管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="handleCreateShift">
          <el-icon><Plus /></el-icon>
          新增班次
        </el-button>
        <el-button @click="handleBatchAssign">
          <el-icon><User /></el-icon>
          批量排班
        </el-button>
      </div>
    </div>

    <!-- 班次列表 -->
    <el-card class="shift-list">
      <el-table :data="shifts" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="班次名称" />
        <el-table-column prop="start_time" label="上班时间" />
        <el-table-column prop="end_time" label="下班时间" />
        <el-table-column prop="flexible_range" label="弹性范围(分钟)" />
        <el-table-column prop="overtime_threshold" label="加班起算点" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleEditShift(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteShift(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 用户排班表格 -->
    <el-card class="user-shift-list">
      <div class="card-header">
        <h3>用户排班安排</h3>
        <div class="header-actions">
          <el-date-picker
            v-model="scheduleDate"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            @change="fetchUserSchedules"
          />
        </div>
      </div>

      <el-table :data="userSchedules" v-loading="scheduleLoading">
        <el-table-column prop="user.username" label="员工" />
        <el-table-column prop="shift.name" label="班次" />
        <el-table-column prop="date" label="日期" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_working_day ? 'success' : 'info'">
              {{ row.is_working_day ? '工作日' : '休息日' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="handleEditUserSchedule(row)">调整</el-button>
            <el-button size="small" type="danger" @click="handleDeleteUserSchedule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑班次对话框 -->
    <el-dialog v-model="shiftDialogVisible" :title="shiftDialogTitle" width="500px">
      <el-form :model="shiftForm" :rules="shiftRules" ref="shiftFormRef" label-width="120px">
        <el-form-item label="班次名称" prop="name">
          <el-input v-model="shiftForm.name" placeholder="请输入班次名称" />
        </el-form-item>
        <el-form-item label="上班时间" prop="start_time">
          <el-time-picker v-model="shiftForm.start_time" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="下班时间" prop="end_time">
          <el-time-picker v-model="shiftForm.end_time" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="弹性范围(分钟)" prop="flexible_range">
          <el-input-number v-model="shiftForm.flexible_range" :min="0" :max="60" />
        </el-form-item>
        <el-form-item label="加班起算点" prop="overtime_threshold">
          <el-input-number v-model="shiftForm.overtime_threshold" :min="0" :max="480" />
          <span style="margin-left: 10px; color: #909399;">分钟</span>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="shiftForm.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shiftDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveShift">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量排班对话框 -->
    <el-dialog v-model="batchDialogVisible" title="批量排班" width="600px">
      <el-form :model="batchForm" :rules="batchRules" ref="batchFormRef" label-width="100px">
        <el-form-item label="员工列表" prop="user_ids">
          <el-select v-model="batchForm.user_ids" multiple placeholder="选择员工" style="width: 100%">
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="班次" prop="shift_id">
          <el-select v-model="batchForm.shift_id" placeholder="选择班次" style="width: 100%">
            <el-option
              v-for="shift in shifts"
              :key="shift.id"
              :label="shift.name"
              :value="shift.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围" prop="date_range">
          <el-date-picker
            v-model="batchForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="工作日设置" prop="is_working_day">
          <el-radio-group v-model="batchForm.is_working_day">
            <el-radio :label="true">工作日</el-radio>
            <el-radio :label="false">休息日</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatchSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User } from '@element-plus/icons-vue'

const loading = ref(false)
const scheduleLoading = ref(false)
const shifts = ref([])
const userSchedules = ref([])
const users = ref([])
const scheduleDate = ref(new Date().toISOString().split('T')[0])

// 班次对话框
const shiftDialogVisible = ref(false)
const shiftDialogTitle = ref('新增班次')
const shiftFormRef = ref()
const shiftForm = ref({
  name: '',
  start_time: '09:00',
  end_time: '18:00',
  flexible_range: 30,
  overtime_threshold: 60,
  is_active: true
})

const shiftRules = {
  name: [{ required: true, message: '请输入班次名称', trigger: 'blur' }],
  start_time: [{ required: true, message: '请选择上班时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择下班时间', trigger: 'change' }]
}

// 批量排班对话框
const batchDialogVisible = ref(false)
const batchFormRef = ref()
const batchForm = ref({
  user_ids: [],
  shift_id: '',
  date_range: [],
  is_working_day: true
})

const batchRules = {
  user_ids: [{ required: true, message: '请选择员工', trigger: 'change' }],
  shift_id: [{ required: true, message: '请选择班次', trigger: 'change' }],
  date_range: [{ required: true, message: '请选择日期范围', trigger: 'change' }]
}

// 获取班次列表
const fetchShifts = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('/api/attendance/shifts', {
      headers: {
        'Authorization': token ? `Bearer ${token}` : ''
      }
    })
    const data = await response.json()
    
    if (response.ok) {
      shifts.value = data
    } else {
      ElMessage.error(data.message || '获取班次列表失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    loading.value = false
  }
}

// 获取用户列表
const fetchUsers = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('/api/users', {
      headers: {
        'Authorization': token ? `Bearer ${token}` : ''
      }
    })
    const data = await response.json()
    
    if (response.ok) {
      users.value = data
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

// 获取用户排班安排
const fetchUserSchedules = async () => {
  scheduleLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/attendance/user-shifts?date=${scheduleDate.value}`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : ''
      }
    })
    const data = await response.json()
    
    if (response.ok) {
      userSchedules.value = data
    } else {
      ElMessage.error(data.message || '获取排班安排失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  } finally {
    scheduleLoading.value = false
  }
}

// 班次操作
const handleCreateShift = () => {
  shiftDialogTitle.value = '新增班次'
  shiftForm.value = {
    name: '',
    start_time: '09:00',
    end_time: '18:00',
    flexible_range: 30,
    overtime_threshold: 60,
    is_active: true
  }
  shiftDialogVisible.value = true
}

const handleEditShift = (shift) => {
  shiftDialogTitle.value = '编辑班次'
  shiftForm.value = { ...shift }
  shiftDialogVisible.value = true
}

const handleSaveShift = async () => {
  if (!shiftFormRef.value) return
  
  await shiftFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      const token = localStorage.getItem('token')
      const url = shiftForm.value.id ? `/api/attendance/shifts/${shiftForm.value.id}` : '/api/attendance/shifts'
      const method = shiftForm.value.id ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify(shiftForm.value)
      })
      
      const data = await response.json()
      
      if (response.ok) {
        ElMessage.success(shiftForm.value.id ? '更新成功' : '创建成功')
        shiftDialogVisible.value = false
        fetchShifts()
      } else {
        ElMessage.error(data.message || '操作失败')
      }
    } catch (error) {
      ElMessage.error('网络错误')
    }
  })
}

const handleDeleteShift = async (shift) => {
  try {
    await ElMessageBox.confirm('确定删除这个班次吗？', '提示', {
      type: 'warning'
    })
    
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/attendance/shifts/${shift.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': token ? `Bearer ${token}` : ''
      }
    })
    
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success('删除成功')
      fetchShifts()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 批量排班操作
const handleBatchAssign = () => {
  batchForm.value = {
    user_ids: [],
    shift_id: '',
    date_range: [],
    is_working_day: true
  }
  batchDialogVisible.value = true
}

const handleBatchSave = async () => {
  if (!batchFormRef.value) return
  
  await batchFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/attendance/user-shifts/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify(batchForm.value)
      })
      
      const data = await response.json()
      
      if (response.ok) {
        ElMessage.success('批量排班成功')
        batchDialogVisible.value = false
        fetchUserSchedules()
      } else {
        ElMessage.error(data.message || '批量排班失败')
      }
    } catch (error) {
      ElMessage.error('网络错误')
    }
  })
}

// 用户排班操作
const handleEditUserSchedule = (schedule) => {
  // 实现编辑用户排班逻辑
  ElMessage.info('编辑用户排班功能待实现')
}

const handleDeleteUserSchedule = async (schedule) => {
  try {
    await ElMessageBox.confirm('确定删除这个排班安排吗？', '提示', {
      type: 'warning'
    })
    
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/attendance/user-shifts/${schedule.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': token ? `Bearer ${token}` : ''
      }
    })
    
    const data = await response.json()
    
    if (response.ok) {
      ElMessage.success('删除成功')
      fetchUserSchedules()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchShifts()
  fetchUsers()
  fetchUserSchedules()
})
</script>

<style scoped>
.shift-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.shift-list, .user-shift-list {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .shift-management {
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

  .filter-card {
    margin-bottom: 16px;
  }

  .filter-form {
    flex-direction: column;
    gap: 12px;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 8px;
    width: 100%;
  }

  .filter-form .el-input,
  .filter-form .el-select {
    width: 100% !important;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .pagination-container {
    justify-content: center;
    margin-top: 16px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .shift-management {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>