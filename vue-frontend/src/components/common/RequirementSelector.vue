<template>
  <div class="requirement-selector">
    <el-button type="primary" @click="showDialog = true" :disabled="disabled">
      <el-icon><Link /></el-icon>
      {{ buttonText }}
    </el-button>

    <div v-if="selectedRequirements.length > 0" class="selected-list">
      <el-tag
        v-for="req in selectedRequirements"
        :key="req.id"
        closable
        @close="handleRemove(req.id)"
        class="requirement-tag"
      >
        <span class="req-identifier">{{ req.identifier }}</span>
        <span class="req-title">{{ req.title }}</span>
      </el-tag>
    </div>

    <el-dialog
      v-model="showDialog"
      title="选择需求"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="selector-toolbar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索需求标识或标题"
          clearable
          style="width: 300px;"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filterStatus"
          placeholder="状态筛选"
          clearable
          style="width: 120px; margin-left: 12px;"
          @change="handleSearch"
        >
          <el-option label="设计中" value="designing" />
          <el-option label="评审中" value="reviewing" />
          <el-option label="已批准" value="approved" />
          <el-option label="已废弃" value="deprecated" />
        </el-select>
        <el-select
          v-model="filterPriority"
          placeholder="优先级筛选"
          clearable
          style="width: 120px; margin-left: 12px;"
          @change="handleSearch"
        >
          <el-option label="高" :value="1" />
          <el-option label="中" :value="2" />
          <el-option label="低" :value="3" />
        </el-select>
      </div>

      <el-table
        ref="tableRef"
        :data="requirementList"
        stripe
        style="width: 100%; margin-top: 16px;"
        height="400px"
        :row-key="getRowKey"
        @selection-change="handleSelectionChange"
        :select-on-indeterminate="false"
      >
        <el-table-column type="selection" width="45" :selectable="isSelectable" />
        <el-table-column prop="identifier" label="需求标识" width="120" />
        <el-table-column prop="title" label="需求标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'designing'" type="info" size="small">设计中</el-tag>
            <el-tag v-else-if="row.status === 'reviewing'" type="warning" size="small">评审中</el-tag>
            <el-tag v-else-if="row.status === 'approved'" type="success" size="small">已批准</el-tag>
            <el-tag v-else-if="row.status === 'deprecated'" type="danger" size="small">已废弃</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.priority === 1" type="danger" size="small">高</el-tag>
            <el-tag v-else-if="row.priority === 2" type="warning" size="small">中</el-tag>
            <el-tag v-else type="info" size="small">低</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner_name" label="负责人" width="100" />
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>

      <template #footer>
        <div class="dialog-footer">
          <div class="selection-info">
            已选择 {{ tempSelections.length }} 个需求
          </div>
          <div>
            <el-button @click="handleCancel">取消</el-button>
            <el-button type="primary" @click="handleConfirm">确定</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Link, Search } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  projectId: {
    type: [Number, String],
    required: true
  },
  buttonText: {
    type: String,
    default: '关联需求'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  maxSelections: {
    type: Number,
    default: Infinity
  },
  linkType: {
    type: String,
    default: 'tests'
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'select'])

const showDialog = ref(false)
const searchQuery = ref('')
const filterStatus = ref('')
const filterPriority = ref('')
const requirementList = ref([])
const tempSelections = ref([])
const tableRef = ref(null)
const loading = ref(false)

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const selectedRequirements = ref([...props.modelValue])

const getRowKey = (row) => row.id

const isSelectable = (row) => {
  if (tempSelections.value.length >= props.maxSelections) {
    return tempSelections.value.some(s => s.id === row.id)
  }
  return true
}

const loadRequirements = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      project_id: props.projectId
    }
    if (searchQuery.value) params.search = searchQuery.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterPriority.value) params.priority = filterPriority.value

    const response = await apiService.requirements.getItems(null, params)
    const data = response?.data || response
    requirementList.value = data?.items || data || []
    pagination.total = data?.total || 0

    await nextTick()
    restoreSelection()
  } catch (error) {
    console.error('加载需求列表失败:', error)
    ElMessage.error('加载需求列表失败')
  } finally {
    loading.value = false
  }
}

const restoreSelection = () => {
  if (!tableRef.value) return

  requirementList.value.forEach(row => {
    if (tempSelections.value.some(s => s.id === row.id)) {
      tableRef.value.toggleRowSelection(row, true)
    }
  })
}

const handleSearch = () => {
  pagination.page = 1
  loadRequirements()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadRequirements()
}

const handlePageSizeChange = (size) => {
  pagination.per_page = size
  loadRequirements()
}

const handleSelectionChange = (selection) => {
  const currentPageIds = requirementList.value.map(r => r.id)
  tempSelections.value = [
    ...tempSelections.value.filter(s => !currentPageIds.includes(s.id)),
    ...selection
  ]
}

const handleRemove = (id) => {
  const index = selectedRequirements.value.findIndex(r => r.id === id)
  if (index > -1) {
    selectedRequirements.value.splice(index, 1)
    emit('update:modelValue', selectedRequirements.value)
    emit('change', selectedRequirements.value)
  }
}

const handleCancel = () => {
  showDialog.value = false
  tempSelections.value = [...selectedRequirements.value]
}

const handleConfirm = () => {
  selectedRequirements.value = [...tempSelections.value]
  emit('update:modelValue', selectedRequirements.value)
  emit('change', selectedRequirements.value)
  emit('select', selectedRequirements.value)
  showDialog.value = false
  ElMessage.success(`已关联 ${selectedRequirements.value.length} 个需求`)
}

watch(() => props.modelValue, (newVal) => {
  selectedRequirements.value = [...newVal]
}, { deep: true })

watch(showDialog, (newVal) => {
  if (newVal) {
    tempSelections.value = [...selectedRequirements.value]
    loadRequirements()
  }
})

onMounted(() => {
  if (props.projectId) {
    loadRequirements()
  }
})
</script>

<style scoped>
.requirement-selector {
  width: 100%;
}

.selected-list {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.requirement-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  max-width: 300px;
}

.req-identifier {
  font-weight: bold;
  color: #409EFF;
}

.req-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selector-toolbar {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selection-info {
  color: #606266;
  font-size: 14px;
}
</style>