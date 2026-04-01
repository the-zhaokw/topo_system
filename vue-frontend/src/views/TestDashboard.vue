<template>
  <div class="test-dashboard">
    <div class="dashboard-header">
      <h2>测试仪表盘</h2>
      <div class="header-actions">
        <el-select v-model="selectedProjectId" placeholder="选择项目" clearable @change="handleProjectChange" style="width: 200px;">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
        <el-button @click="loadDashboard">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div v-loading="loading" v-if="selectedProjectId && dashboardData" class="dashboard-content">
      <el-row :gutter="16" class="overview-row">
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <div class="overview-icon suites">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ dashboardData.overview?.total_suites || 0 }}</div>
              <div class="overview-label">测试集总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <div class="overview-icon cases">
              <el-icon><Document /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ dashboardData.overview?.total_cases || 0 }}</div>
              <div class="overview-label">用例总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <div class="overview-icon executions">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ dashboardData.overview?.in_progress_executions || 0 }}</div>
              <div class="overview-label">进行中执行</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <div class="overview-icon coverage">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ dashboardData.overview?.coverage_rate || 0 }}%</div>
              <div class="overview-label">需求覆盖率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>用例状态分布</span>
            </template>
            <div ref="statusChartRef" style="width: 100%; height: 300px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>用例优先级分布</span>
            </template>
            <div ref="priorityChartRef" style="width: 100%; height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top: 20px;">
        <el-col :span="16">
          <el-card class="table-card">
            <template #header>
              <span>最近执行记录</span>
            </template>
            <el-table :data="dashboardData.recent_pass_rates" stripe style="width: 100%;">
              <el-table-column prop="name" label="执行名称" min-width="150" show-overflow-tooltip />
              <el-table-column prop="pass_rate" label="通过率" width="100">
                <template #default="{ row }">
                  <el-progress :percentage="row.pass_rate" :color="getProgressColor(row.pass_rate)" />
                </template>
              </el-table-column>
              <el-table-column prop="completed_at" label="完成时间" width="160">
                <template #default="{ row }">
                  {{ formatDate(row.completed_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="todo-card">
            <template #header>
              <span>我的待办</span>
            </template>
            <div class="todo-item">
              <span class="todo-label">待设计用例</span>
              <span class="todo-value">{{ dashboardData.my_todo?.pending_cases || 0 }}</span>
            </div>
            <div class="todo-item">
              <span class="todo-label">待评审用例</span>
              <span class="todo-value">{{ dashboardData.my_todo?.pending_reviews || 0 }}</span>
            </div>
            <div class="todo-item">
              <span class="todo-label">待执行任务</span>
              <span class="todo-value">{{ dashboardData.overview?.in_progress_executions || 0 }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="status-dist-card">
            <template #header>
              <span>测试集用例统计</span>
            </template>
            <el-table :data="suiteStats" stripe style="width: 100%;">
              <el-table-column prop="name" label="测试集名称" min-width="150" show-overflow-tooltip />
              <el-table-column prop="case_count" label="用例数" width="100" align="center" />
              <el-table-column label="状态分布" min-width="300">
                <template #default="{ row }">
                  <div class="status-bar">
                    <div v-if="row.status_dist" class="status-segment">
                      <div v-if="row.status_dist.designing" class="segment designing" :style="{ width: (row.status_dist.designing / row.case_count * 100) + '%' }" :title="'设计中: ' + row.status_dist.designing"></div>
                      <div v-if="row.status_dist.pending_review" class="segment pending_review" :style="{ width: (row.status_dist.pending_review / row.case_count * 100) + '%' }" :title="'待评审: ' + row.status_dist.pending_review"></div>
                      <div v-if="row.status_dist.reviewed" class="segment reviewed" :style="{ width: (row.status_dist.reviewed / row.case_count * 100) + '%' }" :title="'已评审: ' + row.status_dist.reviewed"></div>
                      <div v-if="row.status_dist.approved" class="segment approved" :style="{ width: (row.status_dist.approved / row.case_count * 100) + '%' }" :title="'已批准: ' + row.status_dist.approved"></div>
                      <div v-if="row.status_dist.deprecated" class="segment deprecated" :style="{ width: (row.status_dist.deprecated / row.case_count * 100) + '%' }" :title="'废弃: ' + row.status_dist.deprecated"></div>
                    </div>
                    <span v-else>-</span>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-empty v-else-if="!selectedProjectId" description="请先选择一个项目" />
    <el-empty v-else description="暂无数据" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Folder, Document, VideoPlay, DataLine } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import * as echarts from 'echarts'

const router = useRouter()
const route = useRoute()

const projects = ref([])
const selectedProjectId = ref(null)
const dashboardData = ref(null)
const loading = ref(false)
const statusChartRef = ref(null)
const priorityChartRef = ref(null)
let statusChart = null
let priorityChart = null

const suiteStats = computed(() => {
  if (!dashboardData.value?.suite_stats) return []
  return dashboardData.value.suite_stats.map(suite => {
    const statusDist = {}
    if (suite.case_status_dist) {
      Object.entries(suite.case_status_dist).forEach(([status, count]) => {
        statusDist[status] = count
      })
    }
    return {
      ...suite,
      status_dist: statusDist
    }
  })
})

const loadProjects = async () => {
  try {
    const response = await apiService.projects.getList({ per_page: 100 })
    projects.value = response?.projects || response || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

const loadDashboard = async () => {
  if (!selectedProjectId.value) return
  loading.value = true
  try {
    const response = await apiService.tests.getTestDashboard(selectedProjectId.value)
    console.log('Dashboard API response:', response)
    dashboardData.value = response
    await nextTick()
    initCharts()
  } catch (error) {
    console.error('加载仪表盘失败:', error)
    ElMessage.error('加载仪表盘失败')
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  initStatusChart()
  initPriorityChart()
}

const initStatusChart = () => {
  if (!statusChartRef.value || !dashboardData.value?.case_status_distribution) return

  if (statusChart) {
    statusChart.dispose()
  }

  statusChart = echarts.init(statusChartRef.value)
  const dist = dashboardData.value.case_status_distribution

  const statusMap = {
    'designing': '设计中',
    'pending_review': '待评审',
    'reviewed': '已评审',
    'approved': '已批准',
    'deprecated': '废弃'
  }

  const data = Object.entries(dist).map(([status, count]) => ({
    name: statusMap[status] || status,
    value: count
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '用例状态',
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        data: data
      }
    ]
  }

  statusChart.setOption(option)
}

const initPriorityChart = () => {
  if (!priorityChartRef.value || !dashboardData.value?.case_priority_distribution) return

  if (priorityChart) {
    priorityChart.dispose()
  }

  priorityChart = echarts.init(priorityChartRef.value)
  const dist = dashboardData.value.case_priority_distribution

  const priorityMap = { 0: 'P0', 1: 'P1', 2: 'P2', 3: 'P3' }

  const data = Object.entries(dist).map(([priority, count]) => ({
    name: priorityMap[priority] || `P${priority}`,
    value: count
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '优先级',
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        data: data
      }
    ]
  }

  priorityChart.setOption(option)
}

const handleProjectChange = async (projectId) => {
  if (projectId) {
    await loadDashboard()
  } else {
    dashboardData.value = null
  }
}

const getProgressColor = (value) => {
  if (value >= 80) return '#67C23A'
  if (value >= 60) return '#E6A23C'
  return '#F56C6C'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const handleResize = () => {
  if (statusChart) statusChart.resize()
  if (priorityChart) priorityChart.resize()
}

onMounted(async () => {
  await loadProjects()
  // 从路由参数或查询参数中获取项目ID
  const projectIdFromRoute = route.params.projectId || route.query.projectId
  if (projectIdFromRoute) {
    const projectId = parseInt(projectIdFromRoute)
    // 检查项目是否在列表中
    const projectExists = projects.value.some(p => p.id === projectId)
    if (projectExists) {
      selectedProjectId.value = projectId
      await loadDashboard()
    } else {
      console.warn('路由中的项目ID不在项目列表中:', projectId)
    }
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (statusChart) statusChart.dispose()
  if (priorityChart) priorityChart.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.test-dashboard {
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.overview-row {
  margin-bottom: 20px;
}

.overview-card {
  display: flex;
  align-items: center;
  padding: 16px;
  gap: 16px;
}

.overview-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.overview-icon.suites {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
}

.overview-icon.cases {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}

.overview-icon.executions {
  background: linear-gradient(135deg, #E6A23C, #ebb563);
}

.overview-icon.coverage {
  background: linear-gradient(135deg, #909399, #a6a9ad);
}

.overview-info {
  flex: 1;
}

.overview-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.overview-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.chart-card {
  height: 100%;
}

.table-card {
  height: 100%;
}

.todo-card {
  height: 100%;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #ebeef5;
}

.todo-item:last-child {
  border-bottom: none;
}

.todo-label {
  font-size: 14px;
  color: #606266;
}

.todo-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.status-dist-card {
  margin-bottom: 20px;
}

.status-bar {
  display: flex;
  height: 20px;
  border-radius: 4px;
  overflow: hidden;
}

.status-segment {
  display: flex;
  height: 100%;
  width: 100%;
}

.segment {
  height: 100%;
  transition: width 0.3s;
}

.segment.designing {
  background: #909399;
}

.segment.pending_review {
  background: #E6A23C;
}

.segment.reviewed {
  background: #67C23A;
}

.segment.approved {
  background: #409EFF;
}

.segment.deprecated {
  background: #F56C6C;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .test-dashboard {
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

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .chart-container {
    height: 250px !important;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .test-dashboard {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-value {
    font-size: 18px;
  }
}
</style>