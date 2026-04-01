<template>
  <div class="attendance-list">
    <div class="header">
      <h1>考勤记录管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="handlePunch" v-if="hasPunchPermission">
          <el-icon><Clock /></el-icon>
          打卡
        </el-button>
        <el-button @click="handleExport" v-if="hasManagePermission">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <div class="filter-form">
        <el-form :model="filterForm" inline>
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="员工" v-if="hasManagePermission">
            <el-select v-model="filterForm.userId" placeholder="选择员工" clearable>
              <el-option
                v-for="user in users"
                :key="user.id"
                :label="user.username"
                :value="user.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="选择状态" clearable>
              <el-option label="正常" value="normal" />
              <el-option label="迟到" value="late" />
              <el-option label="早退" value="early_leave" />
              <el-option label="缺卡" value="missing" />
              <el-option label="加班" value="overtime" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <!-- 考勤记录表格 -->
    <el-card>
      <el-table :data="attendanceRecords" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user.username" label="员工" />
        <el-table-column prop="date" label="日期" />
        <el-table-column prop="shift.name" label="班次" />
        <el-table-column label="上班打卡">
          <template #default="{ row }">
            <div>{{ row.clock_in_time || '未打卡' }}</div>
            <div v-if="row.clock_in_ip" style="font-size: 12px; color: #999;">IP: {{ row.clock_in_ip }}</div>
            <div v-if="row.late_minutes > 0" style="color: #e6a23c;">迟到 {{ row.late_minutes }} 分钟</div>
            <div v-else-if="row.clock_in_time" style="color: #67c23a;">正常</div>
          </template>
        </el-table-column>
        <el-table-column label="下班打卡">
          <template #default="{ row }">
            <div>{{ row.clock_out_time || '未打卡' }}</div>
            <div v-if="row.clock_out_ip" style="font-size: 12px; color: #999;">IP: {{ row.clock_out_ip }}</div>
            <div v-if="row.early_leave_minutes > 0" style="color: #e6a23c;">早退 {{ row.early_leave_minutes }} 分钟</div>
          </template>
        </el-table-column>
        <el-table-column prop="work_hours" label="工作时长">
          <template #default="{ row }">
            {{ row.work_hours ? row.work_hours.toFixed(2) + ' 小时' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="overtime_hours" label="加班时长">
          <template #default="{ row }">
            {{ row.overtime_hours ? row.overtime_hours.toFixed(2) + ' 小时' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" v-if="hasManagePermission">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
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

    <!-- 打卡对话框 -->
    <el-dialog v-model="punchDialogVisible" title="打卡" width="400px">
      <div class="punch-dialog">
        <div class="current-time">{{ currentTime }}</div>
        <div class="punch-buttons">
          <el-button type="primary" size="large" @click="handleClockIn" :disabled="hasClockedIn">
            上班打卡
          </el-button>
          <el-button type="success" size="large" @click="handleClockOut" :disabled="!hasClockedIn || hasClockedOut">
            下班打卡
          </el-button>
        </div>
        <div class="today-record" v-if="todayRecord">
          <h4>今日打卡记录</h4>
          <p>上班时间: {{ todayRecord.clock_in_time || '未打卡' }}</p>
          <p>下班时间: {{ todayRecord.clock_out_time || '未打卡' }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, Download } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const userStore = useUserStore()
const loading = ref(false)
const attendanceRecords = ref([])
const users = ref([])
const todayRecord = ref(null)
const punchDialogVisible = ref(false)
const currentTime = ref('')

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

// 状态样式
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
.attendance-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.punch-dialog {
  text-align: center;
}

.current-time {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #409eff;
}

.punch-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 20px;
}

.today-record {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.status-normal { color: #67c23a; }
.status-late { color: #e6a23c; }
.status-early-leave { color: #e6a23c; }
.status-missing { color: #f56c6c; }
.status-overtime { color: #409eff; }

@media screen and (max-width: 768px) {
  .attendance-list {
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
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    max-width: calc(50% - 4px);
    font-size: 12px;
    padding: 8px 12px;
  }

  .filter-card {
    margin-bottom: 16px;
  }

  .filter-form .el-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .filter-form .el-form-item {
    margin-bottom: 0;
    width: 100%;
  }

  .filter-form .el-select,
  .filter-form .el-date-editor {
    width: 100% !important;
  }

  .pagination {
    margin-top: 16px;
    text-align: center;
  }

  .punch-buttons {
    flex-direction: column;
    gap: 12px;
  }

  .current-time {
    font-size: 20px;
  }
}

@media screen and (max-width: 480px) {
  .attendance-list {
    padding: 8px;
  }

  .header h1 {
    font-size: 16px;
  }

  .header-actions .el-button {
    max-width: 100%;
    flex: none;
    width: 100%;
  }
}
</style>