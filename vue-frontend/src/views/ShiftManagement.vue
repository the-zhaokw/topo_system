<template>
  <div class="shift-management">
    <!-- 页面头部 - 玻璃拟态风格 -->
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
            <h1>排班管理</h1>
            <p class="subtitle">管理班次设置与员工排班安排</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleCreateShift" class="btn-gradient">
            <el-icon><Plus /></el-icon>
            新增班次
          </el-button>
          <el-button @click="handleBatchAssign" class="btn-secondary">
            <el-icon><User /></el-icon>
            批量排班
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
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ shifts.length }}</div>
              <div class="stat-label">班次总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-active">
            <div class="stat-icon-wrapper stat-icon-wrapper-active">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ activeShiftsCount }}</div>
              <div class="stat-label">启用中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-inactive">
            <div class="stat-icon-wrapper stat-icon-wrapper-inactive">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ inactiveShiftsCount }}</div>
              <div class="stat-label">停用中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-today">
            <div class="stat-icon-wrapper stat-icon-wrapper-today">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ todayScheduledCount }}</div>
              <div class="stat-label">今日排班人数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 班次列表 -->
    <div class="content-section animate-fade-in-up delay-200">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><Timer /></el-icon>
              <h3>班次列表</h3>
              <span class="total-count">共 {{ shifts.length }} 个班次</span>
            </div>
          </div>
        </template>

        <el-table :data="shifts" v-loading="loading" stripe class="custom-table" style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" align="center">
            <template #default="{ row }">
              <span class="id-badge">#{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="班次名称" min-width="120">
            <template #default="{ row }">
              <div class="shift-name">{{ row.name }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="start_time" label="上班时间" width="100" align="center">
            <template #default="{ row }">
              <div class="time-display">
                <el-icon><Clock /></el-icon>
                <span>{{ row.start_time }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="end_time" label="下班时间" width="100" align="center">
            <template #default="{ row }">
              <div class="time-display">
                <el-icon><Clock /></el-icon>
                <span>{{ row.end_time }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="flexible_range" label="弹性范围" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="light" type="info">{{ row.flexible_range }}分钟</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="overtime_threshold" label="加班起算" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="light" type="warning">{{ row.overtime_threshold }}分钟</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'" size="small" effect="light" class="status-tag">
                {{ row.is_active ? '启用' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" align="center" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="handleEditShift(row)" class="btn-edit">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDeleteShift(row)" class="btn-delete">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 用户排班表格 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><User /></el-icon>
              <h3>用户排班安排</h3>
              <span class="today-badge" v-if="isToday(scheduleDate)">
                <el-icon><Calendar /></el-icon>
                今天
              </span>
            </div>
            <div class="header-actions">
              <el-date-picker
                v-model="scheduleDate"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                @change="fetchUserSchedules"
                class="date-picker"
                :class="{ 'today-picker': isToday(scheduleDate) }"
              />
            </div>
          </div>
        </template>

        <el-table :data="userSchedules" v-loading="scheduleLoading" stripe class="custom-table" style="width: 100%">
          <el-table-column prop="user.username" label="员工" min-width="120">
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-name">{{ row.user?.username || '未知用户' }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="shift.name" label="班次" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="light" type="primary" class="shift-tag">
                {{ row.shift?.name || '未分配' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="date" label="日期" width="120" align="center">
            <template #default="{ row }">
              <div class="date-display" :class="{ 'today-highlight': isToday(row.date) }">
                {{ formatDate(row.date) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_working_day ? 'success' : 'info'" size="small" effect="light" class="status-tag">
                {{ row.is_working_day ? '工作日' : '休息日' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" align="center" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="handleEditUserSchedule(row)" class="btn-edit">
                <el-icon><Edit /></el-icon>
                调整
              </el-button>
              <el-button size="small" type="danger" @click="handleDeleteUserSchedule(row)" class="btn-delete">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 新增/编辑班次对话框 -->
    <el-dialog v-model="shiftDialogVisible" :title="shiftDialogTitle" width="500px" class="custom-dialog">
      <el-form :model="shiftForm" :rules="shiftRules" ref="shiftFormRef" label-width="120px">
        <el-form-item label="班次名称" prop="name">
          <el-input v-model="shiftForm.name" placeholder="请输入班次名称" />
        </el-form-item>
        <el-form-item label="上班时间" prop="start_time">
          <el-time-picker v-model="shiftForm.start_time" format="HH:mm" value-format="HH:mm" class="time-picker-input" />
        </el-form-item>
        <el-form-item label="下班时间" prop="end_time">
          <el-time-picker v-model="shiftForm.end_time" format="HH:mm" value-format="HH:mm" class="time-picker-input" />
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
        <el-button type="primary" @click="handleSaveShift" class="btn-gradient">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量排班对话框 -->
    <el-dialog v-model="batchDialogVisible" title="批量排班" width="600px" class="custom-dialog">
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
        <el-button type="primary" @click="handleBatchSave" class="btn-gradient">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User, Calendar, Clock, List, CircleCheck, CircleClose, UserFilled, Timer, Edit, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const scheduleLoading = ref(false)
const shifts = ref([])
const userSchedules = ref([])
const users = ref([])
const scheduleDate = ref(new Date().toISOString().split('T')[0])

// 计算统计数据
const activeShiftsCount = computed(() => {
  return shifts.value.filter(s => s.is_active).length
})

const inactiveShiftsCount = computed(() => {
  return shifts.value.filter(s => !s.is_active).length
})

const todayScheduledCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return userSchedules.value.filter(s => s.date === today).length
})

// 判断是否为今天
const isToday = (dateStr) => {
  if (!dateStr) return false
  const today = new Date().toISOString().split('T')[0]
  return dateStr === today
}

// 格式化日期显示
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  return `${month}-${day}`
}

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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.shift-management {
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
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
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

.stat-card-total::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card-active::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-inactive::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-today::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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

.stat-icon-wrapper-active {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-inactive {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-today {
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

.stat-card-active .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-inactive .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-today .stat-value {
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

.glass-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

/* 内容区域 */
.content-section {
  margin-bottom: 24px;
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

.today-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #059669;
  margin-left: 8px;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 600;
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

.shift-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.time-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #475569;
  font-size: 13px;
}

.time-display .el-icon {
  color: #6366f1;
  font-size: 14px;
}

.status-tag {
  font-weight: 500;
  border-radius: 6px;
}

.shift-tag {
  font-weight: 500;
  border-radius: 6px;
}

.user-info {
  line-height: 1.4;
}

.user-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.date-display {
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.today-highlight {
  color: #059669;
  font-weight: 700;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  padding: 4px 10px;
  border-radius: 6px;
  display: inline-block;
}

.btn-edit,
.btn-delete {
  transition: all 0.3s;
}

.btn-edit:hover,
.btn-delete:hover {
  transform: translateY(-2px);
}

/* 日期选择器 */
.date-picker {
  width: 140px;
}

.today-picker :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #059669 inset;
}

.today-picker :deep(.el-input__inner) {
  color: #059669;
  font-weight: 600;
}

/* 对话框样式 */
.custom-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  margin-right: 0;
}

.custom-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.custom-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.time-picker-input {
  width: 100%;
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
  .shift-management {
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
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 8px 12px;
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

  .content-section {
    margin-bottom: 16px;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-actions {
    width: 100%;
  }

  .date-picker {
    width: 100%;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
  }

  .btn-edit,
  .btn-delete {
    padding: 6px 10px;
    font-size: 12px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
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
