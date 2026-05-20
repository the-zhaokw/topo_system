<template>
  <div class="attendance-list-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Clock /></el-icon>
          </div>
          <div class="title-text">
            <h1>考勤记录管理</h1>
            <p class="subtitle">管理员工考勤打卡记录与统计</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handlePunch" v-if="hasPunchPermission" class="btn-gradient">
            <el-icon><Timer /></el-icon>
            打卡
          </el-button>
          <el-button @click="handleExport" v-if="hasManagePermission" class="btn-secondary">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-attendance">
            <div class="stat-icon-wrapper stat-icon-wrapper-attendance">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ monthlyStats.attendanceDays }}</div>
              <div class="stat-label">本月出勤天数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-late">
            <div class="stat-icon-wrapper stat-icon-wrapper-late">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ monthlyStats.lateCount }}</div>
              <div class="stat-label">迟到次数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-early">
            <div class="stat-icon-wrapper stat-icon-wrapper-early">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ monthlyStats.earlyLeaveCount }}</div>
              <div class="stat-label">早退次数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-missing">
            <div class="stat-icon-wrapper stat-icon-wrapper-missing">
              <el-icon><QuestionFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ monthlyStats.missingCount }}</div>
              <div class="stat-label">缺卡次数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选条件 -->
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
        <el-form :model="filterForm" inline class="filter-form">
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              class="date-picker"
            />
          </el-form-item>
          <el-form-item label="员工" v-if="hasManagePermission">
            <el-select v-model="filterForm.userId" placeholder="选择员工" clearable class="filter-select">
              <el-option
                v-for="user in users"
                :key="user.id"
                :label="user.username"
                :value="user.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="选择状态" clearable class="filter-select">
              <el-option label="正常" value="normal" />
              <el-option label="迟到" value="late" />
              <el-option label="早退" value="early_leave" />
              <el-option label="缺卡" value="missing" />
              <el-option label="加班" value="overtime" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch" class="btn-gradient">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="handleReset" class="btn-secondary">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 考勤记录表格 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><Document /></el-icon>
              <h3>考勤记录列表</h3>
              <span class="total-count">共 {{ pagination.total }} 条记录</span>
            </div>
          </div>
        </template>

        <el-table :data="attendanceRecords" v-loading="loading" stripe class="custom-table" style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="user.username" label="员工" min-width="100">
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-name">{{ row.user?.username || '未知用户' }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="date" label="日期" width="110" align="center">
            <template #default="{ row }">
              <span class="date-text">{{ row.date }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="shift.name" label="班次" width="90" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="light" class="shift-tag">{{ row.shift?.name || '-' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="上班打卡" min-width="140">
            <template #default="{ row }">
              <div class="clock-info">
                <div class="clock-time" :class="{ 'text-missing': !row.clock_in_time }">
                  {{ row.clock_in_time || '未打卡' }}
                </div>
                <div v-if="row.clock_in_ip" class="clock-ip">IP: {{ row.clock_in_ip }}</div>
                <div v-if="row.late_minutes > 0" class="status-late">
                  <el-icon><Warning /></el-icon> 迟到 {{ row.late_minutes }} 分钟
                </div>
                <div v-else-if="row.clock_in_time" class="status-normal">
                  <el-icon><CircleCheck /></el-icon> 正常
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="下班打卡" min-width="140">
            <template #default="{ row }">
              <div class="clock-info">
                <div class="clock-time" :class="{ 'text-missing': !row.clock_out_time }">
                  {{ row.clock_out_time || '未打卡' }}
                </div>
                <div v-if="row.clock_out_ip" class="clock-ip">IP: {{ row.clock_out_ip }}</div>
                <div v-if="row.early_leave_minutes > 0" class="status-early">
                  <el-icon><CircleClose /></el-icon> 早退 {{ row.early_leave_minutes }} 分钟
                </div>
                <div v-else-if="row.clock_out_time && !row.early_leave_minutes" class="status-normal">
                  <el-icon><CircleCheck /></el-icon> 正常
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="work_hours" label="工作时长" width="100" align="center">
            <template #default="{ row }">
              <span class="hours-badge" :class="{ 'hours-normal': row.work_hours >= 8 }">
                {{ row.work_hours ? row.work_hours.toFixed(2) + 'h' : '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="overtime_hours" label="加班时长" width="100" align="center">
            <template #default="{ row }">
              <span class="overtime-badge" v-if="row.overtime_hours && row.overtime_hours > 0">
                +{{ row.overtime_hours.toFixed(2) }}h
              </span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center" fixed="right" v-if="hasManagePermission">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEdit(row)" class="action-btn">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)" class="action-btn">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-section">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 打卡对话框 -->
    <el-dialog v-model="punchDialogVisible" title="打卡" width="400px" class="punch-dialog-wrapper">
      <div class="punch-dialog">
        <div class="current-time">{{ currentTime }}</div>
        <div class="punch-buttons">
          <el-button type="primary" size="large" @click="handleClockIn" :disabled="hasClockedIn" class="btn-clock-in">
            <el-icon><Sunrise /></el-icon>
            上班打卡
          </el-button>
          <el-button type="success" size="large" @click="handleClockOut" :disabled="!hasClockedIn || hasClockedOut" class="btn-clock-out">
            <el-icon><Sunset /></el-icon>
            下班打卡
          </el-button>
        </div>
        <div class="today-record" v-if="todayRecord">
          <h4>今日打卡记录</h4>
          <div class="record-item">
            <span class="record-label">上班时间:</span>
            <span class="record-value" :class="{ 'text-success': todayRecord.clock_in_time }">
              {{ todayRecord.clock_in_time || '未打卡' }}
            </span>
          </div>
          <div class="record-item">
            <span class="record-label">下班时间:</span>
            <span class="record-value" :class="{ 'text-success': todayRecord.clock_out_time }">
              {{ todayRecord.clock_out_time || '未打卡' }}
            </span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, Download, Timer, Filter, Search, Refresh, Document, Edit, Delete, Warning, CircleClose, QuestionFilled, Calendar, CircleCheck, Sunrise, Sunset } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const userStore = useUserStore()
const loading = ref(false)
const attendanceRecords = ref([])
const users = ref([])
const todayRecord = ref(null)
const punchDialogVisible = ref(false)
const currentTime = ref('')

// 月度统计数据
const monthlyStats = ref({
  attendanceDays: 0,
  lateCount: 0,
  earlyLeaveCount: 0,
  missingCount: 0
})

// 权限检查
const hasPunchPermission = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  return user.position !== '访客'
})

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

// 筛选条件
const filterForm = ref({
  dateRange: [],
  userId: '',
  status: ''
})

// 分页
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 计算月度统计
const calculateMonthlyStats = () => {
  const records = attendanceRecords.value
  const now = new Date()
  const currentMonth = now.getMonth()
  const currentYear = now.getFullYear()
  
  // 过滤本月记录
  const monthlyRecords = records.filter(record => {
    const recordDate = new Date(record.date)
    return recordDate.getMonth() === currentMonth && recordDate.getFullYear() === currentYear
  })
  
  monthlyStats.value = {
    attendanceDays: monthlyRecords.filter(r => r.clock_in_time || r.clock_out_time).length,
    lateCount: monthlyRecords.filter(r => r.late_minutes > 0).length,
    earlyLeaveCount: monthlyRecords.filter(r => r.early_leave_minutes > 0).length,
    missingCount: monthlyRecords.filter(r => !r.clock_in_time || !r.clock_out_time).length
  }
}

// 获取考勤记录
const fetchAttendanceRecords = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.currentPage,
      per_page: pagination.value.pageSize
    }
    
    if (filterForm.value.dateRange && filterForm.value.dateRange.length === 2) {
      params.start_date = filterForm.value.dateRange[0]
      params.end_date = filterForm.value.dateRange[1]
    }
    if (filterForm.value.userId) {
      params.user_id = filterForm.value.userId
    }
    if (filterForm.value.status) {
      params.status = filterForm.value.status
    }
    
    const data = await apiService.attendance.getAttendanceRecords(params)
    attendanceRecords.value = data.records || data || []
    pagination.value.total = data.total || data.length || 0
    
    // 计算月度统计
    calculateMonthlyStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取考勤记录失败')
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
      users.value = data.users || data || []
    } else {
      console.error('获取用户列表失败:', data.message || '未知错误')
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

// 获取今日打卡记录
const fetchTodayRecord = async () => {
  try {
    const data = await apiService.attendance.getTodayRecord()
    todayRecord.value = data
  } catch (error) {
    console.error('获取今日记录失败:', error)
    todayRecord.value = null
  }
}

// 打卡相关
const hasClockedIn = computed(() => {
  return todayRecord.value && todayRecord.value.clock_in_time
})

const hasClockedOut = computed(() => {
  return todayRecord.value && todayRecord.value.clock_out_time
})

let punchTimer = null

const handlePunch = async () => {
  punchDialogVisible.value = true
  updateCurrentTime()
  if (punchTimer) clearInterval(punchTimer)
  punchTimer = setInterval(updateCurrentTime, 1000)
  await fetchTodayRecord()
}

onBeforeUnmount(() => {
  if (punchTimer) {
    clearInterval(punchTimer)
    punchTimer = null
  }
})

const updateCurrentTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}

