<template>
  <div class="attendance-report-container">
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
            <h1>考勤统计报表</h1>
            <p class="subtitle">查看员工考勤数据与统计分析</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleExportReport" class="btn-gradient">
            <el-icon><Download /></el-icon>
            导出报表
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="8" :md="4" :lg="4">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview.totalEmployees }}</div>
              <div class="stat-label">应出勤天数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4" :lg="4">
          <div class="stat-card stat-card-attendance">
            <div class="stat-icon-wrapper stat-icon-wrapper-attendance">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview.attendanceRate }}%</div>
              <div class="stat-label">实际出勤</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4" :lg="4">
          <div class="stat-card stat-card-late">
            <div class="stat-icon-wrapper stat-icon-wrapper-late">
              <el-icon><AlarmClock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview.lateCount }}</div>
              <div class="stat-label">迟到次数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4" :lg="4">
          <div class="stat-card stat-card-early">
            <div class="stat-icon-wrapper stat-icon-wrapper-early">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview.earlyLeaveCount || 0 }}</div>
              <div class="stat-label">早退次数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4" :lg="4">
          <div class="stat-card stat-card-missing">
            <div class="stat-icon-wrapper stat-icon-wrapper-missing">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview.missingCount || 0 }}</div>
              <div class="stat-label">缺卡次数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4" :lg="4">
          <div class="stat-card stat-card-overtime">
            <div class="stat-icon-wrapper stat-icon-wrapper-overtime">
              <el-icon><Moon /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview.overtimeHours }}</div>
              <div class="stat-label">加班时长</div>
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
          <el-form-item label="统计周期">
            <el-select v-model="filterForm.period" @change="handlePeriodChange" class="filter-select">
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
              class="date-picker"
            />
          </el-form-item>
          <el-form-item label="统计日期" v-else>
            <el-date-picker
              v-model="filterForm.date"
              :type="getDatePickerType"
              :format="getDateFormat"
              value-format="YYYY-MM-DD"
              class="filter-select"
            />
          </el-form-item>
          <el-form-item label="部门" v-if="hasManagePermission">
            <el-select v-model="filterForm.department" placeholder="选择部门" clearable class="filter-select">
              <el-option label="技术部" value="tech" />
              <el-option label="产品部" value="product" />
              <el-option label="市场部" value="marketing" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch" class="btn-gradient">
              <el-icon><Search /></el-icon>
              生成报表
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 详细统计表格 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><Document /></el-icon>
              <h3>考勤明细</h3>
              <span class="total-count">共 {{ pagination.total }} 条记录</span>
            </div>
          </div>
        </template>

        <el-tabs v-model="activeTab" class="custom-tabs">
          <el-tab-pane label="出勤明细" name="detail">
            <el-table :data="detailData" v-loading="loading" class="custom-table" stripe>
              <el-table-column prop="user.username" label="员工" min-width="100" />
              <el-table-column prop="date" label="日期" width="110" align="center" />
              <el-table-column prop="shift.name" label="班次" width="100" align="center" />
              <el-table-column label="上班打卡" min-width="120" align="center">
                <template #default="{ row }">
                  <div class="time-cell">
                    <span :class="getTimeClass(row.clock_in_status)">{{ row.clock_in_time || '未打卡' }}</span>
                    <el-tag :type="getStatusType(row.clock_in_status)" size="small" effect="light" class="status-tag">
                      {{ getStatusText(row.clock_in_status) }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="下班打卡" min-width="120" align="center">
                <template #default="{ row }">
                  <div class="time-cell">
                    <span :class="getTimeClass(row.clock_out_status)">{{ row.clock_out_time || '未打卡' }}</span>
                    <el-tag :type="getStatusType(row.clock_out_status)" size="small" effect="light" class="status-tag">
                      {{ getStatusText(row.clock_out_status) }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="work_hours" label="工作时长" width="100" align="center">
                <template #default="{ row }">
                  <span class="hours-value">{{ row.work_hours }}h</span>
                </template>
              </el-table-column>
              <el-table-column prop="overtime_hours" label="加班时长" width="100" align="center">
                <template #default="{ row }">
                  <span class="overtime-value" v-if="row.overtime_hours > 0">+{{ row.overtime_hours }}h</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          
          <el-tab-pane label="异常统计" name="exception">
            <el-table :data="exceptionData" v-loading="loading" class="custom-table" stripe>
              <el-table-column prop="user.username" label="员工" min-width="100" />
              <el-table-column prop="late_count" label="迟到次数" width="100" align="center">
                <template #default="{ row }">
                  <span class="exception-late">{{ row.late_count }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="early_leave_count" label="早退次数" width="100" align="center">
                <template #default="{ row }">
                  <span class="exception-early">{{ row.early_leave_count }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="absence_count" label="缺勤天数" width="100" align="center">
                <template #default="{ row }">
                  <span class="exception-absence">{{ row.absence_count }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="overtime_count" label="加班次数" width="100" align="center">
                <template #default="{ row }">
                  <span class="exception-overtime">{{ row.overtime_count }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="total_exceptions" label="异常总数" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.total_exceptions > 0 ? 'danger' : 'success'" size="small">
                    {{ row.total_exceptions }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          
          <el-tab-pane label="加班统计" name="overtime">
            <el-table :data="overtimeData" v-loading="loading" class="custom-table" stripe>
              <el-table-column prop="user.username" label="员工" min-width="100" />
              <el-table-column prop="total_overtime" label="总加班时长" width="120" align="center">
                <template #default="{ row }">
                  <span class="overtime-total">{{ row.total_overtime }}h</span>
                </template>
              </el-table-column>
              <el-table-column prop="weekday_overtime" label="工作日加班" width="110" align="center">
                <template #default="{ row }">
                  <span class="overtime-weekday">{{ row.weekday_overtime }}h</span>
                </template>
              </el-table-column>
              <el-table-column prop="weekend_overtime" label="周末加班" width="110" align="center">
                <template #default="{ row }">
                  <span class="overtime-weekend">{{ row.weekend_overtime }}h</span>
                </template>
              </el-table-column>
              <el-table-column prop="holiday_overtime" label="节假日加班" width="110" align="center">
                <template #default="{ row }">
                  <span class="overtime-holiday">{{ row.holiday_overtime }}h</span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>

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

    <!-- 图表展示 -->
    <div class="chart-section animate-fade-in-up delay-400">
      <el-card class="glass-card chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><TrendCharts /></el-icon>
              考勤趋势分析
            </span>
          </div>
        </template>
        <div class="chart-container">
          <div class="chart-placeholder">
            <div class="chart-icon">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <p class="chart-text">图表展示区域</p>
            <p class="chart-subtext">考勤数据可视化分析即将上线</p>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Download, Calendar, User, CircleCheck, AlarmClock, Timer, Warning, Moon, Filter, Search, Document, TrendCharts, DataAnalysis } from '@element-plus/icons-vue'
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
  earlyLeaveCount: 0,
  missingCount: 0,
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
const getStatusType = (status) => {
  const types = {
    normal: 'success',
    late: 'warning',
    early_leave: 'warning',
    missing: 'danger',
    overtime: 'primary'
  }
  return types[status] || 'info'
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

const getTimeClass = (status) => {
  const classes = {
    normal: 'time-normal',
    late: 'time-late',
    early_leave: 'time-early',
    missing: 'time-missing',
    overtime: 'time-overtime'
  }
  return classes[status] || 'time-default'
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
      earlyLeaveCount: 0,
      missingCount: 0,
      overtimeHours: 0
    }
    
    detailData.value = detailRes?.records || []
    pagination.value.total = detailRes?.total || 0
    
    exceptionData.value = exceptionRes?.records || []
    overtimeData.value = overtimeRes?.records || overtimeRes || []
    
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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.attendance-report-container {
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
  margin-bottom: 16px;
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

/* 6种不同的渐变配色 - 底部渐变条 */
.stat-card-total::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card-attendance::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-late::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-early::before { background: linear-gradient(90deg, #ec4899, #f472b6); }
.stat-card-missing::before { background: linear-gradient(90deg, #ef4444, #f87171); }
.stat-card-overtime::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }

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

/* 6种不同的渐变配色 - 图标背景 */
.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #667eea;
  box-shadow: 0 4px 15px -3px rgba(102, 126, 234, 0.4);
}

.stat-icon-wrapper-attendance {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-late {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-early {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
}

.stat-icon-wrapper-missing {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 15px -3px rgba(239, 68, 68, 0.4);
}

.stat-icon-wrapper-overtime {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
  box-shadow: 0 4px 15px -3px rgba(59, 130, 246, 0.4);
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

/* 6种不同的渐变配色 - 数值文字 */
.stat-card-total .stat-value {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-attendance .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-late .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-early .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-missing .stat-value {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-overtime .stat-value {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
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

.filter-select {
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

/* 自定义标签页 */
.custom-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.custom-tabs :deep(.el-tabs__nav-wrap::after) {
  background: rgba(226, 232, 240, 0.6);
}

.custom-tabs :deep(.el-tabs__item) {
  font-weight: 500;
  color: #64748b;
}

.custom-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
}

.custom-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #667eea, #764ba2);
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

/* 时间单元格 */
.time-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.time-cell span {
  font-size: 13px;
  font-weight: 500;
}

.time-normal { color: #059669; }
.time-late { color: #d97706; }
.time-early { color: #db2777; }
.time-missing { color: #dc2626; }
.time-overtime { color: #2563eb; }
.time-default { color: #64748b; }

.status-tag {
  font-weight: 500;
  border-radius: 6px;
}

.hours-value {
  color: #1e293b;
  font-weight: 600;
}

.overtime-value {
  color: #2563eb;
  font-weight: 600;
}

/* 异常统计 */
.exception-late {
  color: #d97706;
  font-weight: 600;
}

.exception-early {
  color: #db2777;
  font-weight: 600;
}

.exception-absence {
  color: #dc2626;
  font-weight: 600;
}

.exception-overtime {
  color: #2563eb;
  font-weight: 600;
}

/* 加班统计 */
.overtime-total {
  color: #667eea;
  font-weight: 700;
  font-size: 15px;
}

.overtime-weekday {
  color: #059669;
  font-weight: 600;
}

.overtime-weekend {
  color: #d97706;
  font-weight: 600;
}

.overtime-holiday {
  color: #dc2626;
  font-weight: 600;
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 图表区域 */
.chart-section {
  margin-bottom: 24px;
}

.chart-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.chart-container {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  padding: 40px;
}

.chart-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
}

.chart-icon .el-icon {
  font-size: 40px;
  color: #667eea;
}

.chart-text {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.chart-subtext {
  font-size: 14px;
  color: #64748b;
  margin: 0;
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
.delay-400 { animation-delay: 400ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .attendance-report-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
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
    flex-direction: column;
    gap: 8px;
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
  .date-picker {
    width: 100% !important;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .custom-tabs :deep(.el-tabs__item) {
    font-size: 13px;
    padding: 0 12px;
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

  .chart-container {
    height: 280px;
  }

  .chart-icon {
    width: 60px;
    height: 60px;
    border-radius: 18px;
  }

  .chart-icon .el-icon {
    font-size: 30px;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
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

  .chart-container {
    height: 240px;
  }
}
</style>
