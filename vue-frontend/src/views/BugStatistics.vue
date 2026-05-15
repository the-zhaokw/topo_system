<template>
  <div class="bug-statistics">
    <!-- 精致头部区域 -->
    <div class="statistics-header animate-elegant-fade-in-down">
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <div class="title-icon">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="title-glow"></div>
          </div>
          <div class="title-text">
            <h2>Bug统计看板</h2>
            <p>全面分析Bug数据，洞察项目质量</p>
          </div>
        </div>
        <div class="header-actions">
          <el-dropdown @command="handleExportCommand">
            <el-button type="primary" class="btn-gradient btn-shine">
              <el-icon><Download /></el-icon>
              导出
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu class="elegant-dropdown">
                <el-dropdown-item command="data">
                  <el-icon><Document /></el-icon>导出数据 (JSON)
                </el-dropdown-item>
                <el-dropdown-item command="trend">
                  <el-icon><TrendCharts /></el-icon>导出趋势图
                </el-dropdown-item>
                <el-dropdown-item command="distribution">
                  <el-icon><PieChart /></el-icon>导出分布图
                </el-dropdown-item>
                <el-dropdown-item command="all">
                  <el-icon><Collection /></el-icon>导出所有图表
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button @click="refreshData" class="refresh-btn btn-glass">
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

    <!-- 筛选面板 - 玻璃拟态 -->
    <el-card class="filter-panel glass-card-elegant animate-elegant-fade-in-up delay-100" shadow="never">
      <div class="filter-row">
        <div class="filter-item">
          <span class="filter-label">
            <el-icon><Calendar /></el-icon>时间范围
          </span>
          <el-select v-model="filters.timeRange" @change="handleTimeRangeChange" class="filter-select elegant-select">
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
            class="date-range-picker elegant-date-picker"
          />
        </div>

        <div class="filter-item">
          <span class="filter-label">
            <el-icon><Folder /></el-icon>所属项目
          </span>
          <el-select 
            v-model="filters.projectIds" 
            multiple 
            collapse-tags
            collapse-tags-tooltip
            placeholder="全部项目" 
            class="filter-select elegant-select"
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
          <span class="filter-label">
            <el-icon><Collection /></el-icon>Bug类型
          </span>
          <el-select 
            v-model="filters.bugTypes" 
            multiple 
            collapse-tags
            placeholder="全部类型"
            class="filter-select elegant-select"
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
          <span class="filter-label">
            <el-icon><Warning /></el-icon>严重程度
          </span>
          <el-select 
            v-model="filters.severities" 
            multiple 
            collapse-tags
            placeholder="全部等级"
            class="filter-select elegant-select"
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
          <span class="filter-label">
            <el-icon><CircleCheck /></el-icon>Bug状态
          </span>
          <el-select 
            v-model="filters.statuses" 
            multiple 
            collapse-tags
            placeholder="全部状态"
            class="filter-select elegant-select"
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
          <span class="filter-label">
            <el-icon><Flag /></el-icon>优先级
          </span>
          <el-select 
            v-model="filters.priorities" 
            multiple 
            collapse-tags
            placeholder="全部优先"
            class="filter-select elegant-select"
            @change="loadAllData"
          >
            <el-option label="紧急" value="urgent"></el-option>
            <el-option label="高" value="high"></el-option>
            <el-option label="中" value="medium"></el-option>
            <el-option label="低" value="low"></el-option>
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">
            <el-icon><User /></el-icon>创建人
          </span>
          <el-select 
            v-model="filters.reportedBy" 
            multiple 
            collapse-tags
            placeholder="不限"
            class="filter-select elegant-select"
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

        <el-button type="warning" text @click="resetFilters" class="reset-btn btn-text-elegant">
          <el-icon><RefreshLeft /></el-icon>
          重置
        </el-button>
      </div>
    </el-card>

    <!-- 精致KPI统计卡片 -->
    <div class="kpi-cards animate-elegant-fade-in-up delay-200">
      <el-row :gutter="20">
        <el-col :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <div class="kpi-card-elegant" :class="{ 'warning': kpiData.total_bugs > 1000 }">
            <div class="kpi-card-bg"></div>
            <div class="kpi-icon-wrapper kpi-icon-total">
              <el-icon><WarningFilled /></el-icon>
              <div class="icon-glow"></div>
            </div>
            <div class="kpi-content">
              <div class="kpi-value-wrapper">
                <span class="kpi-value" :class="{ 'animate-count-up': kpiData.total_bugs }">
                  {{ kpiData.total_bugs?.toLocaleString() || 0 }}
                </span>
                <span class="kpi-change" :class="getChangeClass(kpiData.total_change)">
                  <el-icon v-if="kpiData.total_change > 0"><ArrowUp /></el-icon>
                  <el-icon v-else-if="kpiData.total_change < 0"><ArrowDown /></el-icon>
                  <el-icon v-else><Minus /></el-icon>
                  {{ Math.abs(kpiData.total_change || 0) }}%
                </span>
              </div>
              <div class="kpi-label">总Bug数</div>
            </div>
            <div class="kpi-progress">
              <div class="progress-bar" :style="{ width: Math.min((kpiData.total_bugs || 0) / 1000 * 100, 100) + '%' }"></div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <div class="kpi-card-elegant" :class="{ 'danger': kpiData.new_bugs > 20 }">
            <div class="kpi-card-bg"></div>
            <div class="kpi-icon-wrapper kpi-icon-new">
              <el-icon><CirclePlusFilled /></el-icon>
              <div class="icon-glow"></div>
            </div>
            <div class="kpi-content">
              <div class="kpi-value-wrapper">
                <span class="kpi-value" :class="{ 'animate-count-up': kpiData.new_bugs }">
                  {{ kpiData.new_bugs || 0 }}
                </span>
                <span class="kpi-sub">{{ filters.timeRange === 'today' ? '今日' : '周期内' }}</span>
              </div>
              <div class="kpi-label">新增Bug</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
        
        <el-col :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <div class="kpi-card-elegant kpi-card-success">
            <div class="kpi-card-bg"></div>
            <div class="kpi-icon-wrapper kpi-icon-resolved">
              <el-icon><CircleCheckFilled /></el-icon>
              <div class="icon-glow"></div>
            </div>
            <div class="kpi-content">
              <div class="kpi-value-wrapper">
                <span class="kpi-value success" :class="{ 'animate-count-up': kpiData.resolved_bugs }">
                  {{ kpiData.resolved_bugs || 0 }}
                </span>
              </div>
              <div class="kpi-label">已解决</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
        
        <el-col :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <div class="kpi-card-elegant" :class="{ 'warning': kpiData.unresolved_bugs > 50 }">
            <div class="kpi-card-bg"></div>
            <div class="kpi-icon-wrapper kpi-icon-unresolved">
              <el-icon><Warning /></el-icon>
              <div class="icon-glow"></div>
            </div>
            <div class="kpi-content">
              <div class="kpi-value-wrapper">
                <span class="kpi-value danger" :class="{ 'animate-count-up': kpiData.unresolved_bugs }">
                  {{ kpiData.unresolved_bugs || 0 }}
                </span>
              </div>
              <div class="kpi-label">未解决</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
        
        <el-col :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <div class="kpi-card-elegant" :class="{ 'warning': kpiData.resolution_rate < 80 }">
            <div class="kpi-card-bg"></div>
            <div class="kpi-icon-wrapper kpi-icon-rate">
              <el-icon><TrendCharts /></el-icon>
              <div class="icon-glow"></div>
            </div>
            <div class="kpi-content">
              <div class="kpi-value-wrapper">
                <span class="kpi-value" :class="{ 'animate-count-up': kpiData.resolution_rate }">
                  {{ kpiData.resolution_rate || 0 }}
                </span>
                <span class="kpi-unit">%</span>
              </div>
              <div class="kpi-label">解决率</div>
            </div>
            <div class="kpi-ring" :style="{ '--progress': (kpiData.resolution_rate || 0) + '%' }">
              <svg viewBox="0 0 36 36">
                <path class="ring-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                <path class="ring-progress" :stroke-dasharray="(kpiData.resolution_rate || 0) + ', 100'" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              </svg>
            </div>
          </div>
        </el-col>
        
        <el-col :span="4" :xs="12" :sm="8" :md="6" :lg="4">
          <div class="kpi-card-elegant" :class="{ 'danger': kpiData.avg_fix_time > 3 }">
            <div class="kpi-card-bg"></div>
            <div class="kpi-icon-wrapper kpi-icon-time">
              <el-icon><Timer /></el-icon>
              <div class="icon-glow"></div>
            </div>
            <div class="kpi-content">
              <div class="kpi-value-wrapper">
                <span class="kpi-value" :class="{ 'animate-count-up': kpiData.avg_fix_time }">
                  {{ kpiData.avg_fix_time || 0 }}
                </span>
                <span class="kpi-unit">天</span>
              </div>
              <div class="kpi-label">平均解决时长</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 图表区域 -->
    <div class="chart-section animate-elegant-fade-in-up delay-300">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card class="chart-card glass-card-elegant" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <div class="title-icon-bg">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                  <span>Bug趋势分析</span>
                </div>
                <el-radio-group v-model="trendGranularity" size="small" @change="loadTrendData" class="chart-controls elegant-radio">
                  <el-radio-button label="day">日</el-radio-button>
                  <el-radio-button label="week">周</el-radio-button>
                  <el-radio-button label="month">月</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div ref="trendChartRef" class="chart-container" style="height: 380px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="chart-section animate-elegant-fade-in-up delay-400">
      <el-row :gutter="20">
        <el-col :span="12" :xs="24">
          <el-card class="chart-card glass-card-elegant" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <div class="title-icon-bg icon-project">
                    <el-icon><PieChart /></el-icon>
                  </div>
                  <span>项目Bug分布</span>
                </div>
                <el-select v-model="projectChartDimension" size="small" @change="loadDistributionData" class="chart-controls elegant-select-small">
                  <el-option label="按项目" value="project"></el-option>
                  <el-option label="按严重程度" value="severity"></el-option>
                  <el-option label="按优先级" value="priority"></el-option>
                  <el-option label="按类型" value="type"></el-option>
                  <el-option label="按状态" value="status"></el-option>
                </el-select>
              </div>
            </template>
            <div ref="projectChartRef" class="chart-container" style="height: 340px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="6" :xs="24">
          <el-card class="chart-card glass-card-elegant" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <div class="title-icon-bg icon-type">
                    <el-icon><Histogram /></el-icon>
                  </div>
                  <span>Bug类型占比</span>
                </div>
              </div>
            </template>
            <div ref="typeChartRef" class="chart-container" style="height: 340px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="6" :xs="24">
          <el-card class="chart-card glass-card-elegant" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <div class="title-icon-bg icon-time">
                    <el-icon><Timer /></el-icon>
                  </div>
                  <span>存活时长分布</span>
                </div>
              </div>
            </template>
            <div ref="survivalChartRef" class="chart-container" style="height: 340px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="chart-section animate-elegant-fade-in-up delay-500">
      <el-row :gutter="20">
        <el-col :span="12" :xs="24">
          <el-card class="chart-card glass-card-elegant" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <div class="title-icon-bg icon-severity">
                    <el-icon><Warning /></el-icon>
                  </div>
                  <span>严重程度分布</span>
                </div>
              </div>
            </template>
            <div ref="severityChartRef" class="chart-container" style="height: 320px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="12" :xs="24">
          <el-card class="chart-card glass-card-elegant" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <div class="title-icon-bg icon-workload">
                    <el-icon><UserFilled /></el-icon>
                  </div>
                  <span>人员工作量分析</span>
                </div>
              </div>
            </template>
            <div ref="workloadChartRef" class="chart-container" style="height: 320px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Bug明细列表 -->
    <el-card class="data-table-card glass-card-elegant animate-elegant-fade-in-up delay-600" shadow="hover">
      <template #header>
        <div class="table-header">
          <div class="table-title">
            <div class="title-icon-bg icon-list">
              <el-icon><List /></el-icon>
            </div>
            <span>Bug明细列表</span>
            <el-badge :value="totalBugs" class="item-count" type="primary" />
          </div>
          <el-radio-group v-model="tableView" size="small" class="table-view-toggle elegant-radio">
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
        class="custom-table elegant-table"
      >
        <el-table-column prop="id" label="ID" width="80">
          <template #default="{ row }">
            <span class="bug-id">#{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="project_name" label="项目" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="light" class="status-tag elegant-tag">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small" effect="light" class="severity-tag elegant-tag">
              {{ getSeverityLabel(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small" effect="light" class="priority-tag elegant-tag">
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
            <el-button type="primary" link @click.stop="viewBugDetail(row)" class="view-btn btn-icon-elegant">
              <el-icon><View /></el-icon>
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
          class="elegant-pagination"
        />
      </div>
    </el-card>

    <!-- 加载遮罩 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <span>数据加载中...</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Refresh, RefreshLeft, Download, ArrowDown, 
  DataAnalysis, WarningFilled, CirclePlusFilled, CircleCheckFilled,
  Warning, TrendCharts, Timer, PieChart, Histogram, List,
  UserFilled, View, ArrowUp, ArrowDownBold, Minus,
  Calendar, Folder, Collection, CircleCheck, Flag, User, Document
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import bugStatisticsService from '@/services/bugStatisticsService'
import { systemTimeService } from '@/services/systemTimeService'

export default {
  name: 'BugStatistics',
  components: { 
    Refresh, RefreshLeft, Download, ArrowDown,
    DataAnalysis, WarningFilled, CirclePlusFilled, CircleCheckFilled,
    Warning, TrendCharts, Timer, PieChart, Histogram, List,
    UserFilled, View, ArrowUp, ArrowDownBold, Minus,
    Calendar, Folder, Collection, CircleCheck, Flag, User, Document
  },
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
        tooltip: { 
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: 'rgba(139, 92, 246, 0.2)',
          borderWidth: 1,
          textStyle: { color: '#1e293b' },
          padding: [12, 16],
          extraCssText: 'box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-radius: 12px;'
        },
        legend: { 
          data: ['新增Bug', '解决Bug', '累计未解决'], 
          bottom: 0,
          textStyle: { color: '#64748b', fontSize: 12 },
          itemGap: 20
        },
        grid: { 
          left: '3%', 
          right: '4%', 
          bottom: '15%', 
          top: '8%',
          containLabel: true 
        },
        xAxis: { 
          type: 'category', 
          data: data.map(d => d.date),
          axisLabel: { 
            rotate: trendGranularity.value === 'day' ? 45 : 0,
            color: '#64748b',
            fontSize: 11
          },
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisTick: { show: false }
        },
        yAxis: { 
          type: 'value',
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
          axisLabel: { color: '#64748b', fontSize: 11 }
        },
        series: [
          {
            name: '新增Bug',
            type: 'line',
            data: data.map(d => d.new_bugs),
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: { color: '#8b5cf6', borderWidth: 2, borderColor: '#fff' },
            lineStyle: { width: 3, shadowColor: 'rgba(139, 92, 246, 0.3)', shadowBlur: 10 },
            areaStyle: { 
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(139, 92, 246, 0.25)' },
                { offset: 1, color: 'rgba(139, 92, 246, 0.02)' }
              ])
            }
          },
          {
            name: '解决Bug',
            type: 'line',
            data: data.map(d => d.resolved_bugs),
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: { color: '#22c55e', borderWidth: 2, borderColor: '#fff' },
            lineStyle: { width: 3, shadowColor: 'rgba(34, 197, 94, 0.3)', shadowBlur: 10 },
            areaStyle: { 
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(34, 197, 94, 0.25)' },
                { offset: 1, color: 'rgba(34, 197, 94, 0.02)' }
              ])
            }
          },
          {
            name: '累计未解决',
            type: 'line',
            data: data.map(d => d.cumulative_unresolved),
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: { color: '#f43f5e', borderWidth: 2, borderColor: '#fff' },
            lineStyle: { width: 3, shadowColor: 'rgba(244, 63, 94, 0.3)', shadowBlur: 10 },
            areaStyle: { 
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(244, 63, 94, 0.25)' },
                { offset: 1, color: 'rgba(244, 63, 94, 0.02)' }
              ])
            }
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
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: 'rgba(139, 92, 246, 0.2)',
          borderWidth: 1,
          textStyle: { color: '#1e293b' },
          padding: [12, 16],
          extraCssText: 'box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-radius: 12px;',
          formatter: (params) => {
            if (dimension === 'status') {
              const p = params[0]
              return `${p.name}: ${p.value}个 (${p.percentage}%)`
            }
            const p = params[0]
            return `${p.name}<br/>总计: ${p.value}<br/>新建: ${p.data?.new || 0}<br/>已解决: ${p.data?.resolved || 0}<br/>已关闭: ${p.data?.closed || 0}`
          }
        },
        legend: { 
          data: isStacked ? ['新建', '已解决', '已关闭'] : [], 
          bottom: 0,
          textStyle: { color: '#64748b', fontSize: 11 }
        },
        grid: { 
          left: '3%', 
          right: '4%', 
          bottom: '15%', 
          top: '8%',
          containLabel: true 
        },
        xAxis: { 
          type: 'category', 
          data: chartData.map(d => d.name),
          axisLabel: { 
            rotate: 30,
            color: '#64748b',
            fontSize: 11
          },
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisTick: { show: false }
        },
        yAxis: { 
          type: 'value', 
          name: 'Bug数量',
          nameTextStyle: { color: '#94a3b8', fontSize: 11 },
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
          axisLabel: { color: '#64748b', fontSize: 11 }
        },
        series: isStacked ? [
          {
            name: '新建',
            type: 'bar',
            stack: 'total',
            data: chartData.map(d => d.new || 0),
            itemStyle: { 
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#fb7185' },
                { offset: 1, color: '#f43f5e' }
              ]),
              borderRadius: [6, 6, 0, 0]
            }
          },
          {
            name: '已解决',
            type: 'bar',
            stack: 'total',
            data: chartData.map(d => d.resolved || 0),
            itemStyle: { 
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#fbbf24' },
                { offset: 1, color: '#f59e0b' }
              ])
            }
          },
          {
            name: '已关闭',
            type: 'bar',
            stack: 'total',
            data: chartData.map(d => d.closed || 0),
            itemStyle: { 
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#4ade80' },
                { offset: 1, color: '#22c55e' }
              ]),
              borderRadius: [0, 0, 6, 6]
            }
          }
        ] : [
          {
            name: 'Bug状态',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '45%'],
            data: chartData,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 3
            },
            label: {
              show: true,
              formatter: '{b}\n{c}个 ({d}%)',
              color: '#64748b',
              fontSize: 11
            },
            emphasis: {
              itemStyle: { 
                shadowBlur: 20, 
                shadowOffsetX: 0, 
                shadowColor: 'rgba(0, 0, 0, 0.15)' 
              }
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
      
      const colors = ['#8b5cf6', '#a78bfa', '#c4b5fd', '#f472b6', '#fb7185', '#