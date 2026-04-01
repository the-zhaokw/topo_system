<template>
  <div class="test-case-table">
    <div class="table-toolbar" v-if="showToolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索标题或标识符..."
          clearable
          style="width: 240px;"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px; margin-left: 12px;" @change="handleFilterChange">
          <el-option label="设计" value="designing" />
          <el-option label="待评审" value="pending_review" />
          <el-option label="已评审" value="reviewed" />
          <el-option label="已批准" value="approved" />
          <el-option label="废弃" value="deprecated" />
        </el-select>
        <el-select v-model="filterPriority" placeholder="优先级" clearable style="width: 100px; margin-left: 12px;" @change="handleFilterChange">
          <el-option label="P0" :value="0" />
          <el-option label="P1" :value="1" />
          <el-option label="P2" :value="2" />
          <el-option label="P3" :value="3" />
        </el-select>
        <el-select v-model="filterType" placeholder="类型" clearable style="width: 100px; margin-left: 12px;" @change="handleFilterChange">
          <el-option label="功能" value="functional" />
          <el-option label="性能" value="performance" />
          <el-option label="安全" value="security" />
        </el-select>
      </div>
      <div class="toolbar-right">
        <slot name="toolbar-actions"></slot>
      </div>
    </div>

    <div v-if="selectedCases.length > 0 && showBatchActions" class="batch-actions-bar">
      <el-alert type="info" :closable="false">
        <template #title>
          已选择 {{ selectedCases.length }} 个用例
          <el-button type="primary" link size="small" @click="clearSelection">清空</el-button>
        </template>
      </el-alert>
      <div class="batch-buttons">
        <slot name="batch-actions"></slot>
      </div>
    </div>

    <el-table
      ref="tableRef"
      :data="displayCases"
      stripe
      style="width: 100%;"
      v-loading="loading"
      :row-key="getRowKey"
      @selection-change="handleSelectionChange"
      @row-dblclick="handleRowDoubleClick"
      :row-class-name="getRowClassName"
    >
      <el-table-column v-if="showSelection" type="selection" width="45" :selectable="isSelectable" />
      <el-table-column prop="identifier" label="标识符" width="120" fixed>
        <template #default="{ row }">
          <el-link type="primary" @click="handleView(row)">{{ row.identifier }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="priority" label="优先级" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.priority === 0" type="danger" size="small">P0</el-tag>
          <el-tag v-else-if="row.priority === 1" type="warning" size="small">P1</el-tag>
          <el-tag v-else-if="row.priority === 2" size="small">P2</el-tag>
          <el-tag v-else type="info" size="small">P3</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.type === 'functional'" size="small">功能</el-tag>
          <el-tag v-else-if="row.type === 'performance'" type="success" size="small">性能</el-tag>
          <el-tag v-else-if="row.type === 'security'" type="warning" size="small">安全</el-tag>
          <el-tag v-else size="small">{{ row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.status === 'designing'" type="info" size="small">设计</el-tag>
          <el-tag v-else-if="row.status === 'pending_review'" type="warning" size="small">待评审</el-tag>
          <el-tag v-else-if="row.status === 'reviewed'" type="success" size="small">已评审</el-tag>
          <el-tag v-else-if="row.status === 'approved'" type="success" size="small">已批准</el-tag>
          <el-tag v-else-if="row.status === 'deprecated'" type="danger" size="small">废弃</el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="showResult" prop="last_result" label="结果" width="100">
        <template #default="{ row }">
          <TestCaseResultBadge
            :case-id="row.id"
            :result="row.last_result"
            :last-executed-at="row.last_executed_at"
            :show-icon="true"
            :show-label="true"
            size="small"
          />
        </template>
      </el-table-column>
      <el-table-column v-if="showAutomted" prop="is_automated" label="自动化" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_automated" type="success" size="small">是</el-tag>
          <el-tag v-else type="info" size="small">否</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="step_count" label="步骤数" width="80" align="center" />
      <el-table-column prop="designer_name" label="设计人" width="100" />
      <el-table-column prop="updated_at" label="更新时间" width="160">
        <template #default="{ row }">
          {{ formatDate(row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column v-if="showActions" label="操作" :width="actionColumnWidth" fixed="right">
        <template #default="{ row }">
          <slot name="row-actions" :row="row">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link size="small" @click="handleExecute(row)">执行</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </slot>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container" v-if="showPagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalCases"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import TestCaseResultBadge from '@/components/common/TestCaseResultBadge.vue'

const props = defineProps({
  cases: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  showToolbar: {
    type: Boolean,
    default: true
  },
  showSelection: {
    type: Boolean,
    default: true
  },
  showBatchActions: {
    type: Boolean,
    default: true
  },
  showResult: {
    type: Boolean,
    default: true
  },
  showAutomted: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  actionColumnWidth: {
    type: [Number, String],
    default: 220
  },
  totalCases: {
    type: Number,
    default: 0
  },
  selectable: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits([
  'load',
  'search',
  'filter-change',
  'selection-change',
  'page-change',
  'size-change',
  'view',
  'edit',
  'execute',
  'delete',
  'batch-action'
])

const tableRef = ref(null)
const searchQuery = ref('')
const filterStatus = ref('')
const filterPriority = ref('')
const filterType = ref('')
const selectedCases = ref([])
const currentPage = ref(1)
const pageSize = ref(20)

const displayCases = computed(() => {
  if (props.showPagination) {
    return props.cases
  }
  return props.cases
})

const getRowKey = (row) => row.id

const isSelectable = () => props.selectable

const getRowClassName = ({ row }) => {
  if (row.last_result === 'failed') return 'row-failed'
  if (row.last_result === 'blocked') return 'row-blocked'
  return ''
}

const handleSearch = () => {
  emit('search', {
    query: searchQuery.value,
    status: filterStatus.value,
    priority: filterPriority.value,
    type: filterType.value
  })
}

const handleFilterChange = () => {
  emit('filter-change', {
    query: searchQuery.value,
    status: filterStatus.value,
    priority: filterPriority.value,
    type: filterType.value
  })
}

const handleSelectionChange = (selection) => {
  selectedCases.value = selection
  emit('selection-change', selection)
}

const handleRowDoubleClick = (row) => {
  handleView(row)
}

const handleView = (row) => {
  emit('view', row)
}

const handleEdit = (row) => {
  emit('edit', row)
}

const handleExecute = (row) => {
  emit('execute', row)
}

const handleDelete = (row) => {
  emit('delete', row)
}

const handlePageChange = (page) => {
  emit('page-change', page)
}

const handleSizeChange = (size) => {
  pageSize.value = size
  emit('size-change', size)
}

const clearSelection = () => {
  tableRef.value?.clearSelection()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

watch([searchQuery, filterStatus, filterPriority, filterType], () => {
  currentPage.value = 1
})

defineExpose({
  clearSelection,
  getSelectedCases: () => selectedCases.value,
  refreshData: () => emit('load')
})
</script>

<style scoped>
.test-case-table {
  width: 100%;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.batch-actions-bar {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.batch-buttons {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.row-failed) {
  background-color: rgba(245, 108, 108, 0.1) !important;
}

:deep(.row-blocked) {
  background-color: rgba(230, 162, 60, 0.1) !important;
}
</style>