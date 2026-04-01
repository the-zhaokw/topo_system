<template>
  <div class="material-category-list">
    <div class="page-header">
      <h1>物料分类管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <i class="el-icon-plus"></i> 新建分类
      </el-button>
    </div>

    <el-card>
      <el-table :data="categories" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="name" label="分类名称"></el-table-column>
        <el-table-column prop="code" label="分类编码"></el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip></el-table-column>
        <el-table-column prop="parent_id" label="父级ID" width="100"></el-table-column>
        <el-table-column prop="level" label="层级" width="80"></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="mini" @click="editCategory(row)">编辑</el-button>
            <el-button size="mini" type="danger" @click="deleteCategory(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑分类对话框 -->
    <el-dialog 
      :title="editMode ? '编辑分类' : '新建分类'" 
      v-model="showCreateDialog"
      width="500px"
    >
      <el-form :model="categoryForm" :rules="rules" ref="categoryFormRef" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称"></el-input>
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
          <el-input v-model="categoryForm.code" placeholder="请输入分类编码"></el-input>
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
          <el-select v-model="categoryForm.parent_id" placeholder="请选择父级分类" style="width: 100%">
            <el-option label="无（顶级分类）" :value="null"></el-option>
            <el-option 
              v-for="category in categories" 
              :key="category.id" 
              :label="category.name" 
              :value="category.id"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCategory" :loading="submitting">
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
  name: 'MaterialCategoryList',
  setup() {
    const categories = ref([])
    const loading = ref(false)
    const showCreateDialog = ref(false)
    const editMode = ref(false)
    const submitting = ref(false)
    const categoryFormRef = ref(null)
    
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
      formatDate,
      editCategory,
      deleteCategory,
      submitCategory,
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
  .material-category-list {
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
  .material-category-list {
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