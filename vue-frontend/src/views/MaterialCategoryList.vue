<template>
  <div class="material-category-list-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Folder /></el-icon>
          </div>
          <div class="title-text">
            <h1>物料分类管理</h1>
            <p class="subtitle">管理系统中的物料分类层级结构</p>
          </div>
        </div>
        <el-button type="primary" class="btn-gradient" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建分类
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalCategories }}</div>
              <div class="stat-label">分类总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-primary">
            <div class="stat-icon-wrapper stat-icon-wrapper-primary">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ level1Count }}</div>
              <div class="stat-label">一级分类</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-secondary">
            <div class="stat-icon-wrapper stat-icon-wrapper-secondary">
              <el-icon><FolderAdd /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ level2Count }}</div>
              <div class="stat-label">二级分类</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-material">
            <div class="stat-icon-wrapper stat-icon-wrapper-material">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ materialCount }}</div>
              <div class="stat-label">物料总数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 分类树卡片 -->
    <div class="content-section animate-fade-in-up delay-200">
      <el-card class="glass-card category-tree-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon><Collection /></el-icon>
              <span>分类列表</span>
              <span class="total-count">共 {{ totalCategories }} 个分类</span>
            </div>
            <div class="header-actions">
              <el-button @click="loadCategories" :loading="loading" class="btn-refresh">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>

        <el-table 
          :data="categories" 
          v-loading="loading"
          stripe
          class="custom-table"
          row-key="id"
          default-expand-all
          :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
          style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="分类名称" min-width="180">
            <template #default="{ row }">
              <div class="category-name-cell">
                <el-icon class="category-icon" :size="16">
                  <Folder v-if="!row.parent_id" />
                  <Document v-else />
                </el-icon>
                <span class="category-name" :class="{ 'is-root': !row.parent_id }">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="code" label="分类编码" width="150">
            <template #default="{ row }">
              <span class="code-text">{{ row.code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" show-overflow-tooltip min-width="200">
            <template #default="{ row }">
              <span class="description-text">{{ row.description || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="level" label="层级" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.level === 1 ? 'primary' : 'info'" size="small" effect="light" class="level-tag">
                {{ row.level === 1 ? '一级' : '二级' }}
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
          <el-table-column label="操作" width="180" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="editCategory(row)" class="action-btn">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" link size="small" @click="deleteCategory(row)" class="action-btn">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 创建/编辑分类对话框 -->
    <el-dialog 
      :title="editMode ? '编辑分类' : '新建分类'" 
      v-model="showCreateDialog"
      width="500px"
      class="category-dialog"
      destroy-on-close
    >
      <el-form :model="categoryForm" :rules="rules" ref="categoryFormRef" label-width="100px" class="category-form">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" prefix-icon="Folder"></el-input>
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
          <el-input v-model="categoryForm.code" placeholder="请输入分类编码" prefix-icon="Key"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="categoryForm.description" 
            placeholder="请输入分类描述"
            :rows="3"
          ></el-input>
        </el-form-item>
        <el-form-item label="父级分类" prop="parent_id">
          <el-select v-model="categoryForm.parent_id" placeholder="请选择父级分类" style="width: 100%" clearable>
            <el-option label="无（顶级分类）" :value="null"></el-option>
            <el-option 
              v-for="category in parentCategories" 
              :key="category.id" 
              :label="category.name" 
              :value="category.id"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false" class="btn-secondary">取消</el-button>
          <el-button type="primary" @click="submitCategory" :loading="submitting" class="btn-gradient">
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
import { Folder, FolderOpened, FolderAdd, Box, Plus, Refresh, Edit, Delete, Collection, Document, Key } from '@element-plus/icons-vue'
import materialsService from '@/services/materials'
import { formatDate } from '@/utils/dateUtils'

export default {
  name: 'MaterialCategoryList',
  components: {
    Folder,
    FolderOpened,
    FolderAdd,
    Box,
    Plus,
    Refresh,
    Edit,
    Delete,
    Collection,
    Document,
    Key
  },
  setup() {
    const categories = ref([])
    const loading = ref(false)
    const showCreateDialog = ref(false)
    const editMode = ref(false)
    const submitting = ref(false)
    const categoryFormRef = ref(null)
    const materialCount = ref(0)
    
    const categoryForm = ref({
      name: '',
      code: '',
      description: '',
      parent_id: null
    })

    const rules = {
      name: [
        { required: true, message: '请输入分类名称', trigger: 'blur' }
      ],
      code: [
        { required: true, message: '请输入分类编码', trigger: 'blur' }
      ]
    }

    // 计算属性
    const totalCategories = computed(() => categories.value.length)
    
    const level1Count = computed(() => 
      categories.value.filter(c => c.level === 1 || !c.parent_id).length
    )
    
    const level2Count = computed(() => 
      categories.value.filter(c => c.level === 2 || c.parent_id).length
    )

    // 可作为父级分类的选项（只包含一级分类）
    const parentCategories = computed(() => 
      categories.value.filter(c => c.level === 1 || !c.parent_id)
    )

    const loadCategories = async () => {
      loading.value = true
      try {
        const response = await materialsService.getCategories()
        categories.value = Array.isArray(response) ? response : (response.categories || [])
      } catch (error) {
        ElMessage.error('加载分类列表失败：' + error.message)
      } finally {
        loading.value = false
      }
    }

    const loadMaterialCount = async () => {
      try {
        const response = await materialsService.getMaterials({ per_page: 1 })
        materialCount.value = response.total || 0
      } catch (error) {
        console.error('加载物料数量失败:', error)
      }
    }

    const editCategory = (category) => {
      editMode.value = true
      categoryForm.value = { ...category }
      showCreateDialog.value = true
    }

    const deleteCategory = async (category) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除分类"${category.name}"吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await materialsService.deleteCategory(category.id)
        ElMessage.success('删除成功')
        loadCategories()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败：' + error.message)
        }
      }
    }

    const submitCategory = async () => {
      if (!categoryFormRef.value) return
      
      try {
        await categoryFormRef.value.validate()
        submitting.value = true
        
        if (editMode.value) {
          await materialsService.updateCategory(categoryForm.value.id, categoryForm.value)
          ElMessage.success('更新成功')
        } else {
          await materialsService.createCategory(categoryForm.value)
          ElMessage.success('创建成功')
        }
        
        showCreateDialog.value = false
        loadCategories()
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
      categoryForm.value = {
        name: '',
        code: '',
        description: '',
        parent_id: null
      }
      if (categoryFormRef.value) {
        categoryFormRef.value.clearValidate()
      }
    }

    onMounted(() => {
      loadCategories()
      loadMaterialCount()
    })

    return {
      categories,
      loading,
      showCreateDialog,
      editMode,
      submitting,
      categoryFormRef,
      categoryForm,
      rules,
      totalCategories,
      level1Count,
      level2Count,
      materialCount,
      parentCategories,
      formatDate,
      editCategory,
      deleteCategory,
      submitCategory,
      resetForm,
      loadCategories
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

.material-category-list-container {
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
.stat-card-primary::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-secondary::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-material::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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

.stat-icon-wrapper-primary {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-secondary {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-material {
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

.stat-card-primary .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-secondary .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-material .stat-value {
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

.category-tree-card :deep(.el-card__header) {
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
  gap: 10px;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.card-title .el-icon {
  color: #0ea5e9;
  font-size: 20px;
}

.total-count {
  font-size: 13px;
  color: #64748b;
  margin-left: 8px;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
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

.btn-refresh {
  transition: all 0.3s;
}

.btn-refresh:hover {
  transform: translateY(-2px);
}

/* 内容区域 */
.content-section {
  margin-bottom: 20px;
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

.category-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-icon {
  color: #0ea5e9;
}

.category-name {
  font-weight: 500;
  color: #475569;
}

.category-name.is-root {
  font-weight: 600;
  color: #1e293b;
}

.code-text {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.6);
  padding: 4px 8px;
  border-radius: 6px;
}

.description-text {
  color: #64748b;
  font-size: 13px;
}

.level-tag {
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

.action-btn {
  opacity: 0;
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) .action-btn {
  opacity: 1;
}

/* 对话框样式 */
.category-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  padding: 20px 24px;
  margin-right: 0;
}

.category-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.category-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.category-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.category-form :deep(.el-input__wrapper),
.category-form :deep(.el-textarea__inner) {
  border-radius: 10px;
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
  .material-category-list-container {
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

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    flex: 1;
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

  .category-dialog {
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
