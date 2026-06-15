<template>
  <div class="material-list-container">
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
            <h1>物料主数据管理</h1>
            <p class="subtitle">管理系统中的所有物料信息</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="showCreateDialog = true" class="btn-gradient">
            <el-icon><Plus /></el-icon> 新建物料
          </el-button>
          <el-button type="success" @click="handleExport" class="btn-success">
            <el-icon><Download /></el-icon> 导出
          </el-button>
          <el-button type="warning" @click="showImportDialog = true" class="btn-warning">
            <el-icon><Upload /></el-icon> 导入
          </el-button>
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
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">物料总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-active">
            <div class="stat-icon-wrapper stat-icon-wrapper-active">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.active }}</div>
              <div class="stat-label">启用中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-warning">
            <div class="stat-icon-wrapper stat-icon-wrapper-warning">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.lowStock }}</div>
              <div class="stat-label">库存预警</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-inventory">
            <div class="stat-icon-wrapper stat-icon-wrapper-inventory">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalInventory }}</div>
              <div class="stat-label">总库存量</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索条件 -->
    <div class="search-section animate-fade-in-up delay-200">
      <el-card class="search-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Search /></el-icon>
              搜索条件
            </span>
          </div>
        </template>
        <el-form :model="searchForm" inline class="search-form">
          <el-form-item label="物料编码">
            <el-input v-model="searchForm.code" placeholder="请输入物料编码" clearable class="search-input"></el-input>
          </el-form-item>
          <el-form-item label="物料名称">
            <el-input v-model="searchForm.name" placeholder="请输入物料名称" clearable class="search-input"></el-input>
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="searchForm.category_id" placeholder="请选择分类" clearable class="search-select">
              <el-option 
                v-for="category in categories" 
                :key="category.id" 
                :label="category.name" 
                :value="category.id"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadMaterials" :loading="loading" class="btn-gradient">
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

    <!-- 物料列表 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><List /></el-icon>
              <h3>物料列表</h3>
              <span class="total-count">共 {{ pagination.total }} 条记录</span>
            </div>
          </div>
        </template>

        <el-table :data="materials" v-loading="loading" stripe class="custom-table" style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="material_code" label="物料编码" width="120">
            <template #default="{ row }">
              <span class="code-text">{{ row.material_code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="物料名称" min-width="150">
            <template #default="{ row }">
              <div class="material-name">{{ row.name }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="specification" label="规格型号" show-overflow-tooltip min-width="120"></el-table-column>
          <el-table-column prop="unit" label="单位" width="80" align="center"></el-table-column>
          <el-table-column prop="category_name" label="分类" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="light" class="category-tag">{{ row.category_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="safety_stock" label="安全库存" width="100" align="center"></el-table-column>
          <el-table-column prop="supplier" label="供应商" width="120" show-overflow-tooltip></el-table-column>
          <el-table-column prop="total_quantity" label="当前库存" width="100" align="center">
            <template #default="{ row }">
              <span :class="{ 'low-stock-warning': row.is_low_stock }">
                {{ row.total_quantity || 0 }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="is_low_stock" label="库存预警" width="90" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_low_stock" type="danger" size="small" effect="light" class="status-tag">库存不足</el-tag>
              <el-tag v-else type="success" size="small" effect="light" class="status-tag">正常</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small" effect="light" class="status-tag">
                {{ row.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
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
              <el-button type="primary" link size="small" @click="editMaterial(row)" class="action-btn">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" link size="small" @click="deleteMaterial(row)" class="action-btn">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
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
            @current-change="handleCurrentChange"
          ></el-pagination>
        </div>
      </el-card>
    </div>

    <!-- 创建/编辑物料对话框 -->
    <el-dialog 
      :title="editMode ? '编辑物料' : '新建物料'" 
      v-model="showCreateDialog"
      width="600px"
      class="material-dialog"
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
        <el-button type="primary" @click="submitMaterial" :loading="submitting" class="btn-gradient">
          {{ editMode ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入物料数据" width="500px" class="material-dialog">
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
        <el-icon class="upload-icon"><Upload /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">只能上传xlsx/xls文件</div>
        </template>
      </el-upload>

      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing" class="btn-gradient">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Box, Plus, Download, Upload, Search, Refresh, List, Edit, Delete, CircleCheck, Warning, DataAnalysis } from '@element-plus/icons-vue'
import materialsService from '@/services/materials'
import { apiService } from '@/services/api'
import { formatDate } from '@/utils/dateUtils'

export default {
  name: 'MaterialList',
  components: {
    Box, Plus, Download, Upload, Search, Refresh, List, Edit, Delete, CircleCheck, Warning, DataAnalysis
  },
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

    // 统计数据
    const stats = computed(() => {
      const total = pagination.value.total
      const active = materials.value.filter(m => m.status === 'active').length
      const lowStock = materials.value.filter(m => m.is_low_stock).length
      const totalInventory = materials.value.reduce((sum, m) => sum + (m.total_quantity || 0), 0)
      return { total, active, lowStock, totalInventory }
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
      stats,
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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.material-list-container {
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

.header-actions {
  display: flex;
  gap: 10px;
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
.stat-card-warning::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-inventory::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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

.stat-icon-wrapper-warning {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-inventory {
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

.stat-card-active .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-warning .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-inventory .stat-value {
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

/* 搜索区域 */
.search-section {
  margin-bottom: 24px;
}

.search-card :deep(.el-card__header) {
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

.search-form {
  padding: 10px 0;
}

.search-input,
.search-select {
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

.btn-success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(17, 153, 142, 0.5);
}

.btn-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-warning:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(245, 158, 11, 0.5);
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

.material-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.category-tag,
.status-tag {
  font-weight: 500;
  border-radius: 6px;
}

.low-stock-warning {
  color: #F56C6C;
  font-weight: bold;
}

.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

.action-btn {
  opacity: 0;
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) .action-btn {
  opacity: 1;
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 对话框样式 */
:deep(.material-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  padding: 20px;
  border-radius: 16px 16px 0 0;
  margin-right: 0;
}

:deep(.material-dialog .el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.material-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

:deep(.material-dialog .el-dialog__body) {
  padding: 24px;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
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
  .material-list-container {
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

  .search-input,
  .search-select {
    width: 100% !important;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .action-btn {
    opacity: 1;
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

  :deep(.material-dialog) {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  :deep(.material-dialog .el-dialog__header) {
    padding: 12px !important;
  }

  :deep(.material-dialog .el-dialog__title) {
    font-size: 16px !important;
  }

  :deep(.material-dialog .el-dialog__body) {
    padding: 12px !important;
    max-height: 60vh !important;
    overflow-y: auto !important;
  }

  :deep(.material-dialog .el-dialog__footer) {
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
  .page-header {
    padding: 16px;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .header-actions .el-button {
    min-width: calc(50% - 4px);
    font-size: 11px;
    padding: 6px 10px;
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

  :deep(.material-dialog) {
    width: 98% !important;
    margin: 5px auto !important;
  }
}
</style>
