<template>
  <div class="category-manager">
    <!-- 分类选择器 -->
    <div class="category-select-wrapper">
      <el-tree-select
        v-model="selectedCategory"
        :data="categories"
        :props="{ label: 'name', value: 'id', children: 'children' }"
        placeholder="选择分类"
        check-strictly
        clearable
        filterable
        :filter-node-method="filterCategory"
        style="width: 100%"
        @change="handleCategoryChange"
      >
        <template #default="{ node, data }">
          <span class="category-option">
            <el-icon v-if="data.children?.length"><Folder /></el-icon>
            <el-icon v-else><Document /></el-icon>
            <span>{{ node.label }}</span>
          </span>
        </template>
      </el-tree-select>
      <el-button 
        type="primary" 
        link 
        :icon="Setting" 
        @click="openManageDialog"
        class="manage-btn"
        title="管理分类"
      />
    </div>

    <!-- 分类管理对话框 -->
    <el-dialog
      v-model="manageDialogVisible"
      title="分类管理"
      width="600px"
      destroy-on-close
    >
      <div class="category-manage-content">
        <!-- 工具栏 -->
        <div class="manage-toolbar">
          <el-button type="primary" :icon="Plus" @click="openCategoryForm()">
            新建分类
          </el-button>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索分类..."
            clearable
            size="small"
            style="width: 200px"
          />
        </div>

        <!-- 分类树 -->
        <el-scrollbar height="400px">
          <el-tree
            ref="categoryTreeRef"
            :data="filteredCategories"
            :props="{ label: 'name', children: 'children' }"
            node-key="id"
            default-expand-all
            :expand-on-click-node="false"
          >
            <template #default="{ node, data }">
              <div class="manage-category-node">
                <span class="node-content">
                  <el-icon v-if="data.children?.length"><Folder /></el-icon>
                  <el-icon v-else><Document /></el-icon>
                  <span class="node-name">{{ node.label }}</span>
                  <span class="node-count" v-if="data.article_count">({{ data.article_count }})</span>
                </span>
                <span class="node-actions">
                  <el-button
                    type="primary"
                    link
                    size="small"
                    :icon="Plus"
                    @click.stop="openCategoryForm(data)"
                    title="添加子分类"
                  />
                  <el-button
                    type="primary"
                    link
                    size="small"
                    :icon="Edit"
                    @click.stop="openCategoryForm(data, true)"
                    title="编辑"
                  />
                  <el-button
                    type="danger"
                    link
                    size="small"
                    :icon="Delete"
                    @click.stop="handleDeleteCategory(data)"
                    title="删除"
                  />
                </span>
              </div>
            </template>
          </el-tree>
        </el-scrollbar>
      </div>
    </el-dialog>

    <!-- 分类表单对话框 -->
    <el-dialog
      v-model="formDialogVisible"
      :title="isEditing ? '编辑分类' : '新建分类'"
      width="450px"
      destroy-on-close
    >
      <el-form :model="categoryForm" label-width="80px" :rules="formRules" ref="formRef">
        <el-form-item label="名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="父分类">
          <el-tree-select
            v-model="categoryForm.parent_id"
            :data="categoryTreeForSelect"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="无（作为顶级分类）"
            clearable
            check-strictly
            :disabled="isEditing && categoryForm.id === categoryForm.parent_id"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="categoryForm.description"
            type="textarea"
            :rows="3"
            placeholder="分类描述（可选）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCategory" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Setting, Folder, Document } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: null
  },
  categories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'refresh'])

// API 基础 URL：路径已带 /api 前缀，dev 模式留空走 Vite 代理
const API_BASE_URL = import.meta.env.DEV ? '' : 'http://172.18.36.249:5000'

