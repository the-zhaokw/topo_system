<template>
  <div class="project-statistics">
    <div class="statistics-header">
      <h2>项目统计看板</h2>
      <div class="header-actions">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <el-card class="kpi-card" shadow="never">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="kpi-item">
            <div class="kpi-value">{{ kpiData.totalProjects || 0 }}</div>
            <div class="kpi-label">项目总数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="kpi-item">
            <div class="kpi-value success">{{ kpiData.activeProjects || 0 }}</div>
            <div class="kpi-label">进行中项目</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="kpi-item">
            <div class="kpi-value">{{ kpiData.totalTasks || 0 }}</div>
            <div class="kpi-label">任务总数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="kpi-item">
            <div class="kpi-value">{{ kpiData.totalBugs || 0 }}</div>
            <div class="kpi-label">缺陷总数</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>项目Bug分布</span>
            </div>
          </template>
          <div ref="bugDistributionChart" style="height: 400px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>项目任务统计</span>
            </div>
          </template>
          <div ref="taskChart" style="height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" style="margin-top: 16px;">
      <template #header>
        <div class="card-header">
          <span>项目详情列表</span>
        </div>
      </template>
      <el-table :data="projectList" v-loading="loading">
        <el-table-column prop="project_name" label="项目名称" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_tasks" label="任务总数" />
        <el-table-column prop="completed_tasks" label="已完成任务" />
        <el-table-column prop="task_completion_rate" label="任务完成率">
          <template #default="{ row }">
            <el-progress :percentage="row.task_completion_rate || 0" :color="getProgressColor(row.task_completion_rate)" />
          </template>
        </el-table-column>
        <el-table-column prop="total_bugs" label="缺陷总数" />
        <el-table-column prop="resolved_bugs" label="已解决缺陷" />
        <el-table-column prop="bug_resolution_rate" label="缺陷解决率">
          <template #default="{ row }">
            <el-progress :percentage="row.bug_resolution_rate || 0" :color="getProgressColor(row.bug_resolution_rate)" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px;">
      <template #header>
        <div class="card-header">
          <span>项目Bug趋势（最近30天）</span>
        </div>
      </template>
      <div ref="trendChart" style="height: 350px;"></div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { apiService } from '@/services/api'

export default {
  name: 'ProjectStatistics',
  components: { Refresh },
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
      if (percentage >= 80) return '#67c23a'
      if (percentage >= 50) return '#e6a23c'
      return '#f56c6c'
    }

    const loadData = async () => {
      loading.value = true
      try {
        const [projectRes, taskRes] = await Promise.all([
          apiService.statistics.getProjectStatistics(),
          apiService.statistics.getTaskStatistics()
        ])

        const projectData = projectRes || {}
        const taskData = taskRes || {}

        const projectStats = projectData.project_bug_distribution || []
        const projects = []
        const projectNames = []
        const bugCounts = []
        const taskCounts = []
        
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

        const taskTotal = taskData.total_tasks || 0
        const taskCompleted = taskData.completed_tasks || 0

        kpiData.value = {
          totalProjects: projects.length,
          activeProjects: projects.filter(p => p.status === 'active').length,
          totalTasks: taskTotal,
          totalBugs: projectStats.reduce((sum, p) => sum + p.bug_count, 0)
        }

        projectList.value = projects
        projectNames.value = projectNames

        nextTick(() => {
          initBugDistributionChart(projectNames, bugCounts)
          initTaskChart(projectNames, taskCounts)
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
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: projectNames, axisLabel: { rotate: 45 } },
        yAxis: { type: 'value', name: 'Bug数量' },
        series: [{
          name: 'Bug数量',
          type: 'bar',
          data: bugCounts,
          itemStyle: { color: '#f56c6c' }
        }]
      }
      bugChartInstance.setOption(option)
    }

    const initTaskChart = (projectNames, taskCounts) => {
      if (!taskChart.value) return
      
      if (taskChartInstance) {
        taskChartInstance.dispose()
      }
      
      taskChartInstance = echarts.init(taskChart.value)
      const option = {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: projectNames, axisLabel: { rotate: 45 } },
        yAxis: { type: 'value', name: '任务数量' },
        series: [
          {
            name: '任务数量',
            type: 'bar',
            data: taskCounts,
            itemStyle: { color: '#409eff' }
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
      const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#c71585', '#00ced1', '#ff6347']
      let colorIndex = 0
      
      for (const [projectName, trendData] of Object.entries(bugTrends)) {
        series.push({
          name: projectName,
          type: 'line',
          data: trendData.map(t => t.new_bugs),
          smooth: true,
          itemStyle: { color: colors[colorIndex % colors.length] }
        })
        colorIndex++
      }
      
      const option = {
        tooltip: { trigger: 'axis' },
        legend: { type: 'scroll', bottom: 0 },
        xAxis: { type: 'category', data: dates, boundaryGap: false },
        yAxis: { type: 'value', name: '新增Bug数' },
        grid: { bottom: 80 },
        series: series
      }
      trendChartInstance.setOption(option)
    }

    const refreshData = () => {
      loadData()
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
.project-statistics {
  padding: 20px;
}

.statistics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.statistics-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.kpi-card {
  margin-bottom: 16px;
}

.kpi-item {
  text-align: center;
  padding: 20px;
}

.kpi-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.kpi-value.success {
  color: #67c23a;
}

.kpi-value.danger {
  color: #f56c6c;
}

.kpi-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.card-header {
  font-size: 16px;
  font-weight: 500;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .project-statistics {
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

  .el-table {
    font-size: 11px !important;
  }

  .pagination-container {
    justify-content: center;
    margin-top: 16px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .project-statistics {
    padding: 8px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>
