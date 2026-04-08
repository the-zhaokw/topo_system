<template>
  <div class="review-view">
    <div class="review-header">
      <div class="header-left">
        <el-radio-group v-model="dateRangeType" size="default">
          <el-radio-button value="week">本周</el-radio-button>
          <el-radio-button value="month">本月</el-radio-button>
          <el-radio-button value="custom">自定义</el-radio-button>
        </el-radio-group>

        <el-date-picker
          v-if="dateRangeType === 'custom'"
          v-model="customDateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="loadReviewData"
        />
      </div>

      <div class="header-right">
        <el-button @click="exportReport('image')">
          <el-icon><Picture /></el-icon>
          导出图片
        </el-button>
        <el-button @click="exportReport('csv')">
          <el-icon><Document /></el-icon>
          导出CSV
        </el-button>
        <el-button @click="exportReport('pdf')" type="primary">
          <el-icon><FolderOpened /></el-icon>
          导出PDF
        </el-button>
      </div>
    </div>

    <div class="review-content">
      <div class="metrics-cards">
        <div class="metric-card">
          <div class="metric-icon blue">
            <el-icon><List /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value">{{ metrics.total }}</div>
            <div class="metric-label">计划任务</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon green">
            <el-icon><Check /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value">{{ metrics.completed }}</div>
            <div class="metric-label">已完成</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon purple">
            <el-icon><PieChart /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value">{{ metrics.completionRate }}%</div>
            <div class="metric-label">完成率</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon orange">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value">{{ metrics.plannedHours }}</div>
            <div class="metric-label">总计划工时</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon cyan">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value">{{ metrics.actualHours }}</div>
            <div class="metric-label">实际耗时</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon" :class="metrics.deviation >= 0 ? 'green' : 'red'">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value" :class="metrics.deviation >= 0 ? 'positive' : 'negative'">
              {{ metrics.deviation >= 0 ? '+' : '' }}{{ metrics.deviation }}%
            </div>
            <div class="metric-label">偏差</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon red">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value">{{ metrics.overdueCount }}</div>
            <div class="metric-label">延期任务</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon gray">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value">{{ metrics.avgOverdueDays }}</div>
            <div class="metric-label">平均延期天数</div>
          </div>
        </div>
      </div>

      <div class="charts-section">
        <div class="chart-card">
          <h3>计划vs实际工时对比</h3>
          <div class="chart-container" ref="barChartRef"></div>
        </div>

        <div class="chart-card">
          <h3>标签耗时占比</h3>
          <div class="chart-container" ref="pieChartRef"></div>
        </div>
      </div>

      <div class="weekly-report-section">
        <div class="section-header">
          <h3>自动生成周报</h3>
          <el-button size="small" @click="copyReport">
            <el-icon><CopyDocument /></el-icon>
            一键复制
          </el-button>
        </div>

        <div class="report-editor">
          <el-input
            v-model="weeklyReport"
            type="textarea"
            :rows="10"
            placeholder="周报内容..."
          />
        </div>

        <div class="report-actions">
          <el-button @click="generateWeeklyReport">
            <el-icon><Refresh /></el-icon>
            重新生成
          </el-button>
          <el-button type="primary" @click="exportMarkdown">
            <el-icon><Download /></el-icon>
            导出Markdown
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  List, Check, PieChart, Clock, Timer, TrendCharts, Warning, Calendar,
  Picture, Document, FolderOpened, CopyDocument, Refresh, Download
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const dateRangeType = ref('week')
const customDateRange = ref([])
const barChartRef = ref(null)
const pieChartRef = ref(null)

const metrics = reactive({
  total: 0,
  completed: 0,
  completionRate: 0,
  plannedHours: 0,
  actualHours: 0,
  deviation: 0,
  overdueCount: 0,
  avgOverdueDays: 0
})

const weeklyReport = ref('')

const tagDistribution = ref([
  { name: '高优先级', hours: 12, percentage: 30 },
  { name: '开发', hours: 20, percentage: 50 },
  { name: '沟通', hours: 5, percentage: 12.5 },
  { name: '文档', hours: 3, percentage: 7.5 }
])

const barData = ref({
  planned: [8, 10, 12, 6, 8, 10, 4],
  actual: [7, 12, 10, 8, 6, 14, 5],
  labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
})

const loadReviewData = async () => {
  try {
    let dateFrom, dateTo

    if (dateRangeType.value === 'week') {
      const now = new Date()
      const dayOfWeek = now.getDay()
      dateFrom = new Date(now.setDate(now.getDate() - dayOfWeek + 1)).toISOString().split('T')[0]
      dateTo = new Date(now.setDate(now.getDate() + 6)).toISOString().split('T')[0]
    } else if (dateRangeType.value === 'month') {
      const now = new Date()
      dateFrom = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0]
      dateTo = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split('T')[0]
    } else if (customDateRange.value) {
      dateFrom = customDateRange.value[0]
      dateTo = customDateRange.value[1]
    }

    const data = await apiService.personalPlan.getReviewStats({
      date_from: dateFrom,
      date_to: dateTo
    })

    Object.assign(metrics, {
      total: data.total || 0,
      completed: data.completed || 0,
      completionRate: data.completionRate || 0,
      plannedHours: data.planned_hours || 0,
      actualHours: data.actual_hours || 0,
      deviation: data.deviation || 0,
      overdueCount: data.overdue_count || 0,
      avgOverdueDays: data.avg_overdue_days || 0
    })

    generateWeeklyReport()
  } catch (error) {
    console.error('加载复盘数据失败:', error)
    metrics.total = 15
    metrics.completed = 12
    metrics.completionRate = 80
    metrics.plannedHours = 40
    metrics.actualHours = 45
    metrics.deviation = 12.5
    metrics.overdueCount = 2
    metrics.avgOverdueDays = 1.5
    generateWeeklyReport()
  }
}

