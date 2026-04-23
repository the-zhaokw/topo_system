<template>
  <div class="bug-statistics">
    <div class="statistics-header">
      <h2>Bug统计看板</h2>
      <div class="header-actions">
        <el-dropdown @command="handleExportCommand">
          <el-button type="primary">
            <el-icon><Download /></el-icon>
            导出
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="data">导出数据 (JSON)</el-dropdown-item>
              <el-dropdown-item command="trend">导出趋势图</el-dropdown-item>
              <el-dropdown-item command="distribution">导出分布图</el-dropdown-item>
              <el-dropdown-item command="all">导出所有图表</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <el-card class="filter-panel" shadow="never">
      <div class="filter-row">
        <div class="filter-item">
          <span class="filter-label">时间范围</span>
          <el-select v-model="filters.timeRange" @change="handleTimeRangeChange" style="width: 140px;">
            <el-option label="今日" value="today"></el-option>
            <el-option label="本周" value="week"></el-option>
            <el-option label="本月" value="month"></el-option>
            <el-option label="本季度" value="quarter"></el-option>
            <el-option label="自定义" value="custom"></el-option>
          </el-select>
        </div>
        
        <div class="filter-item" v-if="filters.timeRange === 'custom'">
          <el-date-picker
            v-model="filters.customDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleDateRangeChange"
            style="width: 260px;"
          />
        </div>

        <div class="filter-item">
          <span class="filter-label">所属项目</span>
          <el-select 
            v-model="filters.projectIds" 
            multiple 
            collapse-tags
            collapse-tags-tooltip
            placeholder="全部项目" 
            style="width: 180px;"
            @change="loadAllData"
          >
            <el-option label="全部项目" :value="''" @click="handleSelectAllProjects" />
            <el-option 
              v-for="project in filterOptions.projects" 
              :key="project.id" 
              :label="project.name" 
              :value="project.id"
            />
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">Bug类型</span>
          <el-select 
            v-model="filters.bugTypes" 
            multiple 
            collapse-tags
            placeholder="全部类型"
            style="width: 160px;"
            @change="loadAllData"
          >
            <el-option 
              v-for="type in filterOptions.bugTypes" 
              :key="type" 
              :label="type" 
              :value="type"
            />
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">严重程度</span>
          <el-select 
            v-model="filters.severities" 
            multiple 
            collapse-tags
            placeholder="全部等级"
            style="width: 140px;"
            @change="loadAllData"
          >
            <el-option label="致命(P0)" value="critical"></el-option>
            <el-option label="严重(P1)" value="high"></el-option>
            <el-option label="一般(P2)" value="medium"></el-option>
            <el-option label="轻微(P3)" value="low"></el-option>
            <el-option label="建议(P4)" value="suggestion"></el-option>
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">Bug状态</span>
          <el-select 
            v-model="filters.statuses" 
            multiple 
            collapse-tags
            placeholder="全部状态"
            style="width: 160px;"
            @change="loadAllData"
          >
            <el-option label="新建" value="new"></el-option>
            <el-option label="处理中" value="in_progress"></el-option>
            <el-option label="已解决" value="resolved"></el-option>
            <el-option label="已关闭" value="closed"></el-option>
            <el-option label="已拒绝" value="rejected"></el-option>
            <el-option label="重新打开" value="reopened"></el-option>
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">优先级</span>
          <el-select 
            v-model="filters.priorities" 
            multiple 
            collapse-tags
            placeholder="全部优先"
            style="width: 120px;"
            @change="loadAllData"
          >
            <el-option label="紧急" value="urgent"></el-option>
            <el-option label="高" value="high"></el-option>
            <el-option label="中" value="medium"></el-option>
            <el-option label="低" value="low"></el-option>
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">创建人</span>
          <el-select 
            v-model="filters.reportedBy" 
            multiple 
            collapse-tags
            placeholder="不限"
            style="width: 140px;"
            @change="loadAllData"
          >
            <el-option 
              v-for="user in filterOptions.users" 
              :key="user.id" 
              :label="user.name" 
              :value="user.id"
            />
          </el-select>
        </div>

        <el-button type="warning" text @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon>
          重置
        </el-button>
      </div>
    </el-card>

    <div class="kpi-cards">
      <el-row :gutter="16">
        <el-col :span="4">
          <el-card class="kpi-card" shadow="hover" :class="{ 'warning': kpiData.total_bugs > 1000 }">
            <div class="kpi-content">
              <div class="kpi-value">
                {{ kpiData.total_bugs?.toLocaleString() || 0 }}
                <span class="kpi-change" :class="getChangeClass(kpiData.total_change)">
                  {{ kpiData.total_change > 0 ? '↑' : '↓' }}{{ Math.abs(kpiData.total_change || 0) }}%
                </span>
              </div>
              <div class="kpi-label">总Bug数</div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="4">
          <el-card class="kpi-card" shadow="hover" :class="{ 'danger': kpiData.new_bugs > 20 }">
            <div class="kpi-content">
              <div class="kpi-value">
                {{ kpiData.new_bugs || 0 }}
                <span class="kpi-sub">{{ filters.timeRange === 'today' ? '今日' : '周期内' }}</span>
              </div>
              <div class="kpi-label">新增Bug</div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="4">
          <el-card class="kpi-card" shadow="hover">
            <div class="kpi-content">
              <div class="kpi-value success">{{ kpiData.resolved_bugs || 0 }}</div>
              <div class="kpi-label">已解决</div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="4">
          <el-card class="kpi-card" shadow="hover" :class="{ 'warning': kpiData.unresolved_bugs > 50 }">
            <div class="kpi-content">
              <div class="kpi-value danger">{{ kpiData.unresolved_bugs || 0 }}</div>
              <div class="kpi-label">未解决</div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="4">
          <el-card class="kpi-card" shadow="hover" :class="{ 'warning': kpiData.resolution_rate < 80 }">
            <div class="kpi-content">
              <div class="kpi-value">{{ kpiData.resolution_rate || 0 }}%</div>
              <div class="kpi-label">解决率</div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="4">
          <el-card class="kpi-card" shadow="hover" :class="{ 'danger': kpiData.avg_fix_time > 3 }">
            <div class="kpi-content">
              <div class="kpi-value">
                {{ kpiData.avg_fix_time || 0 }}
                <span class="kpi-unit">天</span>
              </div>
              <div class="kpi-label">平均解决时长</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="chart-section">
      <el-row :gutter="16">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>Bug趋势分析</span>
                <el-radio-group v-model="trendGranularity" size="small" @change="loadTrendData">
                  <el-radio-button label="day">日</el-radio-button>
                  <el-radio-button label="week">周</el-radio-button>
                  <el-radio-button label="month">月</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div ref="trendChartRef" class="chart-container" style="height: 350px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="chart-section">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>项目Bug分布</span>
                <el-select v-model="projectChartDimension" size="small" @change="loadDistributionData" style="width: 120px;">
                  <el-option label="按项目" value="project"></el-option>
                  <el-option label="按严重程度" value="severity"></el-option>
                  <el-option label="按优先级" value="priority"></el-option>
                  <el-option label="按类型" value="type"></el-option>
                  <el-option label="按状态" value="status"></el-option>
                </el-select>
              </div>
            </template>
            <div ref="projectChartRef" class="chart-container" style="height: 320px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>Bug类型占比</span>
              </div>
            </template>
            <div ref="typeChartRef" class="chart-container" style="height: 320px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>存活时长分布</span>
              </div>
            </template>
            <div ref="survivalChartRef" class="chart-container" style="height: 320px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="chart-section">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>严重程度分布</span>
              </div>
            </template>
            <div ref="severityChartRef" class="chart-container" style="height: 300px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>人员工作量分析</span>
              </div>
            </template>
            <div ref="workloadChartRef" class="chart-container" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-card class="data-table-card" shadow="hover">
      <template #header>
        <div class="table-header">
          <span>Bug明细列表</span>
          <el-radio-group v-model="tableView" size="small">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="unresolved">未解决</el-radio-button>
            <el-radio-button label="resolved">已解决</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <el-table 
        :data="bugList" 
        v-loading="tableLoading"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
        :default-sort="{ prop: 'created_at', order: 'descending' }"
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="project_name" label="项目" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">
              {{ getSeverityLabel(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reporter_name" label="创建人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click.stop="viewBugDetail(row)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalBugs"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <div v-if="loading" class="loading-overlay">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <span>数据加载中...</span>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, RefreshLeft, Loading, Download, ArrowDown } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import bugStatisticsService from '@/services/bugStatisticsService'
import { systemTimeService } from '@/services/systemTimeService'

export default {
  name: 'BugStatistics',
  components: { Refresh, RefreshLeft, Loading, Download, ArrowDown },
  setup() {
    const loading = ref(false)
    const trendGranularity = ref('day')
    const projectChartDimension = ref('project')
    
    const filters = reactive({
      timeRange: 'month',
      customDateRange: [],
      projectIds: [],
      bugTypes: [],
      severities: [],
      statuses: [],
      priorities: [],
      reportedBy: []
    })

    const filterOptions = reactive({
      projects: [],
      bugTypes: [],
      severities: [],
      priorities: [],
      statuses: [],
      users: []
    })

    const kpiData = ref({})

    const trendChartRef = ref(null)
    const projectChartRef = ref(null)
    const typeChartRef = ref(null)
    const survivalChartRef = ref(null)
    const severityChartRef = ref(null)
    const workloadChartRef = ref(null)

    const bugList = ref([])
    const tableLoading = ref(false)
    const tableView = ref('all')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalBugs = ref(0)

    let trendChart = null
    let projectChart = null
    let typeChart = null
    let survivalChart = null
    let severityChart = null
    let workloadChart = null

    const getDateRange = () => {
      const now = systemTimeService.getServerTime()
      let startDate, endDate

      endDate = now.toISOString().split('T')[0]

      switch (filters.timeRange) {
        case 'today':
          startDate = endDate
          break
        case 'week':
          startDate = new Date(now.setDate(now.getDate() - 7)).toISOString().split('T')[0]
          break
        case 'month':
          startDate = new Date(now.setMonth(now.getMonth() - 1)).toISOString().split('T')[0]
          break
        case 'quarter':
          startDate = new Date(now.setMonth(now.getMonth() - 3)).toISOString().split('T')[0]
          break
        case 'custom':
          if (filters.customDateRange && filters.customDateRange.length === 2) {
            startDate = filters.customDateRange[0].toISOString().split('T')[0]
            endDate = filters.customDateRange[1].toISOString().split('T')[0]
          } else {
            startDate = new Date(now.setMonth(now.getMonth() - 1)).toISOString().split('T')[0]
          }
          break
        default:
          startDate = new Date(now.setMonth(now.getMonth() - 1)).toISOString().split('T')[0]
      }

      return { startDate, endDate }
    }

    const buildFilterParams = () => {
      const { startDate, endDate } = getDateRange()
      return {
        start_date: startDate,
        end_date: endDate,
        project_ids: filters.projectIds.join(','),
        bug_types: filters.bugTypes.join(','),
        severities: filters.severities.join(','),
        statuses: filters.statuses.join(','),
        priorities: filters.priorities.join(','),
        reported_by: filters.reportedBy.join(',')
      }
    }

    const getChangeClass = (change) => {
      if (change > 0) return 'up'
      if (change < 0) return 'down'
      return 'stable'
    }

    const initCharts = () => {
      nextTick(() => {
        if (trendChartRef.value) {
          trendChart = echarts.init(trendChartRef.value)
        }
        if (projectChartRef.value) {
          projectChart = echarts.init(projectChartRef.value)
        }
        if (typeChartRef.value) {
          typeChart = echarts.init(typeChartRef.value)
        }
        if (survivalChartRef.value) {
          survivalChart = echarts.init(survivalChartRef.value)
        }
        if (severityChartRef.value) {
          severityChart = echarts.init(severityChartRef.value)
        }
        if (workloadChartRef.value) {
          workloadChart = echarts.init(workloadChartRef.value)
        }
        
        window.addEventListener('resize', handleResize)
      })
    }

    const handleResize = () => {
      trendChart?.resize()
      projectChart?.resize()
      typeChart?.resize()
      survivalChart?.resize()
      severityChart?.resize()
      workloadChart?.resize()
    }

    const loadFilterOptions = async () => {
      try {
        const response = await bugStatisticsService.getFilterOptions()
        if (response.success) {
          filterOptions.projects = response.data.projects || []
          filterOptions.bugTypes = response.data.bug_types || []
          filterOptions.severities = response.data.severities || []
          filterOptions.priorities = response.data.priorities || []
          filterOptions.statuses = response.data.statuses || []
          filterOptions.users = response.data.users || []
        }
      } catch (error) {
        console.error('加载筛选选项失败:', error)
      }
    }

    const loadKpiData = async () => {
      try {
        const params = buildFilterParams()
        const response = await bugStatisticsService.getKpiMetrics(params)
        if (response.success) {
          kpiData.value = response.data
        }
      } catch (error) {
        console.error('加载KPI数据失败:', error)
      }
    }

    const loadTrendData = async () => {
      try {
        const params = buildFilterParams()
        params.granularity = trendGranularity.value
        const response = await bugStatisticsService.getTrendAnalysis(params)
        if (response.success) {
          renderTrendChart(response.data.trend_data || [])
        }
      } catch (error) {
        console.error('加载趋势数据失败:', error)
      }
    }

    const renderTrendChart = (data) => {
      if (!trendChart || !data.length) return
      
      const option = {
        tooltip: { trigger: 'axis' },
        legend: { data: ['新增Bug', '解决Bug', '累计未解决'], bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { 
          type: 'category', 
          data: data.map(d => d.date),
          axisLabel: { rotate: trendGranularity.value === 'day' ? 45 : 0 }
        },
        yAxis: { type: 'value' },
        series: [
          {
            name: '新增Bug',
            type: 'line',
            data: data.map(d => d.new_bugs),
            smooth: true,
            itemStyle: { color: '#409EFF' },
            areaStyle: { opacity: 0.1 }
          },
          {
            name: '解决Bug',
            type: 'line',
            data: data.map(d => d.resolved_bugs),
            smooth: true,
            itemStyle: { color: '#67C23A' },
            areaStyle: { opacity: 0.1 }
          },
          {
            name: '累计未解决',
            type: 'line',
            data: data.map(d => d.cumulative_unresolved),
            smooth: true,
            itemStyle: { color: '#F56C6C' },
            areaStyle: { opacity: 0.2, color: '#F56C6C' }
          }
        ]
      }
      
      trendChart.setOption(option)
    }

    const loadDistributionData = async () => {
      try {
        const params = buildFilterParams()
        params.dimension = projectChartDimension.value
        const response = await bugStatisticsService.getDistributionAnalysis(params)
        if (response.success) {
          renderDistributionChart(response.data.dimension, response.data.distribution || {})
        }
      } catch (error) {
        console.error('加载分布数据失败:', error)
      }
    }

    const renderDistributionChart = (dimension, data) => {
      if (!projectChart) return
      
      let chartData = []
      let seriesData = []
      
      if (dimension === 'status') {
        chartData = Object.entries(data).map(([name, value]) => ({ name, value }))
      } else {
        chartData = Object.entries(data).map(([name, stats]) => ({
          name,
          value: stats.total,
          new: stats.new,
          resolved: stats.resolved,
          closed: stats.closed
        }))
      }
      
      const isStacked = dimension !== 'status'
      
      const option = {
        tooltip: { 
          trigger: 'axis',
          formatter: (params) => {
            if (dimension === 'status') {
              const p = params[0]
              return `${p.name}: ${p.value}个 (${p.percentage}%)`
            }
            const p = params[0]
            return `${p.name}<br/>总计: ${p.value}<br/>新建: ${p.data?.new || 0}<br/>已解决: ${p.data?.resolved || 0}<br/>已关闭: ${p.data?.closed || 0}`
          }
        },
        legend: { data: isStacked ? ['新建', '已解决', '已关闭'] : [], bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { 
          type: 'category', 
          data: chartData.map(d => d.name),
          axisLabel: { rotate: 30 }
        },
        yAxis: { type: 'value', name: 'Bug数量' },
        series: isStacked ? [
          {
            name: '新建',
            type: 'bar',
            stack: 'total',
            data: chartData.map(d => d.new || 0),
            itemStyle: { color: '#F56C6C' }
          },
          {
            name: '已解决',
            type: 'bar',
            stack: 'total',
            data: chartData.map(d => d.resolved || 0),
            itemStyle: { color: '#E6A23C' }
          },
          {
            name: '已关闭',
            type: 'bar',
            stack: 'total',
            data: chartData.map(d => d.closed || 0),
            itemStyle: { color: '#67C23A' }
          }
        ] : [
          {
            name: 'Bug状态',
            type: 'pie',
            radius: ['40%', '70%'],
            data: chartData,
            emphasis: {
              itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
            }
          }
        ]
      }
      
      projectChart.setOption(option, true)
    }

    const loadTypeDistribution = async () => {
      try {
        const params = buildFilterParams()
        const response = await bugStatisticsService.getTypeDistribution(params)
        if (response.success) {
          renderTypeChart(response.data.type_distribution || [])
        }
      } catch (error) {
        console.error('加载类型分布失败:', error)
      }
    }

    const renderTypeChart = (data) => {
      if (!typeChart || !data.length) return
      
      const option = {
        tooltip: { 
          trigger: 'item',
          formatter: '{b}: {c}个 ({d}%)'
        },
        legend: { orient: 'vertical', left: 'left', top: 'middle' },
        series: [
          {
            name: 'Bug类型',
            type: 'pie',
            radius: ['40%', '65%'],
            center: ['60%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 8,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: { show: false, position: 'center' },
            emphasis: {
              label: {
                show: true,
                fontSize: 18,
                fontWeight: 'bold'
              }
            },
            labelLine: { show: false },
            data: data.map((d, i) => ({
              name: d.name,
              value: d.value,
              itemStyle: {
                color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#C0C4CC'][i % 6]
              }
            }))
          }
        ]
      }
      
      typeChart.setOption(option)
    }

    const loadSurvivalDuration = async () => {
      try {
        const params = buildFilterParams()
        const response = await bugStatisticsService.getSurvivalDuration(params)
        if (response.success) {
          renderSurvivalChart(response.data.duration_distribution || [], response.data.total_resolved || 0)
        }
      } catch (error) {
        console.error('加载存活时长失败:', error)
      }
    }

    const renderSurvivalChart = (data, total) => {
      if (!survivalChart || !data.length) return
      
      const option = {
        tooltip: { 
          trigger: 'axis',
          formatter: '{b}: {c}个'
        },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { 
          type: 'category', 
          data: data.map(d => d.name),
          axisLabel: { rotate: 15 }
        },
        yAxis: { type: 'value', name: 'Bug数量' },
        series: [
          {
            name: '存活时长',
            type: 'bar',
            data: data.map((d, i) => ({
              value: d.value,
              itemStyle: {
                color: ['#67C23A', '#409EFF', '#E6A23C', '#F56C6C', '#909399'][i % 5]
              }
            })),
            barWidth: '50%'
          }
        ]
      }
      
      survivalChart.setOption(option)
    }

    const loadSeverityDistribution = async () => {
      try {
        const params = buildFilterParams()
        params.dimension = 'severity'
        const response = await bugStatisticsService.getDistributionAnalysis(params)
        if (response.success) {
          renderSeverityChart(response.data.distribution || {})
        }
      } catch (error) {
        console.error('加载严重程度分布失败:', error)
      }
    }

    const renderSeverityChart = (data) => {
      if (!severityChart || !Object.keys(data).length) return
      
      const categories = Object.keys(data)
      const severityLabels = { critical: 'P0-致命', high: 'P1-严重', medium: 'P2-一般', low: 'P3-轻微', suggestion: 'P4-建议' }
      
      const option = {
        tooltip: { 
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        legend: { data: ['新建', '已解决', '已关闭'], bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { 
          type: 'category', 
          data: categories.map(c => severityLabels[c] || c),
          axisLabel: { rotate: 15 }
        },
        yAxis: { type: 'value', name: 'Bug数量' },
        series: [
          {
            name: '新建',
            type: 'bar',
            stack: 'total',
            data: categories.map(c => data[c]?.new || 0),
            itemStyle: { color: '#F56C6C' }
          },
          {
            name: '已解决',
            type: 'bar',
            stack: 'total',
            data: categories.map(c => data[c]?.resolved || 0),
            itemStyle: { color: '#E6A23C' }
          },
          {
            name: '已关闭',
            type: 'bar',
            stack: 'total',
            data: categories.map(c => data[c]?.closed || 0),
            itemStyle: { color: '#67C23A' }
          }
        ]
      }
      
      severityChart.setOption(option)
    }

    const loadWorkloadData = async () => {
      try {
        const params = buildFilterParams()
        const response = await bugStatisticsService.getPersonWorkload(params)
        if (response.success) {
          renderWorkloadChart(response.data.workload_data || [])
        }
      } catch (error) {
        console.error('加载工作量数据失败:', error)
      }
    }

    const renderWorkloadChart = (data) => {
      if (!workloadChart || !data.length) return
      
      const chartData = data.slice(0, 10)
      
      const option = {
        tooltip: { 
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        legend: { data: ['已分配', '处理中', '已解决', '已关闭'], bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { 
          type: 'value', 
          name: 'Bug数量'
        },
        yAxis: { 
          type: 'category', 
          data: chartData.map(d => d.name),
          axisLabel: { rotate: 0 }
        },
        series: [
          {
            name: '已分配',
            type: 'bar',
            stack: 'total',
            data: chartData.map(d => d.assigned - d.in_progress - d.resolved - d.closed),
            itemStyle: { color: '#909399' }
          },
          {
            name: '处理中',
            type: 'bar',
            stack: 'total',
            data: chartData.map(d => d.in_progress),
            itemStyle: { color: '#E6A23C' }
          },
          {
            name: '已解决',
            type: 'bar',
            stack: 'total',
            data: chartData.map(d => d.resolved),
            itemStyle: { color: '#409EFF' }
          },
          {
            name: '已关闭',
            type: 'bar',
            stack: 'total',
            data: chartData.map(d => d.closed),
            itemStyle: { color: '#67C23A' }
          }
        ]
      }
      
      workloadChart.setOption(option)
    }

    const loadAllData = async () => {
      loading.value = true
      try {
        await Promise.all([
          loadKpiData(),
          loadTrendData(),
          loadDistributionData(),
          loadTypeDistribution(),
          loadSurvivalDuration(),
          loadSeverityDistribution(),
          loadWorkloadData()
        ])
      } finally {
        loading.value = false
      }
      loadBugList()
    }

    const loadBugList = async () => {
      tableLoading.value = true
      try {
        const params = buildFilterParams()
        params.page = currentPage.value
        params.per_page = pageSize.value
        
        if (tableView.value === 'unresolved') {
          params.status = 'new,in_progress,assigned'
        } else if (tableView.value === 'resolved') {
          params.status = 'resolved,closed'
        }
        
        const response = await bugStatisticsService.getBugList(params)
        if (response.success) {
          bugList.value = response.data.bugs || []
          totalBugs.value = response.data.total || 0
        }
      } catch (error) {
        console.error('加载Bug列表失败:', error)
      } finally {
        tableLoading.value = false
      }
    }

    const getStatusType = (status) => {
      const types = {
        'new': 'info',
        'assigned': 'warning',
        'in_progress': 'warning',
        'resolved': 'success',
        'verified': 'success',
        'closed': 'success',
        'rejected': 'danger',
        'reopened': 'danger'
      }
      return types[status] || 'info'
    }

    const getStatusLabel = (status) => {
      const labels = {
        'new': '新建',
        'assigned': '已分配',
        'in_progress': '处理中',
        'resolved': '已解决',
        'verified': '已验证',
        'closed': '已关闭',
        'rejected': '已拒绝',
        'reopened': '重新打开'
      }
      return labels[status] || status
    }

    const getSeverityType = (severity) => {
      const types = {
        'critical': 'danger',
        'high': 'warning',
        'medium': '',
        'low': 'info',
        'suggestion': ''
      }
      return types[severity] || 'info'
    }

    const getSeverityLabel = (severity) => {
      const labels = {
        'critical': '致命(P0)',
        'high': '严重(P1)',
        'medium': '一般(P2)',
        'low': '轻微(P3)',
        'suggestion': '建议(P4)'
      }
      return labels[severity] || severity
    }

    const getPriorityType = (priority) => {
      const types = {
        'urgent': 'danger',
        'high': 'warning',
        'medium': '',
        'low': 'info'
      }
      return types[priority] || 'info'
    }

    const getPriorityLabel = (priority) => {
      const labels = {
        'urgent': '紧急',
        'high': '高',
        'medium': '中',
        'low': '低'
      }
      return labels[priority] || priority
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const handleRowClick = (row) => {
      viewBugDetail(row)
    }

    const viewBugDetail = (row) => {
      window.location.href = `/#/bugs/${row.id}`
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      loadBugList()
    }

    const handlePageChange = (val) => {
      currentPage.value = val
      loadBugList()
    }

    const handleTimeRangeChange = () => {
      currentPage.value = 1
      loadAllData()
    }

    const handleDateRangeChange = () => {
      if (filters.timeRange === 'custom' && filters.customDateRange?.length === 2) {
        loadAllData()
      }
    }

    const handleSelectAllProjects = () => {
      filters.projectIds = []
      loadAllData()
    }

    const resetFilters = () => {
      filters.timeRange = 'month'
      filters.customDateRange = []
      filters.projectIds = []
      filters.bugTypes = []
      filters.severities = []
      filters.statuses = []
      filters.priorities = []
      filters.reportedBy = []
      loadAllData()
    }

    const refreshData = () => {
      loadAllData()
      ElMessage.success('数据已刷新')
    }

    const exportReport = async () => {
      const { startDate, endDate } = getDateRange()
      const exportData = {
        kpi: kpiData.value,
        filters: {
          timeRange: filters.timeRange,
          startDate,
          endDate,
          projects: filters.projectIds,
          bugTypes: filters.bugTypes,
          severities: filters.severities,
          statuses: filters.statuses,
          priorities: filters.priorities
        },
        exportedAt: new Date().toISOString()
      }
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `bug-statistics-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      ElMessage.success('报表导出成功')
    }

    const exportChartAsImage = (chartInstance, chartName) => {
      if (!chartInstance) {
        ElMessage.warning('图表未初始化')
        return
      }
      const url = chartInstance.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
      const link = document.createElement('a')
      link.href = url
      link.download = `${chartName}-${new Date().toISOString().split('T')[0]}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      ElMessage.success(`${chartName} 导出成功`)
    }

    const exportAllCharts = () => {
      exportChartAsImage(trendChart, 'bug-trend')
      setTimeout(() => exportChartAsImage(projectChart, 'bug-distribution'), 300)
      setTimeout(() => exportChartAsImage(typeChart, 'bug-type'), 600)
      setTimeout(() => exportChartAsImage(survivalChart, 'bug-survival'), 900)
      setTimeout(() => exportChartAsImage(severityChart, 'bug-severity'), 1200)
      setTimeout(() => exportChartAsImage(workloadChart, 'bug-workload'), 1500)
    }

    const handleExportCommand = (command) => {
      switch (command) {
        case 'data':
          exportReport()
          break
        case 'trend':
          exportChartAsImage(trendChart, 'bug-trend')
          break
        case 'distribution':
          exportChartAsImage(projectChart, 'bug-distribution')
          break
        case 'all':
          exportAllCharts()
          break
      }
    }

    onMounted(() => {
      initCharts()
      loadFilterOptions().then(() => {
        loadAllData()
      })
    })

    watch(tableView, () => {
      currentPage.value = 1
      loadBugList()
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      trendChart?.dispose()
      projectChart?.dispose()
      typeChart?.dispose()
      survivalChart?.dispose()
      severityChart?.dispose()
      workloadChart?.dispose()
    })

    return {
      loading,
      filters,
      filterOptions,
      kpiData,
      trendGranularity,
      projectChartDimension,
      trendChartRef,
      projectChartRef,
      typeChartRef,
      survivalChartRef,
      severityChartRef,
      workloadChartRef,
      bugList,
      tableLoading,
      tableView,
      currentPage,
      pageSize,
      totalBugs,
      getChangeClass,
      handleTimeRangeChange,
      handleDateRangeChange,
      handleSelectAllProjects,
      loadAllData,
      loadTrendData,
      loadDistributionData,
      resetFilters,
      refreshData,
      exportReport,
      exportChartAsImage,
      exportAllCharts,
      handleExportCommand,
      getStatusType,
      getStatusLabel,
      getSeverityType,
      getSeverityLabel,
      getPriorityType,
      getPriorityLabel,
      formatDate,
      handleRowClick,
      viewBugDetail,
      handleSizeChange,
      handlePageChange
    }
  }
}
</script>

<style scoped>
.bug-statistics {
  padding: 20px;
  position: relative;
}

.statistics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.statistics-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-panel {
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.kpi-cards {
  margin-bottom: 20px;
}

.kpi-card {
  text-align: center;
}

.kpi-card.warning {
  border-left: 4px solid #E6A23C;
}

.kpi-card.danger {
  border-left: 4px solid #F56C6C;
}

.kpi-content {
  padding: 10px 0;
}

.kpi-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.kpi-value.success {
  color: #67C23A;
}

.kpi-value.danger {
  color: #F56C6C;
}

.kpi-change {
  font-size: 14px;
  margin-left: 8px;
}

.kpi-change.up {
  color: #F56C6C;
}

.kpi-change.down {
  color: #67C23A;
}

.kpi-change.stable {
  color: #909399;
}

.kpi-sub {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

.kpi-unit {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

.kpi-label {
  font-size: 14px;
  color: #606266;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  gap: 16px;
}

.loading-overlay .el-icon {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.data-table-card {
  margin-top: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.el-table {
  cursor: pointer;
}

.el-table:hover {
  background-color: #f5f7fa;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .bug-statistics {
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

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
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
  .bug-statistics {
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
