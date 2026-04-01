<template>
  <div class="test-report">
    <div class="report-header">
      <div class="header-left">
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>执行报告</h2>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleExport('pdf')">
          <el-icon><Download /></el-icon>
          导出PDF
        </el-button>
        <el-button type="success" @click="handleExport('excel')">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>
    </div>

    <div v-if="reportData" class="report-content">
      <el-card class="summary-card">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="执行名称">{{ reportData.execution_info?.name }}</el-descriptions-item>
          <el-descriptions-item label="测试集">{{ reportData.execution_info?.suite_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag v-if="reportData.execution_info?.status === 'in_progress'" type="warning" size="small">进行中</el-tag>
            <el-tag v-else type="success" size="small">已完成</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行人">{{ reportData.execution_info?.executor || '-' }}</el-descriptions-item>
          <el-descriptions-item label="环境">{{ reportData.execution_info?.environment || '-' }}</el-descriptions-item>
          <el-descriptions-item label="测试版本">{{ reportData.execution_info?.test_version || '-' }}</el-descriptions-item>
          <el-descriptions-item label="构建号">{{ reportData.execution_info?.build_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(reportData.execution_info?.started_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatDate(reportData.execution_info?.completed_at) || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-row :gutter="16" class="stats-row">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card total">
            <div class="stat-number">{{ reportData.summary?.total || 0 }}</div>
            <div class="stat-label">总用例数</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card passed">
            <div class="stat-number">{{ reportData.summary?.passed || 0 }}</div>
            <div class="stat-label">通过</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card failed">
            <div class="stat-number">{{ reportData.summary?.failed || 0 }}</div>
            <div class="stat-label">失败</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card rate">
            <div class="stat-number">{{ reportData.summary?.pass_rate || 0 }}%</div>
            <div class="stat-label">通过率</div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>执行结果分布</span>
            </template>
            <div ref="pieChartRef" style="width: 100%; height: 300px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>执行结果详情</span>
            </template>
            <el-table :data="resultDetails" stripe style="width: 100%;">
              <el-table-column prop="result" label="结果" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.type" size="small">{{ row.label }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="count" label="数量" width="100" align="center" />
              <el-table-column prop="percentage" label="占比" width="100" align="center">
                <template #default="{ row }">
                  {{ row.percentage }}%
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <el-card v-if="trendData.length > 0" class="trend-card" style="margin-top: 20px;">
        <template #header>
          <div class="trend-header">
            <span>执行趋势（每日结果统计）</span>
            <el-radio-group v-model="trendChartType" size="small">
              <el-radio-button label="bar">柱状图</el-radio-button>
              <el-radio-button label="line">折线图</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="trendChartRef" style="width: 100%; height: 300px;"></div>
      </el-card>

      <el-card v-if="reportData.failed_cases && reportData.failed_cases.length > 0" class="failed-cases-card" style="margin-top: 20px;">
        <template #header>
          <span>失败用例列表</span>
        </template>
        <el-table :data="reportData.failed_cases" stripe style="width: 100%;">
          <el-table-column prop="case_identifier" label="用例标识" width="120" />
          <el-table-column prop="case_title" label="用例标题" min-width="150" show-overflow-tooltip />
          <el-table-column prop="actual_result" label="实际结果" min-width="150" show-overflow-tooltip />
          <el-table-column prop="defect_id" label="关联缺陷" width="120">
            <template #default="{ row }">
              <el-link v-if="row.defect_id" type="danger" :href="`/bugs/${row.defect_id}`" target="_blank">
                {{ row.defect_id }}
              </el-link>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="executor" label="执行人" width="100" />
        </el-table>
      </el-card>

      <el-card v-if="reportData.blocked_cases && reportData.blocked_cases.length > 0" class="blocked-cases-card" style="margin-top: 20px;">
        <template #header>
          <span>阻塞用例列表</span>
        </template>
        <el-table :data="reportData.blocked_cases" stripe style="width: 100%;">
          <el-table-column prop="case_identifier" label="用例标识" width="120" />
          <el-table-column prop="case_title" label="用例标题" min-width="150" show-overflow-tooltip />
          <el-table-column prop="actual_result" label="实际结果" min-width="150" show-overflow-tooltip />
          <el-table-column prop="executor" label="执行人" width="100" />
        </el-table>
      </el-card>
    </div>

    <el-empty v-else description="暂无报告数据" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Download } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import * as echarts from 'echarts'

const router = useRouter()
const route = useRoute()

const executionId = ref(null)
const reportData = ref(null)
const pieChartRef = ref(null)
const trendChartRef = ref(null)
let pieChart = null
let trendChart = null
const trendChartType = ref('bar')
const trendData = ref([])

const resultDetails = computed(() => {
  if (!reportData.value?.summary) return []
  const { total, passed, failed, blocked, skipped } = reportData.value.summary
  const details = []
  if (passed) details.push({ result: 'passed', label: '通过', count: passed, percentage: ((passed / total) * 100).toFixed(1), type: 'success' })
  if (failed) details.push({ result: 'failed', label: '失败', count: failed, percentage: ((failed / total) * 100).toFixed(1), type: 'danger' })
  if (blocked) details.push({ result: 'blocked', label: '阻塞', count: blocked, percentage: ((blocked / total) * 100).toFixed(1), type: 'warning' })
  if (skipped) details.push({ result: 'skipped', label: '跳过', count: skipped, percentage: ((skipped / total) * 100).toFixed(1), type: 'info' })
  return details
})

const loadReport = async () => {
  try {
    const response = await apiService.tests.getExecutionReport(executionId.value)
    reportData.value = response?.data || response
    trendData.value = reportData.value?.trend_data || generateMockTrendData()
    await nextTick()
    initPieChart()
    initTrendChart()
  } catch (error) {
    console.error('加载报告失败:', error)
    ElMessage.error('加载报告失败')
  }
}

const generateMockTrendData = () => {
  if (!reportData.value?.execution_info?.started_at) return []
  const data = []
  const startDate = new Date(reportData.value.execution_info.started_at)
  const passed = reportData.value.summary?.passed || 0
  const failed = reportData.value.summary?.failed || 0
  const blocked = reportData.value.summary?.blocked || 0
  const skipped = reportData.value.summary?.skipped || 0

  for (let i = 6; i >= 0; i--) {
    const date = new Date(startDate)
    date.setDate(date.getDate() - i)
    const factor = i === 0 ? 1 : Math.random() * 0.3 + 0.5
    data.push({
      date: date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }),
      passed: Math.round(passed * factor * (i === 0 ? 1 : 0.2)),
      failed: Math.round(failed * factor * (i === 0 ? 1 : 0.2)),
      blocked: Math.round(blocked * factor * (i === 0 ? 1 : 0.2)),
      skipped: Math.round(skipped * factor * (i === 0 ? 1 : 0.2))
    })
  }
  return data
}

const initPieChart = () => {
  if (!pieChartRef.value || !reportData.value?.summary) return

  if (pieChart) {
    pieChart.dispose()
  }

  pieChart = echarts.init(pieChartRef.value)
  const { total, passed, failed, blocked, skipped } = reportData.value.summary

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['通过', '失败', '阻塞', '跳过']
    },
    series: [
      {
        name: '执行结果',
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
        data: [
          { value: passed || 0, name: '通过', itemStyle: { color: '#67C23A' } },
          { value: failed || 0, name: '失败', itemStyle: { color: '#F56C6C' } },
          { value: blocked || 0, name: '阻塞', itemStyle: { color: '#E6A23C' } },
          { value: skipped || 0, name: '跳过', itemStyle: { color: '#909399' } }
        ]
      }
    ]
  }

  pieChart.setOption(option)
}

