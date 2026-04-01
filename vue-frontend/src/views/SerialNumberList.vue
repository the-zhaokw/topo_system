<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>序列号管理</span>
          <div>
            <el-button type="primary" @click="openCreateDialog">新增序列号</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索条件 -->
      <el-form :model="searchForm" :inline="true" label-width="80px" class="search-form">
        <el-form-item label="物料">
          <el-select v-model="searchForm.material_id" placeholder="请选择物料" clearable filterable>
            <el-option
              v-for="material in materials"
              :key="material.id"
              :label="`${material.material_code} - ${material.name}`"
              :value="material.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="在库待用" value="in_stock"></el-option>
            <el-option label="已领用" value="in_use"></el-option>
            <el-option label="已安装" value="installed"></el-option>
            <el-option label="已报废" value="scraped"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 序列号列表 -->
      <el-table :data="paginatedSerialNumbers" border stripe v-loading="loading">
        <el-table-column prop="serial_number" label="序列号" width="180"></el-table-column>
        <el-table-column prop="material_info.material_code" label="物料编码" width="150"></el-table-column>
        <el-table-column prop="material_info.name" label="物料名称" width="200"></el-table-column>
        <el-table-column prop="current_status" label="当前状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.current_status)">
              {{ getStatusText(scope.row.current_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="current_location" label="当前位置" width="150"></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteSerialNumber(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredSerialNumbers.length"
        class="pagination">
      </el-pagination>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="序列号" prop="serial_number">
          <el-input v-model="form.serial_number" :disabled="!!form.id"></el-input>
        </el-form-item>
        <el-form-item label="物料" prop="material_id">
          <el-select v-model="form.material_id" placeholder="请选择物料" filterable>
            <el-option
              v-for="material in materials"
              :key="material.id"
              :label="`${material.material_code} - ${material.name}`"
              :value="material.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="初始状态" prop="current_status">
          <el-select v-model="form.current_status" placeholder="请选择初始状态">
            <el-option label="在库待用" value="in_stock"></el-option>
            <el-option label="已领用" value="in_use"></el-option>
            <el-option label="已安装" value="installed"></el-option>
            <el-option label="已报废" value="scraped"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remarks" type="textarea"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitForm">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import materialsService from '@/services/materials'

// 数据响应式变量
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = computed(() => form.id ? '编辑序列号' : '新增序列号')

// 表单数据
const form = reactive({
  id: null,
  serial_number: '',
  material_id: null,
  current_status: 'in_stock',
  remarks: ''
})

// 搜索表单
const searchForm = reactive({
  material_id: null,
  status: null
})

// 分页数据
const currentPage = ref(1)
const pageSize = ref(20)

// 列表数据
const serialNumbers = ref([])
const materials = ref([])

// 表单验证规则
const rules = {
  serial_number: [
    { required: true, message: '请输入序列号', trigger: 'blur' }
  ],
  material_id: [
    { required: true, message: '请选择物料', trigger: 'change' }
  ],
  current_status: [
    { required: true, message: '请选择初始状态', trigger: 'change' }
  ]
}

// 计算属性 - 过滤后的序列号列表
const filteredSerialNumbers = computed(() => {
  return serialNumbers.value.filter(serial => {
    return (
      (!searchForm.material_id || serial.material_id === searchForm.material_id) &&
      (!searchForm.status || serial.current_status === searchForm.status)
    )
  })
})

// 计算属性 - 分页后的序列号列表
const paginatedSerialNumbers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSerialNumbers.value.slice(start, end)
})

// 状态文本映射
const getStatusText = (status) => {
  const statusMap = {
    'in_stock': '在库待用',
    'in_use': '已领用',
    'installed': '已安装',
    'scraped': '已报废'
  }
  return statusMap[status] || status
}

// 状态标签类型映射
const getStatusTagType = (status) => {
  const typeMap = {
    'in_stock': 'success',
    'in_use': 'warning',
    'installed': 'info',
    'scraped': 'danger'
  }
  return typeMap[status] || 'info'
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

// 加载序列号列表
const loadSerialNumbers = async () => {
  try {
    loading.value = true
    const data = await materialsService.getSerialNumbers()
    serialNumbers.value = data.map(sn => ({
      ...sn,
      material_info: {
        material_code: sn.material?.material_code || '',
        name: sn.material?.name || ''
      }
    }))
  } catch (error) {
    ElMessage.error('加载序列号列表失败: ' + error.message)
  } finally {
    loading.value = false
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

// 打开创建对话框
const openCreateDialog = () => {
  resetForm()
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (row) => {
  Object.assign(form, {
    id: row.id,
    serial_number: row.serial_number,
    material_id: row.material_id,
    current_status: row.current_status,
    remarks: row.remarks || ''
  })
  dialogVisible.value = true
}

// 提交表单
const formRef = ref(null)
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      const formData = {
        serial_number: form.serial_number,
        material_id: form.material_id,
        current_status: form.current_status,
        remarks: form.remarks
      }
      
      if (form.id) {
        // 编辑操作
        await materialsService.updateSerialNumber(form.id, formData)
        ElMessage.success('序列号更新成功')
      } else {
        // 创建操作
        await materialsService.createSerialNumber(formData)
        ElMessage.success('序列号创建成功')
      }
      
      dialogVisible.value = false
      loadSerialNumbers()
    } catch (error) {
      ElMessage.error((form.id ? '更新' : '创建') + '序列号失败: ' + error.message)
    }
  })
}

// 删除序列号
const deleteSerialNumber = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除该序列号吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await materialsService.deleteSerialNumber(id)
    ElMessage.success('序列号删除成功')
    loadSerialNumbers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除序列号失败: ' + error.message)
    }
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 重置搜索
const resetSearch = () => {
  searchForm.material_id = null
  searchForm.status = null
  currentPage.value = 1
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    serial_number: '',
    material_id: null,
    current_status: 'in_stock',
    remarks: ''
  })
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 组件挂载时加载数据
onMounted(() => {
  loadSerialNumbers()
  loadMaterials()
})
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .serial-number-list {
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
  .serial-number-list {
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