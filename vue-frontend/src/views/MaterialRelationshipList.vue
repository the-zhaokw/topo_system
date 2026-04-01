<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>物料关系管理</span>
          <div>
            <el-button type="primary" @click="openCreateDialog">新增关系</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索条件 -->
      <el-form :model="searchForm" :inline="true" label-width="100px" class="search-form">
        <el-form-item label="父项序列号">
          <el-input v-model="searchForm.parent_sn" placeholder="请输入父项序列号" clearable></el-input>
        </el-form-item>
        <el-form-item label="子项序列号">
          <el-input v-model="searchForm.child_sn" placeholder="请输入子项序列号" clearable></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 关系列表 -->
      <el-table :data="paginatedRelationships" border stripe v-loading="loading">
        <el-table-column prop="parent_sn" label="父项序列号" width="180"></el-table-column>
        <el-table-column prop="parent_type" label="父项类型" width="120"></el-table-column>
        <el-table-column prop="child_sn" label="子项序列号" width="180"></el-table-column>
        <el-table-column prop="child_type" label="子项类型" width="120"></el-table-column>
        <el-table-column prop="slot_port_info" label="槽位/端口信息" width="150"></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button size="small" type="danger" @click="deleteRelationship(scope.row.id)">删除</el-button>
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
        :total="filteredRelationships.length"
        class="pagination">
      </el-pagination>
    </el-card>

    <!-- 新增关系对话框 -->
    <el-dialog title="新增物料关系" v-model="dialogVisible" width="500px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="父项序列号" prop="parent_sn">
          <el-input v-model="form.parent_sn" placeholder="请输入父项序列号"></el-input>
        </el-form-item>
        <el-form-item label="父项类型" prop="parent_type">
          <el-select v-model="form.parent_type" placeholder="请选择父项类型">
            <el-option label="设备" value="equipment"></el-option>
            <el-option label="板卡" value="board"></el-option>
            <el-option label="模块" value="module"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="子项序列号" prop="child_sn">
          <el-input v-model="form.child_sn" placeholder="请输入子项序列号"></el-input>
        </el-form-item>
        <el-form-item label="子项类型" prop="child_type">
          <el-select v-model="form.child_type" placeholder="请选择子项类型">
            <el-option label="板卡" value="board"></el-option>
            <el-option label="模块" value="module"></el-option>
            <el-option label="光模块" value="optical_module"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="槽位/端口信息">
          <el-input v-model="form.slot_port_info" placeholder="请输入槽位或端口信息"></el-input>
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

// 表单数据
const form = reactive({
  parent_sn: '',
  parent_type: '',
  child_sn: '',
  child_type: '',
  slot_port_info: ''
})

// 搜索表单
const searchForm = reactive({
  parent_sn: '',
  child_sn: ''
})

// 分页数据
const currentPage = ref(1)
const pageSize = ref(20)

// 列表数据
const relationships = ref([])

// 表单验证规则
const rules = {
  parent_sn: [
    { required: true, message: '请输入父项序列号', trigger: 'blur' }
  ],
  parent_type: [
    { required: true, message: '请选择父项类型', trigger: 'change' }
  ],
  child_sn: [
    { required: true, message: '请输入子项序列号', trigger: 'blur' }
  ],
  child_type: [
    { required: true, message: '请选择子项类型', trigger: 'change' }
  ]
}

// 计算属性 - 过滤后的关系列表
const filteredRelationships = computed(() => {
  if (!Array.isArray(relationships.value)) return []
  return relationships.value.filter(rel => {
    return (
      (!searchForm.parent_sn || (rel.parent_sn && rel.parent_sn.includes(searchForm.parent_sn))) &&
      (!searchForm.child_sn || (rel.child_sn && rel.child_sn.includes(searchForm.child_sn)))
    )
  })
})

// 计算属性 - 分页后的关系列表
const paginatedRelationships = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRelationships.value.slice(start, end)
})

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

// 加载关系列表
const loadRelationships = async () => {
  try {
    loading.value = true
    const data = await materialsService.getRelationships()
    relationships.value = Array.isArray(data) ? data : []
  } catch (error) {
    ElMessage.error('加载物料关系列表失败: ' + error.message)
    relationships.value = []
  } finally {
    loading.value = false
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  resetForm()
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
        parent_sn: form.parent_sn,
        parent_type: form.parent_type,
        child_sn: form.child_sn,
        child_type: form.child_type,
        slot_port_info: form.slot_port_info
      }
      
      await materialsService.createRelationship(formData)
      ElMessage.success('物料关系创建成功')
      dialogVisible.value = false
      loadRelationships()
    } catch (error) {
      ElMessage.error('创建物料关系失败: ' + error.message)
    }
  })
}

// 删除关系
const deleteRelationship = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除该物料关系吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await materialsService.deleteRelationship(id)
    ElMessage.success('物料关系删除成功')
    loadRelationships()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除物料关系失败: ' + error.message)
    }
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 重置搜索
const resetSearch = () => {
  searchForm.parent_sn = ''
  searchForm.child_sn = ''
  currentPage.value = 1
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    parent_sn: '',
    parent_type: '',
    child_sn: '',
    child_type: '',
    slot_port_info: ''
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
  loadRelationships()
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
  .material-relationship-list {
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
  .material-relationship-list {
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