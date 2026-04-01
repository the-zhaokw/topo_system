<template>
  <div class="test-suite-tree">
    <div v-if="showSearch" class="tree-search">
      <el-input
        v-model="searchQuery"
        placeholder="搜索测试集..."
        clearable
        size="small"
        @input="handleSearch"
        @keydown.enter="handleSearchConfirm"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append v-if="searchQuery">
          <el-button @click="handleSearchClear">
            <el-icon><Close /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>

    <div class="tree-toolbar" v-if="showToolbar">
      <el-button size="small" type="primary" @click="handleCreateRoot" v-if="creatable">
        <el-icon><Plus /></el-icon>
        新建
      </el-button>
      <el-button size="small" @click="handleExpandAll">
        <el-icon><Rank /></el-icon>
        展开
      </el-button>
      <el-button size="small" @click="handleCollapseAll">
        <el-icon><Operation /></el-icon>
        收起
      </el-button>
      <el-button size="small" @click="handleRefresh" :loading="refreshing" v-if="refreshable">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <div v-if="searchQuery && searchResultCount > 0" class="search-result-tip">
      找到 {{ searchResultCount }} 个结果
      <el-button link size="small" @click="handleSearchClear">清除</el-button>
    </div>

    <el-tree
      ref="treeRef"
      :data="treeData"
      :props="treeProps"
      node-key="id"
      :default-expand-all="defaultExpandAll"
      :expand-on-click-node="false"
      :draggable="draggable"
      :allow-drop="handleAllowDrop"
      :allow-drag="handleAllowDrag"
      :filter-node-method="filterNode"
      :highlight-current="highlightCurrent"
      :show-checkbox="showCheckbox"
      :expand-row-click="true"
      @node-click="handleNodeClick"
      @node-contextmenu="handleContextMenu"
      @node-drop="handleNodeDrop"
      @node-drag-start="handleDragStart"
      @check-change="handleCheckChange"
      class="suite-tree"
    >
      <template #default="{ node, data }">
        <span class="tree-node-content" @contextmenu.prevent="() => {}">
          <span class="node-icon">
            <el-icon v-if="data.type === 'functional'"><Document /></el-icon>
            <el-icon v-else-if="data.type === 'performance'"><TrendCharts /></el-icon>
            <el-icon v-else-if="data.type === 'security'"><Lock /></el-icon>
            <el-icon v-else><Folder /></el-icon>
          </span>
          <span class="node-label">{{ node.label }}</span>
          <span class="node-badge">
            <el-tag v-if="data.status === 'designing'" size="small" type="info">设计</el-tag>
            <el-tag v-else-if="data.status === 'reviewed'" size="small" type="success">已评审</el-tag>
            <el-tag v-else-if="data.status === 'deprecated'" size="small" type="danger">废弃</el-tag>
          </span>
          <span v-if="showCaseCount" class="node-count">{{ data.case_count || 0 }}</span>
        </span>
      </template>
    </el-tree>

    <div v-if="contextMenuVisible" class="context-menu" :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }">
      <div class="context-menu-item" @click="handleContextAction('add_child')" v-if="creatable">
        <el-icon><FolderAdd /></el-icon>
        添加子测试集
      </div>
      <div class="context-menu-item" @click="handleContextAction('edit')" v-if="editable">
        <el-icon><Edit /></el-icon>
        编辑测试集
      </div>
      <div class="context-menu-item" @click="handleContextAction('view_cases')">
        <el-icon><Document /></el-icon>
        查看用例
      </div>
      <div class="context-menu-item" @click="handleContextAction('execute')">
        <el-icon><VideoPlay /></el-icon>
        执行测试集
      </div>
      <div class="context-menu-item" @click="handleContextAction('history')">
        <el-icon><Clock /></el-icon>
        版本历史
      </div>
      <div class="context-menu-divider" v-if="creatable"></div>
      <div class="context-menu-item" @click="handleContextAction('copy')" v-if="creatable">
        <el-icon><CopyDocument /></el-icon>
        复制测试集
      </div>
      <div class="context-menu-item" @click="handleContextAction('move')" v-if="creatable">
        <el-icon><Rank /></el-icon>
        移动测试集
      </div>
      <div class="context-menu-divider"></div>
      <div class="context-menu-item" @click="handleContextAction('refresh')">
        <el-icon><Refresh /></el-icon>
        刷新
      </div>
      <div class="context-menu-item danger" @click="handleContextAction('delete')" v-if="deletable">
        <el-icon><Delete /></el-icon>
        删除测试集
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import {
  Search,
  Plus,
  Rank,
  Operation,
  Document,
  TrendCharts,
  Lock,
  Folder,
  VideoPlay,
  CopyDocument,
  Delete,
  Edit,
  Clock,
  FolderAdd,
  Refresh,
  Close
} from '@element-plus/icons-vue'