// 通用 API 请求函数
const apiRequest = async (url, options = {}) => {
  const token = localStorage.getItem('token')
  const headers = {
    ...options.headers,
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  }
  const response = await fetch(`${API_BASE_URL}${url}`, { ...options, headers })
  if (response.status === 401) {
    ElMessage.error('请先登录')
    throw new Error('Unauthorized')
  }
  if (response.status === 403) {
    ElMessage.error('没有权限')
    throw new Error('Forbidden')
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.error || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

// 状态
const selectedCategory = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const manageDialogVisible = ref(false)
const formDialogVisible = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const searchKeyword = ref('')
const categoryTreeRef = ref(null)
const formRef = ref(null)

const categoryForm = reactive({
  id: null,
  name: '',
  parent_id: null,
  description: ''
})

const formRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

// 过滤后的分类树（用于管理对话框）
const filteredCategories = computed(() => {
  if (!searchKeyword.value) return props.categories
  const keyword = searchKeyword.value.toLowerCase()
  
  const filter = (items) => {
    return items.filter(item => {
      const match = item.name.toLowerCase().includes(keyword)
      if (item.children?.length) {
        item.children = filter(item.children)
        return match || item.children.length > 0
      }
      return match
    })
  }
  
  return filter([...props.categories])
})

// 用于选择父分类的树（排除自身及其子分类）
const categoryTreeForSelect = computed(() => {
  if (!isEditing.value || !categoryForm.id) return props.categories
  
  // 递归排除当前分类及其子分类
  const filterSelf = (items) => {
    return items
      .filter(item => item.id !== categoryForm.id)
      .map(item => ({
        ...item,
        children: item.children ? filterSelf(item.children) : []
      }))
  }
  
  return filterSelf([...props.categories])
})

// 过滤分类选项
const filterCategory = (value, data) => {
  if (!value) return true
  return data.name.toLowerCase().includes(value.toLowerCase())
}

// 处理分类选择变化
const handleCategoryChange = (value) => {
  emit('change', value)
}

// 打开管理对话框
const openManageDialog = () => {
  manageDialogVisible.value = true
  searchKeyword.value = ''
}

// 打开分类表单
const openCategoryForm = (category = null, edit = false) => {
  if (edit && category) {
    // 编辑模式
    categoryForm.id = category.id
    categoryForm.name = category.name
    categoryForm.parent_id = category.parent_id
    categoryForm.description = category.description || ''
    isEditing.value = true
  } else if (category) {
    // 添加子分类
    categoryForm.id = null
    categoryForm.name = ''
    categoryForm.parent_id = category.id
    categoryForm.description = ''
    isEditing.value = false
  } else {
    // 新建顶级分类
    categoryForm.id = null
    categoryForm.name = ''
    categoryForm.parent_id = null
    categoryForm.description = ''
    isEditing.value = false
  }
  formDialogVisible.value = true
}

// 保存分类
const saveCategory = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const method = isEditing.value ? 'PUT' : 'POST'
    const url = isEditing.value 
      ? `/api/knowledge/categories/${categoryForm.id}` 
      : '/api/knowledge/categories'
    
    const body = {
      name: categoryForm.name.trim(),
      parent_id: categoryForm.parent_id,
      description: categoryForm.description.trim()
    }

    await apiRequest(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })

    ElMessage.success(isEditing.value ? '更新成功' : '创建成功')
    formDialogVisible.value = false
    emit('refresh')
  } catch (error) {
    console.error('保存分类失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 删除分类
const handleDeleteCategory = async (category) => {
  try {
    // 检查是否有子分类
    if (category.children?.length > 0) {
      await ElMessageBox.confirm(
        `该分类下有 ${category.children.length} 个子分类，删除后会将这些子分类提升为顶级分类。是否继续？`,
        '确认删除',
        { type: 'warning' }
      )
    } else {
      await ElMessageBox.confirm(
        `确定要删除分类 "${category.name}" 吗？`,
        '确认删除',
        { type: 'warning' }
      )
    }

    await apiRequest(`/api/knowledge/categories/${category.id}`, {
      method: 'DELETE'
    })

    ElMessage.success('删除成功')
    
    // 如果删除的是当前选中的分类，清空选择
    if (selectedCategory.value === category.id) {
      selectedCategory.value = null
      emit('change', null)
    }
    
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除分类失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}
</script>

<style scoped>
.category-manager {
  width: 100%;
}

.category-select-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-select-wrapper :deep(.el-tree-select) {
  flex: 1;
}

.manage-btn {
  flex-shrink: 0;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 管理对话框样式 */
.category-manage-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.manage-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.manage-category-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  padding-right: 8px;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

.node-name {
  font-size: 14px;
}

.node-count {
  font-size: 12px;
  color: #909399;
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.manage-category-node:hover .node-actions {
  opacity: 1;
}

/* 树形组件样式调整 */
:deep(.el-tree-node__content) {
  height: 36px;
}

:deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}
</style>