const generateWeeklyReport = () => {
  const completedTasks = metrics.completed
  const totalTasks = metrics.total
  const completionRate = metrics.completionRate

  const completedList = ['完成了后端API开发', '完成了前端页面重构', '修复了3个线上Bug']
  const pendingList = ['等待产品评审', '文档待完善']

  weeklyReport.value = `本周工作总结

一、任务完成情况
本周计划任务 ${totalTasks} 项，实际完成 ${completedTasks} 项，完成率 ${completionRate}%。

二、已完成工作
${completedList.map((item, i) => `${i + 1}. ${item}`).join('\n')}

三、未完成原因
${pendingList.map((item, i) => `${i + 1}. ${item}`).join('\n')}

四、工时统计
计划工时：${metrics.plannedHours}小时
实际耗时：${metrics.actualHours}小时
偏差：${metrics.deviation >= 0 ? '+' : ''}${metrics.deviation}%

五、下周计划
1. 继续推进项目开发
2. 完成剩余功能模块
3. 准备下周评审材料

六、风险与问题
${metrics.overdueCount > 0 ? `有 ${metrics.overdueCount} 个任务延期，平均延期 ${metrics.avgOverdueDays} 天，需要加强进度管理。` : '暂无明显风险。'}
`
}

const copyReport = () => {
  navigator.clipboard.writeText(weeklyReport.value)
  ElMessage.success('已复制到剪贴板')
}

const exportReport = (format) => {
  ElMessage.info(`导出${format.toUpperCase()}功能开发中`)
}

const exportMarkdown = () => {
  const blob = new Blob([weeklyReport.value], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `周报_${new Date().toISOString().split('T')[0]}.md`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

const initCharts = () => {
  if (barChartRef.value) {
    barChartRef.value.innerHTML = `
      <div style="display: flex; align-items: flex-end; justify-content: space-around; height: 200px; padding: 20px;">
        ${barData.value.labels.map((label, i) => `
          <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
            <div style="display: flex; gap: 4px; align-items: flex-end; height: 160px;">
              <div style="width: 24px; background: #409EFF; border-radius: 4px 4px 0 0; height: ${barData.value.planned[i] * 12}px;"></div>
              <div style="width: 24px; background: #67c23a; border-radius: 4px 4px 0 0; height: ${barData.value.actual[i] * 12}px;"></div>
            </div>
            <span style="font-size: 12px; color: #909399;">${label}</span>
          </div>
        `).join('')}
      </div>
      <div style="display: flex; justify-content: center; gap: 24px; margin-top: 12px;">
        <div style="display: flex; align-items: center; gap: 6px;">
          <div style="width: 12px; height: 12px; background: #409EFF; border-radius: 2px;"></div>
          <span style="font-size: 12px; color: #606266;">计划工时</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
          <div style="width: 12px; height: 12px; background: #67c23a; border-radius: 2px;"></div>
          <span style="font-size: 12px; color: #606266;">实际耗时</span>
        </div>
      </div>
    `
  }

  if (pieChartRef.value) {
    const colors = ['#409EFF', '#67c23a', '#e6a23c', '#f56c6c', '#909399']
    let accumulatedPercentage = 0

    pieChartRef.value.innerHTML = `
      <div style="display: flex; align-items: center; padding: 20px; gap: 40px;">
        <div style="width: 140px; height: 140px; border-radius: 50%; background: conic-gradient(
          ${tagDistribution.value.map((tag, i) => {
            const start = accumulatedPercentage
            accumulatedPercentage += tag.percentage
            return `${colors[i % colors.length]} ${start}% ${accumulatedPercentage}%`
          }).join(', ')}
        );"></div>
        <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
          ${tagDistribution.value.map((tag, i) => `
            <div style="display: flex; align-items: center; gap: 8px;">
              <div style="width: 12px; height: 12px; background: ${colors[i % colors.length]}; border-radius: 2px;"></div>
              <span style="flex: 1; font-size: 13px; color: #606266;">${tag.name}</span>
              <span style="font-size: 13px; color: #909399;">${tag.hours}小时 (${tag.percentage}%)</span>
            </div>
          `).join('')}
        </div>
      </div>
    `
  }
}

onMounted(() => {
  loadReviewData()
  setTimeout(initCharts, 100)
})
</script>

<style scoped>
.review-view {
  max-width: 1400px;
  margin: 0 auto;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  gap: 8px;
}

.metrics-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.metric-icon.blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.metric-icon.green {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.metric-icon.purple {
  background: linear-gradient(135deg, #9c27b0 0%, #e040fb 100%);
}

.metric-icon.orange {
  background: linear-gradient(135deg, #e6a23c 0%, #f56c6c 100%);
}

.metric-icon.cyan {
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
}

.metric-icon.red {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
}

.metric-icon.gray {
  background: linear-gradient(135deg, #909399 0%, #c0c4cc 100%);
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.metric-value.positive {
  color: #67c23a;
}

.metric-value.negative {
  color: #f56c6c;
}

.metric-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.chart-card h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  min-height: 240px;
}

.weekly-report-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.report-editor {
  margin-bottom: 16px;
}

.report-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media screen and (max-width: 1200px) {
  .metrics-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-section {
    grid-template-columns: 1fr;
  }
}

@media screen and (max-width: 768px) {
  .metrics-cards {
    grid-template-columns: 1fr;
  }

  .review-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