const props = defineProps({
  projectId: {
    type: [Number, String],
    required: true
  },
  selectedId: {
    type: [Number, String],
    default: null
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  showToolbar: {
    type: Boolean,
    default: true
  },
  showCaseCount: {
    type: Boolean,
    default: true
  },
  showCheckbox: {
    type: Boolean,
    default: false
  },
  defaultExpandAll: {
    type: Boolean,
    default: false
  },
  highlightCurrent: {
    type: Boolean,
    default: true
  },
  draggable: {
    type: Boolean,
    default: true
  },
  selectable: {
    type: Boolean,
    default: true
  },
  creatable: {
    type: Boolean,
    default: true
  },
  deletable: {
    type: Boolean,
    default: true
  },
  editable: {
    type: Boolean,
    default: true
  },
  refreshable: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits([
  'load',
  'select',
  'nodeDrop',
  'checkChange',
  'create',
  'addChild',
  'edit',
  'copy',
  'move',
  'execute',
  'delete',
  'viewCases',
  'history',
  'refresh'
])

const treeRef = ref(null)
const treeData = ref([])
const searchQuery = ref('')
const searchResultCount = ref(0)
const refreshing = ref(false)
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuNode = ref(null)

const treeProps = {
  children: 'children',
  label: 'name'
}

const filterNode = (value, data) => {
  if (!searchQuery.value) return true
  return data.name.toLowerCase().includes(searchQuery.value.toLowerCase())
}

const handleSearch = () => {
  treeRef.value?.filter(searchQuery.value)
  countSearchResults()
}

const countSearchResults = () => {
  if (!searchQuery.value) {
    searchResultCount.value = 0
    return
  }
  const count = countMatchingNodes(treeData.value)
  searchResultCount.value = count
}

const countMatchingNodes = (nodes) => {
  let count = 0
  for (const node of nodes) {
    if (node.name.toLowerCase().includes(searchQuery.value.toLowerCase())) {
      count++
    }
    if (node.children && node.children.length > 0) {
      count += countMatchingNodes(node.children)
    }
  }
  return count
}

const handleSearchConfirm = () => {
  treeRef.value?.filter(searchQuery.value)
  countSearchResults()
}

const handleSearchClear = () => {
  searchQuery.value = ''
  searchResultCount.value = 0
  treeRef.value?.filter('')
}

const handleRefresh = async () => {
  refreshing.value = true
  emit('refresh', null)
  setTimeout(() => {
    refreshing.value = false
  }, 500)
}

const handleNodeClick = (data, node) => {
  emit('select', { data, node })
}

const handleContextMenu = (event, data, node) => {
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuNode.value = { data, node }
  contextMenuVisible.value = true
}

const handleContextAction = (action) => {
  if (!contextMenuNode.value) return

  const { data } = contextMenuNode.value

  switch (action) {
    case 'add_child':
      emit('addChild', data)
      break
    case 'edit':
      emit('edit', data)
      break
    case 'view_cases':
      emit('viewCases', data)
      break
    case 'execute':
      emit('execute', data)
      break
    case 'copy':
      emit('copy', data)
      break
    case 'move':
      emit('move', data)
      break
    case 'delete':
      emit('delete', data)
      break
    case 'history':
      emit('history', data)
      break
    case 'refresh':
      emit('refresh', data)
      break
  }

  closeContextMenu()
}

const closeContextMenu = () => {
  contextMenuVisible.value = false
  contextMenuNode.value = null
}

const handleNodeDrop = (draggingNode, dropNode, type) => {
  emit('nodeDrop', { draggingNode, dropNode, type })
}

const handleCheckChange = (data, checked, indeterminate) => {
  emit('checkChange', { data, checked, indeterminate })
}

const handleAllowDrop = (draggingNode, dropNode, type) => {
  if (draggingNode.data.id === dropNode.data.id) return false
  if (type === 'inner' && draggingNode.data.id === dropNode.data.id) return false
  if (type === 'inner' && draggingNode.data.parent_id === dropNode.data.id) return false
  return true
}

const handleAllowDrag = (draggingNode) => {
  return true
}

const handleDragStart = (event, data, node) => {
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', JSON.stringify({
    id: data.id,
    name: data.name,
    parentId: data.parent_id
  }))
  node.expand()
}

