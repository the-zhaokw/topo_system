<template>
  <div class="test-dashboard">
    <!-- 精致头部区域 -->
    <div class="dashboard-header animate-fade-in-down">
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <div class="title-icon">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="title-glow"></div>
          </div>
          <div class="title-text">
            <h2>测试仪表盘</h2>
            <p>全面掌握测试进度与质量指标</p>
          </div>
        </div>
        <div class="header-actions">
          <el-select v-model="selectedProjectId" placeholder="选择项目" clearable @change="handleProjectChange" class="project-select">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
          <el-button @click="loadDashboard" class="refresh-btn btn-glass">
            <el-icon class="refresh-icon"><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
      <!-- 装饰性背景元素 -->
      <div class="header-decoration">
        <div class="decoration-circle circle-1"></div>
        <div class="decoration-circle circle-2"></div>
        <div class="decoration-circle circle-3"></div>
      </div>
    </div>

    <div v-loading="loading" v-if="selectedProjectId && dashboardData" class="dashboard-content">
      <!-- 概览卡片 - 人工美学设计 -->
      <el-row :gutter="20" class="overview-row animate-fade-in-up delay-100">
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="overview-card-elegant">
            <div class="overview-icon-wrapper overview-icon-suites">
              <el-icon><Folder /></el-icon>
              <div class="icon-glow"></div>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ dashboardData.overview?.total_suites || 0 }}</div>
              <div class="overview-label">测试集总数</div>
            </div>
            <div class="overview-decoration"></div>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="overview-card-elegant">
            <div class="overview-icon-wrapper overview-icon-cases">
              <el-icon><Document /></el-icon>
              <div class="icon-glow"></div>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ dashboardData.overview?.total_cases || 0 }}</div>
              <div class="overview-label">用例总数</div>
            </div>
            <div class="overview-decoration"></div>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="overview-card-elegant">
            <div class="overview-icon-wrapper overview-icon-executions">
              <el-icon><VideoPlay /></el-icon>
              <div class="icon-glow"></div>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ dashboardData.overview?.in_progress_executions || 0 }}</div>
              <div class="overview-label">进行中执行</div>
            </div>
            <div class="overview-decoration"></div>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="overview-card-elegant">
            <div class="overview-icon-wrapper overview-icon-coverage">
              <el-icon><DataLine /></el-icon>
              <div class="icon-glow"></div>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ dashboardData.overview?.coverage_rate || 0 }}%</div>
              <div class="overview-label">需求覆盖率</div>
            </div>
            <div class="overview-decoration"></div>
          </div>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20" class="charts-row animate-fade-in-up delay-200">
        <el-col :span="12" :xs="24">
          <el-card class="chart-card glass-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <el-icon><PieChart /></el-icon>
                  <span>用例状态分布</span>
                </div>
              </div>
            </template>
            <div ref="statusChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :span="12" :xs="24">
          <el-card class="chart-card glass-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <el-icon><Histogram /></el-icon>
                  <span>用例优先级分布</span>
                </div>
              </div>
            </template>
            <div ref="priorityChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 表格和待办区域 -->
      <el-row :gutter="20" class="content-row animate-fade-in-up delay-300">
        <el-col :span="16" :xs="24">
          <el-card class="table-card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><List /></el-icon>
                  <span>最近执行记录</span>
                </div>
              </div>
            </template>
            <el-table :data="dashboardData.recent_pass_rates" stripe class="custom-table">
              <el-table-column prop="name" label="执行名称" min-width="150" show-overflow-tooltip />
              <el-table-column prop="pass_rate" label="通过率" width="120">
                <template #default="{ row }">
                  <div class="progress-wrapper">
                    <el-progress 
                      :percentage="row.pass_rate" 
                      :color="getProgressColor(row.pass_rate)"
                      :stroke-width="8"
                      class="custom-progress"
                    />
                    <span class="progress-text">{{ row.pass_rate }}%</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="completed_at" label="完成时间" width="160">
                <template #default="{ row }">
                  <span class="time-text">{{ formatDate(row.completed_at) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="8" :xs="24">
          <el-card class="todo-card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Bell /></el-icon>
                  <span>我的待办</span>
                </div>
              </div>
            </template>
            <div class="todo-list">
              <div class="todo-item">
                <div class="todo-icon todo-icon-design">
                  <el-icon><EditPen /></el-icon>
                </div>
                <div class="todo-info">
                  <span class="todo-label">待设计用例</span>
                  <span class="todo-value">{{ dashboardData.my_todo?.pending_cases || 0 }}</span>
                </div>
              </div>
              <div class="todo-item">
                <div class="todo-icon todo-icon-review">
                  <el-icon><View /></el-icon>
                </div>
                <div class="todo-info">
                  <span class="todo-label">待评审用例</span>
                  <span class="todo-value">{{ dashboardData.my_todo?.pending_reviews || 0 }}</span>
                </div>
              </div>
              <div class="todo-item">
                <div class="todo-icon todo-icon-execute">
                  <el-icon><VideoPlay /></el-icon>
                </div>
                <div class="todo-info">
                  <span class="todo-label">待执行任务</span>
                  <span class="todo-value">{{ dashboardData.overview?.in_progress_executions || 0 }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 测试集统计 -->
      <el-card class="status-dist-card glass-card animate-fade-in-up delay-400" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon><Collection /></el-icon>
              <span>测试集用例统计</span>
            </div>
          </div>
        </template>
        <el-table :data="suiteStats" stripe class="custom-table">
          <el-table-column prop="name" label="测试集名称" min-width="150" show-overflow-tooltip />
          <el-table-column prop="case_count" label="用例数" width="100" align="center">
            <template #default="{ row }">
              <span class="case-count">{{ row.case_count }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态分布" min-width="350">
            <template #default="{ row }">
              <div class="status-bar-wrapper">
                <div v-if="row.status_dist" class="status-bar">
                  <div v-if="row.status_dist.designing" class="status-segment segment-designing" :style="{ width: (row.status_dist.designing / row.case_count * 100) + '%' }" :title="'设计中: ' + row.status_dist.designing"></div>
                  <div v-if="row.status_dist.pending_review" class="status-segment segment-pending" :style="{ width: (row.status_dist.pending_review / row.case_count * 100) + '%' }" :title="'待评审: ' + row.status_dist.pending_review"></div>
                  <div v-if="row.status_dist.reviewed" class="status-segment segment-reviewed" :style="{ width: (row.status_dist.reviewed / row.case_count * 100) + '%' }" :title="'已评审: ' + row.status_dist.reviewed"></div>
                  <div v-if="row.status_dist.approved" class="status-segment segment-approved" :style="{ width: (row.status_dist.approved / row.case_count * 100) + '%' }" :title="'已批准: ' + row.status_dist.approved"></div>
                  <div v-if="row.status_dist.deprecated" class="status-segment segment-deprecated" :style="{ width: (row.status_dist.deprecated / row.case_count * 100) + '%' }" :title="'废弃: ' + row.status_dist.deprecated"></div>
                </div>
                <span v-else class="no-data">-</span>
              </div>
              <div class="status-legend">
                <span v-if="row.status_dist?.designing" class="legend-item">
                  <span class="legend-dot dot-designing"></span>设计中 {{ row.status_dist.designing }}
                </span>
                <span v-if="row.status_dist?.pending_review" class="legend-item">
                  <span class="legend-dot dot-pending"></span>待评审 {{ row.status_dist.pending_review }}
                </span>
                <span v-if="row.status_dist?.reviewed" class="legend-item">
                  <span class="legend-dot dot-reviewed"></span>已评审 {{ row.status_dist.reviewed }}
                </span>
                <span v-if="row.status_dist?.approved" class="legend-item">
                  <span class="legend-dot dot-approved"></span>已批准 {{ row.status_dist.approved }}
                </span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <el-empty v-else-if="!selectedProjectId" description="请先选择一个项目" class="empty-state" />
    <el-empty v-else description="暂无数据" class="empty-state" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Folder, Document, VideoPlay, DataLine, PieChart, Histogram, List, Bell, EditPen, View, Collection, DataAnalysis } from '@element-plus/icons-vue'
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

  const statusColors = {
    'designing': '#909399',
    'pending_review': '#f59e0b',
    'reviewed': '#10b981',
    'approved': '#3b82f6',
    'deprecated': '#ef4444'
  }

  const data = Object.entries(dist).map(([status, count]) => ({
    name: statusMap[status] || status,
    value: count,
    itemStyle: { color: statusColors[status] || '#909399' }
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: { color: '#1e293b' }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: '#64748b' }
    },
    series: [
      {
        name: '用例状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 3
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
  const priorityColors = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981']

  const data = Object.entries(dist).map(([priority, count], index) => ({
    name: priorityMap[priority] || `P${priority}`,
    value: count,
    itemStyle: { color: priorityColors[index % priorityColors.length] }
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: { color: '#1e293b' }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: '#64748b' }
    },
    series: [
      {
        name: '优先级',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 3
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
  if (value >= 80) return '#10b981'
  if (value >= 60) return '#f59e0b'
  return '#ef4444'
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
  const projectIdFromRoute = route.params.projectId || route.query.projectId
  if (projectIdFromRoute) {
    const projectId = parseInt(projectIdFromRoute)
    const projectExists = projects.value.some(p => p.id === projectId)
    if (projectExists) {
      selectedProjectId.value = projectId
      await loadDashboard()
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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.test-dashboard {
  padding: 20px;
  background: linear-gradient(135deg, #fef9f3 0%, #fdf4ed 25%, #f8fafc 50%, #f1f5f9 75%, #f0f9ff 100%);
  min-height: 100%;
  background-attachment: fixed;
}

/* 精致头部区域 */
.dashboard-header {
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #0c4a6e 0%, #0c4a6e 50%, #0c4a6e 100%);
  border-radius: 20px;
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(30, 27, 75, 0.3);
}

.dashboard-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top, rgba(56, 189, 248, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-icon-wrapper {
  position: relative;
}

.title-icon {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.title-icon .el-icon {
  font-size: 32px;
  color: #818cf8;
}

.title-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.4) 0%, transparent 70%);
  filter: blur(20px);
}

.title-text h2 {
  margin: 0 0 6px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #ffffff 0%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-text p {
  margin: 0;
  font-size: 15px;
  opacity: 0.85;
  color: #a5b4fc;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.project-select {
  width: 200px;
}

.project-select :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
}

.project-select :deep(.el-input__inner) {
  color: white;
}

.project-select :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.refresh-icon {
  margin-right: 6px;
}

/* 装饰性背景元素 */
.header-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(56, 189, 248, 0.1);
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -100px;
  right: -50px;
}

.circle-2 {
  width: 150px;
  height: 150px;
  bottom: -75px;
  right: 100px;
  background: rgba(56, 189, 248, 0.1);
}

.circle-3 {
  width: 100px;
  height: 100px;
  top: 20px;
  right: 200px;
  background: rgba(168, 85, 247, 0.08);
}

/* 概览卡片 - 人工美学设计 */
.overview-row {
  margin-bottom: 24px;
}

.overview-card-elegant {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.04),
    0 4px 16px rgba(0, 0, 0, 0.02),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.overview-card-elegant::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #0ea5e9, #38bdf8, #a855f7);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.overview-card-elegant:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 
    0 12px 24px rgba(0, 0, 0, 0.08),
    0 4px 12px rgba(0, 0, 0, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.overview-card-elegant:hover::before {
  opacity: 1;
}

.overview-card-elegant:hover .icon-glow {
  opacity: 0.6;
}

.overview-card-elegant:hover .overview-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.overview-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 1;
}

.overview-icon-wrapper .el-icon {
  font-size: 28px;
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.overview-icon-suites {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 50%, #a5b4fc 100%);
  color: #0284c7;
}

.overview-icon-cases {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 50%, #6ee7b7 100%);
  color: #047857;
}

.overview-icon-executions {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 50%, #fcd34d 100%);
  color: #b45309;
}

.overview-icon-coverage {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 50%, #60a5fa 100%);
  color: #1d4ed8;
}

.overview-info {
  flex: 1;
  min-width: 0;
  position: relative;
  z-index: 1;
}

.overview-value {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
  transition: transform 0.3s ease;
}

.overview-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 6px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.overview-decoration {
  position: absolute;
  top: 50%;
  right: -20px;
  transform: translateY(-50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.08) 0%, transparent 70%);
  pointer-events: none;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 20px;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.04),
    0 2px 8px rgba(0, 0, 0, 0.02),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.glass-card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 12px 28px rgba(0, 0, 0, 0.08),
    0 4px 12px rgba(0, 0, 0, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.95);
}

/* 图表区域 */
.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-card :deep(.el-card__body) {
  padding: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  color: #1e293b;
  font-size: 16px;
}

.chart-title .el-icon {
  color: #0ea5e9;
  font-size: 20px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* 内容区域 */
.content-row {
  margin-bottom: 24px;
}

.table-card {
  margin-bottom: 20px;
  height: calc(100% - 20px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  color: #1e293b;
  font-size: 16px;
}

.card-title .el-icon {
  color: #0ea5e9;
  font-size: 20px;
}

/* 自定义表格 */
.custom-table :deep(.el-table__header) {
  background: rgba(241, 245, 249, 0.5);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) {
  background: rgba(56, 189, 248, 0.05);
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.custom-progress {
  flex: 1;
}

.progress-text {
  font-size: 13px;
  font-weight: 700;
  color: #64748b;
  min-width: 45px;
  text-align: right;
}

.time-text {
  color: #64748b;
  font-size: 13px;
}

.case-count {
  font-weight: 700;
  color: #1e293b;
  font-size: 15px;
}

/* 待办卡片 */
.todo-card {
  margin-bottom: 20px;
  height: calc(100% - 20px);
}

.todo-list {
  padding: 8px 0;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  margin-bottom: 12px;
  background: rgba(241, 245, 249, 0.5);
  border-radius: 14px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.todo-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.todo-item:last-child {
  margin-bottom: 0;
}

.todo-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.todo-icon .el-icon {
  font-size: 22px;
}

.todo-icon-design {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #b45309;
}

.todo-icon-review {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
  color: #1d4ed8;
}

.todo-icon-execute {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #047857;
}

.todo-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.todo-label {
  font-size: 14px;
  color: #475569;
  font-weight: 600;
}

.todo-value {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 测试集统计 */
.status-dist-card {
  margin-bottom: 20px;
}

.status-bar-wrapper {
  margin-bottom: 8px;
}

.status-bar {
  display: flex;
  height: 24px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.status-segment {
  height: 100%;
  transition: all 0.3s ease;
  cursor: pointer;
}

.status-segment:hover {
  filter: brightness(1.1);
}

.segment-designing {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
}

.segment-pending {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.segment-reviewed {
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
}

.segment-approved {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
}

.segment-deprecated {
  background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
}

.no-data {
  color: #9ca3af;
  font-size: 13px;
}

.status-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-designing {
  background: #6b7280;
}

.dot-pending {
  background: #f59e0b;
}

.dot-reviewed {
  background: #10b981;
}

.dot-approved {
  background: #3b82f6;
}

/* 空状态 */
.empty-state {
  margin-top: 60px;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  .test-dashboard {
    padding: 12px;
  }

  .dashboard-header {
    padding: 20px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-title {
    gap: 16px;
  }

  .title-icon {
    width: 52px;
    height: 52px;
  }

  .title-icon .el-icon {
    font-size: 24px;
  }

  .title-text h2 {
    font-size: 22px;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .project-select {
    width: 100%;
  }

  .refresh-btn {
    width: 100%;
    justify-content: center;
  }

  .overview-card-elegant {
    padding: 20px;
    margin-bottom: 12px;
  }

  .overview-icon-wrapper {
    width: 48px;
    height: 48px;
  }

  .overview-icon-wrapper .el-icon {
    font-size: 24px;
  }

  .overview-value {
    font-size: 26px;
  }

  .chart-container {
    height: 280px;
  }

  .progress-wrapper {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .custom-progress {
    width: 100%;
  }

  .status-legend {
    gap: 8px;
  }
}

@media screen and (max-width: 480px) {
  .dashboard-header {
    padding: 16px;
  }

  .title-text h2 {
    font-size: 20px;
  }

  .overview-value {
    font-size: 24px;
  }

  .chart-container {
    height: 240px;
  }
}
</style>
