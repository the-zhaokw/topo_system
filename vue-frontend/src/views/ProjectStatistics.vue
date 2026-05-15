<template>
  <div class="project-statistics">
    <div class="statistics-header animate-fade-in-down">
      <div class="header-title">
        <div class="title-icon">
          <el-icon><PieChart /></el-icon>
        </div>
        <div class="title-content">
          <h2>项目统计看板</h2>
          <p>全面分析项目数据，洞察项目进展</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button @click="refreshData" class="refresh-btn">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- KPI 统计卡片 - 美学设计 -->
    <div class="kpi-cards animate-fade-in-up delay-100">
      <el-row :gutter="20">
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="kpi-card kpi-card-total" :style="{ '--index': 0 }">
            <div class="kpi-icon-wrapper kpi-icon-total">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">
                <span class="kpi-number">{{ kpiData.totalProjects || 0 }}</span>
              </div>
              <div class="kpi-label">项目总数</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="kpi-card kpi-card-active" :style="{ '--index': 1 }">
            <div class="kpi-icon-wrapper kpi-icon-active">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value success">
                <span class="kpi-number">{{ kpiData.activeProjects || 0 }}</span>
              </div>
              <div class="kpi-label">进行中项目</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="kpi-card kpi-card-tasks" :style="{ '--index': 2 }">
            <div class="kpi-icon-wrapper kpi-icon-tasks">
              <el-icon><List /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value info">
                <span class="kpi-number">{{ kpiData.totalTasks || 0 }}</span>
              </div>
              <div class="kpi-label">需求总数</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="kpi-card kpi-card-bugs" :style="{ '--index': 3 }">
            <div class="kpi-icon-wrapper kpi-icon-bugs">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value danger">
                <span class="kpi-number">{{ kpiData.totalBugs || 0 }}</span>
              </div>
              <div class="kpi-label">缺陷总数</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="20" class="chart-section animate-fade-in-up delay-200">
      <el-col :span="12" :xs="24">
        <el-card class="chart-card glass-card" shadow="hover">
          <template #header>
            <div class="chart-header">
              <div class="chart-title">
                <el-icon><Warning /></el-icon>
                <span>项目Bug分布</span>
              </div>
            </div>
          </template>
          <div ref="bugDistributionChart" class="chart-container" style="height: 400px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12" :xs="24">
        <el-card class="chart-card glass-card" shadow="hover">
          <template #header>
            <div class="chart-header">
              <div class="chart-title">
                <el-icon><List /></el-icon>
                <span>项目需求统计</span>
              </div>
            </div>
          </template>
          <div ref="taskChart" class="chart-container" style="height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="data-table-card glass-card animate-fade-in-up delay-300" shadow="hover">
      <template #header>
        <div class="table-header">
          <div class="table-title">
            <el-icon><Document /></el-icon>
            <span>项目详情列表</span>
          </div>
        </div>
      </template>
      <el-table :data="projectList" v-loading="loading" class="custom-table">
        <el-table-column prop="project_name" label="项目名称" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="light" class="status-tag">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_tasks" label="需求总数" width="100" />
        <el-table-column prop="completed_tasks" label="已完成需求" width="100" />
        <el-table-column prop="task_completion_rate" label="需求完成率" min-width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.task_completion_rate || 0" :color="getProgressColor(row.task_completion_rate)" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column prop="total_bugs" label="缺陷总数" width="100" />
        <el-table-column prop="resolved_bugs" label="已解决缺陷" width="100" />
        <el-table-column prop="bug_resolution_rate" label="缺陷解决率" min-width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.bug_resolution_rate || 0" :color="getProgressColor(row.bug_resolution_rate)" :stroke-width="8" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="chart-card glass-card animate-fade-in-up delay-400" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="chart-header">
          <div class="chart-title">
            <el-icon><TrendCharts /></el-icon>
            <span>项目Bug趋势（最近30天）</span>
          </div>
        </div>
      </template>
      <div ref="trendChart" class="chart-container" style="height: 350px;"></div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, PieChart, FolderOpened, Folder, List, WarningFilled, Document, Warning, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { apiService } from '@/services/api'

