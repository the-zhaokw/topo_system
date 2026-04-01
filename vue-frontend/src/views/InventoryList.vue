<template>
  <div class="inventory-list">
    <div class="page-header">
      <h1>库存管理</h1>
      <el-button type="primary" @click="showTransactionDialog = true">
        <i class="el-icon-plus"></i> 库存交易
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <i class="el-icon-box"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_materials || 0 }}</div>
                <div class="stat-label">物料种类</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon in-stock">
                <i class="el-icon-shopping-bag-1"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_quantity || 0 }}</div>
                <div class="stat-label">总库存量</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon low-stock">
                <i class="el-icon-warning"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.low_stock_count || 0 }}</div>
                <div class="stat-label">低库存物料</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon warehouses">
                <i class="el-icon-office-building"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_warehouses || 0 }}</div>
                <div class="stat-label">仓库数量</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索条件 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="物料">
          <el-select v-model="searchForm.material_id" placeholder="请选择物料" clearable filterable>
            <el-option 
              v-for="material in materials" 
              :key="material.id" 
              :label="`${material.code} - ${material.name}`" 
              :value="material.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="searchForm.warehouse_id" placeholder="请选择仓库" clearable>
            <el-option 
              v-for="warehouse in warehouses" 
              :key="warehouse.id" 
              :label="warehouse.name" 
              :value="warehouse.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="库位">
          <el-select v-model="searchForm.location_id" placeholder="请选择库位" clearable>
            <el-option 
              v-for="location in locations" 
              :key="location.id" 
              :label="location.code" 
              :value="location.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadInventory">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 库存列表 -->
    <el-card>
      <el-table :data="inventory" v-loading="loading">
        <el-table-column prop="material_code" label="物料编码" width="120"></el-table-column>
        <el-table-column prop="material_name" label="物料名称"></el-table-column>
        <el-table-column prop="warehouse_name" label="仓库" width="120"></el-table-column>
        <el-table-column prop="location_code" label="库位" width="120"></el-table-column>
        <el-table-column prop="quantity" label="库存数量" width="100">
          <template #default="{ row }">
            <span :class="{ 'low-stock': row.quantity < row.safety_stock }">
              {{ row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="safety_stock" label="安全库存" width="100"></el-table-column>
        <el-table-column prop="max_stock" label="最大库存" width="100"></el-table-column>
        <el-table-column label="库存状态" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="getStockStatusTag(row.quantity, row.safety_stock, row.max_stock)"
              size="small"
            >
              {{ getStockStatusText(row.quantity, row.safety_stock, row.max_stock) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_transaction_date" label="最后交易时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.last_transaction_date) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        ></el-pagination>
      </div>
    </el-card>

    <!-- 库存交易对话框 -->
    <el-dialog 
      title="库存交易" 
      v-model="showTransactionDialog"
      width="500px"
    >
      <el-form :model="transactionForm" :rules="transactionRules" ref="transactionFormRef" label-width="100px">
        <el-form-item label="交易类型" prop="transaction_type">
          <el-select v-model="transactionForm.transaction_type" placeholder="请选择交易类型" style="width: 100%">
            <el-option label="入库" value="in"></el-option>
            <el-option label="出库" value="out"></el-option>
            <el-option label="调拨" value="transfer"></el-option>
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
        <el-button type="primary" @click="submitTransaction" :loading="submitting">
          提交交易
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import materialsService from '@/services/materials'
import { formatDate } from '@/utils/dateUtils'

export default {
  name: 'InventoryList',
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
      if (quantity > maxStock) return 'warning'
      return 'success'
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
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 0;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stat-icon.total {
  background-color: #409EFF;
}

.stat-icon.in-stock {
  background-color: #67C23A;
}

.stat-icon.low-stock {
  background-color: #E6A23C;
}

.stat-icon.warehouses {
  background-color: #909399;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.search-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.low-stock {
  color: #E6A23C;
  font-weight: bold;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .inventory-list {
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
  .filter-form .el-select {
    width: 100% !important;
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
  .inventory-list {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>