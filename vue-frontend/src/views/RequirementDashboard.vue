<template>
  <div class="requirement-dashboard" v-loading="loading">
    <div class="page-header">
      <div class="header-left">
        <h2>需求仪表盘</h2>
        <span class="subtitle">{{ projectName }} - 需求概览与统计</span>
      </div>
      <div class="header-right">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 概览统计卡片 -->
    <el-row :gutter="20" class="overview-row">
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-icon documents">
            <el-icon><Document /></el-icon>
          </div>
          <div class="overview-content">
            <div class="overview-value">{{ overviewStats.totalDocuments }}</div>
            <div class="overview-label">需求文档</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-icon items">
            <el-icon><List /></el-icon>
          </div>
          <div class="overview-content">
            <div class="overview-value">{{ overviewStats.totalItems }}</div>
            <div class="overview-label">需求条目</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-icon coverage">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="overview-content">
            <div class="overview-value">{{ overviewStats.coverageRate }}%</div>
            <div class="overview-label">需求覆盖率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-icon pending">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="overview-content">
            <div class="overview-value">{{ overviewStats.pendingReview }}</div>
            <div class="overview-label">待评审</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>需求状态分布</span>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>优先级分布</span>
          </template>
          <div ref="priorityChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <span>需求变更趋势（近30天）</span>
          </template>
          <div ref="trendChartRef" class="chart-container-large"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="todo-card">
          <template #header>
            <span>我的待办</span>
            <el-badge :value="myTodos.length" :hidden="myTodos.length === 0" />
          </template>
          <div class="todo-list" v-if="myTodos.length > 0">
            <div 
              v-for="todo in myTodos.slice(0, 5)" 
              :key="todo.id" 
              class="todo-item"
              @click="handleTodoClick(todo)"
            >
              <div class="todo-type">
                <el-tag size="small" :type="getTodoTypeTag(todo.type)">
                  {{ getTodoTypeText(todo.type) }}
                </el-tag>
              </div>
              <div class="todo-content">
                <div class="todo-title">{{ todo.title || todo.identifier }}</div>
                <div class="todo-message">{{ todo.message }}</div>
              </div>
            </div>
            <el-button 
              v-if="myTodos.length > 5" 
              type="primary" 
              link 
              class="view-more-btn"
              @click="showAllTodos"
            >
              查看全部 {{ myTodos.length }} 项
            </el-button>
          </div>
          <el-empty v-else description="暂无待办事项" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细统计表格 -->
    <el-card class="detail-card">
      <template #header>
        <span>各文档需求详情</span>
      </template>
      <el-table :data="documentStats" border stripe>
        <el-table-column prop="name" label="文档名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="goToDocument(row.id)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="docType" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.doc_type === 'functional' ? 'primary' : 'warning'" size="small">
              {{ row.doc_type === 'functional' ? '功能需求' : '非功能需求' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="itemCount" label="条目数" width="80" align="center" />
        <el-table-column prop="approvedCount" label="已批准" width="80" align="center">
          <template #default="{ row }">
            <span class="count-success">{{ row.approvedCount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="completedCount" label="已完成" width="80" align="center">
          <template #default="{ row }">
            <span class="count-success">{{ row.completedCount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pendingCount" label="待处理" width="80" align="center">
          <template #default="{ row }">
            <span class="count-warning">{{ row.pendingCount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="coverage" label="覆盖率" width="120">
          <template #default="{ row }">
            <el-progress 
              :percentage="row.coverage" 
              :color="getCoverageColor(row.coverage)"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="goToDocument(row.id)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 全部待办对话框 -->
    <el-dialog v-model="showTodoDialog" title="我的待办" width="600px">
      <div class="todo-list-full">
        <div 
          v-for="todo in myTodos" 
          :key="todo.id" 
          class="todo-item-full"
          @click="handleTodoClick(todo)"
        >
          <div class="todo-type">
            <el-tag size="small" :type="getTodoTypeTag(todo.type)">
              {{ getTodoTypeText(todo.type) }}
            </el-tag>
          </div>
          <div class="todo-content">
            <div class="todo-title">{{ todo.title || todo.identifier }}</div>
            <div class="todo-message">{{ todo.message }}</div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showTodoDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Document, List, DataLine, Clock } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useUserStore } from '@/stores/user'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const projectName = ref('')
const overviewStats = ref({
  totalDocuments: 0,
  totalItems: 0,
  coverageRate: 0,
  pendingReview: 0
})

const documentStats = ref([])
const myTodos = ref([])
const statusChartRef = ref(null)
const priorityChartRef = ref(null)
const trendChartRef = ref(null)
let statusChart = null
let priorityChart = null
let trendChart = null

const showTodoDialog = ref(false)

const projectId = computed(() => route.params.projectId)

const fetchDashboardData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchStatistics(),
      fetchCoverage(),
      fetchDocumentStats(),
      fetchMyTodos(),
      fetchTrendData()
    ])
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchStatistics = async () => {
  try {
    const response = await api.get(`/projects/${projectId.value}/requirement-statistics`)
    if (response.success) {
      const stats = response.statistics
      overviewStats.value = {
        totalDocuments: Object.values(stats.document_status || {}).reduce((a, b) => a + b, 0),
        totalItems: Object.values(stats.item_status || {}).reduce((a, b) => a + b, 0),
        coverageRate: 0,
        pendingReview: stats.item_status?.pending_review || 0
      }
      renderStatusChart(stats.item_status || {})
      renderPriorityChart(stats.item_priority || {})
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const fetchCoverage = async () => {
  try {
    const response = await api.get(`/projects/${projectId.value}/requirement-coverage`)
    if (response.success) {
      overviewStats.value.coverageRate = response.statistics.coverage_rate || 0
    }
  } catch (error) {
    console.error('获取覆盖率失败:', error)
  }
}

const fetchDocumentStats = async () => {
  try {
    const response = await api.get(`/projects/${projectId.value}/requirement-documents`)
    if (response.success) {
      const docs = response.documents || []
      documentStats.value = await Promise.all(docs.map(async (doc) => {
        const detailRes = await api.get(`/requirement-documents/${doc.id}`)
        const items = detailRes.document?.items || []
        
        const statusCounts = {}
        items.forEach(item => {
          statusCounts[item.status] = (statusCounts[item.status] || 0) + 1
        })
        
        return {
          id: doc.id,
          name: doc.name,
          doc_type: doc.doc_type,
          status: doc.status,
          itemCount: items.length,
          approvedCount: statusCounts.approved || 0,
          completedCount: (statusCounts.completed || 0) + (statusCounts.verified || 0),
          pendingCount: (statusCounts.pending_review || 0) + (statusCounts.in_progress || 0),
          coverage: items.length > 0 ? Math.round(((statusCounts.completed || 0) + (statusCounts.verified || 0)) / items.length * 100) : 0
        }
      }))
    }
  } catch (error) {
    console.error('获取文档统计失败:', error)
  }
}

const fetchMyTodos = async () => {
  try {
    const response = await api.get('/my/requirement-todos')
    if (response.success) {
      myTodos.value = response.todos || []
    }
  } catch (error) {
    console.error('获取待办失败:', error)
  }
}

const fetchTrendData = async () => {
  try {
    const response = await api.get(`/projects/${projectId.value}/requirement-trend`, {
      params: { days: 30 }
    })
    if (response.success) {
      renderTrendChart(response.trend_data || [])
    }
  } catch (error) {
    console.error('获取趋势数据失败:', error)
  }
}

const renderStatusChart = (statusData) => {
  if (!statusChartRef.value) return
  
  if (statusChart) {
    statusChart.dispose()
  }
  
  statusChart = echarts.init(statusChartRef.value)
  
  const statusMap = {
    'pending_review': '待评审',
    'reviewed': '已评审',
    'approved': '已批准',
    'in_progress': '开发中',
    'completed': '已完成',
    'verified': '已验证'
  }
  
  const statusColors = {
    'pending_review': '#909399',
    'reviewed': '#e6a23c',
    'approved': '#67c23a',
    'in_progress': '#409eff',
    'completed': '#67c23a',
    'verified': '#67c23a'
  }
  
  const data = Object.entries(statusData).map(([status, count]) => ({
    name: statusMap[status] || status,
    value: count,
    itemStyle: { color: statusColors[status] || '#409eff' }
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
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
    }]
  }
  
  statusChart.setOption(option)
}

const renderPriorityChart = (priorityData) => {
  if (!priorityChartRef.value) return
  
  if (priorityChart) {
    priorityChart.dispose()
  }
  
  priorityChart = echarts.init(priorityChartRef.value)
  
  const priorityMap = { '1': '低', '2': '中', '3': '高' }
  const priorityColors = { '1': '#909399', '2': '#e6a23c', '3': '#f56c6c' }
  
  const data = Object.entries(priorityData).map(([priority, count]) => ({
    name: priorityMap[priority] || priority,
    value: count,
    itemStyle: { color: priorityColors[priority] || '#409eff' }
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
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
    }]
  }
  
  priorityChart.setOption(option)
}

const renderTrendChart = (trendData) => {
  if (!trendChartRef.value) return
  
  if (trendChart) {
    trendChart.dispose()
  }
  
  trendChart = echarts.init(trendChartRef.value)
  
  const dates = trendData.map(d => d.date)
  const values = trendData.map(d => d.count)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45,
        interval: Math.floor(dates.length / 7)
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [{
      type: 'line',
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      data: values,
      itemStyle: { color: '#409eff' },
      areaColor: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
        ]
      }
    }]
  }
  
  trendChart.setOption(option)
}

const refreshData = () => {
  fetchDashboardData()
}

const handleTodoClick = (todo) => {
  if (todo.type === 'document_review') {
    router.push(`/projects/${projectId.value}/requirements/${todo.doc_id}`)
  } else if (todo.type === 'item_assigned' || todo.type === 'item_review') {
    router.push(`/projects/${projectId.value}/requirements/${todo.doc_id}`)
  }
}

const showAllTodos = () => {
  showTodoDialog.value = true
}

const goToDocument = (docId) => {
  router.push(`/projects/${projectId.value}/requirements/${docId}`)
}

const getStatusType = (status) => {
  const typeMap = {
    'draft': 'info',
    'reviewing': 'warning',
    'approved': 'success',
    'deprecated': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'draft': '草稿',
    'reviewing': '评审中',
    'approved': '已批准',
    'deprecated': '已废弃'
  }
  return textMap[status] || status
}

const getTodoTypeTag = (type) => {
  const tagMap = {
    'item_assigned': 'primary',
    'item_review': 'warning',
    'document_review': 'danger'
  }
  return tagMap[type] || 'info'
}

const getTodoTypeText = (type) => {
  const textMap = {
    'item_assigned': '待分配',
    'item_review': '待评审',
    'document_review': '文档评审'
  }
  return textMap[type] || type
}

const getCoverageColor = (coverage) => {
  if (coverage >= 80) return '#67c23a'
  if (coverage >= 50) return '#e6a23c'
  return '#f56c6c'
}

const handleResize = () => {
  statusChart?.resize()
  priorityChart?.resize()
  trendChart?.resize()
}

onMounted(async () => {
  if (projectId.value) {
    try {
      const projectRes = await api.get(`/projects/${projectId.value}/`)
      if (projectRes.project) {
        projectName.value = projectRes.project.name
      }
    } catch (error) {
      console.error('获取项目信息失败:', error)
    }
    
    await fetchDashboardData()
  }
  
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  statusChart?.dispose()
  priorityChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.requirement-dashboard {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.overview-row {
  margin-bottom: 20px;
}

.overview-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.overview-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 28px;
  color: #fff;
}

.overview-icon.documents {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.overview-icon.items {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.overview-icon.coverage {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
}

.overview-icon.pending {
  background: linear-gradient(135deg, #f56c6c, #f78989);
}

.overview-content {
  flex: 1;
}

.overview-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.overview-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  min-height: 300px;
}

.chart-container {
  height: 250px;
}

.chart-container-large {
  height: 280px;
}

.todo-card {
  min-height: 320px;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 280px;
  overflow-y: auto;
}

.todo-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.todo-item:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.todo-type {
  margin-bottom: 8px;
}

.todo-title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
  margin-bottom: 4px;
}

.todo-message {
  color: #909399;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.view-more-btn {
  width: 100%;
  margin-top: 8px;
}

.detail-card {
  margin-top: 20px;
}

.count-success {
  color: #67c23a;
  font-weight: 600;
}

.count-warning {
  color: #e6a23c;
  font-weight: 600;
}

.todo-list-full {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.todo-item-full {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.todo-item-full:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .requirement-dashboard {
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

  .chart-placeholder {
    font-size: 13px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .requirement-dashboard {
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
