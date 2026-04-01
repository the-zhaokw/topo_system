<template>
  <div class="material-list">
    <div class="page-header">
      <h1>物料主数据管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <i class="el-icon-plus"></i> 新建物料
        </el-button>
        <el-button type="success" @click="handleExport">
          <i class="el-icon-download"></i> 导出
        </el-button>
        <el-button type="warning" @click="showImportDialog = true">
          <i class="el-icon-upload2"></i> 导入
        </el-button>
      </div>
    </div>

    <!-- 搜索条件 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="物料编码">
          <el-input v-model="searchForm.code" placeholder="请输入物料编码" clearable></el-input>
        </el-form-item>
        <el-form-item label="物料名称">
          <el-input v-model="searchForm.name" placeholder="请输入物料名称" clearable></el-input>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category_id" placeholder="请选择分类" clearable>
            <el-option 
              v-for="category in categories" 
              :key="category.id" 
              :label="category.name" 
              :value="category.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadMaterials">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 物料列表 -->
    <el-card>
      <el-table :data="materials" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="material_code" label="物料编码" width="120"></el-table-column>
        <el-table-column prop="name" label="物料名称"></el-table-column>
        <el-table-column prop="specification" label="规格型号" show-overflow-tooltip></el-table-column>
        <el-table-column prop="unit" label="单位" width="80"></el-table-column>
        <el-table-column prop="category_name" label="分类" width="120"></el-table-column>
        <el-table-column prop="safety_stock" label="安全库存" width="100"></el-table-column>
        <el-table-column prop="supplier" label="供应商" width="120"></el-table-column>
        <el-table-column prop="total_quantity" label="当前库存" width="100">
          <template #default="{ row }">
            <span :class="{ 'low-stock-warning': row.is_low_stock }">
              {{ row.total_quantity || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="is_low_stock" label="库存预警" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.is_low_stock" type="danger">库存不足</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
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
            <el-button size="mini" @click="editMaterial(row)">编辑</el-button>
            <el-button size="mini" type="danger" @click="deleteMaterial(row)">删除</el-button>
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

    <!-- 创建/编辑物料对话框 -->
    <el-dialog 
      :title="editMode ? '编辑物料' : '新建物料'" 
      v-model="showCreateDialog"
      width="600px"
    >
      <el-form :model="materialForm" :rules="rules" ref="materialFormRef" label-width="100px">
        <el-form-item label="物料编码" prop="code">
          <el-input v-model="materialForm.code" placeholder="请输入物料编码"></el-input>
        </el-form-item>
        <el-form-item label="物料名称" prop="name">
          <el-input v-model="materialForm.name" placeholder="请输入物料名称"></el-input>
        </el-form-item>
        <el-form-item label="规格型号" prop="specification">
          <el-input v-model="materialForm.specification" placeholder="请输入规格型号"></el-input>
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="materialForm.unit" placeholder="请输入单位"></el-input>
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="materialForm.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option 
              v-for="category in categories" 
              :key="category.id" 
              :label="category.name" 
              :value="category.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="安全库存" prop="safety_stock">
          <el-input-number 
            v-model="materialForm.safety_stock" 
            :min="0" 
            :precision="2"
            style="width: 100%"
          ></el-input-number>
        </el-form-item>
        <el-form-item label="供应商" prop="supplier">
          <el-input v-model="materialForm.supplier" placeholder="请输入供应商名称"></el-input>
        </el-form-item>
        <el-form-item label="供应商编码" prop="supplier_code">
          <el-input v-model="materialForm.supplier_code" placeholder="请输入供应商物料编码"></el-input>
        </el-form-item>
        <el-form-item label="单价" prop="unit_cost">
          <el-input-number 
            v-model="materialForm.unit_cost" 
            :min="0" 
            :precision="2"
            :step="0.01"
            style="width: 100%"
          ></el-input-number>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="materialForm.description" 
            placeholder="请输入物料描述"
            :rows="3"
          ></el-input>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch 
            v-model="materialForm.status" 
            active-value="active" 
            inactive-value="inactive"
          ></el-switch>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitMaterial" :loading="submitting">
          {{ editMode ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入物料数据" width="500px">
      <el-alert
        title="导入说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <div>请上传Excel格式的文件(.xlsx, .xls)，文件应包含以下列：</div>
        <div style="margin-top: 8px;">物料编码*、物料名称、规格型号、单位、分类、安全库存、供应商、供应商编码、单价</div>
      </el-alert>

      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        :on-change="handleFileChange"
        accept=".xlsx,.xls"
        drag
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">只能上传xlsx/xls文件</div>
        </template>
      </el-upload>

      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import materialsService from '@/services/materials'
import { apiService } from '@/services/api'
import { formatDate } from '@/utils/dateUtils'

export default {
  name: 'MaterialList',
  setup() {
    const materials = ref([])
    const categories = ref([])
    const loading = ref(false)
    const showCreateDialog = ref(false)
    const showImportDialog = ref(false)
    const editMode = ref(false)
    const submitting = ref(false)
    const importing = ref(false)
    const materialFormRef = ref(null)
    
    const searchForm = ref({
      code: '',
      name: '',
      category_id: null
    })

    const materialForm = ref({
      code: '',
      name: '',
      specification: '',
      unit: '',
      category_id: null,
      safety_stock: 0,
      supplier: '',
      supplier_code: '',
      unit_cost: 0,
      description: '',
      status: 'active'
    })

    const pagination = ref({
      currentPage: 1,
      pageSize: 10,
      total: 0
    })

    const rules = {
      code: [
        { required: true, message: '请输入物料编码', trigger: 'blur' }
      ],
      name: [
        { required: true, message: '请输入物料名称', trigger: 'blur' }
      ],
      unit: [
        { required: true, message: '请输入单位', trigger: 'blur' }
      ],
      category_id: [
        { required: true, message: '请选择分类', trigger: 'change' }
      ]
    }

    const loadMaterials = async () => {
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
        
        const response = await materialsService.getMaterials(params)
        materials.value = Array.isArray(response) ? response : (response.materials || [])
        pagination.value = Array.isArray(response) ? { ...pagination.value, total: response.length } : { ...pagination.value, total: response.total || 0 }
      } catch (error) {
        ElMessage.error('加载物料列表失败：' + error.message)
      } finally {
        loading.value = false
      }
    }

    const loadCategories = async () => {
      try {
        const response = await materialsService.getCategories()
        categories.value = Array.isArray(response) ? response : (response.categories || [])
      } catch (error) {
        ElMessage.error('加载分类列表失败：' + error.message)
      }
    }

    const editMaterial = (material) => {
      editMode.value = true
      materialForm.value = { ...material }
      showCreateDialog.value = true
    }

    const deleteMaterial = async (material) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除物料"${material.name}"吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        await materialsService.deleteMaterial(material.id)
        ElMessage.success('删除成功')
        loadMaterials()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败：' + error.message)
        }
      }
    }

    const handleExport = async () => {
      try {
        const response = await apiService.materials.exportMaterials()
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        const timestamp = new Date().toISOString().slice(0,10).replace(/-/g, '')
        link.setAttribute('download', `materials_${timestamp}.xlsx`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        ElMessage.success('导出成功')
      } catch (error) {
        ElMessage.error('导出失败')
      }
    }

    const importFile = ref(null)

    const handleImport = async () => {
      if (!importFile.value) {
        ElMessage.warning('请选择要导入的文件')
        return
      }

      try {
        importing.value = true
        const formData = new FormData()
        formData.append('file', importFile.value)

        const response = await apiService.materials.importMaterials(formData)
        ElMessage.success(response.message || '导入成功')
        showImportDialog.value = false
        importFile.value = null
        loadMaterials()
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '导入失败')
      } finally {
        importing.value = false
      }
    }

    const handleFileChange = (file) => {
      importFile.value = file.raw
    }

    const submitMaterial = async () => {
      if (!materialFormRef.value) return
      
      try {
        await materialFormRef.value.validate()
        submitting.value = true
        
        if (editMode.value) {
          await materialsService.updateMaterial(materialForm.value.id, materialForm.value)
          ElMessage.success('更新成功')
        } else {
          await materialsService.createMaterial(materialForm.value)
          ElMessage.success('创建成功')
        }
        
        showCreateDialog.value = false
        loadMaterials()
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

    const resetSearch = () => {
      searchForm.value = {
        code: '',
        name: '',
        category_id: null
      }
      pagination.value.currentPage = 1
      loadMaterials()
    }

    const resetForm = () => {
      editMode.value = false
      materialForm.value = {
        code: '',
        name: '',
        specification: '',
        unit: '',
        category_id: null,
        safety_stock: 0,
        supplier: '',
        supplier_code: '',
        unit_cost: 0,
        description: '',
        status: 'active'
      }
      if (materialFormRef.value) {
        materialFormRef.value.clearValidate()
      }
    }

    const handleSizeChange = (size) => {
      pagination.value.pageSize = size
      pagination.value.currentPage = 1
      loadMaterials()
    }

    const handleCurrentChange = (page) => {
      pagination.value.currentPage = page
      loadMaterials()
    }

    onMounted(() => {
      loadCategories()
      loadMaterials()
    })

    return {
      materials,
      categories,
      loading,
      showCreateDialog,
      showImportDialog,
      editMode,
      submitting,
      importing,
      materialFormRef,
      searchForm,
      materialForm,
      pagination,
      rules,
      formatDate,
      editMaterial,
      deleteMaterial,
      submitMaterial,
      resetSearch,
      resetForm,
      loadMaterials,
      handleSizeChange,
      handleCurrentChange,
      handleExport,
      handleImport,
      handleFileChange
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

.header-actions {
  display: flex;
  gap: 10px;
}

.search-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.low-stock-warning {
  color: #F56C6C;
  font-weight: bold;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .material-list {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-header h1 {
    font-size: 18px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: calc(33% - 6px);
    font-size: 12px;
    padding: 8px 12px;
  }

  .search-card {
    margin-bottom: 16px;
  }

  .search-card .el-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .search-card .el-form-item {
    margin-right: 0;
    margin-bottom: 8px;
    width: 100%;
  }

  .search-card .el-input,
  .search-card .el-select {
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
    margin-top: 16px;
  }

  :deep(.el-pagination) {
    font-size: 11px;
    flex-wrap: wrap;
    gap: 4px;
    justify-content: center;
  }

  :deep(.el-pagination__sizes),
  :deep(.el-pagination__jump) {
    display: none !important;
  }

  :deep(.el-pagination button),
  :deep(.el-pager li) {
    min-width: 28px !important;
    height: 28px !important;
    line-height: 28px !important;
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

  .el-form-item {
    margin-bottom: 12px !important;
  }

  .el-form-item__label {
    font-size: 12px !important;
    padding-bottom: 4px !important;
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: 14px !important;
  }
}

@media screen and (max-width: 480px) {
  .material-list {
    padding: 8px;
  }

  .page-header h1 {
    font-size: 16px;
  }

  .header-actions .el-button {
    min-width: calc(50% - 4px);
    font-size: 11px;
    padding: 6px 10px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .el-dialog {
    width: 98% !important;
    margin: 5px auto !important;
  }
}
</style>