const getLocation = () => {
  return new Promise((resolve) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve(`${position.coords.latitude.toFixed(6)}, ${position.coords.longitude.toFixed(6)}`)
        },
        () => {
          resolve('定位失败')
        },
        { enableHighAccuracy: true, timeout: 5000 }
      )
    } else {
      resolve('不支持定位')
    }
  })
}

const handleClockIn = async () => {
  try {
    const location = await getLocation()
    await apiService.attendance.clockIn({
      timestamp: new Date().toISOString(),
      location: location,
      device: 'Web'
    })
    ElMessage.success('上班打卡成功')
    punchDialogVisible.value = false
    await fetchTodayRecord()
    await fetchAttendanceRecords()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || error.response?.data?.message || '打卡失败')
  }
}

const handleClockOut = async () => {
  try {
    const location = await getLocation()
    await apiService.attendance.clockOut({
      timestamp: new Date().toISOString(),
      location: location,
      device: 'Web'
    })
    ElMessage.success('下班打卡成功')
    punchDialogVisible.value = false
    await fetchTodayRecord()
    await fetchAttendanceRecords()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || error.response?.data?.message || '打卡失败')
  }
}

// 其他操作
const handleSearch = () => {
  pagination.value.currentPage = 1
  fetchAttendanceRecords()
}

