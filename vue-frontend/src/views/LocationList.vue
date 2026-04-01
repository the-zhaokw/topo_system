<template>
  <div class="location-management">
    <el-card class="page-header">
      <template #header>
        <div class="card-header">
          <span>库位管理</span>
          <el-button type="primary" @click="openCreateDialog">新增库位</el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="仓库">
          <el-select v-model="searchForm.warehouse_id" placeholder="请选择仓库" clearable @change="handleSearch">
            <el-option
              v-for="warehouse in warehouses"
              :key="warehouse.id"
              :label="warehouse.name"
              :value="warehouse.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="库位编码">
          <el-input v-model="searchForm.code" placeholder="请输入库位编码" clearable @clear="handleSearch" @keyup.enter="handleSearch"></el-input>
        </el-form-item>
        <el-form-item label="库位名称">
          <el-input v-model="searchForm.name" placeholder="请输入库位名称" clearable @clear="handleSearch" @keyup.enter="handleSearch"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-container">
      <el-table :data="locations" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="warehouse_name" label="所属仓库" width="150"></el-table-column>
        <el-table-column prop="code" label="库位编码" width="150"></el-table-column>
        <el-table-column prop="name" label="库位名称" width="200"></el-table-column>
        <el-table-column prop="area" label="区域" width="100"></el-table-column>
        <el-table-column prop="zone" label="分区" width="100"></el-table-column>
        <el-table-column prop="rack" label="货架" width="100"></el-table-column>
        <el-table-column prop="level" label="层级" width="100"></el-table-column>
        <el-table-column prop="capacity" label="容量" width="100"></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="scope">
            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这个库位吗？"
              @confirm="deleteLocation(scope.row.id)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑库位对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="500px"
      @close="resetForm"
    >
      <el-form :model="locationForm" :rules="formRules" ref="locationFormRef" label-width="100px">
        <el-form-item label="所属仓库" prop="warehouse_id">
          <el-select v-model="locationForm.warehouse_id" placeholder="请选择仓库" style="width: 100%">
            <el-option
              v-for="warehouse in warehouses"
              :key="warehouse.id"
              :label="warehouse.name"
              :value="warehouse.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="库位编码" prop="code">
          <el-input v-model="locationForm.code" placeholder="请输入库位编码"></el-input>
        </el-form-item>
        <el-form-item label="库位名称" prop="name">
          <el-input v-model="locationForm.name" placeholder="请输入库位名称"></el-input>
        </el-form-item>
        <el-form-item label="区域">
          <el-input v-model="locationForm.area" placeholder="请输入区域"></el-input>
        </el-form-item>
        <el-form-item label="分区">
          <el-input v-model="locationForm.zone" placeholder="请输入分区"></el-input>
        </el-form-item>
        <el-form-item label="货架">
          <el-input v-model="locationForm.rack" placeholder="请输入货架"></el-input>
        </el-form-item>
        <el-form-item label="层级">
          <el-input v-model="locationForm.level" placeholder="请输入层级"></el-input>
        </el-form-item>
        <el-form-item label="容量">
          <el-input-number v-model="locationForm.capacity" :min="0" controls-position="right" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="locationForm.description" type="textarea" placeholder="请输入描述"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import materialsService from '@/services/materials'
import { format } from 'date-fns'

// 响应式数据
const locations = ref([])
const warehouses = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEditMode = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 表单引用
const locationFormRef = ref(null)

// 搜索表单
const searchForm = reactive({
  warehouse_id: '',
  code: '',
  name: ''
})

// 库位表单
const locationForm = reactive({
  id: null,
  warehouse_id: '',
  code: '',
  name: '',
  area: '',
  zone: '',
  rack: '',
  level: '',
  capacity: 0,
  description: ''
})

// 表单验证规则
const formRules = {
  warehouse_id: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  code: [{ required: true, message: '请输入库位编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入库位名称', trigger: 'blur' }]
}

// 计算属性
const dialogTitle = computed(() => {
  return isEditMode.value ? '编辑库位' : '新增库位'
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  return format(new Date(dateString), 'yyyy-MM-dd HH:mm:ss')
}

// 加载仓库列表
const loadWarehouses = async () => {
  try {
    warehouses.value = await materialsService.getWarehouses()
  } catch (error) {
    ElMessage.error('加载仓库列表失败: ' + error.message)
  }
}

// 加载库位列表
const loadLocations = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      warehouse_id: searchForm.warehouse_id,
      code: searchForm.code,
      name: searchForm.name
    }
    
    const response = await materialsService.getLocations()
    // 过滤数据
    let filteredData = response
    
    if (searchForm.warehouse_id) {
      filteredData = filteredData.filter(item => item.warehouse_id === searchForm.warehouse_id)
    }
    
    if (searchForm.code) {
      filteredData = filteredData.filter(item => item.code.includes(searchForm.code))
    }
    
    if (searchForm.name) {
      filteredData = filteredData.filter(item => item.name.includes(searchForm.name))
    }
    
    // 分页处理
    total.value = filteredData.length
    const startIndex = (currentPage.value - 1) * pageSize.value
    locations.value = filteredData.slice(startIndex, startIndex + pageSize.value)
  } catch (error) {
    ElMessage.error('加载库位列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  loadLocations()
}

// 重置搜索
const resetSearch = () => {
  searchForm.warehouse_id = ''
  searchForm.code = ''
  searchForm.name = ''
  currentPage.value = 1
  loadLocations()
}

// 打开创建对话框
const openCreateDialog = () => {
  isEditMode.value = false
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (row) => {
  isEditMode.value = true
  Object.assign(locationForm, row)
  dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  try {
    await locationFormRef.value.validate()
    
    submitLoading.value = true
    const formData = { ...locationForm }
    
    if (isEditMode.value) {
      await materialsService.updateLocation(locationForm.id, formData)
      ElMessage.success('库位更新成功')
    } else {
      await materialsService.createLocation(formData)
      ElMessage.success('库位创建成功')
    }
    
    dialogVisible.value = false
    loadLocations()
  } catch (error) {
    ElMessage.error((isEditMode.value ? '更新' : '创建') + '库位失败: ' + error.message)
  } finally {
    submitLoading.value = false
  }
}

// 删除库位
const deleteLocation = async (id) => {
  try {
    await materialsService.deleteLocation(id)
    ElMessage.success('库位删除成功')
    loadLocations()
  } catch (error) {
    ElMessage.error('删除库位失败: ' + error.message)
  }
}

// 重置表单
const resetForm = () => {
  locationFormRef.value?.resetFields()
  locationForm.id = null
  locationForm.warehouse_id = ''
  locationForm.code = ''
  locationForm.name = ''
  locationForm.area = ''
  locationForm.zone = ''
  locationForm.rack = ''
  locationForm.level = ''
  locationForm.capacity = 0
  locationForm.description = ''
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadLocations()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadLocations()
}

// 组件挂载时加载数据
onMounted(() => {
  loadWarehouses()
  loadLocations()
})
</script>

<style scoped>
.location-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 10px;
}

.table-container {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .location-list {
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
  .location-list {
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