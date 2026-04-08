<template>
  <div class="work-stats-detail">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.push('/dashboard')" type="primary" plain>
          <el-icon><ArrowLeft /></el-icon>
          返回个人工作台
        </el-button>
      </div>
      <h2>工作统计详情</h2>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #E3F2FD;">
            <i class="el-icon-bug" style="color: #2196F3;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.summary?.my_bugs || 0 }}</div>
            <div class="stat-label">我的缺陷</div>
          </div>
          <el-button type="primary" size="small" @click="$router.push('/bugs')">查看详情</el-button>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #E3F2FD;">
            <i class="el-icon-bug" style="color: #2196F3;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.summary?.my_bugs || 0 }}</div>
            <div class="stat-label">待修复Bug</div>
          </div>
          <el-button type="primary" size="small" @click="$router.push('/bugs?assignee=me&status=open,in_progress')">查看详情</el-button>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #E3F2FD;">
            <i class="el-icon-circle-plus" style="color: #2196F3;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.summary?.bugs_created_by_me || 0 }}</div>
            <div class="stat-label">我创建的Bug</div>
          </div>
          <el-button type="primary" size="small" @click="$router.push('/bugs?creator=me')">查看详情</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #E3F2FD;">
            <i class="el-icon-info" style="color: #2196F3;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.summary?.new_bugs || 0 }}</div>
            <div class="stat-label">新增Bug</div>
          </div>
          <el-button type="primary" size="small" @click="$router.push('/bugs?status=open')">查看详情</el-button>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #E3F2FD;">
            <i class="el-icon-circle-check" style="color: #2196F3;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.summary?.fixed_bugs || 0 }}</div>
            <div class="stat-label">已修复Bug</div>
          </div>
          <el-button type="primary" size="small" @click="$router.push('/bugs?status=closed,resolved')">查看详情</el-button>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #E3F2FD;">
            <i class="el-icon-folder-opened" style="color: #2196F3;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.summary?.active_projects || 0 }}</div>
            <div class="stat-label">活跃项目</div>
          </div>
          <el-button type="primary" size="small" @click="$router.push('/projects')">查看详情</el-button>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon-box" style="background: #E3F2FD;">
            <i class="el-icon-data-line" style="color: #2196F3;"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.summary?.my_completion_rate || 0 }}%</div>
            <div class="stat-label">完成率</div>
          </div>
          <el-button type="primary" size="small" disabled>统计</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="charts-card" shadow="hover">
      <template #header>
        <span>统计图表</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="12">
          <div ref="severityChartRef" class="chart-container"></div>
        </el-col>
        <el-col :span="12">
          <div ref="priorityChartRef" class="chart-container"></div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { apiService } from '@/services/api'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const userStore = useUserStore()
const statistics = ref({})
const severityChartRef = ref(null)
const priorityChartRef = ref(null)
let severityChart = null
let priorityChart = null

const fetchStatistics = async () => {
  try {
    const response = await apiService.statistics.getDashboardData()
    statistics.value = response
  } catch (error) {
    console.error('获取统计信息失败:', error)
    ElMessage.error('获取统计信息失败')
  }
}

const initCharts = () => {
  if (severityChartRef.value) {
    severityChart = echarts.init(severityChartRef.value)
    const severityOption = {
      title: { text: 'Bug严重程度分布', left: 'center' },
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: statistics.value.severity_distribution?.low || 0, name: '低' },
          { value: statistics.value.severity_distribution?.medium || 0, name: '中' },
          { value: statistics.value.severity_distribution?.high || 0, name: '高' },
          { value: statistics.value.severity_distribution?.critical || 0, name: '严重' }
        ]
      }]
    }
    severityChart.setOption(severityOption)
  }
  
  if (priorityChartRef.value) {
    priorityChart = echarts.init(priorityChartRef.value)
    const priorityOption = {
      title: { text: 'Bug优先级分布', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['低', '中', '高'] },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar',
        data: [
          statistics.value.priority_distribution?.low || 0,
          statistics.value.priority_distribution?.medium || 0,
          statistics.value.priority_distribution?.high || 0
        ]
      }]
    }
    priorityChart.setOption(priorityOption)
  }
}

const handleResize = () => {
  if (severityChart) severityChart.resize()
  if (priorityChart) priorityChart.resize()
}

onMounted(async () => {
  await fetchStatistics()
  setTimeout(() => initCharts(), 100)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (severityChart) severityChart.dispose()
  if (priorityChart) priorityChart.dispose()
})
</script>

<style scoped>
.work-stats-detail {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.header-left {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px 0;
}

.stat-icon-box {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.stat-icon-box i {
  font-size: 32px;
}

.stat-content {
  margin-bottom: 16px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #2196F3;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.charts-card {
  margin-top: 20px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .work-statistics-detail {
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
  .work-statistics-detail {
    padding: 8px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
