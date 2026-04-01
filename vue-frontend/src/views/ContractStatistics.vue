<template>
  <div class="contract-statistics">
    <div class="page-header">
      <h2>合同统计报表</h2>
      <el-button type="primary" @click="fetchStatistics">刷新</el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total_contracts || 0 }}</div>
            <div class="stat-label">合同总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ formatAmount(statistics.total_amount) }}</div>
            <div class="stat-label">合同总金额</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ statistics.active_deliveries || 0 }}</div>
            <div class="stat-label">进行中交付</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ statistics.pending_payments || 0 }}</div>
            <div class="stat-label">待付款项</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>合同状态分布</span>
            </div>
          </template>
          <div class="chart-container">
            <el-table :data="statusData" stripe>
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  {{ getStatusName(row.status) }}
                </template>
              </el-table-column>
              <el-table-column prop="count" label="数量" />
              <el-table-column label="占比">
                <template #default="{ row }">
                  {{ ((row.count / statistics.total_contracts) * 100).toFixed(1) }}%
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>合同类型分布</span>
            </div>
          </template>
          <div class="chart-container">
            <el-table :data="typeData" stripe>
              <el-table-column prop="type" label="类型">
                <template #default="{ row }">
                  {{ getTypeName(row.type) }}
                </template>
              </el-table-column>
              <el-table-column prop="count" label="数量" />
              <el-table-column label="占比">
                <template #default="{ row }">
                  {{ ((row.count / statistics.total_contracts) * 100).toFixed(1) }}%
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>风险等级分布</span>
            </div>
          </template>
          <div class="chart-container">
            <el-table :data="riskData" stripe>
              <el-table-column prop="level" label="风险等级">
                <template #default="{ row }">
                  <el-tag :type="getRiskTag(row.level)">{{ getRiskName(row.level) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="count" label="数量" />
              <el-table-column label="占比">
                <template #default="{ row }">
                  {{ ((row.count / statistics.total_contracts) * 100).toFixed(1) }}%
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>区域分布</span>
            </div>
          </template>
          <div class="chart-container">
            <el-table :data="regionData" stripe>
              <el-table-column prop="region" label="区域" />
              <el-table-column prop="count" label="合同数" />
              <el-table-column prop="total_amount" label="总金额">
                <template #default="{ row }">
                  {{ formatAmount(row.total_amount) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>出口管制风险合同</span>
          <el-button type="danger" size="small" @click="fetchExportControl">查看详情</el-button>
        </div>
      </template>
      <el-table :data="exportControlContracts" v-loading="exportLoading" stripe max-height="300">
        <el-table-column prop="contract_no" label="合同编号" width="150" />
        <el-table-column prop="title" label="合同名称" show-overflow-tooltip />
        <el-table-column prop="country" label="国家" width="100" />
        <el-table-column prop="total_amount" label="金额" width="120">
          <template #default="{ row }">
            {{ formatAmount(row.total_amount, row.currency) }}
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_high_risk ? 'danger' : 'warning'">
              {{ row.is_high_risk ? '高风险' : '中风险' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            {{ getStatusName(row.status) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

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
const getRiskTag = (risk) => {
  const map = { low: 'success', medium: 'warning', high: 'danger', critical: 'danger' }
  return map[risk] || ''
}

const formatAmount = (amount) => {
  if (!amount) return '¥0.00'
  return `¥${parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
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
.contract-statistics {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 20px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 250px;
  overflow-y: auto;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .contract-statistics {
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
  .contract-statistics {
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
