<template>
  <div class="warehouse-list-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Warehouse /></el-icon>
          </div>
          <div class="title-text">
            <h1>仓库管理</h1>
            <p class="subtitle">管理系统中的所有仓库信息</p>
          </div>
        </div>
        <el-button type="primary" class="btn-gradient" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建仓库
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalCount }}</div>
              <div class="stat-label">仓库总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-active">
            <div class="stat-icon-wrapper stat-icon-wrapper-active">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ activeCount }}</div>
              <div class="stat-label">启用中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-inactive">
            <div class="stat-icon-wrapper stat-icon-wrapper-inactive">
              <el-icon><Close /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ inactiveCount }}</div>
              <div class="stat-label">停用中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-inventory">
            <div class="stat-icon-wrapper stat-icon-wrapper-inventory">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalInventory }}</div>
              <div class="stat-label">总库存量</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 仓库列表 -->
    <div class="content-section animate-fade-in-up delay-200">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><List /></el-icon>
              <h3>仓库列表</h3>
              <span class="total-count">共 {{ totalCount }} 个仓库</span>
            </div>
          </div>
        </template>

        <el-table :data="warehouses" v-loading="loading" stripe class="custom-table" style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="code" label="仓库编码" width="120">
            <template #default="{ row }">
              <span class="code-text">{{ row.code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="仓库名称" min-width="150">
            <template #default="{ row }">
              <div class="warehouse-name">
                <el-icon><House /></el-icon>
                <span>{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="仓库类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getWarehouseTypeTag(row.type)" size="small" effect="light" class="type-tag">
                {{ getWarehouseTypeText(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="address" label="地址" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="address-cell">
                <el-icon><Location /></el-icon>
                <span>{{ row.address || '未设置' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="contact_person" label="联系人" width="120">
            <template #default="{ row }">
              <div class="contact-cell">
                <el-icon><User /></el-icon>
                <span>{{ row.contact_person || '未设置' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="contact_phone" label="联系电话" width="130">
            <template #default="{ row }">
              <span class="phone-text">{{ row.contact_phone || '未设置' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="90" align="center">
            <template #default="{ row }">
              <div class="status-wrapper">
                <span class="status-dot" :class="{ 'status-active': row.is_active, 'status-inactive': !row.is_active }"></span>
                <span class="status-text" :class="{ 'text-active': row.is_active, 'text-inactive': !row.is_active }">
                  {{ row.is_active ? '启用' : '停用' }}
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatDate(row.created_at) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link size="small" @click="editWarehouse(row)" class="action-btn">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button type="danger" link size="small" @click="deleteWarehouse(row)" class="action-btn">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 创建/编辑仓库对话框 -->
    <el-dialog 
      :title="editMode ? '编辑仓库' : '新建仓库'" 
      v-model="showCreateDialog"
      width="500px"
      class="warehouse-dialog"
      destroy-on-close
    >
      <el-form :model="warehouseForm" :rules="rules" ref="warehouseFormRef" label-width="100px" class="warehouse-form">
        <el-form-item label="仓库编码" prop="code">
          <el-input v-model="warehouseForm.code" placeholder="请输入仓库编码" prefix-icon="Key"></el-input>
        </el-form-item>
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="warehouseForm.name" placeholder="请输入仓库名称" prefix-icon="House"></el-input>
        </el-form-item>
        <el-form-item label="仓库类型" prop="type">
          <el-select v-model="warehouseForm.type" placeholder="请选择仓库类型" style="width: 100%">
            <el-option label="普通仓库" value="normal">
              <el-icon><House /></el-icon> 普通仓库
            </el-option>
            <el-option label="原材料仓库" value="raw_material">
              <el-icon><Box /></el-icon> 原材料仓库
            </el-option>
            <el-option label="半成品仓库" value="semi_finished">
              <el-icon><Collection /></el-icon> 半成品仓库
            </el-option>
            <el-option label="成品仓库" value="finished">
              <el-icon><Goods /></el-icon> 成品仓库
            </el-option>
            <el-option label="退货仓库" value="return">
              <el-icon><RefreshLeft /></el-icon> 退货仓库
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="warehouseForm.address" placeholder="请输入仓库地址" prefix-icon="Location"></el-input>
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="warehouseForm.contact_person" placeholder="请输入联系人" prefix-icon="User"></el-input>
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="warehouseForm.contact_phone" placeholder="请输入联系电话" prefix-icon="Phone"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="warehouseForm.description" 
            placeholder="请输入仓库描述"
            :rows="3"
          ></el-input>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch 
            v-model="warehouseForm.is_active"
            active-text="启用"
            inactive-text="停用"
            inline-prompt
          ></el-switch>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false" class="btn-secondary">取消</el-button>
          <el-button type="primary" @click="submitWarehouse" :loading="submitting" class="btn-gradient">
            {{ editMode ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import materialsService from '@/services/materials'
import { formatDate } from '@/utils/dateUtils'
import { 
  Warehouse, Plus, OfficeBuilding, Check, Close, Box, 
  List, House, Location, User, Edit, Delete, Key, 
  Collection, Goods, RefreshLeft, Phone 
} from '@element-plus/icons-vue'

export default {
  name: 'WarehouseList',
  components: {
    Warehouse, Plus, OfficeBuilding, Check, Close, Box,
    List, House, Location, User, Edit, Delete, Key,
    Collection, Goods, RefreshLeft, Phone
  },
  setup() {
    const warehouses = ref([])
    const loading = ref(false)
    const showCreateDialog = ref(false)
    const editMode = ref(false)
    const submitting = ref(false)
    const warehouseFormRef = ref(null)
    
    const warehouseForm = ref({
      code: '',
      name: '',
      type: 'normal',
      address: '',
      contact_person: '',
      contact_phone: '',
      description: '',
      is_active: true
    })

    const rules = {
      code: [
        { required: true, message: '请输入仓库编码', trigger: 'blur' }
      ],
      name: [
        { required: true, message: '请输入仓库名称', trigger: 'blur' }
      ],
      type: [
        { required: true, message: '请选择仓库类型', trigger: 'change' }
      ]
    }

    const warehouseTypes = {
      normal: { text: '普通仓库', tag: '' },
      raw_material: { text: '原材料仓库', tag: 'success' },
      semi_finished: { text: '半成品仓库', tag: 'warning' },
      finished: { text: '成品仓库', tag: 'primary' },
      return: { text: '退货仓库', tag: 'danger' }
    }

    // 统计数据计算
    const totalCount = computed(() => warehouses.value.length)
    const activeCount = computed(() => warehouses.value.filter(w => w.is_active).length)
    const inactiveCount = computed(() => warehouses.value.filter(w => !w.is_active).length)
    const totalInventory = computed(() => {
      // 如果有库存数据则累加，否则返回模拟数据
      return warehouses.value.reduce((sum, w) => sum + (w.inventory_count || 0), 0) || 0
    })

    const getWarehouseTypeText = (type) => {
      return warehouseTypes[type]?.text || type
    }

    const getWarehouseTypeTag = (type) => {
      return warehouseTypes[type]?.tag || ''
    }

    const loadWarehouses = async () => {
      loading.value = true
      try {
        const response = await materialsService.getWarehouses()
        warehouses.value = response || []
      } catch (error) {
        ElMessage.error('加载仓库列表失败：' + error.message)
      } finally {
        loading.value = false
      }
    }

    const editWarehouse = (warehouse) => {
      editMode.value = true
      warehouseForm.value = { ...warehouse }
      showCreateDialog.value = true
    }

    const deleteWarehouse = async (warehouse) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除仓库"${warehouse.name}"吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await materialsService.deleteWarehouse(warehouse.id)
        ElMessage.success('删除成功')
        loadWarehouses()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败：' + error.message)
        }
      }
    }

    const submitWarehouse = async () => {
      if (!warehouseFormRef.value) return
      
      try {
        await warehouseFormRef.value.validate()
        submitting.value = true
        
        if (editMode.value) {
          await materialsService.updateWarehouse(warehouseForm.value.id, warehouseForm.value)
          ElMessage.success('更新成功')
        } else {
          await materialsService.createWarehouse(warehouseForm.value)
          ElMessage.success('创建成功')
        }
        
        showCreateDialog.value = false
        loadWarehouses()
      } catch (error) {
        if (error.errors) {
          ElMessage.error('请检查表单填写是否正确')
        } else {
          ElMessage.error((editMode.value ? '更新' : '创建') + '失败：' + error.message)
        }
      } finally {
        submitting.value = false
      }
    }

    const resetForm = () => {
      editMode.value = false
      warehouseForm.value = {
        code: '',
        name: '',
        type: 'normal',
        address: '',
        contact_person: '',
        contact_phone: '',
        description: '',
        is_active: true
      }
      if (warehouseFormRef.value) {
        warehouseFormRef.value.clearValidate()
      }
    }

    onMounted(() => {
      loadWarehouses()
    })

    return {
      warehouses,
      loading,
      showCreateDialog,
      editMode,
      submitting,
      warehouseFormRef,
      warehouseForm,
      rules,
      totalCount,
      activeCount,
      inactiveCount,
      totalInventory,
      formatDate,
      getWarehouseTypeText,
      getWarehouseTypeTag,
      editWarehouse,
      deleteWarehouse,
      submitWarehouse,
      resetForm
    }
  },
  watch: {
    showCreateDialog(val) {
      if (!val) {
        this.resetForm()
      }
    }
  }
}
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.warehouse-list-container {
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

.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-active::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-inactive::before { background: linear-gradient(90deg, #ef4444, #f87171); }
.stat-card-inventory::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }

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

.stat-icon-wrapper-active {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-inactive {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 15px -3px rgba(239, 68, 68, 0.4);
}

.stat-icon-wrapper-inventory {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
  box-shadow: 0 4px 15px -3px rgba(59, 130, 246, 0.4);
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

.stat-card-active .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-inactive .stat-value {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-inventory .stat-value {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
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

.glass-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
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

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.15) 100%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(255, 255, 255, 0.3);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.35) 0%, rgba(255, 255, 255, 0.25) 100%);
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

.id-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.code-text {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.warehouse-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
}

.warehouse-name .el-icon {
  color: #0ea5e9;
}

.type-tag {
  font-weight: 500;
  border-radius: 6px;
}

.address-cell,
.contact-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #475569;
}

.address-cell .el-icon,
.contact-cell .el-icon {
  color: #94a3b8;
  font-size: 14px;
}

.phone-text {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #475569;
}

/* 状态样式 */
.status-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: all 0.3s;
}

.status-active {
  background: linear-gradient(135deg, #10b981, #34d399);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.status-inactive {
  background: linear-gradient(135deg, #ef4444, #f87171);
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.3);
}

.status-text {
  font-size: 13px;
  font-weight: 500;
}

.text-active {
  color: #059669;
}

.text-inactive {
  color: #dc2626;
}

.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.action-btn {
  transition: all 0.3s;
}

.action-btn:hover {
  transform: translateY(-1px);
}

/* 对话框样式 */
.warehouse-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  padding: 20px 24px;
  margin: 0;
}

.warehouse-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.warehouse-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: rgba(255, 255, 255, 0.8);
}

.warehouse-dialog :deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: white;
}

.warehouse-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.warehouse-form :deep(.el-input__wrapper),
.warehouse-form :deep(.el-textarea__inner) {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.warehouse-form :deep(.el-select) {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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
  .warehouse-list-container {
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

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }

  .action-btn {
    padding: 4px 8px;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
  }

  .warehouse-dialog :deep(.el-dialog) {
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