export default {
  name: 'ProjectStatistics',
  components: { Refresh, PieChart, FolderOpened, Folder, List, WarningFilled, Document, Warning, TrendCharts },
  setup() {
    const loading = ref(false)
    const kpiData = ref({})
    const projectList = ref([])
    
    const bugDistributionChart = ref(null)
    const taskChart = ref(null)
    const trendChart = ref(null)

    let bugChartInstance = null
    let taskChartInstance = null
    let trendChartInstance = null

    const getStatusType = (status) => {
      const typeMap = {
        'active': 'success',
        'in_progress': 'primary',
        'completed': 'info',
        'on_hold': 'warning',
        'cancelled': 'danger'
      }
      return typeMap[status] || 'info'
    }

    const getProgressColor = (percentage) => {
      if (percentage >= 80) return '#43e97b'
      if (percentage >= 50) return '#f6d365'
      return '#ff6b6b'
    }

    const loadData = async () => {
      loading.value = true
      try {
        const [projectRes, reqRes] = await Promise.all([
          apiService.statistics.getProjectStatistics(),
          apiService.statistics.getRequirementStatistics()
        ])

        const projectData = projectRes || {}
        const reqData = reqRes || {}

        const projectStats = projectData.project_bug_distribution || []
        const projects = []
        const projectNames = []
        const bugCounts = []
        const reqCounts = []

        for (const p of projectStats) {
          projects.push({
            project_name: p.project_name,
            status: 'active',
            total_tasks: 0,
            completed_tasks: 0,
            task_completion_rate: 0,
            total_bugs: p.bug_count,
            resolved_bugs: 0,
            bug_resolution_rate: 0
          })
          projectNames.push(p.project_name)
          bugCounts.push(p.bug_count)
        }

        const reqTotal = reqData.total_requirements || 0
        const reqCompleted = reqData.completed_requirements || 0

        kpiData.value = {
          totalProjects: projects.length,
          activeProjects: projects.filter(p => p.status === 'active').length,
          totalTasks: reqTotal,
          totalBugs: projectStats.reduce((sum, p) => sum + p.bug_count, 0)
        }

        projectList.value = projects

        nextTick(() => {
          initBugDistributionChart(projectNames, bugCounts)
          initRequirementChart(projectNames, reqCounts)
          initTrendChart(projectData.project_bug_trends || {})
        })

      } catch (error) {
        console.error('加载项目统计数据失败:', error)
        ElMessage.error('加载统计数据失败')
      } finally {
        loading.value = false
      }
    }

    const initBugDistributionChart = (projectNames, bugCounts) => {
      if (!bugDistributionChart.value) return
      
      if (bugChartInstance) {
        bugChartInstance.dispose()
      }
      
      bugChartInstance = echarts.init(bugDistributionChart.value)
      const option = {
        tooltip: { 
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: 'rgba(102, 126, 234, 0.2)',
          borderWidth: 1,
          textStyle: { color: '#1f2937' },
          padding: [12, 16],
          extraCssText: 'box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15); border-radius: 12px;'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '5%',
          containLabel: true
        },
        xAxis: { 
          type: 'category', 
          data: projectNames, 
          axisLabel: { rotate: 45, color: '#64748b', fontSize: 11 },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        yAxis: { 
          type: 'value', 
          name: 'Bug数量',
          nameTextStyle: { color: '#64748b' },
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } },
          axisLabel: { color: '#64748b', fontSize: 11 }
        },
        series: [{
          name: 'Bug数量',
          type: 'bar',
          data: bugCounts,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#ff6b6b' },
              { offset: 1, color: '#ee5a6f' }
            ]),
            borderRadius: [8, 8, 0, 0]
          },
          barWidth: '50%'
        }]
      }
      bugChartInstance.setOption(option)
    }

    const initRequirementChart = (projectNames, reqCounts) => {
      if (!taskChart.value) return

      if (taskChartInstance) {
        taskChartInstance.dispose()
      }

      taskChartInstance = echarts.init(taskChart.value)
      const option = {
        tooltip: { 
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: 'rgba(102, 126, 234, 0.2)',
          borderWidth: 1,
          textStyle: { color: '#1f2937' },
          padding: [12, 16],
          extraCssText: 'box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15); border-radius: 12px;'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '5%',
          containLabel: true
        },
        xAxis: { 
          type: 'category', 
          data: projectNames, 
          axisLabel: { rotate: 45, color: '#64748b', fontSize: 11 },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        yAxis: { 
          type: 'value', 
          name: '需求数量',
          nameTextStyle: { color: '#64748b' },
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } },
          axisLabel: { color: '#64748b', fontSize: 11 }
        },
        series: [
          {
            name: '需求数量',
            type: 'bar',
            data: reqCounts,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#667eea' },
                { offset: 1, color: '#764ba2' }
              ]),
              borderRadius: [8, 8, 0, 0]
            },
            barWidth: '50%'
          }
        ]
      }
      taskChartInstance.setOption(option)
    }

    const initTrendChart = (bugTrends) => {
      if (!trendChart.value) return
      
      if (trendChartInstance) {
        trendChartInstance.dispose()
      }
      
      trendChartInstance = echarts.init(trendChart.value)
      
      const dates = []
      if (Object.keys(bugTrends).length > 0) {
        const firstProject = Object.values(bugTrends)[0]
        if (firstProject && firstProject.length > 0) {
          for (const item of firstProject) {
            dates.push(item.date)
          }
        }
      }
      
      const series = []
      const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#fa709a', '#fee140', '#43e97b', '#4facfe']
      let colorIndex = 0
      
      for (const [projectName, trendData] of Object.entries(bugTrends)) {
        series.push({
          name: projectName,
          type: 'line',
          data: trendData.map(t => t.new_bugs),
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { 
            width: 3,
            color: colors[colorIndex % colors.length],
            shadowColor: colors[colorIndex % colors.length] + '40',
            shadowBlur: 10
          },
          itemStyle: { color: colors[colorIndex % colors.length] }
        })
        colorIndex++
      }
      
      const option = {
        tooltip: { 
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: 'rgba(102, 126, 234, 0.2)',
          borderWidth: 1,
          textStyle: { color: '#1f2937' },
          padding: [12, 16],
          extraCssText: 'box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15); border-radius: 12px;'
        },
        legend: { 
          type: 'scroll', 
          bottom: 0,
          textStyle: { color: '#64748b', fontSize: 11 }
        },
        grid: { 
          bottom: 80,
          left: '3%',
          right: '4%',
          top: '5%',
          containLabel: true
        },
        xAxis: { 
          type: 'category', 
          data: dates, 
          boundaryGap: false,
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisLabel: { color: '#64748b', fontSize: 11 },
          axisTick: { show: false }
        },
        yAxis: { 
          type: 'value', 
          name: '新增Bug数',
          nameTextStyle: { color: '#64748b' },
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } },
          axisLabel: { color: '#64748b', fontSize: 11 }
        },
        series: series
      }
      trendChartInstance.setOption(option)
    }

    const refreshData = () => {
      loadData()
      ElMessage.success('数据已刷新')
    }

    onMounted(() => {
      loadData()
      
      window.addEventListener('resize', () => {
        bugChartInstance?.resize()
        taskChartInstance?.resize()
        trendChartInstance?.resize()
      })
    })

    return {
      loading,
      kpiData,
      projectList,
      bugDistributionChart,
      taskChart,
      trendChart,
      getStatusType,
      getProgressColor,
      refreshData
    }
  }
}
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.project-statistics {
  padding: 24px;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 50%, #eef1f5 100%);
  min-height: 100%;
}