const handleReset = () => {
  filterForm.value = {
    dateRange: [],
    userId: '',
    status: ''
  }
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.value.pageSize = size
  fetchAttendanceRecords()
}

const handleCurrentChange = (page) => {
  pagination.value.currentPage = page
  fetchAttendanceRecords()
}

const handleEdit = (record) => {
  // 跳转到编辑页面
  window.location.href = `/attendance/${record.id}`
}

const handleDelete = async (record) => {
  try {
    await ElMessageBox.confirm('确定删除这条考勤记录吗？', '提示', {
      type: 'warning'
    })

    await apiService.attendance.deleteRecord(record.id)
    ElMessage.success('删除成功')
    fetchAttendanceRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || error.response?.data?.message || '删除失败')
    }
  }
}

const handleExport = async () => {
  try {
    const params = { ...filterForm.value }
    
    if (filterForm.value.dateRange && filterForm.value.dateRange.length === 2) {
      params.start_date = filterForm.value.dateRange[0]
      params.end_date = filterForm.value.dateRange[1]
    }
    
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/attendance/records/export?${new URLSearchParams(params)}`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : ''
      }
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `考勤记录_${new Date().toISOString().split('T')[0]}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } else {
      const data = await response.json()
      ElMessage.error(data.message || '导出失败')
    }
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  fetchAttendanceRecords()
  fetchUsers()
  fetchTodayRecord()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.attendance-list-container {
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

/* 统计卡片不同配色 */
.stat-card-attendance::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card-late::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-early::before { background: linear-gradient(90deg, #ef4444, #f87171); }
.stat-card-missing::before { background: linear-gradient(90deg, #6b7280, #9ca3af); }

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

.stat-icon-wrapper-attendance {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #667eea;
  box-shadow: 0 4px 15px -3px rgba(102, 126, 234, 0.4);
}

.stat-icon-wrapper-late {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-early {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 15px -3px rgba(239, 68, 68, 0.4);
}

.stat-icon-wrapper-missing {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #4b5563;
  box-shadow: 0 4px 15px -3px rgba(107, 114, 128, 0.4);
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

.stat-card-attendance .stat-value {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-late .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-early .stat-value {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-missing .stat-value {
  background: linear-gradient(135deg, #6b7280 0%, #9ca3af 100%);
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

.filter-form {
  padding: 10px 0;
}

.filter-select,
.filter-input {
  width: 160px;
}

.date-picker {
  width: 260px;
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

.date-text {
  font-weight: 500;
  color: #475569;
}

.shift-tag {
  font-weight: 500;
  border-radius: 6px;
}

.clock-info {
  line-height: 1.5;
}

.clock-time {
  font-weight: 500;
  color: #1e293b;
  font-size: 13px;
}

.clock-time.text-missing {
  color: #9ca3af;
  font-style: italic;
}

.clock-ip {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.status-normal {
  font-size: 12px;
  color: #10b981;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.status-late {
  font-size: 12px;
  color: #f59e0b;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.status-early {
  font-size: 12px;
  color: #ef4444;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.hours-badge {
  font-weight: 600;
  color: #64748b;
  font-size: 13px;
}

.hours-badge.hours-normal {
  color: #10b981;
}

.overtime-badge {
  font-weight: 600;
  color: #f59e0b;
  font-size: 13px;
}

.text-muted {
  color: #9ca3af;
}

.action-btn {
  opacity: 0;
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) .action-btn {
  opacity: 1;
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 打卡对话框 */
.punch-dialog-wrapper :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  margin-right: 0;
}

.punch-dialog-wrapper :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.punch-dialog-wrapper :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.punch-dialog {
  text-align: center;
  padding: 10px 0;
}

.current-time {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: 'Monaco', 'Menlo', monospace;
}

.punch-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 24px;
}

.btn-clock-in,
.btn-clock-out {
  flex: 1;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s;
}

.btn-clock-in {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-clock-out {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  border: none;
}

.btn-clock-in:not(:disabled):hover,
.btn-clock-out:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
}

.today-record {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.today-record h4 {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 15px;
  font-weight: 600;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.record-item:last-child {
  border-bottom: none;
}

.record-label {
  color: #64748b;
  font-size: 14px;
}

.record-value {
  font-weight: 600;
  color: #9ca3af;
  font-size: 14px;
}

.record-value.text-success {
  color: #10b981;
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
  .attendance-list-container {
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

  .filter-form {
    flex-direction: column;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 12px;
    width: 100%;
  }

  .filter-select,
  .filter-input,
  .date-picker {
    width: 100% !important;
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

  .punch-buttons {
    flex-direction: column;
    gap: 12px;
  }

  .current-time {
    font-size: 22px;
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
