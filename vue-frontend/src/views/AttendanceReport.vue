<template>
  <div class="attendance-report">
    <div class="header">
      <h1>考勤统计报表</h1>
      <div class="header-actions">
        <el-button type="primary" @click="handleExportReport">
          <el-icon><Download /></el-icon>
          导出报表
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <div class="filter-form">
        <el-form :model="filterForm" inline>
          <el-form-item label="统计周期">
            <el-select v-model="filterForm.period" @change="handlePeriodChange">
              <el-option label="日报" value="daily" />
              <el-option label="周报" value="weekly" />
              <el-option label="月报" value="monthly" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>
          <el-form-item label="日期范围" v-if="filterForm.period === 'custom'">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="统计日期" v-else>
            <el-date-picker
              v-model="filterForm.date"
              :type="getDatePickerType"
              :format="getDateFormat"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="部门" v-if="hasManagePermission">
            <el-select v-model="filterForm.department" placeholder="选择部门" clearable>
              <el-option label="技术部" value="tech" />
              <el-option label="产品部" value="product" />
              <el-option label="市场部" value="marketing" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">生成报表</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <!-- 统计概览 -->
    <div class="overview-cards">
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-value" style="color: #67c23a;">{{ overview.totalEmployees }}</div>
          <div class="stat-label">总人数</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-value" style="color: #409eff;">{{ overview.attendanceRate }}%</div>
          <div class="stat-label">出勤率</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-value" style="color: #e6a23c;">{{ overview.lateCount }}</div>
          <div class="stat-label">迟到人次</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-value" style="color: #f56c6c;">{{ overview.absenceCount }}</div>
          <div class="stat-label">缺勤人次</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-item">
          <div class="stat-value" style="color: #909399;">{{ overview.overtimeHours }}</div>
          <div class="stat-label">加班总时长</div>
        </div>
      </el-card>
    </div>

    <!-- 详细统计表格 -->
    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="出勤明细" name="detail">
          <el-table :data="detailData" v-loading="loading">
            <el-table-column prop="user.username" label="员工" />
            <el-table-column prop="date" label="日期" />
            <el-table-column prop="shift.name" label="班次" />
            <el-table-column label="上班打卡">
              <template #default="{ row }">
                <div>{{ row.clock_in_time || '未打卡' }}</div>
                <div :class="getStatusClass(row.clock_in_status)">
                  {{ getStatusText(row.clock_in_status) }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="下班打卡">
              <template #default="{ row }">
                <div>{{ row.clock_out_time || '未打卡' }}</div>
                <div :class="getStatusClass(row.clock_out_status)">
                  {{ getStatusText(row.clock_out_status) }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="work_hours" label="工作时长" />
            <el-table-column prop="overtime_hours" label="加班时长" />
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="异常统计" name="exception">
          <el-table :data="exceptionData" v-loading="loading">
            <el-table-column prop="user.username" label="员工" />
            <el-table-column prop="late_count" label="迟到次数" />
            <el-table-column prop="early_leave_count" label="早退次数" />
            <el-table-column prop="absence_count" label="缺勤天数" />
            <el-table-column prop="overtime_count" label="加班次数" />
            <el-table-column prop="total_exceptions" label="异常总数" />
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="加班统计" name="overtime">
          <el-table :data="overtimeData" v-loading="loading">
            <el-table-column prop="user.username" label="员工" />
            <el-table-column prop="total_overtime" label="总加班时长" />
            <el-table-column prop="weekday_overtime" label="工作日加班" />
            <el-table-column prop="weekend_overtime" label="周末加班" />
            <el-table-column prop="holiday_overtime" label="节假日加班" />
          </el-table>
        </el-tab-pane>
      </el-tabs>

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

    <!-- 图表展示 -->
    <el-card class="chart-card">
      <h3>考勤趋势分析</h3>
      <div class="chart-container">
        <!-- 这里可以集成图表库，如 ECharts -->
        <div class="chart-placeholder">
          <el-empty description="图表展示区域" :image-size="100" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const userStore = useUserStore()
const loading = ref(false)
const activeTab = ref('detail')
const detailData = ref([])
const exceptionData = ref([])
const overtimeData = ref([])

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

// 筛选条件
const filterForm = ref({
  period: 'daily',
  date: new Date().toISOString().split('T')[0],
  dateRange: [],
  department: ''
})

// 统计概览
const overview = ref({
  totalEmployees: 0,
  attendanceRate: 0,
  lateCount: 0,
  absenceCount: 0,
  overtimeHours: 0
})

// 分页
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 计算日期选择器类型
const getDatePickerType = computed(() => {
  const types = {
    daily: 'date',
    weekly: 'week',
    monthly: 'month'
  }
  return types[filterForm.value.period] || 'date'
})

const getDateFormat = computed(() => {
  const formats = {
    daily: 'YYYY-MM-DD',
    weekly: 'YYYY 第 ww 周',
    monthly: 'YYYY-MM'
  }
  return formats[filterForm.value.period] || 'YYYY-MM-DD'
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

// 处理周期变化
const handlePeriodChange = (period) => {
  if (period !== 'custom') {
    const today = new Date()
    switch (period) {
      case 'daily':
        filterForm.value.date = today.toISOString().split('T')[0]
        break
      case 'weekly':
        // 设置为当前周的第一天
        const weekStart = new Date(today.setDate(today.getDate() - today.getDay() + 1))
        filterForm.value.date = weekStart.toISOString().split('T')[0]
        break
      case 'monthly':
        // 设置为当前月的第一天
        const monthStart = new Date(today.getFullYear(), today.getMonth(), 1)
        filterForm.value.date = monthStart.toISOString().split('T')[0]
        break
    }
  }
}

// 获取报表数据
const fetchReportData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.currentPage,
      per_page: pagination.value.pageSize,
      ...filterForm.value
    }
    
    if (filterForm.value.period === 'custom' && filterForm.value.dateRange.length === 2) {
      params.start_date = filterForm.value.dateRange[0]
      params.end_date = filterForm.value.dateRange[1]
    }
    
    const [overviewRes, detailRes, exceptionRes, overtimeRes] = await Promise.all([
      apiService.attendance.getReportsOverview(params),
      apiService.attendance.getReportsDetail(params),
      apiService.attendance.getExceptions(params),
      apiService.attendance.getStatistics(params)
    ])
    
    overview.value = overviewRes || {
      totalEmployees: 0,
      attendanceRate: 0,
      lateCount: 0,
      absenceCount: 0,
      overtimeHours: 0
    }
    
    detailData.value = detailRes?.records || []
    pagination.value.total = detailRes?.total || 0
    
    exceptionData.value = exceptionRes || []
    overtimeData.value = overtimeRes || []
    
  } catch (error) {
    ElMessage.error('获取报表数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.value.currentPage = 1
  fetchReportData()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.value.pageSize = size
  fetchReportData()
}

const handleCurrentChange = (page) => {
  pagination.value.currentPage = page
  fetchReportData()
}

// 导出报表
const handleExportReport = async () => {
  try {
    const params = { ...filterForm.value }
    
    if (filterForm.value.period === 'custom' && filterForm.value.dateRange.length === 2) {
      params.start_date = filterForm.value.dateRange[0]
      params.end_date = filterForm.value.dateRange[1]
    }
    
    const response = await apiService.attendance.exportAttendanceReport(params)
    
    if (response) {
      const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `考勤报表_${new Date().toISOString().split('T')[0]}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    }
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  fetchReportData()
})
</script>

<style scoped>
.attendance-report {
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

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-item {
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.chart-card {
  margin-top: 20px;
}

.chart-container {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
}

.status-normal { color: #67c23a; }
.status-late { color: #e6a23c; }
.status-early-leave { color: #e6a23c; }
.status-missing { color: #f56c6c; }
.status-overtime { color: #409eff; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .attendance-report {
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
  .filter-form .el-select,
  .filter-form .el-date-picker {
    width: 100% !important;
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }

  .stat-card :deep(.el-card__body) {
    padding: 12px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .table-card {
    margin-bottom: 16px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .pagination-wrapper {
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

  .chart-card {
    margin-bottom: 16px;
  }

  .chart-container {
    height: 250px;
  }

  .chart-placeholder {
    font-size: 13px;
  }
}

@media screen and (max-width: 480px) {
  .attendance-report {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .stats-cards {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .stat-value {
    font-size: 18px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .chart-container {
    height: 200px;
  }
}
</style>