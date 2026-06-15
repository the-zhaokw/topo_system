<template>
  <div class="material-report-container">
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
            <h1>物料报表</h1>
            <p class="subtitle">查看库存汇总、物料流水及库存预警报表</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalMaterials }}</div>
              <div class="stat-label">物料总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-value">
            <div class="stat-icon-wrapper stat-icon-wrapper-value">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ formatCurrency(totalInventoryValue) }}</div>
              <div class="stat-label">库存总值</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-in">
            <div class="stat-icon-wrapper stat-icon-wrapper-in">
              <el-icon><Download /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ monthlyInbound }}</div>
              <div class="stat-label">本月入库</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-out">
            <div class="stat-icon-wrapper stat-icon-wrapper-out">
              <el-icon><Upload /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ monthlyOutbound }}</div>
              <div class="stat-label">本月出库</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 报表标签页 -->
    <div class="report-tabs-container animate-fade-in-up delay-200">
      <el-tabs v-model="activeTab" class="report-tabs">
        <!-- 库存汇总报表 -->
        <el-tab-pane label="库存汇总报表" name="summary">
          <el-card class="glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><DataAnalysis /></el-icon>
                  库存汇总报表
                </span>
                <div>
                  <el-button type="primary" @click="exportSummaryReport" class="btn-gradient">
                    <el-icon><Download /></el-icon>
                    导出
                  </el-button>
                </div>
              </div>
            </template>

            <!-- 搜索条件 -->
            <el-form :model="summarySearchForm" :inline="true" label-width="80px" class="search-form">
              <el-form-item label="物料分类">
                <el-select v-model="summarySearchForm.category_id" placeholder="请选择物料分类" clearable class="filter-select">
                  <el-option
                    v-for="category in categories"
                    :key="category.id"
                    :label="category.name"
                    :value="category.id">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="仓库">
                <el-select v-model="summarySearchForm.warehouse_id" placeholder="请选择仓库" clearable class="filter-select">
                  <el-option
                    v-for="warehouse in warehouses"
                    :key="warehouse.id"
                    :label="warehouse.name"
                    :value="warehouse.id">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadSummaryReport" class="btn-gradient">
                  <el-icon><Search /></el-icon>
                  查询
                </el-button>
                <el-button @click="resetSummarySearch" class="btn-secondary">
                  <el-icon><Refresh /></el-icon>
                  重置
                </el-button>
              </el-form-item>
            </el-form>

            <!-- 报表数据 -->
            <el-table :data="summaryReportData" stripe v-loading="summaryLoading" height="500" class="custom-table">
              <el-table-column prop="material_code" label="物料编码" width="150" fixed>
                <template #default="{ row }">
                  <span class="id-badge">{{ row.material_code }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="material_name" label="物料名称" width="200" fixed></el-table-column>
              <el-table-column prop="category_name" label="物料分类" width="120">
                <template #default="{ row }">
                  <el-tag size="small" effect="light" class="category-tag">{{ row.category_name }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="warehouse_name" label="仓库" width="120"></el-table-column>
              <el-table-column prop="total_quantity" label="总库存" width="100" align="center">
                <template #default="{ row }">
                  <span class="quantity-value">{{ row.total_quantity }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="total_locked" label="锁定库存" width="100" align="center">
                <template #default="{ row }">
                  <span class="locked-value">{{ row.total_locked }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="available_quantity" label="可用库存" width="100" align="center">
                <template #default="{ row }">
                  <span class="available-value">{{ row.available_quantity }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <!-- 物料流水报表 -->
        <el-tab-pane label="物料流水报表" name="flow">
          <el-card class="glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><List /></el-icon>
                  物料流水报表
                </span>
                <div>
                  <el-button type="primary" @click="exportFlowReport" class="btn-gradient">
                    <el-icon><Download /></el-icon>
                    导出
                  </el-button>
                </div>
              </div>
            </template>

            <!-- 搜索条件 -->
            <el-form :model="flowSearchForm" :inline="true" label-width="80px" class="search-form">
              <el-form-item label="物料">
                <el-select v-model="flowSearchForm.material_id" placeholder="请选择物料" clearable filterable class="filter-select">
                  <el-option
                    v-for="material in materials"
                    :key="material.id"
                    :label="`${material.material_code} - ${material.name}`"
                    :value="material.id">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="交易类型">
                <el-select v-model="flowSearchForm.transaction_type" placeholder="请选择交易类型" clearable class="filter-select">
                  <el-option label="入库" value="in"></el-option>
                  <el-option label="出库" value="out"></el-option>
                  <el-option label="调拨" value="transfer"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="flowDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                  class="date-picker">
                </el-date-picker>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadFlowReport" class="btn-gradient">
                  <el-icon><Search /></el-icon>
                  查询
                </el-button>
                <el-button @click="resetFlowSearch" class="btn-secondary">
                  <el-icon><Refresh /></el-icon>
                  重置
                </el-button>
              </el-form-item>
            </el-form>

            <!-- 报表数据 -->
            <el-table :data="flowReportData" stripe v-loading="flowLoading" height="500" class="custom-table">
              <el-table-column prop="transaction_id" label="交易ID" width="100" align="center">
                <template #default="{ row }">
                  <span class="id-badge">#{{ row.transaction_id }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="transaction_type_cn" label="交易类型" width="100" align="center">
                <template #default="scope">
                  <el-tag :type="getTransactionTypeTag(scope.row.transaction_type)" size="small" effect="light" class="transaction-tag">
                    {{ scope.row.transaction_type_cn }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="material_code" label="物料编码" width="150"></el-table-column>
              <el-table-column prop="material_name" label="物料名称" width="200"></el-table-column>
              <el-table-column prop="serial_number" label="序列号" width="180">
                <template #default="{ row }">
                  <span class="serial-number">{{ row.serial_number || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="from_warehouse" label="来源仓库" width="120"></el-table-column>
              <el-table-column prop="to_warehouse" label="目标仓库" width="120"></el-table-column>
              <el-table-column prop="quantity" label="数量" width="100" align="center">
                <template #default="{ row }">
                  <span class="quantity-value">{{ row.quantity }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="reference_id" label="关联单据" width="150"></el-table-column>
              <el-table-column prop="created_by" label="操作人" width="120"></el-table-column>
              <el-table-column prop="created_at" label="交易时间" width="180">
                <template #default="scope">
                  <div class="timestamp">
                    <div class="time-main">{{ formatDate(scope.row.created_at) }}</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="remarks" label="备注" min-width="200">
                <template #default="{ row }">
                  <span class="remarks-text">{{ row.remarks || '-' }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <!-- 库存预警报表 -->
        <el-tab-pane label="库存预警报表" name="alert">
          <el-card class="glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Warning /></el-icon>
                  库存预警报表
                </span>
                <div>
                  <el-button type="primary" @click="exportAlertReport" class="btn-gradient">
                    <el-icon><Download /></el-icon>
                    导出
                  </el-button>
                </div>
              </div>
            </template>

            <!-- 报表数据 -->
            <el-table :data="alertReportData" stripe v-loading="alertLoading" height="500" class="custom-table">
              <el-table-column prop="material_code" label="物料编码" width="150" fixed>
                <template #default="{ row }">
                  <span class="id-badge">{{ row.material_code }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="material_name" label="物料名称" width="200" fixed></el-table-column>
              <el-table-column prop="warehouse_name" label="仓库" width="120"></el-table-column>
              <el-table-column prop="location_name" label="库位" width="120"></el-table-column>
              <el-table-column prop="current_quantity" label="当前库存" width="100" align="center">
                <template #default="{ row }">
                  <span class="quantity-value">{{ row.current_quantity }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="safety_stock" label="安全库存" width="100" align="center">
                <template #default="{ row }">
                  <span class="safety-value">{{ row.safety_stock }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="alert_level" label="预警级别" width="120" align="center">
                <template #default="scope">
                  <el-tag :type="getAlertLevelTag(scope.row.alert_level)" size="small" effect="light" class="alert-tag">
                    {{ scope.row.alert_level }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="last_updated" label="最后更新" width="180">
                <template #default="scope">
                  <div class="timestamp">
                    <div class="time-main">{{ formatDate(scope.row.last_updated) }}</div>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import materialsService from '@/services/materials'
import { saveAs } from 'file-saver'
import { Document, Box, Money, Download, Upload, DataAnalysis, List, Warning, Search, Refresh } from '@element-plus/icons-vue'

// 当前激活的标签页
const activeTab = ref('summary')

// 数据响应式变量
const summaryLoading = ref(false)
const flowLoading = ref(false)
const alertLoading = ref(false)

// 搜索表单
const summarySearchForm = reactive({
  category_id: null,
  warehouse_id: null
})

const flowSearchForm = reactive({
  material_id: null,
  transaction_type: null
})

const flowDateRange = ref([])

// 列表数据
const summaryReportData = ref([])
const flowReportData = ref([])
const alertReportData = ref([])
const categories = ref([])
const warehouses = ref([])
const materials = ref([])

// 统计数据计算
const totalMaterials = computed(() => {
  return summaryReportData.value.length
})

const totalInventoryValue = computed(() => {
  // 模拟计算库存总值
  return summaryReportData.value.reduce((sum, item) => {
    return sum + (item.total_quantity * 100)
  }, 0)
})

const monthlyInbound = computed(() => {
  // 模拟计算本月入库数量
  return flowReportData.value
    .filter(item => item.transaction_type === 'in')
    .reduce((sum, item) => sum + item.quantity, 0)
})

const monthlyOutbound = computed(() => {
  // 模拟计算本月出库数量
  return flowReportData.value
    .filter(item => item.transaction_type === 'out')
    .reduce((sum, item) => sum + item.quantity, 0)
})

// 格式化货币
const formatCurrency = (value) => {
  if (value >= 10000) {
    return '¥' + (value / 10000).toFixed(1) + '万'
  }
  return '¥' + value.toLocaleString()
}

// 交易类型标签类型映射
const getTransactionTypeTag = (type) => {
  const typeMap = {
    'in': 'success',
    'out': 'warning',
    'transfer': 'info'
  }
  return typeMap[type] || 'info'
}

// 预警级别标签类型映射
const getAlertLevelTag = (level) => {
  const levelMap = {
    '严重不足': 'danger',
    '库存偏低': 'warning',
    '正常': 'success'
  }
  return levelMap[level] || 'info'
}

// 日期格式化
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
}

// 加载库存汇总报表
const loadSummaryReport = async () => {
  try {
    summaryLoading.value = true
    const params = {}
    if (summarySearchForm.category_id) params.category_id = summarySearchForm.category_id
    if (summarySearchForm.warehouse_id) params.warehouse_id = summarySearchForm.warehouse_id
    
    const data = await materialsService.getInventorySummary(params)
    summaryReportData.value = data
  } catch (error) {
    ElMessage.error('加载库存汇总报表失败: ' + error.message)
  } finally {
    summaryLoading.value = false
  }
}

// 加载物料流水报表
const loadFlowReport = async () => {
  try {
    flowLoading.value = true
    const params = {}
    if (flowSearchForm.material_id) params.material_id = flowSearchForm.material_id
    if (flowSearchForm.transaction_type) params.transaction_type = flowSearchForm.transaction_type
    if (flowDateRange.value && flowDateRange.value.length === 2) {
      params.start_date = flowDateRange.value[0]
      params.end_date = flowDateRange.value[1]
    }
    
    const data = await materialsService.getTransactionReport(params)
    flowReportData.value = data
  } catch (error) {
    ElMessage.error('加载物料流水报表失败: ' + error.message)
  } finally {
    flowLoading.value = false
  }
}

// 加载库存预警报表
const loadAlertReport = async () => {
  try {
    alertLoading.value = true
    const data = await materialsService.getInventoryAlerts()
    alertReportData.value = data.map(alert => ({
      ...alert,
      alert_level: alert.current_quantity <= alert.safety_stock * 0.5 ? '严重不足' :
                   alert.current_quantity <= alert.safety_stock ? '库存偏低' : '正常'
    }))
  } catch (error) {
    ElMessage.error('加载库存预警报表失败: ' + error.message)
  } finally {
    alertLoading.value = false
  }
}

// 加载物料分类列表
const loadCategories = async () => {
  try {
    const data = await materialsService.getCategories()
    categories.value = data
  } catch (error) {
    ElMessage.error('加载物料分类列表失败: ' + error.message)
  }
}

// 加载仓库列表
const loadWarehouses = async () => {
  try {
    const data = await materialsService.getWarehouses()
    warehouses.value = data
  } catch (error) {
    ElMessage.error('加载仓库列表失败: ' + error.message)
  }
}

// 加载物料列表
const loadMaterials = async () => {
  try {
    const data = await materialsService.getMaterials()
    materials.value = data
  } catch (error) {
    ElMessage.error('加载物料列表失败: ' + error.message)
  }
}

// 重置库存汇总搜索
const resetSummarySearch = () => {
  summarySearchForm.category_id = null
  summarySearchForm.warehouse_id = null
}

// 重置物料流水搜索
const resetFlowSearch = () => {
  flowSearchForm.material_id = null
  flowSearchForm.transaction_type = null
  flowDateRange.value = []
}

// 导出库存汇总报表
const exportSummaryReport = () => {
  try {
    const csvContent = [
      ['物料编码', '物料名称', '物料分类', '仓库', '总库存', '锁定库存', '可用库存'],
      ...summaryReportData.value.map(item => [
        item.material_code,
        item.material_name,
        item.category_name,
        item.warehouse_name,
        item.total_quantity,
        item.total_locked,
        item.available_quantity
      ])
    ].map(row => row.join(',')).join('\n')
    
    const blob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' })
    saveAs(blob, '库存汇总报表.csv')
    ElMessage.success('库存汇总报表导出成功')
  } catch (error) {
    ElMessage.error('导出库存汇总报表失败: ' + error.message)
  }
}

// 导出物料流水报表
const exportFlowReport = () => {
  try {
    const csvContent = [
      ['交易ID', '交易类型', '物料编码', '物料名称', '序列号', '来源仓库', '目标仓库', '数量', '关联单据', '操作人', '交易时间', '备注'],
      ...flowReportData.value.map(item => [
        item.transaction_id,
        item.transaction_type_cn,
        item.material_code,
        item.material_name,
        item.serial_number,
        item.from_warehouse,
        item.to_warehouse,
        item.quantity,
        item.reference_id,
        item.created_by,
        formatDate(item.created_at),
        item.remarks
      ])
    ].map(row => row.join(',')).join('\n')
    
    const blob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' })
    saveAs(blob, '物料流水报表.csv')
    ElMessage.success('物料流水报表导出成功')
  } catch (error) {
    ElMessage.error('导出物料流水报表失败: ' + error.message)
  }
}

// 导出库存预警报表
const exportAlertReport = () => {
  try {
    const csvContent = [
      ['物料编码', '物料名称', '仓库', '库位', '当前库存', '安全库存', '预警级别', '最后更新'],
      ...alertReportData.value.map(item => [
        item.material_code,
        item.material_name,
        item.warehouse_name,
        item.location_name,
        item.current_quantity,
        item.safety_stock,
        item.alert_level,
        formatDate(item.last_updated)
      ])
    ].map(row => row.join(',')).join('\n')
    
    const blob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' })
    saveAs(blob, '库存预警报表.csv')
    ElMessage.success('库存预警报表导出成功')
  } catch (error) {
    ElMessage.error('导出库存预警报表失败: ' + error.message)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadSummaryReport()
  loadCategories()
  loadWarehouses()
  loadMaterials()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.material-report-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(56, 189, 248, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(14, 165, 233, 0.3) 0%, transparent 50%);
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
.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-value::before { background: linear-gradient(90deg, #f093fb, #f5576c); }
.stat-card-in::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-out::before { background: linear-gradient(90deg, #fc4a1a, #f7b733); }

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

/* 统计图标渐变配色 */
.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-icon-wrapper-value {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
}

.stat-icon-wrapper-in {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-out {
  background: linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%);
  color: #ea580c;
  box-shadow: 0 4px 15px -3px rgba(249, 115, 22, 0.4);
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

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-value .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-in .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-out .stat-value {
  background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* 报表标签页容器 */
.report-tabs-container {
  margin-bottom: 20px;
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

.glass-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
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
  color: #0ea5e9;
  font-size: 18px;
}

/* 搜索表单 */
.search-form {
  margin-bottom: 20px;
  padding: 10px 0;
}

.filter-select {
  width: 160px;
}

.date-picker {
  width: 260px;
}

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5);
}

.btn-secondary {
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(56, 189, 248, 0.1);
  border-color: #0ea5e9;
  color: #0ea5e9;
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(56, 189, 248, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

/* ID徽章 */
.id-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

/* 标签样式 */
.category-tag,
.transaction-tag,
.alert-tag {
  font-weight: 500;
  border-radius: 6px;
}

/* 数量样式 */
.quantity-value {
  font-weight: 600;
  color: #1e293b;
}

.locked-value {
  font-weight: 600;
  color: #f59e0b;
}

.available-value {
  font-weight: 600;
  color: #10b981;
}

.safety-value {
  font-weight: 600;
  color: #0ea5e9;
}

/* 序列号 */
.serial-number {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
}

/* 时间戳 */
.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

/* 备注文本 */
.remarks-text {
  color: #64748b;
  font-size: 13px;
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

/* 标签页样式优化 */
.report-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.report-tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: rgba(226, 232, 240, 0.6);
}

.report-tabs :deep(.el-tabs__item) {
  font-weight: 500;
  color: #64748b;
}

.report-tabs :deep(.el-tabs__item.is-active) {
  color: #7dd3fc;
  font-weight: 600;
}

.report-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #7dd3fc, #38bdf8);
  height: 3px;
  border-radius: 2px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .material-report-container {
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

  .search-form {
    flex-direction: column;
  }

  .search-form .el-form-item {
    margin-right: 0;
    margin-bottom: 12px;
    width: 100%;
  }

  .filter-select,
  .date-picker {
    width: 100% !important;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
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

  .el-table {
    font-size: 11px !important;
  }
}
</style>
