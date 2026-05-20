<template>
  <div class="monitoring-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Monitor /></el-icon>
          </div>
          <div class="title-text">
            <h1>系统监控</h1>
            <p class="subtitle">实时监控系统运行状态</p>
          </div>
        </div>
      </div>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="animate-fade-in-up delay-100">
      <el-tab-pane label="监控仪表盘" name="dashboard">
        <div v-loading="dashboardLoading">
          <!-- 统计卡片区域 -->
          <div class="stats-row animate-fade-in-up delay-200">
            <el-row :gutter="16">
              <el-col :xs="12" :sm="6" :md="6" :lg="6">
                <div class="stat-card stat-card-users">
                  <div class="stat-icon-wrapper stat-icon-wrapper-users">
                    <el-icon><User /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ onlineUsers }}</div>
                    <div class="stat-label">在线用户数</div>
                  </div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="6" :md="6" :lg="6">
                <div class="stat-card stat-card-load">
                  <div class="stat-icon-wrapper stat-icon-wrapper-load">
                    <el-icon><Cpu /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ performanceData.cpu?.percent || 0 }}%</div>
                    <div class="stat-label">系统负载</div>
                  </div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="6" :md="6" :lg="6">
                <div class="stat-card stat-card-memory">
                  <div class="stat-icon-wrapper stat-icon-wrapper-memory">
                    <el-icon><Coin /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ performanceData.memory?.percent || 0 }}%</div>
                    <div class="stat-label">内存使用率</div>
                  </div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="6" :md="6" :lg="6">
                <div class="stat-card stat-card-disk">
                  <div class="stat-icon-wrapper stat-icon-wrapper-disk">
                    <el-icon><Folder /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ performanceData.disk?.percent || 0 }}%</div>
                    <div class="stat-label">磁盘使用率</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>

          <div class="stats-row animate-fade-in-up delay-300">
            <el-row :gutter="16">
              <el-col :span="8">
                <div class="stat-card stat-card-alerts">
                  <div class="stat-icon-wrapper stat-icon-wrapper-alerts">
                    <el-icon><Warning /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ activeAlertCount }}</div>
                    <div class="stat-label">活跃告警</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-card stat-card-db">
                  <div class="stat-icon-wrapper stat-icon-wrapper-db">
                    <el-icon><Box /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ dbStats.database_size_mb || 0 }} <span class="stat-unit">MB</span></div>
                    <div class="stat-label">数据库大小</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-card stat-card-requests">
                  <div class="stat-icon-wrapper stat-icon-wrapper-requests">
                    <el-icon><Connection /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ apiStats.total_requests || 0 }}</div>
                    <div class="stat-label">API请求数</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>

          <el-card shadow="hover" class="health-checks-card glass-card animate-fade-in-up delay-400">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><CircleCheck /></el-icon>
                  健康检查详情
                </span>
                <el-button type="primary" link @click="loadDashboard" class="btn-refresh">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>
            <el-table :data="healthChecks" style="width: 100%" class="custom-table">
              <el-table-column prop="name" label="检查项" width="180">
                <template #default="{ row }">
                  <div class="check-item">
                    <el-icon class="check-icon"><Check /></el-icon>
                    <span>{{ row.name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small" effect="light" class="status-tag">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="消息">
                <template #default="{ row }">
                  <span class="message-text">{{ row.message }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="性能监控" name="performance">
        <div v-loading="performanceLoading">
          <el-row :gutter="16" class="animate-fade-in-up delay-200">
            <el-col :span="12">
              <el-card shadow="hover" class="glass-card metric-card">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">
                      <el-icon><Cpu /></el-icon>
                      CPU & 内存
                    </span>
                  </div>
                </template>
                <div class="metric-item">
                  <span class="metric-label">CPU使用率:</span>
                  <div class="metric-value-wrapper">
                    <el-progress :percentage="performanceData.cpu?.percent || 0" :color="getProgressColor(performanceData.cpu?.percent)" :stroke-width="12" class="metric-progress" />
                    <span class="metric-value gradient-text-cpu">{{ performanceData.cpu?.percent || 0 }}%</span>
                  </div>
                </div>
                <div class="metric-item">
                  <span class="metric-label">CPU核心数:</span>
                  <span class="metric-value">{{ performanceData.cpu?.count || 0 }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">内存使用率:</span>
                  <div class="metric-value-wrapper">
                    <el-progress :percentage="performanceData.memory?.percent || 0" :color="getProgressColor(performanceData.memory?.percent)" :stroke-width="12" class="metric-progress" />
                    <span class="metric-value gradient-text-memory">{{ performanceData.memory?.percent || 0 }}%</span>
                  </div>
                </div>
                <div class="metric-item">
                  <span class="metric-label">内存总量:</span>
                  <span class="metric-value">{{ formatBytes(performanceData.memory?.total) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">内存可用:</span>
                  <span class="metric-value">{{ formatBytes(performanceData.memory?.available) }}</span>
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card shadow="hover" class="glass-card metric-card">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">
                      <el-icon><Folder /></el-icon>
                      磁盘 & 网络
                    </span>
                  </div>
                </template>
                <div class="metric-item">
                  <span class="metric-label">磁盘使用率:</span>
                  <div class="metric-value-wrapper">
                    <el-progress :percentage="performanceData.disk?.percent || 0" :color="getProgressColor(performanceData.disk?.percent)" :stroke-width="12" class="metric-progress" />
                    <span class="metric-value gradient-text-disk">{{ performanceData.disk?.percent || 0 }}%</span>
                  </div>
                </div>
                <div class="metric-item">
                  <span class="metric-label">磁盘总量:</span>
                  <span class="metric-value">{{ formatBytes(performanceData.disk?.total) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">磁盘可用:</span>
                  <span class="metric-value">{{ formatBytes(performanceData.disk?.free) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">网络发送:</span>
                  <span class="metric-value gradient-text-network">{{ formatBytes(performanceData.network?.bytes_sent) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">网络接收:</span>
                  <span class="metric-value gradient-text-network">{{ formatBytes(performanceData.network?.bytes_recv) }}</span>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-card shadow="hover" class="process-info-card glass-card animate-fade-in-up delay-300">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Setting /></el-icon>
                  进程信息
                </span>
              </div>
            </template>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">进程ID</span>
                <span class="info-value">{{ performanceData.process?.pid || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">进程CPU占用</span>
                <span class="info-value gradient-text-cpu">{{ performanceData.process?.cpu_percent || 0 }}%</span>
              </div>
              <div class="info-item">
                <span class="info-label">进程内存占用</span>
                <span class="info-value gradient-text-memory">{{ performanceData.process?.memory_percent || 0 }}%</span>
              </div>
              <div class="info-item">
                <span class="info-label">线程数</span>
                <span class="info-value">{{ performanceData.process?.num_threads || 0 }}</span>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="数据库监控" name="database">
        <div v-loading="databaseLoading">
          <el-card shadow="hover" class="glass-card animate-fade-in-up delay-200">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Box /></el-icon>
                  数据库统计
                </span>
                <el-button type="primary" link @click="loadDatabaseStats" class="btn-refresh">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>
            <el-row :gutter="16" class="db-stats-row">
              <el-col :span="8">
                <div class="db-stat-item">
                  <div class="db-stat-icon">
                    <el-icon><DataLine /></el-icon>
                  </div>
                  <span class="db-stat-label">数据库大小</span>
                  <span class="db-stat-value">{{ dbStats.database_size_mb }} <span class="stat-unit">MB</span></span>
                </div>
              </el-col>
            </el-row>
            <el-table :data="dbStats.tables" style="width: 100%; margin-top: 16px;" class="custom-table">
              <el-table-column prop="name" label="表名" />
              <el-table-column prop="count" label="记录数" align="right">
                <template #default="{ row }">
                  <span class="count-badge">{{ row.count }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="API统计" name="api-stats">
        <div v-loading="apiLoading">
          <el-card shadow="hover" class="glass-card animate-fade-in-up delay-200">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Connection /></el-icon>
                  API请求统计
                </span>
                <el-button type="primary" link @click="loadApiStats" class="btn-refresh">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>
            <el-row :gutter="16" class="api-stats-row">
              <el-col :span="6">
                <div class="api-stat-item">
                  <div class="api-stat-icon">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                  <span class="api-stat-label">总请求数</span>
                  <span class="api-stat-value">{{ apiStats.total_requests }}</span>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="api-stat-item">
                  <div class="api-stat-icon">
                    <el-icon><Timer /></el-icon>
                  </div>
                  <span class="api-stat-label">平均响应时间</span>
                  <span class="api-stat-value">{{ apiStats.avg_response_time }} <span class="stat-unit">ms</span></span>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="api-stat-item">
                  <div class="api-stat-icon">
                    <el-icon><Warning /></el-icon>
                  </div>
                  <span class="api-stat-label">错误率</span>
                  <span class="api-stat-value gradient-text-error">{{ apiStats.error_rate }}%</span>
                </div>
              </el-col>
            </el-row>
            <el-table :data="apiStats.top_endpoints" style="width: 100%; margin-top: 16px;" class="custom-table">
              <el-table-column prop="endpoint" label="端点">
                <template #default="{ row }">
                  <span class="endpoint-badge">{{ row.endpoint }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="count" label="请求次数" align="right">
                <template #default="{ row }">
                  <span class="count-badge">{{ row.count }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="告警管理" name="alerts">
        <div v-loading="alertsLoading">
          <el-card shadow="hover" class="glass-card animate-fade-in-up delay-200">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Bell /></el-icon>
                  告警列表
                </span>
                <el-button type="primary" link @click="loadAlerts" class="btn-refresh">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>
            <el-table :data="alertList" style="width: 100%" class="custom-table">
              <el-table-column prop="id" label="ID" width="80" align="center">
                <template #default="{ row }">
                  <span class="id-badge">{{ row.id }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="level" label="级别" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="getAlertLevelType(row.level)" size="small" effect="light" class="alert-tag">
                    {{ row.level }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'active' ? 'danger' : 'success'" size="small" effect="light" class="status-tag">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180" align="center">
                <template #default="{ row }">
                  <span class="timestamp">{{ row.created_at }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center" fixed="right">
                <template #default="{ row }">
                  <el-button
                    v-if="row.status === 'active'"
                    type="primary"
                    link
                    size="small"
                    @click="handleResolveAlert(row.id)"
                    class="resolve-btn">
                    <el-icon><Check /></el-icon>
                    解决
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="系统日志" name="logs">
        <div v-loading="logsLoading">
          <el-card shadow="hover" class="glass-card animate-fade-in-up delay-200">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Document /></el-icon>
                  系统日志
                </span>
                <div class="header-actions">
                  <el-select v-model="logFilter.level" placeholder="日志级别" clearable style="width: 120px; margin-right: 8px;">
                    <el-option label="DEBUG" value="DEBUG" />
                    <el-option label="INFO" value="INFO" />
                    <el-option label="WARNING" value="WARNING" />
                    <el-option label="ERROR" value="ERROR" />
                  </el-select>
                  <el-button type="primary" link @click="loadLogs" class="btn-refresh">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </div>
            </template>
            <el-table :data="logList" style="width: 100%" class="custom-table">
              <el-table-column prop="timestamp" label="时间" width="180" align="center">
                <template #default="{ row }">
                  <span class="timestamp">{{ row.timestamp }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="level" label="级别" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="getLogLevelType(row.level)" size="small" effect="light" class="log-tag">
                    {{ row.level }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="source" label="来源" width="120" align="center">
                <template #default="{ row }">
                  <span class="source-badge">{{ row.source }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="消息">
                <template #default="{ row }">
                  <span class="message-text">{{ row.message }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="系统信息" name="system-info">
        <div v-loading="systemInfoLoading">
          <el-card shadow="hover" class="glass-card animate-fade-in-up delay-200">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><InfoFilled /></el-icon>
                  系统信息
                </span>
                <el-button type="primary" link @click="loadSystemInfo" class="btn-refresh">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">平台</span>
                <span class="info-value">{{ systemInfo.platform }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">主机名</span>
                <span class="info-value">{{ systemInfo.hostname }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Python版本</span>
                <span class="info-value">{{ systemInfo.python_version }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">CPU核心数</span>
                <span class="info-value">{{ systemInfo.cpu_count }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">内存总量</span>
                <span class="info-value">{{ formatBytes(systemInfo.memory_total) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">启动时间</span>
                <span class="info-value">{{ systemInfo.boot_time }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">应用名称</span>
                <span class="info-value">{{ systemInfo.app?.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">应用版本</span>
                <span class="info-value">{{ systemInfo.app?.version }}</span>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { apiService } from '@/services/api'
import {
  Monitor, Cpu, Coin, Folder, Warning, Connection, Box, User,
  Refresh, Check, CircleCheck, Setting, DataLine, TrendCharts, Timer,
  Bell, Document, InfoFilled
} from '@element-plus/icons-vue'

const activeTab = ref('dashboard')

const dashboardLoading = ref(false)
const performanceLoading = ref(false)
const databaseLoading = ref(false)
const apiLoading = ref(false)
const alertsLoading = ref(false)
const logsLoading = ref(false)
const systemInfoLoading = ref(false)

const healthData = ref({})
const performanceData = ref({})
const dbStats = ref({ tables: [] })
const apiStats = ref({})
const alertList = ref([])
const logList = ref([])
const systemInfo = ref({})

const logFilter = ref({ level: '' })

// 在线用户数（模拟数据，实际应从API获取）
const onlineUsers = ref(42)

const healthStatusClass = computed(() => {
  const status = healthData.value.status
  if (status === 'healthy') return 'status-healthy'
  if (status === 'warning') return 'status-warning'
  if (status === 'critical') return 'status-critical'
  return ''
})

const healthChecks = computed(() => {
  const checks = healthData.value.checks || {}
  return Object.entries(checks).map(([name, data]) => ({
    name: getCheckName(name),
    status: data.status,
    message: data.message
  }))
})

const activeAlertCount = computed(() => {
  return alertList.value.filter(a => a.status === 'active').length
})

const getCheckName = (key) => {
  const names = {
    database: '数据库',
    disk: '磁盘',
    memory: '内存',
    api: 'API'
  }
  return names[key] || key
}

const getStatusType = (status) => {
  const types = {
    healthy: 'success',
    warning: 'warning',
    critical: 'danger'
  }
  return types[status] || 'info'
}

const getAlertLevelType = (level) => {
  const types = {
    info: 'info',
    warning: 'warning',
    critical: 'danger'
  }
  return types[level] || 'info'
}

const getLogLevelType = (level) => {
  const types = {
    DEBUG: 'info',
    INFO: 'success',
    WARNING: 'warning',
    ERROR: 'danger'
  }
  return types[level] || 'info'
}

const getProgressColor = (percent) => {
  if (percent > 90) return '#F56C6C'
  if (percent > 70) return '#E6A23C'
  return '#67C23A'
}

const formatBytes = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(2)} ${units[i]}`
}

const loadDashboard = async () => {
  dashboardLoading.value = true
  try {
    const [healthRes, perfRes, dbRes, apiRes, alertsRes] = await Promise.all([
      apiService.monitoring.getHealth(),
      apiService.monitoring.getPerformance(),
      apiService.monitoring.getDatabaseStats(),
      apiService.monitoring.getApiStats(),
      apiService.monitoring.getAlerts()
    ])
    healthData.value = healthRes.data || healthRes
    performanceData.value = perfRes.data || perfRes
    dbStats.value = dbRes.data || dbRes
    apiStats.value = apiRes.data || apiRes
    alertList.value = (alertsRes.data || alertsRes).alerts || []
  } catch (error) {
    console.error('加载监控仪表盘失败:', error)
    ElMessage.error('加载监控仪表盘失败')
  } finally {
    dashboardLoading.value = false
  }
}

const loadDatabaseStats = async () => {
  databaseLoading.value = true
  try {
    const res = await apiService.monitoring.getDatabaseStats()
    dbStats.value = res.data || res
  } catch (error) {
    console.error('加载数据库统计失败:', error)
    ElMessage.error('加载数据库统计失败')
  } finally {
    databaseLoading.value = false
  }
}

const loadApiStats = async () => {
  apiLoading.value = true
  try {
    const res = await apiService.monitoring.getApiStats()
    apiStats.value = res.data || res
  } catch (error) {
    console.error('加载API统计失败:', error)
    ElMessage.error('加载API统计失败')
  } finally {
    apiLoading.value = false
  }
}

const loadAlerts = async () => {
  alertsLoading.value = true
  try {
    const res = await apiService.monitoring.getAlerts()
    alertList.value = (res.data || res).alerts || []
  } catch (error) {
    console.error('加载告警列表失败:', error)
    ElMessage.error('加载告警列表失败')
  } finally {
    alertsLoading.value = false
  }
}

const loadLogs = async () => {
  logsLoading.value = true
  try {
    const params = {}
    if (logFilter.value.level) {
      params.level = logFilter.value.level
    }
    const res = await apiService.monitoring.getLogs(params)
    logList.value = (res.data || res).logs || []
  } catch (error) {
    console.error('加载日志失败:', error)
    ElMessage.error('加载日志失败')
  } finally {
    logsLoading.value = false
  }
}

const loadSystemInfo = async () => {
  systemInfoLoading.value = true
  try {
    const res = await apiService.monitoring.getSystemInfo()
    systemInfo.value = res.data || res
  } catch (error) {
    console.error('加载系统信息失败:', error)
    ElMessage.error('加载系统信息失败')
  } finally {
    systemInfoLoading.value = false
  }
}

const handleResolveAlert = async (alertId) => {
  try {
    await apiService.monitoring.resolveAlert(alertId)
    ElMessage.success('告警已解决')
    loadAlerts()
  } catch (error) {
    console.error('解决告警失败:', error)
    ElMessage.error('解决告警失败')
  }
}

const handleTabChange = (tabName) => {
  switch (tabName) {
    case 'dashboard':
      loadDashboard()
      break
    case 'performance':
      if (!performanceData.value.cpu) {
        loadDashboard()
      }
      break
    case 'database':
      if (!dbStats.value.tables?.length) {
        loadDatabaseStats()
      }
      break
    case 'api-stats':
      if (!apiStats.value.total_requests) {
        loadApiStats()
      }
      break
    case 'alerts':
      if (!alertList.value.length) {
        loadAlerts()
      }
      break
    case 'logs':
      if (!logList.value.length) {
        loadLogs()
      }
      break
    case 'system-info':
      if (!systemInfo.value.platform) {
        loadSystemInfo()
      }
      break
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.monitoring-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(102, 126, 234, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(118, 75, 162, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.page-header::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
  pointer-events: none;
}

.header-bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
}

.orb-1 {
  width: 200px;
  height: 200px;
  background: #f093fb;
  top: -50px;
  right: 10%;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 150px;
  height: 150px;
  background: #4facfe;
  bottom: -30px;
  right: 30%;
  animation: float 8s ease-in-out infinite reverse;
}

.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-icon-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.title-icon {
  font-size: 32px;
  color: white;
}

.title-text h1 {
  margin: 0 0 6px 0;
  color: white;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 400;
}

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.stat-card::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  transform: scaleX(0);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15), 0 10px 20px -5px rgba(0, 0, 0, 0.1);
}

.stat-card:hover::before {
  transform: scaleX(1);
}

/* 统计卡片渐变配色 */
.stat-card-users::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card-load::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-memory::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-disk::before { background: linear-gradient(90deg, #ec4899, #f472b6); }
.stat-card-alerts::before { background: linear-gradient(90deg, #ef4444, #f87171); }
.stat-card-db::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.stat-card-requests::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.4s;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.stat-icon-wrapper-users {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #667eea;
  box-shadow: 0 4px 15px -3px rgba(102, 126, 234, 0.4);
}

.stat-icon-wrapper-load {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-memory {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-disk {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
}

.stat-icon-wrapper-alerts {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 15px -3px rgba(239, 68, 68, 0.4);
}

.stat-icon-wrapper-db {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
  box-shadow: 0 4px 15px -3px rgba(59, 130, 246, 0.4);
}

.stat-icon-wrapper-requests {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  color: #7c3aed;
  box-shadow: 0 4px 15px -3px rgba(139, 92, 246, 0.4);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card-users .stat-value {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-load .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-memory .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-disk .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-alerts .stat-value {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-db .stat-value {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-requests .stat-value {
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-unit {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s;
}

.glass-card:hover {
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 10px 20px -5px rgba(0, 0, 0, 0.08);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.card-title .el-icon {
  color: #6366f1;
  font-size: 18px;
}

.health-checks-card {
  margin-top: 16px;
}

/* 按钮样式 */
.btn-refresh {
  transition: all 0.3s;
}

.btn-refresh:hover {
  transform: translateY(-2px);
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(99, 102, 241, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.id-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.check-icon {
  color: #6366f1;
  font-size: 16px;
}

.status-tag,
.alert-tag,
.log-tag {
  font-weight: 500;
  border-radius: 6px;
}

.message-text {
  color: #475569;
  font-size: 13px;
}

.timestamp {
  font-size: 13px;
  color: #64748b;
}

.source-badge {
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
}

.count-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #6366f1;
  font-weight: 600;
}

.endpoint-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #475569;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
}

.resolve-btn {
  opacity: 0;
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) .resolve-btn {
  opacity: 1;
}

/* 指标卡片 */
.metric-card {
  margin-bottom: 16px;
}

.metric-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.metric-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.metric-item .metric-label {
  width: 120px;
  color: #64748b;
  font-weight: 500;
  font-size: 14px;
}

.metric-value-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.metric-progress {
  flex: 1;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  min-width: 60px;
  text-align: right;
}

/* 渐变文字效果 */
.gradient-text-cpu {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-memory {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-disk {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-network {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-error {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.process-info-card {
  margin-top: 16px;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.info-item {
  padding: 16px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s;
}

.info-item:hover {
  background: rgba(241, 245, 249, 0.9);
  transform: translateY(-2px);
}

.info-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

/* 数据库统计 */
.db-stats-row {
  margin-bottom: 16px;
}

.db-stat-item {
  text-align: center;
  padding: 24px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(96, 165, 250, 0.1) 100%);
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  transition: all 0.3s;
}

.db-stat-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px -5px rgba(59, 130, 246, 0.3);
}

.db-stat-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: white;
  font-size: 24px;
}

.db-stat-label {
  display: block;
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 500;
}

.db-stat-value {
  display: block;
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* API统计 */
.api-stats-row {
  margin-bottom: 16px;
}

.api-stat-item {
  text-align: center;
  padding: 20px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 16px;
  transition: all 0.3s;
}

.api-stat-item:hover {
  background: rgba(241, 245, 249, 0.9);
  transform: translateY(-4px);
}

.api-stat-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  color: white;
  font-size: 20px;
}

.api-stat-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 6px;
  font-weight: 500;
}

.api-stat-value {
  display: block;
  font-size: 22px;
  font-weight: 800;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 头部操作 */
.header-actions {
  display: flex;
  align-items: center;
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

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
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

/* 状态样式 */
.status-healthy {
  color: #67c23a;
}

.status-warning {
  color: #e6a23c;
}

.status-critical {
  color: #f56c6c;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .monitoring-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-title {
    gap: 14px;
  }

  .title-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 14px;
  }

  .title-icon {
    font-size: 24px;
  }

  .title-text h1 {
    font-size: 22px;
  }

  .subtitle {
    font-size: 13px;
  }

  .stats-row {
    margin-bottom: 20px;
  }

  .stat-card {
    padding: 16px;
    gap: 12px;
    margin-bottom: 12px;
  }

  .stat-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  .info-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .info-item {
    padding: 12px;
  }

  .info-value {
    font-size: 14px;
  }

  .metric-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .metric-item .metric-label {
    width: 100%;
  }

  .metric-value-wrapper {
    width: 100%;
  }

  .db-stat-item,
  .api-stat-item {
    padding: 16px;
    margin-bottom: 12px;
  }

  .db-stat-value,
  .api-stat-value {
    font-size: 20px;
  }

  .resolve-btn {
    opacity: 1;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-value {
    font-size: 20px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .el-table {
    font-size: 11px !important;
  }
}
</style>