const handleCreateRoot = () => {
  emit('create', { parentId: null })
}

const handleExpandAll = () => {
  const nodes = treeRef.value?.store.nodesMap
  if (nodes) {
    Object.values(nodes).forEach(node => {
      node.expanded = true
    })
  }
}

const handleCollapseAll = () => {
  const nodes = treeRef.value?.store.nodesMap
  if (nodes) {
    Object.values(nodes).forEach(node => {
      node.expanded = false
    })
  }
}

const setCurrentNode = (nodeId) => {
  treeRef.value?.setCurrentKey(nodeId)
}

const getSelectedNode = () => {
  return treeRef.value?.getCurrentNode()
}

const updateTreeData = (data) => {
  treeData.value = data
}

const handleClickOutside = (event) => {
  if (contextMenuVisible.value) {
    closeContextMenu()
  }
}

watch(() => props.selectedId, (newVal) => {
  if (newVal) {
    setCurrentNode(newVal)
  }
})

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

defineExpose({
  setCurrentNode,
  getSelectedNode,
  updateTreeData,
  expandAll: handleExpandAll,
  collapseAll: handleCollapseAll
})
</script>

<style scoped>
.test-suite-tree {
  position: relative;
  width: 100%;
  height: 100%;
}

.tree-search {
  padding: 8px;
  border-bottom: 1px solid #ebeef5;
}

.tree-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px;
  border-bottom: 1px solid #ebeef5;
}

.suite-tree {
  padding: 8px;
  max-height: calc(100% - 90px);
  overflow-y: auto;
}

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding-right: 8px;
}

.node-icon {
  display: flex;
  align-items: center;
  color: #409EFF;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-badge {
  flex-shrink: 0;
}

.node-count {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

.context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 9999;
  min-width: 160px;
  padding: 4px 0;
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: all 0.2s;
}

.context-menu-item:hover {
  background: #f5f7fa;
  color: #409EFF;
}

.context-menu-item.danger {
  color: #F56C6C;
}

.context-menu-item.danger:hover {
  background: #fef0f0;
  color: #f56c6c;
}

.context-menu-divider {
  height: 1px;
  background: #e4e7ed;
  margin: 4px 0;
}

.search-result-tip {
  padding: 8px 12px;
  background: #ecf5ff;
  color: #409EFF;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #d9ecff;
}

.is-dragging-over {
  background-color: #f5f7fa !important;
}

.suite-tree .el-tree-node__content:hover {
  background-color: #f5f7fa;
}

.suite-tree .el-tree-node.is-dragging .el-tree-node__content {
  opacity: 0.5;
}

.suite-tree .el-tree-node.is-drop-inner .el-tree-node__content {
  background-color: #e7f7e7;
}
</style>