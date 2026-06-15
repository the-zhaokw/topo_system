<template>
  <div class="inventory-list-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Box /></el-icon>
          </div>
          <div class="title-text">
            <h1>库存管理</h1>
            <p class="subtitle">管理物料库存、仓库和库位信息</p>
          </div>
        </div>
        <el-button type="primary" class="btn-gradient" @click="showTransactionDialog = true">
          <el-icon><Plus /></el-icon>
          库存交易
        </el-button>
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
              <div class="stat-value">{{ stats.total_quantity || 0 }}</div>
              <div class="stat-label">库存总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-warning">
            <div class="stat-icon-wrapper stat-icon-wrapper-warning">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.low_stock_count || 0 }}</div>
              <div class="stat-label">库存预警</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-in">
            <div class="stat-icon-wrapper stat-icon-wrapper-in">
              <el-icon><Download /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.monthly_in || 0 }}</div>
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
              <div class="stat-value">{{ stats.monthly_out || 0 }}</div>
              <div class="stat-label">本月出库</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索筛选区域 -->
    <div class="filter-section animate-fade-in-up delay-200">
      <el-card class="filter-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Filter /></el-icon>
              筛选条件
            </span>
          </div>
        </template>
        <el-form :model="searchForm" inline class="filter-form">
          <el-form-item label="物料">
            <el-select v-model="searchForm.material_id" placeholder="请选择物料" clearable filterable class="filter-select">
              <el-option 
                v-for="material in materials" 
                :key="material.id" 
                :label="`${material.code} - ${material.name}`" 
                :value="material.id"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="仓库">
            <el-select v-model="searchForm.warehouse_id" placeholder="请选择仓库" clearable class="filter-select">
              <el-option 
                v-for="warehouse in warehouses" 
                :key="warehouse.id" 
                :label="warehouse.name" 
                :value="warehouse.id"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="库位">
            <el-select v-model="searchForm.location_id" placeholder="请选择库位" clearable class="filter-select">
              <el-option 
                v-for="location in locations" 
                :key="location.id" 
                :label="location.code" 
                :value="location.id"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadInventory" :loading="loading" class="btn-gradient">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="resetSearch" class="btn-secondary">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 库存列表 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><List /></el-icon>
              <h3>库存列表</h3>
              <span class="total-count">共 {{ pagination.total }} 条记录</span>
            </div>
          </div>
        </template>

        <el-table 
          :data="inventory" 
          v-loading="loading"
          stripe
          class="custom-table"
          style="width: 100%"
          :row-class-name="tableRowClassName">
          <el-table-column prop="material_code" label="物料编码" width="120" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.material_code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="material_name" label="物料名称" min-width="150">
            <template #default="{ row }">
              <div class="material-info">
                <div class="material-name">{{ row.material_name }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="warehouse_name" label="仓库" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="light" class="warehouse-tag">
                {{ row.warehouse_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="location_code" label="库位" width="100" align="center">
            <template #default="{ row }">
              <span class="location-code">{{ row.location_code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="库存数量" width="100" align="center">
            <template #default="{ row }">
              <span :class="{ 'warning-text': row.quantity < row.safety_stock, 'quantity-value': row.quantity >= row.safety_stock }">
                {{ row.quantity }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="safety_stock" label="安全库存" width="100" align="center">
            <template #default="{ row }">
              <span class="safety-stock">{{ row.safety_stock }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="max_stock" label="最大库存" width="100" align="center">
            <template #default="{ row }">
              <span class="max-stock">{{ row.max_stock }}</span>
            </template>
          </el-table-column>
          <el-table-column label="库存状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag 
                :type="getStockStatusTag(row.quantity, row.safety_stock, row.max_stock)"
                size="small"
                effect="light"
                class="status-tag"
              >
                {{ getStockStatusText(row.quantity, row.safety_stock, row.max_stock) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="last_transaction_date" label="最后交易时间" width="160" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatDate(row.last_transaction_date) }}</div>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-section">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
          </el-pagination>
        </div>
      </el-card>
    </div>

    <!-- 库存交易对话框 -->
    <el-dialog 
      title="库存交易" 
      v-model="showTransactionDialog"
      width="500px"
      class="transaction-dialog"
    >
      <el-form :model="transactionForm" :rules="transactionRules" ref="transactionFormRef" label-width="100px">
        <el-form-item label="交易类型" prop="transaction_type">
          <el-select v-model="transactionForm.transaction_type" placeholder="请选择交易类型" style="width: 100%">
            <el-option label="入库" value="in">
              <el-icon style="margin-right: 8px;"><Download /></el-icon>入库
            </el-option>
            <el-option label="出库" value="out">
              <el-icon style="margin-right: 8px;"><Upload /></el-icon>出库
            </el-option>
            <el-option label="调拨" value="transfer">
              <el-icon style="margin-right: 8px;"><Switch /></el-icon>调拨
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="物料" prop="material_id">
          <el-select v-model="transactionForm.material_id" placeholder="请选择物料" filterable style="width: 100%">
            <el-option 
              v-for="material in materials" 
              :key="material.id" 
              :label="`${material.code} - ${material.name}`" 
              :value="material.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="仓库" prop="warehouse_id">
          <el-select v-model="transactionForm.warehouse_id" placeholder="请选择仓库" style="width: 100%">
            <el-option 
              v-for="warehouse in warehouses" 
              :key="warehouse.id" 
              :label="warehouse.name" 
              :value="warehouse.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="库位" prop="location_id">
          <el-select v-model="transactionForm.location_id" placeholder="请选择库位" style="width: 100%">
            <el-option 
              v-for="location in filteredLocations" 
              :key="location.id" 
              :label="location.code" 
              :value="location.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number 
            v-model="transactionForm.quantity" 
            :min="1" 
            :precision="0"
            style="width: 100%"
          ></el-input-number>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input 
            type="textarea" 
            v-model="transactionForm.notes" 
            placeholder="请输入交易备注"
            :rows="3"
          ></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showTransactionDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTransaction" :loading="submitting" class="btn-gradient">
          提交交易
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Box, Plus, Warning, Download, Upload, Filter, Search, Refresh, List, Switch } from '@element-plus/icons-vue'
import materialsService from '@/services/materials'
import { formatDate } from '@/utils/dateUtils'

export default {
  name: 'InventoryList',
  components: {
    Box,
    Plus,
    Warning,
    Download,
    Upload,
    Filter,
    Search,
    Refresh,
    List,
    Switch
  },
  setup() {
    const inventory = ref([])
    const materials = ref([])
    const warehouses = ref([])
    const locations = ref([])
    const stats = ref({})
    const loading = ref(false)
    const showTransactionDialog = ref(false)
    const submitting = ref(false)
    const transactionFormRef = ref(null)
    
    const searchForm = ref({
      material_id: null,
      warehouse_id: null,
      location_id: null
    })

    const transactionForm = ref({
      transaction_type: 'in',
      material_id: null,
      warehouse_id: null,
      location_id: null,
      quantity: 1,
      notes: ''
    })

    const pagination = ref({
      currentPage: 1,
      pageSize: 10,
      total: 0
    })

    const transactionRules = {
      transaction_type: [
        { required: true, message: '请选择交易类型', trigger: 'change' }
      ],
      material_id: [
        { required: true, message: '请选择物料', trigger: 'change' }
      ],
      warehouse_id: [
        { required: true, message: '请选择仓库', trigger: 'change' }
      ],
      quantity: [
        { required: true, message: '请输入数量', trigger: 'blur' }
      ]
    }

    const filteredLocations = computed(() => {
      if (!transactionForm.value.warehouse_id) {
        return locations.value
      }
      return locations.value.filter(location => 
        location.warehouse_id === transactionForm.value.warehouse_id
      )
    })

    const getStockStatusText = (quantity, safetyStock, maxStock) => {
      if (quantity <= 0) return '缺货'
      if (quantity < safetyStock) return '低库存'
      if (quantity > maxStock) return '超储'
      return '正常'
    }

    const getStockStatusTag = (quantity, safetyStock, maxStock) => {
      if (quantity <= 0) return 'danger'
      if (quantity < safetyStock) return 'warning'
      if (quantity > maxStock) return 'info'
      return 'success'
    }

    // 表格行类名 - 用于库存预警行特殊标识
    const tableRowClassName = ({ row }) => {
      if (row.quantity <= 0) {
        return 'stock-danger-row'
      }
      if (row.quantity < row.safety_stock) {
        return 'stock-warning-row'
      }
      if (row.quantity > row.max_stock) {
        return 'stock-info-row'
      }
      return ''
    }

    const loadInventory = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.value.currentPage,
          per_page: pagination.value.pageSize,
          ...searchForm.value
        }
        
        // 移除空值参数
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null) {
            delete params[key]
          }
        })
        
        const response = await materialsService.getInventory(params)
        inventory.value = response.inventory || []
        pagination.value.total = response.total || 0
      } catch (error) {
        ElMessage.error('加载库存列表失败：' + error.message)
      } finally {
        loading.value = false
      }
    }

    const loadStats = async () => {
      try {
        const response = await materialsService.getInventoryStats()
        stats.value = response.stats || {}
      } catch (error) {
        console.error('加载库存统计失败：', error)
      }
    }

    const loadMaterials = async () => {
      try {
        const response = await materialsService.getMaterials()
        materials.value = Array.isArray(response) ? response : (response.materials || [])
      } catch (error) {
        ElMessage.error('加载物料列表失败：' + error.message)
      }
    }

    const loadWarehouses = async () => {
      try {
        const response = await materialsService.getWarehouses()
        warehouses.value = Array.isArray(response) ? response : (response.warehouses || [])
      } catch (error) {
        ElMessage.error('加载仓库列表失败：' + error.message)
      }
    }

    const loadLocations = async () => {
      try {
        const response = await materialsService.getLocations()
        locations.value = Array.isArray(response) ? response : (response.locations || [])
      } catch (error) {
        ElMessage.error('加载库位列表失败：' + error.message)
      }
    }

    const submitTransaction = async () => {
      if (!transactionFormRef.value) return
      
      try {
        await transactionFormRef.value.validate()
        submitting.value = true
        
        await materialsService.createTransaction(transactionForm.value)
        ElMessage.success('交易提交成功')
        
        showTransactionDialog.value = false
        loadInventory()
        loadStats()
      } catch (error) {
        if (error.errors) {
          ElMessage.error('请检查表单填写是否正确')
        } else {
          ElMessage.error('交易提交失败：' + error.message)
        }
      } finally {
        submitting.value = false
      }
    }

    const resetSearch = () => {
      searchForm.value = {
        material_id: null,
        warehouse_id: null,
        location_id: null
      }
      pagination.value.currentPage = 1
      loadInventory()
    }

    const resetTransactionForm = () => {
      transactionForm.value = {
        transaction_type: 'in',
        material_id: null,
        warehouse_id: null,
        location_id: null,
        quantity: 1,
        notes: ''
      }
      if (transactionFormRef.value) {
        transactionFormRef.value.clearValidate()
      }
    }

    const handleSizeChange = (size) => {
      pagination.value.pageSize = size
      pagination.value.currentPage = 1
      loadInventory()
    }

    const handleCurrentChange = (page) => {
      pagination.value.currentPage = page
      loadInventory()
    }

    onMounted(() => {
      loadStats()
      loadMaterials()
      loadWarehouses()
      loadLocations()
      loadInventory()
    })

    return {
      inventory,
      materials,
      warehouses,
      locations,
      stats,
      loading,
      showTransactionDialog,
      submitting,
      transactionFormRef,
      searchForm,
      transactionForm,
      pagination,
      transactionRules,
      filteredLocations,
      formatDate,
      getStockStatusText,
      getStockStatusTag,
      tableRowClassName,
      submitTransaction,
      resetSearch,
      resetTransactionForm,
      loadInventory,
      handleSizeChange,
      handleCurrentChange
    }
  },
  watch: {
    showTransactionDialog(val) {
      if (!val) {
        this.resetTransactionForm()
      }
    }
  }
}
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.inventory-list-container {
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

/* 4种不同的渐变配色 */
.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-warning::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-in::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-out::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-icon-wrapper-warning {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-in {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-out {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
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

.stat-card-warning .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-in .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-out .stat-value {
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

/* 筛选区域 */
.filter-section {
  margin-bottom: 24px;
}

.filter-card :deep(.el-card__header) {
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
  color: #0ea5e9;
  font-size: 18px;
}

.filter-form {
  padding: 10px 0;
}

.filter-select {
  width: 180px;
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

/* 内容区域 */
.content-section {
  margin-bottom: 20px;
}

/* 表格头部 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-title .el-icon {
  color: #0ea5e9;
  font-size: 20px;
}

.table-title h3 {
  margin: 0;
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
}

.total-count {
  font-size: 13px;
  color: #64748b;
  margin-left: 8px;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 12px;
  border-radius: 20px;
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

/* 库存预警行特殊颜色标识 */
.custom-table :deep(.stock-danger-row) {
  background-color: rgba(239, 68, 68, 0.08) !important;
}

.custom-table :deep(.stock-danger-row:hover) {
  background-color: rgba(239, 68, 68, 0.15) !important;
}

.custom-table :deep(.stock-warning-row) {
  background-color: rgba(245, 158, 11, 0.08) !important;
}

.custom-table :deep(.stock-warning-row:hover) {
  background-color: rgba(245, 158, 11, 0.15) !important;
}

.custom-table :deep(.stock-info-row) {
  background-color: rgba(59, 130, 246, 0.05) !important;
}

.custom-table :deep(.stock-info-row:hover) {
  background-color: rgba(59, 130, 246, 0.1) !important;
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

.material-info {
  line-height: 1.4;
}

.material-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.warehouse-tag {
  font-weight: 500;
  border-radius: 6px;
}

.location-code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(226, 232, 240, 0.6);
  padding: 2px 8px;
  border-radius: 4px;
}

.quantity-value {
  font-weight: 600;
  color: #1e293b;
}

.warning-text {
  color: #f59e0b;
  font-weight: 700;
}

.safety-stock,
.max-stock {
  font-size: 13px;
  color: #64748b;
}

.status-tag {
  font-weight: 500;
  border-radius: 6px;
}

.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 交易对话框 */
.transaction-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  padding: 20px;
  margin-right: 0;
}

.transaction-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.transaction-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
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

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .inventory-list-container {
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
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  .filter-form {
    flex-direction: column;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 12px;
    width: 100%;
  }

  .filter-select {
    width: 100% !important;
  }

  .table-header {
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

  .pagination-section {
    justify-content: center;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
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