.statistics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: var(--gradient-dark);
  border-radius: 20px;
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(26, 26, 46, 0.3);
}

.statistics-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at 30% 20%, rgba(102, 126, 234, 0.4) 0%, transparent 50%),
              radial-gradient(ellipse at 70% 80%, rgba(240, 147, 251, 0.3) 0%, transparent 50%);
  pointer-events: none;
  animation: aurora 15s ease infinite;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 1;
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
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.title-icon .el-icon {
  font-size: 32px;
  color: #a5b4fc;
}

.title-content h2 {
  margin: 0 0 6px 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.title-content p {
  margin: 0;
  font-size: 15px;
  opacity: 0.85;
  font-weight: 400;
}

.header-actions {
  display: flex;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.25);
  color: white;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.35);
  transform: translateY(-2px);
}

/* KPI 统计卡片 - 美学设计 */
.kpi-cards {
  margin-bottom: 24px;
}

.kpi-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
  animation: fadeInUp 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
  animation-delay: calc(var(--index, 0) * 100ms);
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  transform: scaleX(0);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.kpi-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.06) 0%, transparent 70%);
  pointer-events: none;
}

.kpi-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1);
}

.kpi-card:hover::before {
  transform: scaleX(1);
}

.kpi-card-total::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.kpi-card-active::before { background: linear-gradient(90deg, #43e97b, #38f9d7); }
.kpi-card-tasks::before { background: linear-gradient(90deg, #4facfe, #00f2fe); }
.kpi-card-bugs::before { background: linear-gradient(90deg, #ff6b6b, #ee5a6f); }

.kpi-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.kpi-icon-wrapper::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, transparent 100%);
}

.kpi-card:hover .kpi-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.kpi-icon-wrapper .el-icon {
  font-size: 28px;
  position: relative;
  z-index: 1;
}

.kpi-icon-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #667eea;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
}

.kpi-icon-active {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 16px rgba(67, 233, 123, 0.25);
}

.kpi-icon-tasks {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
  box-shadow: 0 4px 16px rgba(79, 172, 254, 0.25);
}

.kpi-icon-bugs {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 16px rgba(255, 107, 107, 0.25);
}

.kpi-content {
  flex: 1;
  min-width: 0;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: -0.02em;
}

.kpi-value.success {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.kpi-value.info {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.kpi-value.danger {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.kpi-number {
  font-variant-numeric: tabular-nums;
}

.kpi-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 6px;
  font-weight: 500;
}

.kpi-decoration {
  position: absolute;
  top: 50%;
  right: -30px;
  transform: translateY(-50%);
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.08) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s;
  pointer-events: none;
}

.kpi-card:hover .kpi-decoration {
  opacity: 1;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 12px 40px rgba(31, 38, 135, 0.12);
  transform: translateY(-2px);
}

.chart-section {
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
  font-weight: 600;
  color: #1f2937;
  font-size: 16px;
}

.chart-title .el-icon {
  color: #667eea;
  font-size: 20px;
}

.chart-container {
  width: 100%;
}

/* 数据表格 */
.data-table-card {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #1f2937;
  font-size: 16px;
}

.table-title .el-icon {
  color: #667eea;
  font-size: 20px;
}

.custom-table :deep(.el-table__header) {
  background: rgba(241, 245, 249, 0.6);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) {
  background: rgba(102, 126, 234, 0.04);
}

.status-tag {
  font-weight: 500;
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

@keyframes aurora {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-fade-in-down {
  animation: fadeInDown 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation-fill-mode: both;
}

.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }
.delay-400 { animation-delay: 400ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .project-statistics {
    padding: 16px;
  }

  .statistics-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
    padding: 20px 24px;
  }

  .header-title {
    gap: 16px;
  }

  .title-icon {
    width: 52px;
    height: 52px;
  }

  .title-icon .el-icon {
    font-size: 26px;
  }

  .title-content h2 {
    font-size: 22px;
  }

  .title-content p {
    font-size: 13px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    flex: 1;
  }

  .kpi-card {
    padding: 18px;
    gap: 12px;
    margin-bottom: 12px;
  }

  .kpi-icon-wrapper {
    width: 48px;
    height: 48px;
  }

  .kpi-icon-wrapper .el-icon {
    font-size: 24px;
  }

  .kpi-value {
    font-size: 24px;
  }

  .kpi-label {
    font-size: 12px;
  }

  .chart-container {
    height: 300px !important;
  }

  .chart-section .el-col {
    margin-bottom: 16px;
  }

  .chart-section .el-col:last-child {
    margin-bottom: 0;
  }
}

@media screen and (max-width: 480px) {
  .statistics-header {
    padding: 16px 20px;
  }

  .kpi-value {
    font-size: 22px;
  }

  .chart-container {
    height: 250px !important;
  }
}
</style>