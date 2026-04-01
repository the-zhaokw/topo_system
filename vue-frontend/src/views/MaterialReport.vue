<template>
  <div class="app-container">
    <el-tabs v-model="activeTab" class="report-tabs">
      <!-- 库存汇总报表 -->
      <el-tab-pane label="库存汇总报表" name="summary">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>库存汇总报表</span>
              <div>
                <el-button type="primary" @click="exportSummaryReport">导出</el-button>
              </div>
            </div>
          </template>

          <!-- 搜索条件 -->
          <el-form :model="summarySearchForm" :inline="true" label-width="80px" class="search-form">
            <el-form-item label="物料分类">
              <el-select v-model="summarySearchForm.category_id" placeholder="请选择物料分类" clearable>
                <el-option
                  v-for="category in categories"
                  :key="category.id"
                  :label="category.name"
                  :value="category.id">
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="仓库">
              <el-select v-model="summarySearchForm.warehouse_id" placeholder="请选择仓库" clearable>
                <el-option
                  v-for="warehouse in warehouses"
                  :key="warehouse.id"
                  :label="warehouse.name"
                  :value="warehouse.id">
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadSummaryReport">查询</el-button>
              <el-button @click="resetSummarySearch">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 报表数据 -->
          <el-table :data="summaryReportData" border stripe v-loading="summaryLoading" height="500">
            <el-table-column prop="material_code" label="物料编码" width="150" fixed></el-table-column>
            <el-table-column prop="material_name" label="物料名称" width="200" fixed></el-table-column>
            <el-table-column prop="category_name" label="物料分类" width="120"></el-table-column>
            <el-table-column prop="warehouse_name" label="仓库" width="120"></el-table-column>
            <el-table-column prop="total_quantity" label="总库存" width="100"></el-table-column>
            <el-table-column prop="total_locked" label="锁定库存" width="100"></el-table-column>
            <el-table-column prop="available_quantity" label="可用库存" width="100"></el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 物料流水报表 -->
      <el-tab-pane label="物料流水报表" name="flow">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>物料流水报表</span>
              <div>
                <el-button type="primary" @click="exportFlowReport">导出</el-button>
              </div>
            </div>
          </template>

          <!-- 搜索条件 -->
          <el-form :model="flowSearchForm" :inline="true" label-width="80px" class="search-form">
            <el-form-item label="物料">
              <el-select v-model="flowSearchForm.material_id" placeholder="请选择物料" clearable filterable>
                <el-option
                  v-for="material in materials"
                  :key="material.id"
                  :label="`${material.material_code} - ${material.name}`"
                  :value="material.id">
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="交易类型">
              <el-select v-model="flowSearchForm.transaction_type" placeholder="请选择交易类型" clearable>
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
                value-format="YYYY-MM-DD">
              </el-date-picker>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadFlowReport">查询</el-button>
              <el-button @click="resetFlowSearch">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 报表数据 -->
          <el-table :data="flowReportData" border stripe v-loading="flowLoading" height="500">
            <el-table-column prop="transaction_id" label="交易ID" width="100"></el-table-column>
            <el-table-column prop="transaction_type_cn" label="交易类型" width="100">
              <template #default="scope">
                <el-tag :type="getTransactionTypeTag(scope.row.transaction_type)">
                  {{ scope.row.transaction_type_cn }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="material_code" label="物料编码" width="150"></el-table-column>
            <el-table-column prop="material_name" label="物料名称" width="200"></el-table-column>
            <el-table-column prop="serial_number" label="序列号" width="180"></el-table-column>
            <el-table-column prop="from_warehouse" label="来源仓库" width="120"></el-table-column>
            <el-table-column prop="to_warehouse" label="目标仓库" width="120"></el-table-column>
            <el-table-column prop="quantity" label="数量" width="100"></el-table-column>
            <el-table-column prop="reference_id" label="关联单据" width="150"></el-table-column>
            <el-table-column prop="created_by" label="操作人" width="120"></el-table-column>
            <el-table-column prop="created_at" label="交易时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="remarks" label="备注" min-width="200"></el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 库存预警报表 -->
      <el-tab-pane label="库存预警报表" name="alert">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>库存预警报表</span>
              <div>
                <el-button type="primary" @click="exportAlertReport">导出</el-button>
              </div>
            </div>
          </template>

          <!-- 报表数据 -->
          <el-table :data="alertReportData" border stripe v-loading="alertLoading" height="500">
            <el-table-column prop="material_code" label="物料编码" width="150" fixed></el-table-column>
            <el-table-column prop="material_name" label="物料名称" width="200" fixed></el-table-column>
            <el-table-column prop="warehouse_name" label="仓库" width="120"></el-table-column>
            <el-table-column prop="location_name" label="库位" width="120"></el-table-column>
            <el-table-column prop="current_quantity" label="当前库存" width="100"></el-table-column>
            <el-table-column prop="safety_stock" label="安全库存" width="100"></el-table-column>
            <el-table-column prop="alert_level" label="预警级别" width="120">
              <template #default="scope">
                <el-tag :type="getAlertLevelTag(scope.row.alert_level)">
                  {{ scope.row.alert_level }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_updated" label="最后更新" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.last_updated) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import materialsService from '@/services/materials'
import { saveAs } from 'file-saver'

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
.app-container {
  padding: 20px;
}

.report-tabs {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .material-report {
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

  .search-form {
    margin-bottom: 16px;
  }

  .search-form .el-form-item {
    margin-bottom: 12px;
    width: 100%;
  }

  .search-form .el-input,
  .search-form .el-select {
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
  .material-report {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>