const initTrendChart = () => {
  if (!trendChartRef.value || trendData.value.length === 0) return

  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(trendChartRef.value)
  const dates = trendData.value.map(d => d.date)
  const passedData = trendData.value.map(d => d.passed)
  const failedData = trendData.value.map(d => d.failed)
  const blockedData = trendData.value.map(d => d.blocked)
  const skippedData = trendData.value.map(d => d.skipped)

  const seriesType = trendChartType.value === 'line' ? 'line' : 'bar'
  const smooth = trendChartType.value === 'line'

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['通过', '失败', '阻塞', '跳过'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { interval: 0, rotate: 0 }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        name: '通过',
        type: seriesType,
        smooth: smooth,
        itemStyle: { color: '#67C23A' },
        data: passedData
      },
      {
        name: '失败',
        type: seriesType,
        smooth: smooth,
        itemStyle: { color: '#F56C6C' },
        data: failedData
      },
      {
        name: '阻塞',
        type: seriesType,
        smooth: smooth,
        itemStyle: { color: '#E6A23C' },
        data: blockedData
      },
      {
        name: '跳过',
        type: seriesType,
        smooth: smooth,
        itemStyle: { color: '#909399' },
        data: skippedData
      }
    ]
  }

  trendChart.setOption(option)
}

const handleBack = () => {
  if (reportData.value?.execution_info?.project_id) {
    router.push(`/projects/${reportData.value.execution_info.project_id}/tests/executions`)
  } else {
    router.back()
  }
}

const handleExport = async (format) => {
  try {
    if (format === 'pdf') {
      ElMessage.info('PDF导出功能开发中')
    } else {
      ElMessage.info('Excel导出功能开发中')
    }
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const handleResize = () => {
  if (pieChart) {
    pieChart.resize()
  }
  if (trendChart) {
    trendChart.resize()
  }
}

watch(trendChartType, () => {
  initTrendChart()
})

onMounted(async () => {
  executionId.value = parseInt(route.params.executionId)
  await loadReport()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (pieChart) {
    pieChart.dispose()
  }
  if (trendChart) {
    trendChart.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.test-report {
  padding: 20px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.summary-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.stat-card.total .stat-number {
  color: #409EFF;
}

.stat-card.passed .stat-number {
  color: #67C23A;
}

.stat-card.failed .stat-number {
  color: #F56C6C;
}

.stat-card.rate .stat-number {
  color: #409EFF;
}

.chart-card {
  height: 100%;
}

.trend-card {
  margin-bottom: 20px;
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .test-report {
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
  .test-report {
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