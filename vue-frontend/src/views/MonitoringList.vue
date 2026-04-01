<template>
  <div class="monitoring-container">
    <div class="page-header">
      <h1>系统监控</h1>
      <p>实时监控系统运行状态</p>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="监控仪表盘" name="dashboard">
        <div v-loading="dashboardLoading">
          <el-row :gutter="16" class="stats-row">
            <el-col :span="6">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-icon health">
                  <el-icon><Monitor /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label">系统健康</div>
                  <div class="stat-value" :class="healthStatusClass">
                    {{ healthData.status || 'unknown' }}
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-icon cpu">
                  <el-icon><Cpu /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label">CPU使用率</div>
                  <div class="stat-value">{{ performanceData.cpu?.percent || 0 }}%</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-icon memory">
                  <el-icon><Coin /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label">内存使用率</div>
                  <div class="stat-value">{{ performanceData.memory?.percent || 0 }}%</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-icon disk">
                  <el-icon><Folder /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label">磁盘使用率</div>
                  <div class="stat-value">{{ performanceData.disk?.percent || 0 }}%</div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" class="stats-row">
            <el-col :span="8">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-icon alerts">
                  <el-icon><Warning /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label">活跃告警</div>
                  <div class="stat-value">{{ activeAlertCount }}</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-icon db">
                  <el-icon><Box /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label">数据库大小</div>
                  <div class="stat-value">{{ dbStats.database_size_mb || 0 }} MB</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-icon requests">
                  <el-icon><Connection /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label">API请求数</div>
                  <div class="stat-value">{{ apiStats.total_requests || 0 }}</div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-card shadow="hover" class="health-checks-card">
            <template #header>
              <div class="card-header">
                <span>健康检查详情</span>
                <el-button type="primary" link @click="loadDashboard">刷新</el-button>
              </div>
            </template>
            <el-table :data="healthChecks" style="width: 100%">
              <el-table-column prop="name" label="检查项" width="180" />
              <el-table-column prop="status" label="状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="消息" />
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="性能监控" name="performance">
        <div v-loading="performanceLoading">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <span>CPU & 内存</span>
                </template>
                <div class="metric-item">
                  <span class="metric-label">CPU使用率:</span>
                  <el-progress :percentage="performanceData.cpu?.percent || 0" :color="getProgressColor(performanceData.cpu?.percent)" />
                </div>
                <div class="metric-item">
                  <span class="metric-label">CPU核心数:</span>
                  <span>{{ performanceData.cpu?.count || 0 }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">内存使用率:</span>
                  <el-progress :percentage="performanceData.memory?.percent || 0" :color="getProgressColor(performanceData.memory?.percent)" />
                </div>
                <div class="metric-item">
                  <span class="metric-label">内存总量:</span>
                  <span>{{ formatBytes(performanceData.memory?.total) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">内存可用:</span>
                  <span>{{ formatBytes(performanceData.memory?.available) }}</span>
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <span>磁盘 & 网络</span>
                </template>
                <div class="metric-item">
                  <span class="metric-label">磁盘使用率:</span>
                  <el-progress :percentage="performanceData.disk?.percent || 0" :color="getProgressColor(performanceData.disk?.percent)" />
                </div>
                <div class="metric-item">
                  <span class="metric-label">磁盘总量:</span>
                  <span>{{ formatBytes(performanceData.disk?.total) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">磁盘可用:</span>
                  <span>{{ formatBytes(performanceData.disk?.free) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">网络发送:</span>
                  <span>{{ formatBytes(performanceData.network?.bytes_sent) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">网络接收:</span>
                  <span>{{ formatBytes(performanceData.network?.bytes_recv) }}</span>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-card shadow="hover" class="process-info-card">
            <template #header>
              <span>进程信息</span>
            </template>
            <div class="metric-item">
              <span class="metric-label">进程ID:</span>
              <span>{{ performanceData.process?.pid }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">进程CPU占用:</span>
              <span>{{ performanceData.process?.cpu_percent }}%</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">进程内存占用:</span>
              <span>{{ performanceData.process?.memory_percent }}%</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">线程数:</span>
              <span>{{ performanceData.process?.num_threads }}</span>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="数据库监控" name="database">
        <div v-loading="databaseLoading">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>数据库统计</span>
                <el-button type="primary" link @click="loadDatabaseStats">刷新</el-button>
              </div>
            </template>
            <el-row :gutter="16" class="db-stats-row">
              <el-col :span="8">
                <div class="db-stat-item">
                  <span class="db-stat-label">数据库大小</span>
                  <span class="db-stat-value">{{ dbStats.database_size_mb }} MB</span>
                </div>
              </el-col>
            </el-row>
            <el-table :data="dbStats.tables" style="width: 100%; margin-top: 16px;">
              <el-table-column prop="name" label="表名" />
              <el-table-column prop="count" label="记录数" align="right" />
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="API统计" name="api-stats">
        <div v-loading="apiLoading">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>API请求统计</span>
                <el-button type="primary" link @click="loadApiStats">刷新</el-button>
              </div>
            </template>
            <el-row :gutter="16" class="api-stats-row">
              <el-col :span="6">
                <div class="api-stat-item">
                  <span class="api-stat-label">总请求数</span>
                  <span class="api-stat-value">{{ apiStats.total_requests }}</span>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="api-stat-item">
                  <span class="api-stat-label">平均响应时间</span>
                  <span class="api-stat-value">{{ apiStats.avg_response_time }} ms</span>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="api-stat-item">
                  <span class="api-stat-label">错误率</span>
                  <span class="api-stat-value">{{ apiStats.error_rate }}%</span>
                </div>
              </el-col>
            </el-row>
            <el-table :data="apiStats.top_endpoints" style="width: 100%; margin-top: 16px;" title="Top Endpoints">
              <el-table-column prop="endpoint" label="端点" />
              <el-table-column prop="count" label="请求次数" align="right" />
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="告警管理" name="alerts">
        <div v-loading="alertsLoading">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>告警列表</span>
                <el-button type="primary" link @click="loadAlerts">刷新</el-button>
              </div>
            </template>
            <el-table :data="alertList" style="width: 100%">
              <el-table-column prop="id" label="ID" width="120" />
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="level" label="级别" width="100">
                <template #default="{ row }">
                  <el-tag :type="getAlertLevelType(row.level)" size="small">
                    {{ row.level }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'active' ? 'danger' : 'success'" size="small">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180" />
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button
                    v-if="row.status === 'active'"
                    type="primary"
                    link
                    size="small"
                    @click="handleResolveAlert(row.id)">
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
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>系统日志</span>
                <div>
                  <el-select v-model="logFilter.level" placeholder="日志级别" clearable style="width: 120px; margin-right: 8px;">
                    <el-option label="DEBUG" value="DEBUG" />
                    <el-option label="INFO" value="INFO" />
                    <el-option label="WARNING" value="WARNING" />
                    <el-option label="ERROR" value="ERROR" />
                  </el-select>
                  <el-button type="primary" link @click="loadLogs">刷新</el-button>
                </div>
              </div>
            </template>
            <el-table :data="logList" style="width: 100%">
              <el-table-column prop="timestamp" label="时间" width="180" />
              <el-table-column prop="level" label="级别" width="100">
                <template #default="{ row }">
                  <el-tag :type="getLogLevelType(row.level)" size="small">
                    {{ row.level }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="source" label="来源" width="120" />
              <el-table-column prop="message" label="消息" />
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="系统信息" name="system-info">
        <div v-loading="systemInfoLoading">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>系统信息</span>
                <el-button type="primary" link @click="loadSystemInfo">刷新</el-button>
              </div>
            </template>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">平台:</span>
                <span class="info-value">{{ systemInfo.platform }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">主机名:</span>
                <span class="info-value">{{ systemInfo.hostname }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Python版本:</span>
                <span class="info-value">{{ systemInfo.python_version }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">CPU核心数:</span>
                <span class="info-value">{{ systemInfo.cpu_count }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">内存总量:</span>
                <span class="info-value">{{ formatBytes(systemInfo.memory_total) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">启动时间:</span>
                <span class="info-value">{{ systemInfo.boot_time }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">应用名称:</span>
                <span class="info-value">{{ systemInfo.app?.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">应用版本:</span>
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
  Monitor, Cpu, Coin, Folder, Warning, Connection, Box
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
.monitoring-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  margin-bottom: 8px;
}

.page-header p {
  color: #909399;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
}

.stat-icon.health {
  background: #ecf5ff;
  color: #409eff;
}

.stat-icon.cpu {
  background: #f0f9ff;
  color: #36cfc9;
}

.stat-icon.memory {
  background: #fff7e6;
  color: #faad14;
}

.stat-icon.disk {
  background: #e6fffb;
  color: #13c2c2;
}

.stat-icon.alerts {
  background: #fff1f0;
  color: #ff4d4f;
}

.stat-icon.db {
  background: #f6ffed;
  color: #52c41a;
}

.stat-icon.requests {
  background: #f9f0ff;
  color: #722ed1;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-value.status-healthy {
  color: #67c23a;
}

.stat-value.status-warning {
  color: #e6a23c;
}

.stat-value.status-critical {
  color: #f56c6c;
}

.health-checks-card {
  margin-top: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.metric-item .metric-label {
  width: 140px;
  color: #606266;
}

.process-info-card {
  margin-top: 16px;
}

.db-stats-row, .api-stats-row {
  margin-bottom: 16px;
}

.db-stat-item, .api-stat-item {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.db-stat-label, .api-stat-label {
  display: block;
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.db-stat-value, .api-stat-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.info-label {
  display: block;
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.info-value {
  font-size: 16px;
  color: #303133;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .monitoring-container {
    padding: 12px;
  }

  .page-header {
    margin-bottom: 16px;
  }

  .page-header h1 {
    font-size: 18px;
    margin-bottom: 4px;
  }

  .page-header p {
    font-size: 12px;
  }

  .stats-row {
    margin-bottom: 12px;
  }

  .stats-row .el-col {
    width: 50%;
    max-width: 50%;
    flex: 0 0 50%;
    margin-bottom: 8px;
    padding: 0 6px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-card :deep(.el-card__body) {
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .stat-value {
    font-size: 18px;
  }

  .health-checks-card,
  .performance-card,
  .alerts-card,
  .logs-card {
    margin-bottom: 12px;
  }

  .card-header {
    font-size: 14px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .pagination {
    justify-content: center;
    margin-top: 16px;
  }

  :deep(.el-pagination) {
    font-size: 11px;
    flex-wrap: wrap;
    gap: 4px;
  }

  :deep(.el-pagination__sizes),
  :deep(.el-pagination__jump) {
    display: none !important;
  }

  .chart-container {
    height: 200px !important;
  }

  .metric-card {
    padding: 12px;
  }

  .metric-value {
    font-size: 20px;
  }

  .info-grid {
    grid-template-columns: 1fr !important;
    gap: 8px;
  }

  .info-item {
    padding: 10px;
  }

  .info-label {
    font-size: 12px;
  }

  .info-value {
    font-size: 14px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .el-dialog__header {
    padding: 12px !important;
  }

  .el-dialog__title {
    font-size: 16px !important;
  }

  .el-dialog__body {
    padding: 12px !important;
    max-height: 60vh !important;
    overflow-y: auto !important;
  }

  .el-dialog__footer {
    padding: 12px !important;
  }
}

@media screen and (max-width: 480px) {
  .monitoring-container {
    padding: 8px;
  }

  .page-header h1 {
    font-size: 16px;
  }

  .stats-row .el-col {
    width: 100%;
    max-width: 100%;
    flex: 0 0 100%;
  }

  .stat-card :deep(.el-card__body) {
    padding: 10px;
  }

  .stat-icon {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }

  .stat-value {
    font-size: 16px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .chart-container {
    height: 180px !important;
  }
}
</style>
