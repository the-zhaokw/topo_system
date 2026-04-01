<template>
  <div class="warehouse-list">
    <div class="page-header">
      <h1>仓库管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <i class="el-icon-plus"></i> 新建仓库
      </el-button>
    </div>

    <el-card>
      <el-table :data="warehouses" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="code" label="仓库编码" width="120"></el-table-column>
        <el-table-column prop="name" label="仓库名称"></el-table-column>
        <el-table-column prop="type" label="仓库类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getWarehouseTypeTag(row.type)">
              {{ getWarehouseTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" show-overflow-tooltip></el-table-column>
        <el-table-column prop="contact_person" label="联系人" width="120"></el-table-column>
        <el-table-column prop="contact_phone" label="联系电话" width="120"></el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="mini" @click="editWarehouse(row)">编辑</el-button>
            <el-button size="mini" type="danger" @click="deleteWarehouse(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑仓库对话框 -->
    <el-dialog 
      :title="editMode ? '编辑仓库' : '新建仓库'" 
      v-model="showCreateDialog"
      width="500px"
    >
      <el-form :model="warehouseForm" :rules="rules" ref="warehouseFormRef" label-width="100px">
        <el-form-item label="仓库编码" prop="code">
          <el-input v-model="warehouseForm.code" placeholder="请输入仓库编码"></el-input>
        </el-form-item>
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="warehouseForm.name" placeholder="请输入仓库名称"></el-input>
        </el-form-item>
        <el-form-item label="仓库类型" prop="type">
          <el-select v-model="warehouseForm.type" placeholder="请选择仓库类型" style="width: 100%">
            <el-option label="普通仓库" value="normal"></el-option>
            <el-option label="原材料仓库" value="raw_material"></el-option>
            <el-option label="半成品仓库" value="semi_finished"></el-option>
            <el-option label="成品仓库" value="finished"></el-option>
            <el-option label="退货仓库" value="return"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="warehouseForm.address" placeholder="请输入仓库地址"></el-input>
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="warehouseForm.contact_person" placeholder="请输入联系人"></el-input>
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="warehouseForm.contact_phone" placeholder="请输入联系电话"></el-input>
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
          <el-switch v-model="warehouseForm.is_active"></el-switch>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitWarehouse" :loading="submitting">
          {{ editMode ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import materialsService from '@/services/materials'
import { formatDate } from '@/utils/dateUtils'

export default {
  name: 'WarehouseList',
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

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .warehouse-list {
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
  .warehouse-list {
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