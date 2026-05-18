<template>
  <div class="contract-statistics-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Document /></el-icon>
          </div>
          <div class="title-text">
            <h1>合同统计报表</h1>
            <p class="subtitle">全面分析合同数据，掌握业务动态</p>
          </div>
        </div>
        <el-button type="primary" @click="fetchStatistics" class="btn-refresh">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="12" :md="8" :lg="4.8">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><DocumentChecked /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.total_contracts || 0 }}</div>
              <div class="stat-label">合同总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="8" :lg="4.8">
          <div class="stat-card stat-card-active">
            <div class="stat-icon-wrapper stat-icon-wrapper-active">
              <el-icon><Loading /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statusData.find(s => s.status === 'active')?.count || 0 }}</div>
              <div class="stat-label">进行中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="8" :lg="4.8">
          <div class="stat-card stat-card-completed">
            <div class="stat-icon-wrapper stat-icon-wrapper-completed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statusData.find(s => s.status === 'completed')?.count || 0 }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="8" :lg="4.8">
          <div class="stat-card stat-card-expired">
            <div class="stat-icon-wrapper stat-icon-wrapper-expired">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statusData.find(s => s.status === 'expired')?.count || 0 }}</div>
              <div class="stat-label">已过期</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="8" :lg="4.8">
          <div class="stat-card stat-card-amount">
            <div class="stat-icon-wrapper stat-icon-wrapper-amount">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ formatAmountShort(statistics.total_amount) }}</div>
              <div class="stat-label">总金额</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section animate-fade-in-up delay-200">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="glass-card chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><PieChart /></el-icon>
                  合同状态分布
                </span>
              </div>
            </template>
            <div class="chart-container">
              <el-table :data="statusData" stripe class="custom-table">
                <el-table-column prop="status" label="状态" min-width="100">
                  <template #default="{ row }">
                    <el-tag :type="getStatusTagType(row.status)" size="small" effect="light" class="status-tag">
                      {{ getStatusName(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="count" label="数量" width="80" align="center" />
                <el-table-column label="占比" width="100" align="center">
                  <template #default="{ row }">
                    <div class="progress-bar-wrapper">
                      <div class="progress-bar" :style="{ width: getPercentage(row.count) + '%', background: getStatusGradient(row.status) }"></div>
                      <span class="progress-text">{{ getPercentage(row.count) }}%</span>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="glass-card chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Collection /></el-icon>
                  合同类型分布
                </span>
              </div>
            </template>
            <div class="chart-container">
              <el-table :data="typeData" stripe class="custom-table">
                <el-table-column prop="type" label="类型" min-width="140">
                  <template #default="{ row }">
                    <span class="type-name">{{ getTypeName(row.type) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="count" label="数量" width="80" align="center" />
                <el-table-column label="占比" width="100" align="center">
                  <template #default="{ row }">
                    <div class="progress-bar-wrapper">
                      <div class="progress-bar" :style="{ width: getPercentage(row.count) + '%', background: getTypeGradient(row.type) }"></div>
                      <span class="progress-text">{{ getPercentage(row.count) }}%</span>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 风险等级和区域分布 -->
    <div class="charts-section animate-fade-in-up delay-300">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="glass-card chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Warning /></el-icon>
                  风险等级分布
                </span>
              </div>
            </template>
            <div class="chart-container">
              <el-table :data="riskData" stripe class="custom-table">
                <el-table-column prop="level" label="风险等级" min-width="100">
                  <template #default="{ row }">
                    <el-tag :type="getRiskTag(row.level)" size="small" effect="light" class="risk-tag">
                      {{ getRiskName(row.level) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="count" label="数量" width="80" align="center" />
                <el-table-column label="占比" width="100" align="center">
                  <template #default="{ row }">
                    <div class="progress-bar-wrapper">
                      <div class="progress-bar" :style="{ width: getPercentage(row.count) + '%', background: getRiskGradient(row.level) }"></div>
                      <span class="progress-text">{{ getPercentage(row.count) }}%</span>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="glass-card chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><MapLocation /></el-icon>
                  区域分布
                </span>
              </div>
            </template>
            <div class="chart-container">
              <el-table :data="regionData" stripe class="custom-table">
                <el-table-column prop="region" label="区域" min-width="100">
                  <template #default="{ row }">
                    <span class="region-name">{{ row.region }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="count" label="合同数" width="80" align="center" />
                <el-table-column prop="total_amount" label="总金额" min-width="120" align="right">
                  <template #default="{ row }">
                    <span class="amount-text">{{ formatAmount(row.total_amount) }}</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 出口管制风险合同 -->
    <div class="risk-section animate-fade-in-up delay-400">
      <el-card class="glass-card risk-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title card-title-danger">
              <el-icon><WarningFilled /></el-icon>
              出口管制风险合同
            </span>
            <el-button type="danger" size="small" @click="fetchExportControl" :loading="exportLoading" class="btn-danger-gradient">
              <el-icon><View /></el-icon>
              查看详情
            </el-button>
          </div>
        </template>
        <el-table :data="exportControlContracts" v-loading="exportLoading" stripe class="custom-table risk-table" max-height="300">
          <el-table-column prop="contract_no" label="合同编号" width="150">
            <template #default="{ row }">
              <span class="contract-no">{{ row.contract_no }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="合同名称" show-overflow-tooltip min-width="200">
            <template #default="{ row }">
              <span class="contract-title">{{ row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="country" label="国家" width="100" align="center">
            <template #default="{ row }">
              <span class="country-tag">{{ row.country }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="金额" width="140" align="right">
            <template #default="{ row }">
              <span class="amount-highlight">{{ formatAmount(row.total_amount, row.currency) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="风险等级" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_high_risk ? 'danger' : 'warning'" size="small" effect="dark" class="risk-level-tag">
                {{ row.is_high_risk ? '高风险' : '中风险' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)" size="small" effect="light">
                {{ getStatusName(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { Document, Refresh, DocumentChecked, Loading, CircleCheck, Timer, Money, PieChart, Collection, Warning, MapLocation, WarningFilled, View } from '@element-plus/icons-vue'

const loading = ref(false)
const exportLoading = ref(false)
const statistics = ref({})
const exportControlContracts = ref([])

const statusData = computed(() => {
  const dist = statistics.value.status_distribution || {}
  return Object.entries(dist).map(([status, count]) => ({ status, count }))
})

const typeData = computed(() => {
  const dist = statistics.value.type_distribution || {}
  return Object.entries(dist).map(([type, count]) => ({ type, count }))
})

const riskData = computed(() => {
  const dist = statistics.value.risk_distribution || {}
  return Object.entries(dist).map(([level, count]) => ({ level, count }))
})

const regionData = computed(() => {
  return statistics.value.region_stats || []
})

const statusMap = {
  draft: '草稿',
  pending_review: '待审核',
  pending_approval: '待审批',
  active: '执行中',
  completed: '已完成',
  expired: '已过期',
  terminated: '已终止',
  cancelled: '已取消',
  rejected: '已拒绝'
}

const typeMap = {
  equipment_sales: '设备销售合同',
  software_license: '软件许可合同',
  framework_agreement: '框架协议',
  purchase_order: '采购订单',
  engineering_service: '工程服务合同',
  maintenance_service: '维护服务合同',
  patent_license: '专利许可合同',
  oem_agreement: 'OEM代工协议',
  supply_agreement: '供应协议',
  international_project: '国际项目合同'
}

const riskMap = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '重大风险'
}

const getStatusName = (status) => statusMap[status] || status
const getTypeName = (type) => typeMap[type] || type
const getRiskName = (risk) => riskMap[risk] || risk

const getStatusTagType = (status) => {
  const map = {
    draft: 'info',
    pending_review: 'warning',
    pending_approval: 'warning',
    active: 'success',
    completed: 'success',
    expired: 'info',
    terminated: 'danger',
    cancelled: 'danger',
    rejected: 'danger'
  }
  return map[status] || ''
}

const getRiskTag = (risk) => {
  const map = { low: 'success', medium: 'warning', high: 'danger', critical: 'danger' }
  return map[risk] || ''
}

const getStatusGradient = (status) => {
  const map = {
    draft: 'linear-gradient(90deg, #94a3b8, #cbd5e1)',
    pending_review: 'linear-gradient(90deg, #f59e0b, #fbbf24)',
    pending_approval: 'linear-gradient(90deg, #f59e0b, #fbbf24)',
    active: 'linear-gradient(90deg, #10b981, #34d399)',
    completed: 'linear-gradient(90deg, #3b82f6, #60a5fa)',
    expired: 'linear-gradient(90deg, #6b7280, #9ca3af)',
    terminated: 'linear-gradient(90deg, #ef4444, #f87171)',
    cancelled: 'linear-gradient(90deg, #ef4444, #f87171)',
    rejected: 'linear-gradient(90deg, #ef4444, #f87171)'
  }
  return map[status] || 'linear-gradient(90deg, #667eea, #764ba2)'
}

const getTypeGradient = (type) => {
  const gradients = [
    'linear-gradient(90deg, #667eea, #764ba2)',
    'linear-gradient(90deg, #f093fb, #f5576c)',
    'linear-gradient(90deg, #4facfe, #00f2fe)',
    'linear-gradient(90deg, #43e97b, #38f9d7)',
    'linear-gradient(90deg, #fa709a, #fee140)',
    'linear-gradient(90deg, #a8edea, #fed6e3)',
    'linear-gradient(90deg, #ff9a9e, #fecfef)',
    'linear-gradient(90deg, #ffecd2, #fcb69f)',
    'linear-gradient(90deg, #ff8a80, #ffab91)',
    'linear-gradient(90deg, #b39ddb, #9575cd)'
  ]
  const types = Object.keys(typeMap)
  const index = types.indexOf(type)
  return gradients[index % gradients.length]
}

const getRiskGradient = (risk) => {
  const map = {
    low: 'linear-gradient(90deg, #10b981, #34d399)',
    medium: 'linear-gradient(90deg, #f59e0b, #fbbf24)',
    high: 'linear-gradient(90deg, #ef4444, #f87171)',
    critical: 'linear-gradient(90deg, #dc2626, #ef4444)'
  }
  return map[risk] || 'linear-gradient(90deg, #667eea, #764ba2)'
}

const getPercentage = (count) => {
  const total = statistics.value.total_contracts || 1
  return ((count / total) * 100).toFixed(1)
}

const formatAmount = (amount, currency = 'CNY') => {
  if (!amount) return '¥0.00'
  const symbol = currency === 'USD' ? '$' : '¥'
  return `${symbol}${parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const formatAmountShort = (amount) => {
  if (!amount) return '0'
  const num = parseFloat(amount)
  if (num >= 100000000) {
    return (num / 100000000).toFixed(1) + '亿'
  } else if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString('en-US')
}

const fetchStatistics = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/contracts/statistics')
    statistics.value = response.data
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

const fetchExportControl = async () => {
  exportLoading.value = true
  try {
    const response = await axios.get('/api/contracts/export-control')
    exportControlContracts.value = response.data.export_control_contracts
  } catch (error) {
    ElMessage.error('获取出口管制合同失败')
  } finally {
    exportLoading.value = false
  }
}

onMounted(() => {
  fetchStatistics()
  fetchExportControl()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.contract-statistics-container {
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

/* 5种不同的渐变配色 */
.stat-card-total::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card-active::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-completed::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.stat-card-expired::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-amount::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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

.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #667eea;
  box-shadow: 0 4px 15px -3px rgba(102, 126, 234, 0.4);
}

.stat-icon-wrapper-active {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-completed {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
  box-shadow: 0 4px 15px -3px rgba(59, 130, 246, 0.4);
}

.stat-icon-wrapper-expired {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-amount {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-active .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-completed .stat-value {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-expired .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-amount .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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

.charts-section {
  margin-bottom: 24px;
}

.chart-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

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

.card-title-danger {
  color: #dc2626;
}

.card-title-danger .el-icon {
  color: #dc2626;
}

.chart-container {
  padding: 10px 0;
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

/* 进度条 */
.progress-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  height: 6px;
  border-radius: 3px;
  transition: width 0.6s ease;
  flex: 1;
}

.progress-text {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
  min-width: 40px;
  text-align: right;
}

/* 状态标签 */
.status-tag,
.risk-tag {
  font-weight: 500;
  border-radius: 6px;
}

.type-name,
.region-name {
  font-weight: 500;
  color: #1e293b;
}

.amount-text {
  font-weight: 600;
  color: #059669;
  font-family: 'Monaco', 'Menlo', monospace;
}

/* 风险区域 */
.risk-section {
  margin-bottom: 20px;
}

.risk-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(239, 68, 68, 0.2);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(220, 38, 38, 0.05) 100%);
}

.risk-table :deep(.el-table__header th) {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(220, 38, 38, 0.08) 100%);
}

.contract-no {
  font-family: 'Monaco', 'Menlo', monospace;
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
}

.contract-title {
  font-weight: 500;
  color: #1e293b;
}

.country-tag {
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
}

.amount-highlight {
  font-weight: 700;
  color: #dc2626;
  font-family: 'Monaco', 'Menlo', monospace;
}

.risk-level-tag {
  font-weight: 600;
  border-radius: 6px;
}

/* 按钮样式 */
.btn-refresh {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s;
}

.btn-refresh:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
}

.btn-danger-gradient {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border: none;
  transition: all 0.3s;
}

.btn-danger-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(239, 68, 68, 0.5);
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

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .contract-statistics-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
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
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .charts-section {
    margin-bottom: 16px;
  }

  .chart-card {
    margin-bottom: 16px;
  }

  .chart-container {
    height: auto;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
  }

  .progress-bar-wrapper {
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
  }

  .progress-bar {
    width: 100%;
  }

  .progress-text {
    text-align: left;
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
    font-size: 18px;
  }

  .el-table {
    font-size: 11px !important;
  }
}
</style>
